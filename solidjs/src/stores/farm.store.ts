/**
 * Farm Store
 * Global state management for farms
 */

import { createSignal } from 'solid-js';
import { FarmService, type Farm, type FarmPlot } from '../services/farm.service';

// Global state
const [farms, setFarms] = createSignal<Farm[]>([]);
const [currentFarm, setCurrentFarm] = createSignal<Farm | null>(null);
const [farmPlots, setFarmPlots] = createSignal<FarmPlot[]>([]);
const [isLoading, setIsLoading] = createSignal(false);
const [error, setError] = createSignal<string | null>(null);

/**
 * Load all farms for current user
 */
export async function loadFarms(): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const data = await FarmService.getFarms();
    setFarms(data);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to load farms');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Load a specific farm
 */
export async function loadFarm(id: number): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const farm = await FarmService.getFarm(id);
    setCurrentFarm(farm);
    
    // Also load plots for this farm
    await loadFarmPlots(id);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to load farm');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Create a new farm
 */
export async function createFarm(data: any): Promise<Farm> {
  setIsLoading(true);
  setError(null);

  try {
    const farm = await FarmService.createFarm(data);
    setFarms([...farms(), farm]);
    setCurrentFarm(farm);
    return farm;
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to create farm');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Update a farm
 */
export async function updateFarm(id: number, data: any): Promise<Farm> {
  setIsLoading(true);
  setError(null);

  try {
    const updatedFarm = await FarmService.updateFarm(id, data);
    
    // Update in list
    setFarms(farms().map(f => f.id === id ? updatedFarm : f));
    
    // Update current if it's the same farm
    if (currentFarm()?.id === id) {
      setCurrentFarm(updatedFarm);
    }
    
    return updatedFarm;
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to update farm');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Delete a farm
 */
export async function deleteFarm(id: number): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    await FarmService.deleteFarm(id);
    setFarms(farms().filter(f => f.id !== id));
    
    if (currentFarm()?.id === id) {
      setCurrentFarm(null);
    }
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to delete farm');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Load plots for a farm
 */
export async function loadFarmPlots(farmId: number): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const plots = await FarmService.getFarmPlots(farmId);
    setFarmPlots(plots);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to load plots');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Create a new plot
 */
export async function createPlot(data: any): Promise<FarmPlot> {
  setIsLoading(true);
  setError(null);

  try {
    const plot = await FarmService.createPlot(data);
    setFarmPlots([...farmPlots(), plot]);
    return plot;
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to create plot');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Delete a plot
 */
export async function deletePlot(farmId: number, id: number): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    await FarmService.deletePlot(farmId, id);
    setFarmPlots(farmPlots().filter(p => p.id !== id));
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to delete plot');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

// Export signals
export { farms, currentFarm, farmPlots, isLoading, error };
