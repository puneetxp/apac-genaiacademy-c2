/**
 * Veterinary Doctors Page
 * Find a livestock doctor and connect with them by call, WhatsApp, or email,
 * or add a doctor you know to the directory so other farmers can find them.
 */

import { Component, For, Show, createSignal, onMount } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import {
    FiPlus,
    FiPhone,
    FiMessageCircle,
    FiMail,
    FiMapPin,
    FiStar,
    FiCheckCircle,
    FiX,
    FiArrowLeft,
} from 'solid-icons/fi';
import {
    VeterinaryDoctorsService,
    type VeterinaryDoctor,
    type DoctorCreateInput,
} from '../../services/veterinary-doctors.service';

const SPECIES_OPTIONS = ['cattle', 'buffalo', 'goat', 'sheep', 'poultry'];

const emptyForm: DoctorCreateInput = {
    name: '',
    clinic_name: '',
    specialization: '',
    species_supported: [],
    phone: '',
    whatsapp: '',
    email: '',
    location_state: '',
    location_district: '',
    address: '',
    available_now: true,
    notes: '',
};

const VeterinaryDoctors: Component = () => {
    const navigate = useNavigate();
    const [doctors, setDoctors] = createSignal<VeterinaryDoctor[]>([]);
    const [loading, setLoading] = createSignal(false);
    const [error, setError] = createSignal<string | null>(null);

    const [speciesFilter, setSpeciesFilter] = createSignal('');
    const [availableOnly, setAvailableOnly] = createSignal(false);

    const [showAddForm, setShowAddForm] = createSignal(false);
    const [form, setForm] = createSignal<DoctorCreateInput>({ ...emptyForm });
    const [submitting, setSubmitting] = createSignal(false);
    const [formError, setFormError] = createSignal<string | null>(null);

    const loadDoctors = async () => {
        setLoading(true);
        setError(null);
        try {
            const results = await VeterinaryDoctorsService.list({
                species: speciesFilter() || undefined,
                available_only: availableOnly() || undefined,
            });
            setDoctors(results);
        } catch (err: any) {
            setError(err?.message || 'Failed to load doctors');
        } finally {
            setLoading(false);
        }
    };

    onMount(loadDoctors);

    const toggleSpecies = (species: string) => {
        const current = form().species_supported || [];
        const next = current.includes(species)
            ? current.filter((s) => s !== species)
            : [...current, species];
        setForm({ ...form(), species_supported: next });
    };

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        setFormError(null);

        const data = form();
        if (!data.name.trim() || !data.phone.trim()) {
            setFormError('Name and phone number are required');
            return;
        }

        setSubmitting(true);
        try {
            await VeterinaryDoctorsService.create(data);
            setForm({ ...emptyForm });
            setShowAddForm(false);
            await loadDoctors();
        } catch (err: any) {
            setFormError(err?.message || 'Failed to add doctor');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div class="min-h-screen bg-slate-50 pb-20">
            <div class="bg-white border-b border-slate-200 px-4 sm:px-8 py-8">
                <div class="max-w-7xl mx-auto">
                    <button
                        onClick={() => navigate('/livestock/hub')}
                        class="flex items-center gap-2 text-slate-500 hover:text-indigo-600 font-bold text-sm mb-4 transition-colors"
                    >
                        <FiArrowLeft /> Back to Livestock Hub
                    </button>
                    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <h1 class="text-3xl font-black text-slate-900 tracking-tight">Livestock Doctors</h1>
                            <p class="text-slate-500 font-medium">Find a doctor for your animals, or add one you trust</p>
                        </div>
                        <button
                            onClick={() => setShowAddForm(true)}
                            class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-2xl font-bold transition-all shadow-lg shadow-indigo-200 flex items-center gap-2 group"
                        >
                            <FiPlus class="group-hover:rotate-90 transition-transform" />
                            <span>Add Doctor</span>
                        </button>
                    </div>

                    {/* Filters */}
                    <div class="flex flex-wrap gap-3 mt-8">
                        <select
                            value={speciesFilter()}
                            onChange={(e) => { setSpeciesFilter(e.currentTarget.value); loadDoctors(); }}
                            class="px-4 py-2 rounded-xl border border-slate-200 font-bold text-sm text-slate-700 bg-white"
                        >
                            <option value="">All species</option>
                            <For each={SPECIES_OPTIONS}>
                                {(species) => <option value={species}>{species}</option>}
                            </For>
                        </select>
                        <button
                            onClick={() => { setAvailableOnly(!availableOnly()); loadDoctors(); }}
                            class={`px-4 py-2 rounded-xl font-bold text-sm transition-all ${availableOnly()
                                ? 'bg-emerald-600 text-white'
                                : 'bg-white border border-slate-200 text-slate-700'
                                }`}
                        >
                            Available now
                        </button>
                    </div>
                </div>
            </div>

            <div class="max-w-7xl mx-auto px-4 sm:px-8 mt-8">
                <Show when={error()}>
                    <div class="mb-6 p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-2xl font-medium">
                        {error()}
                    </div>
                </Show>

                <Show when={!loading()} fallback={
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                        <div class="h-56 bg-white rounded-3xl" />
                        <div class="h-56 bg-white rounded-3xl" />
                        <div class="h-56 bg-white rounded-3xl" />
                    </div>
                }>
                    <Show when={doctors().length > 0} fallback={
                        <div class="bg-white rounded-3xl p-12 text-center border border-slate-100">
                            <p class="text-slate-500 font-medium mb-4">No doctors found yet for this filter.</p>
                            <button
                                onClick={() => setShowAddForm(true)}
                                class="text-indigo-600 font-bold hover:underline"
                            >
                                Be the first to add one
                            </button>
                        </div>
                    }>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            <For each={doctors()}>
                                {(doctor) => (
                                    <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm hover:border-indigo-100 transition-all">
                                        <div class="flex justify-between items-start mb-3">
                                            <div>
                                                <h3 class="text-lg font-black text-slate-900">{doctor.name}</h3>
                                                <Show when={doctor.clinic_name}>
                                                    <p class="text-sm text-slate-500 font-medium">{doctor.clinic_name}</p>
                                                </Show>
                                            </div>
                                            <Show when={doctor.verified}>
                                                <span class="flex items-center gap-1 text-emerald-600 text-xs font-bold shrink-0">
                                                    <FiCheckCircle /> Verified
                                                </span>
                                            </Show>
                                        </div>

                                        <div class="flex flex-wrap gap-2 mb-4">
                                            <Show when={doctor.specialization}>
                                                <span class="px-3 py-1 bg-indigo-50 text-indigo-600 text-xs font-bold rounded-full uppercase tracking-tighter">
                                                    {doctor.specialization}
                                                </span>
                                            </Show>
                                            <For each={doctor.species_supported}>
                                                {(species) => (
                                                    <span class="px-3 py-1 bg-slate-50 text-slate-600 text-xs font-bold rounded-full capitalize">
                                                        {species}
                                                    </span>
                                                )}
                                            </For>
                                        </div>

                                        <Show when={doctor.location_district || doctor.location_state}>
                                            <div class="flex items-center gap-2 text-sm text-slate-500 font-medium mb-2">
                                                <FiMapPin />
                                                <span>{[doctor.location_district, doctor.location_state].filter(Boolean).join(', ')}</span>
                                            </div>
                                        </Show>

                                        <Show when={doctor.total_ratings > 0}>
                                            <div class="flex items-center gap-1 text-sm text-amber-600 font-bold mb-4">
                                                <FiStar />
                                                <span>{Number(doctor.rating ?? 0).toFixed(1)} ({doctor.total_ratings})</span>
                                            </div>
                                        </Show>

                                        <div class="flex gap-2 mt-4">
                                            <Show when={doctor.call_link}>
                                                <a
                                                    href={doctor.call_link}
                                                    class="flex-1 flex items-center justify-center gap-2 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition-all text-sm"
                                                >
                                                    <FiPhone /> Call
                                                </a>
                                            </Show>
                                            <Show when={doctor.whatsapp_link}>
                                                <a
                                                    href={doctor.whatsapp_link}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    class="flex-1 flex items-center justify-center gap-2 py-3 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold rounded-xl transition-all text-sm"
                                                >
                                                    <FiMessageCircle /> WhatsApp
                                                </a>
                                            </Show>
                                            <Show when={doctor.email_link}>
                                                <a
                                                    href={doctor.email_link}
                                                    class="flex items-center justify-center py-3 px-3 bg-slate-50 hover:bg-slate-100 text-slate-600 font-bold rounded-xl transition-all text-sm"
                                                >
                                                    <FiMail />
                                                </a>
                                            </Show>
                                        </div>
                                    </div>
                                )}
                            </For>
                        </div>
                    </Show>
                </Show>
            </div>

            {/* Add Doctor Modal */}
            <Show when={showAddForm()}>
                <div class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                    <div class="bg-white rounded-3xl p-8 max-w-lg w-full max-h-[90vh] overflow-y-auto">
                        <div class="flex justify-between items-center mb-6">
                            <h2 class="text-xl font-black text-slate-900">Add a Doctor</h2>
                            <button onClick={() => setShowAddForm(false)} class="text-slate-400 hover:text-slate-600">
                                <FiX class="text-xl" />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} class="space-y-4">
                            <Show when={formError()}>
                                <div class="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-sm font-medium">
                                    {formError()}
                                </div>
                            </Show>

                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-1">Name *</label>
                                <input
                                    type="text"
                                    required
                                    value={form().name}
                                    onInput={(e) => setForm({ ...form(), name: e.currentTarget.value })}
                                    class="w-full px-4 py-3 rounded-xl border border-slate-200 font-medium"
                                    placeholder="Dr. Anita Sharma"
                                />
                            </div>

                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-1">Clinic name</label>
                                <input
                                    type="text"
                                    value={form().clinic_name}
                                    onInput={(e) => setForm({ ...form(), clinic_name: e.currentTarget.value })}
                                    class="w-full px-4 py-3 rounded-xl border border-slate-200 font-medium"
                                />
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-bold text-slate-700 mb-1">Phone *</label>
                                    <input
                                        type="tel"
                                        required
                                        value={form().phone}
                                        onInput={(e) => setForm({ ...form(), phone: e.currentTarget.value })}
                                        class="w-full px-4 py-3 rounded-xl border border-slate-200 font-medium"
                                        placeholder="+91XXXXXXXXXX"
                                    />
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-700 mb-1">WhatsApp</label>
                                    <input
                                        type="tel"
                                        value={form().whatsapp}
                                        onInput={(e) => setForm({ ...form(), whatsapp: e.currentTarget.value })}
                                        class="w-full px-4 py-3 rounded-xl border border-slate-200 font-medium"
                                        placeholder="Same as phone if blank"
                                    />
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-1">Email</label>
                                <input
                                    type="email"
                                    value={form().email}
                                    onInput={(e) => setForm({ ...form(), email: e.currentTarget.value })}
                                    class="w-full px-4 py-3 rounded-xl border border-slate-200 font-medium"
                                />
                            </div>

                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-2">Species treated</label>
                                <div class="flex flex-wrap gap-2">
                                    <For each={SPECIES_OPTIONS}>
                                        {(species) => (
                                            <button
                                                type="button"
                                                onClick={() => toggleSpecies(species)}
                                                class={`px-3 py-1.5 rounded-full text-xs font-bold capitalize transition-all ${(form().species_supported || []).includes(species)
                                                    ? 'bg-indigo-600 text-white'
                                                    : 'bg-slate-50 text-slate-600'
                                                    }`}
                                            >
                                                {species}
                                            </button>
                                        )}
                                    </For>
                                </div>
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-bold text-slate-700 mb-1">State</label>
                                    <input
                                        type="text"
                                        value={form().location_state}
                                        onInput={(e) => setForm({ ...form(), location_state: e.currentTarget.value })}
                                        class="w-full px-4 py-3 rounded-xl border border-slate-200 font-medium"
                                    />
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-700 mb-1">District</label>
                                    <input
                                        type="text"
                                        value={form().location_district}
                                        onInput={(e) => setForm({ ...form(), location_district: e.currentTarget.value })}
                                        class="w-full px-4 py-3 rounded-xl border border-slate-200 font-medium"
                                    />
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-1">Notes</label>
                                <textarea
                                    value={form().notes}
                                    onInput={(e) => setForm({ ...form(), notes: e.currentTarget.value })}
                                    class="w-full px-4 py-3 rounded-xl border border-slate-200 font-medium"
                                    rows={2}
                                    placeholder="Experience, timings, anything worth knowing"
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={submitting()}
                                class="w-full py-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold rounded-2xl transition-all"
                            >
                                {submitting() ? 'Adding...' : 'Add Doctor'}
                            </button>
                        </form>
                    </div>
                </div>
            </Show>
        </div>
    );
};

export default VeterinaryDoctors;
