/**
 * Dashboard Page
 * Main dashboard for authenticated users with comprehensive farming overview
 */

import {
  Component,
  createResource,
  createSignal,
  For,
  lazy,
  Show,
  Suspense,
} from "solid-js";
import { A, useNavigate } from "@solidjs/router";
import { isAuthenticated, signOut, user } from "../stores/auth.store";
import { DashboardService } from "../services/dashboard.service";
import NotificationPermissionPrompt from "../components/notifications/NotificationPermissionPrompt";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { ErrorDisplay } from "../components/ui/ErrorDisplay";
import { SkeletonDashboard } from "../components/ui/SkeletonScreen";
import { showToast } from "../components/ui/Toast";
import ServicesMenu from "../components/ui/ServicesMenu";
import AskAnythingCard from "../components/assistant/AskAnythingCard";
import FarmJourney from "../components/dashboard/FarmJourney";
import SatelliteHealthCard from "../components/farm/SatelliteHealthCard";
import { showSection } from "../stores/app-config.store";

// Lazy load heavy dashboard components for better performance
const QuickStats = lazy(() => import("../components/dashboard/QuickStats"));
const ActiveCropsCard = lazy(() =>
  import("../components/dashboard/ActiveCropsCard")
);
const MarketplaceListingsCard = lazy(() =>
  import("../components/dashboard/MarketplaceListingsCard")
);
const UpcomingTasksCard = lazy(() =>
  import("../components/dashboard/UpcomingTasksCard")
);
const BuyerInterestsCard = lazy(() =>
  import("../components/dashboard/BuyerInterestsCard")
);
const WeatherAlertsCard = lazy(() =>
  import("../components/dashboard/WeatherAlertsCard")
);
const StrategyTimelineProgress = lazy(() =>
  import("../components/dashboard/StrategyTimelineProgress")
);
const AnalyticsBoard = lazy(() =>
  import("../components/dashboard/board/AnalyticsBoard")
);

