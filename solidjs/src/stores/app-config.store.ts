/**
 * App configuration store
 * Per-device choices for what the Dashboard shows and how much the Plant Crop
 * form asks for. Everything defaults to ON so nothing disappears until the
 * farmer switches it off on the Configuration page (/settings).
 */

import { createRoot, createSignal } from 'solid-js';

export type DashboardSection =
    | 'assistant'
    | 'services'
    | 'stats'
    | 'quickActions'
    | 'farms'
    | 'weather'
    | 'strategy'
    | 'crops'
    | 'listings'
    | 'tasks'
    | 'buyers';

export type CropField = 'variety' | 'harvestDate' | 'yield' | 'marketPrice' | 'supportingCrops';

export interface AppConfig {
    dashboard: Record<DashboardSection, boolean>;
    cropForm: Record<CropField, boolean>;
}

export const DASHBOARD_SECTIONS: { id: DashboardSection; emoji: string; label: string; hint: string }[] = [
    { id: 'assistant', emoji: '🎙️', label: 'Add livestock by voice', hint: 'AI assistant card at the top' },
    { id: 'services', emoji: '☰', label: 'All services grid', hint: 'Full services menu on the dashboard' },
    { id: 'stats', emoji: '📈', label: 'Quick stats', hint: 'Farms, crops, listings and revenue totals' },
    { id: 'quickActions', emoji: '⚡', label: 'Quick actions', hint: 'Add Farm, Get Strategy, Marketplace, My Listings' },
    { id: 'farms', emoji: '🏡', label: 'Your farms', hint: 'Farm cards with manage / analytics buttons' },
    { id: 'weather', emoji: '🌦️', label: 'Weather alerts', hint: 'Shown only when there are alerts' },
    { id: 'strategy', emoji: '📋', label: 'Strategy timeline', hint: 'Season-by-season plan progress' },
    { id: 'crops', emoji: '🌱', label: 'Active crops', hint: 'Crops currently growing' },
    { id: 'listings', emoji: '🛒', label: 'Marketplace listings', hint: 'Your active listings' },
    { id: 'tasks', emoji: '✅', label: 'Upcoming tasks', hint: 'Milestones due soon' },
    { id: 'buyers', emoji: '🧑‍💼', label: 'Buyer interests', hint: 'Buyers interested in your produce' },
];

export const CROP_FIELDS: { id: CropField; emoji: string; label: string; hint: string }[] = [
    { id: 'supportingCrops', emoji: '🌿', label: 'Supporting crops', hint: 'Inter/companion crops grown with the main crop' },
    { id: 'variety', emoji: '🏷️', label: 'Variety', hint: 'Seed variety or hybrid name' },
    { id: 'harvestDate', emoji: '📅', label: 'Expected harvest date', hint: 'If hidden, set to ~4 months after sowing' },
    { id: 'yield', emoji: '⚖️', label: 'Expected yield', hint: 'Quintals you expect to harvest' },
    { id: 'marketPrice', emoji: '₹', label: 'Market price', hint: 'Expected ₹ per quintal, used for profit' },
];

const allOn = <K extends string>(items: { id: K }[]) =>
    Object.fromEntries(items.map((i) => [i.id, true])) as Record<K, boolean>;

const DEFAULTS: AppConfig = {
    dashboard: allOn(DASHBOARD_SECTIONS),
    cropForm: allOn(CROP_FIELDS),
};

const STORAGE_KEY = 'app_config';

const readSaved = (): AppConfig => {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return DEFAULTS;
        const saved = JSON.parse(raw) as Partial<AppConfig>;
        // Merge so sections added later default to ON for existing users
        return {
            dashboard: { ...DEFAULTS.dashboard, ...(saved.dashboard || {}) },
            cropForm: { ...DEFAULTS.cropForm, ...(saved.cropForm || {}) },
        };
    } catch {
        return DEFAULTS;
    }
};

const store = createRoot(() => {
    const [config, setConfig] = createSignal<AppConfig>(readSaved());

    const save = (next: AppConfig) => {
        setConfig(next);
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        } catch {
            // storage blocked (private window) - keep the choice for this session only
        }
    };

    return { config, save };
});

export const appConfig = store.config;

export const showSection = (id: DashboardSection) => appConfig().dashboard[id] !== false;
export const showCropField = (id: CropField) => appConfig().cropForm[id] !== false;

export const setDashboardSection = (id: DashboardSection, on: boolean) =>
    store.save({ ...appConfig(), dashboard: { ...appConfig().dashboard, [id]: on } });

export const setCropField = (id: CropField, on: boolean) =>
    store.save({ ...appConfig(), cropForm: { ...appConfig().cropForm, [id]: on } });

export const resetAppConfig = () => store.save(DEFAULTS);
