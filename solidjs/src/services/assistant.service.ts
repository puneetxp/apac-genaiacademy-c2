/**
 * Assistant Service
 * Sends a voice recording or typed text to /voice/assist and gets back what
 * to do: open a menu option, a short reply, a question ("which animal?"), or
 * a record proposal the user approves before anything is saved.
 */

import apiClient from '../lib/api-client';

export interface AssistMatch {
    id: string;
    score: number;
}

export interface AssistProposal {
    entity: 'livestock' | 'livestock_health_record';
    fields: Record<string, string | number>;
    summary: string;
}

export interface AssistResult {
    transcript: string;
    language: string;
    intent: 'navigate' | 'create' | 'answer' | 'clarify';
    confidence: number;
    auto_open: boolean;
    reply: string;
    matches: AssistMatch[];
    proposal: AssistProposal | null;
    animal_options: number[];
    vet_help: boolean;
    /** Required fields still empty in the proposal */
    missing?: string[];
    fallback?: boolean;
}

export interface AssistRequest {
    audio_base64?: string;
    mime_type?: string;
    text?: string;
    lang: string;
    menu: { id: string; label: string }[];
    animals: { id: number; label: string }[];
    history: { role: 'user' | 'assistant'; text: string }[];
    focus_animal_id?: number | null;
    /** Guided form filling: the AI updates `draft` from the conversation */
    task?: 'add_livestock';
    draft?: Record<string, unknown>;
}

export class AssistantService {
    static async assist(body: AssistRequest): Promise<AssistResult> {
        const response = await apiClient.post<{ success: boolean; data: AssistResult }>('/voice/assist', body);
        return response.data.data;
    }

    /** Recording blob -> base64 (no data: prefix) */
    static blobToBase64(blob: Blob): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(String(reader.result).split(',')[1] || '');
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }
}
