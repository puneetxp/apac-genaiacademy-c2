import { test, expect } from '@playwright/test';

/**
 * AI-Powered Crop Planning Test
 * Demonstrates: Annual crop strategy with AI recommendations
 * Note: Uses shared authentication from global-setup.ts
 */

test.describe('AI-Powered Crop Planning', () => {
  test('Create annual crop strategy with AI recommendations', async ({ page }) => {
    console.log('🎬 Starting AI crop planning test...');
    
    // First, get a farm ID from the dashboard
    await test.step('Get farm ID from dashboard', async () => {
      await page.goto('/dashboard');
      await page.waitForTimeout(1000);
      
      // Try to get farm ID from the page
      const farmCard = page.locator('[data-farm-id]').first();
      const farmIdExists = await farmCard.count() > 0;
      
      if (!farmIdExists) {
        console.log('⚠️  No farms found, skipping test');
        test.skip();
      }
    });
    
    await test.step('Navigate to crop planning', async () => {
      // Get the first farm's ID
      const farmId = await page.locator('[data-farm-id]').first().getAttribute('data-farm-id');
      await page.goto(`/strategy/request?farmId=${farmId}`);
      await expect(page.locator('h1')).toContainText('Annual Crop Strategy');
      await page.waitForTimeout(1000);
    });

    await test.step('Select farm', async () => {
      await page.selectOption('select[name="farm_id"]', { index: 1 });
      await page.waitForTimeout(500);
    });

    await test.step('Get AI crop recommendations', async () => {
      await page.click('button:has-text("Get AI Recommendations")');
      await page.waitForTimeout(3000); // Wait for AI processing
      
      // Verify recommendations appear
      await expect(page.locator('.recommendation-card')).toHaveCount(3, { timeout: 5000 });
      
      console.log('✓ AI generated crop recommendations');
      await page.waitForTimeout(2000);
    });

    await test.step('View recommendation details', async () => {
      // Click first recommendation
      await page.click('.recommendation-card:first-child');
      await page.waitForTimeout(1000);
      
      // Verify details shown
      await expect(page.locator('.recommendation-details')).toBeVisible();
      await expect(page.locator('text=Expected Yield')).toBeVisible();
      await expect(page.locator('text=Profitability Score')).toBeVisible();
      
      await page.waitForTimeout(2000);
    });

    await test.step('Add crop to plan', async () => {
      await page.fill('input[name="crop_name"]', 'Wheat');
      await page.fill('input[name="area"]', '2.5');
      await page.fill('input[name="expected_yield"]', '3500');
      await page.selectOption('select[name="season"]', 'rabi');
      await page.waitForTimeout(500);
    });

    await test.step('Set planting dates', async () => {
      await page.fill('input[name="planting_date"]', '2026-11-01');
      await page.fill('input[name="harvest_date"]', '2027-03-15');
      await page.waitForTimeout(500);
    });

    await test.step('Submit crop plan', async () => {
      await page.click('button:has-text("Add to Plan")');
      await page.waitForTimeout(2000);
      
      await expect(page.locator('text=Crop added successfully')).toBeVisible();
      await page.waitForTimeout(1000);
    });

    await test.step('View complete annual plan', async () => {
      await page.click('button:has-text("View Annual Plan")');
      await page.waitForTimeout(1000);
      
      // Verify plan summary
      await expect(page.locator('.crop-timeline')).toBeVisible();
      await expect(page.locator('.profitability-chart')).toBeVisible();
      
      console.log('✓ Annual crop plan created with AI insights');
      await page.waitForTimeout(2000);
    });
  });
});
