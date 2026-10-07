/**
 * Analytics Board
 * Board-style overview of the farmer's existing farms, crops and livestock:
 * KPI tiles, charts (donut, bars, grouped bars, gauge, trend) with a table view
 * each, sortable tables, and an AI income projection driven by demand signals.
 */

import { Component, createMemo, createResource, createSignal, For, Show } from "solid-js";
import { A } from "@solidjs/router";
import { user } from "../../../stores/auth.store";
import type { DashboardData, ActiveCrop } from "../../../services/dashboard.service";
import { BoardService, type DemandSignal, type LivestockRow } from "../../../services/board.service";
import {
  BarList,
  ChartCard,
  DataTable,
  DatumTable,
  DonutChart,
  Gauge,
  GroupedBarChart,
  inr,
  num,
  StatTile,
  TrendChart,
  type Datum,
} from "./charts";

type Tab = "overview" | "farms" | "livestock" | "ai";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "📊 Overview" },
  { id: "farms", label: "🌾 Farms & Crops" },
  { id: "livestock", label: "🐄 Livestock" },
  { id: "ai", label: "✨ AI Projections" },
];

const groupSum = <T,>(rows: T[], by: (r: T) => string, val: (r: T) => number): Datum[] => {
  const m = new Map<string, number>();
  for (const r of rows) m.set(by(r) || "unknown", (m.get(by(r) || "unknown") || 0) + val(r));
  return [...m].map(([label, value]) => ({ label, value }));
};

const date = (s?: string | null) => (s ? new Date(s).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "2-digit" }) : "—");

const STAGE_STYLE: Record<string, string> = {
  planted: "bg-blue-50 text-blue-700",
  growing: "bg-green-50 text-green-700",
  maturing: "bg-amber-50 text-amber-700",
  ready: "bg-emerald-100 text-emerald-800",
  overdue: "bg-red-50 text-red-700",
};

const DEMAND_STYLE: Record<string, { cls: string; icon: string }> = {
  high: { cls: "bg-green-50 text-green-800", icon: "▲" },
  medium: { cls: "bg-gray-100 text-gray-700", icon: "●" },
  low: { cls: "bg-red-50 text-red-700", icon: "▼" },
};

