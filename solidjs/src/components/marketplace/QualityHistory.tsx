/**
 * Quality History Component
 * Displays quality verification history for farmer reputation tracking
 */

import { Component, For, Show } from 'solid-js';
import { QualityVerification } from '../../services/advance-booking.service';

interface QualityHistoryProps {
  verifications: QualityVerification[];
  farmerId?: number;
}

export const QualityHistory: Component<QualityHistoryProps> = (props) => {
  const calculatePassRate = () => {
    if (props.verifications.length === 0) return 0;
    const passed = props.verifications.filter(v => v.passed).length;
    return Math.round((passed / props.verifications.length) * 100);
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return 'text-green-600 bg-green-50';
      case 'B':
        return 'text-blue-600 bg-blue-50';
      case 'C':
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getVerifierTypeLabel = (type: string) => {
    switch (type) {
      case 'platform':
        return 'Platform Verifier';
      case 'third_party':
        return 'Third-Party Verifier';
      case 'buyer':
        return 'Buyer Verification';
      default:
        return type;
    }
  };

  return (
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold mb-6">Quality Verification History</h2>

      {/* Summary Stats */}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-blue-50 rounded-lg p-4">
          <p class="text-sm text-gray-600 mb-1">Total Verifications</p>
          <p class="text-3xl font-bold text-blue-600">{props.verifications.length}</p>
        </div>
        <div class="bg-green-50 rounded-lg p-4">
          <p class="text-sm text-gray-600 mb-1">Pass Rate</p>
          <p class="text-3xl font-bold text-green-600">{calculatePassRate()}%</p>
        </div>
        <div class="bg-purple-50 rounded-lg p-4">
          <p class="text-sm text-gray-600 mb-1">Average Grade</p>
          <p class="text-3xl font-bold text-purple-600">
            {props.verifications.length > 0
              ? props.verifications.reduce((sum, v) => {
                  const gradeValue = v.quality_grade === 'A' ? 3 : v.quality_grade === 'B' ? 2 : 1;
                  return sum + gradeValue;
                }, 0) / props.verifications.length > 2.5
                ? 'A'
                : props.verifications.reduce((sum, v) => {
                    const gradeValue = v.quality_grade === 'A' ? 3 : v.quality_grade === 'B' ? 2 : 1;
                    return sum + gradeValue;
                  }, 0) / props.verifications.length > 1.5
                ? 'B'
                : 'C'
              : 'N/A'}
          </p>
        </div>
      </div>

      {/* Verification List */}
      <Show
        when={props.verifications.length > 0}
        fallback={
          <div class="text-center py-8 text-gray-500">
            <p>No quality verifications yet</p>
          </div>
        }
      >
        <div class="space-y-4">
          <For each={props.verifications}>
            {(verification) => (
              <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex items-start justify-between mb-3">
                  <div>
                    <div class="flex items-center space-x-2 mb-1">
                      <span
                        class={`px-3 py-1 rounded-full text-sm font-medium ${getGradeColor(
                          verification.quality_grade
                        )}`}
                      >
                        Grade {verification.quality_grade}
                      </span>
                      <span
                        class={`px-3 py-1 rounded-full text-sm font-medium ${
                          verification.passed
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {verification.passed ? '✓ Passed' : '✗ Failed'}
                      </span>
                    </div>
                    <p class="text-sm text-gray-600">
                      {getVerifierTypeLabel(verification.verifier_type)}
                    </p>
                  </div>
                  <p class="text-sm text-gray-500">
                    {new Date(verification.verification_date).toLocaleDateString()}
                  </p>
                </div>

                {/* Quality Metrics */}
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                  <Show when={verification.quality_metrics.size}>
                    <div>
                      <p class="text-xs text-gray-500">Size</p>
                      <p class="text-sm font-medium">{verification.quality_metrics.size}</p>
                    </div>
                  </Show>
                  <Show when={verification.quality_metrics.moisture_content !== undefined}>
                    <div>
                      <p class="text-xs text-gray-500">Moisture</p>
                      <p class="text-sm font-medium">
                        {verification.quality_metrics.moisture_content}%
                      </p>
                    </div>
                  </Show>
                  <Show when={verification.quality_metrics.organic_certified !== undefined}>
                    <div>
                      <p class="text-xs text-gray-500">Organic</p>
                      <p class="text-sm font-medium">
                        {verification.quality_metrics.organic_certified ? 'Yes' : 'No'}
                      </p>
                    </div>
                  </Show>
                  <Show when={verification.quality_metrics.defects_tolerance !== undefined}>
                    <div>
                      <p class="text-xs text-gray-500">Defects</p>
                      <p class="text-sm font-medium">
                        {verification.quality_metrics.defects_tolerance}%
                      </p>
                    </div>
                  </Show>
                </div>

                {/* Photos */}
                <Show when={verification.photos && verification.photos.length > 0}>
                  <div class="mb-3">
                    <p class="text-xs text-gray-500 mb-2">Documentation Photos</p>
                    <div class="flex space-x-2 overflow-x-auto">
                      <For each={verification.photos}>
                        {(photo) => (
                          <img
                            src={photo}
                            alt="Quality verification"
                            class="w-20 h-20 object-cover rounded cursor-pointer hover:opacity-80"
                            onClick={() => window.open(photo, '_blank')}
                          />
                        )}
                      </For>
                    </div>
                  </div>
                </Show>

                {/* Notes */}
                <Show when={verification.notes}>
                  <div class="bg-gray-50 rounded p-3">
                    <p class="text-xs text-gray-500 mb-1">Notes</p>
                    <p class="text-sm text-gray-700">{verification.notes}</p>
                  </div>
                </Show>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};
