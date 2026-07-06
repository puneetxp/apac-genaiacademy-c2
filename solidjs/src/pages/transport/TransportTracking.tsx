import { Component, createResource, For, Show } from 'solid-js';
import {
    FiTruck,
    FiMapPin,
    FiPackage,
    FiClock,
    FiCheckCircle,
    FiAlertCircle,
    FiPlus
} from 'solid-icons/fi';
import { onMount } from 'solid-js';
import { Transport_bookingService } from '../../shared/Service/Services';

const TransportTracking: Component = () => {
    onMount(() => {
        Transport_bookingService.all();
    });

    const bookings = () => Transport_bookingService.allstate();


    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed': return 'text-emerald-600 bg-emerald-50';
            case 'in_transit': return 'text-amber-600 bg-amber-50';
            case 'pending': return 'text-blue-600 bg-blue-50';
            default: return 'text-slate-600 bg-slate-50';
        }
    };

    return (
        <div class="min-h-screen bg-slate-50 pb-20">
            {/* Header section */}
            <div class="bg-indigo-600 px-4 sm:px-8 py-12 text-white overflow-hidden relative">
                {/* Decorative background circle */}
                <div class="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl pointer-events-none" />

                <div class="max-w-7xl mx-auto relative z-10">
                    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                        <div>
                            <div class="flex items-center gap-3 mb-2">
                                <div class="p-2 bg-white/20 rounded-xl">
                                    <FiTruck class="text-2xl" />
                                </div>
                                <h1 class="text-3xl font-black tracking-tight">Logistics Hub</h1>
                            </div>
                            <p class="text-indigo-100 font-medium italic">Streamlining the journey from farm to market</p>
                        </div>
                        <button class="bg-white text-indigo-600 hover:bg-indigo-50 px-8 py-4 rounded-2xl font-black transition-all shadow-xl shadow-indigo-900/20 flex items-center gap-2">
                            <FiPlus />
                            Book New Transport
                        </button>
                    </div>
                </div>
            </div>

            <div class="max-w-7xl mx-auto px-4 sm:px-8 -mt-8 relative z-20">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Active Bookings List */}
                    <div class="lg:col-span-2 space-y-6">
                        <div class="bg-white rounded-[40px] p-8 border border-slate-100 shadow-xl shadow-slate-200/50">
                            <h2 class="text-2xl font-black text-slate-900 mb-8">Recent Shipments</h2>

                            <Show when={true} fallback={<div class="space-y-4 animate-pulse">
                                <div class="h-32 bg-slate-100 rounded-3xl" />
                                <div class="h-32 bg-slate-100 rounded-3xl" />
                            </div>}>

                                <div class="space-y-4">
                                    <For each={bookings()}>
                                        {(booking) => (
                                            <div class="group border border-slate-100 hover:border-indigo-200 p-6 rounded-3xl transition-all cursor-pointer hover:shadow-lg hover:shadow-indigo-50">
                                                <div class="flex flex-col sm:flex-row justify-between gap-4">
                                                    <div class="flex gap-4">
                                                        <div class="w-16 h-16 bg-slate-50 flex items-center justify-center rounded-2xl group-hover:bg-indigo-50 transition-colors">
                                                            <FiPackage class="text-2xl text-slate-400 group-hover:text-indigo-600" />
                                                        </div>
                                                        <div>
                                                            <h3 class="text-lg font-black text-slate-900">#{booking.id.toString().padStart(6, '0')}</h3>
                                                            <div class="flex items-center gap-2 mt-1">
                                                                <span class={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${getStatusColor(booking.status || 'pending')}`}>
                                                                    {booking.status?.replace('_', ' ') || 'PENDING'}
                                                                </span>
                                                                <span class="text-slate-400 text-xs font-bold">• {new Date(booking.scheduled_pickup_date).toLocaleDateString()}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div class="flex flex-col items-end gap-2">
                                                        <div class="flex items-center gap-2 text-slate-600 font-black">
                                                            <span>₹{booking.total_cost?.toLocaleString()}</span>
                                                        </div>
                                                        <button class="text-indigo-600 font-bold text-sm flex items-center gap-1 group/btn">
                                                            Details <FiClock class="group-hover/btn:rotate-12 transition-transform" />
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Route preview */}
                                                <div class="mt-6 flex items-center gap-3">
                                                    <div class="flex flex-col items-center gap-1">
                                                        <FiMapPin class="text-indigo-600" />
                                                        <div class="w-0.5 h-4 bg-slate-200" />
                                                        <FiMapPin class="text-rose-500" />
                                                    </div>
                                                    <div class="flex-1 space-y-4">
                                                        <div class="text-xs">
                                                            <p class="text-slate-400 font-bold uppercase tracking-wider">Pickup</p>
                                                            <p class="text-slate-900 font-black">Farm #156, Pune District</p>
                                                        </div>
                                                        <div class="text-xs">
                                                            <p class="text-slate-400 font-bold uppercase tracking-wider">Destination</p>
                                                            <p class="text-slate-900 font-black">APMC Market, Vashi</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </For>
                                </div>
                            </Show>
                        </div>
                    </div>

                    {/* Sidebar: Tracking Stats & Helper */}
                    <div class="space-y-8">
                        <div class="bg-white rounded-[40px] p-8 border border-slate-100 shadow-xl shadow-slate-200/50">
                            <h3 class="text-xl font-black text-slate-900 mb-6">Logistics Stats</h3>
                            <div class="space-y-6">
                                <div class="flex items-center gap-4">
                                    <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center">
                                        <FiTruck />
                                    </div>
                                    <div>
                                        <p class="text-2xl font-black text-slate-900">4 Active</p>
                                        <p class="text-slate-500 text-sm font-medium italic">Shipments on road</p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-4">
                                    <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center">
                                        <FiCheckCircle />
                                    </div>
                                    <div>
                                        <p class="text-2xl font-black text-slate-900">128 Total</p>
                                        <p class="text-slate-500 text-sm font-medium italic">Successfully delivered</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bg-slate-900 rounded-[40px] p-8 text-white relative overflow-hidden group">
                            <div class="absolute -bottom-10 -right-10 w-40 h-40 bg-indigo-500/20 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700" />
                            <FiAlertCircle class="text-4xl text-indigo-400 mb-6" />
                            <h3 class="text-xl font-black mb-2">Carrier Network</h3>
                            <p class="text-slate-400 text-sm font-medium leading-relaxed mb-6">
                                Connect with over 500+ verified rural transport providers across the state. Gain access to transparent pricing and live GPS tracking.
                            </p>
                            <button class="w-full py-4 bg-indigo-600 hover:bg-indigo-700 rounded-2xl font-black transition-all">
                                Expand Network
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TransportTracking;
