/**
 * Pashu Home (livestock home screen)
 * Animall-style Hindi-first home for livestock farmers: buy/sell animals,
 * know rates, milk plan, veterinary doctors nearby, my animals and top
 * animals in the area. Every tile routes to a page that already exists.
 */

import { Component, For, Show, createSignal, onMount } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import {
    FiChevronRight,
    FiPhone,
    FiMessageCircle,
    FiMapPin,
    FiCheckCircle,
    FiStar,
    FiUser,
    FiShield,
    FiTruck,
    FiBell,
    FiActivity,
} from 'solid-icons/fi';
import { LivestockService } from '../../shared/Service/Services';
import {
    LivestockMarketplaceService,
    type LivestockMarketplaceListing,
} from '../../services/livestock-marketplace.service';
import {
    VeterinaryDoctorsService,
    type VeterinaryDoctor,
} from '../../services/veterinary-doctors.service';
import ProfileDrawer from '../../components/ui/ProfileDrawer';

const formatINR = (amount: number) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount || 0);

const PashuHome: Component = () => {
    const navigate = useNavigate();

    const [liveCount, setLiveCount] = createSignal(0);
    const [topListings, setTopListings] = createSignal<LivestockMarketplaceListing[]>([]);
    const [doctors, setDoctors] = createSignal<VeterinaryDoctor[]>([]);
    const [menuOpen, setMenuOpen] = createSignal(false);
    const [loadingDoctors, setLoadingDoctors] = createSignal(true);

    onMount(() => {
        LivestockService.all();
        // Load both sections in parallel; each fails on its own
        LivestockMarketplaceService.getListings({}, 1, 8)
            .then((res) => {
                setLiveCount(res.total || 0);
                setTopListings(res.listings || []);
            })
            .catch(() => {
                // marketplace unavailable — tiles still work, counts stay hidden
            });
        VeterinaryDoctorsService.list({})
            .then((list) => setDoctors(list.slice(0, 6)))
            .catch(() => {
                // doctor directory unavailable — section shows the empty state
            })
            .finally(() => setLoadingDoctors(false));
    });

    const myAnimals = () => LivestockService.allstate() || [];

    const priceRange = () => {
        const prices = topListings().map((l) => l.asking_price).filter(Boolean);
        if (!prices.length) return null;
        return `${formatINR(Math.min(...prices))} - ${formatINR(Math.max(...prices))}`;
    };

    const topArea = () => {
        const l = topListings()[0];
        return l ? [l.location_district, l.location_state].filter(Boolean).join(', ') : '';
    };

    const otherServices = [
        { label: 'पशु डॉक्टर', sub: 'डॉक्टर से बात करें', icon: FiPhone, path: '/livestock/doctors' },
        { label: 'पशु स्वास्थ्य', sub: 'टीका व इलाज रिकॉर्ड', icon: FiShield, path: '/livestock/hub' },
        { label: 'पशु परिवहन', sub: 'गाड़ी ट्रैक करें', icon: FiTruck, path: '/transport/tracking' },
        { label: 'सूचनाएं', sub: 'ज़रूरी अलर्ट', icon: FiBell, path: '/notifications' },
    ];

    return (
        <div class="min-h-screen bg-slate-100 pb-24">
            <ProfileDrawer open={menuOpen()} onClose={() => setMenuOpen(false)} />

            {/* Header */}
            <header class="sticky top-0 z-40 bg-teal-700 text-white px-4 pt-4 pb-3 shadow">
                <div class="max-w-3xl mx-auto flex items-center justify-between">
                    <div>
                        <h1 class="text-2xl font-bold tracking-tight">🐄 पशु सेवा</h1>
                        <p class="text-sm text-teal-100">गाय, भैंस, बकरी — हर पशु के लिए</p>
                    </div>
                    <button
                        onClick={() => setMenuOpen(true)}
                        class="w-11 h-11 rounded-full bg-amber-100 text-teal-800 flex items-center justify-center text-xl border-2 border-white"
                        aria-label="प्रोफ़ाइल"
                    >
                        <FiUser />
                    </button>
                </div>
            </header>

            <main class="max-w-3xl mx-auto px-4 pt-4 space-y-6">
                {/* Vet doctor banner */}
                <section class="bg-white border border-teal-600 rounded-2xl p-4">
                    <div class="flex items-center justify-between gap-2">
                        <span class="inline-flex items-center gap-1 bg-teal-700 text-white text-sm font-semibold px-3 py-1 rounded-full">
                            🩺 पशु डॉक्टर
                        </span>
                        <Show when={liveCount() > 0}>
                            <span class="text-sm text-slate-600">
                                <span class="bg-green-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded mr-1">LIVE</span>
                                {liveCount()} पशु बिकाऊ हैं
                            </span>
                        </Show>
                    </div>
                    <div class="flex items-center justify-between gap-3 mt-3">
                        <p class="text-xl font-bold text-slate-900 leading-snug">
                            बीमार पशु? <span class="text-teal-700">डॉक्टर से तुरंत बात करें</span>
                        </p>
                        <button
                            onClick={() => navigate('/livestock/doctors')}
                            class="shrink-0 bg-teal-700 hover:bg-teal-800 text-white font-semibold px-5 py-3 rounded-xl min-h-touch-android"
                        >
                            कॉल करें
                        </button>
                    </div>
                </section>

                {/* Buy / Sell */}
                <section class="grid grid-cols-2 gap-3">
                    <button
                        onClick={() => navigate('/livestock-marketplace')}
                        class="bg-gradient-to-br from-teal-600 to-teal-800 text-white rounded-2xl p-4 text-center shadow border-4 border-white"
                    >
                        <p class="text-xl font-bold">पशु ख़रीदें ›</p>
                        <Show when={liveCount() > 0}>
                            <p class="text-sm text-lime-300 mt-1">● {liveCount()}+ पशु</p>
                        </Show>
                        <p class="text-5xl mt-3">🐄🐃🐐</p>
                    </button>
                    <button
                        onClick={() => navigate('/marketplace/my-listings')}
                        class="bg-gradient-to-br from-teal-600 to-teal-800 text-white rounded-2xl p-4 text-center shadow border-4 border-white"
                    >
                        <p class="text-xl font-bold">पशु बेचें »</p>
                        <p class="text-sm text-lime-300 mt-1">● सही ख़रीदार पाएं</p>
                        <p class="text-5xl mt-3">🤝🐄</p>
                    </button>
                </section>

                {/* Quick tools */}
                <section class="grid grid-cols-3 gap-3">
                    <QuickTile title="रेट जानें" sub="पशु का सही रेट" emoji="🧮" onClick={() => navigate('/marketplace/intelligence')} />
                    <QuickTile title="दूध बढ़ाये" sub="योजना बनाएँ" emoji="🥛" onClick={() => navigate('/livestock/diet-plan')} />
                    <QuickTile title="पशु डॉक्टर" sub="इलाज व सलाह" emoji="🩺" onClick={() => navigate('/livestock/doctors')} />
                </section>

                {/* My animals */}
                <section>
                    <SectionHeader title="मेरे पशु" action="सब देखें" onAction={() => navigate('/livestock/hub')} />
                    <Show
                        when={myAnimals().length > 0}
                        fallback={
                            <EmptyCard text="अभी कोई पशु नहीं जोड़ा गया" cta="पशु जोड़ें" onClick={() => navigate('/livestock/hub')} />
                        }
                    >
                        <div class="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 snap-x">
                            <For each={myAnimals()}>
                                {(animal: any) => (
                                    <div class="snap-start shrink-0 w-72 bg-white rounded-2xl border border-slate-200 overflow-hidden">
                                        <div class={`flex items-center gap-2 px-3 py-2 text-sm font-medium ${animal.status === 'healthy' ? 'bg-green-50 text-green-700' : 'bg-rose-50 text-rose-700'}`}>
                                            <FiCheckCircle />
                                            {animal.status === 'healthy' ? 'पशु स्वस्थ है' : 'डॉक्टर को दिखाएं'}
                                        </div>
                                        <div class="p-3">
                                            <p class="text-lg font-bold text-slate-900 capitalize">
                                                {animal.breed || animal.species}
                                            </p>
                                            <p class="text-sm text-slate-500 capitalize">
                                                {animal.species} · संख्या {animal.quantity ?? 1}
                                            </p>
                                            <Show when={animal.status !== 'healthy'}>
                                                <button
                                                    onClick={() => navigate('/livestock/doctors')}
                                                    class="mt-3 w-full py-2 rounded-xl bg-teal-100 text-teal-800 font-semibold"
                                                >
                                                    डॉक्टर से संपर्क करें
                                                </button>
                                            </Show>
                                        </div>
                                    </div>
                                )}
                            </For>
                        </div>
                    </Show>
                </section>

                {/* Veterinary doctors */}
                <section>
                    <SectionHeader title="पास के पशु डॉक्टर" action="सब देखें" onAction={() => navigate('/livestock/doctors')} />
                    <Show
                        when={doctors().length > 0}
                        fallback={
                            <Show
                                when={!loadingDoctors()}
                                fallback={
                                    <div class="flex gap-3 overflow-hidden">
                                        <div class="shrink-0 w-64 h-36 bg-white rounded-2xl animate-pulse" />
                                        <div class="shrink-0 w-64 h-36 bg-white rounded-2xl animate-pulse" />
                                    </div>
                                }
                            >
                                <EmptyCard text="अपने इलाके के डॉक्टर खोजें या जोड़ें" cta="डॉक्टर देखें" onClick={() => navigate('/livestock/doctors')} />
                            </Show>
                        }
                    >
                        <div class="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 snap-x">
                            <For each={doctors()}>
                                {(doc) => (
                                    <div class="snap-start shrink-0 w-64 bg-white rounded-2xl border border-slate-200 p-3">
                                        <div class="flex items-start justify-between gap-2">
                                            <div class="min-w-0">
                                                <p class="font-bold text-slate-900 truncate">
                                                    डॉ. {doc.name}
                                                    <Show when={doc.verified}>
                                                        <FiCheckCircle class="inline ml-1 text-teal-600" />
                                                    </Show>
                                                </p>
                                                <p class="text-xs text-slate-500 truncate">{doc.specialization || doc.clinic_name || 'पशु चिकित्सक'}</p>
                                            </div>
                                            <span class={`text-[10px] font-bold px-2 py-0.5 rounded-full ${doc.available_now ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                                                {doc.available_now ? 'उपलब्ध' : 'व्यस्त'}
                                            </span>
                                        </div>
                                        <div class="flex items-center gap-3 text-xs text-slate-500 mt-2">
                                            <Show when={doc.location_district || doc.location_state}>
                                                <span class="flex items-center gap-1 truncate">
                                                    <FiMapPin /> {doc.location_district || doc.location_state}
                                                </span>
                                            </Show>
                                            <Show when={doc.total_ratings > 0}>
                                                <span class="flex items-center gap-1">
                                                    <FiStar class="text-amber-500" /> {doc.rating.toFixed(1)}
                                                </span>
                                            </Show>
                                        </div>
                                        <div class="grid grid-cols-2 gap-2 mt-3">
                                            <a
                                                href={doc.call_link || `tel:${doc.phone}`}
                                                class="flex items-center justify-center gap-1 py-2 rounded-xl bg-teal-700 text-white text-sm font-semibold"
                                            >
                                                <FiPhone /> कॉल
                                            </a>
                                            <Show
                                                when={doc.whatsapp_link || doc.whatsapp}
                                                fallback={<span class="py-2 rounded-xl bg-slate-50" />}
                                            >
                                                <a
                                                    href={doc.whatsapp_link || `https://wa.me/${(doc.whatsapp || '').replace(/\D/g, '')}`}
                                                    target="_blank"
                                                    rel="noopener"
                                                    class="flex items-center justify-center gap-1 py-2 rounded-xl bg-green-100 text-green-800 text-sm font-semibold"
                                                >
                                                    <FiMessageCircle /> WhatsApp
                                                </a>
                                            </Show>
                                        </div>
                                    </div>
                                )}
                            </For>
                        </div>
                    </Show>
                </section>

                {/* Other services */}
                <section>
                    <h2 class="text-xl font-bold text-slate-800 mb-3">अन्य सुविधाएं</h2>
                    <div class="grid grid-cols-2 gap-3">
                        <For each={otherServices}>
                            {(s) => (
                                <button
                                    onClick={() => navigate(s.path)}
                                    class="bg-white rounded-2xl p-4 flex items-center gap-3 text-left shadow-sm"
                                >
                                    <s.icon class="text-2xl text-teal-700 shrink-0" />
                                    <span class="flex-1 min-w-0">
                                        <span class="block font-bold text-teal-800">{s.label}</span>
                                        <span class="block text-xs text-slate-500">{s.sub}</span>
                                    </span>
                                    <FiChevronRight class="text-teal-700 shrink-0" />
                                </button>
                            )}
                        </For>
                    </div>
                </section>

                {/* Top animals in area */}
                <Show when={topListings().length > 0}>
                    <section>
                        <h2 class="text-xl font-bold text-slate-800 mb-3">
                            {topArea() ? `${topArea()} में भारी मांग` : 'भारी मांग'}
                        </h2>
                        <div class="bg-white rounded-2xl p-4 shadow-sm">
                            <div class="flex items-center justify-between">
                                <p class="font-bold text-orange-600">🔶 आपके क्षेत्र के टॉप पशु</p>
                                <button onClick={() => navigate('/livestock-marketplace')} class="text-teal-700 text-sm font-semibold">
                                    और जानें ›
                                </button>
                            </div>
                            <div class="grid grid-cols-4 gap-2 mt-3">
                                <For each={topListings().slice(0, 4)}>
                                    {(l) => (
                                        <button
                                            onClick={() => navigate('/livestock-marketplace')}
                                            class="aspect-square rounded-lg bg-teal-50 hover:bg-teal-100 flex flex-col items-center justify-center text-center"
                                        >
                                            <span class="text-3xl">🐄</span>
                                            <span class="text-[10px] text-slate-600">{formatINR(l.asking_price)}</span>
                                        </button>
                                    )}
                                </For>
                            </div>
                            <Show when={priceRange()}>
                                <p class="text-lg font-bold text-slate-900 mt-3">{priceRange()}</p>
                            </Show>
                            <Show when={topArea()}>
                                <p class="text-sm text-slate-500 flex items-center gap-1 mt-1">
                                    <FiMapPin /> {topArea()}
                                </p>
                            </Show>
                        </div>
                    </section>
                </Show>

                {/* Sell CTA */}
                <section class="bg-gradient-to-r from-teal-700 to-teal-600 rounded-2xl p-5 text-white flex items-center justify-between gap-3">
                    <div>
                        <p class="text-xl font-semibold leading-snug">बेचना आसान है<br />पशु सेवा के साथ</p>
                        <button
                            onClick={() => navigate('/marketplace/my-listings')}
                            class="mt-4 bg-white text-teal-800 font-semibold px-5 py-3 rounded-xl min-h-touch-android"
                        >
                            पशु दर्ज करें
                        </button>
                    </div>
                    <span class="text-6xl">🐄🐐</span>
                </section>

                <footer class="text-center text-slate-400 py-6">
                    <p class="tracking-[0.4em] font-bold text-xl">BHARAT</p>
                    <p class="text-lg">का अपना पशु ऐप</p>
                    <FiActivity class="inline text-3xl mt-1" />
                </footer>
            </main>
        </div>
    );
};

const QuickTile: Component<{ title: string; sub: string; emoji: string; onClick: () => void }> = (props) => (
    <button
        onClick={props.onClick}
        class="bg-teal-200/70 rounded-2xl p-3 text-center border-4 border-white shadow-sm"
    >
        <p class="font-bold text-teal-900">{props.title} ›</p>
        <p class="text-xs text-teal-800 mt-0.5">{props.sub}</p>
        <p class="text-4xl mt-2">{props.emoji}</p>
    </button>
);

const SectionHeader: Component<{ title: string; action: string; onAction: () => void }> = (props) => (
    <div class="flex items-center justify-between mb-3">
        <h2 class="text-xl font-bold text-slate-800">{props.title}</h2>
        <button onClick={props.onAction} class="text-teal-700 font-semibold flex items-center">
            {props.action} <FiChevronRight />
        </button>
    </div>
);

const EmptyCard: Component<{ text: string; cta: string; onClick: () => void }> = (props) => (
    <div class="bg-white rounded-2xl p-4 flex items-center justify-between gap-3 border border-dashed border-teal-300">
        <p class="text-slate-600">{props.text}</p>
        <button onClick={props.onClick} class="shrink-0 bg-teal-700 text-white text-sm font-semibold px-4 py-2 rounded-xl">
            {props.cta}
        </button>
    </div>
);

export default PashuHome;
