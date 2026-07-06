/**
 * Quality Premium Calculator Component
 * Calculates quality-based premium or penalty adjustments
 */

import { Component, createSignal, Show } from 'solid-js';

interface QualityPremiumCalculatorProps {
  basePrice: number;
  quantity: number;
  expectedGrade: string;
  actualGrade: string;
  qualityMetrics: {
    moisture_content?: number;
    defects_tolerance?: number;
    organic_certified?: boolean;
  };
  qualityStandards: {
    moisture_content?: number;
    defects_tolerance?: number;
    organic_certified?: boolean;
  };
}

export const QualityPremiumCalculator: Component<QualityPremiumCalculatorProps> = (props) => {
  const calculateGradePremium = () => {
    const gradeValues: Record<string, number> = { A: 3, B: 2, C: 1 };
    const expectedValue = gradeValues[props.expectedGrade] || 2;
    const actualValue = gradeValues[props.actualGrade] || 2;
    
    if (actualValue > expectedValue) {
      // Premium for better grade
      return (actualValue - expectedValue) * 0.10; // 10% per grade level
    } else if (actualValue < expectedValue) {
      // Penalty for lower grade
      return (actualValue - expectedValue) * 0.15; // 15% penalty per grade level
    }
    return 0;
  };

  const calculateMoisturePremium = () => {
    if (!props.qualityMetrics.moisture_content || !props.qualityStandards.moisture_content) {
      return 0;
    }

    const difference = props.qualityMetrics.moisture_content - props.qualityStandards.moisture_content;
    
    if (difference > 0) {
      // Penalty for excess moisture (1% penalty per 1% excess moisture)
      return -0.01 * difference;
    } else if (difference < -2) {
      // Premium for significantly lower moisture (0.5% premium per 1% below standard)
      return 0.005 * Math.abs(difference);
    }
    return 0;
  };

  const calculateDefectsPremium = () => {
    if (props.qualityMetrics.defects_tolerance === undefined || 
        props.qualityStandards.defects_tolerance === undefined) {
      return 0;
    }

    const difference = props.qualityMetrics.defects_tolerance - props.qualityStandards.defects_tolerance;
    
    if (difference > 0) {
      // Penalty for excess defects (2% penalty per 1% excess defects)
      return -0.02 * difference;
    } else if (difference < -1) {
      // Premium for significantly lower defects (1% premium per 1% below standard)
      return 0.01 * Math.abs(difference);
    }
    return 0;
  };

  const calculateOrganicPremium = () => {
    if (props.qualityStandards.organic_certified && props.qualityMetrics.organic_certified) {
      return 0.15; // 15% premium for organic certification
    } else if (props.qualityStandards.organic_certified && !props.qualityMetrics.organic_certified) {
      return -0.20; // 20% penalty for missing required organic certification
    }
    return 0;
  };

  const getTotalPremiumPercentage = () => {
    const gradePremium = calculateGradePremium();
    const moisturePremium = calculateMoisturePremium();
    const defectsPremium = calculateDefectsPremium();
    const organicPremium = calculateOrganicPremium();
    
    return gradePremium + moisturePremium + defectsPremium + organicPremium;
  };

  const getAdjustedPrice = () => {
    const premiumPercentage = getTotalPremiumPercentage();
    return props.basePrice * (1 + premiumPercentage);
  };

  const getAdjustedTotal = () => {
    return getAdjustedPrice() * props.quantity;
  };

  const getPremiumAmount = () => {
    return (getAdjustedPrice() - props.basePrice) * props.quantity;
  };

  const premiumPercentage = getTotalPremiumPercentage();
  const isPremium = premiumPercentage > 0;
  const isPenalty = premiumPercentage < 0;

  return (
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold mb-6">Quality Premium Calculation</h2>

      {/* Base Information */}
      <div class="bg-gray-50 rounded-lg p-4 mb-6">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-600">Base Price</p>
            <p class="text-lg font-medium">₹{props.basePrice.toFixed(2)}/kg</p>
          </div>
          <div>
            <p class="text-sm text-gray-600">Quantity</p>
            <p class="text-lg font-medium">{props.quantity} kg</p>
          </div>
          <div>
            <p class="text-sm text-gray-600">Expected Grade</p>
            <p class="text-lg font-medium">Grade {props.expectedGrade}</p>
          </div>
          <div>
            <p class="text-sm text-gray-600">Actual Grade</p>
            <p class="text-lg font-medium">Grade {props.actualGrade}</p>
          </div>
        </div>
      </div>

      {/* Premium/Penalty Breakdown */}
      <div class="space-y-3 mb-6">
        <h3 class="font-bold text-lg mb-3">Adjustment Breakdown</h3>

        {/* Grade Premium */}
        <div class="flex items-center justify-between py-2 border-b border-gray-200">
          <span class="text-sm">Grade Adjustment</span>
          <span class={`font-medium ${calculateGradePremium() >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {calculateGradePremium() >= 0 ? '+' : ''}{(calculateGradePremium() * 100).toFixed(1)}%
          </span>
        </div>

        {/* Moisture Premium */}
        <Show when={props.qualityMetrics.moisture_content !== undefined}>
          <div class="flex items-center justify-between py-2 border-b border-gray-200">
            <span class="text-sm">Moisture Content Adjustment</span>
            <span class={`font-medium ${calculateMoisturePremium() >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {calculateMoisturePremium() >= 0 ? '+' : ''}{(calculateMoisturePremium() * 100).toFixed(1)}%
            </span>
          </div>
        </Show>

        {/* Defects Premium */}
        <Show when={props.qualityMetrics.defects_tolerance !== undefined}>
          <div class="flex items-center justify-between py-2 border-b border-gray-200">
            <span class="text-sm">Defects Tolerance Adjustment</span>
            <span class={`font-medium ${calculateDefectsPremium() >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {calculateDefectsPremium() >= 0 ? '+' : ''}{(calculateDefectsPremium() * 100).toFixed(1)}%
            </span>
          </div>
        </Show>

        {/* Organic Premium */}
        <Show when={props.qualityStandards.organic_certified !== undefined}>
          <div class="flex items-center justify-between py-2 border-b border-gray-200">
            <span class="text-sm">Organic Certification Adjustment</span>
            <span class={`font-medium ${calculateOrganicPremium() >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {calculateOrganicPremium() >= 0 ? '+' : ''}{(calculateOrganicPremium() * 100).toFixed(1)}%
            </span>
          </div>
        </Show>

        {/* Total Premium/Penalty */}
        <div class="flex items-center justify-between py-3 border-t-2 border-gray-300 mt-2">
          <span class="font-bold">Total Adjustment</span>
          <span class={`font-bold text-lg ${isPremium ? 'text-green-600' : isPenalty ? 'text-red-600' : 'text-gray-600'}`}>
            {premiumPercentage >= 0 ? '+' : ''}{(premiumPercentage * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Final Calculation */}
      <div class={`rounded-lg p-6 ${isPremium ? 'bg-green-50 border border-green-200' : isPenalty ? 'bg-red-50 border border-red-200' : 'bg-gray-50 border border-gray-200'}`}>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Adjusted Price per kg</span>
            <span class="font-medium">₹{getAdjustedPrice().toFixed(2)}</span>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">
              {isPremium ? 'Premium Amount' : isPenalty ? 'Penalty Amount' : 'Adjustment'}
            </span>
            <span class={`font-medium ${isPremium ? 'text-green-600' : isPenalty ? 'text-red-600' : 'text-gray-600'}`}>
              {getPremiumAmount() >= 0 ? '+' : ''}₹{getPremiumAmount().toFixed(2)}
            </span>
          </div>

          <div class="flex items-center justify-between pt-3 border-t-2 border-gray-300">
            <span class="font-bold text-lg">Final Total Amount</span>
            <span class="font-bold text-2xl text-green-600">
              ₹{getAdjustedTotal().toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Explanation */}
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 class="font-medium text-blue-900 mb-2">How Quality Premium Works</h4>
        <ul class="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Better quality grade: +10% premium per grade level</li>
          <li>Lower quality grade: -15% penalty per grade level</li>
          <li>Lower moisture content: +0.5% premium per 1% below standard</li>
          <li>Higher moisture content: -1% penalty per 1% above standard</li>
          <li>Lower defects: +1% premium per 1% below standard</li>
          <li>Higher defects: -2% penalty per 1% above standard</li>
          <li>Organic certification: +15% premium when required and met</li>
          <li>Missing organic certification: -20% penalty when required but not met</li>
        </ul>
      </div>
    </div>
  );
};
