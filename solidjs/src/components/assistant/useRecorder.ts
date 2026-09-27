/**
 * Microphone recording for the assistant: tap to start, tap to stop,
 * the finished clip is handed to onDone. Shared by the floating assistant
 * and the inline Add Livestock card.
 */

import { createSignal, onCleanup } from 'solid-js';
import { showToast } from '../ui/Toast';
import { t } from '../../stores/i18n.store';

export function useRecorder(onDone: (audio: Blob) => void) {
    const [recording, setRecording] = createSignal(false);
    let recorder: MediaRecorder | null = null;
    let chunks: Blob[] = [];

    const start = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mime = ['audio/webm', 'audio/ogg', 'audio/mp4'].find((m) => MediaRecorder.isTypeSupported?.(m)) || '';
            recorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
            chunks = [];
            recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data);
            recorder.onstop = () => {
                stream.getTracks().forEach((tr) => tr.stop());
                const blob = new Blob(chunks, { type: (recorder?.mimeType || 'audio/webm').split(';')[0] });
                recorder = null;
                if (blob.size > 500) onDone(blob);
            };
            recorder.start();
            setRecording(true);
        } catch {
            showToast('warning', t('ai.micDenied'));
        }
    };

    /** Stop; with discard=true the clip is thrown away (e.g. panel closed) */
    const stop = (discard = false) => {
        if (!recorder) return;
        if (discard) chunks = [];
        recorder.stop();
        setRecording(false);
    };

    const toggle = () => (recording() ? stop() : start());

    onCleanup(() => stop(true));

    return { recording, start, stop, toggle };
}
