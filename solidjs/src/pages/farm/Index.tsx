import { Component, For, Show, createResource } from "solid-js";
import apiClient from "../../lib/api-client";

interface FarmRecord {
  id: number;
  name: string;
  description?: string | null;
  location_state: string;
  location_district: string;
  location_block?: string | null;
  location_village?: string | null;
  total_area: number;
  area_unit?: string | null;
  primary_soil_type?: string | null;
  irrigation_type?: string | null;
  is_active?: boolean | number | null;
  created_at?: string;
}

const fetchFarms = async (): Promise<FarmRecord[]> => {
  // apiClient baseURL already includes /api/v1; prepend slash to keep version segment intact
  const response = await apiClient.get<FarmRecord[]>("/islogin/farm", {
    cache: false,
  });
  return response.data;
};

const FarmIndex: Component = () => {
  const [farms] = createResource(fetchFarms);

  return (
    <section class="mx-auto max-w-6xl px-4 py-10">
      <header class="mb-8 flex items-center justify-between">
        <div>
          <p class="text-sm uppercase tracking-wide text-green-600">My Farms</p>
          <h1 class="text-3xl font-bold text-gray-900">Registered holdings</h1>
          <p class="mt-2 text-sm text-gray-500">
            Listing all farms returned by the /api/islogin/farm endpoint.
          </p>
        </div>
      </header>

      <Show when={!farms.loading} fallback={<div class="text-gray-500">Loading farms...</div>}>
        <Show when={(farms() || []).length > 0} fallback={<div class="rounded-lg border border-dashed border-gray-300 p-8 text-center text-gray-500">No farms found.</div>}>
          <div class="grid gap-4 md:grid-cols-2">
            <For each={farms()}>
              {(farm) => (
                <article class="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
                  <div class="mb-3 flex items-center justify-between">
                    <h2 class="text-xl font-semibold text-gray-900">{farm.name}</h2>
                    <span class={`rounded-full px-3 py-1 text-xs font-semibold ${farm.is_active ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                      {farm.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>
                  <p class="text-sm text-gray-600">
                    {farm.description || "No description provided."}
                  </p>

                  <dl class="mt-4 grid grid-cols-2 gap-3 text-sm text-gray-700">
                    <div>
                      <dt class="text-xs uppercase tracking-wide text-gray-500">Location</dt>
                      <dd>
                        {[farm.location_village, farm.location_block, farm.location_district, farm.location_state]
                          .filter(Boolean)
                          .join(", ") || "Unknown"}
                      </dd>
                    </div>
                    <div>
                      <dt class="text-xs uppercase tracking-wide text-gray-500">Area</dt>
                      <dd>
                        {farm.total_area} {farm.area_unit || "acres"}
                      </dd>
                    </div>
                    <div>
                      <dt class="text-xs uppercase tracking-wide text-gray-500">Soil</dt>
                      <dd>{farm.primary_soil_type || "-"}</dd>
                    </div>
                    <div>
                      <dt class="text-xs uppercase tracking-wide text-gray-500">Irrigation</dt>
                      <dd>{farm.irrigation_type || "-"}</dd>
                    </div>
                  </dl>

                  <p class="mt-4 text-xs text-gray-400">
                    Registered on {farm.created_at ? new Date(farm.created_at).toLocaleDateString() : "N/A"}
                  </p>
                </article>
              )}
            </For>
          </div>
        </Show>
      </Show>
    </section>
  );
};

export default FarmIndex;
