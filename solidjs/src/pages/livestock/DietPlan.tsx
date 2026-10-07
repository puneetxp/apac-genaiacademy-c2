/**
 * Diet Plan (/livestock/diet-plan)
 * Farmer picks the animal, weight, daily milk and pregnancy; the page shows a
 * daily feed plan (green / dry fodder, concentrate, mineral mixture, salt,
 * water) from the NDDB / ICAR thumb rules in utils/dietPlan.
 */

import { Component, For, createMemo, createSignal } from 'solid-js';
import { A } from '@solidjs/router';
import { calculateDietPlan, type DietSpecies } from '../../utils/dietPlan';
import LanguageSwitcher from '../../components/ui/LanguageSwitcher';
import { t } from '../../stores/i18n.store';
import type { TKey } from '../../i18n/en';

const SPECIES: { id: DietSpecies; emoji: string; defaultWeight: number; defaultMilk: number }[] = [
    { id: 'cow', emoji: '🐄', defaultWeight: 350, defaultMilk: 8 },
    { id: 'buffalo', emoji: '🐃', defaultWeight: 450, defaultMilk: 8 },
    { id: 'goat', emoji: '🐐', defaultWeight: 35, defaultMilk: 1 },
];

const DietPlan: Component = () => {
    const [species, setSpecies] = createSignal<DietSpecies>('cow');
    const [weight, setWeight] = createSignal(350);
    const [milk, setMilk] = createSignal(8);
    const [pregnant, setPregnant] = createSignal(false);

    const plan = createMemo(() =>
        calculateDietPlan({
            species: species(),
            weightKg: weight(),
            milkLitresPerDay: milk(),
            pregnantLastTrimester: pregnant(),
        }),
    );

    const pickSpecies = (id: DietSpecies) => {
        const s = SPECIES.find((x) => x.id === id)!;
        setSpecies(id);
        setWeight(s.defaultWeight);
        setMilk(s.defaultMilk);
    };

    const isGoat = () => species() === 'goat';

    const rows = () => [
        { emoji: '🌿', key: 'diet.green', value: `${plan().greenFodderKg} ${t('unit.kg')}` },
        { emoji: '🌾', key: 'diet.dry', value: `${plan().dryFodderKg} ${t('unit.kg')}` },
        { emoji: '🥣', key: 'diet.conc', value: `${plan().concentrateKg} ${t('unit.kg')}` },
        { emoji: '🧪', key: 'diet.mineral', value: `${plan().mineralMixtureG} ${t('unit.g')}` },
        { emoji: '🧂', key: 'diet.salt', value: `${plan().saltG} ${t('unit.g')}` },
        { emoji: '💧', key: 'diet.water', value: `${plan().waterLitres} ${t('unit.l')}` },
    ];

    return (
        <div class="min-h-screen bg-gray-50">
            <header class="bg-white shadow sticky top-0 z-10">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center gap-3">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900">{t('diet.title')}</h1>
                        <p class="text-sm text-gray-600 mt-1">{t('diet.subtitle')}</p>
                    </div>
                    <div class="flex items-center gap-3">
                    <LanguageSwitcher class="hidden sm:inline-flex" />
                    <A href="/livestock" class="px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors">
                        🐄 {t('nav.livestock')}
                    </A>
                    </div>
                </div>
            </header>

            <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Inputs */}
                    <section class="bg-white rounded-lg shadow-md p-6 border border-green-100 space-y-6">
                        <h2 class="text-xl font-bold text-gray-900 border-b pb-2">{t('diet.yourAnimal')}</h2>
                        <div class="grid grid-cols-3 gap-3">
                            <For each={SPECIES}>
                                {(s) => (
                                    <button
                                        type="button"
                                        onClick={() => pickSpecies(s.id)}
                                        class={`rounded-lg p-3 text-center border-2 transition-colors ${species() === s.id ? 'bg-green-50 border-green-600 text-green-800' : 'bg-white border-gray-200 text-gray-700 hover:border-green-300'}`}
                                    >
                                        <span class="block text-3xl">{s.emoji}</span>
                                        <span class="block font-semibold mt-1">{t(`species.${s.id}` as TKey)}</span>
                                    </button>
                                )}
                            </For>
                        </div>
                        <label class="block">
                            <span class="flex justify-between text-sm font-medium text-gray-700">
                                {t('diet.weight')} <span class="text-green-700 font-semibold">{weight()} {t('unit.kg')}</span>
                            </span>
                            <input
                                type="range"
                                min={isGoat() ? 10 : 150}
                                max={isGoat() ? 90 : 800}
                                step={isGoat() ? 1 : 10}
                                value={weight()}
                                onInput={(e) => setWeight(Number(e.currentTarget.value))}
                                class="w-full mt-2 accent-green-600"
                            />
                        </label>
                        <label class="block">
                            <span class="flex justify-between text-sm font-medium text-gray-700">
                                {t('diet.milk')} <span class="text-green-700 font-semibold">{milk()} {t('unit.l')}</span>
                            </span>
                            <input
                                type="range"
                                min={0}
                                max={isGoat() ? 5 : 30}
                                step={isGoat() ? 0.25 : 0.5}
                                value={milk()}
                                onInput={(e) => setMilk(Number(e.currentTarget.value))}
                                class="w-full mt-2 accent-green-600"
                            />
                        </label>
                        <label class="flex items-center justify-between gap-3">
                            <span class="text-sm font-medium text-gray-700">{t('diet.pregnant')}</span>
                            <input
                                type="checkbox"
                                checked={pregnant()}
                                onChange={(e) => setPregnant(e.currentTarget.checked)}
                                class="w-5 h-5 accent-green-600"
                            />
                        </label>
                    </section>

                    {/* Plan */}
                    <section class="bg-white rounded-lg shadow-md p-6 border border-green-100">
                        <h2 class="text-xl font-bold text-gray-900 border-b pb-2 mb-2">{t('diet.ration')}</h2>
                        <ul class="divide-y divide-gray-100">
                            <For each={rows()}>
                                {(r) => (
                                    <li class="flex items-center gap-3 py-3">
                                        <span class="text-2xl w-8 text-center">{r.emoji}</span>
                                        <span class="flex-1 min-w-0">
                                            <span class="block font-semibold text-gray-900">{t(r.key as TKey)}</span>
                                            <span class="block text-sm text-gray-500">{t(`${r.key}.sub` as TKey)}</span>
                                        </span>
                                        <span class="font-bold text-green-700 whitespace-nowrap">{r.value}</span>
                                    </li>
                                )}
                            </For>
                        </ul>
                    </section>
                </div>

                <section class="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h2 class="font-bold text-yellow-900 mb-2">{t('diet.tips')}</h2>
                    <ul class="space-y-1.5 text-sm text-yellow-900 list-disc pl-5">
                        <For each={plan().tips}>{(tip) => <li>{t(tip)}</li>}</For>
                    </ul>
                </section>

                <section class="mt-6 bg-white rounded-lg shadow p-4 flex flex-col sm:flex-row sm:items-center gap-3">
                    <p class="flex-1 text-sm text-gray-600">
                        ℹ️ {t('diet.disclaimer')}
                    </p>
                    <A
                        href="/livestock/doctors"
                        class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md text-center"
                    >
                        🩺 {t('diet.talkVet')}
                    </A>
                </section>
            </main>
        </div>
    );
};

export default DietPlan;
