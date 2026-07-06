/**
 * Farm Address Fields Component
 * Reusable address input fields for farm registration with pincode lookup
 */

import { Component, createSignal, Show } from "solid-js";
import apiClient from "../../lib/api-client";
import SLUSIService, { type SoilLookupResponse } from "../../services/slusi.service";

export interface SoilFieldData {
  nitrogen?: number | null;
  phosphorus?: number | null;
  potassium?: number | null;
  sulfur?: number | null;
  boron?: number | null;
  iron?: number | null;
  zinc?: number | null;
  copper?: number | null;
  manganese?: number | null;
  organic_carbon?: number | null;
  ph_level?: number | null;
  electrical_conductivity?: number | null;
  soil_depth_class?: string | null;
  slope_class?: string | null;
  erosion_class?: string | null;
  soil_texture_class?: string | null;
  land_capability_class?: string | null;
  land_irrigability_class?: string | null;
  hydrological_soil_group?: string | null;
}

export interface FarmAddressData {
  latitude?: number;
  longitude?: number;
  pincode?: string;
  state?: string;
  district?: string;
  village?: string;
  address_line?: string;
}

interface FarmAddressFieldsProps {
  addressData: FarmAddressData;
  onUpdate: (
    field: keyof FarmAddressData,
    value: string | number | undefined,
  ) => void;
  onSoilTypeFound?: (soilType: string) => void;
  onSoilDataFound?: (data: SoilFieldData, partial: boolean) => void;
  validationErrors?: Record<string, string>;
  showGPSOption?: boolean;
}

