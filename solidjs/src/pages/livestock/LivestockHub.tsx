import { Component, For, Show, createSignal, onMount } from 'solid-js';

import {
    FiPlus,
    FiHeart,
    FiActivity,
    FiShield,
    FiTrendingUp,
    FiCalendar,
    FiAlertCircle
} from 'solid-icons/fi';
import { LivestockService, Livestock_health_recordService } from '../../shared/Service/Services';

const LivestockHub: Component = () => {
    const [selectedTab, setSelectedTab] = createSignal<'overview' | 'health' | 'production'>('overview');

    // Fetch livestock data
    onMount(() => {
        LivestockService.all();
        Livestock_health_recordService.all();
    });

    const livestock = () => LivestockService.allstate();
    const healthRecords = () => Livestock_health_recordService.allstate();


    const stats = [
        { label: 'Total Head', value: () => livestock()?.length || 0, icon: FiActivity, color: 'text-blue-600', bg: 'bg-blue-50' },
        { label: 'Healthy', value: () => livestock()?.filter(l => l.status === 'healthy').length || 0, icon: FiHeart, color: 'text-emerald-600', bg: 'bg-emerald-50' },
        { label: 'Critical', value: () => livestock()?.filter(l => l.status === 'sick' || l.status === 'critical').length || 0, icon: FiAlertCircle, color: 'text-rose-600', bg: 'bg-rose-50' },
        { label: 'Upcoming Vax', value: () => 12, icon: FiShield, color: 'text-amber-600', bg: 'bg-amber-50' },
    ];

    return (
        <div class="min-h-screen bg-slate-50 pb-20">
            {/* Header section with Glassmorphism */}
            <div class="bg-white border-b border-slate-200 px-4 sm:px-8 py-8">
                <div class="max-w-7xl mx-auto">
                    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <h1 class="text-3xl font-black text-slate-900 tracking-tight">Livestock Hub</h1>
                            <p class="text-slate-500 font-medium">Precision management for your animal assets</p>
                        </div>
                        <button class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-2xl font-bold transition-all shadow-lg shadow-indigo-200 flex items-center gap-2 group">
                            <FiPlus class="group-hover:rotate-90 transition-transform" />
                            <span>Add Livestock</span>
                        </button>
                    </div>

                    {/* Stats Grid */}
                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
                        <For each={stats}>
                            {(stat) => (
                                <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                                    <div class={`w-12 h-12 ${stat.bg} ${stat.color} rounded-2xl flex items-center justify-center mb-4 text-xl`}>
                                        <stat.icon />
                                    </div>
                                    <p class="text-slate-500 text-sm font-bold uppercase tracking-wider">{stat.label}</p>
                                    <h3 class="text-2xl font-black text-slate-900 mt-1">{stat.value()}</h3>
                                </div>
                            )}
                        </For>
                    </div>
                </div>
            </div>

            <div class="max-w-7xl mx-auto px-4 sm:px-8 mt-8">
                {/* Tabs */}
                <div class="flex gap-2 p-1 bg-slate-200/50 rounded-2xl w-fit mb-8">
                    <For each={['overview', 'health', 'production'] as const}>
                        {(tab) => (
                            <button
                                onClick={() => setSelectedTab(tab)}
                                class={`px-6 py-2 rounded-xl font-bold capitalize transition-all ${selectedTab() === tab
                                    ? 'bg-white text-indigo-600 shadow-sm'
                                    : 'text-slate-500 hover:text-slate-700'
                                    }`}
                            >
                                {tab}
                            </button>
                        )}
                    </For>
                </div>

                <Show when={true} fallback={<div class="animate-pulse space-y-4">
                    <div class="h-40 bg-white rounded-3xl" />
                    <div class="h-40 bg-white rounded-3xl" />
                </div>}>

                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Main Livestock Feed */}
                        <div class="lg:col-span-2 space-y-6">
                            <h2 class="text-xl font-black text-slate-900">Current Inventory</h2>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <For each={livestock()}>
                                    {(animal) => (
                                        <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm hover:border-indigo-100 transition-all group">
                                            <div class="flex justify-between items-start mb-4">
                                                <div>
                                                    <span class="px-3 py-1 bg-indigo-50 text-indigo-600 text-xs font-bold rounded-full uppercase tracking-tighter">
                                                        {animal.species}
                                                    </span>
                                                    <h3 class="text-lg font-black text-slate-900 mt-2">{animal.breed}</h3>
                                                </div>
                                                <div class={`w-3 h-3 rounded-full ${animal.status === 'healthy' ? 'bg-emerald-500' : 'bg-rose-500'
                                                    }`} />
                                            </div>
                                            <div class="space-y-3">
                                                <div class="flex justify-between text-sm">
                                                    <span class="text-slate-500 font-medium">Quantity</span>
                                                    <span class="text-slate-900 font-bold">{animal.quantity}</span>
                                                </div>
                                                <div class="flex justify-between text-sm">
                                                    <span class="text-slate-500 font-medium">Expected ROI</span>
                                                    <span class="text-indigo-600 font-bold">{animal.expected_roi}%</span>
                                                </div>
                                            </div>
                                            <button class="w-full mt-6 py-3 bg-slate-50 text-slate-600 font-bold rounded-xl group-hover:bg-indigo-600 group-hover:text-white transition-all">
                                                View Details
                                            </button>
                                        </div>
                                    )}
                                </For>
                            </div>
                        </div>

                        {/* Sidebar: Health Alerts & Production Trends */}
                        <div class="space-y-8">
                            <div>
                                <h2 class="text-xl font-black text-slate-900 mb-6 flex items-center gap-2">
                                    <FiShield class="text-indigo-600" />
                                    Health Alerts
                                </h2>
                                <div class="bg-white rounded-3xl overflow-hidden border border-slate-100 shadow-sm">
                                    <For each={healthRecords()?.slice(0, 3)}>
                                        {(record) => (
                                            <div class="p-4 border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors cursor-pointer">
                                                <div class="flex gap-4">
                                                    <div class="w-10 h-10 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center shrink-0">
                                                        <FiAlertCircle />
                                                    </div>
                                                    <div>
                                                        <p class="text-sm font-bold text-slate-900">{record.record_type}</p>
                                                        <p class="text-xs text-slate-500 font-medium mt-1">{record.description}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </For>
                                    <button class="w-full p-4 text-center text-indigo-600 font-bold text-sm bg-indigo-50/30 hover:bg-indigo-50/50 transition-colors">
                                        View All Records
                                    </button>
                                </div>
                            </div>

                            <div class="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-3xl p-8 text-white shadow-xl">
                                <FiTrendingUp class="text-3xl mb-4" />
                                <h3 class="text-xl font-black mb-2">ROI Analytics</h3>
                                <p class="text-indigo-100 text-sm font-medium mb-6">
                                    Your livestock assets have grown by 14.2% this quarter compared to projection.
                                </p>
                                <button class="w-full py-4 bg-white/20 backdrop-blur-md hover:bg-white/30 rounded-2xl font-bold transition-all">
                                    Full Report
                                </button>
                            </div>
                        </div>
                    </div>
                </Show>
            </div>
        </div>
    );
};

export default LivestockHub;
