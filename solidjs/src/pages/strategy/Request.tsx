/**
 * Strategy Request Page
 * Request annual crop strategy generation for a farm
 */

import { Component, createSignal, Show, onMount, lazy, Suspense } from 'solid-js';
import { useNavigate, useSearchParams } from '@solidjs/router';
import { generateStrategy, currentStrategy, isLoading, error } from '../../stores/strategy.store';
import { loadFarm, currentFarm } from '../../stores/farm.store';
import { user } from '../../stores/auth.store';
import { QuotaStatus } from '../../components/quota/QuotaStatus';
import { QuotaWarning } from '../../components/quota/QuotaWarning';
import { QuotaExceededNotification } from '../../components/quota/QuotaExceededNotification';
import { AIQuotaService, QuotaStatus as QuotaStatusType } from '../../services/ai-quota.service';

// Lazy load heavy strategy components
const StrategyRequestForm = lazy(() => import('../../components/strategy/StrategyRequestForm'));
const StrategyResults = lazy(() => import('../../components/strategy/StrategyResults'));

const StrategyRequestPage: Component = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [showResults, setShowResults] = createSignal(false);
  const [farmLoading, setFarmLoading] = createSignal(true);
  const [quotaStatus, setQuotaStatus] = createSignal<QuotaStatusType | null>(null);
  const [showWarning, setShowWarning] = createSignal(true);
  const [showExceededNotification, setShowExceededNotification] = createSignal(true);

  onMount(async () => {
    const farmId = searchParams.farmId as string;
    
    if (!farmId) {
      navigate('/dashboard');
      return;
    }

    try {
      await loadFarm(parseInt(farmId));
      // Load quota status
      const currentUser = user();
      if (currentUser?.id) {
        const status = await AIQuotaService.getQuotaStatus(currentUser.id);
        setQuotaStatus(status);
      }

      // Handle auto-generation if requested
      if (searchParams.autoGen === 'true') {
        const preferredCrop = searchParams.preferredCrop as string | undefined;
        await handleGenerateStrategy(undefined, undefined, preferredCrop);
      }
    } catch (err) {
      console.error('Failed to load farm or handle auto-gen:', err);
      // Don't navigate away if it's just an auto-gen error, keep the farm loaded
    } finally {
      setFarmLoading(false);
    }
  });

  const handleGenerateStrategy = async (
    previousCrops?: string,
    budgetPerAcre?: number,
    preferredCrop?: string,
    customMessage?: string
  ) => {
    const farmId = searchParams.farmId as string;
    
    if (!farmId) return;

    try {
      await generateStrategy(parseInt(farmId), previousCrops, budgetPerAcre, preferredCrop, customMessage);
      setShowResults(true);
    } catch (err) {
      console.error('Failed to generate strategy:', err);
    }
  };

  const handleSaveStrategy = () => {
    // Navigate to results page with save option
    const farmId = searchParams.farmId as string;
    navigate(`/strategy/results?farmId=${farmId}`);
  };

  const handleBack = () => {
    setShowResults(false);
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  return (
    <div class="min-h-screen bg-gray-50">
      {/* Header */}
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Annual Crop Strategy</h1>
          <button
            onClick={() => navigate('/dashboard')}
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Show when={farmLoading()}>
          <div class="text-center py-12">
            <p class="text-gray-600">Loading farm details...</p>
          </div>
        </Show>

        <Show when={!farmLoading() && !currentFarm()}>
          <div class="bg-white rounded-lg shadow-md p-6 text-center">
            <p class="text-gray-600">Farm not found</p>
          </div>
        </Show>

        <Show when={!farmLoading() && currentFarm()}>
          {/* Quota Notifications */}
          <Show when={quotaStatus()}>
            {(status) => (
              <>
                <Show when={showExceededNotification()}>
                  <QuotaExceededNotification
                    quotaExceeded={status().quota_exceeded}
                    nextResetTime={status().next_reset}
                    onDismiss={() => setShowExceededNotification(false)}
                  />
                </Show>
                <Show when={showWarning()}>
                  <QuotaWarning
                    remainingQuota={status().remaining_quota}
                    quotaLimit={status().quota_limit}
                    onDismiss={() => setShowWarning(false)}
                  />
                </Show>
              </>
            )}
          </Show>

          {/* Quota Status Card */}
          <div class="mb-6">
            <QuotaStatus userId={1} showDetails={true} />
          </div>

          <Show when={error()}>
            <div class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
              {error()}
            </div>
          </Show>

          <Show when={!showResults()}>
            <Suspense fallback={<div class="bg-white rounded-lg shadow-md p-6 animate-pulse h-96" />}>
              <StrategyRequestForm
                farmId={currentFarm()!.id}
                farmName={currentFarm()!.name}
                onSubmit={handleGenerateStrategy}
                onCancel={handleCancel}
                isLoading={isLoading()}
              />
            </Suspense>
          </Show>

          <Show when={showResults() && currentStrategy()}>
            <Suspense fallback={<div class="bg-white rounded-lg shadow-md p-6 animate-pulse h-96" />}>
              <StrategyResults
                strategy={currentStrategy()!}
                onSave={handleSaveStrategy}
                onBack={handleBack}
              />
            </Suspense>
          </Show>
        </Show>
      </main>
    </div>
  );
};

export default StrategyRequestPage;
