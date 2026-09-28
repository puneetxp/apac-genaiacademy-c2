/**
 * Crop health from space (Sentinel-2)
 * For one farm (farm page) or the farmer's farms (dashboard): the latest clear
 * satellite reading as plain words (green cover, water, trend), an NDVI trend
 * line over the last months, and true-colour + NDVI pictures of the field.
 */

import { Component, For, Show, createMemo, createResource, createSignal } from 'solid-js';
import { t } from '../../stores/i18n.store';
import type { TKey } from '../../i18n/en';
import apiClient from '../../lib/api-client';

interface Summary {
    status: 'ok' | 'no_data' | 'no_location';
    observed_on?: string;
    days_old?: number;
    ndvi?: number;
    ndmi?: number;
    ndre?: number;
    vigour?: 'bare' | 'sparse' | 'moderate' | 'dense' | 'unknown';
    water?: 'stress' | 'low' | 'ok' | null;
    trend?: 'falling' | 'rising' | 'steady' | null;
    ndvi_change?: number | null;
    flags?: string[];
}
interface Obs { observed_on: string; ndvi: number | null; ndmi: number | null; clear_pct: number | null }
interface FarmHealth {
    farm_id: number;
    farm_name: string;
    summary: Summary;
    observations: Obs[];
    images?: { true_color: string; ndvi: string } | null;
}

const VIGOUR_STYLE: Record<string, string> = {
    bare: 'bg-amber-100 text-amber-900',
    sparse: 'bg-yellow-100 text-yellow-900',
    moderate: 'bg-lime-100 text-lime-900',
    dense: 'bg-green-100 text-green-900',
    unknown: 'bg-gray-100 text-gray-700',
};
const WATER_STYLE: Record<string, string> = { stress: 'bg-red-100 text-red-800', low: 'bg-amber-100 text-amber-900', ok: 'bg-sky-100 text-sky-900' };
const TREND_ICON: Record<string, string> = { rising: '↗', falling: '↘', steady: '→' };

async function load(farmId?: number, refresh = false): Promise<FarmHealth[]> {
    if (farmId) {
        const res = await apiClient.get<{ data: FarmHealth }>(`/satellite/farm/${farmId}${refresh ? '?refresh=true' : ''}`, { cache: false, timeout: 90000 });
        return [res.data.data];
    }
    const res = await apiClient.get<{ data: FarmHealth[] }>('/satellite/my-farms', { cache: false, timeout: 90000 });
    return res.data.data || [];
}

/** NDVI over time as a small line (oldest left) */
const Trend: Component<{ obs: Obs[] }> = (props) => {
    const pts = createMemo(() => [...props.obs].filter((o) => o.ndvi != null).reverse());
    const W = 240, H = 56, P = 4;
    const path = () => {
        const p = pts();
        if (p.length < 2) return '';
        return p
            .map((o, i) => {
                const x = P + (i * (W - 2 * P)) / (p.length - 1);
                const y = H - P - ((Math.max(-0.1, Math.min(0.9, o.ndvi!)) + 0.1) / 1.0) * (H - 2 * P);
                return `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`;
            })
            .join(' ');
    };
    return (
        <Show when={pts().length >= 2}>
            <div>
                <svg viewBox={`0 0 ${W} ${H}`} class="w-full h-14" role="img" aria-label={t('sat.trendLabel')}>
                    <line x1={P} x2={W - P} y1={H - P - 0.7 * (H - 2 * P)} y2={H - P - 0.7 * (H - 2 * P)} stroke="#d1d5db" stroke-dasharray="3 3" />
                    <path d={path()} fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />
                </svg>
                <div class="flex justify-between text-[10px] text-gray-500">
                    <span>{pts()[0].observed_on}</span>
                    <span>{t('sat.healthyLine')}</span>
                    <span>{pts()[pts().length - 1].observed_on}</span>
                </div>
            </div>
        </Show>
    );
};

