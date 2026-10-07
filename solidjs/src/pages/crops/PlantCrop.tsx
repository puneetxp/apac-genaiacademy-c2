import { Component, createSignal, For, onMount, Show } from 'solid-js';
import { useSearchParams, useNavigate, A } from '@solidjs/router';
import { IoArrowBack, IoLeaf, IoCalendar, IoResize, IoCheckmarkCircle, IoAlertCircle } from 'solid-icons/io';
import { CropService, type SupportingCropInput } from '../../services/crop.service';
import { showCropField } from '../../stores/app-config.store';
import { DashboardService } from '../../services/dashboard.service';

const PlantCropPage: Component = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = createSignal(false);
  const [success, setSuccess] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  const [formData, setFormData] = createSignal({
    farm_id: parseInt((searchParams.farmId as string) || '0'),
    crop_name: (searchParams.cropName as string) || '',
    variety: (searchParams.variety as string) || '',
    season: (searchParams.season as string) || 'Kharif',
    area: parseFloat((searchParams.area as string) || '1.0'),
    planting_date: (searchParams.plantingDate as string) || new Date().toISOString().split('T')[0],
    expected_harvest_date: (searchParams.harvestDate as string) || '',
    expected_yield: parseFloat((searchParams.expectedYield as string) || '0'),
    market_price: parseFloat((searchParams.marketPrice as string) || '0'),
  });

  // Supporting (inter/companion) crops grown alongside the main crop, e.g. Maize + Cowpea
  const [supportingCrops, setSupportingCrops] = createSignal<SupportingCropInput[]>([]);
  const addSupportingCrop = () =>
    setSupportingCrops([...supportingCrops(), { crop_name: '', variety: '', area: undefined }]);
  const updateSupportingCrop = (index: number, patch: Partial<SupportingCropInput>) =>
    setSupportingCrops(supportingCrops().map((c, i) => (i === index ? { ...c, ...patch } : c)));
  const removeSupportingCrop = (index: number) =>
    setSupportingCrops(supportingCrops().filter((_, i) => i !== index));

  onMount(() => {
    if (!formData().expected_harvest_date) {
      const harvestDate = new Date(formData().planting_date);
      harvestDate.setMonth(harvestDate.getMonth() + 4);
      setFormData({ ...formData(), expected_harvest_date: harvestDate.toISOString().split('T')[0] });
    }
  });

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    if (showCropField('marketPrice') && formData().expected_yield > 0 && (!formData().market_price || formData().market_price <= 0)) {
      const confirmed = window.confirm('Market price is set to ₹0. Are you sure you want to continue?');
      if (!confirmed) {
        return;
      }
    }
    setLoading(true);
    setError(null);
    
    try {
      // Fields switched off in Configuration are left out; the API fills sensible defaults
      await CropService.quickPlant({
        farm_id: formData().farm_id,
        plot_id: null,
        crop_name: formData().crop_name,
        variety: showCropField('variety') ? formData().variety : undefined,
        season: formData().season,
        area: formData().area,
        planting_date: formData().planting_date,
        expected_harvest_date: showCropField('harvestDate') ? formData().expected_harvest_date || undefined : undefined,
        expected_yield: showCropField('yield') ? formData().expected_yield || undefined : undefined,
        market_price: showCropField('marketPrice') ? formData().market_price || undefined : undefined,
        supporting_crops: showCropField('supportingCrops')
          ? supportingCrops()
              .filter((c) => c.crop_name.trim())
              .map((c) => ({ crop_name: c.crop_name.trim(), variety: c.variety || undefined, area: c.area || undefined }))
          : [],
      });
      setSuccess(true);
      setTimeout(() => navigate(`/analytics/farm/${formData().farm_id}`), 2000);
    } catch (err: any) {
      setError(err.message || "Failed to plant crop. Please check your data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-2xl mx-auto">
        <A 
          href={`/analytics/farm/${formData().farm_id}`}
          class="inline-flex items-center gap-2 text-green-700 font-bold mb-8 hover:translate-x-1 transition-transform no-underline"
        >
          <IoArrowBack /> Back to Analytics
        </A>

        <div class="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 md:p-12 shadow-2xl border border-white relative overflow-hidden">
          {/* Success Overlay */}
          <Show when={success()}>
            <div class="absolute inset-0 z-50 bg-white/90 backdrop-blur-md flex flex-col items-center justify-center text-center p-8 animate-in fade-in duration-500">
              <div class="w-24 h-24 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-6 animate-bounce">
                <IoCheckmarkCircle size={60} />
              </div>
              <h2 class="text-3xl font-black text-gray-900 mb-2">Planting Confirmed!</h2>
              <p class="text-gray-500 font-medium tracking-wide">Your {formData().crop_name} cycle has been started.</p>
              <p class="text-sm text-gray-400 mt-8">Redirecting you back...</p>
            </div>
          </Show>

          <div class="flex items-center gap-4 mb-10">
            <div class="p-4 bg-green-600 text-white rounded-3xl shadow-lg rotate-3">
              <IoLeaf size={32} />
            </div>
            <div>
              <h1 class="text-3xl font-black text-gray-900 leading-tight">Identify & Plant</h1>
              <p class="text-gray-500 font-medium">Review and start your new crop cycle</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} class="space-y-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-2">
                <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Crop Name</label>
                <div class="relative">
                  <input 
                    type="text" 
                    value={formData().crop_name}
                    onInput={(e) => setFormData({ ...formData(), crop_name: e.currentTarget.value })}
                    class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-5 py-4 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                    required
                  />
                  <IoLeaf class="absolute right-5 top-1/2 -translate-y-1/2 text-gray-300" />
                </div>
              </div>


              <Show when={showCropField('variety')}>
              <div class="space-y-2">
                <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Variety (Optional)</label>
                <input 
                  type="text" 
                  value={formData().variety}
                  onInput={(e) => setFormData({ ...formData(), variety: e.currentTarget.value })}
                  class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-5 py-4 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                  placeholder="e.g. Hybrid Alpha"
                />
              </div>
              </Show>

              <div class="space-y-2">
                <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Season</label>
                <select 
                  value={formData().season}
                  onChange={(e) => setFormData({ ...formData(), season: e.currentTarget.value })}
                  class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-5 py-4 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none appearance-none"
                >
                  <option value="Kharif">Kharif (Jun-Oct)</option>
                  <option value="Rabi">Rabi (Nov-Mar)</option>
                  <option value="Zaid">Zaid (Mar-Jun)</option>
                  <option value="Summer">Summer (Mar-May)</option>
                  <option value="Winter">Winter (Nov-Feb)</option>
                  <option value="Spring">Spring (Feb-Apr)</option>
                  <option value="Autumn">Autumn (Sep-Nov)</option>
                  <option value="Year-Round">Year-Round</option>
                </select>
              </div>

              <div class="space-y-2">
                <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Area (Acres)</label>
                <div class="relative">
                  <input 
                    type="number" 
                    step="0.01"
                    value={formData().area}
                    onInput={(e) => setFormData({ ...formData(), area: parseFloat(e.currentTarget.value) })}
                    class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-5 py-4 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                    required
                  />
                  <IoResize class="absolute right-5 top-1/2 -translate-y-1/2 text-gray-300" />
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Sowing Date</label>
                <div class="relative">
                  <input 
                    type="date" 
                    value={formData().planting_date}
                    onInput={(e) => setFormData({ ...formData(), planting_date: e.currentTarget.value })}
                    class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-5 py-4 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                    required
                  />
                  <IoCalendar class="absolute right-5 top-1/2 -translate-y-1/2 text-gray-300" />
                </div>
              </div>

              <Show when={showCropField('harvestDate')}>
              <div class="space-y-2">
                <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Expected Harvest</label>
                <div class="relative">
                  <input 
                    type="date" 
                    value={formData().expected_harvest_date}
                    onInput={(e) => setFormData({ ...formData(), expected_harvest_date: e.currentTarget.value })}
                    class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-5 py-4 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                  />
                  <IoCalendar class="absolute right-5 top-1/2 -translate-y-1/2 text-gray-300" />
                </div>
              </div>
              </Show>

              <Show when={showCropField('yield')}>
              <div class="space-y-2">
                <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Expected Yield (Quintals, optional)</label>
                <div class="relative">
                  <input 
                    type="number" 
                    step="0.1"
                    value={formData().expected_yield}
                    onInput={(e) => setFormData({ ...formData(), expected_yield: parseFloat(e.currentTarget.value) || 0 })}
                    class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-5 py-4 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                  />
                  <div class="absolute right-5 top-1/2 -translate-y-1/2 font-bold text-gray-400 text-xs">Qtl</div>
                </div>
              </div>
              </Show>

              <Show when={showCropField('marketPrice')}>
              <div class="space-y-2">
                <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">Market Price (₹/Quintal, optional)</label>
                <div class="relative">
                  <input 
                    type="number" 
                    step="1"
                    value={formData().market_price}
                    onInput={(e) => setFormData({ ...formData(), market_price: parseFloat(e.currentTarget.value) || 0 })}
                    class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-5 py-4 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                  />
                  <div class="absolute right-5 top-1/2 -translate-y-1/2 font-bold text-gray-400 text-xs">₹/Qtl</div>
                </div>
              </div>
              </Show>
            </div>

            <Show when={showCropField('supportingCrops')}>
              <div class="space-y-3">
                <div class="flex items-center justify-between gap-3">
                  <label class="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">
                    Supporting Crops (Optional)
                  </label>
                  <button
                    type="button"
                    onClick={addSupportingCrop}
                    class="text-sm font-bold text-green-700 hover:text-green-800 px-3 py-1 rounded-xl hover:bg-green-50"
                  >
                    + Add supporting crop
                  </button>
                </div>
                <Show when={supportingCrops().length === 0}>
                  <p class="text-sm text-gray-400 ml-1">
                    Growing an intercrop or companion crop with {formData().crop_name || 'this crop'}? For example Maize + Cowpea, Sugarcane + Onion.
                  </p>
                </Show>
                <For each={supportingCrops()}>
                  {(crop, i) => (
                    <div class="grid grid-cols-1 sm:grid-cols-[2fr_2fr_1fr_auto] gap-2 items-center">
                      <input
                        type="text"
                        placeholder="Crop name"
                        value={crop.crop_name}
                        onInput={(e) => updateSupportingCrop(i(), { crop_name: e.currentTarget.value })}
                        class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-4 py-3 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                      />
                      <input
                        type="text"
                        placeholder="Variety (optional)"
                        value={crop.variety || ''}
                        onInput={(e) => updateSupportingCrop(i(), { variety: e.currentTarget.value })}
                        class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-4 py-3 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                      />
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        placeholder={`${formData().area || ''} ac`}
                        title="Area in acres (defaults to the main crop's area)"
                        value={crop.area ?? ''}
                        onInput={(e) => updateSupportingCrop(i(), { area: parseFloat(e.currentTarget.value) || undefined })}
                        class="w-full bg-gray-50 border-2 border-gray-100 rounded-2xl px-4 py-3 font-bold text-gray-800 focus:border-green-500 focus:bg-white transition-all outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => removeSupportingCrop(i())}
                        class="text-rose-500 hover:bg-rose-50 rounded-xl px-3 py-2 font-bold"
                        aria-label="Remove supporting crop"
                      >
                        ✕
                      </button>
                    </div>
                  )}
                </For>
              </div>
            </Show>

            <A href="/settings" class="block text-center text-xs font-bold text-gray-400 hover:text-green-700 no-underline">
              ⚙️ Choose which fields this form asks for
            </A>

            <Show when={error()}>
              <div class="p-4 bg-rose-50 text-rose-600 rounded-2xl border border-rose-100 text-sm font-bold flex items-center gap-2">
                <IoAlertCircle /> {error()}
              </div>
            </Show>

            <button 
              type="submit"
              disabled={loading()}
              class="w-full bg-green-600 hover:bg-green-700 text-white font-black py-5 rounded-3xl shadow-xl shadow-green-200 transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-3 text-lg"
            >
              {loading() ? (
                <div class="w-6 h-6 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>🚀 Confirm Planting</>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PlantCropPage;
