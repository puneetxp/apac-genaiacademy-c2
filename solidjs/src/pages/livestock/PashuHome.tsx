/**
 * Livestock Home (/livestock)
 * Entry point for livestock management, styled like the Farmer Dashboard:
 * quick actions, my animals, nearby veterinary doctors, animals for sale,
 * and other livestock services. Every link routes to an existing page.
 */

import { Component, For, Show, createSignal, onMount } from 'solid-js';
import { A, useNavigate } from '@solidjs/router';
import { LivestockService } from '../../shared/Service/Services';
import {
    LivestockMarketplaceService,
    type LivestockMarketplaceListing,
} from '../../services/livestock-marketplace.service';
import {
    VeterinaryDoctorsService,
    type VeterinaryDoctor,
} from '../../services/veterinary-doctors.service';
import ProfileDrawer from '../../components/ui/ProfileDrawer';
import AddLivestockCard from '../../components/assistant/AddLivestockCard';
import LanguageSwitcher from '../../components/ui/LanguageSwitcher';
import { t, tValue } from '../../stores/i18n.store';
import type { TKey } from '../../i18n/en';

const formatINR = (amount: number) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount || 0);

const QUICK_ACTIONS = [
    { href: '/livestock-marketplace', emoji: '🐄', key: 'qa.buy', color: 'from-green-500 to-green-600 hover:from-green-600 hover:to-green-700' },
    { href: '/marketplace/my-listings', emoji: '📝', key: 'qa.sell', color: 'from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700' },
    { href: '/livestock/doctors', emoji: '🩺', key: 'qa.vet', color: 'from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700' },
    { href: '/livestock/diet-plan', emoji: '🥛', key: 'qa.diet', color: 'from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700' },
];

const OTHER_SERVICES = [
    { href: '/livestock/hub', emoji: '💉', key: 'more.health' },
    { href: '/marketplace/intelligence', emoji: '📊', key: 'more.rates' },
    { href: '/transport/tracking', emoji: '🚚', key: 'more.transport' },
    { href: '/notifications', emoji: '🔔', key: 'more.notifications' },
];

