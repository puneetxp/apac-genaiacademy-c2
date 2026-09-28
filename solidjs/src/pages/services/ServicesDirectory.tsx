/**
 * Services (/services)
 * Simple directory of vets, insurance, loans, shops and transport.
 * Everyone signed in can browse and call. Admins add/edit/delete any service;
 * service providers add services and manage only the ones linked to them.
 */

import { Component, For, Show, createMemo, createSignal, onMount } from 'solid-js';
import { A } from '@solidjs/router';
import LanguageSwitcher from '../../components/ui/LanguageSwitcher';
import { showToast } from '../../components/ui/Toast';
import { t } from '../../stores/i18n.store';
import type { TKey } from '../../i18n/en';
import {
    SERVICE_CATEGORIES,
    ServicesDirectory as Api,
    canManageService,
    serviceWriteScope,
    type Service,
} from '../../services/services-directory.service';

const CATEGORY_EMOJI: Record<string, string> = { vet: '🩺', insurance: '🛡️', loan: '🏦', shop: '🏪', transport: '🚚' };

type Form = Partial<Service>;
const emptyForm = (): Form => ({ category: 'vet', name: '', phone: '', available_now: true, verified: false, is_active: true });

const ServicesDirectoryPage: Component = () => {
    const [services, setServices] = createSignal<Service[]>([]);
    const [loading, setLoading] = createSignal(true);
    const [category, setCategory] = createSignal<string>('');
    const [form, setForm] = createSignal<Form | null>(null);
    const [saving, setSaving] = createSignal(false);

    const writeScope = serviceWriteScope;
    const isAdmin = () => writeScope() === 'isuper';

    const load = async () => {
        setLoading(true);
        try {
            setServices(await Api.list());
        } catch {
            showToast('error', t('services.failed'));
        } finally {
            setLoading(false);
        }
    };
    onMount(load);

    // Farmers only see active services; admins/providers also see inactive ones they manage
    const visible = createMemo(() =>
        services()
            .filter((s) => s.is_active || canManageService(s))
            .filter((s) => !category() || s.category === category()),
    );

    const set = (k: keyof Service, v: any) => setForm({ ...form()!, [k]: v });

    const save = async (e: Event) => {
        e.preventDefault();
        const f = form()!;
        if (!f.name?.trim() || !f.phone?.trim() || !f.category) return;
        setSaving(true);
        const body: Form = { ...f };
        if (body.user_id !== undefined && body.user_id !== null && String(body.user_id) !== '') body.user_id = Number(body.user_id);
        else delete body.user_id;
        try {
            if (f.id) await Api.update(f.id, body);
            else await Api.create(body);
            showToast('success', t('services.saved'));
            setForm(null);
            await load();
        } catch {
            showToast('error', t('services.failed'));
        } finally {
            setSaving(false);
        }
    };

    const remove = async (s: Service) => {
        if (!confirm(t('services.confirmDelete'))) return;
        try {
            await Api.remove(s.id);
            showToast('success', t('services.deleted'));
            await load();
        } catch {
            showToast('error', t('services.failed'));
        }
    };

    const textField = (key: keyof Service, labelKey: TKey, opts: { required?: boolean; type?: string; wide?: boolean } = {}) => (
        <label class={`block text-sm ${opts.wide ? 'sm:col-span-2' : ''}`}>
            <span class="text-gray-700">
                {t(labelKey)}
                {opts.required ? ' *' : ''}
            </span>
            <input
                type={opts.type || 'text'}
                required={opts.required}
                value={(form()?.[key] as any) ?? ''}
                onInput={(e) => set(key, e.currentTarget.value)}
                class="mt-1 w-full border border-gray-300 rounded-md px-3 py-2 outline-none focus:border-green-500"
            />
        </label>
    );

    return (
        <div class="min-h-screen bg-gray-50">
            <header class="bg-white shadow sticky top-0 z-10">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center gap-3">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900">{t('services.title')}</h1>
                        <p class="text-sm text-gray-600 mt-1">{t('services.subtitle')}</p>
                    </div>
                    <div class="flex items-center gap-3">
                        <LanguageSwitcher class="hidden sm:inline-flex" />
                        <Show when={writeScope()}>
                            <button
                                type="button"
                                onClick={() => setForm(emptyForm())}
                                class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md shadow-sm"
                            >
                                ➕ {t('services.add')}
                            </button>
                        </Show>
                    </div>
                </div>
            </header>

            <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-4">
                {/* Category tabs */}
                <div class="flex gap-2 overflow-x-auto pb-1">
                    <For each={['', ...SERVICE_CATEGORIES]}>
                        {(c) => (
                            <button
                                type="button"
                                onClick={() => setCategory(c)}
                                class={`shrink-0 px-4 py-2 rounded-full text-sm font-medium border ${category() === c ? 'bg-green-600 border-green-600 text-white' : 'bg-white border-gray-300 text-gray-700 hover:border-green-400'}`}
                            >
                                {c ? `${CATEGORY_EMOJI[c]} ${t(`cat.${c}` as TKey)}` : t('services.all')}
                            </button>
                        )}
                    </For>
                </div>

                {/* Add / edit form */}
                <Show when={form()}>
                    <form onSubmit={save} class="bg-white rounded-lg shadow-md p-6 border border-green-100 space-y-4">
                        <h2 class="text-lg font-bold text-gray-900 border-b pb-2">
                            {form()!.id ? t('services.edit') : t('services.add')}
                        </h2>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <label class="block text-sm">
                                <span class="text-gray-700">{t('field.category')} *</span>
                                <select
                                    value={form()!.category}
                                    onChange={(e) => set('category', e.currentTarget.value)}
                                    class="mt-1 w-full border border-gray-300 rounded-md px-3 py-2 outline-none focus:border-green-500"
                                >
                                    <For each={SERVICE_CATEGORIES}>
                                        {(c) => <option value={c}>{CATEGORY_EMOJI[c]} {t(`cat.${c}` as TKey)}</option>}
                                    </For>
                                </select>
                            </label>
                            {textField('name', 'field.svc_name', { required: true })}
                            {textField('organisation', 'field.organisation')}
                            {textField('phone', 'field.phone', { required: true, type: 'tel' })}
                            {textField('whatsapp', 'field.whatsapp', { type: 'tel' })}
                            {textField('email', 'field.email', { type: 'email' })}
                            {textField('location_district', 'field.location_district')}
                            {textField('location_state', 'field.location_state')}
                            {textField('languages', 'field.languages')}
                            <Show when={isAdmin()}>{textField('user_id', 'field.user_id', { type: 'number' })}</Show>
                            {textField('address', 'field.address', { wide: true })}
                            {textField('description', 'field.description', { wide: true })}
                        </div>
                        <div class="flex flex-wrap gap-4 text-sm">
                            <label class="flex items-center gap-2">
                                <input type="checkbox" checked={!!form()!.available_now} onChange={(e) => set('available_now', e.currentTarget.checked)} class="w-4 h-4 accent-green-600" />
                                {t('field.available_now')}
                            </label>
                            <Show when={isAdmin()}>
                                <label class="flex items-center gap-2">
                                    <input type="checkbox" checked={!!form()!.verified} onChange={(e) => set('verified', e.currentTarget.checked)} class="w-4 h-4 accent-green-600" />
                                    {t('field.verified')}
                                </label>
                            </Show>
                        </div>
                        <div class="flex gap-2">
                            <button type="submit" disabled={saving()} class="px-5 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white font-medium rounded-md">
                                {saving() ? '…' : t('services.save')}
                            </button>
                            <button type="button" onClick={() => setForm(null)} class="px-5 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-md">
                                {t('ai.cancel')}
                            </button>
                        </div>
                    </form>
                </Show>

                {/* List */}
                <Show
                    when={!loading()}
                    fallback={
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <For each={[1, 2, 3]}>{() => <div class="h-36 bg-white rounded-lg shadow animate-pulse" />}</For>
                        </div>
                    }
                >
                    <Show when={visible().length > 0} fallback={<p class="text-center text-gray-500 py-12">{t('services.none')}</p>}>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <For each={visible()}>
                                {(s) => (
                                    <div class={`bg-white rounded-lg shadow p-4 border ${s.is_active ? 'border-gray-100' : 'border-dashed border-gray-300 opacity-70'}`}>
                                        <div class="flex items-start justify-between gap-2">
                                            <div class="min-w-0">
                                                <p class="text-xs font-semibold text-green-700">
                                                    {CATEGORY_EMOJI[s.category] || '🧰'} {t(`cat.${s.category}` as TKey)}
                                                </p>
                                                <p class="font-bold text-gray-900 truncate">
                                                    {s.name}
                                                    <Show when={s.verified}>
                                                        <span class="ml-1 text-green-600" title={t('services.verified')}>✔</span>
                                                    </Show>
                                                </p>
                                                <Show when={s.organisation}>
                                                    <p class="text-sm text-gray-600 truncate">{s.organisation}</p>
                                                </Show>
                                            </div>
                                            <div class="flex flex-col items-end gap-1 shrink-0">
                                                <span class={`text-xs px-2 py-1 rounded ${s.available_now ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                                    {s.available_now ? t('vet.available') : t('vet.busy')}
                                                </span>
                                                <Show when={serviceWriteScope() === 'service_provider' && canManageService(s)}>
                                                    <span class="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-800">{t('services.mine')}</span>
                                                </Show>
                                            </div>
                                        </div>
                                        <Show when={s.location_district || s.location_state}>
                                            <p class="text-sm text-gray-500 mt-2">
                                                📍 {[s.location_district, s.location_state].filter(Boolean).join(', ')}
                                            </p>
                                        </Show>
                                        <Show when={s.description}>
                                            <p class="text-sm text-gray-600 mt-1 line-clamp-2">{s.description}</p>
                                        </Show>
                                        <div class="flex flex-wrap gap-2 mt-3">
                                            <a href={`tel:${s.phone}`} class="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md">
                                                📞 {t('vet.call')}
                                            </a>
                                            <Show when={s.whatsapp}>
                                                <a
                                                    href={`https://wa.me/${(s.whatsapp || '').replace(/\D/g, '')}`}
                                                    target="_blank"
                                                    rel="noopener"
                                                    class="px-3 py-1.5 border border-green-600 text-green-700 hover:bg-green-50 text-sm font-medium rounded-md"
                                                >
                                                    WhatsApp
                                                </a>
                                            </Show>
                                            <Show when={canManageService(s)}>
                                                <button
                                                    type="button"
                                                    onClick={() => setForm({ ...s })}
                                                    class="px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                                                >
                                                    ✏️ {t('services.edit')}
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => remove(s)}
                                                    class="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md"
                                                >
                                                    🗑 {t('services.delete')}
                                                </button>
                                            </Show>
                                        </div>
                                    </div>
                                )}
                            </For>
                        </div>
                    </Show>
                </Show>

                <p class="text-center text-sm text-gray-500">
                    <A href="/livestock/doctors" class="text-green-700 hover:underline">🩺 {t('card.vets')} →</A>
                </p>
            </main>
        </div>
    );
};

export default ServicesDirectoryPage;
