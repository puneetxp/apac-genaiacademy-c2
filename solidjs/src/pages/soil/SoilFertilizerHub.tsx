/**
 * Soil & Fertilizer Hub Page
 * Integrated view for soil health, nutrient tracking, and fertilizer management
 */

import { Component, createResource, createSignal, For, Show, Suspense } from 'solid-js';
import {
    FarmService,
    Farm_plotService,
    SoilHealthService,
    SoilMapService,
    FertilizerRecommendationService,
    Fertilizer_applicationService
} from '../../shared/Service/Services';
import { onMount } from 'solid-js';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorDisplay } from '../../components/ui/ErrorDisplay';


const SoilFertilizerHub: Component = () => {
    const [selectedFarmId, setSelectedFarmId] = createSignal<number | null>(null);
    const [selectedPlotId, setSelectedPlotId] = createSignal<number | null>(null);

    onMount(() => {
        FarmService.all();
    });

    const farms = () => FarmService.allstate();
    const plots = () => Farm_plotService.allstate().filter(p => p.farm_id === selectedFarmId());

    const soilHealth = () => SoilHealthService.allstate().find(s => s.plot_id === selectedPlotId());
    const soilMaps = () => SoilMapService.allstate().filter(s => s.plot_id === selectedPlotId());
    const recommendations = () => FertilizerRecommendationService.allstate().find(r => r.plot_id === selectedPlotId());
    const history = () => Fertilizer_applicationService.allstate().filter(h => h.plot_id === selectedPlotId());

    onMount(() => {
        if (selectedFarmId()) Farm_plotService.all();
    });

    // Update data when plot selected
    onMount(() => {
        if (selectedPlotId()) {
            SoilHealthService.all();
            SoilMapService.all();
            FertilizerRecommendationService.all();
            Fertilizer_applicationService.all();
        }
    });


    return (
        <div class="min-h-screen bg-emerald-50 pb-20">
            {/* Elegant Green Header */}
            <div class="bg-gradient-to-r from-emerald-800 to-teal-900 pt-12 pb-24 px-4 sm:px-6 lg:px-8 shadow-xl">
                <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                    <div>
                        <h1 class="text-4xl font-black text-white tracking-tight">Soil & Nutrients</h1>
                        <p class="text-emerald-100 font-medium opacity-90">Maximize yield with scientific land management</p>
                    </div>

                    <div class="flex gap-4 w-full md:w-auto">
                        <select
                            onInput={(e) => {
                                setSelectedFarmId(parseInt(e.currentTarget.value));
                                setSelectedPlotId(null);
                            }}
                            class="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl px-4 py-3 text-white font-bold outline-none ring-teal-500 focus:ring-2 transition-all w-full md:w-48"
                        >
                            <option value="">Select Farm</option>
                            <For each={farms()}>
                                {(farm) => <option value={farm.id} class="text-slate-800">{farm.name}</option>}
                            </For>
                        </select>

                        <select
                            disabled={!selectedFarmId()}
                            onInput={(e) => setSelectedPlotId(parseInt(e.currentTarget.value))}
                            class="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl px-4 py-3 text-white font-bold outline-none ring-teal-500 focus:ring-2 transition-all w-full md:w-48 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <option value="">Select Plot</option>
                            <For each={plots()}>
                                {(plot) => <option value={plot.id} class="text-slate-800">{plot.plot_name}</option>}
                            </For>
                        </select>
                    </div>
                </div>
            </div>

            <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 -mt-12">
                <Show when={selectedPlotId()} fallback={
                    <div class="bg-white rounded-3xl shadow-2xl p-20 text-center border border-slate-100">
                        <div class="text-7xl mb-6">🏜️</div>
                        <h2 class="text-2xl font-black text-slate-800 mb-2">Ready to analyze your land?</h2>
                        <p class="text-slate-500 max-w-md mx-auto">Select a farm and plot from the menu above to see detailed soil health, satellite maps, and personalized fertilizer plans.</p>
                    </div>
                }>
                    <div class="space-y-8">
                        {/* Top Stats Row */}
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div class="bg-white rounded-2xl shadow-lg p-6 border border-emerald-100 text-center relative overflow-hidden group">
                                <div class="relative z-10">
                                    <p class="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-1">Health Score</p>
                                    <h3 class="text-4xl font-black text-emerald-600">{soilHealth()?.health_score || '--'}<span class="text-base font-medium text-slate-400">/100</span></h3>
                                </div>
                                <div class="absolute -right-2 -bottom-2 text-6xl opacity-5 group-hover:scale-110 transition-transform">🧬</div>
                            </div>
                            <div class="bg-white rounded-2xl shadow-lg p-6 border border-emerald-100 text-center relative overflow-hidden group">
                                <div class="relative z-10">
                                    <p class="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-1">Soil pH</p>
                                    <h3 class="text-4xl font-black text-slate-800">{soilHealth()?.ph_level || '--'}</h3>
                                </div>
                                <div class="absolute -right-2 -bottom-2 text-6xl opacity-5 group-hover:scale-110 transition-transform">🧪</div>
                            </div>
                            <div class="bg-white rounded-2xl shadow-lg p-6 border border-emerald-100 text-center relative overflow-hidden group">
                                <div class="relative z-10">
                                    <p class="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-1">Organic Carbon</p>
                                    <h3 class="text-4xl font-black text-slate-800">{soilHealth()?.organic_carbon || '--'}<span class="text-base font-medium text-slate-400">%</span></h3>
                                </div>
                                <div class="absolute -right-2 -bottom-2 text-6xl opacity-5 group-hover:scale-110 transition-transform">💎</div>
                            </div>
                            <div class="bg-white rounded-2xl shadow-lg p-6 border border-emerald-100 text-center relative overflow-hidden group">
                                <div class="relative z-10">
                                    <p class="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-1">Last Test</p>
                                    <h3 class="text-xl font-black text-slate-800 mt-2">{soilHealth()?.last_test_date ? new Date(soilHealth()!.last_test_date).toLocaleDateString() : 'No Data'}</h3>
                                </div>
                                <div class="absolute -right-2 -bottom-2 text-6xl opacity-5 group-hover:scale-110 transition-transform">🗓️</div>
                            </div>
                        </div>

                        {/* Middle Content: Maps & Recommendations */}
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <div class="bg-white rounded-3xl shadow-xl p-8 border border-slate-100 min-h-[400px]">
                                <h3 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-2">
                                    <span class="text-emerald-500">🗺️</span> Nutrient Heatmaps
                                </h3>
                                <Show when={soilMaps() && soilMaps()!.length > 0} fallback={
                                    <div class="aspect-video bg-slate-50 rounded-2xl flex items-center justify-center border-2 border-dashed border-slate-200">
                                        <p class="text-slate-400 font-bold">No satellite maps available for this plot yet.</p>
                                    </div>
                                }>
                                    <div class="space-y-4">
                                        <For each={soilMaps()}>
                                            {(map) => (
                                                <div class="relative rounded-2xl overflow-hidden border border-slate-200 group">
                                                    <img src={map.map_url} alt={map.layer_type} class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-700" />
                                                    <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-4">
                                                        <span class="text-white font-black uppercase text-xs tracking-widest">{map.layer_type} Map</span>
                                                    </div>
                                                </div>
                                            )}
                                        </For>
                                    </div>
                                </Show>
                            </div>

                            <div class="bg-white rounded-3xl shadow-xl p-8 border border-slate-100">
                                <h3 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-2">
                                    <span class="text-amber-500">🛠️</span> Nutrient Management Plan
                                </h3>
                                <Suspense fallback={<LoadingSpinner />}>
                                    <Show when={recommendations()} fallback={<p class="text-slate-500">No active fertilizer plan. Request a soil analysis to get started.</p>}>
                                        <div class="space-y-4">
                                            <div class="p-4 bg-emerald-50 rounded-2xl border border-emerald-100">
                                                <p class="text-xs font-black text-emerald-600 uppercase mb-1">Target Crop</p>
                                                <p class="text-slate-800 font-bold">{recommendations()?.crop_type} - {recommendations()?.growth_stage} Stage</p>
                                            </div>
                                            <For each={recommendations()?.recommended_fertilizers}>
                                                {(fert) => (
                                                    <div class="p-5 bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                                                        <div class="flex justify-between items-start mb-2">
                                                            <h4 class="font-black text-slate-800">{fert.name}</h4>
                                                            <span class="text-[10px] bg-amber-100 text-amber-700 font-black px-2 py-0.5 rounded uppercase">Urgent</span>
                                                        </div>
                                                        <p class="text-sm text-slate-600 mb-3">{fert.dosage} • {fert.application_method}</p>
                                                        <div class="flex items-center gap-2 text-xs font-bold text-slate-400">
                                                            <span>🕒 Ideal Timing:</span>
                                                            <span class="text-slate-700">{fert.timing}</span>
                                                        </div>
                                                    </div>
                                                )}
                                            </For>
                                        </div>
                                    </Show>
                                </Suspense>
                            </div>
                        </div>

                        {/* Bottom Content: Historial Tracking */}
                        <div class="bg-white rounded-3xl shadow-xl p-8 border border-slate-100">
                            <h3 class="text-xl font-black text-slate-800 mb-6">Fertilizer Application History</h3>
                            <Show when={history() && history()!.length > 0} fallback={<p class="text-slate-400 italic">No previous applications recorded.</p>}>
                                <div class="overflow-x-auto">
                                    <table class="w-full text-left">
                                        <thead>
                                            <tr class="text-[10px] font-black uppercase text-slate-400 tracking-widest border-b">
                                                <th class="pb-3 px-4">Date</th>
                                                <th class="pb-3 px-4">Fertilizer</th>
                                                <th class="pb-3 px-4">Amount</th>
                                                <th class="pb-3 px-4">Method</th>
                                                <th class="pb-3 px-4">Growth Stage</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <For each={history()}>
                                                {(entry) => (
                                                    <tr class="border-b last:border-0 hover:bg-slate-50 transition-colors">
                                                        <td class="py-4 px-4 text-sm font-medium text-slate-800">{new Date(entry.application_date).toLocaleDateString()}</td>
                                                        <td class="py-4 px-4 text-sm font-bold text-slate-800">{entry.fertilizer_type}</td>
                                                        <td class="py-4 px-4 text-sm text-slate-600">{entry.quantity_kg} kg</td>
                                                        <td class="py-4 px-4 text-sm text-slate-600">{entry.application_method}</td>
                                                        <td class="py-4 px-4 text-sm font-bold text-emerald-600">{entry.growth_stage}</td>
                                                    </tr>
                                                )}
                                            </For>

                                        </tbody>
                                    </table>
                                </div>
                            </Show>
                        </div>
                    </div>
                </Show>
            </main>
        </div>
    );
};

export default SoilFertilizerHub;
