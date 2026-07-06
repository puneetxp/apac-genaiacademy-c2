/**
 * Error Display Component
 * Shows user-friendly error messages with retry functionality
 */

import { Show } from 'solid-js';
import type { ApiError } from '../../lib/api-client';

export interface ErrorDisplayProps {
  error: ApiError | Error | string | null;
  onRetry?: () => void;
  title?: string;
  fullScreen?: boolean;
}

export function ErrorDisplay(props: ErrorDisplayProps) {
  const getErrorMessage = (): string => {
    if (!props.error) return 'An unknown error occurred';
    
    if (typeof props.error === 'string') {
      return props.error;
    }
    
    if ('message' in props.error) {
      return props.error.message;
    }
    
    return 'An unexpected error occurred';
  };

  const getErrorDetails = (): string | undefined => {
    if (typeof props.error === 'object' && props.error && 'detail' in props.error) {
      return (props.error as ApiError).detail;
    }
    return undefined;
  };

  const getStatusCode = (): number | undefined => {
    if (typeof props.error === 'object' && props.error && 'status' in props.error) {
      return (props.error as ApiError).status;
    }
    return undefined;
  };

  const getUserFriendlyMessage = (): string => {
    const status = getStatusCode();
    
    if (status === 401) {
      return 'Your session has expired. Please sign in again.';
    }
    
    if (status === 403) {
      return 'You do not have permission to access this resource.';
    }
    
    if (status === 404) {
      return 'The requested resource was not found.';
    }
    
    if (status === 408) {
      return 'The request took too long. Please check your connection and try again.';
    }
    
    if (status && status >= 500) {
      return 'Our servers are experiencing issues. Please try again later.';
    }
    
    return getErrorMessage();
  };

  const content = () => (
    <div class="flex flex-col items-center justify-center text-center p-6">
      {/* Error Icon */}
      <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      {/* Error Title */}
      <h3 class="text-lg font-semibold text-gray-900 mb-2">
        {props.title || 'Something went wrong'}
      </h3>

      {/* Error Message */}
      <p class="text-sm text-gray-600 mb-1 max-w-md">
        {getUserFriendlyMessage()}
      </p>

      {/* Error Details */}
      <Show when={getErrorDetails()}>
        <p class="text-xs text-gray-500 mb-4 max-w-md">
          {getErrorDetails()}
        </p>
      </Show>

      {/* Status Code */}
      <Show when={getStatusCode()}>
        <p class="text-xs text-gray-400 mb-4">
          Error Code: {getStatusCode()}
        </p>
      </Show>

      {/* Retry Button */}
      <Show when={props.onRetry}>
        <button
          onClick={props.onRetry}
          class="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Try Again
        </button>
      </Show>
    </div>
  );

  return (
    <Show
      when={props.fullScreen}
      fallback={
        <div class="bg-red-50 border border-red-200 rounded-lg">
          {content()}
        </div>
      }
    >
      <div class="fixed inset-0 bg-white flex items-center justify-center z-50">
        {content()}
      </div>
    </Show>
  );
}

/**
 * Inline Error Message (for form fields)
 */
export interface InlineErrorProps {
  message?: string;
}

export function InlineError(props: InlineErrorProps) {
  return (
    <Show when={props.message}>
      <div class="flex items-center gap-2 text-red-600 text-sm mt-1">
        <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <span>{props.message}</span>
      </div>
    </Show>
  );
}

export default ErrorDisplay;
