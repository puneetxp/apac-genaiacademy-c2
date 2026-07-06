import { Component, createResource, For, Show } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { isAuthenticated } from "../stores/auth.store";
import { DashboardService } from "../services/dashboard.service";

const Home: Component = () => {
  const navigate = useNavigate();

  const [profileStatus] = createResource(
    () => isAuthenticated(),
    async (auth) => {
      if (!auth) return null;
      try {
        return await DashboardService.getProfileStatus();
      } catch (error) {
        return null;
      }
    },
  );

  return (
    <div class="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      {/* Hero Section - Mobile Optimized */}
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-16">
        <div class="text-center">
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-3 sm:mb-4 leading-tight">
            🌾 Rural Farming & Livestock Platform
          </h1>
          <p class="text-base sm:text-lg lg:text-xl text-gray-600 mb-6 sm:mb-8 max-w-3xl mx-auto px-2">
            AI-powered platform helping farmers maximize profits through
            comprehensive annual crop strategies and direct marketplace access
          </p>

          {/* CTA Buttons - Touch Optimized */}
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-4 sm:px-0">
            <Show
              when={!isAuthenticated()}
              fallback={
                <button
                  onClick={() => navigate("/dashboard")}
                  class="w-full sm:w-auto px-8 py-4 bg-green-600 hover:bg-green-700 active:bg-green-800 text-white font-medium rounded-lg transition-colors shadow-lg min-h-touch-android"
                >
                  Go to Dashboard
                </button>
              }
            >
              <button
                onClick={() => navigate("/auth/signup")}
                class="w-full sm:w-auto px-8 py-4 bg-green-600 hover:bg-green-700 active:bg-green-800 text-white font-medium rounded-lg transition-colors shadow-lg min-h-touch-android"
              >
                Get Started
              </button>
              <button
                onClick={() => navigate("/auth/signin")}
                class="w-full sm:w-auto px-8 py-4 bg-white hover:bg-gray-50 active:bg-gray-100 text-green-600 font-medium rounded-lg transition-colors shadow-lg border-2 border-green-600 min-h-touch-android"
              >
                Sign In
              </button>
            </Show>
            <button
              onClick={() => navigate("/farm/register")}
              class="w-full sm:w-auto px-8 py-4 bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 text-white font-medium rounded-lg transition-colors shadow-lg min-h-touch-android flex items-center justify-center gap-2"
            >
              <span>🏡</span> Add Farm
            </button>
          </div>
        </div>

        {/* Authenticated User Content */}
        <Show
          when={isAuthenticated() && profileStatus() &&
            ((profileStatus()?.farms?.length || 0) > 0 ||
              (profileStatus()?.plots?.length || 0) > 0)}
        >
          <div class="mt-12 sm:mt-16 bg-white rounded-lg shadow-lg overflow-hidden border border-green-100 p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span>🌾</span> Your Farming Operations
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Farms Section */}
              <Show when={(profileStatus()?.farms?.length || 0) > 0}>
                <div>
                  <h3 class="text-xl font-semibold text-green-800 mb-4 border-b pb-2">
                    Your Farms
                  </h3>
                  <div class="space-y-4">
                    <For each={profileStatus()?.farms}>
                      {(farm: any) => (
                        <div class="bg-green-50 rounded-md p-4 shadow-sm border border-green-100 flex items-start gap-4">
                          <div class="text-3xl">🏡</div>
                          <div>
                            <h4 class="font-bold text-gray-800 text-lg">
                              {farm.name}
                            </h4>
                            <p class="text-gray-600 text-sm mt-1">
                              Location: {farm.location || "Not specified"}
                            </p>
                            <p class="text-green-700 font-medium text-sm mt-2">
                              {farm.total_area} {farm.area_unit}
                            </p>
                          </div>
                        </div>
                      )}
                    </For>
                  </div>
                </div>
              </Show>

              {/* Plots Section */}
              <Show when={(profileStatus()?.plots?.length || 0) > 0}>
                <div>
                  <h3 class="text-xl font-semibold text-green-800 mb-4 border-b pb-2">
                    Your Plots & Crops
                  </h3>
                  <div class="space-y-4">
                    <For each={profileStatus()?.plots}>
                      {(plot: any) => (
                        <div class="bg-white rounded-md p-4 shadow-sm border border-green-200 hover:shadow-md transition-shadow">
                          <div class="flex justify-between items-center mb-2">
                            <h4 class="font-bold text-gray-800">
                              {plot.plot_name}
                            </h4>
                            <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                              {plot.area} {plot.area_unit}
                            </span>
                          </div>
                          <Show
                            when={plot.crop_type}
                            fallback={
                              <p class="text-gray-500 text-sm italic">
                                No active crop
                              </p>
                            }
                          >
                            <div class="flex items-center gap-2 mt-2">
                              <span class="text-xl">🌱</span>
                              <span class="text-gray-700 font-medium">
                                {plot.crop_type}
                              </span>
                            </div>
                            <Show when={plot.crop_variety}>
                              <p class="text-gray-500 text-sm mt-1 ml-7">
                                Variety: {plot.crop_variety}
                              </p>
                            </Show>
                          </Show>
                        </div>
                      )}
                    </For>
                  </div>
                </div>
              </Show>
            </div>

            <div class="mt-6 pt-4 border-t flex justify-center">
              <button
                onClick={() => navigate("/dashboard")}
                class="text-green-600 hover:text-green-800 font-medium flex items-center gap-1 transition-colors"
              >
                View full dashboard <span>→</span>
              </button>
            </div>
          </div>
        </Show>

        {/* Features - Mobile Optimized Grid */}
        <div class="mt-12 sm:mt-20 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          <div class="bg-white p-5 sm:p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div class="text-4xl sm:text-3xl mb-3 sm:mb-4">🌾</div>
            <h3 class="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
              Annual Crop Strategy
            </h3>
            <p class="text-sm sm:text-base text-gray-600 leading-relaxed">
              Get AI-powered recommendations for Kharif, Rabi, and Zaid seasons
              with profit estimates and implementation timelines
            </p>
          </div>

          <div class="bg-white p-5 sm:p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div class="text-4xl sm:text-3xl mb-3 sm:mb-4">🤝</div>
            <h3 class="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
              Direct Marketplace
            </h3>
            <p class="text-sm sm:text-base text-gray-600 leading-relaxed">
              Connect directly with buyers, eliminate middlemen, and get better
              prices for your produce
            </p>
          </div>

          <div class="bg-white p-5 sm:p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow sm:col-span-2 lg:col-span-1">
            <div class="text-4xl sm:text-3xl mb-3 sm:mb-4">📊</div>
            <h3 class="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
              Market Intelligence
            </h3>
            <p class="text-sm sm:text-base text-gray-600 leading-relaxed">
              Access real-time market data, demand forecasts, and profit
              projections to make informed decisions
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
