/**
 * Sign Up Form Component
 * User registration with email/phone and password
 */

import { Component, createSignal, Show } from 'solid-js';
import { AuthService, type SignUpData } from '../../services/auth.service';
import AddressFields, { type AddressData } from './AddressFields';
import QuickSignIn from './QuickSignIn';

interface SignUpFormProps {
  onSuccess: (username: string) => void;
  /** Google / phone sign-up: the account already exists and the user is signed in */
  onQuickSuccess: () => void;
  onSignInClick: () => void;
}

const SignUpForm: Component<SignUpFormProps> = (props) => {
  const [formData, setFormData] = createSignal<SignUpData>({
    username: '',
    password: '',
    email: '',
    phone_number: '',
    full_name: '',
  });
  const [optional, setOptional] = createSignal<boolean>(false);
  const [addressData, setAddressData] = createSignal<AddressData>({});
  const [confirmPassword, setConfirmPassword] = createSignal('');
  const [isLoading, setIsLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [validationErrors, setValidationErrors] = createSignal<Record<string, string>>({});

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    const data = formData();

    if (!data.username || data.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    } else if (/\s/.test(data.username)) {
      errors.username = 'Username cannot contain spaces';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(data.username)) {
      errors.username = 'Username can only contain letters, numbers, hyphens, and underscores';
    }

    if (!data.full_name || data.full_name.length < 2) {
      errors.full_name = 'Full name is required';
    }

    if (!data.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.email = 'Valid email is required';
    }

    if (data.phone_number && !/^\+91\d{10}$/.test(data.phone_number)) {
      errors.phone_number = 'Phone must be in format +919876543210';
    }

    if (!data.password || data.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }

    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(data.password)) {
      errors.password = 'Password must contain uppercase, lowercase, and number';
    }

    if (data.password !== confirmPassword()) {
      errors.confirmPassword = 'Passwords do not match';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Merge form data with address data
      const signUpData: SignUpData = {
        ...formData(),
        phone_number: formData().phone_number?.trim() || undefined,
        ...addressData()
      };
      await AuthService.signUp(signUpData);
      props.onSuccess(formData().username);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign up failed');
    } finally {
      setIsLoading(false);
    }
  };

  const updateField = (field: keyof SignUpData, value: string) => {
    setFormData({ ...formData(), [field]: value });
    // Clear validation error for this field
    setValidationErrors({ ...validationErrors(), [field]: '' });
  };

  const updateAddressField = (field: keyof AddressData, value: string | number | undefined) => {
    setAddressData({ ...addressData(), [field]: value });
    // Clear validation error for this field
    setValidationErrors({ ...validationErrors(), [field]: '' });
  };

  return (
    <div class="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">
        Create Account
      </h2>

      <Show when={error()}>
        <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error()}
        </div>
      </Show>

      <QuickSignIn onSuccess={props.onQuickSuccess} onError={setError} disabled={isLoading()} />

      <div class="my-5 flex items-center gap-3 text-xs text-gray-400">
        <div class="h-px flex-1 bg-gray-200" />
        or create an account with email
        <div class="h-px flex-1 bg-gray-200" />
      </div>

      <form onSubmit={handleSubmit} class="space-y-4">
        {/* Username */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Username *
          </label>
          <input
            type="text"
            value={formData().username}
            onInput={(e) => updateField('username', e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Choose a username"
            required
          />
          <Show when={validationErrors().username}>
            <p class="mt-1 text-sm text-red-600">{validationErrors().username}</p>
          </Show>
          <p class="mt-1 text-xs text-gray-500">
            For display only. Use your email to sign in.
          </p>
        </div>

        {/* Full Name */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Full Name *
          </label>
          <input
            type="text"
            value={formData().full_name}
            onInput={(e) => updateField('full_name', e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Enter your full name"
            required
          />
          <Show when={validationErrors().full_name}>
            <p class="mt-1 text-sm text-red-600">{validationErrors().full_name}</p>
          </Show>
        </div>

        {/* Email */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Email *
          </label>
          <input
            type="email"
            value={formData().email}
            onInput={(e) => updateField('email', e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="your@email.com"
            required
          />
          <Show when={validationErrors().email}>
            <p class="mt-1 text-sm text-red-600">{validationErrors().email}</p>
          </Show>
        </div>

        {/* Phone Number */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Phone Number (optional)
          </label>
          <input
            type="tel"
            value={formData().phone_number}
            onInput={(e) => updateField('phone_number', e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="+919876543210"
          />
          <Show when={validationErrors().phone_number}>
            <p class="mt-1 text-sm text-red-600">{validationErrors().phone_number}</p>
          </Show>
          <p class="mt-1 text-xs text-gray-500">Format: +91 followed by 10 digits</p>
        </div>

        {/* Password */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Password *
          </label>
          <input
            type="password"
            value={formData().password}
            onInput={(e) => updateField('password', e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Create a strong password"
            required
          />
          <Show when={validationErrors().password}>
            <p class="mt-1 text-sm text-red-600">{validationErrors().password}</p>
          </Show>
          <p class="mt-1 text-xs text-gray-500">
            Min 8 characters with uppercase, lowercase, and number
          </p>
        </div>

        {/* Confirm Password */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Confirm Password *
          </label>
          <input
            type="password"
            value={confirmPassword()}
            onInput={(e) => {
              setConfirmPassword(e.currentTarget.value);
              setValidationErrors({ ...validationErrors(), confirmPassword: '' });
            }}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Re-enter your password"
            required
          />
          <Show when={validationErrors().confirmPassword}>
            <p class="mt-1 text-sm text-red-600">{validationErrors().confirmPassword}</p>
          </Show>
        </div>
        {/* Toggle for Optional Address Fields */}
        <div class="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={optional()}
            onChange={(e) => setOptional(e.currentTarget.checked)}
            class="relative inline-block h-4 w-10 after:absolute after:top-3 appearance-none rounded-full before:absolute before:left-0 before:top-0 before:inline-block before:h-6 before:w-full before:rounded-full before:bg-slate-200 before:transition-colors before:duration-200 before:ease-in after:absolute after:left-0.5 after:top-2/4 after:h-4 after:w-5 after:-translate-y-2/4 after:rounded-full after:bg-white after:transition-transform after:duration-200 after:ease-in checked:before:bg-slate-800 checked:after:translate-x-[calc(100%-4px)] dark:after:bg-white"
          />
          <label class="text-sm font-medium text-gray-700">
            Add address information (optional)
          </label>
        </div>

        {/* Address Fields (Optional) */}
        <Show when={optional()}>
        <AddressFields
          addressData={addressData()}
          onUpdate={updateAddressField}
          validationErrors={validationErrors()}
          showGPSOption={true}
        />
        </Show>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading()}
          class="w-full py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
        >
          {isLoading() ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>

      {/* Sign In Link */}
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Already have an account?{' '}
          <button
            onClick={props.onSignInClick}
            class="text-green-600 hover:text-green-700 font-medium"
          >
            Sign In
          </button>
        </p>
      </div>
    </div>
  );
};

export default SignUpForm;
