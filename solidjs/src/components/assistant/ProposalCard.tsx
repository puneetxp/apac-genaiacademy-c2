/**
 * Proposal Card
 * Preview of a record the assistant wants to add. Every field is editable;
 * nothing is saved until the user taps Approve, and saving goes through the
 * normal islogin CRUD services (same rules as any other form).
 */

import { Component, For, Show, createEffect, createSignal, on } from 'solid-js';
import type { AssistProposal } from '../../services/assistant.service';
import { FarmService, LivestockService, Livestock_health_recordService } from '../../shared/Service/Services';
import { user } from '../../stores/auth.store';
import { t } from '../../stores/i18n.store';
import type { TKey } from '../../i18n/en';

type FieldDef = { name: string; type: 'text' | 'number' | 'date' | 'select'; options?: string[]; required?: boolean };

const FIELDS: Record<AssistProposal['entity'], FieldDef[]> = {
    livestock: [
        { name: 'species', type: 'select', options: ['cattle', 'buffalo', 'goat', 'sheep', 'poultry'], required: true },
        { name: 'breed', type: 'text', required: true },
        { name: 'name', type: 'text' },
        { name: 'quantity', type: 'number', required: true },
        { name: 'purchase_price', type: 'number', required: true },
        { name: 'purchase_date', type: 'date', required: true },
        { name: 'purpose', type: 'select', options: ['dairy', 'meat', 'breeding', 'eggs'], required: true },
        { name: 'village', type: 'text' },
        { name: 'district', type: 'text' },
        { name: 'state', type: 'text' },
    ],
    livestock_health_record: [
        { name: 'record_type', type: 'select', options: ['vaccination', 'checkup', 'treatment', 'breeding'], required: true },
        { name: 'record_date', type: 'date', required: true },
        { name: 'description', type: 'text', required: true },
        { name: 'veterinarian_name', type: 'text' },
        { name: 'cost', type: 'number' },
        { name: 'next_due_date', type: 'date' },
        { name: 'notes', type: 'text' },
    ],
};

const NUMERIC = new Set(['quantity', 'purchase_price', 'cost']);
const today = () => new Date().toISOString().slice(0, 10);

interface ProposalCardProps {
    proposal: AssistProposal;
    animals: { id: number; label: string }[];
    onSaved: () => void;
    onCancel: () => void;
    /** Called whenever the user edits a field, so the chat keeps the latest draft */
    onChange?: (values: Record<string, any>) => void;
}

