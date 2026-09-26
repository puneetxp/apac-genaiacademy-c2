/**
 * /strategy/results?farmId=… — opens the newest saved annual strategy for a farm.
 * Request.tsx ("Save strategy") and the dashboard link here; the strategy itself is shown by
 * /crops/annual-strategy/:id, so this page only finds the right one and redirects.
 */
import { Component, createSignal, onMount, Show } from 'solid-js';
import { A, useNavigate, useSearchParams } from '@solidjs/router';
import { StrategyService } from '../../services/strategy.service';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

const StrategyResultsPage: Component = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);

  onMount(async () => {
    const farmId = Number(searchParams.farmId);
    try {
      const all = (await StrategyService.getFarmStrategies(farmId)) || [];
      const list = Array.isArray(all) ? all : [];
      const forFarm = farmId ? list.filter((s: any) => Number(s.farm_id) === farmId) : list;
      const latest = [...forFarm].sort((a: any, b: any) =>
        new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime() || Number(b.id) - Number(a.id))[0];
      if (latest) {
        navigate(`/crops/annual-strategy/${latest.id}`, { replace: true });
        return;
      }
    } catch (e: any) {
      console.warn('Could not load saved strategies:', e);
      setError('Could not load your saved strategies. Please try again.');
    }
    setLoading(false);
  });

  return (
    <div class="max-w-2xl mx-auto p-6">
      <Show when={!loading()} fallback={<LoadingSpinner />}>
        <div class="bg-white rounded-2xl shadow p-8 text-center">
          <h1 class="text-2xl font-bold text-gray-900 mb-2">Strategy results</h1>
          <p class="text-gray-600 mb-6">
            {error() || 'No saved strategy for this farm yet. Generate one to see it here.'}
          </p>
          <A
            href={searchParams.farmId ? `/strategy/request?farmId=${searchParams.farmId}` : '/strategy/select-farm'}
            class="inline-block px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700"
          >
            Generate a strategy
          </A>
        </div>
      </Show>
    </div>
  );
};

export default StrategyResultsPage;
