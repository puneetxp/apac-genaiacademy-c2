/**
 * Loading Spinner Component
 * Displays animated loading indicator
 */

import { Show } from 'solid-js';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'white' | 'gray';
  text?: string;
  fullScreen?: boolean;
}

export function LoadingSpinner(props: LoadingSpinnerProps) {
  const size = () => props.size || 'md';
  const color = () => props.color || 'primary';

  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
    xl: 'w-16 h-16 border-4',
  };

  const colorClasses = {
    primary: 'border-green-600 border-t-transparent',
    white: 'border-white border-t-transparent',
    gray: 'border-gray-400 border-t-transparent',
  };

  const spinnerClass = () => 
    `${sizeClasses[size()]} ${colorClasses[color()]} rounded-full animate-spin`;

  return (
    <Show
      when={props.fullScreen}
      fallback={
        <div class="flex flex-col items-center justify-center gap-3">
          <div class={spinnerClass()} />
          <Show when={props.text}>
            <p class="text-sm text-gray-600">{props.text}</p>
          </Show>
        </div>
      }
    >
      <div class="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
        <div class="flex flex-col items-center justify-center gap-4">
          <div class={spinnerClass()} />
          <Show when={props.text}>
            <p class="text-base text-gray-700 font-medium">{props.text}</p>
          </Show>
        </div>
      </div>
    </Show>
  );
}

export default LoadingSpinner;
