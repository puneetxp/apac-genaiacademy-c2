/**
 * Board chart primitives
 * Dependency-free SVG charts for the dashboard Analytics Board. Every chart has
 * a hover tooltip, and ChartCard can flip any chart to its table view.
 */

import { Component, createMemo, createSignal, For, JSX, onCleanup, onMount, Show } from "solid-js";

// Categorical slots, assigned in this fixed order (validated for CVD on light surfaces).
export const SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"];
export const OTHER = "#a3a29c";

export const inr = (n: number) => {
  const a = Math.abs(n);
  const trim = (v: number) => (v >= 100 ? v.toFixed(0) : v.toFixed(1).replace(/\.0$/, ""));
  const body = a >= 1e7 ? trim(a / 1e7) + "Cr" : a >= 1e5 ? trim(a / 1e5) + "L" : a >= 1e3 ? trim(a / 1e3) + "k" : String(Math.round(a));
  return `${n < 0 ? "−" : ""}₹${body}`;
};
export const num = (n: number) => (Number.isInteger(n) ? String(n) : n.toFixed(1));

/** Round axis ticks (0, 25k, 50k…) covering [min, max]. */
export const niceTicks = (min: number, max: number, count = 4): number[] => {
  const span = max - min || 1;
  const raw = span / count;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((st) => st >= raw) || raw;
  const lo = Math.floor(min / step) * step;
  const hi = Math.ceil(max / step) * step;
  const out: number[] = [];
  for (let v = lo; v <= hi + step / 2; v += step) out.push(Math.round(v * 100) / 100);
  return out;
};

/** Track an element's rendered width so SVG text stays at its real pixel size. */
const useWidth = (fallback: number) => {
  const [w, setW] = createSignal(fallback);
  let el: HTMLDivElement | undefined;
  const ref = (e: HTMLDivElement) => (el = e);
  onMount(() => {
    if (!el) return;
    setW(el.clientWidth || fallback);
    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(() => el && el.clientWidth && setW(el.clientWidth));
    ro.observe(el);
    onCleanup(() => ro.disconnect());
  });
  return { w, ref, el: () => el };
};

export interface Datum {
  label: string;
  value: number;
}

/** Fold anything past `max` slices into "Other" so no generated hue is ever needed. */
export const foldOther = (data: Datum[], max = 6): Datum[] => {
  const sorted = [...data].sort((a, b) => b.value - a.value);
  if (sorted.length <= max) return sorted;
  const rest = sorted.slice(max - 1).reduce((s, d) => s + d.value, 0);
  return [...sorted.slice(0, max - 1), { label: "Other", value: rest }];
};

const Tooltip: Component<{ x: number; y: number; children: JSX.Element }> = (props) => (
  <div
    class="pointer-events-none absolute z-20 -translate-x-1/2 -translate-y-full rounded-md bg-gray-900 px-2.5 py-1.5 text-xs text-white shadow-lg whitespace-nowrap"
    style={{ left: `${props.x}px`, top: `${props.y - 8}px` }}
  >
    {props.children}
  </div>
);

const Empty: Component<{ text?: string }> = (props) => (
  <div class="flex h-40 items-center justify-center rounded-lg border border-dashed border-gray-200 text-sm text-gray-400">
    {props.text || "No data yet"}
  </div>
);

const Legend: Component<{ items: { label: string; color: string; dashed?: boolean }[] }> = (props) => (
  <div class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600">
    <For each={props.items}>
      {(i) => (
        <span class="inline-flex items-center gap-1.5">
          <span
            class="inline-block h-2.5 w-2.5 rounded-sm"
            style={i.dashed ? { border: `2px dashed ${i.color}` } : { background: i.color }}
          />
          {i.label}
        </span>
      )}
    </For>
  </div>
);

// ─── Card shell ─────────────────────────────────────────────────────────────

