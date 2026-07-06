/**
 * Auth guard utilities
 * Checks if the user is currently logged in based on stored tokens
 */

export function isLogin(): boolean {
  try {
    const access_token = localStorage.getItem('access_token');
    const refresh_token = localStorage.getItem('refresh_token');
    return !!(access_token && refresh_token);
  } catch {
    return false;
  }
}
