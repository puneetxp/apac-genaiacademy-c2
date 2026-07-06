/**
 * Farm Dashboard Page
 * View and manage a specific farm
 */

import { Component, createEffect, createSignal, Show } from "solid-js";
import { useNavigate, useParams } from "@solidjs/router";
import {
  currentFarm,
  deleteFarm,
  loadFarm,
  loadFarmPlots,
} from "../../stores/farm.store";
import FarmProfileDashboard from "../../components/farm/FarmProfileDashboard";
import PlotManagement from "../../components/farm/PlotManagement";
import FarmRegistrationForm from "../../components/farm/FarmRegistrationForm";

import FarmEditForm from "../../components/farm/FarmEditForm";

const FarmDashboardPage: Component = () => {
  const params = useParams();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = createSignal(false);
  const [showPlotManagement, setShowPlotManagement] = createSignal(false);
  const [isLoading, setIsLoading] = createSignal(true);

  createEffect(async () => {
    const farmId = parseInt(params.id);
    if (farmId) {
      try {
        await loadFarm(farmId);
        await loadFarmPlots(farmId);
      } catch (err) {
        console.error("Failed to load farm:", err);
        navigate("/dashboard");
      } finally {
        setIsLoading(false);
      }
    }
  });

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleDelete = async () => {
    const farmId = parseInt(params.id);
    try {
      await deleteFarm(farmId);
      navigate("/dashboard");
    } catch (err) {
      console.error("Failed to delete farm:", err);
    }
  };

  const handleManagePlots = () => {
    setShowPlotManagement(true);
  };

  const handleGenerateStrategy = () => {
    const farmId = parseInt(params.id);
    navigate(`/strategy/request?farmId=${farmId}`);
  };

  const handleUpdateSuccess = async () => {
    setIsEditing(false);
    const farmId = parseInt(params.id);
    setIsLoading(true);
    try {
      await loadFarm(farmId);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div class="min-h-screen bg-gray-50">
      {/* Header */}
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Farm Management</h1>
          <button
            onClick={() => navigate("/dashboard")}
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Show when={isLoading()}>
          <div class="text-center py-12">
            <p class="text-gray-600">Loading farm details...</p>
          </div>
        </Show>

        <Show when={!isLoading() && currentFarm() && !isEditing()}>
          <FarmProfileDashboard
            farm={currentFarm()!}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onManagePlots={handleManagePlots}
            onGenerateStrategy={handleGenerateStrategy}
          />
        </Show>

        <Show when={isEditing() && currentFarm()}>
          <FarmEditForm
            farm={currentFarm()!}
            onSuccess={handleUpdateSuccess}
            onCancel={() => setIsEditing(false)}
          />
        </Show>

        <Show when={showPlotManagement() && currentFarm()}>
          <PlotManagement
            farmId={currentFarm()!.id}
            farmName={currentFarm()!.name}
            onClose={() => setShowPlotManagement(false)}
          />
        </Show>
      </main>
    </div>
  );
};

export default FarmDashboardPage;
