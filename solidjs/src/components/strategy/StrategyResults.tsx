/**
 * Strategy Results Component - Premium Edition
 * Display generated annual crop strategy with "WOW" effect
 */

import { Component, Show, For, createMemo } from 'solid-js';
import type { AnnualStrategy } from '../../services/strategy.service';
import SeasonalRecommendations from './SeasonalRecommendations';
import ImplementationTimeline from './ImplementationTimeline';
import { IoCash, IoAnalytics, IoAlertCircle, IoTrendingUp, IoLeaf, IoArrowBack, IoSave } from 'solid-icons/io';

interface StrategyResultsProps {
  strategy: AnnualStrategy;
  onSave?: () => void;
  onBack?: () => void;
  isSaving?: boolean;
}

const StrategyResults: Component<StrategyResultsProps> = (props) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const MONTH_ORDER = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const upcomingTimeline = createMemo(() => {
    return props.strategy.monthly_action_plan;
  });

  return (
    <div class="space-y-12 pb-20 overflow-x-hidden">
      {/* Premium Hero Header */}
      <div class="relative bg-gradient-to-br from-green-700 via-green-800 to-indigo-900 rounded-[3rem] p-10 md:p-16 text-white shadow-2xl overflow-hidden group">
        <div class="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
        <div class="absolute bottom-0 left-0 w-64 h-64 bg-blue-400/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>
        
        <div class="relative z-10">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
            <div class="space-y-4">
              <div class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md px-4 py-1.5 rounded-full border border-white/20 text-sm font-bold tracking-widest uppercase">
                <span class="relative flex h-2 w-2">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                Optimized Strategy 2026/27
              </div>
              <h1 class="text-4xl md:text-6xl font-black tracking-tight leading-tight">
                {props.strategy.farm_name}
              </h1>
              <p class="text-xl text-green-100/80 font-medium flex items-center gap-2">
                <IoLeaf class="text-green-400" /> {props.strategy.location}
              </p>
            </div>

            <div class="flex flex-wrap gap-4">
              <Show when={props.onBack}>
                <button
                  onClick={props.onBack}
                  class="flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 text-white font-bold rounded-2xl transition-all active:scale-95 no-underline"
                >
                  <IoArrowBack /> Edit Request
                </button>
              </Show>
              <button
                type="button"
                disabled
                class="flex items-center gap-2 px-8 py-4 bg-white/40 text-gray-400 font-black rounded-2xl shadow-inner cursor-not-allowed"
              >
                <IoSave /> Lock Strategy (Coming Soon)
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 lg:grid-cols-4 gap-6 mt-16 pt-16 border-t border-white/10">
            <div class="space-y-2">
              <div class="flex items-center gap-2 text-green-200 text-sm font-bold uppercase tracking-wider">
                <IoCash /> Annual Profit
              </div>
              <div class="text-3xl md:text-4xl font-black">
                {formatCurrency(props.strategy.annual_summary.total_expected_profit_per_acre)}
              </div>
              <div class="text-xs text-green-300">Expected net per acre</div>
            </div>

            <div class="space-y-2">
              <div class="flex items-center gap-2 text-blue-200 text-sm font-bold uppercase tracking-wider">
                <IoTrendingUp /> Potential ROI
              </div>
              <div class="text-3xl md:text-4xl font-black">
                {props.strategy.annual_summary.roi_percentage.toFixed(0)}%
              </div>
              <div class="text-xs text-blue-300">Strategic return</div>
            </div>

            <div class="space-y-2">
              <div class="flex items-center gap-2 text-purple-200 text-sm font-bold uppercase tracking-wider">
                <IoAnalytics /> Sustainability
              </div>
              <div class="text-3xl md:text-4xl font-black">
                {(props.strategy.annual_summary.sustainability_score * 100).toFixed(0)}/100
              </div>
              <div class="text-xs text-purple-300">Soil health focus</div>
            </div>

            <div class="space-y-2">
              <div class="flex items-center gap-2 text-orange-200 text-sm font-bold uppercase tracking-wider">
                <IoAlertCircle /> Risk Level
              </div>
              <div class="text-3xl md:text-4xl font-black capitalize">
                {props.strategy.annual_summary.risk_level}
              </div>
              <div class="text-xs text-orange-300">Market & Climate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div class="grid grid-cols-1 xl:grid-cols-12 gap-12">
        <div class="xl:col-span-8 space-y-12">
          {/* Seasonal View */}
          <SeasonalRecommendations
            kharif={props.strategy.kharif}
            rabi={props.strategy.rabi}
            zaid={props.strategy.zaid}
          />
          
          {/* Timeline View */}
          <Show when={props.strategy.monthly_action_plan.length > 0}>
            <ImplementationTimeline
              monthlyActions={upcomingTimeline()}
            />
          </Show>
        </div>

        <aside class="xl:col-span-4 space-y-8">
          {/* Alternative Routes Card */}
          <Show when={props.strategy.alternative_options.length > 0}>
            <div class="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 shadow-2xl border border-white/50 sticky top-8">
              <h3 class="text-2xl font-black text-gray-900 mb-8 flex items-center gap-3">
                <span class="p-2 bg-orange-100 text-orange-600 rounded-xl"><IoAnalytics /></span>
                Smart Alternatives
              </h3>
              
              <div class="space-y-6">
                <For each={props.strategy.alternative_options}>
                  {(option) => (
                    <div class="group relative bg-white rounded-3xl p-6 border border-gray-100 shadow-sm transition-all hover:shadow-xl hover:-translate-y-1">
                      <div class="flex justify-between items-start mb-4">
                        <div class="space-y-1">
                          <span class="text-[10px] font-black uppercase tracking-widest text-orange-500 py-1 px-2 bg-orange-50 rounded-lg">
                            {option.season}
                          </span>
                          <h4 class="text-xl font-bold text-gray-800 pt-1">{option.crop}</h4>
                        </div>
                        <div class="text-right">
                          <div class={`text-sm font-black ${option.profit_difference >= 0 ? 'text-green-600' : 'text-rose-500'}`}>
                            {option.profit_difference >= 0 ? '+' : ''}{formatCurrency(option.profit_difference)}
                          </div>
                          <div class="text-[10px] text-gray-400 font-bold uppercase">vs Primary</div>
                        </div>
                      </div>
                      <p class="text-sm text-gray-500 leading-relaxed font-medium">
                        {option.risk_comparison}
                      </p>
                      
                      <div class="mt-6 pt-4 border-t border-gray-50 flex justify-between items-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <span class="text-xs font-bold text-gray-400 lowercase">Switch route?</span>
                        <button class="text-xs font-black text-green-600 hover:underline">Select Option →</button>
                      </div>
                    </div>
                  )}
                </For>
              </div>

              <div class="mt-8 p-6 bg-indigo-50 rounded-3xl border border-indigo-100">
                <p class="text-xs font-bold text-indigo-900 leading-relaxed">
                  💡 Pro-tip: Strategies can be updated mid-season if market conditions shift significantly.
                </p>
              </div>
            </div>
          </Show>
        </aside>
      </div>

      {/* Footer Timestamp */}
      <div class="flex flex-col items-center gap-2 pt-12 opacity-40">
        <div class="w-12 h-1 bg-gray-200 rounded-full"></div>
        <div class="text-xs font-black uppercase tracking-widest text-gray-500">
          Generated via CropSense AI • {new Date(props.strategy.generated_at).toLocaleString('en-IN')}
        </div>
      </div>
    </div>
  );
};

export default StrategyResults;