const Dashboard: Component = () => {
  const navigate = useNavigate();
  const [refreshTrigger, setRefreshTrigger] = createSignal(0);

  // First, check if user has any data (lightweight check)
  const [profileStatus] = createResource(
    () => ({ trigger: refreshTrigger(), authenticated: isAuthenticated() }),
    async ({ authenticated }) => {
      if (!authenticated) return null;
      try {
        return await DashboardService.getProfileStatus();
      } catch (error) {
        console.error("Failed to check profile status:", error);
        return null;
      }
    },
  );

  // The dashboardData is now embedded within profileStatus
  const dashboardData = () => profileStatus()?.dashboard_data;

  const handleSignOut = async () => {
    await signOut();
    navigate("/auth/signin");
  };

  const handleRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
    showToast("info", "Refreshing dashboard...");
  };

  const handleGetStrategy = (farmId?: number) => {
    if (farmId) {
      navigate(`/strategy/request?farmId=${farmId}`);
      return;
    }

    if ((profileStatus()?.farms?.length || 0) === 0) {
      showToast("warning", "Add a farm first so we know which profile to analyze.");
      navigate("/farm/register");
      return;
    }

    navigate("/strategy/select-farm");
  };

  return (
    <div class="min-h-screen bg-gray-50">
      {/* Notification Permission Prompt */}
      <NotificationPermissionPrompt
        autoShow={true}
        onPermissionGranted={() => console.log("Notifications enabled")}
        onPermissionDenied={() => console.log("Notifications denied")}
      />

      {/* Header */}
      <header class="bg-white/95 backdrop-blur border-b border-gray-200 sticky top-0 z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div class="flex items-center justify-between gap-3">
            <div class="min-w-0">
              <h1 class="text-lg sm:text-2xl font-bold text-gray-900 truncate">
                Farmer Dashboard
              </h1>
              <p class="text-xs sm:text-sm text-gray-500 truncate">
                Welcome back, {user()?.full_name || user()?.username}
              </p>
            </div>
            <div class="flex items-center gap-1.5 sm:gap-2 shrink-0">
              <A
                href="/assistant"
                class="px-3 sm:px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm flex items-center gap-1.5"
                title="Chat or talk with CropSense AI about your farm"
              >
                <span>✦</span> Ask AI
              </A>
              <A
                href="/farm/register"
                class="px-3 sm:px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm flex items-center gap-1.5"
                title="Register a new farm"
              >
                <span>＋</span><span class="hidden sm:inline">Add Farm</span>
              </A>
              {/* Secondary links: desktop only (mobile has the bottom nav) */}
              <div class="hidden md:flex items-center gap-0.5 ml-1 pl-2 border-l border-gray-200">
                <A href="/livestock" class="px-2.5 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg" title="Livestock management">
                  🐄 Livestock
                </A>
                <A href="/livestock/doctors" class="px-2.5 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg" title="Veterinary doctors">
                  🩺 Vets
                </A>
                <A href="/settings" class="px-2.5 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg" title="Choose what the dashboard shows" aria-label="Configure dashboard">
                  ⚙️
                </A>
                <button type="button" onClick={handleRefresh} class="px-2.5 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg" title="Refresh dashboard" aria-label="Refresh dashboard">
                  🔄
                </button>
                <button type="button" onClick={handleSignOut} class="px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg font-medium">
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-24 sm:pb-8">
        {/* The whole season at a glance: land → soil → plan → sow → protect → harvest → sell, plus livestock */}
        <Show when={showSection("journey") && !profileStatus.loading && profileStatus()}>
          <div class="mb-6">
            <FarmJourney
              farms={profileStatus()?.farms || []}
              hasStrategies={!!profileStatus()?.has_strategies}
              data={profileStatus()?.dashboard_data}
            />
          </div>
        </Show>
        {/* Ask or add anything (farm, crop, expense, sale, animal) by voice or text — works before onboarding too */}
        <Show when={showSection("assistant") && !profileStatus.loading && !profileStatus()?.is_onboarding_complete}>
          <div class="mb-8">
            <AskAnythingCard />
          </div>
        </Show>
        {/* Every service in one place; outside the loading/empty states so navigation always works. */}
        <Show when={showSection("services")}>
          <section class="bg-white rounded-lg shadow p-4 sm:p-6 mb-8" aria-label="All services">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">All Services</h2>
            <ServicesMenu variant="grid" searchable />
          </section>
        </Show>
        <Show
          when={!profileStatus.loading}
          fallback={<SkeletonDashboard />}
        >
          <Show
            when={profileStatus() && profileStatus()!.is_onboarding_complete}
            fallback={
              <div class="text-center py-20">
                <div class="text-6xl mb-6">🌾</div>
                <h2 class="text-3xl font-bold text-gray-900 mb-3">
                  Welcome to CropSense AI!
                </h2>
                <p class="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
                  Get started by registering your farm. Once registered, you can
                  create an AI-powered annual strategy, track your crops, and
                  connect with buyers in the marketplace.
                </p>

                {/* Onboarding Steps */}
                <div class="max-w-4xl mx-auto mb-10">
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                    <div class="bg-white rounded-lg shadow-md p-6 border-2 border-green-200">
                      <div class="text-4xl mb-3">1️⃣</div>
                      <h3 class="text-xl font-semibold text-gray-900 mb-2">
                        Register Your Farm
                      </h3>
                      <p class="text-gray-600 text-sm">
                        Add your farm details including location, soil type, and
                        irrigation facilities.
                      </p>
                    </div>

                    <div class="bg-white rounded-lg shadow-md p-6 border-2 border-blue-200">
                      <div class="text-4xl mb-3">2️⃣</div>
                      <h3 class="text-xl font-semibold text-gray-900 mb-2">
                        Get AI Strategy
                      </h3>
                      <p class="text-gray-600 text-sm">
                        Receive personalized crop recommendations for Kharif,
                        Rabi, and Zaid seasons.
                      </p>
                    </div>

                    <div class="bg-white rounded-lg shadow-md p-6 border-2 border-purple-200">
                      <div class="text-4xl mb-3">3️⃣</div>
                      <h3 class="text-xl font-semibold text-gray-900 mb-2">
                        Connect with Buyers
                      </h3>
                      <p class="text-gray-600 text-sm">
                        List your crops in the marketplace and connect with
                        verified buyers.
                      </p>
                    </div>
                  </div>
                </div>

                {/* CTA Buttons */}
                <div class="flex justify-center gap-4">
                  <A
                    href="/farm/register"
                    class="px-8 py-4 bg-green-600 hover:bg-green-700 text-white text-lg font-semibold rounded-lg shadow-lg transition-all transform hover:scale-105 text-center"
                  >
                    🏡 Register Your Farm
                  </A>
                  <A
                    href="/marketplace"
                    class="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white text-lg font-semibold rounded-lg shadow-lg transition-all transform hover:scale-105 text-center"
                  >
                    🛒 Browse Marketplace
                  </A>
                </div>
              </div>
            }
          >
            {/* User has data - show full dashboard */}
            <Show
              when={!profileStatus.loading && !profileStatus.error}
              fallback={
                <Show
                  when={profileStatus.error}
                  fallback={<SkeletonDashboard />}
                >
                  <ErrorDisplay
                    error={profileStatus.error}
                    onRetry={handleRefresh}
                    title="Failed to load dashboard"
                  />
                </Show>
              }
            >
              <Show when={dashboardData()}>
                {(data) => (
                  <div class="space-y-6">
                    {/* Quick Stats */}
                    <Show when={showSection("stats")}>
                      <Suspense
                        fallback={
                          <div class="h-32 bg-gray-100 animate-pulse rounded-lg" />
                        }
                      >
                        <QuickStats stats={data().stats} />
                      </Suspense>
                    </Show>

                    {/* Crop health from space (Sentinel-2) for the farmer's farms */}
                    <Show when={showSection("satellite")}>
                      <SatelliteHealthCard />
                    </Show>

                    {/* Farm & livestock board: charts, tables and AI projections */}
                    <Show when={showSection("board")}>
                      <Suspense
                        fallback={
                          <div class="h-96 bg-gray-100 animate-pulse rounded-lg" />
                        }
                      >
                        <AnalyticsBoard
                          data={data()}
                          farms={profileStatus()?.farms || []}
                        />
                      </Suspense>
                    </Show>

                    <Show when={showSection("assistant")}>
                      <AskAnythingCard />
                    </Show>

                    {/* Quick Actions */}
                    <Show when={showSection("quickActions")}>
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <A
                        href="/farm/register"
                        class="p-4 bg-gradient-to-br from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white rounded-lg shadow-lg transition-all text-left"
                      >
                        <div class="text-2xl mb-2">🏡</div>
                        <h3 class="font-semibold text-lg">Add Farm</h3>
                        <p class="text-sm opacity-90">Register new land</p>
                      </A>
                      <button
                        type="button"
                        onClick={() => handleGetStrategy()}
                        class="p-4 bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg shadow-lg transition-all text-left"
                      >
                        <div class="text-2xl mb-2">📊</div>
                        <h3 class="font-semibold text-lg">Get Strategy</h3>
                        <p class="text-sm opacity-90">AI-powered plan</p>
                      </button>
                      <A
                        href="/marketplace"
                        class="p-4 bg-gradient-to-br from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white rounded-lg shadow-lg transition-all text-left"
                      >
                        <div class="text-2xl mb-2">🛒</div>
                        <h3 class="font-semibold text-lg">Marketplace</h3>
                        <p class="text-sm opacity-90">Browse listings</p>
                      </A>
                      <A
                        href="/marketplace/my-listings"
                        class="p-4 bg-gradient-to-br from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-lg shadow-lg transition-all text-left"
                      >
                        <div class="text-2xl mb-2">📝</div>
                        <h3 class="font-semibold text-lg">My Listings</h3>
                        <p class="text-sm opacity-90">Manage sales</p>
                      </A>
                    </div>
                    </Show>

                    {/* Farms Display */}
                    <Show when={showSection("farms") && (profileStatus()?.farms?.length || 0) > 0}>
                      <div class="bg-white rounded-lg shadow-md p-6 border border-green-100">
                        <div class="flex justify-between items-center mb-4 border-b pb-2">
                          <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                            <span>🏡</span> Your Farms
                          </h2>
                          <button
                            onClick={() => navigate("/farm/register")}
                            class="text-sm text-green-600 hover:text-green-800 font-medium"
                          >
                            + Add Another
                          </button>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          <For each={profileStatus()?.farms}>
                            {(farm: any) => (
                              <div class="bg-green-50 rounded-lg p-4 shadow-sm border border-green-200">
                                <h3 class="font-bold text-gray-800 text-lg">
                                  {farm.name}
                                </h3>
                                <p class="text-gray-600 text-sm mt-1">
                                  Location: {farm.location || "Not specified"}
                                </p>
                                <div class="mt-3 flex justify-between items-center">
                                  <span class="text-green-700 font-medium text-sm bg-green-100 px-2 py-1 rounded">
                                    {farm.total_area} {farm.area_unit}
                                  </span>
                                  <div class="flex gap-2">
                                    <Show when={farm.ph_level || farm.nitrogen}>
                                      <span class="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800" title="Soil Test Data Available">
                                        🌱 Soil Data
                                      </span>
                                    </Show>
                                    <span
                                      class={`text-xs px-2 py-1 rounded ${
                                        farm.is_active
                                          ? "bg-green-100 text-green-800"
                                          : "bg-gray-100 text-gray-800"
                                      }`}
                                    >
                                      {farm.is_active ? "Active" : "Inactive"}
                                    </span>
                                  </div>
                                </div>
                                <div class="mt-4 pt-4 border-t border-green-200/50 flex gap-2">
                                  <button
                                    onClick={() => navigate(`/farm/${farm.id}`)}
                                    class="flex-1 py-2 bg-white text-green-700 hover:bg-green-100 font-medium text-sm rounded transition-colors"
                                  >
                                    Manage Farm
                                  </button>
                                  <button
                                    onClick={() =>
                                      navigate(`/analytics/farm/${farm.id}`)}
                                    class="flex-1 py-2 bg-green-600 text-white hover:bg-green-700 font-medium text-sm rounded transition-colors"
                                  >
                                    Analytics
                                  </button>
                                  <button
                                    onClick={() => handleGetStrategy(farm.id)}
                                    class="flex-1 py-2 bg-blue-600 text-white hover:bg-blue-700 font-medium text-sm rounded transition-colors"
                                  >
                                    Get Strategy
                                  </button>
                                </div>
                              </div>
                            )}
                          </For>
                        </div>
                      </div>
                    </Show>

                    {/* Weather Alerts - Priority Display */}
                    <Show
                      when={showSection("weather") && data().weather_alerts &&
                        data().weather_alerts.length > 0}
                    >
                      <Suspense
                        fallback={
                          <div class="h-40 bg-gray-100 animate-pulse rounded-lg" />
                        }
                      >
                        <WeatherAlertsCard alerts={data().weather_alerts} />
                      </Suspense>
                    </Show>

                    {/* Strategy Timeline Progress */}
                    <Show
                      when={showSection("strategy") && data().strategy_timeline &&
                        data().strategy_timeline!.length > 0}
                    >
                      <Suspense
                        fallback={
                          <div class="h-64 bg-gray-100 animate-pulse rounded-lg" />
                        }
                      >
                        <StrategyTimelineProgress
                          seasons={data().strategy_timeline!}
                        />
                      </Suspense>
                    </Show>

                    {/* Main Dashboard Grid */}
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Active Crops */}
                      <Show when={showSection("crops")}>
                      <Suspense
                        fallback={
                          <div class="h-80 bg-gray-100 animate-pulse rounded-lg" />
                        }
                      >
                        <ActiveCropsCard crops={data().active_crops} />
                      </Suspense>
                      </Show>

                      {/* Marketplace Listings */}
                      <Show when={showSection("listings")}>
                      <Suspense
                        fallback={
                          <div class="h-80 bg-gray-100 animate-pulse rounded-lg" />
                        }
                      >
                        <MarketplaceListingsCard
                          listings={data().active_listings}
                        />
                      </Suspense>
                      </Show>

                      {/* Upcoming Tasks */}
                      <Show when={showSection("tasks")}>
                      <Suspense
                        fallback={
                          <div class="h-80 bg-gray-100 animate-pulse rounded-lg" />
                        }
                      >
                        <UpcomingTasksCard tasks={data().upcoming_tasks} />
                      </Suspense>
                      </Show>

                      {/* Buyer Interests */}
                      <Show when={showSection("buyers")}>
                      <Suspense
                        fallback={
                          <div class="h-80 bg-gray-100 animate-pulse rounded-lg" />
                        }
                      >
                        <BuyerInterestsCard
                          interests={data().buyer_interests}
                        />
                      </Suspense>
                      </Show>
                    </div>
                  </div>
                )}
              </Show>
            </Show>
          </Show>
        </Show>
      </main>
    </div>
  );
};

export default Dashboard;
