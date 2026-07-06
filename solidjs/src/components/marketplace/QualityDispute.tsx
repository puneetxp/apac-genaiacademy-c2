/**
 * Quality Dispute Component
 * Handles quality verification disputes between farmers and buyers
 */

import { Component, createSignal, Show } from 'solid-js';

interface QualityDisputeProps {
  bookingId: number;
  verificationId: number;
  onSubmit: (dispute: DisputeData) => Promise<void>;
  onCancel: () => void;
}

export interface DisputeData {
  dispute_reason: string;
  evidence_description: string;
  evidence_photos: string[];
  requested_resolution: string;
}

export const QualityDispute: Component<QualityDisputeProps> = (props) => {
  const [disputeReason, setDisputeReason] = createSignal('');
  const [evidenceDescription, setEvidenceDescription] = createSignal('');
  const [evidencePhotos, setEvidencePhotos] = createSignal<string[]>([]);
  const [requestedResolution, setRequestedResolution] = createSignal('');
  const [submitting, setSubmitting] = createSignal(false);
  const [error, setError] = createSignal('');

  const handlePhotoUpload = async (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

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

      // TODO: Implement actual photo upload
      // For now, create a local URL
      const photoUrl = URL.createObjectURL(file);
      setEvidencePhotos([...evidencePhotos(), photoUrl]);
    } catch (err: any) {
      setError(err.message || 'Failed to upload photo');
    }
  };

  const removePhoto = (index: number) => {
    setEvidencePhotos(evidencePhotos().filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const dispute: DisputeData = {
        dispute_reason: disputeReason(),
        evidence_description: evidenceDescription(),
        evidence_photos: evidencePhotos(),
        requested_resolution: requestedResolution(),
      };

      await props.onSubmit(dispute);
    } catch (err: any) {
      setError(err.message || 'Failed to submit dispute');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold mb-6 text-red-600">Quality Dispute Resolution</h2>

      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <p class="text-sm text-yellow-800">
          <strong>Important:</strong> Disputes are reviewed by our quality assurance team. Please
          provide detailed evidence to support your claim.
        </p>
      </div>

      <Show when={error()}>
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error()}
        </div>
      </Show>

      <form onSubmit={handleSubmit} class="space-y-6">
        {/* Dispute Reason */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason for Dispute <span class="text-red-500">*</span>
          </label>
          <select
            value={disputeReason()}
            onChange={(e) => setDisputeReason(e.currentTarget.value)}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            required
          >
            <option value="">Select a reason</option>
            <option value="incorrect_grade">Incorrect Quality Grade</option>
            <option value="incorrect_metrics">Incorrect Quality Metrics</option>
            <option value="unfair_assessment">Unfair Assessment</option>
            <option value="damaged_during_transport">Damaged During Transport</option>
            <option value="verifier_bias">Verifier Bias</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Evidence Description */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Evidence Description <span class="text-red-500">*</span>
          </label>
          <textarea
            value={evidenceDescription()}
            onInput={(e) => setEvidenceDescription(e.currentTarget.value)}
            rows={6}
            placeholder="Provide detailed description of why you believe the quality verification was incorrect. Include specific measurements, observations, or circumstances that support your claim."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            required
          />
          <p class="text-sm text-gray-500 mt-1">
            Minimum 100 characters required
          </p>
        </div>

        {/* Evidence Photos */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Evidence Photos
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handlePhotoUpload}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
          />
          <p class="text-sm text-gray-500 mt-1">
            Upload photos that support your dispute (max 5MB per photo)
          </p>

          {/* Photo Preview */}
          <Show when={evidencePhotos().length > 0}>
            <div class="mt-4 grid grid-cols-3 gap-4">
              {evidencePhotos().map((photo, index) => (
                <div class="relative">
                  <img
                    src={photo}
                    alt={`Evidence photo ${index + 1}`}
                    class="w-full h-32 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => removePhoto(index)}
                    class="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </Show>
        </div>

        {/* Requested Resolution */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Requested Resolution <span class="text-red-500">*</span>
          </label>
          <select
            value={requestedResolution()}
            onChange={(e) => setRequestedResolution(e.currentTarget.value)}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            required
          >
            <option value="">Select requested resolution</option>
            <option value="re_verification">Request Re-Verification</option>
            <option value="third_party_verification">Third-Party Verification</option>
            <option value="grade_adjustment">Grade Adjustment</option>
            <option value="penalty_waiver">Penalty Waiver</option>
            <option value="contract_cancellation">Contract Cancellation</option>
          </select>
        </div>

        {/* Dispute Process Information */}
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 class="font-medium text-blue-900 mb-2">Dispute Resolution Process</h3>
          <ol class="text-sm text-blue-800 space-y-1 list-decimal list-inside">
            <li>Your dispute will be reviewed within 24-48 hours</li>
            <li>Our quality assurance team will examine all evidence</li>
            <li>Additional verification may be requested if needed</li>
            <li>Both parties will be notified of the decision</li>
            <li>Resolution will be implemented within 3-5 business days</li>
          </ol>
        </div>

        {/* Actions */}
        <div class="flex space-x-4">
          <button
            type="submit"
            disabled={submitting() || evidenceDescription().length < 100}
            class="flex-1 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {submitting() ? 'Submitting Dispute...' : 'Submit Dispute'}
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
