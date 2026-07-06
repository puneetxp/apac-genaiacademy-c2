/**
 * Crop Progress Indicator Component
 * Visual progress bar showing crop growth stages from planting to harvest
 */

import { Component, createMemo } from 'solid-js';

interface CropProgressIndicatorProps {
  plantingDate: string;
  expectedHarvestDate: string;
  growthStage: 'planted' | 'growing' | 'maturing' | 'ready' | 'overdue';
}

const CropProgressIndicator: Component<CropProgressIndicatorProps> = (props) => {
  // Calculate progress percentage based on dates
  const progressPercentage = createMemo(() => {
    const plantDate = new Date(props.plantingDate).getTime();
    const harvestDate = new Date(props.expectedHarvestDate).getTime();
    const now = Date.now();
    
    const totalDuration = harvestDate - plantDate;
    const elapsed = now - plantDate;
    
    const percentage = Math.min(Math.max((elapsed / totalDuration) * 100, 0), 100);
    
    // If overdue, show 100%
    if (props.growthStage === 'overdue') return 100;
    
    return Math.round(percentage);
  });

  // Get color based on growth stage
  const getProgressColor = () => {
    switch (props.growthStage) {
      case 'ready':
        return 'bg-green-500';
      case 'maturing':
        return 'bg-yellow-500';
      case 'growing':
        return 'bg-blue-500';
      case 'planted':
        return 'bg-gray-400';
      case 'overdue':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  // Get stage milestones
  const milestones = [
    { label: 'Planted', position: 0, icon: '🌱' },
    { label: 'Growing', position: 33, icon: '🌿' },
    { label: 'Maturing', position: 66, icon: '🌾' },
    { label: 'Ready', position: 100, icon: '✅' },
  ];

  return (
    <div class="my-3">
      {/* Progress Bar */}
      <div class="relative">
        <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            class={`h-full transition-all duration-500 ${getProgressColor()}`}
            style={{ width: `${progressPercentage()}%` }}
          />
        </div>
        
        {/* Milestone Markers */}
        <div class="relative mt-2">
          <div class="flex justify-between items-start">
            {milestones.map((milestone) => (
              <div 
                class="flex flex-col items-center"
                style={{ width: '25%' }}
              >
                <div 
                  class={`text-xs transition-all ${
                    progressPercentage() >= milestone.position 
                      ? 'opacity-100 scale-110' 
                      : 'opacity-40'
                  }`}
                >
                  {milestone.icon}
                </div>
                <span 
                  class={`text-xs mt-1 transition-all ${
                    progressPercentage() >= milestone.position 
                      ? 'text-gray-900 font-medium' 
                      : 'text-gray-400'
                  }`}
                >
                  {milestone.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Progress Percentage */}
      <div class="text-center mt-2">
        <span class="text-xs font-medium text-gray-600">
          {progressPercentage()}% Complete
        </span>
      </div>
    </div>
  );
};

export default CropProgressIndicator;