export const ChartCard: Component<{
  title: string;
  subtitle?: string;
  badge?: string;
  class?: string;
  table?: () => JSX.Element;
  children: JSX.Element;
}> = (props) => {
  const [asTable, setAsTable] = createSignal(false);
  return (
    <section class={`rounded-xl border border-gray-200 bg-white p-4 shadow-sm ${props.class || ""}`}>
      <header class="mb-3 flex items-start justify-between gap-2">
        <div>
          <h3 class="flex items-center gap-2 text-sm font-semibold text-gray-900">
            {props.title}
            <Show when={props.badge}>
              <span class="rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-medium text-violet-700">{props.badge}</span>
            </Show>
          </h3>
          <Show when={props.subtitle}>
            <p class="mt-0.5 text-xs text-gray-500">{props.subtitle}</p>
          </Show>
        </div>
        <Show when={props.table}>
          <button
            type="button"
            onClick={() => setAsTable(!asTable())}
            class="shrink-0 rounded-md border border-gray-200 px-2 py-1 text-[11px] text-gray-600 hover:bg-gray-50"
            aria-pressed={asTable()}
          >
            {asTable() ? "📈 Chart" : "▦ Table"}
          </button>
        </Show>
      </header>
      <Show when={asTable() && props.table} fallback={props.children}>
        {props.table!()}
      </Show>
    </section>
  );
};

// ─── KPI tile ───────────────────────────────────────────────────────────────

export const StatTile: Component<{
  label: string;
  value: string;
  hint?: string;
  icon?: string;
  trend?: number[];
  delta?: number;
}> = (props) => (
  <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
    <div class="flex items-center justify-between text-xs font-medium text-gray-500">
      <span>{props.label}</span>
      <span class="text-base">{props.icon}</span>
    </div>
    <div class="mt-1 text-2xl font-bold text-gray-900">{props.value}</div>
    <div class="mt-1 flex items-end justify-between gap-2">
      <span class="text-xs text-gray-500">
        <Show when={props.delta !== undefined}>
          <span class={props.delta! >= 0 ? "text-green-700" : "text-red-700"}>
            {props.delta! >= 0 ? "▲" : "▼"} {Math.abs(props.delta!).toFixed(0)}%{" "}
          </span>
        </Show>
        {props.hint}
      </span>
      <Show when={props.trend && props.trend.length > 1}>
        <Sparkline values={props.trend!} />
      </Show>
    </div>
  </div>
);

export const Sparkline: Component<{ values: number[]; color?: string; width?: number; height?: number }> = (props) => {
  const w = () => props.width || 72;
  const h = () => props.height || 24;
  const path = createMemo(() => {
    const v = props.values;
    const max = Math.max(...v), min = Math.min(...v);
    const span = max - min || 1;
    return v
      .map((y, i) => `${i ? "L" : "M"}${((i / (v.length - 1)) * (w() - 4) + 2).toFixed(1)},${(h() - 2 - ((y - min) / span) * (h() - 4)).toFixed(1)}`)
      .join(" ");
  });
  return (
    <svg width={w()} height={h()} aria-hidden="true">
      <path d={path()} fill="none" stroke={props.color || SERIES[0]} stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  );
};

// ─── Donut ──────────────────────────────────────────────────────────────────

