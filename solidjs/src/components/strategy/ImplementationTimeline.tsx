/**
 * Implementation Timeline Component
 * Display month-by-month action plan with premium glassmorphism UI
 */

import { Component, For } from 'solid-js';
import type { MonthlyAction } from '../../services/strategy.service';
import { IoCalendar, IoLeaf, IoWater, IoFlask, IoCut, IoCheckmarkCircle } from 'solid-icons/io';

interface ImplementationTimelineProps {
  monthlyActions: MonthlyAction[];
}

const ImplementationTimeline: Component<ImplementationTimelineProps> = (props) => {
  const getActionIcon = (action: string) => {
    const text = action.toLowerCase();
    if (text.includes('sow') || text.includes('plant')) return <IoLeaf class="text-green-500" />;
    if (text.includes('water') || text.includes('irrigat')) return <IoWater class="text-blue-500" />;
    if (text.includes('fertil') || text.includes('manure') || text.includes('nutrient')) return <IoFlask class="text-purple-500" />;
    if (text.includes('weed') || text.includes('pest') || text.includes('protect')) return <IoFlask class="text-orange-500" />;
    if (text.includes('harvest') || text.includes('pick') || text.includes('collect')) return <IoCut class="text-amber-500" />;
    return <IoCheckmarkCircle class="text-gray-400" />;
  };

  const getMonthColor = (month: string): string => {
    const monthLower = month.toLowerCase();
    if (['june', 'july', 'august', 'september', 'october'].includes(monthLower)) return 'from-green-500 to-emerald-600';
    if (['november', 'december', 'january', 'february', 'march', 'april'].includes(monthLower)) return 'from-blue-500 to-indigo-600';
    return 'from-amber-400 to-orange-500';
  };

  return (
    <div class="relative py-12 px-6 overflow-hidden">
      {/* Background Orbs for Glassmorphism Effect */}
      <div class="absolute top-0 left-0 w-64 h-64 bg-green-200/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
      <div class="absolute bottom-0 right-0 w-96 h-96 bg-blue-200/20 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

      <div class="relative z-10 max-w-4xl mx-auto">
        <div class="flex items-center gap-4 mb-12">
          <div class="p-3 bg-white/50 backdrop-blur-md rounded-2xl shadow-sm border border-white/50">
            <IoCalendar size={32} class="text-gray-800" />
          </div>
          <div>
            <h3 class="text-3xl font-black text-gray-900 tracking-tight">12-Month Roadmap</h3>
            <p class="text-gray-500 font-medium">Step-by-step implementation guide for your farm</p>
          </div>
        </div>

        <div class="relative ml-4 md:ml-12 border-l-2 border-dashed border-gray-200 pl-8 md:pl-16 space-y-12">
          <For each={props.monthlyActions}>
            {(monthAction, index) => (
              <div class="relative group">
                {/* Timeline Dot */}
                <div class={`absolute -left-[41px] md:-left-[73px] top-0 w-12 h-12 rounded-2xl shadow-xl flex items-center justify-center text-white font-bold text-xs ring-4 ring-white transition-transform group-hover:scale-110 bg-gradient-to-br ${getMonthColor(monthAction.month)}`}>
                  {monthAction.month.substring(0, 3).toUpperCase()}
                </div>

                {/* Card Container */}
                <div class="bg-white/70 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white transition-all hover:bg-white/90 hover:shadow-2xl">
                  <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                    <h4 class="text-2xl font-bold text-gray-800 flex items-center gap-3">
                      {monthAction.month} 
                      <span class="text-xs font-medium px-3 py-1 bg-gray-100 rounded-full text-gray-500 uppercase tracking-widest whitespace-nowrap">
                        Phase {index() + 1}
                      </span>
                    </h4>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <For each={monthAction.actions}>
                      {(action) => (
                        <div class="flex items-start gap-3 p-4 bg-white/50 rounded-2xl border border-white/50 shadow-sm transition-all hover:shadow-md hover:border-blue-100 group/item">
                          <div class="flex-shrink-0 p-2 bg-white rounded-xl shadow-sm group-hover/item:scale-110 transition-transform">
                            {getActionIcon(action)}
                          </div>
                          <span class="text-gray-700 font-medium leading-relaxed pt-1">{action}</span>
                        </div>
                      )}
                    </For>
                  </div>
                </div>
              </div>
            )}
          </For>
        </div>
      </div>
    </div>
  );
};

export default ImplementationTimeline;
