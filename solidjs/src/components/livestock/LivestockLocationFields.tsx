/**
 * Livestock Location Fields Component
 * Address input for livestock location (can differ from farm address)
 */

import { Component, createSignal, Show } from "solid-js";
import apiClient from "../../lib/api-client";

export interface LivestockLocationData {
  latitude?: number;
  longitude?: number;
  pincode?: string;
  state?: string;
  district?: string;
  village?: string;
  address_line?: string;
}

interface LivestockLocationFieldsProps {
  locationData: LivestockLocationData;
  onUpdate: (
    field: keyof LivestockLocationData,
    value: string | number | undefined,
  ) => void;
  validationErrors?: Record<string, string>;
  farmAddress?: {
    pincode?: string;
    state?: string;
    district?: string;
    village?: string;
    address_line?: string;
  };
}

const LivestockLocationFields: Component<LivestockLocationFieldsProps> = (
  props,
) => {
  const [isLoadingPincode, setIsLoadingPincode] = createSignal(false);
  const [villages, setVillages] = createSignal<string[]>([]);
  const [pincodeError, setPincodeError] = createSignal<string | null>(null);
  const [useGPS, setUseGPS] = createSignal(false);
  const [gpsLoading, setGpsLoading] = createSignal(false);
  const [useFarmAddress, setUseFarmAddress] = createSignal(false);

  // Auto-fill address from pincode
  const handlePincodeLookup = async (pincode: string) => {
    if (pincode.length !== 6 || !/^\d{6}$/.test(pincode)) {
      setPincodeError(null);
      setVillages([]);
      return;
    }

    setIsLoadingPincode(true);
    setPincodeError(null);

    try {
      const response = await apiClient.get(`/address/pincode/${pincode}`);

      if (response.data) {
        props.onUpdate("state", response.data.state);
        props.onUpdate("district", response.data.district);
        setVillages(response.data.villages || []);

        // Auto-select first village if only one option
        if (response.data.villages && response.data.villages.length === 1) {
          props.onUpdate("village", response.data.villages[0]);
        }
      }
    } catch (error) {
      console.error("Pincode lookup failed:", error);
      setPincodeError("Invalid pincode or lookup failed");
      setVillages([]);
    } finally {
      setIsLoadingPincode(false);
    }
  };

  // Get GPS coordinates from browser
  const handleGetGPS = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }

    setGpsLoading(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        props.onUpdate("latitude", position.coords.latitude);
        props.onUpdate("longitude", position.coords.longitude);
        setGpsLoading(false);
        setUseGPS(true);
      },
      (error) => {
        console.error("GPS error:", error);
        alert("Unable to get your location. Please enter address manually.");
        setGpsLoading(false);
      },
    );
  };

  // Use farm address
  const handleUseFarmAddress = () => {
    if (!props.farmAddress) return;

    if (props.farmAddress.pincode) {
      props.onUpdate("pincode", props.farmAddress.pincode);
    }
    if (props.farmAddress.state) {
      props.onUpdate("state", props.farmAddress.state);
    }
    if (props.farmAddress.district) {
      props.onUpdate("district", props.farmAddress.district);
    }
    if (props.farmAddress.village) {
      props.onUpdate("village", props.farmAddress.village);
    }
    if (props.farmAddress.address_line) {
      props.onUpdate("address_line", props.farmAddress.address_line);
    }

    setUseFarmAddress(true);
  };

  return (
    <div class="space-y-4 border-t pt-4 mt-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-700">
          Livestock Location (Optional)
        </h3>
        <div class="flex gap-2">
          <Show when={props.farmAddress}>
            <button
              type="button"
              onClick={handleUseFarmAddress}
              class="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              📍 Use Farm Address
            </button>
          </Show>
          <button
            type="button"
            onClick={handleGetGPS}
            disabled={gpsLoading()}
            class="text-sm text-green-600 hover:text-green-700 font-medium disabled:text-gray-400"
          >
            {gpsLoading() ? "Getting location..." : "📍 Use My Location"}
          </button>
        </div>
      </div>

      <p class="text-sm text-gray-500">
        Specify livestock location if different from farm address. This helps
        with location-specific recommendations.
      </p>

      {/* Pincode */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Pincode
        </label>
        <input
          type="text"
          value={props.locationData.pincode || ""}
          onInput={(e) => {
            const value = e.currentTarget.value;
            props.onUpdate("pincode", value);
            if (value.length === 6) {
              handlePincodeLookup(value);
            }
          }}
          maxLength={6}
          pattern="\d{6}"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="Enter 6-digit pincode"
        />
        <Show when={isLoadingPincode()}>
          <p class="mt-1 text-sm text-blue-600">Looking up pincode...</p>
        </Show>
        <Show when={pincodeError()}>
          <p class="mt-1 text-sm text-red-600">{pincodeError()}</p>
        </Show>
        <Show when={props.validationErrors?.pincode}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.pincode}
          </p>
        </Show>
      </div>

      {/* State (auto-filled) */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          State
        </label>
        <input
          type="text"
          value={props.locationData.state || ""}
          onInput={(e) => props.onUpdate("state", e.currentTarget.value)}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
          placeholder="Auto-filled from pincode"
          readOnly={isLoadingPincode()}
        />
        <Show when={props.validationErrors?.state}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.state}
          </p>
        </Show>
      </div>

      {/* District (auto-filled) */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          District
        </label>
        <input
          type="text"
          value={props.locationData.district || ""}
          onInput={(e) => props.onUpdate("district", e.currentTarget.value)}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
          placeholder="Auto-filled from pincode"
          readOnly={isLoadingPincode()}
        />
        <Show when={props.validationErrors?.district}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.district}
          </p>
        </Show>
      </div>

      {/* Village/VPO (dropdown if multiple options) */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Village/VPO
        </label>
        <Show
          when={villages().length > 0}
          fallback={
            <input
              type="text"
              value={props.locationData.village || ""}
              onInput={(e) => props.onUpdate("village", e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Enter village/VPO name"
            />
          }
        >
          <select
            value={props.locationData.village || ""}
            onChange={(e) => props.onUpdate("village", e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select village/VPO</option>
            {villages().map((village) => (
              <option value={village}>{village}</option>
            ))}
          </select>
        </Show>
        <Show when={props.validationErrors?.village}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.village}
          </p>
        </Show>
      </div>

      {/* Address Line */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Address Line (Optional)
        </label>
        <input
          type="text"
          value={props.locationData.address_line || ""}
          onInput={(e) => props.onUpdate("address_line", e.currentTarget.value)}
          maxLength={255}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="House/Building number, Street, Landmark"
        />
      </div>

      {/* GPS Coordinates (if captured) */}
      <Show
        when={useGPS() && props.locationData.latitude &&
          props.locationData.longitude}
      >
        <div class="p-3 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-800">
            ✓ GPS Location captured: {props.locationData.latitude?.toFixed(6)},
            {" "}
            {props.locationData.longitude?.toFixed(6)}
          </p>
        </div>
      </Show>
    </div>
  );
};

export default LivestockLocationFields;
