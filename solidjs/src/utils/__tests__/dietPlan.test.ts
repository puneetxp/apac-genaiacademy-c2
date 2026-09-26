import { describe, it, expect } from 'vitest';
import { calculateDietPlan } from '../dietPlan';

describe('calculateDietPlan', () => {
    it('cow: 1.5 kg maintenance + 1 kg per 2.5 L milk', () => {
        const plan = calculateDietPlan({ species: 'cow', weightKg: 400, milkLitresPerDay: 10, pregnantLastTrimester: false });
        expect(plan.concentrateKg).toBe(5.5);
        expect(plan.saltG).toBe(30);
        expect(plan.greenFodderKg).toBeGreaterThan(plan.dryFodderKg);
    });

    it('buffalo: 2 kg maintenance + 1 kg per 2 L milk, +1.5 kg when pregnant', () => {
        const plan = calculateDietPlan({ species: 'buffalo', weightKg: 450, milkLitresPerDay: 8, pregnantLastTrimester: true });
        expect(plan.concentrateKg).toBe(7.5);
        expect(plan.tips.some((t) => t.includes('गर्भ'))).toBe(true);
    });

    it('goat: 250 g + 400 g per litre', () => {
        const plan = calculateDietPlan({ species: 'goat', weightKg: 35, milkLitresPerDay: 1, pregnantLastTrimester: false });
        expect(plan.concentrateKg).toBe(0.7);
        expect(plan.saltG).toBe(10);
    });

    it('never returns negative fodder for bad input', () => {
        const plan = calculateDietPlan({ species: 'cow', weightKg: -5, milkLitresPerDay: NaN, pregnantLastTrimester: false });
        expect(plan.greenFodderKg).toBe(0);
        expect(plan.dryFodderKg).toBe(0);
        expect(plan.concentrateKg).toBe(1.5);
    });
});
