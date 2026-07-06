/**
 * Password Reset Component
 * Forgot password flow with confirmation code
 */

import { Component, createSignal, Show } from 'solid-js';
import { AuthService } from '../../services/auth.service';

interface PasswordResetProps {
  onSuccess: () => void;
  onCancel: () => void;
}

const PasswordReset: Component<PasswordResetProps> = (props) => {
  const [step, setStep] = createSignal<'request' | 'confirm'>('request');
  const [username, setUsername] = createSignal('');
  const [confirmationCode, setConfirmationCode] = createSignal('');
  const [newPassword, setNewPassword] = createSignal('');
  const [confirmPassword, setConfirmPassword] = createSignal('');
  const [isLoading, setIsLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [successMessage, setSuccessMessage] = createSignal<string | null>(null);

  const handleRequestReset = async (e: Event) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    try {
      await AuthService.forgotPassword({ username: username() });
      setSuccessMessage('Reset code sent to your email/phone!');
      setTimeout(() => setStep('confirm'), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmReset = async (e: Event) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    // Validate password
    if (newPassword().length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(newPassword())) {
      setError('Password must contain uppercase, lowercase, and number');
      return;
    }

    if (newPassword() !== confirmPassword()) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      await AuthService.confirmForgotPassword({
        username: username(),
        confirmation_code: confirmationCode(),
        new_password: newPassword(),
      });
      setSuccessMessage('Password reset successfully!');
      setTimeout(() => props.onSuccess(), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Reset failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div class="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-2xl font-bold text-gray-800 mb-2 text-center">
        Reset Password
      </h2>
      <p class="text-sm text-gray-600 mb-6 text-center">
        {step() === 'request'
          ? 'Enter your username to receive a reset code'
          : 'Enter the code and your new password'}
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

      <Show when={step() === 'request'}>
        <form onSubmit={handleRequestReset} class="space-y-4">
          {/* Username */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              type="text"
              value={username()}
              onInput={(e) => setUsername(e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Enter your username"
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
              disabled={isLoading()}
              class="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
            >
              {isLoading() ? 'Sending...' : 'Send Code'}
            </button>
          </div>
        </form>
      </Show>

      <Show when={step() === 'confirm'}>
        <form onSubmit={handleConfirmReset} class="space-y-4">
          {/* Confirmation Code */}
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
              class="w-full px-3 py-2 text-center text-xl tracking-widest border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="000000"
              maxLength={6}
              required
            />
          </div>

          {/* New Password */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <input
              type="password"
              value={newPassword()}
              onInput={(e) => setNewPassword(e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Enter new password"
              required
            />
            <p class="mt-1 text-xs text-gray-500">
              Min 8 characters with uppercase, lowercase, and number
            </p>
          </div>

          {/* Confirm Password */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password
            </label>
            <input
              type="password"
              value={confirmPassword()}
              onInput={(e) => setConfirmPassword(e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Re-enter new password"
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
              disabled={isLoading()}
              class="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
            >
              {isLoading() ? 'Resetting...' : 'Reset Password'}
            </button>
          </div>
        </form>
      </Show>
    </div>
  );
};

export default PasswordReset;
