/**
 * Sign In Page
 * Handles user authentication flow with MFA support
 */

import { Component, createSignal, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import SignInForm from '../../components/auth/SignInForm';
import MFAVerification from '../../components/auth/MFAVerification';
import PasswordReset from '../../components/auth/PasswordReset';

const SignInPage: Component = () => {
  const navigate = useNavigate();
  const [view, setView] = createSignal<'signin' | 'mfa' | 'reset'>('signin');
  const [username, setUsername] = createSignal('');
  const [mfaSession, setMfaSession] = createSignal('');

  const handleSignInSuccess = () => {
    navigate('/dashboard');
  };

  const handleMFARequired = (user: string, session: string) => {
    setUsername(user);
    setMfaSession(session);
    setView('mfa');
  };

  const handleMFASuccess = () => {
    navigate('/dashboard');
  };

  const handleMFACancel = () => {
    setView('signin');
  };

  const handleSignUpClick = () => {
    navigate('/auth/signup');
  };

  const handleForgotPasswordClick = () => {
    setView('reset');
  };

  const handleResetSuccess = () => {
    setView('signin');
  };

  const handleResetCancel = () => {
    setView('signin');
  };

  return (
    <div class="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
      <Show when={view() === 'signin'}>
        <SignInForm
          onSuccess={handleSignInSuccess}
          onMFARequired={handleMFARequired}
          onSignUpClick={handleSignUpClick}
          onForgotPasswordClick={handleForgotPasswordClick}
        />
      </Show>

      <Show when={view() === 'mfa'}>
        <MFAVerification
          username={username()}
          session={mfaSession()}
          onSuccess={handleMFASuccess}
          onCancel={handleMFACancel}
        />
      </Show>

      <Show when={view() === 'reset'}>
        <PasswordReset
          onSuccess={handleResetSuccess}
          onCancel={handleResetCancel}
        />
      </Show>
    </div>
  );
};

export default SignInPage;
