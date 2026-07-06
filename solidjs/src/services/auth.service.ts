/**
 * Authentication Service
 * Handles all Firebase / Google Cloud Authentication operations
 */

import apiClient from '../lib/api-client';
import { buildUrl } from '~/config/api-registry';

export interface SignUpData {
  username: string;
  password: string;
  email: string;
  phone_number: string;
  full_name: string;
  user_type?: string; // farmer, buyer, admin
  // Optional address fields
  latitude?: number;
  longitude?: number;
  pincode?: string;
  state?: string;
  district?: string;
  village?: string;
  address_line?: string;
}

export interface SignInData {
  username: string;
  password: string;
}

export interface MFAVerifyData {
  username: string;
  session: string;
  mfa_code: string;
}

export interface ForgotPasswordData {
  username: string;
}

export interface ConfirmForgotPasswordData {
  username: string;
  confirmation_code: string;
  new_password: string;
}

export interface AuthTokens {
  access_token: string;
  id_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

export interface User {
  id: number; // Integer ID from users.id (BIGINT)
  username: string;
  email: string;
  full_name: string;
  user_type: string;
  phone_number?: string;
  is_verified?: boolean;
  is_active?: boolean;
  cognito_user_id?: string;
  firebase_id?: string;
  language_preference?: string;
  email_verified?: boolean;
  phone_verified?: boolean;
}

export class AuthService {
  /**
   * Sign up a new user
   */
  static async signUp(data: SignUpData): Promise<{ user_sub: string; user_confirmed: boolean }> {
    const url = buildUrl('auth', 'signup');
    const response = await apiClient.post<{ user_sub: string; user_confirmed: boolean }>(
      url,
      data,
      { requiresAuth: false }
    );
    return response.data;
  }

  /**
   * Confirm sign up with verification code
   */
  static async confirmSignUp(username: string, confirmation_code: string): Promise<boolean> {
    const url = buildUrl('auth', 'verifyEmail');
    await apiClient.post(
      url,
      { username, confirmation_code },
      { requiresAuth: false }
    );
    return true;
  }

  /**
   * Resend confirmation code
   */
  static async resendConfirmationCode(username: string): Promise<void> {
    const url = buildUrl('auth', 'resendVerification');
    await apiClient.post(
      url,
      { username },
      { requiresAuth: false }
    );
  }

  /**
   * Sign in user
   */
  static async signIn(data: SignInData): Promise<AuthTokens | { challenge: string; session: string }> {
    const url = buildUrl('auth', 'login'); // Maps to /api/v1/auth/signin in backend
    const response = await apiClient.post<AuthTokens | { challenge: string; session: string }>(
      url,
      data,
      { requiresAuth: false }
    );
    return response.data;
  }

  /**
   * Verify MFA code
   */
  static async verifyMFA(data: MFAVerifyData): Promise<AuthTokens> {
    // MFA verify endpoint not in registry, use direct URL
    const response = await apiClient.post<AuthTokens>(
      '/api/v1/auth/mfa-verify',
      data,
      { requiresAuth: false }
    );
    return response.data;
  }

  /**
   * Refresh access token
   */
  static async refreshToken(username: string, refresh_token: string): Promise<AuthTokens> {
    const url = buildUrl('auth', 'refresh');
    const response = await apiClient.post<AuthTokens>(
      url,
      { username, refresh_token },
      { requiresAuth: false }
    );
    return response.data;
  }

  /**
   * Sign out user
   */
  static async signOut(access_token: string): Promise<void> {
    const url = buildUrl('auth', 'logout');
    await apiClient.post(url, {});
  }

  /**
   * Initiate forgot password flow
   */
  static async forgotPassword(data: ForgotPasswordData): Promise<void> {
    const url = buildUrl('auth', 'forgotPassword');
    await apiClient.post(
      url,
      data,
      { requiresAuth: false }
    );
  }

  /**
   * Confirm forgot password with code
   */
  static async confirmForgotPassword(data: ConfirmForgotPasswordData): Promise<void> {
    const url = buildUrl('auth', 'resetPassword');
    await apiClient.post(
      url,
      data,
      { requiresAuth: false }
    );
  }

  /**
   * Get current user details
   */
  static async getUser(access_token: string): Promise<User> {
    const url = buildUrl('auth', 'me');
    const response = await apiClient.get<User>(url);
    return response.data;
  }

  /**
   * Store tokens in local storage
   */
  static storeTokens(tokens: AuthTokens, username: string): void {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('id_token', tokens.id_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    localStorage.setItem('username', username);
    localStorage.setItem('token_expires_at', String(Date.now() + tokens.expires_in * 1000));
  }

  /**
   * Get stored tokens
   */
  static getStoredTokens(): { access_token: string; refresh_token: string; username: string } | null {
    const access_token = localStorage.getItem('access_token');
    const refresh_token = localStorage.getItem('refresh_token');
    const username = localStorage.getItem('username');

    if (!access_token || !refresh_token || !username) {
      return null;
    }

    return { access_token, refresh_token, username };
  }

  /**
   * Check if token is expired
   */
  static isTokenExpired(): boolean {
    const expiresAt = localStorage.getItem('token_expires_at');
    if (!expiresAt) return true;

    return Date.now() >= parseInt(expiresAt);
  }

  /**
   * Clear stored tokens
   */
  static clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    localStorage.removeItem('token_expires_at');
  }
}
