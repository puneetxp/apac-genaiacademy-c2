/**
 * Diet Plan (दूध बढ़ाये / डाइट प्लान)
 * Farmer picks the animal, weight, daily milk and pregnancy; the page shows a
 * daily feed plan (green / dry fodder, concentrate, mineral mixture, salt,
 * water) from the NDDB / ICAR thumb rules in utils/dietPlan.
 */

import { Component, For, createMemo, createSignal } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { FiArrowLeft, FiPhone, FiInfo } from 'solid-icons/fi';
import { calculateDietPlan, type DietSpecies } from '../../utils/dietPlan';

const SPECIES: { id: DietSpecies; label: string; emoji: string; defaultWeight: number }[] = [
    { id: 'cow', label: 'गाय', emoji: '🐄', defaultWeight: 350 },
    { id: 'buffalo', label: 'भैंस', emoji: '🐃', defaultWeight: 450 },
    { id: 'goat', label: 'बकरी', emoji: '🐐', defaultWeight: 35 },
];

const DietPlan: Component = () => {
    const navigate = useNavigate();
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
        setSpecies(id);
        const s = SPECIES.find((x) => x.id === id)!;
        setWeight(s.defaultWeight);
        setMilk(id === 'goat' ? 1 : 8);
    };

    const maxWeight = () => (species() === 'goat' ? 90 : 800);
    const maxMilk = () => (species() === 'goat' ? 5 : 30);

    const rows = () => [
        { emoji: '🌿', label: 'हरा चारा', sub: 'बरसीम, नेपियर, मक्का', value: `${plan().greenFodderKg} किलो` },
        { emoji: '🌾', label: 'सूखा चारा', sub: 'भूसा, कड़बी', value: `${plan().dryFodderKg} किलो` },
        { emoji: '🥣', label: 'दाना / पशु आहार', sub: 'खल, चोकर, दलिया', value: `${plan().concentrateKg} किलो` },
        { emoji: '🧂', label: 'मिनरल मिक्सचर', sub: 'रोज़ दाने में मिलाएं', value: `${plan().mineralMixtureG} ग्राम` },
        { emoji: '🧂', label: 'नमक', sub: 'साधारण नमक', value: `${plan().saltG} ग्राम` },
        { emoji: '💧', label: 'पानी', sub: 'साफ़, ताज़ा', value: `${plan().waterLitres} लीटर` },
    ];

    return (
        <div class="min-h-screen bg-slate-100 pb-24">
            <header class="sticky top-0 z-40 bg-teal-700 text-white px-4 py-4 shadow">
                <div class="max-w-3xl mx-auto flex items-center gap-3">
                    <button onClick={() => navigate(-1)} class="p-2 -ml-2 text-xl" aria-label="वापस">
                        <FiArrowLeft />
                    </button>
                    <div>
                        <h1 class="text-xl font-bold">डाइट प्लान</h1>
                        <p class="text-sm text-teal-100">सही खुराक, ज़्यादा दूध</p>
                    </div>
                </div>
            </header>

            <main class="max-w-3xl mx-auto px-4 pt-4 space-y-4">
                {/* Species */}
                <section class="grid grid-cols-3 gap-3">
                    <For each={SPECIES}>
                        {(s) => (
                            <button
                                onClick={() => pickSpecies(s.id)}
                                class={`rounded-2xl p-3 text-center border-2 transition-colors ${species() === s.id ? 'bg-teal-700 text-white border-teal-700' : 'bg-white text-slate-800 border-transparent'}`}
                            >
                                <span class="block text-4xl">{s.emoji}</span>
                                <span class="block font-bold mt-1">{s.label}</span>
                            </button>
                        )}
                    </For>
                </section>

                {/* Inputs */}
                <section class="bg-white rounded-2xl p-4 space-y-5">
                    <label class="block">
                        <span class="flex justify-between font-semibold text-slate-800">
                            पशु का वज़न <span class="text-teal-700">{weight()} किलो</span>
                        </span>
                        <input
                            type="range"
                            min={species() === 'goat' ? 10 : 150}
                            max={maxWeight()}
                            step={species() === 'goat' ? 1 : 10}
                            value={weight()}
                            onInput={(e) => setWeight(Number(e.currentTarget.value))}
                            class="w-full mt-2 accent-teal-700"
                        />
                    </label>
                    <label class="block">
                        <span class="flex justify-between font-semibold text-slate-800">
                            रोज़ का दूध <span class="text-teal-700">{milk()} लीटर</span>
                        </span>
                        <input
                            type="range"
                            min={0}
                            max={maxMilk()}
                            step={species() === 'goat' ? 0.25 : 0.5}
                            value={milk()}
                            onInput={(e) => setMilk(Number(e.currentTarget.value))}
                            class="w-full mt-2 accent-teal-700"
                        />
                    </label>
                    <label class="flex items-center justify-between gap-3">
                        <span class="font-semibold text-slate-800">गर्भ के आख़िरी 3 महीने?</span>
                        <input
                            type="checkbox"
                            checked={pregnant()}
                            onChange={(e) => setPregnant(e.currentTarget.checked)}
                            class="w-6 h-6 accent-teal-700"
                        />
                    </label>
                </section>

                {/* Plan */}
                <section class="bg-white rounded-2xl overflow-hidden">
                    <h2 class="bg-teal-50 text-teal-900 font-bold px-4 py-3">रोज़ की खुराक</h2>
                    <div class="divide-y divide-slate-100">
                        <For each={rows()}>
                            {(r) => (
                                <div class="flex items-center gap-3 px-4 py-3">
                                    <span class="text-2xl w-8 text-center">{r.emoji}</span>
                                    <span class="flex-1 min-w-0">
                                        <span class="block font-semibold text-slate-800">{r.label}</span>
                                        <span class="block text-xs text-slate-500">{r.sub}</span>
                                    </span>
                                    <span class="font-bold text-teal-800 whitespace-nowrap">{r.value}</span>
                                </div>
                            )}
                        </For>
                    </div>
                </section>

                <section class="bg-amber-50 border border-amber-200 rounded-2xl p-4">
                    <h2 class="font-bold text-amber-900 mb-2">ज़रूरी सलाह</h2>
                    <ul class="space-y-1.5 text-sm text-amber-900 list-disc pl-5">
                        <For each={plan().tips}>{(t) => <li>{t}</li>}</For>
                    </ul>
                </section>

                <section class="bg-white rounded-2xl p-4 flex items-center gap-3">
                        <FiInfo class="text-2xl text-teal-700 shrink-0" />
                        <p class="flex-1 text-sm text-slate-600">
                            यह एक सामान्य अनुमान है। पशु की सेहत के हिसाब से डॉक्टर से सलाह ज़रूर लें।
                        </p>
                        <button
                            onClick={() => navigate('/livestock/doctors')}
                            class="shrink-0 flex items-center gap-1 bg-teal-700 text-white text-sm font-semibold px-3 py-2 rounded-xl"
                        >
                            <FiPhone /> डॉक्टर
                        </button>
                </section>
            </main>
        </div>
    );
};

export default DietPlan;
