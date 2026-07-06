/**
 * Quality Verification Form Component
 * Allows verifiers to submit quality verification results with photos and metrics
 */

import { Component, createSignal, For, Show } from 'solid-js';
import { AdvanceBookingService, QualityVerificationRequest } from '../../services/advance-booking.service';

interface QualityVerificationFormProps {
  bookingId: number;
  qualityStandards: {
    grade: string;
    size?: string;
    moisture_content?: number;
    organic_certified: boolean;
    defects_tolerance?: number;
  };
  onSuccess: () => void;
  onCancel: () => void;
}

export const QualityVerificationForm: Component<QualityVerificationFormProps> = (props) => {
  const [verifierType, setVerifierType] = createSignal<'platform' | 'third_party' | 'buyer'>('platform');
  const [qualityGrade, setQualityGrade] = createSignal(props.qualityStandards.grade);
  const [size, setSize] = createSignal(props.qualityStandards.size || '');
  const [moistureContent, setMoistureContent] = createSignal(props.qualityStandards.moisture_content || 0);
  const [organicCertified, setOrganicCertified] = createSignal(props.qualityStandards.organic_certified);
  const [defectsTolerance, setDefectsTolerance] = createSignal(props.qualityStandards.defects_tolerance || 0);
  const [photos, setPhotos] = createSignal<string[]>([]);
  const [uploadingPhoto, setUploadingPhoto] = createSignal(false);
  const [passed, setPassed] = createSignal(true);
  const [notes, setNotes] = createSignal('');
  const [submitting, setSubmitting] = createSignal(false);
  const [error, setError] = createSignal('');

  const handlePhotoUpload = async (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    setUploadingPhoto(true);
    setError('');

    try {
      const file = input.files[0];
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Photo size must be less than 5MB');
        return;
      }

      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Only image files are allowed');
        return;
      }

      const photoUrl = await AdvanceBookingService.uploadPhoto(file);
      setPhotos([...photos(), photoUrl]);
    } catch (err: any) {
      setError(err.message || 'Failed to upload photo');
    } finally {
      setUploadingPhoto(false);
    }
  };

  const removePhoto = (index: number) => {
    setPhotos(photos().filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const qualityMetrics: Record<string, any> = {
        size: size(),
        moisture_content: moistureContent(),
        organic_certified: organicCertified(),
        defects_tolerance: defectsTolerance(),
      };

      const verification: QualityVerificationRequest = {
        verifier_type: verifierType(),
        quality_grade: qualityGrade(),
        quality_metrics: qualityMetrics,
        photos: photos(),
        passed: passed(),
        notes: notes() || undefined,
      };

      await AdvanceBookingService.submitQualityVerification(props.bookingId, verification);
      props.onSuccess();
    } catch (err: any) {
      setError(err.message || 'Failed to submit quality verification');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold mb-6">Quality Verification</h2>

      <Show when={error()}>
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error()}
        </div>
      </Show>

      <form onSubmit={handleSubmit} class="space-y-6">
        {/* Verifier Type */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Verifier Type
          </label>
          <select
            value={verifierType()}
            onChange={(e) => setVerifierType(e.currentTarget.value as any)}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
            required
          >
            <option value="platform">Platform Verifier</option>
            <option value="third_party">Third-Party Verifier</option>
            <option value="buyer">Buyer Verification</option>
          </select>
        </div>

        {/* Quality Grade */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Quality Grade
          </label>
          <select
            value={qualityGrade()}
            onChange={(e) => setQualityGrade(e.currentTarget.value)}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
            required
          >
            <option value="A">Grade A (Premium)</option>
            <option value="B">Grade B (Standard)</option>
            <option value="C">Grade C (Basic)</option>
          </select>
          <p class="text-sm text-gray-500 mt-1">
            Expected: {props.qualityStandards.grade}
          </p>
        </div>

        {/* Size */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Size Classification
          </label>
          <input
            type="text"
            value={size()}
            onInput={(e) => setSize(e.currentTarget.value)}
            placeholder="e.g., Large, Medium, Small"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
          <Show when={props.qualityStandards.size}>
            <p class="text-sm text-gray-500 mt-1">
              Expected: {props.qualityStandards.size}
            </p>
          </Show>
        </div>

        {/* Moisture Content */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Moisture Content (%)
          </label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="100"
            value={moistureContent()}
            onInput={(e) => setMoistureContent(parseFloat(e.currentTarget.value))}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
          <Show when={props.qualityStandards.moisture_content}>
            <p class="text-sm text-gray-500 mt-1">
              Maximum allowed: {props.qualityStandards.moisture_content}%
            </p>
          </Show>
        </div>

        {/* Organic Certification */}
        <div>
          <label class="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={organicCertified()}
              onChange={(e) => setOrganicCertified(e.currentTarget.checked)}
              class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <span class="text-sm font-medium text-gray-700">
              Organic Certified
            </span>
          </label>
          <Show when={props.qualityStandards.organic_certified}>
            <p class="text-sm text-red-500 mt-1">
              ⚠️ Organic certification is required for this booking
            </p>
          </Show>
        </div>

        {/* Defects Tolerance */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Defects Tolerance (%)
          </label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="100"
            value={defectsTolerance()}
            onInput={(e) => setDefectsTolerance(parseFloat(e.currentTarget.value))}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
          <Show when={props.qualityStandards.defects_tolerance}>
            <p class="text-sm text-gray-500 mt-1">
              Maximum allowed: {props.qualityStandards.defects_tolerance}%
            </p>
          </Show>
        </div>

        {/* Photo Upload */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Quality Documentation Photos
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handlePhotoUpload}
            disabled={uploadingPhoto()}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
          <p class="text-sm text-gray-500 mt-1">
            Upload photos of the produce (max 5MB per photo)
          </p>

          {/* Photo Preview */}
          <Show when={photos().length > 0}>
            <div class="mt-4 grid grid-cols-3 gap-4">
              <For each={photos()}>
                {(photo, index) => (
                  <div class="relative">
                    <img
                      src={photo}
                      alt={`Quality photo ${index() + 1}`}
                      class="w-full h-32 object-cover rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() => removePhoto(index())}
                      class="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600"
                    >
                      ×
                    </button>
                  </div>
                )}
              </For>
            </div>
          </Show>

          <Show when={uploadingPhoto()}>
            <p class="text-sm text-blue-600 mt-2">Uploading photo...</p>
          </Show>
        </div>

        {/* Pass/Fail */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Verification Result
          </label>
          <div class="flex space-x-4">
            <label class="flex items-center space-x-2">
              <input
                type="radio"
                name="passed"
                checked={passed()}
                onChange={() => setPassed(true)}
                class="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
              />
              <span class="text-sm font-medium text-green-700">Pass</span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                type="radio"
                name="passed"
                checked={!passed()}
                onChange={() => setPassed(false)}
                class="w-4 h-4 text-red-600 border-gray-300 focus:ring-red-500"
              />
              <span class="text-sm font-medium text-red-700">Fail</span>
            </label>
          </div>
        </div>

        {/* Notes */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Verification Notes
          </label>
          <textarea
            value={notes()}
            onInput={(e) => setNotes(e.currentTarget.value)}
            rows={4}
            placeholder="Add any additional notes or observations..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>

        {/* Actions */}
        <div class="flex space-x-4">
          <button
            type="submit"
            disabled={submitting()}
            class="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {submitting() ? 'Submitting...' : 'Submit Verification'}
          </button>
          <button
            type="button"
            onClick={props.onCancel}
            disabled={submitting()}
            class="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed font-medium"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};
