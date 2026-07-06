/**
 * Skeleton Screen Components
 * Displays placeholder content while data is loading
 */

import { For } from 'solid-js';

/**
 * Base Skeleton Component
 */
export interface SkeletonProps {
  width?: string;
  height?: string;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
  className?: string;
}

export function Skeleton(props: SkeletonProps) {
  const roundedClasses = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  };

  const rounded = () => props.rounded || 'md';

  return (
    <div
      class={`bg-gray-200 animate-pulse ${roundedClasses[rounded()]} ${props.className || ''}`}
      style={{
        width: props.width || '100%',
        height: props.height || '1rem',
      }}
    />
  );
}

/**
 * Card Skeleton
 */
export function SkeletonCard() {
  return (
    <div class="bg-white rounded-lg shadow-md p-6 space-y-4">
      <Skeleton height="1.5rem" width="60%" />
      <Skeleton height="1rem" width="100%" />
      <Skeleton height="1rem" width="90%" />
      <Skeleton height="1rem" width="80%" />
      <div class="flex gap-2 mt-4">
        <Skeleton height="2rem" width="5rem" rounded="md" />
        <Skeleton height="2rem" width="5rem" rounded="md" />
      </div>
    </div>
  );
}

/**
 * List Skeleton
 */
export interface SkeletonListProps {
  count?: number;
}

export function SkeletonList(props: SkeletonListProps) {
  const count = () => props.count || 3;

  return (
    <div class="space-y-4">
      <For each={Array(count()).fill(0)}>
        {() => (
          <div class="bg-white rounded-lg shadow-sm p-4 space-y-3">
            <div class="flex items-center gap-3">
              <Skeleton width="3rem" height="3rem" rounded="full" />
              <div class="flex-1 space-y-2">
                <Skeleton height="1rem" width="40%" />
                <Skeleton height="0.875rem" width="60%" />
              </div>
            </div>
            <Skeleton height="0.75rem" width="100%" />
            <Skeleton height="0.75rem" width="80%" />
          </div>
        )}
      </For>
    </div>
  );
}

/**
 * Table Skeleton
 */
export interface SkeletonTableProps {
  rows?: number;
  columns?: number;
}

export function SkeletonTable(props: SkeletonTableProps) {
  const rows = () => props.rows || 5;
  const columns = () => props.columns || 4;

  return (
    <div class="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div class="bg-gray-50 p-4 border-b border-gray-200">
        <div class="flex gap-4">
          <For each={Array(columns()).fill(0)}>
            {() => <Skeleton height="1rem" width="100%" />}
          </For>
        </div>
      </div>
      {/* Rows */}
      <div class="divide-y divide-gray-200">
        <For each={Array(rows()).fill(0)}>
          {() => (
            <div class="p-4">
              <div class="flex gap-4">
                <For each={Array(columns()).fill(0)}>
                  {() => <Skeleton height="0.875rem" width="100%" />}
                </For>
              </div>
            </div>
          )}
        </For>
      </div>
    </div>
  );
}

/**
 * Form Skeleton
 */
export function SkeletonForm() {
  return (
    <div class="bg-white rounded-lg shadow-md p-6 space-y-6">
      <For each={Array(4).fill(0)}>
        {() => (
          <div class="space-y-2">
            <Skeleton height="1rem" width="30%" />
            <Skeleton height="2.5rem" width="100%" rounded="md" />
          </div>
        )}
      </For>
      <div class="flex gap-3 mt-6">
        <Skeleton height="2.5rem" width="6rem" rounded="md" />
        <Skeleton height="2.5rem" width="6rem" rounded="md" />
      </div>
    </div>
  );
}

/**
 * Dashboard Skeleton
 */
export function SkeletonDashboard() {
  return (
    <div class="space-y-6">
      {/* Stats Cards */}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <For each={Array(3).fill(0)}>
          {() => (
            <div class="bg-white rounded-lg shadow-md p-6 space-y-3">
              <Skeleton height="1rem" width="50%" />
              <Skeleton height="2rem" width="40%" />
              <Skeleton height="0.75rem" width="60%" />
            </div>
          )}
        </For>
      </div>
      {/* Main Content */}
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  );
}

export default Skeleton;
