import { Component } from 'solid-js';

interface SkeletonLoaderProps {
  type?: 'text' | 'card' | 'list' | 'image' | 'table';
  count?: number;
  className?: string;
}

/**
 * Skeleton loader component for better perceived performance during data loading
 * Shows placeholder content while actual data is being fetched
 */
export const SkeletonLoader: Component<SkeletonLoaderProps> = (props) => {
  const type = () => props.type || 'text';
  const count = () => props.count || 1;

  const baseClasses = 'animate-pulse bg-gray-200 rounded';

  const renderSkeleton = () => {
    switch (type()) {
      case 'text':
        return (
          <div class="space-y-2">
            {Array.from({ length: count() }).map((_, i) => (
              <div class={`${baseClasses} h-4 w-full`} />
            ))}
          </div>
        );

      case 'card':
        return (
          <div class="space-y-4">
            {Array.from({ length: count() }).map((_, i) => (
              <div class={`${baseClasses} p-4 space-y-3`}>
                <div class={`${baseClasses} h-6 w-3/4`} />
                <div class={`${baseClasses} h-4 w-full`} />
                <div class={`${baseClasses} h-4 w-5/6`} />
              </div>
            ))}
          </div>
        );

      case 'list':
        return (
          <div class="space-y-2">
            {Array.from({ length: count() }).map((_, i) => (
              <div class="flex items-center space-x-3">
                <div class={`${baseClasses} h-12 w-12 rounded-full`} />
                <div class="flex-1 space-y-2">
                  <div class={`${baseClasses} h-4 w-3/4`} />
                  <div class={`${baseClasses} h-3 w-1/2`} />
                </div>
              </div>
            ))}
          </div>
        );

      case 'image':
        return (
          <div class="space-y-4">
            {Array.from({ length: count() }).map((_, i) => (
              <div class={`${baseClasses} h-48 w-full`} />
            ))}
          </div>
        );

      case 'table':
        return (
          <div class="space-y-2">
            <div class={`${baseClasses} h-10 w-full`} />
            {Array.from({ length: count() }).map((_, i) => (
              <div class={`${baseClasses} h-12 w-full`} />
            ))}
          </div>
        );

      default:
        return <div class={`${baseClasses} h-4 w-full`} />;
    }
  };

  return (
    <div class={props.className}>
      {renderSkeleton()}
    </div>
  );
};

/**
 * Skeleton loader for marketplace listing cards
 */
export const ListingCardSkeleton: Component = () => (
  <div class="bg-white rounded-lg shadow-md p-4 animate-pulse">
    <div class="bg-gray-200 h-6 w-3/4 rounded mb-3" />
    <div class="space-y-2 mb-4">
      <div class="bg-gray-200 h-4 w-full rounded" />
      <div class="bg-gray-200 h-4 w-5/6 rounded" />
    </div>
    <div class="flex justify-between items-center">
      <div class="bg-gray-200 h-8 w-24 rounded" />
      <div class="bg-gray-200 h-8 w-32 rounded" />
    </div>
  </div>
);

/**
 * Skeleton loader for farm profile cards
 */
export const FarmCardSkeleton: Component = () => (
  <div class="bg-white rounded-lg shadow-md p-6 animate-pulse">
    <div class="flex items-center justify-between mb-4">
      <div class="bg-gray-200 h-6 w-1/2 rounded" />
      <div class="bg-gray-200 h-8 w-20 rounded" />
    </div>
    <div class="space-y-3">
      <div class="flex justify-between">
        <div class="bg-gray-200 h-4 w-1/3 rounded" />
        <div class="bg-gray-200 h-4 w-1/4 rounded" />
      </div>
      <div class="flex justify-between">
        <div class="bg-gray-200 h-4 w-1/3 rounded" />
        <div class="bg-gray-200 h-4 w-1/4 rounded" />
      </div>
      <div class="flex justify-between">
        <div class="bg-gray-200 h-4 w-1/3 rounded" />
        <div class="bg-gray-200 h-4 w-1/4 rounded" />
      </div>
    </div>
  </div>
);

/**
 * Skeleton loader for strategy timeline
 */
export const TimelineSkeleton: Component = () => (
  <div class="space-y-4 animate-pulse">
    {Array.from({ length: 3 }).map((_, i) => (
      <div class="flex items-start space-x-4">
        <div class="bg-gray-200 h-10 w-10 rounded-full flex-shrink-0" />
        <div class="flex-1 space-y-2">
          <div class="bg-gray-200 h-5 w-1/4 rounded" />
          <div class="bg-gray-200 h-4 w-full rounded" />
          <div class="bg-gray-200 h-4 w-3/4 rounded" />
        </div>
      </div>
    ))}
  </div>
);
