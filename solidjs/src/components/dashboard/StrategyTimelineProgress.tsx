/**
 * Strategy Timeline Progress Component
 * Displays annual strategy timeline with completed/pending tasks by season
 */

import { Component, For, Show, createMemo } from 'solid-js';

interface SeasonProgress {
  season: 'Kharif' | 'Rabi' | 'Zaid';
  crop: string;
  startMonth: number;
  endMonth: number;
  tasks: {
    month: string;
    actions: string[];
    completed: boolean;
  }[];
  status: 'upcoming' | 'active' | 'completed';
}

interface StrategyTimelineProgressProps {
  seasons: SeasonProgress[];
}

const StrategyTimelineProgress: Component<StrategyTimelineProgressProps> = (props) => {
  const currentMonth = new Date().getMonth();

  // Calculate overall progress
  const overallProgress = createMemo(() => {
    let totalTasks = 0;
    let completedTasks = 0;

    props.seasons.forEach(season => {
      season.tasks.forEach(task => {
        totalTasks += task.actions.length;
        if (task.completed) {
          completedTasks += task.actions.length;
        }
      });
    });

    return totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
  });

  const getSeasonColor = (season: string) => {
    switch (season) {
      case 'Kharif':
        return 'from-green-500 to-green-600';
      case 'Rabi':
        return 'from-blue-500 to-blue-600';
      case 'Zaid':
        return 'from-orange-500 to-orange-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getSeasonIcon = (season: string) => {
    switch (season) {
      case 'Kharif':
        return '🌧️'; // Monsoon season
      case 'Rabi':
        return '❄️'; // Winter season
      case 'Zaid':
        return '☀️'; // Summer season
      default:
        return '🌾';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'active':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'upcoming':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅ Completed';
      case 'active':
        return '🔄 In Progress';
      case 'upcoming':
        return '📅 Upcoming';
      default:
        return status;
    }
  };

  return (
    <div class="bg-white rounded-lg shadow p-6">
      <div class="mb-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-2">
          Annual Strategy Timeline
        </h2>
        
        {/* Overall Progress */}
        <div class="mt-4">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-gray-700">
              Overall Annual Progress
            </span>
            <span class="text-sm font-semibold text-blue-600">
              {overallProgress()}%
            </span>
          </div>
          <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-500"
              style={{ width: `${overallProgress()}%` }}
            />
          </div>
        </div>
      </div>

      {/* Season Timeline */}
      <Show
        when={props.seasons && props.seasons.length > 0}
        fallback={
          <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2">📊</div>
            <p>No annual strategy yet</p>
            <p class="text-sm mt-1">Create a strategy to see your timeline</p>
          </div>
        }
      >
        <div class="space-y-6">
          <For each={props.seasons}>
            {(season, index) => {
              const seasonProgress = createMemo(() => {
                const totalActions = season.tasks.reduce((sum, task) => sum + task.actions.length, 0);
                const completedActions = season.tasks
                  .filter(task => task.completed)
                  .reduce((sum, task) => sum + task.actions.length, 0);
                return totalActions > 0 ? Math.round((completedActions / totalActions) * 100) : 0;
              });

              return (
                <div class="border border-gray-200 rounded-lg overflow-hidden">
                  {/* Season Header */}
                  <div class={`bg-gradient-to-r ${getSeasonColor(season.season)} p-4 text-white`}>
                    <div class="flex justify-between items-center">
                      <div class="flex items-center gap-3">
                        <span class="text-3xl">{getSeasonIcon(season.season)}</span>
                        <div>
                          <h3 class="text-lg font-semibold">
                            {season.season} Season
                          </h3>
                          <p class="text-sm opacity-90">
                            {season.crop}
                          </p>
                        </div>
                      </div>
                      <span class={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusBadge(season.status)} bg-white`}>
                        {getStatusLabel(season.status)}
                      </span>
                    </div>
                    
                    {/* Season Progress Bar */}
                    <div class="mt-3">
                      <div class="flex justify-between items-center mb-1">
                        <span class="text-xs opacity-90">Season Progress</span>
                        <span class="text-xs font-semibold">{seasonProgress()}%</span>
                      </div>
                      <div class="h-2 bg-white/30 rounded-full overflow-hidden">
                        <div
                          class="h-full bg-white transition-all duration-500"
                          style={{ width: `${seasonProgress()}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Monthly Tasks */}
                  <div class="p-4">
                    <div class="space-y-3">
                      <For each={season.tasks}>
                        {(task) => (
                          <div class={`border rounded-lg p-3 ${
                            task.completed 
                              ? 'border-green-300 bg-green-50' 
                              : 'border-gray-200'
                          }`}>
                            <div class="flex items-start gap-2">
                              <div class="text-xl">
                                {task.completed ? '✅' : '📋'}
                              </div>
                              <div class="flex-1">
                                <h4 class={`font-medium text-sm ${
                                  task.completed ? 'text-green-800' : 'text-gray-900'
                                }`}>
                                  {task.month}
                                </h4>
                                <ul class="mt-2 space-y-1">
                                  <For each={task.actions}>
                                    {(action) => (
                                      <li class={`text-xs ${
                                        task.completed ? 'text-green-700 line-through' : 'text-gray-600'
                                      }`}>
                                        • {action}
                                      </li>
                                    )}
                                  </For>
                                </ul>
                              </div>
                            </div>
                          </div>
                        )}
                      </For>
                    </div>
                  </div>
                </div>
              );
            }}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default StrategyTimelineProgress;
