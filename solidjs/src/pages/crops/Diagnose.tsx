/**
 * Check your crop — photo diagnosis
 * The farmer picks one of their crops (or types a name), takes a close-up photo,
 * and Gemini (multimodal) says what is wrong in their language: disease, pest,
 * nutrient problem or healthy, how sure it is, how urgent, and what to do in
 * IPM order (field practice → organic → chemical). Chemicals India has banned
 * are removed by the server's safety check, and doses are left to the label.
 * Every check is saved, which also feeds district-level outbreak data.
 */

import { Component, For, Show, createResource, createSignal, onCleanup } from 'solid-js';
import { A } from '@solidjs/router';
import { lang, t } from '../../stores/i18n.store';
import type { TKey } from '../../i18n/en';
import { AssistantService, type Option } from '../../services/assistant.service';
import { DiagnosisService, type Diagnosis } from '../../services/diagnosis.service';

const URGENCY_STYLE: Record<string, string> = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-amber-100 text-amber-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
};
const CATEGORY_ICON: Record<string, string> = {
    disease: '🦠', pest: '🐛', nutrient: '🧪', abiotic: '☀️', healthy: '✅', unclear: '❓',
};

const List: Component<{ title: string; items?: string[]; icon?: string }> = (props) => (
    <Show when={props.items?.length}>
        <div>
            <h3 class="text-sm font-semibold text-gray-900">{props.icon} {props.title}</h3>
            <ul class="mt-1 list-disc pl-5 space-y-0.5 text-sm text-gray-700">
                <For each={props.items}>{(item) => <li>{item}</li>}</For>
            </ul>
        </div>
    </Show>
);

