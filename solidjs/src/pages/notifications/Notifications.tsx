import { Component, createResource, For, Show, createSignal } from 'solid-js';
import {
    FiBell,
    FiCheck,
    FiTrash2,
    FiInfo,
    FiAlertTriangle,
    FiSettings,
    FiSearch
} from 'solid-icons/fi';
import { NotificationService } from '../../shared/Service/Services';
import { onMount } from 'solid-js';


const Notifications: Component = () => {
    const [searchQuery, setSearchQuery] = createSignal('');

    onMount(() => {
        NotificationService.all();
    });

    const notifications = () => NotificationService.allstate();


    const filteredNotifications = () => {
        if (!notifications()) return [];
        return notifications()!.filter(n =>
            n.title.toLowerCase().includes(searchQuery().toLowerCase()) ||
            n.message.toLowerCase().includes(searchQuery().toLowerCase())
        );
    };

    const markAsRead = async (id: number) => {
        const n = NotificationService.findState(id);
        if (n) {
            await NotificationService.update(id, { ...n, is_read: true });
        }
    };

    const deleteNotification = async (id: number) => {
        await NotificationService.del(id);
    };


    const getIcon = (type: string) => {
        switch (type) {
            case 'alert': return <FiAlertTriangle class="text-rose-500" />;
            case 'info': return <FiInfo class="text-blue-500" />;
            default: return <FiBell class="text-indigo-500" />;
        }
    };

    return (
        <div class="min-h-screen bg-slate-50 pb-20">
            <div class="max-w-4xl mx-auto px-4 sm:px-8 py-12">
                <div class="flex justify-between items-center mb-12">
                    <div>
                        <h1 class="text-4xl font-black text-slate-900 tracking-tight flex items-center gap-3">
                            Notifications
                            <Show when={notifications()?.filter(n => !n.is_read).length}>
                                <span class="bg-rose-500 text-white text-[10px] font-black px-2 py-1 rounded-full align-top">
                                    {notifications()?.filter(n => !n.is_read).length}
                                </span>
                            </Show>
                        </h1>
                        <p class="text-slate-500 font-medium mt-1 uppercase tracking-widest text-xs">Stay updated with your farm operations</p>
                    </div>
                    <button class="p-4 bg-white rounded-2xl border border-slate-200 text-slate-400 hover:text-indigo-600 hover:border-indigo-100 transition-all shadow-sm">
                        <FiSettings class="text-xl" />
                    </button>
                </div>

                {/* Search & Bulk Actions */}
                <div class="flex gap-4 mb-8">
                    <div class="relative flex-1">
                        <FiSearch class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search updates..."
                            value={searchQuery()}
                            onInput={(e) => setSearchQuery(e.currentTarget.value)}
                            class="w-full pl-12 pr-6 py-4 bg-white border border-slate-200 rounded-2xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none font-medium"
                        />
                    </div>
                    <button class="px-6 py-4 bg-white border border-slate-200 rounded-2xl text-slate-600 font-bold hover:bg-slate-50 transition-all text-sm whitespace-nowrap">
                        Mark all read
                    </button>
                </div>

                <Show when={true} fallback={<div class="animate-pulse space-y-4">
                    <For each={[1, 2, 3]}>
                        {() => <div class="h-24 bg-white rounded-3xl" />}
                    </For>
                </div>}>

                    <div class="space-y-4">
                        <For each={filteredNotifications()} fallback={
                            <div class="text-center py-20">
                                <div class="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-300 transform scale-150 opacity-20">
                                    <FiBell />
                                </div>
                                <h3 class="text-xl font-black text-slate-400">All caught up!</h3>
                                <p class="text-slate-400 font-medium italic">No new notifications found</p>
                            </div>
                        }>
                            {(n) => (
                                <div
                                    class={`group relative bg-white p-6 rounded-3xl border transition-all flex gap-6 ${n.is_read ? 'border-slate-100 opacity-70' : 'border-indigo-50 shadow-lg shadow-indigo-100/50 ring-1 ring-indigo-500/10'
                                        }`}
                                >
                                    <div class={`w-14 h-14 rounded-2xl flex items-center justify-center text-2xl shrink-0 ${n.is_read ? 'bg-slate-50' : 'bg-indigo-50/50'
                                        }`}>
                                        {getIcon(n.type)}
                                    </div>
                                    <div class="flex-1 pr-12">
                                        <div class="flex justify-between items-start mb-1">
                                            <h3 class={`text-lg font-black tracking-tight ${n.is_read ? 'text-slate-600' : 'text-slate-900'}`}>
                                                {n.title}
                                            </h3>
                                            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest italic pt-1">
                                                {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        </div>
                                        <p class={`text-sm leading-relaxed ${n.is_read ? 'text-slate-500 font-medium' : 'text-slate-600 font-bold italic'}`}>
                                            {n.message}
                                        </p>
                                    </div>

                                    {/* Actions */}
                                    <div class="absolute right-6 top-1/2 -translate-y-1/2 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        {!n.is_read && (
                                            <button
                                                onClick={() => markAsRead(n.id)}
                                                class="p-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors"
                                            >
                                                <FiCheck />
                                            </button>
                                        )}
                                        <button
                                            onClick={() => deleteNotification(n.id)}
                                            class="p-2 bg-rose-50 text-rose-600 rounded-lg hover:bg-rose-100 transition-colors"
                                        >
                                            <FiTrash2 />
                                        </button>
                                    </div>
                                </div>
                            )}
                        </For>
                    </div>
                </Show>
            </div>
        </div>
    );
};

export default Notifications;
