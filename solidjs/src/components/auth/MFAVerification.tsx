/**
 * MFA Verification Component
 * SMS/TOTP code verification
 */

import { Component, createSignal, Show } from 'solid-js';
import { verifyMFA } from '../../stores/auth.store';

interface MFAVerificationProps {
  username: string;
  session: string;
  onSuccess: () => void;
  onCancel: () => void;
}

const MFAVerification: Component<MFAVerificationProps> = (props) => {
  const [mfaCode, setMfaCode] = createSignal('');
  const [isLoading, setIsLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setError(null);

    if (mfaCode().length !== 6) {
      setError('MFA code must be 6 digits');
      return;
    }

    setIsLoading(true);

    try {
      await verifyMFA(props.username, props.session, mfaCode());
      props.onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'MFA verification failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div class="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-2xl font-bold text-gray-800 mb-2 text-center">
        Two-Factor Authentication
      </h2>
      <p class="text-sm text-gray-600 mb-6 text-center">
        Enter the 6-digit code sent to your phone
      </p>

      <Show when={error()}>
        <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error()}
        </div>
      </Show>

      <form onSubmit={handleSubmit} class="space-y-4">
        {/* MFA Code Input */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Verification Code
          </label>
          <input
            type="text"
            value={mfaCode()}
            onInput={(e) => {
              const value = e.currentTarget.value.replace(/\D/g, '').slice(0, 6);
              setMfaCode(value);
            }}
            class="w-full px-3 py-2 text-center text-2xl tracking-widest border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="000000"
            maxLength={6}
            required
            autocomplete="one-time-code"
          />
          <p class="mt-1 text-xs text-gray-500 text-center">
            Enter the 6-digit code from your SMS
          </p>
        </div>

        {/* Buttons */}
        <div class="flex gap-3">
          <button
            type="button"
            onClick={props.onCancel}
            class="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading() || mfaCode().length !== 6}
            class="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
          >
            {isLoading() ? 'Verifying...' : 'Verify'}
          </button>
        </div>
      </form>

      {/* Help Text */}
      <div class="mt-6 text-center">
        <p class="text-xs text-gray-500">
          Didn't receive a code? Check your phone or try signing in again.
        </p>
      </div>
    </div>
  );
};

export default MFAVerification;