const Diagnose: Component = () => {
    const [crops] = createResource(() => AssistantService.cropOptions());
    const [history, { refetch }] = createResource(() => DiagnosisService.history(8));
    const [cropId, setCropId] = createSignal<number | null>(null);
    const [cropName, setCropName] = createSignal('');
    const [photo, setPhoto] = createSignal<{ base64: string; mime: string; previewUrl: string } | null>(null);
    const [busy, setBusy] = createSignal(false);
    const [error, setError] = createSignal('');
    const [result, setResult] = createSignal<Diagnosis | null>(null);

    onCleanup(() => {
        const p = photo();
        if (p) URL.revokeObjectURL(p.previewUrl);
        window.speechSynthesis?.cancel();
    });

    const onFile = async (file?: File | null) => {
        if (!file) return;
        setError('');
        setResult(null);
        try {
            setPhoto(await DiagnosisService.prepareImage(file));
        } catch {
            setError(t('diag.badPhoto'));
        }
    };

    const run = async () => {
        const p = photo();
        if (!p || busy()) return;
        setBusy(true);
        setError('');
        setResult(null);
        try {
            const { diagnosis } = await DiagnosisService.diagnose({
                image_base64: p.base64,
                mime_type: p.mime,
                crop_id: cropId() ?? undefined,
                crop_name: cropId() ? undefined : cropName().trim() || undefined,
                lang: lang(),
            });
            setResult(diagnosis);
            refetch();
        } catch (err: any) {
            // Show the real reason (e.g. AI unavailable) instead of a made-up answer
            setError(`${t('diag.failed')} ${AssistantService.errorReason(err)}`.trim());
        } finally {
            setBusy(false);
        }
    };

    const speak = (d: Diagnosis) => {
        if (!('speechSynthesis' in window)) return;
        const text = [d.local_name || d.disease_name, d.additional_notes, ...(d.treatment?.cultural || []).slice(0, 2), ...(d.treatment?.organic || []).slice(0, 2)]
            .filter(Boolean)
            .join('. ');
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = `${d.language || lang()}-IN`;
        window.speechSynthesis.speak(u);
    };

    const askMore = (d: Diagnosis) =>
        `/assistant?q=${encodeURIComponent(t('diag.askMoreQ', { name: d.disease_name || '', crop: d.crop_identified || cropName() || '' }))}`;

    const pct = (v?: number) => `${Math.round(Math.min(Math.max(Number(v) || 0, 0), 1) * 100)}%`;

    return (
        <div class="min-h-screen bg-gray-50 pb-24">
            <header class="bg-white shadow-sm">
                <div class="max-w-3xl mx-auto px-4 py-4 flex items-center gap-3">
                    <A href="/dashboard" class="text-gray-500 hover:text-gray-800" aria-label={t('diag.back')}>←</A>
                    <div>
                        <h1 class="text-xl font-bold text-gray-900">🔬 {t('diag.title')}</h1>
                        <p class="text-sm text-gray-600">{t('diag.subtitle')}</p>
                    </div>
                </div>
            </header>

            <main class="max-w-3xl mx-auto px-4 py-6 space-y-6">
                <section class="bg-white rounded-lg shadow p-4 sm:p-6 space-y-4">
                    {/* 1. Which crop */}
                    <div>
                        <label class="block text-sm font-semibold text-gray-900 mb-1">1. {t('diag.whichCrop')}</label>
                        <Show
                            when={(crops() || []).length > 0}
                            fallback={
                                <input
                                    type="text"
                                    value={cropName()}
                                    onInput={(e) => setCropName(e.currentTarget.value)}
                                    placeholder={t('diag.cropPlaceholder')}
                                    class="w-full border border-gray-300 rounded-md px-3 py-2 outline-none focus:border-green-500"
                                />
                            }
                        >
                            <select
                                class="w-full border border-gray-300 rounded-md px-3 py-2 bg-white"
                                value={cropId() ?? ''}
                                onChange={(e) => setCropId(e.currentTarget.value ? Number(e.currentTarget.value) : null)}
                            >
                                <option value="">{t('diag.otherCrop')}</option>
                                <For each={crops() as Option[]}>{(c) => <option value={c.id}>{c.label}</option>}</For>
                            </select>
                            <Show when={!cropId()}>
                                <input
                                    type="text"
                                    value={cropName()}
                                    onInput={(e) => setCropName(e.currentTarget.value)}
                                    placeholder={t('diag.cropPlaceholder')}
                                    class="mt-2 w-full border border-gray-300 rounded-md px-3 py-2 outline-none focus:border-green-500"
                                />
                            </Show>
                        </Show>
                    </div>

                    {/* 2. Photo */}
                    <div>
                        <p class="text-sm font-semibold text-gray-900 mb-1">2. {t('diag.photo')}</p>
                        <p class="text-xs text-gray-500 mb-2">{t('diag.photoTip')}</p>
                        <div class="flex flex-wrap gap-2">
                            <label class="cursor-pointer px-4 py-2 rounded-md bg-green-600 hover:bg-green-700 text-white text-sm font-medium">
                                📷 {t('diag.takePhoto')}
                                <input type="file" accept="image/*" capture="environment" class="hidden" onChange={(e) => onFile(e.currentTarget.files?.[0])} />
                            </label>
                            <label class="cursor-pointer px-4 py-2 rounded-md border border-gray-300 hover:bg-gray-50 text-sm font-medium text-gray-700">
                                🖼️ {t('diag.gallery')}
                                <input type="file" accept="image/*" class="hidden" onChange={(e) => onFile(e.currentTarget.files?.[0])} />
                            </label>
                        </div>
                        <Show when={photo()}>
                            {(p) => <img src={p().previewUrl} alt={t('diag.photo')} class="mt-3 max-h-72 rounded-lg border object-contain" />}
                        </Show>
                    </div>

                    <button
                        type="button"
                        onClick={run}
                        disabled={!photo() || busy()}
                        class="w-full py-3 rounded-md bg-green-700 hover:bg-green-800 disabled:opacity-50 text-white font-semibold"
                    >
                        {busy() ? t('diag.checking') : `🔬 ${t('diag.check')}`}
                    </button>
                    <Show when={error()}>
                        <p class="text-sm text-red-700 bg-red-50 border border-red-200 rounded-md p-3" role="alert">{error()}</p>
                    </Show>
                </section>

                {/* Result */}
                <Show when={result()}>
                    {(r) => (
                        <section class="bg-white rounded-lg shadow p-4 sm:p-6 space-y-4" aria-live="polite">
                            <Show
                                when={r().disease_detected !== false || r().category}
                                fallback={<p class="text-sm text-gray-700">{r().error || t('diag.notPlant')}</p>}
                            >
                                <div class="flex items-start justify-between gap-3">
                                    <div>
                                        <p class="text-xs uppercase tracking-wide text-gray-500">
                                            {CATEGORY_ICON[r().category || ''] || '🔬'} {t(`diag.cat.${r().category || 'unclear'}` as TKey)}
                                            {r().crop_identified ? ` · ${r().crop_identified}` : ''}
                                        </p>
                                        <h2 class="text-2xl font-bold text-gray-900">{r().local_name || r().disease_name}</h2>
                                        <Show when={r().local_name && r().disease_name && r().local_name !== r().disease_name}>
                                            <p class="text-sm text-gray-600">{r().disease_name}</p>
                                        </Show>
                                        <Show when={r().scientific_name}>
                                            <p class="text-sm italic text-gray-500">{r().scientific_name}</p>
                                        </Show>
                                    </div>
                                    <button type="button" onClick={() => speak(r())} class="shrink-0 text-sm text-green-700 hover:text-green-900 font-medium">
                                        🔊 {t('ai.listen')}
                                    </button>
                                </div>

                                <div>
                                    <div class="flex justify-between text-xs text-gray-600">
                                        <span>{t('diag.confidence')}</span>
                                        <span>{pct(r().confidence)}</span>
                                    </div>
                                    <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div class="h-full bg-green-600" style={{ width: pct(r().confidence) }} />
                                    </div>
                                </div>

                                <div class="flex flex-wrap gap-2 text-xs">
                                    <Show when={r().urgency}>
                                        <span class={`rounded-full px-2.5 py-1 font-medium ${URGENCY_STYLE[r().urgency!] || 'bg-gray-100'}`}>
                                            {t('diag.urgency')}: {r().urgency}
                                        </span>
                                    </Show>
                                    <Show when={r().severity}>
                                        <span class="rounded-full px-2.5 py-1 bg-gray-100 text-gray-800">{t('diag.severity')}: {r().severity}</span>
                                    </Show>
                                    <Show when={r().spread_risk}>
                                        <span class="rounded-full px-2.5 py-1 bg-gray-100 text-gray-800">{t('diag.spread')}: {r().spread_risk}</span>
                                    </Show>
                                </div>

                                <Show when={r().better_photo_tip && Number(r().confidence) < 0.6}>
                                    <p class="text-sm bg-amber-50 border border-amber-200 rounded-md p-3">📷 {r().better_photo_tip}</p>
                                </Show>

                                <List title={t('diag.seen')} items={r().symptoms_observed} icon="👀" />
                                <List title={t('diag.causes')} items={r().possible_causes} icon="🔎" />

                                <div class="rounded-lg border border-green-200 bg-green-50 p-3 space-y-3">
                                    <h3 class="font-semibold text-green-900">{t('diag.whatToDo')}</h3>
                                    <List title={t('diag.cultural')} items={r().treatment?.cultural} icon="🌾" />
                                    <List title={t('diag.organic')} items={r().treatment?.organic} icon="🌿" />
                                    <Show when={r().treatment?.chemical?.length}>
                                        <div>
                                            <List title={t('diag.chemical')} items={r().treatment?.chemical} icon="⚗️" />
                                            <p class="mt-1 text-xs text-gray-600">⚠️ {t('diag.labelNote')}</p>
                                        </div>
                                    </Show>
                                    <Show when={r().safety?.removed?.length}>
                                        <p class="text-xs text-red-800 bg-red-50 border border-red-200 rounded p-2">
                                            🛡️ {t('diag.removed')}{' '}
                                            {r().safety!.removed.map((x) => x.reason).join('; ')}
                                        </p>
                                    </Show>
                                </div>

                                <List title={t('diag.prevention')} items={r().prevention} icon="🛡️" />
                                <List title={t('diag.lookAlikes')} items={r().look_alikes} icon="🔁" />
                                <Show when={r().additional_notes}>
                                    <p class="text-sm text-gray-700">{r().additional_notes}</p>
                                </Show>

                                <div class="flex flex-wrap gap-2 pt-2">
                                    <A href={askMore(r())} class="px-4 py-2 rounded-md bg-green-600 hover:bg-green-700 text-white text-sm font-medium">
                                        ✦ {t('diag.askMore')}
                                    </A>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setResult(null);
                                            setPhoto(null);
                                        }}
                                        class="px-4 py-2 rounded-md border border-gray-300 hover:bg-gray-50 text-sm font-medium text-gray-700"
                                    >
                                        📷 {t('diag.again')}
                                    </button>
                                </div>
                                <p class="text-[11px] text-gray-400">{t('diag.disclaimer')}</p>
                            </Show>
                        </section>
                    )}
                </Show>

                {/* Recent checks */}
                <Show when={(history() || []).length > 0}>
                    <section class="bg-white rounded-lg shadow p-4 sm:p-6">
                        <h2 class="text-base font-semibold text-gray-900 mb-2">{t('diag.recent')}</h2>
                        <ul class="divide-y">
                            <For each={history()}>
                                {(h) => (
                                    <li class="py-2 flex items-center justify-between gap-3 text-sm">
                                        <span>
                                            {CATEGORY_ICON[h.category || ''] || '🔬'} <span class="font-medium">{h.disease_name || '—'}</span>
                                            <span class="text-gray-500"> · {h.crop_name || ''}</span>
                                        </span>
                                        <span class="text-xs text-gray-500 shrink-0">{new Date(h.created_at).toLocaleDateString()}</span>
                                    </li>
                                )}
                            </For>
                        </ul>
                    </section>
                </Show>
            </main>
        </div>
    );
};

export default Diagnose;
