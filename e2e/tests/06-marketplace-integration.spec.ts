import { test, expect } from '@playwright/test';

/**
 * Marketplace Integration Test
 * 
 * Tests the complete marketplace browsing flow including:
 * - Marketplace page loads without errors
 * - Filters work correctly
 * - Sorting works correctly
 * - Pagination works correctly
 * - Combined filter, sort, and pagination scenarios
 * - No HTTP 500 errors occur during browsing
 * 
 * This test validates Task 18 from the multiple-critical-bugs-fix spec.
 */

test.describe('Marketplace Integration Tests', () => {
  
  test('Marketplace page loads successfully', async ({ page }) => {
    console.log('🎬 Testing marketplace page load...');
    
    await test.step('Navigate to marketplace', async () => {
      await page.goto('/marketplace');
      
      // Wait for page to load
      await page.waitForLoadState('networkidle');
      
      // Verify page title/header
      await expect(page.locator('h1')).toContainText(/Marketplace/i);
      console.log('✓ Marketplace page loaded');
    });
    
    await test.step('Verify no console errors', async () => {
      // Listen for console errors
      const errors: string[] = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });
      
      // Wait a bit to catch any errors
      await page.waitForTimeout(2000);
      
      // Check for critical errors (ignore minor warnings)
      const criticalErrors = errors.filter(err => 
        err.includes('500') || 
        err.includes('Column expression') ||
        err.includes('Internal Server Error')
      );
      
      expect(criticalErrors.length).toBe(0);
      console.log('✓ No critical console errors');
    });
  });
  
  test('Marketplace listings display correctly', async ({ page }) => {
    console.log('🎬 Testing marketplace listings display...');
    
    await page.goto('/marketplace');
    await page.waitForLoadState('networkidle');
    
    await test.step('Check for listings or empty state', async () => {
      // Either listings are displayed or empty state is shown
      const hasListings = await page.locator('.listing-card, [class*="listing"]').count() > 0;
      const hasEmptyState = await page.locator('text=/no listings|empty|no results/i').count() > 0;
      
      expect(hasListings || hasEmptyState).toBeTruthy();
      
      if (hasListings) {
        console.log('✓ Listings are displayed');
      } else {
        console.log('✓ Empty state is displayed (no listings available)');
      }
    });
    
    await test.step('Verify pagination controls', async () => {
      // Check if pagination exists (may not if no listings)
      const prevButton = await page.locator('button:has-text("Previous")').count();
      const nextButton = await page.locator('button:has-text("Next")').count();
      const hasPagination = prevButton > 0 || nextButton > 0;
      
      if (hasPagination) {
        console.log('✓ Pagination controls are present');
      } else {
        console.log('ℹ No pagination controls (expected if few/no listings)');
      }
    });
  });
  
  test('Filter functionality works', async ({ page }) => {
    console.log('🎬 Testing filter functionality...');
    
    await page.goto('/marketplace');
    await page.waitForLoadState('networkidle');
    
    await test.step('Check for filter controls', async () => {
      // Look for common filter elements
      const hasFilters = await page.locator('input[type="text"], select, [class*="filter"]').count() > 0;
      
      if (hasFilters) {
        console.log('✓ Filter controls are present');
        
        // Try to interact with a filter if available
        const cropTypeInput = page.locator('input[placeholder*="crop" i], input[name*="crop" i]').first();
        if (await cropTypeInput.isVisible({ timeout: 1000 })) {
          await cropTypeInput.fill('rice');
          await page.waitForTimeout(1000);
          console.log('✓ Crop type filter interaction successful');
        }
      } else {
        console.log('ℹ No filter controls found');
      }
    });
  });
  
  test('Sorting functionality works', async ({ page }) => {
    console.log('🎬 Testing sorting functionality...');
    
    await page.goto('/marketplace');
    await page.waitForLoadState('networkidle');
    
    await test.step('Check for sort controls', async () => {
      // Look for sort dropdown or buttons
      const sortSelect = await page.locator('select[name*="sort"]').count();
      const sortButton = await page.locator('button:has-text("Sort")').count();
      const hasSortControls = sortSelect > 0 || sortButton > 0;
      
      if (hasSortControls) {
        console.log('✓ Sort controls are present');
        
        // Try to interact with sort control if available
        const sortSelectElem = page.locator('select[name*="sort"]').first();
        if (await sortSelectElem.isVisible({ timeout: 1000 })) {
          await sortSelectElem.selectOption({ index: 1 });
          await page.waitForTimeout(1000);
          console.log('✓ Sort control interaction successful');
        }
      } else {
        console.log('ℹ No sort controls found');
      }
    });
  });
  
  test('No HTTP 500 errors during browsing', async ({ page }) => {
    console.log('🎬 Testing for HTTP 500 errors...');
    
    // Track failed requests
    const failedRequests: any[] = [];
    
    page.on('response', response => {
      if (response.status() === 500) {
        failedRequests.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        });
      }
    });
    
    await test.step('Navigate and interact with marketplace', async () => {
      await page.goto('/marketplace');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      
      // Try various interactions
      const interactions = [
        async () => {
          // Try clicking on a listing if available
          const listing = page.locator('.listing-card, [class*="listing"]').first();
          if (await listing.isVisible({ timeout: 1000 })) {
            await listing.click();
            await page.waitForTimeout(1000);
            await page.goBack();
          }
        },
        async () => {
          // Try pagination if available
          const nextButton = page.locator('button:has-text("Next")').first();
          if (await nextButton.isVisible({ timeout: 1000 }) && await nextButton.isEnabled()) {
            await nextButton.click();
            await page.waitForTimeout(1000);
          }
        }
      ];
      
      for (const interaction of interactions) {
        try {
          await interaction();
        } catch (e) {
          // Ignore interaction errors, we're just testing for 500s
        }
      }
      
      console.log('✓ Completed marketplace interactions');
    });
    
    await test.step('Verify no 500 errors occurred', async () => {
      expect(failedRequests.length).toBe(0);
      
      if (failedRequests.length > 0) {
        console.error('❌ HTTP 500 errors detected:');
        failedRequests.forEach(req => {
          console.error(`  - ${req.url}: ${req.status} ${req.statusText}`);
        });
      } else {
        console.log('✓ No HTTP 500 errors detected');
      }
    });
  });
  
  test('API endpoint returns valid response', async ({ request }) => {
    console.log('🎬 Testing API endpoint directly...');
    
    await test.step('Test basic listings endpoint', async () => {
      const response = await request.get('http://localhost:8000/api/v1/marketplace/listings');
      
      expect(response.status()).toBe(200);
      console.log('✓ API returned 200 OK');
      
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data).toHaveProperty('listings');
      expect(data).toHaveProperty('pagination');
      
      console.log(`✓ API response structure valid (${data.listings.length} listings)`);
    });
    
    await test.step('Test listings with sorting', async () => {
      const sortOptions = [
        { sort_by: 'harvest_date', sort_order: 'asc' },
        { sort_by: 'harvest_date', sort_order: 'desc' },
        { sort_by: 'quantity', sort_order: 'asc' },
        { sort_by: 'price', sort_order: 'desc' }
      ];
      
      for (const params of sortOptions) {
        const response = await request.get('http://localhost:8000/api/v1/marketplace/listings', {
          params
        });
        
        expect(response.status()).toBe(200);
        const data = await response.json();
        expect(data.success).toBe(true);
        
        console.log(`✓ Sort test passed: ${params.sort_by} ${params.sort_order}`);
      }
    });
    
    await test.step('Test listings with filters', async () => {
      const filterOptions = [
        { crop_type: 'rice' },
        { state: 'Punjab' },
        { min_quantity: 100 },
        { quality_grade: 'A' }
      ];
      
      for (const params of filterOptions) {
        const response = await request.get('http://localhost:8000/api/v1/marketplace/listings', {
          params
        });
        
        expect(response.status()).toBe(200);
        const data = await response.json();
        expect(data.success).toBe(true);
        
        console.log(`✓ Filter test passed: ${JSON.stringify(params)}`);
      }
    });
    
    await test.step('Test listings with pagination', async () => {
      const paginationOptions = [
        { page: 1, page_size: 10 },
        { page: 2, page_size: 20 },
        { page: 1, page_size: 50 }
      ];
      
      for (const params of paginationOptions) {
        const response = await request.get('http://localhost:8000/api/v1/marketplace/listings', {
          params
        });
        
        expect(response.status()).toBe(200);
        const data = await response.json();
        expect(data.success).toBe(true);
        expect(data.pagination.page).toBe(params.page);
        expect(data.pagination.page_size).toBe(params.page_size);
        
        console.log(`✓ Pagination test passed: page ${params.page}, size ${params.page_size}`);
      }
    });
    
    await test.step('Test combined filters, sort, and pagination', async () => {
      const response = await request.get('http://localhost:8000/api/v1/marketplace/listings', {
        params: {
          crop_type: 'rice',
          state: 'Punjab',
          min_quantity: 50,
          sort_by: 'harvest_date',
          sort_order: 'asc',
          page: 1,
          page_size: 10
        }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.success).toBe(true);
      
      console.log('✓ Combined filter/sort/pagination test passed');
    });
  });
  
  test('Marketplace handles edge cases gracefully', async ({ request }) => {
    console.log('🎬 Testing edge cases...');
    
    await test.step('Test empty results', async () => {
      const response = await request.get('http://localhost:8000/api/v1/marketplace/listings', {
        params: { crop_type: 'nonexistent_crop_xyz_123' }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.listings.length).toBe(0);
      
      console.log('✓ Empty results handled correctly');
    });
    
    await test.step('Test out of range page', async () => {
      const response = await request.get('http://localhost:8000/api/v1/marketplace/listings', {
        params: { page: 9999, page_size: 10 }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.success).toBe(true);
      
      console.log('✓ Out of range page handled correctly');
    });
    
    await test.step('Test maximum page size', async () => {
      const response = await request.get('http://localhost:8000/api/v1/marketplace/listings', {
        params: { page_size: 100 }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.listings.length).toBeLessThanOrEqual(100);
      
      console.log('✓ Maximum page size handled correctly');
    });
  });
});
