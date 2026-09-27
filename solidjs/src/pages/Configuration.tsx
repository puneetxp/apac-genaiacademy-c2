/**
 * Configuration (/settings)
 * Choose which sections the Dashboard shows and which extra fields the
 * Plant Crop form asks for (including supporting crops). Saved on this device.
 */

import { Component, For } from 'solid-js';
import { A } from '@solidjs/router';
import {
    CROP_FIELDS,
    DASHBOARD_SECTIONS,
    resetAppConfig,
    setCropField,
    setDashboardSection,
    showCropField,
    showSection,
} from '../stores/app-config.store';
import { showToast } from '../components/ui/Toast';

const Toggle: Component<{
    emoji: string;
    label: string;
    hint: string;
    checked: boolean;
    onChange: (on: boolean) => void;
}> = (props) => (
    <label class="flex items-center justify-between gap-4 py-3 border-b border-gray-100 last:border-0 cursor-pointer">
        <span class="flex items-start gap-3 min-w-0">
            <span class="text-xl w-7 text-center shrink-0">{props.emoji}</span>
            <span class="min-w-0">
                <span class="block font-medium text-gray-900">{props.label}</span>
                <span class="block text-sm text-gray-500">{props.hint}</span>
            </span>
        </span>
        <input
            type="checkbox"
            class="h-5 w-5 shrink-0 accent-green-600"
            checked={props.checked}
            onChange={(e) => props.onChange(e.currentTarget.checked)}
        />
    </label>
);

const Configuration: Component = () => (
    <div class="min-h-screen bg-gray-50 pb-24">
        <header class="bg-white shadow sticky top-0 z-10 px-4 sm:px-6 lg:px-8 py-4">
            <div class="max-w-3xl mx-auto flex justify-between items-center gap-3">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">Configuration</h1>
                    <p class="text-sm text-gray-600 mt-1">Pick what the dashboard shows and what the crop form asks for</p>
                </div>
                <A href="/dashboard" class="px-3 py-2 text-green-700 hover:bg-green-50 rounded-md text-sm font-medium">
                    ← Dashboard
                </A>
            </div>
        </header>

        <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
            <section class="bg-white rounded-lg shadow p-4 sm:p-6">
                <h2 class="text-lg font-semibold text-gray-900">Dashboard sections</h2>
                <p class="text-sm text-gray-500 mb-2">
                    Switched-off sections are only hidden. Everything is still in the ☰ Services menu.
                </p>
                <For each={DASHBOARD_SECTIONS}>
                    {(s) => (
                        <Toggle
                            emoji={s.emoji}
                            label={s.label}
                            hint={s.hint}
                            checked={showSection(s.id)}
                            onChange={(on) => setDashboardSection(s.id, on)}
                        />
                    )}
                </For>
            </section>

            <section class="bg-white rounded-lg shadow p-4 sm:p-6">
                <h2 class="text-lg font-semibold text-gray-900">Plant Crop form</h2>
                <p class="text-sm text-gray-500 mb-2">
                    Crop name, season, area and sowing date are always asked. Turn off the rest for a quicker form.
                </p>
                <For each={CROP_FIELDS}>
                    {(f) => (
                        <Toggle
                            emoji={f.emoji}
                            label={f.label}
                            hint={f.hint}
                            checked={showCropField(f.id)}
                            onChange={(on) => setCropField(f.id, on)}
                        />
                    )}
                </For>
            </section>

            <button
                type="button"
                class="w-full sm:w-auto px-4 py-2 text-sm text-gray-700 bg-white border border-gray-200 rounded-md hover:bg-gray-100"
                onClick={() => {
                    resetAppConfig();
                    showToast('info', 'Configuration reset: everything is shown again');
                }}
            >
                Reset to show everything
            </button>
        </main>
    </div>
);

export default Configuration;