const PashuHome: Component = () => {
    const navigate = useNavigate();

    const [liveCount, setLiveCount] = createSignal(0);
    const [topListings, setTopListings] = createSignal<LivestockMarketplaceListing[]>([]);
    const [doctors, setDoctors] = createSignal<VeterinaryDoctor[]>([]);
    const [menuOpen, setMenuOpen] = createSignal(false);
    const [loadingDoctors, setLoadingDoctors] = createSignal(true);

    onMount(() => {
        LivestockService.all();
        // Load both sections in parallel; each fails on its own
        LivestockMarketplaceService.getListings({}, 1, 6)
            .then((res) => {
                setLiveCount(res.total || 0);
                setTopListings(res.listings || []);
            })
            .catch(() => {
                // marketplace unavailable — the section stays hidden
            });
        VeterinaryDoctorsService.list({})
            .then((list) => setDoctors(list.slice(0, 6)))
            .catch(() => {
                // doctor directory unavailable — section shows the empty state
            })
            .finally(() => setLoadingDoctors(false));
    });

    const myAnimals = () => LivestockService.allstate() || [];
    const healthyCount = () => myAnimals().filter((a: any) => a.status === 'healthy').length;
    const needsCareCount = () => myAnimals().length - healthyCount();

    return (
        <div class="min-h-screen bg-gray-50">
            <ProfileDrawer open={menuOpen()} onClose={() => setMenuOpen(false)} />

            {/* Header — same pattern as Farmer Dashboard */}
            <header class="bg-white shadow sticky top-0 z-10">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div class="flex justify-between items-center gap-3">
                        <div>
                            <h1 class="text-2xl font-bold text-gray-900">{t('livestock.title')}</h1>
                            <p class="text-sm text-gray-600 mt-1">{t('livestock.subtitle')}</p>
                        </div>
                        <div class="flex items-center gap-3">
                            <LanguageSwitcher class="hidden md:inline-flex" />
                            <A
                                href="#add-livestock"
                                class="hidden sm:flex px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors shadow-sm items-center gap-2"
                            >
                                <span>➕</span> {t('livestock.addAnimal')}
                            </A>
                            <A
                                href="/dashboard"
                                class="hidden sm:block px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                            >
                                🌾 {t('livestock.dashboard')}
                            </A>
                            <button
                                type="button"
                                onClick={() => setMenuOpen(true)}
                                class="px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                                aria-label={t('livestock.menu')}
                            >
                                ☰ {t('livestock.menu')}
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
                <AddLivestockCard id="add-livestock" />
                {/* Stats */}
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Stat label={t('stat.total')} value={myAnimals().length} emoji="🐄" />
                    <Stat label={t('stat.healthy')} value={healthyCount()} emoji="✅" />
                    <Stat label={t('stat.needCare')} value={needsCareCount()} emoji="⚠️" />
                    <Stat label={t('stat.forSale')} value={liveCount()} emoji="🏷️" />
                </div>

                {/* Quick Actions */}
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <For each={QUICK_ACTIONS}>
                        {(a) => (
                            <A href={a.href} class={`p-4 bg-gradient-to-br ${a.color} text-white rounded-lg shadow-lg transition-all text-left`}>
                                <div class="text-2xl mb-2">{a.emoji}</div>
                                <h3 class="font-semibold text-lg">{t(a.key as TKey)}</h3>
                                <p class="text-sm opacity-90">{t(`${a.key}.sub` as TKey)}</p>
                            </A>
                        )}
                    </For>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* My Livestock */}
                    <Card title={t('card.myLivestock')} emoji="🐄" action={t('action.viewAll')} onAction={() => navigate('/livestock/hub')}>
                        <Show
                            when={myAnimals().length > 0}
                            fallback={
                                <Empty text={t('animal.none')} cta={t('livestock.addAnimal')} onClick={() => document.getElementById('add-livestock')?.scrollIntoView({ behavior: 'smooth' })} />
                            }
                        >
                            <ul class="divide-y divide-gray-100">
                                <For each={myAnimals().slice(0, 5)}>
                                    {(animal: any) => (
                                        <li class="py-3 flex items-center justify-between gap-3">
                                            <div class="min-w-0">
                                                <p class="font-semibold text-gray-900 capitalize truncate">{animal.breed || tValue('species', animal.species)}</p>
                                                <p class="text-sm text-gray-500 capitalize">
                                                    {tValue('species', animal.species)} · {t('animal.qty', { n: animal.quantity ?? 1 })}
                                                </p>
                                            </div>
                                            <Show
                                                when={animal.status === 'healthy'}
                                                fallback={
                                                    <button
                                                        onClick={() => navigate('/livestock/doctors')}
                                                        class="text-xs px-2 py-1 rounded bg-red-100 text-red-700 font-medium hover:bg-red-200"
                                                    >
                                                        {t('animal.needsCare')}
                                                    </button>
                                                }
                                            >
                                                <span class="text-xs px-2 py-1 rounded bg-green-100 text-green-800">{t('animal.healthy')}</span>
                                            </Show>
                                        </li>
                                    )}
                                </For>
                            </ul>
                        </Show>
                    </Card>

                    {/* Veterinary Doctors */}
                    <Card title={t('card.vets')} emoji="🩺" action={t('action.viewAll')} onAction={() => navigate('/livestock/doctors')}>
                        <Show
                            when={doctors().length > 0}
                            fallback={
                                <Show
                                    when={!loadingDoctors()}
                                    fallback={
                                        <div class="space-y-3">
                                            <div class="h-14 bg-gray-100 animate-pulse rounded-lg" />
                                            <div class="h-14 bg-gray-100 animate-pulse rounded-lg" />
                                        </div>
                                    }
                                >
                                    <Empty text={t('vet.none')} cta={t('vet.findOrAdd')} onClick={() => navigate('/livestock/doctors')} />
                                </Show>
                            }
                        >
                            <ul class="divide-y divide-gray-100">
                                <For each={doctors()}>
                                    {(doc) => (
                                        <li class="py-3 flex items-center justify-between gap-3">
                                            <div class="min-w-0">
                                                <p class="font-semibold text-gray-900 truncate">
                                                    {t('vet.dr', { name: doc.name })}
                                                    <Show when={doc.verified}>
                                                        <span class="ml-1 text-green-600" title={t('vet.verified')}>✔</span>
                                                    </Show>
                                                </p>
                                                <p class="text-sm text-gray-500 truncate">
                                                    {[doc.specialization || doc.clinic_name, doc.location_district || doc.location_state]
                                                        .filter(Boolean)
                                                        .join(' · ') || t('vet.default')}
                                                    <Show when={doc.total_ratings > 0}> · ⭐ {doc.rating.toFixed(1)}</Show>
                                                </p>
                                            </div>
                                            <div class="flex items-center gap-2 shrink-0">
                                                <span class={`hidden sm:inline text-xs px-2 py-1 rounded ${doc.available_now ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                                    {doc.available_now ? t('vet.available') : t('vet.busy')}
                                                </span>
                                                <a
                                                    href={doc.call_link || `tel:${doc.phone}`}
                                                    class="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md"
                                                >
                                                    📞 {t('vet.call')}
                                                </a>
                                                <Show when={doc.whatsapp_link || doc.whatsapp}>
                                                    <a
                                                        href={doc.whatsapp_link || `https://wa.me/${(doc.whatsapp || '').replace(/\D/g, '')}`}
                                                        target="_blank"
                                                        rel="noopener"
                                                        class="px-3 py-1.5 bg-white border border-green-600 text-green-700 hover:bg-green-50 text-sm font-medium rounded-md"
                                                    >
                                                        {t('vet.whatsapp')}
                                                    </a>
                                                </Show>
                                            </div>
                                        </li>
                                    )}
                                </For>
                            </ul>
                        </Show>
                    </Card>
                </div>

                {/* Animals for sale */}
                <Show when={topListings().length > 0}>
                    <Card title={t('card.forSale')} emoji="🏷️" action={t('action.browseAll')} onAction={() => navigate('/livestock-marketplace')}>
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            <For each={topListings()}>
                                {(l) => (
                                    <A href="/livestock-marketplace" class="bg-green-50 rounded-lg p-4 border border-green-200 hover:shadow-md transition-shadow">
                                        <div class="flex justify-between items-start gap-2">
                                            <p class="font-bold text-gray-800 text-lg">{formatINR(l.asking_price)}</p>
                                            <span class="text-xs px-2 py-1 rounded bg-green-100 text-green-800 capitalize">{tValue('health', l.health_status)}</span>
                                        </div>
                                        <p class="text-sm text-gray-600 mt-1">
                                            {t('sale.years', { n: Math.round(((l.current_age_months || 0) / 12) * 10) / 10 })}
                                            <Show when={l.milk_production_liters_per_day}> · {t('sale.litresPerDay', { n: l.milk_production_liters_per_day! })}</Show>
                                        </p>
                                        <p class="text-sm text-gray-500 mt-1">
                                            📍 {[l.location_district, l.location_state].filter(Boolean).join(', ') || '—'}
                                        </p>
                                    </A>
                                )}
                            </For>
                        </div>
                    </Card>
                </Show>

                {/* Other services */}
                <Card title={t('card.more')} emoji="🧰">
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <For each={OTHER_SERVICES}>
                            {(s) => (
                                <A href={s.href} class="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-colors">
                                    <span class="text-2xl">{s.emoji}</span>
                                    <span class="min-w-0">
                                        <span class="block font-semibold text-gray-900">{t(s.key as TKey)}</span>
                                        <span class="block text-sm text-gray-500">{t(`${s.key}.sub` as TKey)}</span>
                                    </span>
                                </A>
                            )}
                        </For>
                    </div>
                </Card>
            </main>
        </div>
    );
};

const Stat: Component<{ label: string; value: number; emoji: string }> = (props) => (
    <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center justify-between">
            <p class="text-sm text-gray-600">{props.label}</p>
            <span class="text-xl">{props.emoji}</span>
        </div>
        <p class="text-2xl font-bold text-gray-900 mt-1">{props.value}</p>
    </div>
);

const Card: Component<{ title: string; emoji: string; action?: string; onAction?: () => void; children: any }> = (props) => (
    <section class="bg-white rounded-lg shadow-md p-6 border border-green-100">
        <div class="flex justify-between items-center mb-4 border-b pb-2">
            <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                <span>{props.emoji}</span> {props.title}
            </h2>
            <Show when={props.action}>
                <button onClick={props.onAction} class="text-sm text-green-600 hover:text-green-800 font-medium">
                    {props.action} →
                </button>
            </Show>
        </div>
        {props.children}
    </section>
);

const Empty: Component<{ text: string; cta: string; onClick: () => void }> = (props) => (
    <div class="text-center py-6">
        <p class="text-gray-500 mb-3">{props.text}</p>
        <button onClick={props.onClick} class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md">
            {props.cta}
        </button>
    </div>
);

export default PashuHome;
