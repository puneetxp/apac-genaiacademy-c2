/**
 * Sign Up Page
 * Handles user registration flow with email confirmation
 */

import { Component, createSignal, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import SignUpForm from '../../components/auth/SignUpForm';
import EmailConfirmation from '../../components/auth/EmailConfirmation';

const SignUpPage: Component = () => {
  const navigate = useNavigate();
  const [step, setStep] = createSignal<'signup' | 'confirm'>('signup');
  const [username, setUsername] = createSignal('');

  const handleSignUpSuccess = (newUsername: string) => {
    setUsername(newUsername);
    setStep('confirm');
  };

  const handleConfirmSuccess = () => {
    navigate('/auth/signin');
  };

  const handleSignInClick = () => {
    navigate('/auth/signin');
  };

  const handleCancelConfirm = () => {
    setStep('signup');
  };

  return (
    <div class="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
      <Show when={step() === 'signup'}>
        <SignUpForm
          onSuccess={handleSignUpSuccess}
          onQuickSuccess={() => navigate('/dashboard')}
          onSignInClick={handleSignInClick}
        />
      </Show>

      <Show when={step() === 'confirm'}>
        <EmailConfirmation
          username={username()}
          onSuccess={handleConfirmSuccess}
          onCancel={handleCancelConfirm}
        />
      </Show>
    </div>
  );
};

export default SignUpPage;
