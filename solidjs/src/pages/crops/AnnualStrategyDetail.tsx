/**
 * Annual Strategy Detail Page
 * Displays a saved annual crop strategy fetched by ID from the URL
 */

import { Component, createSignal, onMount, Show } from 'solid-js';
import { useParams, useNavigate } from '@solidjs/router';
import { StrategyService } from '../../services/strategy.service';
import type { AnnualStrategy } from '../../services/strategy.service';
import StrategyResults from '../../components/strategy/StrategyResults';
import { IoArrowBack, IoAlertCircle } from 'solid-icons/io';

const AnnualStrategyDetail: Component = () => {
  const params = useParams();
  const navigate = useNavigate();

  const [strategy, setStrategy] = createSignal<AnnualStrategy | null>(null);
  const [loading, setLoading] = createSignal(true);
  const [errorMsg, setErrorMsg] = createSignal<string | null>(null);

  onMount(async () => {
    const id = params.id;
    if (!id) {
      navigate('/dashboard');
      return;
    }

    try {
      // The GET /annual-strategy/{id} endpoint returns AnnualStrategyResponse
      // which has the same shape as AnnualStrategy
      const data = await StrategyService.getStrategy(id) as unknown as AnnualStrategy;
      setStrategy(data);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to load strategy';
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  });

  return (
    <div class="min-h-screen bg-gradient-to-br from-slate-950 via-green-950 to-slate-900 px-4 py-8">
      {/* Loading */}
      <Show when={loading()}>
        <div class="flex flex-col items-center justify-center min-h-[60vh] gap-6">
          <div class="w-16 h-16 border-4 border-green-400/30 border-t-green-400 rounded-full animate-spin" />
          <p class="text-green-300 text-lg font-medium animate-pulse">Loading strategy…</p>
        </div>
      </Show>

      {/* Error */}
      <Show when={!loading() && errorMsg()}>
        <div class="max-w-lg mx-auto mt-24 bg-red-500/10 border border-red-500/30 rounded-3xl p-10 text-center">
          <IoAlertCircle class="text-red-400 text-5xl mx-auto mb-4" />
          <h2 class="text-white text-2xl font-bold mb-2">Strategy Not Found</h2>
          <p class="text-red-300 mb-6">{errorMsg()}</p>
          <button
            onClick={() => navigate('/dashboard')}
            class="inline-flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 text-white font-bold rounded-2xl transition-all"
          >
            <IoArrowBack /> Go to Dashboard
          </button>
        </div>
      </Show>

      {/* Strategy Results */}
      <Show when={!loading() && strategy()}>
        <div class="max-w-6xl mx-auto">
          {/* Back button */}
          <button
            onClick={() => navigate(-1 as any)}
            class="mb-6 flex items-center gap-2 text-green-300 hover:text-white transition-colors font-medium"
          >
            <IoArrowBack /> Back
          </button>

          <StrategyResults
            strategy={strategy()!}
            onBack={() => navigate(-1 as any)}
          />
        </div>
      </Show>
    </div>
  );
};

export default AnnualStrategyDetail;
