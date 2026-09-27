/**
 * Add Livestock card (Dashboard + Livestock home)
 * The farmer types or speaks about the animal; the AI fills the livestock
 * form over the conversation, asking for whatever is still missing. The form
 * preview stays visible and editable; nothing is saved until Approve.
 * "Fill form myself" opens the same preview empty.
 */

import { Component, For, Show, createSignal } from 'solid-js';
import { t, lang } from '../../stores/i18n.store';
import type { TKey } from '../../i18n/en';
import { AssistantService, type AssistProposal } from '../../services/assistant.service';
import { FarmService, LivestockService } from '../../shared/Service/Services';
import { showToast } from '../ui/Toast';
import ProposalCard from './ProposalCard';
import { useRecorder } from './useRecorder';

type Msg = { role: 'user' | 'assistant'; text: string };

// Browser voice for read-aloud: Indian variant of the language code (en-IN, hi-IN, gu-IN, ...)
const speechLang = (code: string) => `${code}-IN`;
const emptyProposal = (): AssistProposal => ({ entity: 'livestock', fields: {}, summary: '' });

const AddLivestockCard: Component<{ id?: string }> = (props) => {
    const [expanded, setExpanded] = createSignal(false);
    const [messages, setMessages] = createSignal<Msg[]>([]);
    const [input, setInput] = createSignal('');
    const [busy, setBusy] = createSignal(false);
    const [proposal, setProposal] = createSignal<AssistProposal | null>(null);
    const [draft, setDraft] = createSignal<Record<string, any>>({});
    const [missing, setMissing] = createSignal<string[]>([]);

    const expand = () => {
        if (!expanded()) {
            setExpanded(true);
            FarmService.all();
        }
    };

    const reset = () => {
        recorder.stop(true);
        setMessages([]);
        setProposal(null);
        setDraft({});
        setMissing([]);
        setInput('');
        setExpanded(false);
    };

    const openManual = () => {
        expand();
        if (!proposal()) setProposal(emptyProposal());
    };

    const speak = (text: string) => {
        if (!('speechSynthesis' in window) || !text) return;
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = speechLang(lang());
        window.speechSynthesis.speak(u);
    };

    const send = async (payload: { text?: string; audio?: Blob }) => {
        const text = payload.text?.trim();
        if (!text && !payload.audio) return;
        expand();
        const history = messages().slice(-10);
        setMessages([...history, { role: 'user', text: text || '🎤 …' }]);
        setInput('');
        setBusy(true);
        try {
            const result = await AssistantService.assist({
                text,
                ...(payload.audio
                    ? { audio_base64: await AssistantService.blobToBase64(payload.audio), mime_type: payload.audio.type || 'audio/webm' }
                    : {}),
                lang: lang(),
                menu: [],
                animals: [],
                history,
                task: 'add_livestock',
                draft: draft(),
            });
            if (payload.audio && result.transcript) {
                const list = [...messages()];
                list[list.length - 1] = { role: 'user', text: result.transcript };
                setMessages(list);
            }
            if (result.reply) setMessages([...messages(), { role: 'assistant', text: result.reply }]);
            if (result.proposal) {
                setProposal(result.proposal);
                setDraft({ ...draft(), ...result.proposal.fields });
            }
            setMissing(result.missing || []);
        } catch (err: any) {
            const unavailable = err?.status === 503 || /unavailable/i.test(err?.message || '');
            setMessages([...messages(), { role: 'assistant', text: unavailable ? t('ai.unavailable') : t('ai.error') }]);
            if (!proposal()) setProposal(emptyProposal()); // let them finish by hand
        } finally {
            setBusy(false);
        }
    };

    const recorder = useRecorder((audio) => send({ audio }));

    return (
        <section id={props.id} class="bg-white rounded-lg shadow-md p-4 sm:p-6 border border-green-100">
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                <div>
                    <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <span>🐄</span> {t('addLs.title')}
                    </h2>
                    <p class="text-sm text-gray-600 mt-1">{t('addLs.subtitle')}</p>
                </div>
                <div class="flex gap-2 shrink-0">
                    <Show when={expanded()}>
                        <button type="button" onClick={reset} class="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-md">
                            ↺ {t('addLs.reset')}
                        </button>
                    </Show>
                    <button
                        type="button"
                        onClick={openManual}
                        class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md shadow-sm"
                    >
                        ➕ {t('addLs.title')}
                    </button>
                </div>
            </div>

            {/* Message input — always visible */}
            <form
                class="mt-4 flex items-center gap-2"
                onSubmit={(e) => {
                    e.preventDefault();
                    send({ text: input() });
                }}
            >
                <button
                    type="button"
                    onClick={recorder.toggle}
                    disabled={busy()}
                    class={`shrink-0 w-11 h-11 rounded-full text-lg flex items-center justify-center text-white disabled:opacity-50 ${recorder.recording() ? 'bg-red-600 animate-pulse' : 'bg-green-600 hover:bg-green-700'}`}
                    aria-label={recorder.recording() ? t('ai.stop') : t('ai.record')}
                    title={recorder.recording() ? t('ai.stop') : t('ai.record')}
                >
                    {recorder.recording() ? '■' : '🎤'}
                </button>
                <input
                    type="text"
                    value={input()}
                    onInput={(e) => setInput(e.currentTarget.value)}
                    onFocus={expand}
                    placeholder={recorder.recording() ? t('ai.listening') : t('addLs.placeholder')}
                    disabled={recorder.recording()}
                    class="flex-1 min-w-0 border border-gray-300 rounded-md px-3 py-2.5 outline-none focus:border-green-500"
                />
                <button
                    type="submit"
                    disabled={busy() || !input().trim()}
                    class="shrink-0 px-4 py-2.5 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium rounded-md"
                >
                    {t('ai.send')}
                </button>
            </form>

            <Show when={expanded()}>
                <div class="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* Conversation */}
                    <div class="bg-gray-50 rounded-lg p-3 space-y-2 max-h-96 overflow-y-auto">
                        <div class="bg-white rounded-lg px-3 py-2 text-sm text-gray-800 shadow-sm">{t('addLs.greeting')}</div>
                        <For each={messages()}>
                            {(m) => (
                                <Show
                                    when={m.role === 'assistant'}
                                    fallback={
                                        <div class="flex justify-end">
                                            <div class="max-w-[85%] bg-green-600 text-white rounded-lg rounded-br-none px-3 py-2 text-sm">{m.text}</div>
                                        </div>
                                    }
                                >
                                    <div class="max-w-[90%] bg-white rounded-lg rounded-bl-none px-3 py-2 text-sm text-gray-800 shadow-sm">
                                        <p>{m.text}</p>
                                        <button onClick={() => speak(m.text)} class="mt-1 text-xs text-green-700 hover:text-green-900 font-medium">
                                            🔊 {t('ai.listen')}
                                        </button>
                                    </div>
                                </Show>
                            )}
                        </For>
                        <Show when={busy()}>
                            <p class="text-sm text-gray-500 animate-pulse">{t('ai.thinking')}</p>
                        </Show>
                        <Show when={proposal() && messages().length > 0 && !busy()}>
                            <p class={`text-xs font-medium ${missing().length ? 'text-amber-700' : 'text-green-700'}`}>
                                {missing().length
                                    ? t('addLs.missing', { fields: missing().map((f) => t(`field.${f}` as TKey)).join(', ') })
                                    : `✓ ${t('addLs.ready')}`}
                            </p>
                        </Show>
                    </div>

                    {/* Live form preview */}
                    <Show
                        when={proposal()}
                        fallback={
                            <div class="hidden lg:flex items-center justify-center border-2 border-dashed border-gray-200 rounded-lg text-sm text-gray-400 p-6 text-center">
                                {t('ai.preview')}
                            </div>
                        }
                    >
                        <ProposalCard
                            proposal={proposal()!}
                            animals={[]}
                            onChange={(values) => setDraft(values)}
                            onSaved={() => {
                                showToast('success', t('ai.saved'));
                                LivestockService.all();
                                reset();
                            }}
                            onCancel={reset}
                        />
                    </Show>
                </div>
            </Show>
        </section>
    );
};

export default AddLivestockCard;
