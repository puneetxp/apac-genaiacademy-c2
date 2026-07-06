/**
 * Delivery Address Fields Component
 * Address input for marketplace delivery location
 */

import { Component, createSignal, Show } from "solid-js";
import apiClient from "../../lib/api-client";

export interface DeliveryAddressData {
  delivery_latitude?: number;
  delivery_longitude?: number;
  delivery_pincode?: string;
  delivery_state?: string;
  delivery_district?: string;
  delivery_village?: string;
  delivery_address_line?: string;
}

interface DeliveryAddressFieldsProps {
  addressData: DeliveryAddressData;
  onUpdate: (
    field: keyof DeliveryAddressData,
    value: string | number | undefined,
  ) => void;
  validationErrors?: Record<string, string>;
  title?: string;
  description?: string;
}

const DeliveryAddressFields: Component<DeliveryAddressFieldsProps> = (
  props,
) => {
  const [isLoadingPincode, setIsLoadingPincode] = createSignal(false);
  const [villages, setVillages] = createSignal<string[]>([]);
  const [pincodeError, setPincodeError] = createSignal<string | null>(null);
  const [useGPS, setUseGPS] = createSignal(false);
  const [gpsLoading, setGpsLoading] = createSignal(false);

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
        props.onUpdate("delivery_state", response.data.state);
        props.onUpdate("delivery_district", response.data.district);
        setVillages(response.data.villages || []);

        // Auto-select first village if only one option
        if (response.data.villages && response.data.villages.length === 1) {
          props.onUpdate("delivery_village", response.data.villages[0]);
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
        props.onUpdate("delivery_latitude", position.coords.latitude);
        props.onUpdate("delivery_longitude", position.coords.longitude);
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

  return (
    <div class="space-y-4 border-t pt-4 mt-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-700">
          {props.title || "Delivery Address (Optional)"}
        </h3>
        <button
          type="button"
          onClick={handleGetGPS}
          disabled={gpsLoading()}
          class="text-sm text-green-600 hover:text-green-700 font-medium disabled:text-gray-400"
        >
          {gpsLoading() ? "Getting location..." : "📍 Use My Location"}
        </button>
      </div>

      <p class="text-sm text-gray-500">
        {props.description ||
          "Specify delivery location for logistics planning."}
      </p>

      {/* Pincode */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Pincode
        </label>
        <input
          type="text"
          value={props.addressData.delivery_pincode || ""}
          onInput={(e) => {
            const value = e.currentTarget.value;
            props.onUpdate("delivery_pincode", value);
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
        <Show when={props.validationErrors?.delivery_pincode}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.delivery_pincode}
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
          value={props.addressData.delivery_state || ""}
          onInput={(e) =>
            props.onUpdate("delivery_state", e.currentTarget.value)}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
          placeholder="Auto-filled from pincode"
          readOnly={isLoadingPincode()}
        />
        <Show when={props.validationErrors?.delivery_state}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.delivery_state}
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
          value={props.addressData.delivery_district || ""}
          onInput={(e) =>
            props.onUpdate("delivery_district", e.currentTarget.value)}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
          placeholder="Auto-filled from pincode"
          readOnly={isLoadingPincode()}
        />
        <Show when={props.validationErrors?.delivery_district}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.delivery_district}
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
              value={props.addressData.delivery_village || ""}
              onInput={(e) =>
                props.onUpdate("delivery_village", e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Enter village/VPO name"
            />
          }
        >
          <select
            value={props.addressData.delivery_village || ""}
            onChange={(e) =>
              props.onUpdate("delivery_village", e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select village/VPO</option>
            {villages().map((village) => (
              <option value={village}>{village}</option>
            ))}
          </select>
        </Show>
        <Show when={props.validationErrors?.delivery_village}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.delivery_village}
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
          value={props.addressData.delivery_address_line || ""}
          onInput={(e) =>
            props.onUpdate("delivery_address_line", e.currentTarget.value)}
          maxLength={255}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="House/Building number, Street, Landmark"
        />
      </div>

      {/* GPS Coordinates (if captured) */}
      <Show
        when={useGPS() && props.addressData.delivery_latitude &&
          props.addressData.delivery_longitude}
      >
        <div class="p-3 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-800">
            ✓ GPS Location captured:{" "}
            {props.addressData.delivery_latitude?.toFixed(6)},{" "}
            {props.addressData.delivery_longitude?.toFixed(6)}
          </p>
        </div>
      </Show>
    </div>
  );
};

export default DeliveryAddressFields;