export const DonutChart: Component<{ data: Datum[]; format?: (n: number) => string; centerLabel?: string }> = (props) => {
  const fmt = (n: number) => (props.format || num)(n);
  const data = createMemo(() => foldOther(props.data.filter((d) => d.value > 0)));
  const total = createMemo(() => data().reduce((s, d) => s + d.value, 0));
  const color = (d: Datum, i: number) => (d.label === "Other" ? OTHER : SERIES[i % SERIES.length]);
  const [hover, setHover] = createSignal<number | null>(null);
  const R = 70, r = 46, C = 90;

  const arcs = createMemo(() => {
    let a0 = -Math.PI / 2;
    return data().map((d) => {
      const sweep = (d.value / total()) * Math.PI * 2;
      const a1 = a0 + sweep;
      const gap = data().length > 1 ? 0.012 : 0; // 2px surface gap between slices
      const s = a0 + gap, e = a1 - gap;
      const large = e - s > Math.PI ? 1 : 0;
      const p = (rad: number, ang: number) => `${C + rad * Math.cos(ang)},${C + rad * Math.sin(ang)}`;
      const path =
        sweep >= Math.PI * 2 - 0.001
          ? `M${C},${C - R}A${R},${R} 0 1 1 ${C - 0.01},${C - R}L${C - 0.01},${C - r}A${r},${r} 0 1 0 ${C},${C - r}Z`
          : `M${p(R, s)}A${R},${R} 0 ${large} 1 ${p(R, e)}L${p(r, e)}A${r},${r} 0 ${large} 0 ${p(r, s)}Z`;
      const mid = (a0 + a1) / 2;
      a0 = a1;
      return { d, path, mx: C + R * Math.cos(mid), my: C + R * Math.sin(mid) };
    });
  });

  return (
    <Show when={total() > 0} fallback={<Empty />}>
      <div class="flex flex-wrap items-center justify-center gap-x-5 gap-y-3">
        <div class="relative shrink-0">
          <svg width="160" height="160" viewBox="0 0 180 180" role="img" aria-label="Donut chart">
            <For each={arcs()}>
              {(a, i) => (
                <path
                  d={a.path}
                  fill={color(a.d, i())}
                  opacity={hover() === null || hover() === i() ? 1 : 0.35}
                  onMouseEnter={() => setHover(i())}
                  onMouseLeave={() => setHover(null)}
                  class="cursor-pointer transition-opacity"
                />
              )}
            </For>
            <text x="90" y="86" text-anchor="middle" class="fill-gray-900 text-lg font-bold">
              {hover() !== null ? fmt(data()[hover()!].value) : fmt(total())}
            </text>
            <text x="90" y="104" text-anchor="middle" class="fill-gray-500 text-[11px]">
              {hover() !== null ? data()[hover()!].label : props.centerLabel || "Total"}
            </text>
          </svg>
        </div>
        <ul class="min-w-[170px] flex-1 space-y-1 text-xs">
          <For each={data()}>
            {(d, i) => (
              <li
                class="flex items-center justify-between gap-3 rounded px-1.5 py-0.5"
                classList={{ "bg-gray-50": hover() === i() }}
                onMouseEnter={() => setHover(i())}
                onMouseLeave={() => setHover(null)}
              >
                <span class="flex min-w-0 items-center gap-2 text-gray-700">
                  <span class="h-2.5 w-2.5 shrink-0 rounded-sm" style={{ background: color(d, i()) }} />
                  <span class="truncate capitalize">{d.label}</span>
                </span>
                <span class="shrink-0 whitespace-nowrap font-medium tabular-nums text-gray-900">
                  {fmt(d.value)} <span class="font-normal text-gray-400">{((d.value / total()) * 100).toFixed(0)}%</span>
                </span>
              </li>
            )}
          </For>
        </ul>
      </div>
    </Show>
  );
};

// ─── Bars ───────────────────────────────────────────────────────────────────

/** Horizontal bars: best for ranked categories with long labels. */
export const BarList: Component<{ data: Datum[]; format?: (n: number) => string; color?: string; max?: number }> = (props) => {
  const fmt = (n: number) => (props.format || num)(n);
  const rows = createMemo(() => [...props.data].sort((a, b) => b.value - a.value).slice(0, props.max || 8));
  const top = createMemo(() => Math.max(...rows().map((d) => d.value), 1));
  return (
    <Show when={rows().length} fallback={<Empty />}>
      <ul class="space-y-2.5">
        <For each={rows()}>
          {(d) => (
            <li class="group" title={`${d.label}: ${fmt(d.value)}`}>
              <div class="mb-1 flex justify-between text-xs">
                <span class="truncate capitalize text-gray-700">{d.label}</span>
                <span class="font-medium text-gray-900">{fmt(d.value)}</span>
              </div>
              <div class="h-2.5 w-full rounded-full bg-gray-100">
                <div
                  class="h-2.5 rounded-full transition-all group-hover:opacity-80"
                  style={{ width: `${Math.max((d.value / top()) * 100, 1.5)}%`, background: props.color || SERIES[0] }}
                />
              </div>
            </li>
          )}
        </For>
      </ul>
    </Show>
  );
};

