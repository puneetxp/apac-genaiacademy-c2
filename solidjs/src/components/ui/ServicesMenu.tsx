/**
 * Services Menu
 * One catalog of every service in the app, grouped the way farmers think
 * about them (animals, farming, market, account). Used by the profile
 * drawer, the Profile page and the /menu page so the list stays in one place.
 */

import { Component, For, Show, createMemo, createSignal } from 'solid-js';
import { useNavigate, useLocation } from '@solidjs/router';
import { FiChevronRight, FiSearch, FiX } from 'solid-icons/fi';

export interface ServiceItem {
    label: string;
    sub: string;
    emoji: string;
    path: string;
}

export interface ServiceGroup {
    title: string;
    items: ServiceItem[];
}

export const SERVICE_GROUPS: ServiceGroup[] = [
    {
        title: 'पशु सेवाएं',
        items: [
            { label: 'पशु होम', sub: 'Livestock home', emoji: '🐄', path: '/livestock' },
            { label: 'पशु डॉक्टर', sub: 'Veterinary doctors', emoji: '🩺', path: '/livestock/doctors' },
            { label: 'पशु ख़रीदें', sub: 'Buy animals', emoji: '🐃', path: '/livestock-marketplace' },
            { label: 'पशु बेचें', sub: 'Sell animals', emoji: '🤝', path: '/marketplace/my-listings' },
            { label: 'पशु स्वास्थ्य', sub: 'Health & vaccination', emoji: '💉', path: '/livestock/hub' },
            { label: 'डाइट प्लान', sub: 'Feed & milk plan', emoji: '🥛', path: '/livestock/diet-plan' },
        ],
    },
    {
        title: 'खेती',
        items: [
            { label: 'मेरा खेत', sub: 'My farm', emoji: '🏡', path: '/farm' },
            { label: 'खेत जोड़ें', sub: 'Register farm', emoji: '🚜', path: '/farm/register' },
            { label: 'मेरी फसलें', sub: 'My crops', emoji: '🌱', path: '/crops/my-crops' },
            { label: 'फसल लगाएं', sub: 'Plant a crop', emoji: '🌾', path: '/crops/plant' },
            { label: 'फसल योजना', sub: 'Annual strategy', emoji: '📋', path: '/strategy/request' },
            { label: 'मिट्टी व खाद', sub: 'Soil & fertilizer', emoji: '🧪', path: '/soil/hub' },
            { label: 'कीट व रोग', sub: 'Pest & disease', emoji: '🐛', path: '/pest-disease/hub' },
            { label: 'मौसम', sub: 'Climate', emoji: '🌦️', path: '/climate/hub' },
            { label: 'प्लॉट जांच', sub: 'Plot analysis', emoji: '🗺️', path: '/plots/analyze' },
        ],
    },
    {
        title: 'बाज़ार',
        items: [
            { label: 'मंडी', sub: 'Marketplace', emoji: '🛒', path: '/marketplace' },
            { label: 'रेट जानें', sub: 'Market rates', emoji: '🧮', path: '/marketplace/intelligence' },
            { label: 'मेरी बुकिंग', sub: 'Bookings', emoji: '📦', path: '/marketplace/bookings' },
            { label: 'ख़रीदार', sub: 'Buyer dashboard', emoji: '🧑‍💼', path: '/marketplace/buyer-dashboard' },
            { label: 'सप्लाई योजना', sub: 'Supply planning', emoji: '📈', path: '/marketplace/supply-planning' },
            { label: 'परिवहन', sub: 'Transport tracking', emoji: '🚚', path: '/transport/tracking' },
        ],
    },
    {
        title: 'मेरा खाता',
        items: [
            { label: 'प्रोफ़ाइल', sub: 'Profile', emoji: '👤', path: '/users/profile' },
            { label: 'सूचनाएं', sub: 'Notifications', emoji: '🔔', path: '/notifications' },
            { label: 'सुरक्षा', sub: 'Security', emoji: '🔒', path: '/users/security' },
            { label: 'डैशबोर्ड', sub: 'Dashboard', emoji: '📊', path: '/dashboard' },
            { label: 'AI उपयोग', sub: 'AI quota', emoji: '🤖', path: '/quota/history' },
        ],
    },
];

