import { Component, createResource, Show, For, createSignal, onMount, onCleanup } from 'solid-js';
import { useParams, useNavigate, A } from '@solidjs/router';
import { DashboardService } from '../../services/dashboard.service';
import { IoArrowBack, IoTrendingUp, IoFlask, IoCalendar, IoStatsChart, IoCheckmarkCircle, IoCash, IoAdd, IoClose, IoLeaf, IoTrash } from 'solid-icons/io';

const FarmAnalyticsPage: Component = () => {
  const params = useParams();
  const navigate = useNavigate();
  const farmId = () => parseInt(params.id || '0');

  const [analytics, { refetch }] = createResource(farmId, DashboardService.getFarmAnalytics);
  const [planting, setPlanting] = createSignal<string | null>(null);
  const [toastMessage, setToastMessage] = createSignal<string | null>(null);
  const [showSuccess, setShowSuccess] = createSignal<string | null>(null);

  // Expense Modal State
  const [showExpenseModal, setShowExpenseModal] = createSignal<string | null>(null); // cropId
  const [expenseData, setExpenseData] = createSignal({
    category: 'Labor',
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0]
  });
  const [isSubmitting, setIsSubmitting] = createSignal(false);
  const [deletingCropId, setDeletingCropId] = createSignal<string | null>(null);

  const triggerReload = () => {
    if (!analytics.loading) {
      refetch();
    }
  };

  onMount(() => {
    triggerReload();
    if (typeof window !== 'undefined') {
      window.addEventListener('focus', triggerReload);
    }
  });

  onCleanup(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('focus', triggerReload);
    }
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleAddExpense = async (e: Event) => {
    e.preventDefault();
    const cropId = showExpenseModal();
    if (!cropId) return;

    setIsSubmitting(true);
    try {
      await DashboardService.addCropExpense(cropId, {
        category: expenseData().category,
        amount: parseFloat(expenseData().amount),
        description: expenseData().description,
        expense_date: expenseData().date
      });

      setShowExpenseModal(null);
      setExpenseData({
        category: 'Labor',
        amount: '',
        description: '',
        date: new Date().toISOString().split('T')[0]
      });

      setToastMessage('Expense added successfully!');
      setTimeout(() => setToastMessage(null), 3000);
      refetch();
    } catch (error) {
      console.error("Failed to add expense:", error);
      alert("Failed to add expense. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteCrop = async (cropId: string | number, cropName: string) => {
    if (!window.confirm(`Delete ${cropName}? This action cannot be undone.`)) {
      return;
    }

    setDeletingCropId(String(cropId));
    try {
      await DashboardService.deleteCrop(cropId);
      setToastMessage(`${cropName} deleted successfully!`);
      setTimeout(() => setToastMessage(null), 3000);
      refetch();
    } catch (error) {
      console.error('Failed to delete crop:', error);
      alert('Failed to delete crop. Please try again.');
    } finally {
      setDeletingCropId(null);
    }
  };

  return (
    <div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 py-8 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto">
        {/* Success Notification */}
        <Show when={toastMessage()}>
          <div class="fixed top-8 left-1/2 -translate-x-1/2 z-[100] animate-bounce">
            <div class="bg-green-600 text-white px-6 py-3 rounded-full shadow-2xl flex items-center gap-2 border border-green-500/50 backdrop-blur-md">
              <IoCheckmarkCircle size={20} />
              <span class="font-bold">{toastMessage()}</span>
            </div>
          </div>
        </Show>

        {/* Expense Modal */}
        <Show when={showExpenseModal()}>
          <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[90] flex items-center justify-center p-4">
            <div class="bg-white rounded-3xl w-full max-w-md overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-200">
              <div class="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white flex justify-between items-center">
                <h3 class="text-xl font-bold flex items-center gap-2">
                  <IoCash /> Add Crop Expense
                </h3>
                <button onClick={() => setShowExpenseModal(null)} class="hover:bg-white/20 p-1 rounded-full transition-colors">
                  <IoClose size={24} />
                </button>
              </div>
              <form onSubmit={handleAddExpense} class="p-6 space-y-4">
                <div class="space-y-1">
                  <label class="text-sm font-semibold text-gray-700">Category</label>
                  <select
                    value={expenseData().category}
                    onInput={(e) => setExpenseData({ ...expenseData(), category: e.currentTarget.value })}
                    class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                  >
                    <For each={['Seeds', 'Labor', 'Fertilizer', 'Pesticide', 'Equipment', 'Other']}>
                      {(cat) => <option value={cat}>{cat}</option>}
                    </For>
                  </select>
                </div>
                <div class="space-y-1">
                  <label class="text-sm font-semibold text-gray-700">Amount (₹)</label>
                  <input
                    type="number"
                    value={expenseData().amount}
                    onInput={(e) => setExpenseData({ ...expenseData(), amount: e.currentTarget.value })}
                    placeholder="Enter amount"
                    class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                  />
                </div>
                <div class="space-y-1">
                  <label class="text-sm font-semibold text-gray-700">Date</label>
                  <input
                    type="date"
                    value={expenseData().date}
                    onInput={(e) => setExpenseData({ ...expenseData(), date: e.currentTarget.value })}
                    class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                  />
                </div>
                <div class="space-y-1">
                  <label class="text-sm font-semibold text-gray-700">Description (Optional)</label>
                  <textarea
                    value={expenseData().description}
                    onInput={(e) => setExpenseData({ ...expenseData(), description: e.currentTarget.value })}
                    placeholder="E.g. Purchased high-yield seeds"
                    class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none h-24 resize-none"
                  ></textarea>
                </div>
                <button
                  type="submit"
                  disabled={isSubmitting()}
                  class="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl font-bold shadow-lg hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                >
                  {isSubmitting() ? 'Saving...' : 'Save Expense'}
                </button>
              </form>
            </div>
          </div>
        </Show>

        {/* Header */}
        <div class="flex items-center justify-between mb-8">
          <div class="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              class="p-2 bg-white rounded-full shadow hover:shadow-md transition-shadow text-gray-600"
            >
              <IoArrowBack size={24} />
            </button>
            <Show when={!analytics.loading} fallback={<div class="h-8 w-48 bg-gray-200 animate-pulse rounded"></div>}>
              <h1 class="text-3xl font-bold text-gray-900">{analytics()?.farm_name} Analytics</h1>
            </Show>
          </div>
          <div class="text-sm text-gray-500 bg-white/50 backdrop-blur-md px-4 py-2 rounded-full border border-white/50">
            Real-time Insights
          </div>
        </div>

        <Show when={!analytics.loading} fallback={<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(() => <div class="h-64 bg-white/50 animate-pulse rounded-2xl border border-white"></div>)}
        </div>}>
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Stats */}
            <div class="lg:col-span-2 space-y-8">
              {/* Farm Summary Cards */}
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white/80 backdrop-blur-xl rounded-3xl p-6 shadow-lg border border-white/50 flex flex-col justify-center">
                  <span class="text-[10px] text-gray-400 uppercase font-bold tracking-widest mb-1">Total Farm Area</span>
                  <div class="flex items-baseline gap-2">
                    <span class="text-2xl font-black text-gray-900">{analytics()?.farm_total_area || 0}</span>
                    <span class="text-sm font-medium text-gray-500">Acres</span>
                  </div>
                </div>
                <div class="bg-white/80 backdrop-blur-xl rounded-3xl p-6 shadow-lg border border-white/50 flex flex-col justify-center">
                  <span class="text-[10px] text-gray-400 uppercase font-bold tracking-widest mb-1">Total Plots</span>
                  <div class="flex items-baseline gap-2">
                    <span class="text-2xl font-black text-gray-900">{analytics()?.farm_plots?.length || 0}</span>
                    <span class="text-sm font-medium text-gray-500">Active</span>
                  </div>
                </div>
                <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl p-6 shadow-xl border border-white/20 flex flex-col justify-center text-white">
                  <span class="text-[10px] text-blue-100 uppercase font-bold tracking-widest mb-1">Total Projected Profit</span>
                  <div class="flex items-baseline gap-2">
                    <span class="text-2xl font-black">
                      {formatCurrency(analytics()?.active_crops?.reduce((sum: number, c: any) => sum + (c.projected_profit || 0), 0) || 0)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Active Crops Section */}
              <div class="bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white/50">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                  <span class="p-2 bg-amber-100 text-amber-600 rounded-lg"><IoLeaf /></span>
                  Active Crop Performance
                </h3>

                <Show when={analytics()?.active_crops?.length > 0} fallback={
                  <div class="text-center py-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                    <p class="text-gray-500 italic">No active crops found. Start planting to see analytics!</p>
                  </div>
                }>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <For each={analytics()?.active_crops}>
                      {(crop) => (
                        <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                          <div class="absolute top-0 right-0 px-3 py-1 bg-green-100 text-green-700 text-[10px] font-bold uppercase rounded-bl-xl">
                            {crop.status}
                          </div>

                          <div class="flex justify-between items-start mb-4">
                            <div>
                              <h4 class="font-bold text-lg text-gray-900">{crop.crop_name}</h4>
                              <p class="text-xs text-gray-500">
                                {crop.crop_variety} • {crop.plot_name}
                                <span class="ml-1 px-1.5 py-0.5 bg-gray-100 rounded text-[10px]">{crop.plot_area} Acres</span>
                                <span class="ml-1 px-1.5 py-0.5 bg-gray-100 rounded text-[10px]">{crop.soil_type}</span>
                              </p>
                            </div>
                            <div class="flex items-center gap-2">
                              <button
                                onClick={() => setShowExpenseModal(crop.id)}
                                class="p-2 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-100 transition-colors group-hover:scale-110"
                                title="Add Expense"
                              >
                                <IoAdd size={20} />
                              </button>
                              <button
                                onClick={() => handleDeleteCrop(crop.id, crop.crop_name)}
                                disabled={deletingCropId() === String(crop.id)}
                                class="p-2 bg-rose-50 text-rose-600 rounded-xl hover:bg-rose-100 transition-colors group-hover:scale-110 disabled:opacity-50 disabled:pointer-events-none"
                                title="Delete Crop"
                              >
                                {deletingCropId() === String(crop.id) ? (
                                  <span class="text-[10px] font-bold uppercase">...</span>
                                ) : (
                                  <IoTrash size={18} />
                                )}
                              </button>
                            </div>
                          </div>

                          <div class="space-y-4">
                            <div class="bg-gray-50 rounded-xl p-3">
                              <span class="text-[10px] text-gray-400 uppercase font-bold block mb-1">Expenses</span>
                              <span class="text-sm font-bold text-red-600">{formatCurrency(crop.total_expenses)}</span>
                            </div>
                            <div class="bg-gray-50 rounded-xl p-3">
                              <span class="text-[10px] text-gray-400 uppercase font-bold block mb-1">Proj. Profit</span>
                              <span class="text-sm font-bold text-green-600">{formatCurrency(crop.projected_profit)}</span>
                            </div>
                            <div class="bg-gray-50 rounded-xl p-3">
                              <span class="text-[10px] text-gray-400 uppercase font-bold block mb-1">Exp. Yield</span>
                              <span class="text-sm font-bold text-gray-700">{crop.expected_yield} <span class="text-[10px] font-normal">Qtl</span></span>
                            </div>
                            <div class="bg-gray-50 rounded-xl p-3">
                              <span class="text-[10px] text-gray-400 uppercase font-bold block mb-1">Market Price</span>
                              <span class="text-sm font-bold text-gray-700">₹{Math.round(crop.expected_profit / (crop.expected_yield || 1))}<span class="text-[10px] font-normal">/Qtl</span></span>
                            </div>
                          </div>

                          <div class="space-y-1">
                            <div class="flex justify-between text-[10px] font-bold uppercase">
                              <span class="text-gray-400">Financial Health</span>
                              <span class={crop.projected_profit > 0 ? 'text-green-600' : 'text-red-600'}>
                                {Math.round((crop.projected_profit / (crop.expected_profit || 1)) * 100)}% Margin
                              </span>
                            </div>
                            <div class="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                              <div
                                class={`h-full rounded-full transition-all duration-1000 ${crop.projected_profit > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                                style={{ width: `${Math.min(Math.max((crop.projected_profit / (crop.expected_profit || 1)) * 100, 5), 100)}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      )}
                    </For>
                  </div>
                </Show>
              </div>

              {/* Farm Plots Overview Section */}
              <div class="bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white/50">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                  <span class="p-2 bg-blue-100 text-blue-600 rounded-lg"><IoFlask /></span>
                  Farm Plots Overview
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <For each={analytics()?.farm_plots}>
                    {(plot) => (
                      <div class="bg-gray-50 rounded-2xl p-5 border border-gray-100 hover:border-blue-200 transition-colors">
                        <div class="flex justify-between items-center mb-3">
                          <span class="font-bold text-gray-900">{plot.plot_name}</span>
                          <span class="text-[10px] font-black bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full uppercase">
                            {plot.area} Acres
                          </span>
                        </div>
                        <div class="space-y-2">
                          <div class="flex justify-between text-xs">
                            <span class="text-gray-500">Soil Type</span>
                            <span class="font-medium text-gray-700">{plot.soil_type || 'N/A'}</span>
                          </div>
                          <div class="flex justify-between text-xs pt-1 border-t border-gray-100 mt-1">
                            <span class="text-gray-500 italic">Current Crop</span>
                            <span class={`${plot.current_crop ? 'text-blue-600 font-bold' : 'text-gray-400'}`}>
                              {plot.current_crop || 'Empty / Fallow'}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </For>
                </div>
              </div>

              {/* Plot Performance Chart (CSS Based) */}
              <div class="bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white/50 overflow-hidden relative">
                <div class="absolute top-0 right-0 p-8 opacity-10">
                  <IoStatsChart size={120} />
                </div>
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                  <span class="p-2 bg-green-100 text-green-600 rounded-lg"><IoStatsChart /></span>
                  Plot-level Accuracy
                </h3>
                <div class="space-y-6">
                  <For each={analytics()?.plot_performance}>
                    {(plot) => (
                      <div class="space-y-2">
                        <div class="flex justify-between text-sm font-medium">
                          <span class="text-gray-700">{plot.plot_name}</span>
                          <span class="text-green-600">{plot.yield_accuracy.toFixed(1)}% Accuracy</span>
                        </div>
                        <div class="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                          <div
                            class="h-full bg-gradient-to-r from-green-400 to-green-600 rounded-full shadow-sm shadow-green-200 transition-all duration-1000"
                            style={{ width: `${Math.min(plot.yield_accuracy, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </For>
                </div>
              </div>

              {/* Profit Trends */}
              <div class="bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white/50 overflow-hidden">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                  <span class="p-2 bg-blue-100 text-blue-600 rounded-lg"><IoTrendingUp /></span>
                  Actual Profit Trend
                </h3>
                <div class="h-64 flex items-end gap-4 px-2">
                  <Show when={analytics()?.profit_trends?.length > 0} fallback={
                    <div class="flex-1 h-full flex items-center justify-center text-gray-400 italic">
                      No profit data yet for current cycle
                    </div>
                  }>
                    <For each={analytics()?.profit_trends}>
                      {(trend) => (
                        <div class="flex-1 flex flex-col items-center group">
                          <div
                            class="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-lg relative group-hover:from-blue-600 group-hover:to-blue-500 transition-all cursor-pointer"
                            style={{ height: `${Math.max(10, (trend.profit / 50000) * 100)}%` }}
                          >
                            <div class="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                              {formatCurrency(trend.profit)}
                            </div>
                          </div>
                          <span class="text-[10px] text-gray-500 mt-2 rotate-45 origin-left">{trend.month}</span>
                        </div>
                      )}
                    </For>
                  </Show>
                </div>
              </div>
            </div>

            {/* Sidebar Cards */}
            <div class="space-y-6">
              {/* Active Strategy + Recommended Crops Card */}
              <div class="bg-gradient-to-br from-green-600 to-green-700 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden group">
                <div class="absolute -right-10 -bottom-10 opacity-20 group-hover:scale-110 transition-transform pointer-events-none">
                  <IoFlask size={180} />
                </div>

                {/* Show strategy summary banner if one exists */}
                <Show when={analytics()?.latest_strategy}>
                  <div class="mb-5 bg-white/15 rounded-2xl p-4 border border-white/20">
                    <p class="text-green-100 text-xs uppercase tracking-wider font-semibold mb-1">Active Strategy</p>
                    <p class="text-xl font-black uppercase tracking-tight">{analytics()?.latest_strategy.crops.join(' & ')}</p>
                    <p class="text-green-100 text-sm mt-1">
                      Expected: <span class="font-bold text-white">{formatCurrency(analytics()?.latest_strategy.expected_profit)}</span>/year
                    </p>
                    <button
                      onClick={() => navigate(`/crops/annual-strategy/${analytics()?.latest_strategy.id}`)}
                      class="mt-3 w-full py-2 bg-white text-green-700 rounded-xl font-bold text-sm shadow hover:bg-green-50 transition-colors"
                    >
                      View Full Strategy →
                    </button>
                  </div>
                </Show>

                <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                  <IoFlask /> Recommended Crops — {analytics()?.current_season ? `${analytics().current_season.charAt(0).toUpperCase() + analytics().current_season.slice(1)} Season` : 'Current Season'}
                </h3>

                <Show when={analytics()?.recommended_crops?.length > 0} fallback={
                  <div class="space-y-3">
                    <p class="text-green-100 italic text-sm">No crop recommendations available yet.</p>
                    <button
                      onClick={() => navigate(`/strategy/request?farmId=${analytics()?.farm_id}`)}
                      class="w-full py-3 bg-white text-green-700 rounded-2xl font-bold shadow-lg hover:bg-green-50 transition-all active:scale-95"
                    >
                      Generate Full Strategy
                    </button>
                  </div>
                }>
                  <div class="space-y-3">
                    <div class="text-sm text-green-100 font-medium">
                      Top picks for {analytics()?.recommended_crops?.[0]?.season_display || 'Current Season'}:
                    </div>
                    <For each={analytics()?.recommended_crops}>
                      {(crop: any) => {
                        // Compute harvest date from planting + days_to_harvest if not provided
                        const getHarvestDate = () => {
                          if (crop.optimal_harvest_window) return crop.optimal_harvest_window;
                          if (crop.optimal_planting_window && crop.days_to_harvest) {
                            const d = new Date(crop.optimal_planting_window);
                            d.setDate(d.getDate() + parseInt(crop.days_to_harvest));
                            return d.toISOString().split('T')[0];
                          }
                          return '';
                        };

                        const formatDate = (d: string) => {
                          if (!d) return '—';
                          try {
                            return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
                          } catch { return d; }
                        };

                        return (
                          <div class="w-full text-left bg-white/10 rounded-xl p-4 backdrop-blur-sm border border-white/20 transition-all hover:bg-white/20 group relative z-10">
                            <div class="flex justify-between items-start mb-1">
                              <div>
                                <span class="font-bold text-xl text-white">{crop.crop_name}</span>
                                <Show when={crop.variety}>
                                  <span class="ml-2 text-xs text-green-200 font-medium">{crop.variety}</span>
                                </Show>
                              </div>
                              <Show when={crop.expected_yield_per_acre}>
                                <span class="text-xs bg-green-500/80 px-2 py-1 rounded-full text-white font-bold shrink-0">{crop.expected_yield_per_acre}</span>
                              </Show>
                            </div>
                            <Show when={crop.suitability_reason}>
                              <div class="text-sm text-green-100 mb-3 leading-tight border-b border-green-400/30 pb-3">{crop.suitability_reason}</div>
                            </Show>

                            {/* Seeding & Harvest Date Rows */}
                            <div class="grid grid-cols-2 gap-2 text-xs mt-2 mb-3">
                              <div class="bg-white/10 rounded-lg p-2">
                                <span class="text-green-300 block mb-0.5 font-semibold uppercase tracking-wider text-[10px]">🌱 Sow By</span>
                                <span class="font-bold text-white">{formatDate(crop.optimal_planting_window)}</span>
                              </div>
                              <div class="bg-white/10 rounded-lg p-2">
                                <span class="text-amber-300 block mb-0.5 font-semibold uppercase tracking-wider text-[10px]">🌾 Harvest</span>
                                <span class="font-bold text-white">{formatDate(getHarvestDate())}</span>
                              </div>
                            </div>
                            <Show when={crop.days_to_harvest}>
                              <div class="text-[11px] text-green-200 mb-3">⏱ {crop.days_to_harvest} days to harvest</div>
                            </Show>

                            <div class="grid grid-cols-2 gap-3 pt-3 border-t border-white/10">
                              <button
                                onClick={() => {
                                  const pDate = crop.optimal_planting_window || new Date().toISOString().split('T')[0];
                                  const hDate = getHarvestDate();
                                  const area = analytics()?.farm_total_area || 1.0;
                                  const season = analytics()?.current_season || 'Kharif';

                                  // Parse yield per acre for pre-filling
                                  let yieldPerAcre = 0;
                                  if (crop.expected_yield_per_acre) {
                                    const match = crop.expected_yield_per_acre.match(/(\d+)(?:-(\d+))?/);
                                    if (match) {
                                      const min = parseInt(match[1]);
                                      const max = match[2] ? parseInt(match[2]) : min;
                                      yieldPerAcre = (min + max) / 2;
                                    }
                                  }

                                  // Calculate total yield for the farm area
                                  const totalYield = yieldPerAcre * area;
                                  
                                  // Calculate price per quintal from profit per acre
                                  // expected_profit_per_acre = yieldPerAcre * pricePerQuintal
                                  const priceVal = (crop.expected_profit_per_acre && yieldPerAcre > 0) 
                                    ? Math.round(crop.expected_profit_per_acre / yieldPerAcre) 
                                    : 0;

                                  navigate(`/crops/plant?farmId=${analytics().farm_id}&cropName=${encodeURIComponent(crop.crop_name)}&variety=${encodeURIComponent(crop.variety || '')}&plantingDate=${pDate}&harvestDate=${hDate}&area=${area}&season=${season}&expectedYield=${totalYield}&marketPrice=${priceVal}`);
                                }}
                                class="bg-white text-green-700 py-2 px-1 rounded-lg text-center font-bold text-xs hover:bg-green-50 transition-all shadow-lg flex items-center justify-center gap-1 active:scale-95"
                              >
                                🚀 Plant Now
                              </button>
                              <A
                                href={`/strategy/request?farmId=${analytics().farm_id}&autoGen=true&preferredCrop=${encodeURIComponent(crop.crop_name)}`}
                                class="bg-black/20 text-white border border-white/20 py-2 px-1 rounded-lg text-center font-bold text-xs hover:bg-white/10 transition-colors flex items-center justify-center gap-1 no-underline"
                              >
                                🧠 Strategy
                              </A>
                            </div>
                          </div>
                        );
                      }}
                    </For>

                    <Show when={!analytics()?.latest_strategy}>
                      <button
                        onClick={() => navigate(`/strategy/request?farmId=${analytics()?.farm_id}`)}
                        class="w-full py-3 bg-white text-green-700 rounded-2xl font-bold shadow-lg hover:bg-green-50 transition-all active:scale-95 mt-2 relative z-10"
                      >
                        Generate Full Strategy
                      </button>
                    </Show>
                  </div>
                </Show>
              </div>

              {/* Resource Management */}
              <div class="bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white/50">
                <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <IoCalendar class="text-orange-500" /> Cycle Progress
                </h3>
                <div class="relative pt-1">
                  <div class="flex mb-2 items-center justify-between">
                    <div>
                      <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-orange-600 bg-orange-200">
                        {analytics()?.current_season ? `${analytics().current_season} CYCLE` : 'CURRENT CYCLE'}
                      </span>
                    </div>
                    <div class="text-right">
                      <span class="text-xs font-semibold inline-block text-orange-600">
                        65%
                      </span>
                    </div>
                  </div>
                  <div class="overflow-hidden h-2 mb-4 text-xs flex rounded-full bg-orange-100">
                    <div style={{ width: "65%" }} class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-orange-500"></div>
                  </div>
                </div>
                <p class="text-sm text-gray-600">You are halfway through the {analytics()?.current_season || 'current'} season. Maintain crop health to maximize yields.</p>
              </div>
            </div>
          </div>
        </Show>
      </div>
    </div>
  );
};

export default FarmAnalyticsPage;