const ProposalCard: Component<ProposalCardProps> = (props) => {
    const isAnimal = props.proposal.entity === 'livestock';
    const farms = () => (FarmService.allstate() || []) as any[];

    const [values, setValues] = createSignal<Record<string, any>>({
        ...(isAnimal ? { quantity: 1, purchase_date: today() } : { record_date: today() }),
        ...props.proposal.fields,
    });
    const [saving, setSaving] = createSignal(false);
    const [error, setError] = createSignal<string | null>(null);

    const set = (k: string, v: any) => {
        setValues({ ...values(), [k]: v });
        props.onChange?.(values());
    };

    // The AI filled more fields in a later turn — merge them in, keeping the user's own edits to other fields
    createEffect(
        on(
            () => props.proposal.fields,
            (fields) => setValues({ ...values(), ...fields }),
            { defer: true },
        ),
    );

    // Farms may still be loading when the card opens — default to the first one when they arrive
    createEffect(() => {
        if (isAnimal && values().farm_id == null && farms()[0]) set('farm_id', farms()[0].id);
    });

    const missing = () => {
        const v = values();
        const req = FIELDS[props.proposal.entity].filter((f) => f.required).map((f) => f.name);
        req.push(isAnimal ? 'farm_id' : 'livestock_id');
        return req.filter((k) => v[k] === undefined || v[k] === null || v[k] === '');
    };

    const approve = async () => {
        if (missing().length) {
            setError(t('ai.required'));
            return;
        }
        setSaving(true);
        setError(null);
        const body: Record<string, any> = { ...values() };
        for (const k of Object.keys(body)) if (NUMERIC.has(k) && body[k] !== '') body[k] = Number(body[k]);
        for (const k of ['farm_id', 'livestock_id']) if (body[k] !== undefined) body[k] = Number(body[k]);
        try {
            if (isAnimal) {
                if (user()?.id) body.farmer_id = user()!.id;
                await LivestockService.create(body);
            } else {
                await Livestock_health_recordService.create(body);
            }
            props.onSaved();
        } catch {
            setError(t('ai.saveFailed'));
        } finally {
            setSaving(false);
        }
    };

    const optionLabel = (field: string, opt: string) =>
        field === 'species' ? t(`species.${opt}` as TKey) : opt.charAt(0).toUpperCase() + opt.slice(1);

    return (
        <div class="bg-white border-2 border-green-200 rounded-lg p-3 space-y-3">
            <div>
                <p class="text-xs font-semibold text-green-700 uppercase tracking-wide">{t('ai.preview')}</p>
                <p class="font-bold text-gray-900">{isAnimal ? t('ai.newAnimal') : t('ai.newHealth')}</p>
                <Show when={props.proposal.summary}>
                    <p class="text-sm text-gray-600">{props.proposal.summary}</p>
                </Show>
            </div>

            {/* Owner: which farm / which animal — chosen by the user, never by the AI */}
            <Show
                when={isAnimal}
                fallback={
                    <Show when={props.animals.length > 0} fallback={<p class="text-sm text-red-600">{t('ai.noAnimal')}</p>}>
                        <label class="block text-sm">
                            <span class="text-gray-700">{t('ai.chooseAnimal')} *</span>
                            <select
                                value={values().livestock_id ?? ''}
                                onChange={(e) => set('livestock_id', e.currentTarget.value)}
                                class="mt-1 w-full border border-gray-300 rounded-md px-2 py-2 focus:border-green-500 outline-none"
                            >
                                <option value="">—</option>
                                <For each={props.animals}>{(a) => <option value={a.id}>{a.label}</option>}</For>
                            </select>
                        </label>
                    </Show>
                }
            >
                <Show when={farms().length > 0} fallback={<p class="text-sm text-red-600">{t('ai.noFarm')}</p>}>
                    <label class="block text-sm">
                        <span class="text-gray-700">{t('ai.chooseFarm')} *</span>
                        <select
                            value={values().farm_id ?? ''}
                            onChange={(e) => set('farm_id', e.currentTarget.value)}
                            class="mt-1 w-full border border-gray-300 rounded-md px-2 py-2 focus:border-green-500 outline-none"
                        >
                            <For each={farms()}>{(f) => <option value={f.id}>{f.name || `#${f.id}`}</option>}</For>
                        </select>
                    </label>
                </Show>
            </Show>

            <div class="grid grid-cols-2 gap-2">
                <For each={FIELDS[props.proposal.entity]}>
                    {(f) => (
                        <label class={`block text-sm ${f.name === 'description' || f.name === 'notes' ? 'col-span-2' : ''}`}>
                            <span class="text-gray-700">
                                {t(`field.${f.name}` as TKey)}
                                {f.required ? ' *' : ''}
                            </span>
                            <Show
                                when={f.type === 'select'}
                                fallback={
                                    <input
                                        type={f.type}
                                        value={values()[f.name] ?? ''}
                                        onInput={(e) => set(f.name, e.currentTarget.value)}
                                        class={`mt-1 w-full border rounded-md px-2 py-2 outline-none focus:border-green-500 ${f.required && !values()[f.name] ? 'border-amber-400 bg-amber-50' : 'border-gray-300'}`}
                                    />
                                }
                            >
                                <select
                                    value={values()[f.name] ?? ''}
                                    onChange={(e) => set(f.name, e.currentTarget.value)}
                                    class={`mt-1 w-full border rounded-md px-2 py-2 outline-none focus:border-green-500 ${f.required && !values()[f.name] ? 'border-amber-400 bg-amber-50' : 'border-gray-300'}`}
                                >
                                    <option value="">—</option>
                                    <For each={f.options}>{(o) => <option value={o}>{optionLabel(f.name, o)}</option>}</For>
                                </select>
                            </Show>
                        </label>
                    )}
                </For>
            </div>

            <Show when={error()}>
                <p class="text-sm text-red-600">{error()}</p>
            </Show>

            <div class="flex gap-2">
                <button
                    type="button"
                    onClick={approve}
                    disabled={saving()}
                    class="flex-1 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white font-medium rounded-md"
                >
                    {saving() ? '…' : `✓ ${t('ai.approve')}`}
                </button>
                <button
                    type="button"
                    onClick={props.onCancel}
                    class="px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-md"
                >
                    {t('ai.cancel')}
                </button>
            </div>
        </div>
    );
};

export default ProposalCard;
