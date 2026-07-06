/**
 * Harvest Countdown Component
 * Displays countdown timer for active crops approaching harvest
 */

import { Component, Show } from 'solid-js';

interface HarvestCountdownProps {
  daysUntilHarvest: number;
  growthStage: string;
}

const HarvestCountdown: Component<HarvestCountdownProps> = (props) => {
  const getCountdownColor = () => {
    if (props.daysUntilHarvest < 0) return 'text-red-600 bg-red-50 border-red-200';
    if (props.daysUntilHarvest <= 7) return 'text-green-600 bg-green-50 border-green-200';
    if (props.daysUntilHarvest <= 30) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-blue-600 bg-blue-50 border-blue-200';
  };

  const getCountdownIcon = () => {
    if (props.daysUntilHarvest < 0) return '⚠️';
    if (props.daysUntilHarvest <= 7) return '🎯';
    if (props.daysUntilHarvest <= 30) return '⏰';
    return '📅';
  };

  const getCountdownMessage = () => {
    if (props.daysUntilHarvest < 0) {
      return `Overdue by ${Math.abs(props.daysUntilHarvest)} days`;
    }
    if (props.daysUntilHarvest === 0) {
      return 'Ready for harvest today!';
    }
    if (props.daysUntilHarvest === 1) {
      return 'Ready for harvest tomorrow!';
    }
    if (props.daysUntilHarvest <= 7) {
      return `Ready in ${props.daysUntilHarvest} days`;
    }
    if (props.daysUntilHarvest <= 30) {
      const weeks = Math.ceil(props.daysUntilHarvest / 7);
      return `${weeks} week${weeks > 1 ? 's' : ''} until harvest`;
    }
    const months = Math.floor(props.daysUntilHarvest / 30);
    const remainingDays = props.daysUntilHarvest % 30;
    if (months > 0 && remainingDays > 0) {
      return `${months} month${months > 1 ? 's' : ''}, ${remainingDays} days`;
    }
    if (months > 0) {
      return `${months} month${months > 1 ? 's' : ''} until harvest`;
    }
    return `${props.daysUntilHarvest} days until harvest`;
  };

  return (
    <div class={`mt-3 p-3 rounded-lg border ${getCountdownColor()}`}>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-xl">{getCountdownIcon()}</span>
          <div>
            <p class="text-sm font-semibold">
              {getCountdownMessage()}
            </p>
            <Show when={props.daysUntilHarvest > 0 && props.daysUntilHarvest <= 7}>
              <p class="text-xs mt-1 opacity-75">
                Prepare for harvest soon!
              </p>
            </Show>
            <Show when={props.daysUntilHarvest < 0}>
              <p class="text-xs mt-1 opacity-75">
                Consider harvesting immediately
              </p>
            </Show>
          </div>
        </div>
        <Show when={props.daysUntilHarvest >= 0}>
          <div class="text-right">
            <div class="text-2xl font-bold">
              {props.daysUntilHarvest}
            </div>
            <div class="text-xs opacity-75">
              days
            </div>
          </div>
        </Show>
      </div>
    </div>
  );
};

export default HarvestCountdown;
