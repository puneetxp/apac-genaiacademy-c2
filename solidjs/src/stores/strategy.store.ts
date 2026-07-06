/**
 * Strategy Store
 * Global state management for annual crop strategies
 */

import { createSignal } from 'solid-js';
import { StrategyService, type AnnualStrategy, type SavedStrategy } from '../services/strategy.service';

// Global state
const [currentStrategy, setCurrentStrategy] = createSignal<AnnualStrategy | null>(null);
const [savedStrategies, setSavedStrategies] = createSignal<SavedStrategy[]>([]);
const [isLoading, setIsLoading] = createSignal(false);
const [error, setError] = createSignal<string | null>(null);

/**
 * Generate annual crop strategy
 */
export async function generateStrategy(
  farmId: number,
  previousCrops?: string,
  budgetPerAcre?: number,
  preferredCrop?: string,
  customMessage?: string
): Promise<AnnualStrategy> {
  setIsLoading(true);
  setError(null);

  try {
    const strategy = await StrategyService.generateStrategy({
      farm_id: farmId,
      previous_crops: previousCrops,
      budget_per_acre: budgetPerAcre,
      preferred_crop: preferredCrop,
      custom_message: customMessage
    });
    
    setCurrentStrategy(strategy);
    return strategy;
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to generate strategy';
    setError(message);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Save generated strategy
 */
export async function saveStrategy(
  farmId: number,
  strategyData: AnnualStrategy,
  notes?: string
): Promise<SavedStrategy> {
  setIsLoading(true);
  setError(null);

  try {
    const saved = await StrategyService.saveStrategy({
      farm_id: farmId,
      strategy_data: strategyData,
      notes,
    });
    
    // Add to saved strategies list
    setSavedStrategies([saved, ...savedStrategies()]);
    
    return saved;
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to save strategy';
    setError(message);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Load saved strategies for a farm
 */
export async function loadFarmStrategies(farmId: number): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const strategies = await StrategyService.getFarmStrategies(farmId);
    setSavedStrategies(strategies);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to load strategies';
    setError(message);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Load a specific strategy
 */
export async function loadStrategy(strategyId: string): Promise<SavedStrategy> {
  setIsLoading(true);
  setError(null);

  try {
    const strategy = await StrategyService.getStrategy(strategyId);
    return strategy;
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to load strategy';
    setError(message);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Update strategy status
 */
export async function updateStrategyStatus(
  strategyId: string,
  status: string
): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const updated = await StrategyService.updateStrategyStatus(strategyId, status);
    
    // Update in list
    setSavedStrategies(
      savedStrategies().map(s => s.id === strategyId ? updated : s)
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to update strategy';
    setError(message);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Clear current strategy
 */
export function clearCurrentStrategy(): void {
  setCurrentStrategy(null);
  setError(null);
}

// Export signals
export { currentStrategy, savedStrategies, isLoading, error };
