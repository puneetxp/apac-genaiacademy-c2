/**
 * Authentication Store
 * Global state management for authentication
 */

import { createSignal, createEffect } from 'solid-js';
import { AuthService, type User, type AuthTokens } from '../services/auth.service';
import type { ConfirmationResult } from 'firebase/auth';
import { googleSignInPopup, confirmPhoneOtp, firebaseSignOut, type FirebaseSession } from '../lib/firebase';

// Global state
const [user, setUser] = createSignal<User | null>(null);
const [isAuthenticated, setIsAuthenticated] = createSignal(false);
const [isLoading, setIsLoading] = createSignal(true);
const [error, setError] = createSignal<string | null>(null);

/**
 * Initialize auth state from stored tokens
 */
export async function initializeAuth() {
  setIsLoading(true);
  setError(null);

  try {
    const tokens = AuthService.getStoredTokens();
    
    if (!tokens) {
      setIsAuthenticated(false);
      setUser(null);
      setIsLoading(false);
      return;
    }

    // Try to load cached user data first
    const cachedUser = localStorage.getItem('user_data');
    if (cachedUser) {
      try {
        setUser(JSON.parse(cachedUser));
        setIsAuthenticated(true);
      } catch (err) {
        console.error('Failed to parse cached user data:', err);
      }
    }

    // Check if token is expired
    if (AuthService.isTokenExpired()) {
      // Try to refresh token
      try {
        const newTokens = await AuthService.refreshToken(tokens.username, tokens.refresh_token);
        AuthService.storeTokens(newTokens, tokens.username);
        
        // Get user details
        const userData = await AuthService.getUser(newTokens.access_token);
        setUser(userData);
        setIsAuthenticated(true);
        // Cache user data
        localStorage.setItem('user_data', JSON.stringify(userData));
      } catch (err) {
        // Refresh failed, clear tokens
        AuthService.clearTokens();
        localStorage.removeItem('user_data');
        setIsAuthenticated(false);
        setUser(null);
      }
    } else {
      // Token still valid, get user details
      try {
        const userData = await AuthService.getUser(tokens.access_token);
        setUser(userData);
        setIsAuthenticated(true);
        // Cache user data
        localStorage.setItem('user_data', JSON.stringify(userData));
      } catch (err) {
        // Token invalid, clear
        AuthService.clearTokens();
        localStorage.removeItem('user_data');
        setIsAuthenticated(false);
        setUser(null);
      }
    }
  } catch (err) {
    console.error('Auth initialization error:', err);
    setError(err instanceof Error ? err.message : 'Authentication failed');
    setIsAuthenticated(false);
    setUser(null);
  } finally {
    setIsLoading(false);
  }
}

/**
 * Turn a Firebase session (Google or phone) into an app session backed by the Postgres user
 */
async function completeFirebaseSignIn(getSession: () => Promise<FirebaseSession>, failure: string): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const { idToken, refreshToken } = await getSession();
    const tokens = await AuthService.firebaseSignIn(idToken, refreshToken);
    // /auth/refresh looks the user up by this name, so it must be the app username.
    AuthService.storeTokens(tokens, tokens.user?.username ?? 'firebase-user');

    const userData = await AuthService.getUser(tokens.access_token);
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('user_data', JSON.stringify(userData));
  } catch (err) {
    setError(err instanceof Error ? err.message : failure);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Sign in with Google (Firebase popup) — no password or phone needed
 */
export function signInWithGoogle(): Promise<void> {
  return completeFirebaseSignIn(googleSignInPopup, 'Google sign-in failed');
}

/**
 * Finish phone sign-in with the SMS code from sendPhoneOtp()
 */
export function signInWithPhoneOtp(confirmation: ConfirmationResult, code: string): Promise<void> {
  return completeFirebaseSignIn(() => confirmPhoneOtp(confirmation, code), 'Phone sign-in failed');
}

/**
 * Sign in user
 */
export async function signIn(username: string, password: string): Promise<{ requiresMFA: boolean; session?: string }> {
  setIsLoading(true);
  setError(null);

  try {
    const result = await AuthService.signIn({ username, password });

    // Check if MFA is required
    if ('challenge' in result && result.challenge === 'SMS_MFA') {
      setIsLoading(false);
      return { requiresMFA: true, session: result.session };
    }

    // No MFA, store tokens
    const tokens = result as AuthTokens;
    AuthService.storeTokens(tokens, username);

    // Get user details
    const userData = await AuthService.getUser(tokens.access_token);
    setUser(userData);
    setIsAuthenticated(true);
    // Cache user data
    localStorage.setItem('user_data', JSON.stringify(userData));
    setIsLoading(false);

    return { requiresMFA: false };
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Sign in failed');
    setIsLoading(false);
    throw err;
  }
}

/**
 * Verify MFA code
 */
export async function verifyMFA(username: string, session: string, mfa_code: string): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const tokens = await AuthService.verifyMFA({ username, session, mfa_code });
    AuthService.storeTokens(tokens, username);

    // Get user details
    const userData = await AuthService.getUser(tokens.access_token);
    setUser(userData);
    setIsAuthenticated(true);
    // Cache user data
    localStorage.setItem('user_data', JSON.stringify(userData));
  } catch (err) {
    setError(err instanceof Error ? err.message : 'MFA verification failed');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Sign out user
 */
export async function signOut(): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const tokens = AuthService.getStoredTokens();
    if (tokens) {
      await AuthService.signOut(tokens.access_token);
    }
    await firebaseSignOut();
  } catch (err) {
    console.error('Sign out error:', err);
    // Continue with local sign out even if API call fails
  } finally {
    AuthService.clearTokens();
    localStorage.removeItem('user_data');
    setUser(null);
    setIsAuthenticated(false);
    setIsLoading(false);
  }
}

/**
 * Refresh access token
 */
export async function refreshAccessToken(): Promise<boolean> {
  try {
    const tokens = AuthService.getStoredTokens();
    if (!tokens) return false;

    const newTokens = await AuthService.refreshToken(tokens.username, tokens.refresh_token);
    AuthService.storeTokens(newTokens, tokens.username);

    return true;
  } catch (err) {
    console.error('Token refresh error:', err);
    AuthService.clearTokens();
    setUser(null);
    setIsAuthenticated(false);
    return false;
  }
}

/**
 * Get access token (with auto-refresh if expired)
 */
export async function getAccessToken(): Promise<string | null> {
  const tokens = AuthService.getStoredTokens();
  if (!tokens) return null;

  // Check if token is expired
  if (AuthService.isTokenExpired()) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) return null;
    
    const newTokens = AuthService.getStoredTokens();
    return newTokens?.access_token || null;
  }

  return tokens.access_token;
}

// Export signals
export { user, isAuthenticated, isLoading, error };

// Auto-refresh token before expiry
createEffect(() => {
  if (!isAuthenticated()) return;

  const checkTokenExpiry = setInterval(async () => {
    if (AuthService.isTokenExpired()) {
      await refreshAccessToken();
    }
  }, 60000); // Check every minute

  return () => clearInterval(checkTokenExpiry);
});
