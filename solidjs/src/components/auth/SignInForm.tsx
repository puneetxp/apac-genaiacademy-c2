/**
 * Sign In Form Component
 * User authentication with username/password
 */

import { Component, createSignal, Show } from 'solid-js';
import { signIn } from '../../stores/auth.store';
import QuickSignIn from './QuickSignIn';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { InlineError } from '../ui/ErrorDisplay';
import { showToast } from '../ui/Toast';

interface SignInFormProps {
  onSuccess: () => void;
  onMFARequired: (username: string, session: string) => void;
  onSignUpClick: () => void;
  onForgotPasswordClick: () => void;
}

const SignInForm: Component<SignInFormProps> = (props) => {
  const [username, setUsername] = createSignal('');
  const [password, setPassword] = createSignal('');
  const [isLoading, setIsLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await signIn(username(), password());

      if (result.requiresMFA && result.session) {
        showToast('info', 'MFA verification required');
        props.onMFARequired(username(), result.session);
      } else {
        showToast('success', 'Signed in successfully');
        props.onSuccess();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign in failed';
      setError(errorMessage);
      showToast('error', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div class="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">
        Sign In
      </h2>

      <Show when={error()}>
        <div class="mb-4 p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg flex items-start gap-2">
          <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <span class="text-sm">{error()}</span>
        </div>
      </Show>

      <QuickSignIn onSuccess={props.onSuccess} onError={setError} disabled={isLoading()} />

      <div class="my-5 flex items-center gap-3 text-xs text-gray-400">
        <div class="h-px flex-1 bg-gray-200" />
        or sign in with username / email
        <div class="h-px flex-1 bg-gray-200" />
      </div>

      <form onSubmit={handleSubmit} class="space-y-4">
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
            autocomplete="username"
          />
        </div>

        {/* Password */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            type="password"
            value={password()}
            onInput={(e) => setPassword(e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Enter your password"
            required
            autocomplete="current-password"
          />
        </div>

        {/* Forgot Password Link */}
        <div class="text-right">
          <button
            type="button"
            onClick={props.onForgotPasswordClick}
            class="text-sm text-green-600 hover:text-green-700"
          >
            Forgot password?
          </button>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading()}
          class="w-full py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors flex items-center justify-center gap-2"
        >
          <Show when={isLoading()}>
            <LoadingSpinner size="sm" color="white" />
          </Show>
          {isLoading() ? 'Signing In...' : 'Sign In'}
        </button>
      </form>

      {/* Sign Up Link */}
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Don't have an account?{' '}
          <button
            onClick={props.onSignUpClick}
            class="text-green-600 hover:text-green-700 font-medium"
          >
            Sign Up
          </button>
        </p>
      </div>
    </div>
  );
};

export default SignInForm;
