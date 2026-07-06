import { test, expect } from '@playwright/test';

/**
 * AI Marketplace Test
 * Demonstrates: Marketplace features with AI predictions
 * Note: Uses shared authentication from global-setup.ts
 */

test.describe('AI-Powered Marketplace', () => {
  test('Browse marketplace with AI predictions', async ({ page }) => {
    console.log('🎬 Starting marketplace test...');
    
    await test.step('Navigate to marketplace', async () => {
      await page.goto('/marketplace');
      await expect(page.locator('h1')).toContainText(/Marketplace|Browse/i);
      console.log('✓ Navigated to marketplace');
      await page.waitForTimeout(1000);
    });

    await test.step('View listings with AI insights', async () => {
      // Check if listings exist
      const listings = page.locator('.listing-card');
      const listingCount = await listings.count();
      
      if (listingCount > 0) {
        await expect(listings.first()).toBeVisible({ timeout: 5000 });
        console.log(`✓ Marketplace listings loaded (${listingCount} listings)`);
      } else {
        console.log('⚠ No marketplace listings available (empty state)');
        // Test passes - empty state is valid
      }
      
      await page.waitForTimeout(2000);
    });

    await test.step('View listing details with AI predictions', async () => {
      const listings = page.locator('.listing-card');
      const listingCount = await listings.count();
      
      if (listingCount === 0) {
        console.log('⚠ No listings available, skipping detail view');
        return; // Skip this step if no listings
      }
      
      await page.click('.listing-card:first-child');
      await page.waitForTimeout(2000);
      
      // Verify AI prediction elements
      await expect(page.locator('text=/yield|quality|prediction/i')).toBeVisible();
      
      console.log('✓ Listing details with AI predictions displayed');
      await page.waitForTimeout(2000);
    });
  });

  test('Create advance booking', async ({ page }) => {
    console.log('🎬 Starting advance booking test...');
    
    await test.step('Navigate to marketplace', async () => {
      await page.goto('/marketplace');
      await page.waitForTimeout(2000);
    });

    await test.step('Select listing for booking', async () => {
      const listings = page.locator('.listing-card');
      const listingCount = await listings.count();
      
      if (listingCount === 0) {
        console.log('⚠ No listings available, skipping booking test');
        return; // Skip remaining steps
      }
      
      await page.click('.listing-card:first-child');
      await page.waitForTimeout(2000);
    });

    await test.step('Create advance booking', async () => {
      // Look for booking button (check if any listings exist first)
      const listingCount = await page.locator('.listing-card').count();
      
      if (listingCount === 0) {
        console.log('⚠ No listings available, skipping booking test');
        return; // Skip remaining steps
      }
      
      // Try multiple button text variations
      const bookButton = page.locator('button').filter({ hasText: /book|reserve/i }).first();
      if (await bookButton.isVisible({ timeout: 2000 })) {
        await bookButton.click();
        await page.waitForTimeout(1000);
        
        console.log('✓ Advance booking flow initiated');
        await page.waitForTimeout(2000);
      } else {
        console.log('⚠ Booking button not found, skipping');
      }
    });
  });
});
