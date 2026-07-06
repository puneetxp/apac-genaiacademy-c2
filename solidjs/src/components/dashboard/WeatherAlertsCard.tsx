/**
 * Weather Alerts Card Component
 * Displays weather alerts and warnings
 */

import { Component, For, Show } from 'solid-js';
import type { WeatherAlert } from '../../services/dashboard.service';

interface WeatherAlertsCardProps {
  alerts: WeatherAlert[];
}

const WeatherAlertsCard: Component<WeatherAlertsCardProps> = (props) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-400';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-400';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-400';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-400';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-400';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'medium':
        return '⚡';
      case 'low':
        return 'ℹ️';
      default:
        return '📢';
    }
  };

  const getAlertTypeIcon = (type: string) => {
    switch (type) {
      case 'storm':
        return '⛈️';
      case 'rain':
        return '🌧️';
      case 'heat':
        return '🌡️';
      case 'cold':
        return '❄️';
      case 'wind':
        return '💨';
      case 'frost':
        return '🧊';
      default:
        return '🌤️';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const isActive = (validFrom: string, validUntil: string) => {
    const now = new Date();
    return new Date(validFrom) <= now && now <= new Date(validUntil);
  };

  return (
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">
        Weather Alerts
      </h2>
      
      <Show
        when={props.alerts && props.alerts.length > 0}
        fallback={
          <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2">☀️</div>
            <p>No active weather alerts</p>
            <p class="text-sm mt-1">Weather conditions are favorable</p>
          </div>
        }
      >
        <div class="space-y-3">
          <For each={props.alerts}>
            {(alert) => (
              <div class={`border-2 rounded-lg p-4 ${getSeverityColor(alert.severity)} ${
                isActive(alert.valid_from, alert.valid_until) ? 'shadow-lg' : 'opacity-75'
              }`}>
                <div class="flex items-start gap-3 mb-2">
                  <div class="text-2xl">
                    {getSeverityIcon(alert.severity)}
                    {getAlertTypeIcon(alert.alert_type)}
                  </div>
                  <div class="flex-1">
                    <div class="flex justify-between items-start">
                      <h3 class="font-semibold text-gray-900">{alert.title}</h3>
                      <span class="px-2 py-1 rounded text-xs font-bold uppercase">
                        {alert.severity}
                      </span>
                    </div>
                    <p class="text-sm mt-1">{alert.description}</p>
                  </div>
                </div>
                
                <div class="ml-11 space-y-2">
                  <div class="text-sm">
                    <span class="font-medium">Affected Area:</span> {alert.affected_area}
                  </div>
                  <div class="text-sm">
                    <span class="font-medium">Valid:</span> {formatDate(alert.valid_from)} - {formatDate(alert.valid_until)}
                  </div>
                  
                  <Show when={alert.recommendations && alert.recommendations.length > 0}>
                    <div class="mt-3 pt-3 border-t border-current border-opacity-20">
                      <p class="text-sm font-medium mb-1">Recommendations:</p>
                      <ul class="text-sm space-y-1">
                        <For each={alert.recommendations}>
                          {(rec) => (
                            <li class="flex items-start gap-2">
                              <span>•</span>
                              <span>{rec}</span>
                            </li>
                          )}
                        </For>
                      </ul>
                    </div>
                  </Show>
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default WeatherAlertsCard;
