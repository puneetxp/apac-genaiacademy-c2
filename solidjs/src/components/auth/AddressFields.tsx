/**
 * Address Fields Component
 * Reusable address input fields with pincode lookup integration
 */

import { Component, createSignal, Show, createEffect } from 'solid-js';
import apiClient from '../../lib/api-client';

export interface AddressData {
  latitude?: number;
  longitude?: number;
  pincode?: string;
  state?: string;
  district?: string;
  village?: string;
  address_line?: string;
}

interface AddressFieldsProps {
  addressData: AddressData;
  onUpdate: (field: keyof AddressData, value: string | number | undefined) => void;
  validationErrors?: Record<string, string>;
  showGPSOption?: boolean;
}

const AddressFields: Component<AddressFieldsProps> = (props) => {
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
      const response = await apiClient.get(`/address/pincode/${pincode}`, { requiresAuth: false });
      
      if (response.data) {
        props.onUpdate('state', response.data.state);
        props.onUpdate('district', response.data.district);
        setVillages(response.data.villages || []);
        
        // Auto-select first village if only one option
        if (response.data.villages && response.data.villages.length === 1) {
          props.onUpdate('village', response.data.villages[0]);
        }
      }
    } catch (error) {
      console.error('Pincode lookup failed:', error);
      setPincodeError('Invalid pincode or lookup failed');
      setVillages([]);
    } finally {
      setIsLoadingPincode(false);
    }
  };

  // Get GPS coordinates from browser
  const handleGetGPS = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }

    setGpsLoading(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        props.onUpdate('latitude', position.coords.latitude);
        props.onUpdate('longitude', position.coords.longitude);
        setGpsLoading(false);
        setUseGPS(true);
      },
      (error) => {
        console.error('GPS error:', error);
        alert('Unable to get your location. Please enter address manually.');
        setGpsLoading(false);
      }
    );
  };

  return (
    <div class="space-y-4 border-t pt-4 mt-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-700">Address (Optional)</h3>
        <Show when={props.showGPSOption !== false}>
          <button
            type="button"
            onClick={handleGetGPS}
            disabled={gpsLoading()}
            class="text-sm text-green-600 hover:text-green-700 font-medium disabled:text-gray-400"
          >
            {gpsLoading() ? 'Getting location...' : '📍 Use My Location'}
          </button>
        </Show>
      </div>

      <p class="text-sm text-gray-500">
        Adding your address helps us provide location-specific recommendations.
      </p>

      {/* Pincode */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Pincode
        </label>
        <input
          type="text"
          value={props.addressData.pincode || ''}
          onInput={(e) => {
            const value = e.currentTarget.value;
            props.onUpdate('pincode', value);
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
          <p class="mt-1 text-sm text-red-600">{props.validationErrors?.pincode}</p>
        </Show>
      </div>

      {/* State (auto-filled) */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          State
        </label>
        <input
          type="text"
          value={props.addressData.state || ''}
          onInput={(e) => props.onUpdate('state', e.currentTarget.value)}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
          placeholder="Auto-filled from pincode"
          readOnly={isLoadingPincode()}
        />
        <Show when={props.validationErrors?.state}>
          <p class="mt-1 text-sm text-red-600">{props.validationErrors?.state}</p>
        </Show>
      </div>

      {/* District (auto-filled) */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          District
        </label>
        <input
          type="text"
          value={props.addressData.district || ''}
          onInput={(e) => props.onUpdate('district', e.currentTarget.value)}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
          placeholder="Auto-filled from pincode"
          readOnly={isLoadingPincode()}
        />
        <Show when={props.validationErrors?.district}>
          <p class="mt-1 text-sm text-red-600">{props.validationErrors?.district}</p>
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
              value={props.addressData.village || ''}
              onInput={(e) => props.onUpdate('village', e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Enter village/VPO name"
            />
          }
        >
          <select
            value={props.addressData.village || ''}
            onChange={(e) => props.onUpdate('village', e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select village/VPO</option>
            {villages().map((village) => (
              <option value={village}>{village}</option>
            ))}
          </select>
        </Show>
        <Show when={props.validationErrors?.village}>
          <p class="mt-1 text-sm text-red-600">{props.validationErrors?.village}</p>
        </Show>
      </div>

      {/* Address Details */}
      <div>
        <input
          type="text"
          value={props.addressData.address_line || ''}
          onInput={(e) => props.onUpdate('address_line', e.currentTarget.value)}
          maxLength={255}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="House/Building number, Street, Landmark"
        />
      </div>

      {/* GPS Coordinates (if captured) */}
      <Show when={useGPS() && props.addressData.latitude && props.addressData.longitude}>
        <div class="p-3 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-800">
            ✓ GPS Location captured: {props.addressData.latitude?.toFixed(6)}, {props.addressData.longitude?.toFixed(6)}
          </p>
        </div>
      </Show>
    </div>
  );
};

export default AddressFields;
