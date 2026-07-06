/**
 * Upcoming Tasks Card Component
 * Displays upcoming farming tasks from implementation timeline with progress tracking
 */

import { Component, For, Show, createMemo } from 'solid-js';
import type { UpcomingTask } from '../../services/dashboard.service';
import TaskProgressBar from './TaskProgressBar';

interface UpcomingTasksCardProps {
  tasks: UpcomingTask[];
}

const UpcomingTasksCard: Component<UpcomingTasksCardProps> = (props) => {
  // Calculate overall progress
  const overallProgress = createMemo(() => {
    if (!props.tasks || props.tasks.length === 0) return 100;
    
    const completedTasks = props.tasks.filter(t => t.status === 'completed').length;
    return Math.round((completedTasks / props.tasks.length) * 100);
  });

  const completedCount = createMemo(() => 
    props.tasks ? props.tasks.filter(t => t.status === 'completed').length : 0
  );

  const pendingCount = createMemo(() => 
    props.tasks ? props.tasks.filter(t => t.status === 'pending').length : 0
  );

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return '🔴';
      case 'medium':
        return '🟡';
      case 'low':
        return '🟢';
      default:
        return '⚪';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      month: 'short',
      day: 'numeric',
    });
  };

  const isOverdue = (dateString: string) => {
    return new Date(dateString) < new Date();
  };

  return (
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-gray-800">
          Upcoming Tasks
        </h2>
        <div class="text-sm text-gray-600">
          {completedCount()} / {props.tasks?.length || 0} completed
        </div>
      </div>

      {/* Overall Progress Bar */}
      <Show when={props.tasks && props.tasks.length > 0}>
        <div class="mb-4">
          <TaskProgressBar 
            completed={completedCount()}
            total={props.tasks.length}
            label="Overall Progress"
          />
        </div>
      </Show>
      
      <Show
        when={props.tasks && props.tasks.length > 0}
        fallback={
          <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2">✅</div>
            <p>No upcoming tasks</p>
            <p class="text-sm mt-1">All caught up!</p>
          </div>
        }
      >
        <div class="space-y-3">
          <For each={props.tasks}>
            {(task) => (
              <div class={`border rounded-lg p-4 hover:shadow-md transition-shadow ${
                isOverdue(task.due_date) && task.status !== 'completed' 
                  ? 'border-red-300 bg-red-50' 
                  : task.status === 'completed'
                  ? 'border-green-300 bg-green-50 opacity-60'
                  : 'border-gray-200'
              }`}>
                <div class="flex items-start gap-3">
                  <div class="text-2xl">
                    {task.status === 'completed' ? '✅' : getPriorityIcon(task.priority)}
                  </div>
                  <div class="flex-1">
                    <div class="flex justify-between items-start mb-1">
                      <h3 class={`font-semibold ${
                        task.status === 'completed' ? 'text-gray-600 line-through' : 'text-gray-900'
                      }`}>
                        {task.title}
                      </h3>
                      <div class="flex items-center gap-2">
                        <Show when={task.status === 'completed'}>
                          <span class="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800 border border-green-300">
                            Completed
                          </span>
                        </Show>
                        <Show when={task.status !== 'completed'}>
                          <span class={`px-2 py-1 rounded text-xs font-medium border ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                        </Show>
                      </div>
                    </div>
                    <p class="text-sm text-gray-600 mb-2">{task.description}</p>
                    <div class="flex items-center gap-4 text-xs text-gray-500">
                      <span>
                        📅 Due: {formatDate(task.due_date)}
                        {isOverdue(task.due_date) && task.status !== 'completed' && (
                          <span class="text-red-600 font-medium ml-1">(Overdue)</span>
                        )}
                      </span>
                      <span>📂 {task.category}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default UpcomingTasksCard;
