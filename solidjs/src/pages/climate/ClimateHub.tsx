/**
 * Climate Hub Page
 * Dynamic dashboard for weather forecasts, severe alerts, and climate-aware farming
 */

import { Component, createResource, createSignal, For, Show, Suspense } from 'solid-js';
import { WeatherForecastService, SevereAlertService } from '../../shared/Service/Services';
import { onMount } from 'solid-js';

import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { showToast } from '../../components/ui/Toast';
import {
    FiSearch,
    FiAlertTriangle,
    FiShield,
    FiAlertCircle
} from 'solid-icons/fi';
import { ErrorDisplay } from '../../components/ui/ErrorDisplay';

const ClimateHub: Component = () => {
    // Default to a central location if GPS not available
    const [lat, setLat] = createSignal(19.0760);
    const [lon, setLon] = createSignal(72.8777);

    onMount(() => {
        WeatherForecastService.all();
        SevereAlertService.all();
    });

    const forecast = () => WeatherForecastService.allstate();
    const alerts = () => SevereAlertService.allstate();


    return (
        <div class="min-h-screen bg-sky-50 pb-20">
            {/* Dynamic Background based on first forecast day */}
            <div class={`h-80 transition-all duration-1000 ${forecast()?.[0]?.condition?.includes('Rain') ? 'bg-gradient-to-br from-slate-700 to-blue-900' :
                (forecast()?.[0]?.temp_max ?? 0) > 35 ? 'bg-gradient-to-br from-orange-400 to-red-600' :
                    'bg-gradient-to-br from-sky-400 to-blue-600'
                } relative overflow-hidden flex items-center px-4 sm:px-8`}>
                {/* Decorative elements */}
                <div class="absolute top-0 right-0 p-8 text-[200px] opacity-10 pointer-events-none select-none">
                    {forecast()?.[0]?.condition?.includes('Rain') ? '🌧️' : '☀️'}
                </div>

                <div class="max-w-5xl mx-auto w-full z-10 flex flex-col md:flex-row justify-between items-center gap-8">
                    <div class="text-white text-center md:text-left">
                        <h1 class="text-4xl font-black tracking-tighter mb-2">Climate Hub</h1>
                        <p class="text-sky-100 font-medium">Hyper-local weather intelligence for your farm</p>
                        <div class="flex items-center gap-2 mt-4 bg-white/10 backdrop-blur-md rounded-full px-4 py-1 self-start inline-flex">
                            <span class="text-xs">📍 Mumbai, Maharashtra</span>
                        </div>
                    </div>

                    <Show when={forecast() && forecast()![0]}>
                        <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl flex items-center gap-6 min-w-[300px]">
                            <div class="text-6xl">{forecast()![0].icon}</div>
                            <div>
                                <p class="text-white/70 text-sm font-bold uppercase tracking-widest">{forecast()![0].condition}</p>
                                <h2 class="text-5xl font-black text-white">{Math.round(forecast()![0].temp_max)}°<span class="text-2xl opacity-60">c</span></h2>
                                <div class="flex gap-4 mt-2">
                                    <span class="text-xs text-blue-200 font-bold">💧 {forecast()![0].rainfall_prob}% Rain</span>
                                    <span class="text-xs text-orange-200 font-bold">🌡️ {Math.round(forecast()![0].temp_min)}° Min</span>
                                </div>
                            </div>
                        </div>
                    </Show>
                </div>
            </div>

            <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 -mt-16">

                {/* Crucial Severe Alerts Section */}
                <Show when={alerts() && alerts()!.length > 0}>
                    <div class="mb-8 p-6 bg-rose-50 border-2 border-rose-200 rounded-3xl shadow-xl animate-pulse">
                        <h3 class="text-rose-700 font-black text-xl mb-4 flex items-center gap-2">
                            <span>⚠️</span> SEVERE WEATHER ALERTS
                        </h3>
                        <div class="space-y-4">
                            <For each={alerts()}>
                                {(alert) => (
                                    <div class="bg-white p-4 rounded-2xl border border-rose-100 shadow-sm flex gap-4">
                                        <div class="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center text-2xl shrink-0">🚩</div>
                                        <div>
                                            <p class="text-rose-800 font-bold">{alert.alert_type.toUpperCase()} - {alert.severity.toUpperCase()}</p>
                                            <p class="text-slate-600 text-sm mt-1">{alert.message}</p>
                                            <div class="mt-3 p-3 bg-rose-50 rounded-xl border border-rose-100">
                                                <p class="text-xs font-black text-rose-700">ACT NOW: {alert.recommendation}</p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </For>
                        </div>
                    </div>
                </Show>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Weekly Forecast */}
                    <div class="lg:col-span-2 space-y-6">
                        <div class="bg-white rounded-3xl shadow-xl p-8 border border-slate-100 overflow-hidden relative">
                            <div class="absolute top-0 right-0 p-4 opacity-5 text-8xl pointer-events-none select-none">📅</div>
                            <h3 class="text-xl font-black text-slate-800 mb-8 pb-4 border-b">7-Day Forecast</h3>

                            <Suspense fallback={<LoadingSpinner />}>
                                <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-4">
                                    <For each={forecast()}>
                                        {(day) => (
                                            <div class="flex flex-col items-center p-4 rounded-2xl hover:bg-sky-50 transition-all border border-transparent hover:border-sky-100 group">
                                                <p class="text-xs font-bold text-slate-400 mb-3">{new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}</p>
                                                <div class="text-3xl mb-3 group-hover:scale-125 transition-all">{day.icon}</div>
                                                <p class="text-lg font-black text-slate-800">{Math.round(day.temp_max)}°</p>
                                                <p class="text-[10px] font-bold text-slate-400">{Math.round(day.temp_min)}°</p>
                                                <div class="mt-3 w-full bg-blue-100 rounded-full h-1">
                                                    <div class="bg-blue-500 h-full rounded-full" style={`width: ${day.rainfall_prob}%`}></div>
                                                </div>
                                                <p class="text-[8px] font-black text-blue-500 mt-1">{day.rainfall_prob}%</p>
                                            </div>
                                        )}
                                    </For>
                                </div>
                            </Suspense>
                        </div>

                        {/* Smart Agriculture Insights */}
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-gradient-to-br from-green-600 to-emerald-700 rounded-3xl shadow-xl p-8 text-white relative overflow-hidden group">
                                <div class="relative z-10">
                                    <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center text-2xl mb-4">🌱</div>
                                    <h4 class="text-xl font-bold mb-2">Planting Window</h4>
                                    <p class="text-green-100 text-sm mb-6 opacity-90 leading-relaxed">Based on next week's rainfall forecast, the optimal window for Wheat sowing starts in 3 days.</p>
                                    <button class="px-6 py-2 bg-white text-green-700 rounded-xl font-bold text-xs hover:bg-green-50 transition-all shadow-lg active:scale-95">Analyze Soil-Moisture</button>
                                </div>
                                <div class="absolute -right-4 -bottom-4 text-9xl opacity-10 group-hover:scale-110 transition-all duration-700">🌾</div>
                            </div>

                            <div class="bg-gradient-to-br from-orange-500 to-amber-600 rounded-3xl shadow-xl p-8 text-white relative overflow-hidden group">
                                <div class="relative z-10">
                                    <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center text-2xl mb-4">💧</div>
                                    <h4 class="text-xl font-bold mb-2">Irrigation Guide</h4>
                                    <p class="text-orange-100 text-sm mb-6 opacity-90 leading-relaxed">High evaporation expected this week. Consider morning irrigation to maximize water efficiency.</p>
                                    <button class="px-6 py-2 bg-white text-orange-700 rounded-xl font-bold text-xs hover:bg-orange-50 transition-all shadow-lg active:scale-95">Schedule Timer</button>
                                </div>
                                <div class="absolute -right-4 -bottom-4 text-9xl opacity-10 group-hover:scale-110 transition-all duration-700">🌦️</div>
                            </div>
                        </div>
                    </div>

                    {/* Sidebar Insights */}
                    <div class="space-y-6">
                        <div class="bg-white rounded-3xl shadow-xl p-8 border border-slate-100">
                            <h3 class="font-bold border-b pb-4 mb-6 flex items-center gap-2">
                                <span class="text-blue-500">📉</span> Historical Context
                            </h3>
                            <div class="space-y-6">
                                <div class="flex gap-4">
                                    <div class="w-1 bg-blue-400 rounded-full"></div>
                                    <div>
                                        <p class="text-[10px] font-black text-slate-400 tracking-widest uppercase">Vs Last Year</p>
                                        <p class="text-sm font-bold text-slate-800">2°C Cooler than normal for March</p>
                                    </div>
                                </div>
                                <div class="flex gap-4">
                                    <div class="w-1 bg-amber-400 rounded-full"></div>
                                    <div>
                                        <p class="text-[10px] font-black text-slate-400 tracking-widest uppercase">Rainfall Trend</p>
                                        <p class="text-sm font-bold text-slate-800">14% Less pre-monsoon shower</p>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-8 pt-6 border-t font-black text-xs text-slate-300 italic text-center uppercase tracking-[0.2em]">CropSense AI Intelligence</div>
                        </div>

                        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl shadow-xl p-8 text-white">
                            <h3 class="font-bold mb-4">Radar Visualizer</h3>
                            <div class="aspect-square bg-slate-700 rounded-2xl border-2 border-slate-600 overflow-hidden relative flex items-center justify-center group cursor-pointer">
                                <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1524661142528-76400a9bcc30?q=80&w=1470&auto=format&fit=crop')] bg-cover opacity-50 transition-transform duration-1000 group-hover:scale-110"></div>
                                <div class="absolute inset-0 bg-blue-500/20 animate-pulse"></div>
                                <div class="z-10 text-center">
                                    <div class="text-3xl mb-2">📡</div>
                                    <p class="text-[10px] font-bold tracking-widest uppercase">Open Live Radar</p>
                                </div>
                                <div class="absolute top-2 right-2 flex items-center gap-1 bg-red-500 px-2 py-0.5 rounded text-[8px] font-black animate-bounce">
                                    <span class="w-1.5 h-1.5 bg-white rounded-full"></span> LIVE
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default ClimateHub;
