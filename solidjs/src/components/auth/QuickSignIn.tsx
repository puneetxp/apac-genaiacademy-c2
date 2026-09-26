/**
 * Quick Sign-In
 * Google and phone-OTP buttons shared by the sign-in and sign-up pages. Both create the
 * account on first use, so there is no separate registration step for these methods.
 */

import { Component, createSignal, Show } from 'solid-js';
import type { ConfirmationResult } from 'firebase/auth';
import { signInWithGoogle, signInWithPhoneOtp } from '../../stores/auth.store';
import { sendPhoneOtp } from '../../lib/firebase';
import { showToast } from '../ui/Toast';

interface QuickSignInProps {
  onSuccess: () => void;
  onError: (message: string | null) => void;
  disabled?: boolean;
}

const QuickSignIn: Component<QuickSignInProps> = (props) => {
  const [busy, setBusy] = createSignal(false);
  const [showPhone, setShowPhone] = createSignal(false);
  const [phone, setPhone] = createSignal('+91');
  const [otp, setOtp] = createSignal('');
  const [confirmation, setConfirmation] = createSignal<ConfirmationResult | null>(null);

  const disabled = () => busy() || !!props.disabled;

  const run = async (action: () => Promise<void>, fallback: string) => {
    props.onError(null);
    setBusy(true);
    try {
      await action();
    } catch (err) {
      const message = err instanceof Error ? err.message : fallback;
      // Closing the Google popup isn't an error worth shouting about.
      if (!message.includes('popup-closed-by-user')) {
        props.onError(message);
        showToast('error', message);
      }
    } finally {
      setBusy(false);
    }
  };

  const handleGoogle = () =>
    run(async () => {
      await signInWithGoogle();
      showToast('success', 'Signed in successfully');
      props.onSuccess();
    }, 'Google sign-in failed');

  const handleSendOtp = (e: Event) => {
    e.preventDefault();
    return run(async () => {
      setConfirmation(await sendPhoneOtp(phone().replace(/[\s-]/g, ''), 'phone-recaptcha'));
      showToast('success', 'Code sent by SMS');
    }, 'Could not send the code');
  };

  const handleVerifyOtp = (e: Event) => {
    e.preventDefault();
    const pending = confirmation();
    if (!pending) return;
    return run(async () => {
      await signInWithPhoneOtp(pending, otp());
      showToast('success', 'Signed in successfully');
      props.onSuccess();
    }, 'Invalid code');
  };

  return (
    <div>
      <button
        type="button"
        onClick={handleGoogle}
        disabled={disabled()}
        class="w-full py-2.5 px-4 bg-white border border-gray-300 hover:bg-gray-50 disabled:opacity-60 disabled:cursor-not-allowed text-gray-800 font-medium rounded-md transition-colors flex items-center justify-center gap-3"
      >
        <svg class="w-5 h-5" viewBox="0 0 48 48" aria-hidden="true">
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
        </svg>
        Continue with Google
      </button>

      <Show
        when={showPhone()}
        fallback={
          <button
            type="button"
            onClick={() => setShowPhone(true)}
            disabled={disabled()}
            class="mt-3 w-full py-2.5 px-4 bg-white border border-gray-300 hover:bg-gray-50 disabled:opacity-60 text-gray-800 font-medium rounded-md transition-colors"
          >
            Continue with phone (OTP)
          </button>
        }
      >
        <Show
          when={confirmation()}
          fallback={
            <form onSubmit={handleSendOtp} class="mt-3 flex gap-2">
              <input
                type="tel"
                value={phone()}
                onInput={(e) => setPhone(e.currentTarget.value)}
                class="flex-1 min-w-0 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="+919876543210"
                required
                autocomplete="tel"
              />
              <button
                type="submit"
                disabled={disabled()}
                class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md"
              >
                Send code
              </button>
            </form>
          }
        >
          <form onSubmit={handleVerifyOtp} class="mt-3 flex gap-2">
            <input
              type="text"
              inputmode="numeric"
              pattern="\d{6}"
              maxlength={6}
              value={otp()}
              onInput={(e) => setOtp(e.currentTarget.value)}
              class="flex-1 min-w-0 px-3 py-2 border border-gray-300 rounded-md tracking-widest focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="6-digit code"
              required
              autocomplete="one-time-code"
            />
            <button
              type="submit"
              disabled={disabled()}
              class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md"
            >
              Verify
            </button>
          </form>
          <button
            type="button"
            onClick={() => { setConfirmation(null); setOtp(''); }}
            class="mt-1 text-xs text-green-600 hover:text-green-700"
          >
            Change number
          </button>
        </Show>
      </Show>
      <div id="phone-recaptcha" />
    </div>
  );
};

export default QuickSignIn;
