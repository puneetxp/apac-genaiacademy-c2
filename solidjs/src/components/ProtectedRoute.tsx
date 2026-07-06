/**
 * Protected Route Component
 * Redirects to sign-in if user is not authenticated
 */

import { Component, Show, createEffect } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { isAuthenticated, isLoading } from '../stores/auth.store';

interface ProtectedRouteProps {
  children: any;
}

const ProtectedRoute: Component<ProtectedRouteProps> = (props) => {
  const navigate = useNavigate();

  // Wait for auth to finish loading before checking authentication
  createEffect(() => {
    if (!isLoading() && !isAuthenticated()) {
      navigate('/auth/signin', { replace: true });
    }
  });

  return (
    <Show when={!isLoading()} fallback={
      <div class="min-h-screen flex items-center justify-center">
        <p class="text-gray-600">Loading...</p>
      </div>
    }>
      <Show when={isAuthenticated()} fallback={
        <div class="min-h-screen flex items-center justify-center">
          <p class="text-gray-600">Redirecting to sign in...</p>
        </div>
      }>
        {props.children}
      </Show>
    </Show>
  );
};

export default ProtectedRoute;