const SatelliteHealthCard: Component<{ farmId?: number }> = (props) => {
    const [refreshing, setRefreshing] = createSignal(false);
    const [data, { mutate }] = createResource(() => props.farmId ?? 0, (id) => load(id || undefined));
    const [index, setIndex] = createSignal(0);
    const current = () => (data() || [])[index()];

    const refresh = async () => {
        const f = current();
        if (!f || refreshing()) return;
        setRefreshing(true);
        try {
            const [fresh] = await load(f.farm_id, true);
            mutate((list) => (list || []).map((x) => (x.farm_id === f.farm_id ? { ...x, ...fresh } : x)));
        } finally {
            setRefreshing(false);
        }
    };

    return (
        <section class="bg-white rounded-lg shadow p-4 sm:p-5" aria-label={t('sat.title')}>
            <div class="flex items-start justify-between gap-2">
                <div>
                    <h2 class="text-lg font-semibold text-gray-900">🛰️ {t('sat.title')}</h2>
                    <p class="text-xs text-gray-500">{t('sat.subtitle')}</p>
                </div>
                <Show when={current()?.summary?.status === 'ok' || current()?.summary?.status === 'no_data'}>
                    <button type="button" onClick={refresh} disabled={refreshing()} class="text-sm text-green-700 hover:text-green-900 disabled:opacity-50">
                        {refreshing() ? '…' : `🔄 ${t('sat.refresh')}`}
                    </button>
                </Show>
            </div>

            <Show when={!data.loading} fallback={<div class="mt-3 h-32 bg-gray-100 animate-pulse rounded-lg" />}>
                <Show when={data.error}>
                    <p class="mt-3 text-sm text-gray-600">{t('sat.unavailable')}</p>
                </Show>
                <Show when={(data() || []).length > 1}>
                    <div class="mt-3 flex flex-wrap gap-2">
                        <For each={data()}>
                            {(f, i) => (
                                <button
                                    type="button"
                                    onClick={() => setIndex(i())}
                                    class={`px-3 py-1 rounded-full text-sm border ${i() === index() ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-700 border-gray-300'}`}
                                >
                                    {f.farm_name}
                                </button>
                            )}
                        </For>
                    </div>
                </Show>
                <Show when={current()}>
                    {(f) => (
                        <Show
                            when={f().summary?.status === 'ok'}
                            fallback={
                                <p class="mt-3 text-sm text-gray-600">
                                    {f().summary?.status === 'no_location' ? t('sat.noLocation') : t('sat.noData')}
                                </p>
                            }
                        >
                            <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="space-y-3">
                                    <p class="text-xs text-gray-500">
                                        {t('sat.seenOn', { date: f().summary.observed_on || '', days: String(f().summary.days_old ?? '') })}
                                    </p>
                                    <div class="flex flex-wrap gap-2 text-sm">
                                        <span class={`rounded-full px-3 py-1 font-medium ${VIGOUR_STYLE[f().summary.vigour || 'unknown']}`}>
                                            🌿 {t(`sat.vigour.${f().summary.vigour || 'unknown'}` as TKey)}
                                        </span>
                                        <Show when={f().summary.water}>
                                            <span class={`rounded-full px-3 py-1 font-medium ${WATER_STYLE[f().summary.water!]}`}>
                                                💧 {t(`sat.water.${f().summary.water}` as TKey)}
                                            </span>
                                        </Show>
                                        <Show when={f().summary.trend}>
                                            <span class="rounded-full px-3 py-1 bg-gray-100 text-gray-800">
                                                {TREND_ICON[f().summary.trend!]} {t(`sat.trend.${f().summary.trend}` as TKey)}
                                            </span>
                                        </Show>
                                    </div>
                                    <For each={f().summary.flags || []}>
                                        {(flag) => <p class="text-sm bg-amber-50 border border-amber-200 rounded-md p-2">⚠️ {t(`sat.flag.${flag}` as TKey)}</p>}
                                    </For>
                                    <Trend obs={f().observations} />
                                    <p class="text-[11px] text-gray-500">
                                        NDVI {f().summary.ndvi?.toFixed(2)} · NDMI {f().summary.ndmi?.toFixed(2)} · NDRE {f().summary.ndre?.toFixed(2)}
                                    </p>
                                </div>
                                <Show when={f().images}>
                                    {(img) => (
                                        <div>
                                            <div class="grid grid-cols-2 gap-2">
                                                <figure>
                                                    <img src={img().true_color} alt={t('sat.photo')} loading="lazy" class="w-full aspect-square rounded-md border object-cover bg-gray-100" />
                                                    <figcaption class="text-[11px] text-gray-500 mt-1">{t('sat.photo')}</figcaption>
                                                </figure>
                                                <figure>
                                                    <img src={img().ndvi} alt={t('sat.ndviMap')} loading="lazy" class="w-full aspect-square rounded-md border object-cover bg-gray-100" />
                                                    <figcaption class="text-[11px] text-gray-500 mt-1">{t('sat.ndviMap')}</figcaption>
                                                </figure>
                                            </div>
                                            <div class="mt-1 h-2 rounded-full" style={{ background: 'linear-gradient(to right,#a50026,#f46d43,#fee08b,#a6d96a,#1a9850)' }} />
                                            <div class="flex justify-between text-[10px] text-gray-500"><span>{t('sat.weak')}</span><span>{t('sat.strong')}</span></div>
                                        </div>
                                    )}
                                </Show>
                            </div>
                            <p class="mt-3 text-[10px] text-gray-400">{t('sat.source')}</p>
                        </Show>
                    )}
                </Show>
            </Show>
        </section>
    );
};

export default SatelliteHealthCard;
