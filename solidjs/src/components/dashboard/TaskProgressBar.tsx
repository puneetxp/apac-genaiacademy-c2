/**
 * Task Progress Bar Component
 * Displays progress bar for completed vs pending tasks
 */

import { Component, createMemo } from 'solid-js';

interface TaskProgressBarProps {
  completed: number;
  total: number;
  label?: string;
  showPercentage?: boolean;
}

const TaskProgressBar: Component<TaskProgressBarProps> = (props) => {
  const percentage = createMemo(() => {
    if (props.total === 0) return 0;
    return Math.round((props.completed / props.total) * 100);
  });

  const getProgressColor = () => {
    const pct = percentage();
    if (pct === 100) return 'bg-green-500';
    if (pct >= 75) return 'bg-blue-500';
    if (pct >= 50) return 'bg-yellow-500';
    if (pct >= 25) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getProgressTextColor = () => {
    const pct = percentage();
    if (pct === 100) return 'text-green-600';
    if (pct >= 75) return 'text-blue-600';
    if (pct >= 50) return 'text-yellow-600';
    if (pct >= 25) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div class="w-full">
      {/* Label and Stats */}
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm font-medium text-gray-700">
          {props.label || 'Progress'}
        </span>
        <span class={`text-sm font-semibold ${getProgressTextColor()}`}>
          {props.showPercentage !== false && `${percentage()}% • `}
          {props.completed} / {props.total}
        </span>
      </div>

      {/* Progress Bar */}
      <div class="relative">
        <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            class={`h-full transition-all duration-500 ${getProgressColor()}`}
            style={{ width: `${percentage()}%` }}
          />
        </div>
        
        {/* Progress Segments Indicator */}
        <div class="absolute top-0 left-0 right-0 h-3 flex">
          {Array.from({ length: 4 }).map((_, i) => (
            <div 
              class="flex-1 border-r border-white/30"
              style={{ width: '25%' }}
            />
          ))}
        </div>
      </div>

      {/* Status Message */}
      <div class="mt-1 text-xs text-gray-500">
        {percentage() === 100 && '🎉 All tasks completed!'}
        {percentage() >= 75 && percentage() < 100 && '💪 Almost there!'}
        {percentage() >= 50 && percentage() < 75 && '📈 Good progress'}
        {percentage() >= 25 && percentage() < 50 && '🚀 Keep going'}
        {percentage() < 25 && percentage() > 0 && '🌱 Just getting started'}
        {percentage() === 0 && '📋 Ready to begin'}
      </div>
    </div>
  );
};

export default TaskProgressBar;