interface ServicesMenuProps {
    /** 'grid' = icon tiles (pages), 'list' = compact rows (drawer) */
    variant?: 'grid' | 'list';
    /** Called after navigating, e.g. to close a drawer */
    onNavigate?: () => void;
    /** Show a search box above the groups */
    searchable?: boolean;
}

const ServicesMenu: Component<ServicesMenuProps> = (props) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [query, setQuery] = createSignal('');

    const go = (path: string) => {
        navigate(path);
        props.onNavigate?.();
    };

    const isCurrent = (path: string) => location.pathname === path;

    // Match Hindi label or English line, case-insensitive
    const groups = createMemo(() => {
        const q = query().trim().toLowerCase();
        if (!q) return SERVICE_GROUPS;
        return SERVICE_GROUPS
            .map((g) => ({
                ...g,
                items: g.items.filter((i) => i.label.includes(q) || i.sub.toLowerCase().includes(q)),
            }))
            .filter((g) => g.items.length > 0);
    });

    return (
        <div class="space-y-5">
            <Show when={props.searchable}>
                <div class="relative">
                    <FiSearch class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                        type="search"
                        value={query()}
                        onInput={(e) => setQuery(e.currentTarget.value)}
                        placeholder="सेवा खोजें… (Search)"
                        class="w-full pl-10 pr-10 py-3 rounded-2xl bg-white border border-slate-200 outline-none focus:border-teal-500 text-slate-800"
                    />
                    <Show when={query()}>
                        <button
                            onClick={() => setQuery('')}
                            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400"
                            aria-label="साफ़ करें"
                        >
                            <FiX />
                        </button>
                    </Show>
                </div>
            </Show>
            <Show when={groups().length === 0}>
                <p class="text-center text-slate-500 py-6">कोई सेवा नहीं मिली</p>
            </Show>
            <For each={groups()}>
                {(group) => (
                    <section>
                        <h3 class="text-sm font-bold text-teal-800 uppercase tracking-wide mb-2">{group.title}</h3>
                        <Show
                            when={props.variant === 'list'}
                            fallback={
                                <div class="grid grid-cols-3 sm:grid-cols-4 gap-2">
                                    <For each={group.items}>
                                        {(item) => (
                                            <button
                                                onClick={() => go(item.path)}
                                                class={`bg-white rounded-2xl p-3 text-center shadow-sm border transition-colors ${isCurrent(item.path) ? 'border-teal-600 ring-2 ring-teal-600/20' : 'border-slate-100 hover:border-teal-300'}`}
                                            >
                                                <span class="block text-3xl">{item.emoji}</span>
                                                <span class="block font-bold text-sm text-slate-800 mt-1">{item.label}</span>
                                                <span class="block text-[10px] text-slate-500">{item.sub}</span>
                                            </button>
                                        )}
                                    </For>
                                </div>
                            }
                        >
                            <div class="bg-white rounded-2xl divide-y divide-slate-100 overflow-hidden">
                                <For each={group.items}>
                                    {(item) => (
                                        <button
                                            onClick={() => go(item.path)}
                                            class={`w-full flex items-center gap-3 px-3 py-3 text-left transition-colors min-h-touch-android ${isCurrent(item.path) ? 'bg-teal-50' : 'hover:bg-teal-50'}`}
                                        >
                                            <span class="text-2xl w-8 text-center">{item.emoji}</span>
                                            <span class="flex-1 min-w-0">
                                                <span class="block font-semibold text-slate-800">{item.label}</span>
                                                <span class="block text-xs text-slate-500">{item.sub}</span>
                                            </span>
                                            <FiChevronRight class="text-teal-700" />
                                        </button>
                                    )}
                                </For>
                            </div>
                        </Show>
                    </section>
                )}
            </For>
        </div>
    );
};

export default ServicesMenu;
