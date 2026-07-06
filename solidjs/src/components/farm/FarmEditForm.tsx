/**
 * Farm Edit Form Component
 * Form for updating existing farm details
 */

import { Component, createSignal, onMount, Show } from "solid-js";
import {
  DISTRICTS_BY_STATE,
  type Farm,
  type FarmUpdate,
  INDIAN_STATES,
  IRRIGATION_TYPES,
  SOIL_TYPES,
} from "../../services/farm.service";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { InlineError } from "../ui/ErrorDisplay";
import { showToast } from "../ui/Toast";
import FarmAddressFields, { type FarmAddressData } from "./FarmAddressFields";

interface FarmEditFormProps {
  farm: Farm;
  onSuccess: () => void;
  onCancel: () => void;
}

const FarmEditForm: Component<FarmEditFormProps> = (props) => {
  const [formData, setFormData] = createSignal<FarmUpdate>({
    name: "",
    state: "",
    district: "",
    village: "",
    pincode: "",
    address_line: "",
    total_area_acres: 0,
    latitude: undefined,
    longitude: undefined,
    primary_soil_type: "",
    irrigation_type: "",
  });

  const [isLoading, setIsLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [validationErrors, setValidationErrors] = createSignal<
    Record<string, string>
  >({});
  const [showSuccess, setShowSuccess] = createSignal(false);

  onMount(() => {
    setFormData({
      name: props.farm.name,
      state: props.farm.state,
      district: props.farm.district,
      village: props.farm.village,
      pincode: props.farm.pincode,
      address_line: props.farm.address_line,
      total_area_acres: props.farm.total_area_acres,
      latitude: props.farm.latitude,
      longitude: props.farm.longitude,
      primary_soil_type: props.farm.primary_soil_type,
      irrigation_type: props.farm.irrigation_type,
    });
  });

  const getDistricts = () => {
    const state = formData().state || "";
    return state ? DISTRICTS_BY_STATE[state] || [] : [];
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    const data = formData();

    if (!data.name || data.name.length < 2) {
      errors.name = "Farm name must be at least 2 characters";
    }

    if (!data.pincode || data.pincode.length !== 6) {
      errors.pincode = "Pincode must be 6 digits";
    }

    if (!data.state) {
      errors.state = "State is required";
    }

    if (!data.district) {
      errors.district = "District is required";
    }

    if (!data.village) {
      errors.village = "Village/VPO is required";
    }

    if (
      !data.total_area_acres || data.total_area_acres < 0.1 ||
      data.total_area_acres > 10000
    ) {
      errors.total_area_acres = "Area must be between 0.1 and 10000 acres";
    }

    // GPS coordinates validation
    if (
      (data.latitude && !data.longitude) || (!data.latitude && data.longitude)
    ) {
      errors.gps = "Both latitude and longitude must be provided together";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) {
      showToast("error", "Please fix the form errors");
      return;
    }

    setIsLoading(true);

    try {
      const { updateFarm } = await import("../../stores/farm.store");
      await updateFarm(props.farm.id, formData());
      setShowSuccess(true);
      showToast("success", "Farm updated successfully");

      setTimeout(() => {
        props.onSuccess();
      }, 1500);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : "Failed to update farm";
      setError(errorMessage);
      showToast("error", errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const updateField = <K extends keyof FarmUpdate>(
    field: K,
    value: FarmUpdate[K],
  ) => {
    setFormData({ ...formData(), [field]: value });
    setValidationErrors({ ...validationErrors(), [field]: "" });
  };

  const updateAddressField = (
    field: keyof FarmAddressData,
    value: string | number | undefined,
  ) => {
    setFormData({ ...formData(), [field]: value });
    setValidationErrors({ ...validationErrors(), [field]: "" });
  };

  return (
    <div class="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-2xl font-bold text-gray-800 mb-6">
        Edit Farm Details
      </h2>

      <Show when={error()}>
        <div class="mb-4 p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg flex items-start gap-2">
          <svg
            class="w-5 h-5 flex-shrink-0 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clip-rule="evenodd"
            />
          </svg>
          <span class="text-sm">{error()}</span>
        </div>
      </Show>

      <Show when={showSuccess()}>
        <div class="mb-4 p-4 bg-green-50 border border-green-200 text-green-800 rounded-lg flex items-start gap-2">
          <svg
            class="w-5 h-5 flex-shrink-0 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clip-rule="evenodd"
            />
          </svg>
          <div>
            <p class="font-medium">Farm updated successfully</p>
          </div>
        </div>
      </Show>

      <form onSubmit={handleSubmit} class="space-y-4">
        {/* Farm Name */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Farm Name <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="farm_name"
            value={formData().name}
            onInput={(e) => updateField("name", e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="e.g., Green Valley Farm"
            required
          />
          <Show when={validationErrors().name}>
            <InlineError message={validationErrors().name} />
          </Show>
        </div>

        {/* Total Area */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Total Land Area (acres) <span class="text-red-500">*</span>
          </label>
          <input
            type="number"
            name="total_area_acres"
            step="0.1"
            min="0.1"
            max="10000"
            value={formData().total_area_acres || ""}
            onInput={(e) =>
              updateField(
                "total_area_acres",
                parseFloat(e.currentTarget.value) || 0,
              )}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="e.g., 5.5"
            required
          />
          <Show when={validationErrors().total_area_acres}>
            <InlineError message={validationErrors().total_area_acres} />
          </Show>
          <p class="mt-1 text-xs text-gray-500">
            Enter area between 0.1 and 10000 acres
          </p>
        </div>

        {/* Soil & Irrigation */}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Primary Soil Type (Optional)
            </label>
            <select
              name="primary_soil_type"
              value={formData().primary_soil_type || ""}
              onInput={(e) =>
                updateField("primary_soil_type", e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">Select Soil Type</option>
              <For each={SOIL_TYPES}>
                {(type) => <option value={type}>{type}</option>}
              </For>
            </select>
            <p class="mt-1 text-xs text-gray-500">
              Default soil type for your plots
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Primary Irrigation Type (Optional)
            </label>
            <select
              name="irrigation_type"
              value={formData().irrigation_type || ""}
              onInput={(e) =>
                updateField("irrigation_type", e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">Select Irrigation Method</option>
              <For each={IRRIGATION_TYPES}>
                {(type) => <option value={type}>{type}</option>}
              </For>
            </select>
            <p class="mt-1 text-xs text-gray-500">
              Default irrigation for your plots
            </p>
          </div>
        </div>

        {/* Farm Address Fields Component */}
        <FarmAddressFields
          addressData={{
            latitude: formData().latitude,
            longitude: formData().longitude,
            pincode: formData().pincode,
            state: formData().state,
            district: formData().district,
            village: formData().village,
            address_line: formData().address_line,
          }}
          onUpdate={updateAddressField}
          validationErrors={validationErrors()}
          showGPSOption={true}
        />

        {/* Buttons */}
        <div class="flex gap-3 pt-4">
          <Show when={props.onCancel}>
            <button
              type="button"
              onClick={props.onCancel}
              class="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-700 font-medium rounded-md transition-colors"
              disabled={isLoading()}
            >
              Cancel
            </button>
          </Show>
          <button
            type="submit"
            disabled={isLoading()}
            class="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors flex items-center justify-center gap-2"
          >
            <Show when={isLoading()}>
              <LoadingSpinner size="sm" color="white" />
            </Show>
            {isLoading() ? "Saving Changes..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FarmEditForm;
