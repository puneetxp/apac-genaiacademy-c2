/**
 * Email Confirmation Component
 * Verify email/phone with confirmation code
 */

import { Component, createSignal, Show } from 'solid-js';
import { AuthService } from '../../services/auth.service';

interface EmailConfirmationProps {
  username: string;
  onSuccess: () => void;
  onCancel: () => void;
}

const EmailConfirmation: Component<EmailConfirmationProps> = (props) => {
  const [confirmationCode, setConfirmationCode] = createSignal('');
  const [isLoading, setIsLoading] = createSignal(false);
  const [isResending, setIsResending] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [successMessage, setSuccessMessage] = createSignal<string | null>(null);

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (confirmationCode().length !== 6) {
      setError('Confirmation code must be 6 digits');
      return;
    }

    setIsLoading(true);

    try {
      await AuthService.confirmSignUp(props.username, confirmationCode());
      setSuccessMessage('Account confirmed successfully!');
      setTimeout(() => props.onSuccess(), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Confirmation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setError(null);
    setSuccessMessage(null);
    setIsResending(true);

    try {
      await AuthService.resendConfirmationCode(props.username);
      setSuccessMessage('Confirmation code resent successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Resend failed');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div class="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-2xl font-bold text-gray-800 mb-2 text-center">
        Confirm Your Account
      </h2>
      <p class="text-sm text-gray-600 mb-6 text-center">
        Enter the 6-digit code sent to your email/phone
      </p>

      <Show when={error()}>
        <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error()}
        </div>
      </Show>

      <Show when={successMessage()}>
        <div class="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          {successMessage()}
        </div>
      </Show>

      <form onSubmit={handleSubmit} class="space-y-4">
        {/* Confirmation Code Input */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Confirmation Code
          </label>
          <input
            type="text"
            value={confirmationCode()}
            onInput={(e) => {
              const value = e.currentTarget.value.replace(/\D/g, '').slice(0, 6);
              setConfirmationCode(value);
            }}
            class="w-full px-3 py-2 text-center text-2xl tracking-widest border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="000000"
            maxLength={6}
            required
          />
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
            disabled={isLoading() || confirmationCode().length !== 6}
            class="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
          >
            {isLoading() ? 'Confirming...' : 'Confirm'}
          </button>
        </div>
      </form>

      {/* Resend Code */}
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Didn't receive a code?{' '}
          <button
            onClick={handleResendCode}
            disabled={isResending()}
            class="text-green-600 hover:text-green-700 font-medium disabled:text-gray-400"
          >
            {isResending() ? 'Resending...' : 'Resend Code'}
          </button>
        </p>
      </div>
    </div>
  );
};

export default EmailConfirmation;