const FarmAddressFields: Component<FarmAddressFieldsProps> = (props) => {
  const [isLoadingPincode, setIsLoadingPincode] = createSignal(false);
  const [villages, setVillages] = createSignal<string[]>([]);
  const [pincodeError, setPincodeError] = createSignal<string | null>(null);
  const [useGPS, setUseGPS] = createSignal(false);
  const [gpsLoading, setGpsLoading] = createSignal(false);
  const [soilLookupLoading, setSoilLookupLoading] = createSignal(false);
  const [soilPartial, setSoilPartial] = createSignal(false);

  // STEP 1: Auto-fill base address from standard Pincode API
  const handlePincodeLookup = async (pincode: string) => {
    if (pincode.length !== 6 || !/^\d{6}$/.test(pincode)) {
      setPincodeError(null);
      setVillages([]);
      return;
    }

    setIsLoadingPincode(true);
    setPincodeError(null);

    try {
      // Use standard Pincode API for state, district, and village list
      const response = await apiClient.get(`/address/pincode/${pincode}`);

      if (response.data) {
        if (response.data.state) props.onUpdate("state", response.data.state);
        if (response.data.district) props.onUpdate("district", response.data.district);
        
        if (response.data.villages && response.data.villages.length > 0) {
           setVillages(response.data.villages);
           // NOTE: We don't auto-fill soil yet, selection does that
        }
      }
    } catch (error) {
      console.error("Standard Pincode lookup failed:", error);
      setPincodeError("Could not find Pincode in database");
      setVillages([]);
    } finally {
      setIsLoadingPincode(false);
    }
  };

  // STEP 2: Enrich with AI-predicted soil type upon village selection
  const handleVillageSelection = async (village: string) => {
    const p = props.addressData.pincode;
    if (!p || !village) return;

    try {
      // Call Bedrock AI for precise soil type for this VPO
      const response = await apiClient.get(`/farms/location-lookup?pincode=${p}&village=${village}`);
      if (response.data && response.data.primary_soil_type && props.onSoilTypeFound) {
        props.onSoilTypeFound(response.data.primary_soil_type);
      }
    } catch (error) {
      console.error("AI Village enrichment failed:", error);
    }
  };

  // Get GPS coordinates from browser and enrich via Bedrock AI + SLUSI
  const handleGetGPS = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }

    setGpsLoading(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        props.onUpdate("latitude", lat);
        props.onUpdate("longitude", lon);
        setUseGPS(true);

        let resolvedState = props.addressData.state;
        let resolvedDistrict = props.addressData.district;

        // Attempt to auto-fill state, district, pincode, and soil type from GPS
        try {
          const response = await apiClient.get(`/farms/location-lookup?latitude=${lat}&longitude=${lon}`);
          if (response.data) {
            if (response.data.state) {
              props.onUpdate("state", response.data.state);
              resolvedState = response.data.state;
            }
            if (response.data.district) {
              props.onUpdate("district", response.data.district);
              resolvedDistrict = response.data.district;
            }
            if (response.data.pincode) props.onUpdate("pincode", response.data.pincode);
            if (response.data.village) {
              props.onUpdate("village", response.data.village);
              setVillages([response.data.village]);
            }
            if (response.data.primary_soil_type && props.onSoilTypeFound) {
              props.onSoilTypeFound(response.data.primary_soil_type);
            }
          }
        } catch (error) {
          console.error("AI GPS enrichment failed:", error);
        }

        // SLUSI soil lookup — fires after location is resolved
        if (resolvedState && resolvedDistrict && props.onSoilDataFound) {
          setSoilLookupLoading(true);
          try {
            const soilData = await SLUSIService.fetchSoilLookup(lat, lon, resolvedState, resolvedDistrict);
            const profile = soilData.shc_profile;
            setSoilPartial(profile.partial_data);
            props.onSoilDataFound(
              {
                nitrogen: profile.nitrogen,
                phosphorus: profile.phosphorus,
                potassium: profile.potassium,
                sulfur: profile.sulfur,
                boron: profile.boron,
                iron: profile.iron,
                zinc: profile.zinc,
                copper: profile.copper,
                manganese: profile.manganese,
                organic_carbon: profile.organic_carbon,
                ph_level: profile.ph_level,
                electrical_conductivity: profile.electrical_conductivity,
                soil_depth_class: profile.soil_depth_class,
                slope_class: profile.slope_class,
                erosion_class: profile.erosion_class,
                soil_texture_class: profile.soil_texture_class,
                land_capability_class: profile.land_capability_class,
                land_irrigability_class: profile.land_irrigability_class,
                hydrological_soil_group: profile.hydrological_soil_group,
              },
              profile.partial_data,
            );
          } catch (error) {
            console.error("SLUSI soil lookup failed:", error);
          } finally {
            setSoilLookupLoading(false);
          }
        }

        setGpsLoading(false);
      },
      (error) => {
        console.error("GPS error:", error);
        alert("Unable to get farm location. Please enter address manually.");
        setGpsLoading(false);
      },
    );
  };

  return (
    <div class="space-y-4 border-t pt-4 mt-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-700">Farm Address</h3>
        <Show when={props.showGPSOption !== false}>
          <button
            type="button"
            onClick={handleGetGPS}
            disabled={gpsLoading()}
            class="text-sm text-green-600 hover:text-green-700 font-medium disabled:text-gray-400"
          >
            {gpsLoading() ? "Getting location..." : "📍 Capture Farm Location"}
          </button>
        </Show>
      </div>

      <p class="text-sm text-gray-500">
        Farm address helps us provide location-specific crop recommendations and
        weather alerts.
      </p>

      {/* Pincode & Search Suggestions */}
      <div class="relative">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Pincode <span class="text-red-500">*</span>
        </label>
        <div class="relative">
          <input
            type="text"
            name="pincode"
            value={props.addressData.pincode || ""}
            onInput={(e) => {
              const value = e.currentTarget.value;
              props.onUpdate("pincode", value);
              if (value.length === 6) {
                handlePincodeLookup(value);
              } else {
                setVillages([]);
              }
            }}
            maxLength={6}
            pattern="\d{6}"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Enter 6-digit pincode"
          />
          <Show when={isLoadingPincode()}>
            <div class="absolute right-3 top-2.5">
              <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-green-600"></div>
            </div>
          </Show>
        </div>

        {/* Floating AI Suggestions List (Search Style) */}
        <Show when={villages().length > 0}>
          <div class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
            <div class="p-2 bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Select your Village/VPO
            </div>
            <ul class="divide-y divide-gray-100">
              {villages().slice(0, 5).map((v) => (
                <li>
                  <button
                    type="button"
                    class="w-full px-4 py-3 text-left hover:bg-green-50 transition-colors flex flex-col"
                    onClick={() => {
                      props.onUpdate("village", v);
                      handleVillageSelection(v); // Trigger AI step for soil
                      setVillages([]); // Hide suggestions after selection
                    }}
                  >
                    <span class="font-medium text-gray-900">{v}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
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

      {/* State - Required (auto-filled) */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          State <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          name="state"
          value={props.addressData.state || ""}
          onInput={(e) => props.onUpdate("state", e.currentTarget.value)}
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
          placeholder="Auto-filled from pincode"
          readOnly
        />
        <Show when={props.validationErrors?.state}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.state}
          </p>
        </Show>
      </div>

      {/* District - Required (auto-filled) */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          District <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          name="district"
          value={props.addressData.district || ""}
          onInput={(e) => props.onUpdate("district", e.currentTarget.value)}
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
          placeholder="Auto-filled from pincode"
          readOnly
        />
        <Show when={props.validationErrors?.district}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.district}
          </p>
        </Show>
      </div>

      {/* Selected Village Display - Manual override allowed */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Village/VPO <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          name="village"
          value={props.addressData.village || ""}
          onInput={(e) => props.onUpdate("village", e.currentTarget.value)}
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="Select from suggestions or enter manually"
        />
        <Show when={props.validationErrors?.village}>
          <p class="mt-1 text-sm text-red-600">
            {props.validationErrors?.village}
          </p>
        </Show>
      </div>

      {/* Address Line - Optional */}
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Address Line (Optional)
        </label>
        <input
          type="text"
          name="address_line"
          value={props.addressData.address_line || ""}
          onInput={(e) => props.onUpdate("address_line", e.currentTarget.value)}
          maxLength={255}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="Farm house number, Street, Landmark"
        />
      </div>

      {/* GPS Coordinates (if captured) */}
      <Show
        when={useGPS() && props.addressData.latitude &&
          props.addressData.longitude}
      >
        <div class="p-3 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-800">
            ✓ Farm GPS Location captured:{" "}
            {props.addressData.latitude?.toFixed(6)},{" "}
            {props.addressData.longitude?.toFixed(6)}
          </p>
          <p class="text-xs text-green-600 mt-1">
            This enables GPS-enhanced AI recommendations for your farm.
          </p>
        </div>
      </Show>
    </div>
  );
};

export default FarmAddressFields;