/** Vertical grouped bars on one shared axis (e.g. investment vs expected return). Negative values show in the tooltip, bars clamp at 0. */
export const GroupedBarChart: Component<{
  categories: string[];
  series: { name: string; values: number[] }[];
  format?: (n: number) => string;
  height?: number;
}> = (props) => {
  const fmt = (n: number) => (props.format || num)(n);
  const H = () => props.height || 220;
  const size = useWidth(520);
  const W = () => size.w();
  const PAD_L = 52, PAD_B = 26, PAD_T = 10;
  const [hover, setHover] = createSignal<{ c: number; x: number; y: number } | null>(null);
  const ticks = createMemo(() => niceTicks(0, Math.max(1, ...props.series.flatMap((s) => s.values))));
  const max = () => ticks()[ticks().length - 1];
  const band = () => (W() - PAD_L) / Math.max(props.categories.length, 1);
  const barW = () => Math.max(6, Math.min(24, (band() * 0.6) / Math.max(props.series.length, 1) - 2));
  const y = (v: number) => PAD_T + (H() - PAD_T - PAD_B) * (1 - Math.max(0, v) / max());
  const track = (c: number) => (e: MouseEvent) => {
    const r = size.el()!.getBoundingClientRect();
    setHover({ c, x: e.clientX - r.left, y: e.clientY - r.top });
  };

  return (
    <Show when={props.categories.length} fallback={<Empty />}>
      <div class="relative" ref={size.ref}>
        <svg width={W()} height={H()} class="block" role="img" aria-label="Grouped bar chart">
          <For each={ticks()}>
            {(t) => (
              <g>
                <line x1={PAD_L} x2={W()} y1={y(t)} y2={y(t)} stroke="#eceae4" />
                <text x={PAD_L - 8} y={y(t) + 3} text-anchor="end" font-size="10" fill="#8a8984">{fmt(t)}</text>
              </g>
            )}
          </For>
          <For each={props.categories}>
            {(cat, c) => {
              const cx = () => PAD_L + band() * c() + band() / 2;
              const groupW = () => props.series.length * (barW() + 2) - 2;
              return (
                <g onMouseEnter={track(c())} onMouseMove={track(c())} onMouseLeave={() => setHover(null)}>
                  <rect x={cx() - band() / 2} y={PAD_T} width={band()} height={H() - PAD_B - PAD_T} rx="6" fill={hover()?.c === c() ? "#f6f5f1" : "transparent"} />
                  <For each={props.series}>
                    {(s, si) => {
                      const v = () => Math.max(0, s.values[c()] || 0);
                      const x = () => cx() - groupW() / 2 + si() * (barW() + 2);
                      const h = () => (v() > 0 ? Math.max(y(0) - y(v()), 4) : 0);
                      const r = () => Math.min(4, h(), barW() / 2);
                      return (
                        <Show when={h() > 0}>
                          <path
                            d={`M${x()},${y(0)}v${-h() + r()}q0,${-r()} ${r()},${-r()}h${barW() - 2 * r()}q${r()},0 ${r()},${r()}v${h() - r()}z`}
                            fill={SERIES[si() % SERIES.length]}
                          />
                        </Show>
                      );
                    }}
                  </For>
                  <text x={cx()} y={H() - 8} text-anchor="middle" font-size="11" fill="#52514e" class="capitalize">
                    {cat.length > 14 ? cat.slice(0, 13) + "…" : cat}
                  </text>
                </g>
              );
            }}
          </For>
        </svg>
        <Show when={hover()}>
          {(h) => (
            <Tooltip x={h().x} y={h().y}>
              <div class="mb-0.5 font-semibold capitalize">{props.categories[h().c]}</div>
              <For each={props.series}>
                {(s, si) => (
                  <div class="flex items-center gap-1.5">
                    <span class="h-2 w-2 rounded-sm" style={{ background: SERIES[si()] }} />
                    {s.name}: <span class={(s.values[h().c] || 0) < 0 ? "text-red-300" : ""}>{fmt(s.values[h().c] || 0)}</span>
                  </div>
                )}
              </For>
            </Tooltip>
          )}
        </Show>
        <Show when={props.series.length > 1}>
          <Legend items={props.series.map((s, i) => ({ label: s.name, color: SERIES[i] }))} />
        </Show>
      </div>
    </Show>
  );
};