const AnalyticsBoard: Component<{ data: DashboardData; farms: any[] }> = (props) => {
  const [tab, setTab] = createSignal<Tab>("overview");
  const farmerId = () => user()?.id;

  const [livestock] = createResource(farmerId, (id) => BoardService.getLivestock(id));
  const [portfolio] = createResource(farmerId, (id) => BoardService.getPortfolio(id));

  const crops = (): ActiveCrop[] => props.data.active_crops || [];
  const herd = (): LivestockRow[] => livestock() || [];
  const defaultState = () => props.farms.find((f) => f.state)?.state || herd().find((l) => l.state)?.state || "";

  const [signals] = createResource(
    () => (livestock.loading ? null : { crops: crops(), herd: herd(), state: defaultState() }),
    ({ crops, herd, state }) =>
      state
        ? BoardService.getDemandSignals([
            ...crops.map((c) => ({ item_type: "crop" as const, item_name: c.crop_type, state })),
            ...herd.map((l) => ({ item_type: "livestock" as const, item_name: l.species, state: l.state || state })),
          ])
        : Promise.resolve([] as DemandSignal[]),
  );

  const projection = createMemo(() => BoardService.buildIncomeProjection(crops(), herd(), signals() || []));
  const pastIncome = () => projection().filter((p) => !p.projected).reduce((s, p) => s + p.value, 0);
  const nextIncome = () => projection().filter((p) => p.projected).reduce((s, p) => s + p.value, 0);
  const incomeDelta = () => (pastIncome() > 0 ? ((nextIncome() - pastIncome()) / pastIncome()) * 100 : undefined);

  const totalArea = () => props.farms.reduce((s, f) => s + (Number(f.total_area) || 0), 0);
  const areaUnit = () => props.farms[0]?.area_unit || "acres";
  const headCount = () => herd().reduce((s, l) => s + l.quantity, 0);
  const herdInvestment = () => herd().reduce((s, l) => s + l.purchase_price * l.quantity, 0);
  const cropProfit = () => crops().reduce((s, c) => s + (Number(c.projected_profit ?? c.expected_profit) || 0), 0);
  const cropExpenses = () => crops().reduce((s, c) => s + (Number(c.total_expenses) || 0), 0);

  // Derived series
  const areaByFarm = () => props.farms.map((f) => ({ label: f.name, value: Number(f.total_area) || 0 }));
  const cropsByStage = () => groupSum(crops(), (c) => c.growth_stage, () => 1);
  const cropsByType = () => groupSum(crops(), (c) => c.crop_type, () => 1);
  const harvestSoon = () =>
    crops().filter((c) => c.days_until_harvest >= 0).map((c) => ({ label: `${c.crop_type}${c.plot_name ? " · " + c.plot_name : ""}`, value: c.days_until_harvest }));
  const headBySpecies = () => groupSum(herd(), (l) => l.species, (l) => l.quantity);
  const headByPurpose = () => groupSum(herd(), (l) => l.purpose, (l) => l.quantity);
  const herdByFarm = () => groupSum(herd(), (l) => props.farms.find((f) => f.id === l.farm_id)?.name || `Farm #${l.farm_id}`, (l) => l.quantity);
  const speciesMoney = createMemo(() => {
    const src = portfolio()?.livestock_by_species;
    const rows = src && Object.keys(src).length
      ? Object.entries(src).map(([k, v]) => ({ k, inv: Number(v.investment) || 0, ret: Number(v.expected_returns) || 0 }))
      : groupSum(herd(), (l) => l.species, (l) => l.purchase_price * l.quantity).map((d) => ({
          k: d.label,
          inv: d.value,
          ret: herd().filter((l) => l.species === d.label).reduce((s, l) => s + (l.expected_roi || 0) * l.quantity, 0),
        }));
    return { categories: rows.map((r) => r.k), series: [{ name: "Investment", values: rows.map((r) => r.inv) }, { name: "Expected returns", values: rows.map((r) => r.ret) }] };
  });
  const cropMoney = createMemo(() => {
    const rows = crops().slice(0, 8);
    return {
      categories: rows.map((c) => c.crop_type),
      series: [
        { name: "Expenses", values: rows.map((c) => Number(c.total_expenses) || 0) },
        { name: "Projected profit", values: rows.map((c) => Number(c.projected_profit ?? c.expected_profit) || 0) },
      ],
    };
  });
  const roi = () =>
    portfolio()?.overall_roi_percentage ??
    (herdInvestment() > 0 ? (herd().reduce((s, l) => s + (l.expected_roi || 0) * l.quantity, 0) / herdInvestment()) * 100 : 0);
  const breakEven = () => portfolio()?.break_even_summary || { achieved: 0, pending: headCount() };

  const incomeBySource = createMemo(() => {
    const ahead = projection().filter((p) => p.projected).length;
    return [
      ...groupSum(
        crops().filter((c) => c.days_until_harvest >= 0 && c.days_until_harvest <= ahead * 31),
        (c) => c.crop_type,
        (c) => Number(c.projected_profit ?? c.expected_profit) || 0,
      ),
      ...groupSum(herd(), (l) => l.species, (l) => ((l.expected_roi || 0) * l.quantity * ahead) / 12),
    ];
  });

  const insights = createMemo(() => {
    const out: string[] = [];
    const s = signals() || [];
    const hot = s.filter((x) => x.demand_level === "high");
    const cold = s.filter((x) => x.demand_level === "low");
    if (hot.length) out.push(`Buyer demand is rising for ${hot.map((x) => x.item_name).join(", ")} — consider listing early in the marketplace.`);
    if (cold.length) out.push(`Demand is softening for ${cold.map((x) => x.item_name).join(", ")} — hold stock or look at advance booking.`);
    const ready = crops().filter((c) => c.growth_stage === "ready" || c.growth_stage === "overdue");
    if (ready.length) out.push(`${ready.length} crop${ready.length > 1 ? "s are" : " is"} ready or overdue for harvest.`);
    const loss = crops().filter((c) => (Number(c.projected_profit ?? c.expected_profit) || 0) < 0);
    if (loss.length) out.push(`${loss.map((c) => c.crop_type).join(", ")} ${loss.length > 1 ? "are" : "is"} projected at a loss — review expenses.`);
    if (breakEven().pending > 0 && headCount() > 0) out.push(`${breakEven().pending} of ${headCount()} animals have not yet reached break-even.`);
    if (incomeDelta() !== undefined) out.push(`Next 6 months projected at ${inr(nextIncome())}, ${incomeDelta()! >= 0 ? "up" : "down"} ${Math.abs(incomeDelta()!).toFixed(0)}% on the last 6.`);
    if (!s.length) out.push("Not enough buyer-interest history in your state yet for demand signals — projections use your own crop and livestock plans.");
    return out;
  });

  // ─── Tables ───────────────────────────────────────────────────────────────

  const FarmTable = () => (
    <DataTable
      rows={props.farms}
      empty="No farms registered"
      columns={[
        { key: "name", label: "Farm", render: (f: any) => <A href={`/farm/${f.id}`} class="font-medium text-green-700 hover:underline">{f.name}</A> },
        { key: "location", label: "Location", value: (f: any) => f.location || [f.district, f.state].filter(Boolean).join(", ") || "—" },
        { key: "total_area", label: "Area", align: "right", value: (f: any) => Number(f.total_area) || 0, render: (f: any) => `${num(Number(f.total_area) || 0)} ${f.area_unit || ""}` },
        { key: "herd", label: "Livestock", align: "right", value: (f: any) => herd().filter((l) => l.farm_id === f.id).reduce((s, l) => s + l.quantity, 0) },
        { key: "soil", label: "Soil data", value: (f: any) => (f.ph_level || f.nitrogen ? "Yes" : "No"), render: (f: any) => (f.ph_level || f.nitrogen ? <span class="text-green-700">✓ Tested</span> : <span class="text-gray-400">—</span>) },
        { key: "is_active", label: "Status", value: (f: any) => (f.is_active ? "Active" : "Inactive") },
      ]}
    />
  );

  const CropTable = () => (
    <DataTable
      rows={crops()}
      empty="No active crops"
      columns={[
        { key: "crop_type", label: "Crop", render: (c: ActiveCrop) => <span class="font-medium capitalize">{c.crop_type}{c.crop_variety ? <span class="text-gray-400"> · {c.crop_variety}</span> : ""}</span> },
        { key: "plot_name", label: "Plot" },
        { key: "growth_stage", label: "Stage", render: (c: ActiveCrop) => <span class={`rounded-full px-2 py-0.5 text-[11px] capitalize ${STAGE_STYLE[c.growth_stage] || "bg-gray-100"}`}>{c.growth_stage}</span> },
        { key: "planting_date", label: "Sown", value: (c: ActiveCrop) => c.planting_date || "", render: (c: ActiveCrop) => date(c.planting_date) },
        { key: "days_until_harvest", label: "Harvest in", align: "right", value: (c: ActiveCrop) => c.days_until_harvest, render: (c: ActiveCrop) => (c.days_until_harvest < 0 ? "Due" : `${c.days_until_harvest}d`) },
        { key: "estimated_quantity", label: "Yield", align: "right", value: (c: ActiveCrop) => Number(c.estimated_quantity) || 0, render: (c: ActiveCrop) => `${num(Number(c.estimated_quantity) || 0)} ${c.quantity_unit || ""}` },
        { key: "total_expenses", label: "Expenses", align: "right", value: (c: ActiveCrop) => Number(c.total_expenses) || 0, render: (c: ActiveCrop) => inr(Number(c.total_expenses) || 0) },
        { key: "profit", label: "Proj. profit", align: "right", value: (c: ActiveCrop) => Number(c.projected_profit ?? c.expected_profit) || 0, render: (c: ActiveCrop) => { const p = Number(c.projected_profit ?? c.expected_profit) || 0; return <span class={p < 0 ? "text-red-700" : ""}>{inr(p)}</span>; } },
      ]}
    />
  );

  const LivestockTable = () => (
    <DataTable
      rows={herd()}
      empty="No livestock added yet"
      columns={[
        { key: "species", label: "Species", render: (l: LivestockRow) => <span class="font-medium capitalize">{l.species}</span> },
        { key: "breed", label: "Breed" },
        { key: "quantity", label: "Qty", align: "right" },
        { key: "purpose", label: "Purpose", render: (l: LivestockRow) => <span class="capitalize">{l.purpose}</span> },
        { key: "farm", label: "Farm", value: (l: LivestockRow) => props.farms.find((f) => f.id === l.farm_id)?.name || `#${l.farm_id}` },
        { key: "purchase_date", label: "Bought", value: (l: LivestockRow) => l.purchase_date || "", render: (l: LivestockRow) => date(l.purchase_date) },
        { key: "investment", label: "Investment", align: "right", value: (l: LivestockRow) => l.purchase_price * l.quantity, render: (l: LivestockRow) => inr(l.purchase_price * l.quantity) },
        { key: "expected_roi", label: "Exp. returns", align: "right", value: (l: LivestockRow) => (l.expected_roi || 0) * l.quantity, render: (l: LivestockRow) => (l.expected_roi ? inr(l.expected_roi * l.quantity) : "—") },
        { key: "break_even_date", label: "Break-even", value: (l: LivestockRow) => l.break_even_date || "", render: (l: LivestockRow) => (l.break_even_date ? (new Date(l.break_even_date) <= new Date() ? <span class="text-green-700">✓ {date(l.break_even_date)}</span> : date(l.break_even_date)) : "—") },
      ]}
    />
  );

  const SignalTable = () => (
    <DataTable
      rows={signals() || []}
      empty={signals.loading ? "Asking the AI for demand signals…" : "No demand signals yet for your items"}
      columns={[
        { key: "item_name", label: "Item", render: (s: DemandSignal) => <span class="font-medium capitalize">{s.item_name}</span> },
        { key: "item_type", label: "Type", render: (s: DemandSignal) => <span class="capitalize">{s.item_type}</span> },
        { key: "demand_level", label: "Demand", render: (s: DemandSignal) => <span class={`rounded-full px-2 py-0.5 text-[11px] capitalize ${DEMAND_STYLE[s.demand_level]?.cls}`}>{DEMAND_STYLE[s.demand_level]?.icon} {s.demand_level}</span> },
        { key: "growth_rate", label: "Growth", align: "right", render: (s: DemandSignal) => `${s.growth_rate >= 0 ? "+" : ""}${(s.growth_rate * 100).toFixed(0)}%` },
        { key: "confidence", label: "Confidence", align: "right", render: (s: DemandSignal) => `${(s.confidence * 100).toFixed(0)}%` },
        { key: "data_points", label: "Data points", align: "right" },
        { key: "state", label: "Market" },
      ]}
    />
  );

  const ProjectionTable = () => (
    <DataTable
      dense
      rows={projection()}
      columns={[
        { key: "label", label: "Month", render: (p: any) => <span>{p.label}{p.projected ? <span class="ml-1 text-violet-600">· AI</span> : ""}</span> },
        { key: "value", label: "Income", align: "right", render: (p: any) => inr(p.value) },
        { key: "range", label: "Range", align: "right", render: (p: any) => (p.projected ? `${inr(p.low)} – ${inr(p.high)}` : "actual") },
      ]}
    />
  );

  const Income = (p: { height?: number }) => (
    <ChartCard
      title="Income outlook — last 6 months & next 6"
      subtitle="Crop profit in harvest month + livestock returns spread monthly, scaled by AI demand"
      badge="AI"
      class="lg:col-span-2"
      table={ProjectionTable}
    >
      <TrendChart points={projection()} format={inr} seriesLabel="Income" height={p.height} />
    </ChartCard>
  );

  return (
    <section aria-label="Analytics board" class="space-y-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Farm Board</h2>
          <p class="text-xs text-gray-500">Everything you run, in one place — hover a chart for details, or switch it to a table.</p>
        </div>
        <div class="flex gap-1 overflow-x-auto rounded-lg bg-gray-100 p-1" role="tablist">
          <For each={TABS}>
            {(t) => (
              <button
                type="button"
                role="tab"
                aria-selected={tab() === t.id}
                onClick={() => setTab(t.id)}
                class={`whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${tab() === t.id ? "bg-white text-gray-900 shadow-sm" : "text-gray-600 hover:text-gray-900"}`}
              >
                {t.label}
              </button>
            )}
          </For>
        </div>
      </div>

      {/* KPI row is shared by every tab */}
      <div class="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <StatTile icon="🏡" label="Farms" value={String(props.farms.length)} hint={`${num(totalArea())} ${areaUnit()}`} />
        <StatTile icon="🌱" label="Active crops" value={String(crops().length)} hint={`${crops().filter((c) => c.growth_stage === "ready").length} ready`} />
        <StatTile icon="🐄" label="Livestock" value={livestock.loading ? "…" : String(headCount())} hint={`${headBySpecies().length} species`} />
        <StatTile icon="💰" label="Invested" value={inr(herdInvestment() + cropExpenses())} hint="crops + animals" />
        <StatTile icon="📈" label="Livestock ROI" value={`${Number(roi()).toFixed(1)}%`} hint="expected" />
        <StatTile
          icon="✨"
          label="Next 6 mo (AI)"
          value={inr(nextIncome())}
          delta={incomeDelta()}
          hint="projected"
          trend={projection().map((p) => p.value)}
        />
      </div>

      {/* Overview */}
      <Show when={tab() === "overview"}>
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Income />
          <ChartCard title="Where next 6 months' income comes from" table={() => <DatumTable data={incomeBySource()} format={inr} valueLabel="Income" />}>
            <DonutChart data={incomeBySource()} format={inr} centerLabel="Projected" />
          </ChartCard>
          <ChartCard title="Crops by growth stage" table={() => <DatumTable data={cropsByStage()} valueLabel="Crops" />}>
            <DonutChart data={cropsByStage()} centerLabel="Crops" />
          </ChartCard>
          <ChartCard title="Livestock by species" table={() => <DatumTable data={headBySpecies()} valueLabel="Head" />}>
            <DonutChart data={headBySpecies()} centerLabel="Head" />
          </ChartCard>
          <ChartCard title="AI insights" badge="AI">
            <ul class="space-y-2 text-sm text-gray-700">
              <For each={insights()}>{(i) => <li class="flex gap-2"><span class="text-violet-500">✦</span><span>{i}</span></li>}</For>
            </ul>
          </ChartCard>
        </div>
      </Show>

      {/* Farms & crops */}
      <Show when={tab() === "farms"}>
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <ChartCard title="Land by farm" subtitle={areaUnit()} table={() => <DatumTable data={areaByFarm()} label="Farm" valueLabel="Area" />}>
            <BarList data={areaByFarm()} color="#1baf7a" />
          </ChartCard>
          <ChartCard title="Crops by type" table={() => <DatumTable data={cropsByType()} label="Crop" valueLabel="Count" />}>
            <DonutChart data={cropsByType()} centerLabel="Crops" />
          </ChartCard>
          <ChartCard title="Days to harvest" subtitle="Soonest first" table={() => <DatumTable data={harvestSoon()} label="Crop" valueLabel="Days" />}>
            <BarList data={[...harvestSoon()].sort((a, b) => a.value - b.value)} format={(d) => `${d}d`} color="#eda100" />
          </ChartCard>
          <ChartCard
            title="Crop expenses vs projected profit"
            class="lg:col-span-3"
            table={() => <DatumTable data={cropMoney().categories.map((c, i) => ({ label: c, value: cropMoney().series[1].values[i] - cropMoney().series[0].values[i] }))} format={inr} label="Crop" valueLabel="Profit − expenses" />}
          >
            <GroupedBarChart categories={cropMoney().categories} series={cropMoney().series} format={inr} />
          </ChartCard>
          <ChartCard title="Your farms" class="lg:col-span-3"><FarmTable /></ChartCard>
          <ChartCard title="Active crops" class="lg:col-span-3"><CropTable /></ChartCard>
        </div>
      </Show>

      {/* Livestock */}
      <Show when={tab() === "livestock"}>
        <Show
          when={herd().length || livestock.loading}
          fallback={
            <div class="rounded-xl border border-dashed border-gray-300 bg-white p-8 text-center">
              <div class="text-4xl">🐄</div>
              <p class="mt-2 text-sm text-gray-600">No livestock yet. Add animals by voice with the assistant above, or by hand.</p>
              <A href="/livestock" class="mt-3 inline-block rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">Go to Livestock</A>
            </div>
          }
        >
          <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <ChartCard title="Head by species" table={() => <DatumTable data={headBySpecies()} valueLabel="Head" />}>
              <DonutChart data={headBySpecies()} centerLabel="Head" />
            </ChartCard>
            <ChartCard title="Head by purpose" table={() => <DatumTable data={headByPurpose()} valueLabel="Head" />}>
              <DonutChart data={headByPurpose()} centerLabel="Head" />
            </ChartCard>
            <ChartCard title="Portfolio health">
              <Gauge value={Number(roi())} max={100} label="Expected ROI" />
              <div class="mt-4">
                <div class="mb-1 flex justify-between text-xs text-gray-600">
                  <span>Break-even reached</span>
                  <span class="font-medium text-gray-900">{breakEven().achieved} / {breakEven().achieved + breakEven().pending}</span>
                </div>
                <div class="flex h-2.5 w-full gap-0.5 overflow-hidden rounded-full bg-gray-100">
                  <div class="h-full rounded-full bg-[#0ca30c]" style={{ width: `${(breakEven().achieved / Math.max(breakEven().achieved + breakEven().pending, 1)) * 100}%` }} />
                </div>
              </div>
            </ChartCard>
            <ChartCard
              title="Investment vs expected returns by species"
              class="lg:col-span-2"
              table={() => <DatumTable data={speciesMoney().categories.map((c, i) => ({ label: c, value: speciesMoney().series[1].values[i] - speciesMoney().series[0].values[i] }))} format={inr} label="Species" valueLabel="Returns − investment" />}
            >
              <GroupedBarChart categories={speciesMoney().categories} series={speciesMoney().series} format={inr} />
            </ChartCard>
            <ChartCard title="Animals per farm" table={() => <DatumTable data={herdByFarm()} label="Farm" valueLabel="Head" />}>
              <BarList data={herdByFarm()} color="#eb6834" />
            </ChartCard>
            <ChartCard title="Livestock register" class="lg:col-span-3"><LivestockTable /></ChartCard>
          </div>
        </Show>
      </Show>

      {/* AI projections */}
      <Show when={tab() === "ai"}>
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Income height={260} />
          <ChartCard title="AI insights" badge="AI">
            <ul class="space-y-2 text-sm text-gray-700">
              <For each={insights()}>{(i) => <li class="flex gap-2"><span class="text-violet-500">✦</span><span>{i}</span></li>}</For>
            </ul>
          </ChartCard>
          <ChartCard
            title="Market demand signals"
            subtitle={`Buyer-interest forecast for the next 90 days${defaultState() ? ` · ${defaultState()}` : ""}`}
            badge="AI"
            class="lg:col-span-3"
          >
            <SignalTable />
          </ChartCard>
        </div>
      </Show>
    </section>
  );
};

export default AnalyticsBoard;