// ─── Trend + projection ─────────────────────────────────────────────────────

export interface TrendPoint {
  label: string;
  value: number;
  projected?: boolean;
  low?: number;
  high?: number;
}

/** Area/line over time; projected points draw dashed with a confidence band. */
export const TrendChart: Component<{
  points: TrendPoint[];
  format?: (n: number) => string;
  height?: number;
  seriesLabel?: string;
}> = (props) => {
  const fmt = (n: number) => (props.format || num)(n);
  const H = () => props.height || 220;
  const size = useWidth(620);
  const W = () => size.w();
  const PAD_L = 56, PAD_B = 26, PAD_T = 12, PAD_R = 12;
  const [hover, setHover] = createSignal<number | null>(null);
  const pts = () => props.points;
  const ticks = createMemo(() =>
    niceTicks(Math.min(0, ...pts().map((p) => Math.min(p.value, p.low ?? 0))), Math.max(1, ...pts().map((p) => Math.max(p.value, p.high ?? 0)))),
  );
  const max = () => ticks()[ticks().length - 1];
  const min = () => ticks()[0];
  const x = (i: number) => PAD_L + ((W() - PAD_L - PAD_R) * i) / Math.max(pts().length - 1, 1);
  const y = (v: number) => PAD_T + (H() - PAD_T - PAD_B) * (1 - (v - min()) / (max() - min() || 1));
  const line = (arr: [number, number][]) => arr.map(([i, v], k) => `${k ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("");

  const firstProj = createMemo(() => pts().findIndex((p) => p.projected));
  const actual = createMemo(() => pts().map((p, i) => [i, p.value] as [number, number]).filter(([i]) => !pts()[i].projected));
  const proj = createMemo(() => {
    const f = firstProj();
    if (f < 0) return [];
    const start = Math.max(f - 1, 0);
    return pts().slice(start).map((p, k) => [start + k, p.value] as [number, number]);
  });
  const bandPath = createMemo(() => {
    const b = pts().map((p, i) => ({ i, p })).filter(({ p }) => p.projected && p.low !== undefined && p.high !== undefined);
    if (b.length < 2) return "";
    return (
      b.map(({ i, p }, k) => `${k ? "L" : "M"}${x(i)},${y(p.high!)}`).join("") +
      [...b].reverse().map(({ i, p }) => `L${x(i)},${y(p.low!)}`).join("") +
      "Z"
    );
  });

  const onMove = (e: MouseEvent) => {
    const r = size.el()!.getBoundingClientRect();
    const i = Math.round(((e.clientX - r.left - PAD_L) / (W() - PAD_L - PAD_R)) * (pts().length - 1));
    setHover(Math.max(0, Math.min(pts().length - 1, i)));
  };
  const hoverPx = () => (hover() === null ? { x: 0, y: 0 } : { x: x(hover()!), y: y(pts()[hover()!].value) });

  return (
    <Show when={pts().length > 1} fallback={<Empty />}>
      <div class="relative" ref={size.ref}>
        <svg width={W()} height={H()} class="block" role="img" aria-label="Trend chart" onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
          <defs>
            <linearGradient id="trendFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stop-color={SERIES[0]} stop-opacity="0.22" />
              <stop offset="100%" stop-color={SERIES[0]} stop-opacity="0" />
            </linearGradient>
          </defs>
          <For each={ticks()}>
            {(t) => (
              <g>
                <line x1={PAD_L} x2={W() - PAD_R} y1={y(t)} y2={y(t)} stroke="#eceae4" />
                <text x={PAD_L - 6} y={y(t) + 3} text-anchor="end" font-size="10" fill="#8a8984">{fmt(t)}</text>
              </g>
            )}
          </For>
          <Show when={firstProj() > 0}>
            <rect x={x(firstProj() - 1)} y={PAD_T} width={x(pts().length - 1) - x(firstProj() - 1)} height={H() - PAD_T - PAD_B} fill="#f5f3ff" />
            <text x={x(firstProj() - 1) + 6} y={PAD_T + 12} font-size="10" font-weight="600" fill="#4a3aa7">AI projection →</text>
          </Show>
          <Show when={bandPath()}>
            <path d={bandPath()} fill={SERIES[6]} opacity="0.12" />
          </Show>
          <Show when={actual().length > 1}>
            <path d={`${line(actual())}L${x(actual()[actual().length - 1][0])},${y(min())}L${x(actual()[0][0])},${y(min())}Z`} fill="url(#trendFill)" />
            <path d={line(actual())} fill="none" stroke={SERIES[0]} stroke-width="2" stroke-linejoin="round" />
          </Show>
          <Show when={proj().length > 1}>
            <path d={line(proj())} fill="none" stroke={SERIES[6]} stroke-width="2" stroke-dasharray="5 4" stroke-linejoin="round" />
          </Show>
          <For each={pts()}>
            {(p, i) => (
              <Show when={i() % Math.ceil(pts().length / 8) === 0 || i() === pts().length - 1}>
                <text x={x(i())} y={H() - 8} text-anchor="middle" font-size="10" fill="#6b6a65">{p.label}</text>
              </Show>
            )}
          </For>
          <Show when={hover() !== null}>
            <line x1={x(hover()!)} x2={x(hover()!)} y1={PAD_T} y2={H() - PAD_B} stroke="#a3a29c" stroke-dasharray="2 3" />
            <circle
              cx={x(hover()!)}
              cy={y(pts()[hover()!].value)}
              r="4.5"
              fill={pts()[hover()!].projected ? SERIES[6] : SERIES[0]}
              stroke="white"
              stroke-width="2"
            />
          </Show>
        </svg>
        <Show when={hover() !== null}>
          <Tooltip x={hoverPx().x} y={hoverPx().y}>
            <div class="font-semibold">
              {pts()[hover()!].label} {pts()[hover()!].projected ? "· projected" : ""}
            </div>
            <div>{props.seriesLabel || "Value"}: {fmt(pts()[hover()!].value)}</div>
            <Show when={pts()[hover()!].low !== undefined}>
              <div class="text-gray-300">
                Range {fmt(pts()[hover()!].low!)} – {fmt(pts()[hover()!].high!)}
              </div>
            </Show>
          </Tooltip>
        </Show>
        <Legend
          items={[
            { label: `${props.seriesLabel || "Value"} (actual)`, color: SERIES[0] },
            ...(firstProj() >= 0 ? [{ label: "AI projection (with confidence range)", color: SERIES[6], dashed: true }] : []),
          ]}
        />
      </div>
    </Show>
  );
};

// ─── Gauge ──────────────────────────────────────────────────────────────────

export const Gauge: Component<{ value: number; max?: number; label: string; format?: (n: number) => string }> = (props) => {
  const max = () => props.max || 100;
  const pct = () => Math.max(0, Math.min(1, props.value / max()));
  const R = 70, C = 90;
  const arc = (p: number) => {
    const a = Math.PI * (1 - p);
    return `${C + R * Math.cos(a)},${C - R * Math.sin(a)}`;
  };
  const status = () => (props.value >= 25 ? { c: "#0ca30c", t: "✓ Healthy" } : props.value >= 0 ? { c: "#fab219", t: "! Modest" } : { c: "#d03b3b", t: "✕ Loss" });
  return (
    <div class="flex flex-col items-center">
      <svg width="180" height="104" viewBox="0 0 180 104" role="img" aria-label={`${props.label} ${props.value}`}>
        <path d={`M${arc(0)}A${R},${R} 0 0 1 ${arc(1)}`} fill="none" stroke="#eceae4" stroke-width="14" stroke-linecap="round" />
        <Show when={pct() > 0}>
          <path d={`M${arc(0)}A${R},${R} 0 0 1 ${arc(pct())}`} fill="none" stroke={status().c} stroke-width="14" stroke-linecap="round" />
        </Show>
        <text x="90" y="84" text-anchor="middle" class="fill-gray-900 text-xl font-bold">
          {(props.format || ((n: number) => `${n.toFixed(1)}%`))(props.value)}
        </text>
        <text x="90" y="100" text-anchor="middle" class="fill-gray-500 text-[11px]">{props.label}</text>
      </svg>
      <span class="mt-1 text-xs font-medium text-gray-700">{status().t}</span>
    </div>
  );
};

// ─── Table ──────────────────────────────────────────────────────────────────

export interface Column<T> {
  key: string;
  label: string;
  align?: "left" | "right";
  value?: (row: T) => number | string;
  render?: (row: T) => JSX.Element;
}

export function DataTable<T>(props: { columns: Column<T>[]; rows: T[]; empty?: string; dense?: boolean }) {
  const [sort, setSort] = createSignal<{ key: string; dir: 1 | -1 } | null>(null);
  const get = (row: T, c: Column<T>) => (c.value ? c.value(row) : (row as any)[c.key]);
  const rows = createMemo(() => {
    const s = sort();
    if (!s) return props.rows;
    const col = props.columns.find((c) => c.key === s.key)!;
    return [...props.rows].sort((a, b) => {
      const va = get(a, col), vb = get(b, col);
      return (typeof va === "number" && typeof vb === "number" ? va - vb : String(va ?? "").localeCompare(String(vb ?? ""))) * s.dir;
    });
  });
  return (
    <Show when={props.rows.length} fallback={<Empty text={props.empty} />}>
      <div class="-mx-4 overflow-x-auto px-4">
        <table class="w-full min-w-[480px] text-left text-xs">
          <thead>
            <tr class="border-b border-gray-200 text-gray-500">
              <For each={props.columns}>
                {(c) => (
                  <th class={`py-2 pr-3 font-medium ${c.align === "right" ? "text-right" : ""}`}>
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 hover:text-gray-900"
                      onClick={() => setSort(sort()?.key === c.key ? { key: c.key, dir: sort()!.dir === 1 ? -1 : 1 } : { key: c.key, dir: 1 })}
                    >
                      {c.label}
                      <span class="text-[9px]">{sort()?.key === c.key ? (sort()!.dir === 1 ? "▲" : "▼") : "↕"}</span>
                    </button>
                  </th>
                )}
              </For>
            </tr>
          </thead>
          <tbody>
            <For each={rows()}>
              {(row) => (
                <tr class="border-b border-gray-100 hover:bg-gray-50">
                  <For each={props.columns}>
                    {(c) => (
                      <td class={`${props.dense ? "py-1.5" : "py-2.5"} pr-3 text-gray-800 ${c.align === "right" ? "text-right tabular-nums" : ""}`}>
                        {c.render ? c.render(row) : String(get(row, c) ?? "—")}
                      </td>
                    )}
                  </For>
                </tr>
              )}
            </For>
          </tbody>
        </table>
      </div>
    </Show>
  );
}

/** Simple two-column table for a chart's table view. */
export const DatumTable: Component<{ data: Datum[]; format?: (n: number) => string; label?: string; valueLabel?: string }> = (props) => (
  <DataTable
    dense
    rows={props.data}
    columns={[
      { key: "label", label: props.label || "Item", render: (d: Datum) => <span class="capitalize">{d.label}</span> },
      { key: "value", label: props.valueLabel || "Value", align: "right", render: (d: Datum) => (props.format || num)(d.value) },
    ]}
  />
);
