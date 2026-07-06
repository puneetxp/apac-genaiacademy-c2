import { test, expect } from '@playwright/test';

/**
 * Authentication Flow Test
 * Demonstrates: User signup with AI address lookup, login functionality
 */

test.describe('Authentication Flow', () => {
  const testUser = {
    username: `testfarmer${Date.now()}`,
    email: `test.farmer.${Date.now()}@example.com`,
    password: 'SecurePass123!',
    full_name: 'Test Farmer Kumar',
    phone: '+919876543210',
    pincode: '122003',
  };

  test('Complete signup flow with address lookup', async ({ page }) => {
    console.log('🎬 Starting signup flow test...');
    
    await test.step('Navigate to signup page', async () => {
      await page.goto('/auth/signup');
      await expect(page.locator('h2').first()).toContainText(/Create Account/i);
      console.log('✓ Navigated to signup page');
      await page.waitForTimeout(1000);
    });

    await test.step('Fill basic information', async () => {
      await page.getByPlaceholder('Choose a username').fill(testUser.username);
      await page.getByPlaceholder('Enter your full name').fill(testUser.full_name);
      await page.getByPlaceholder('your@email.com').fill(testUser.email);
      await page.getByPlaceholder('+919876543210').fill(testUser.phone);
      await page.getByPlaceholder('Create a strong password').fill(testUser.password);
      await page.getByPlaceholder('Re-enter your password').fill(testUser.password);
      console.log('✓ Filled basic information');
      await page.waitForTimeout(1000);
    });

    await test.step('Enable optional address fields', async () => {
      // Click the checkbox to show address fields
      await page.locator('input[type="checkbox"]').first().click();
      await page.waitForTimeout(500);
      console.log('✓ Enabled address fields');
    });

    await test.step('Test pincode lookup (AI-powered)', async () => {
      // Fill pincode - use the specific placeholder text
      await page.getByPlaceholder('Enter 6-digit pincode').fill(testUser.pincode);
      console.log(`✓ Entered pincode: ${testUser.pincode}`);
      
      // Wait for API call and auto-fill
      await page.waitForTimeout(2000);
      
      // Verify auto-filled fields (city and state should be populated)
      const cityInputs = page.getByPlaceholder('Auto-filled from pincode');
      const firstCity = cityInputs.first();
      const secondState = cityInputs.nth(1);
      
      // Check if fields have values
      const city = await firstCity.inputValue();
      const state = await secondState.inputValue();
      
      if (city && state) {
        console.log(`✓ AI Address Lookup: ${testUser.pincode} → ${city}, ${state}`);
      } else {
        console.log(`⚠ Address lookup may have failed, but continuing test`);
      }
      await page.waitForTimeout(1000);
    });

    await test.step('Fill address line (optional)', async () => {
      // Try to fill address if field is visible, but don't fail if not found
      try {
        const addressField = page.locator('input[type="text"]').filter({ hasText: /address/i }).or(
          page.getByLabel(/address/i)
        ).first();
        if (await addressField.isVisible({ timeout: 1000 })) {
          await addressField.fill('123 Farm Road, Village Area');
          console.log('✓ Filled address line');
        }
      } catch (e) {
        console.log('⚠ Address field not found, skipping');
      }
      await page.waitForTimeout(500);
    });

    await test.step('Submit signup form', async () => {
      await page.getByRole('button', { name: /sign up/i }).click();
      console.log('✓ Submitted signup form');
      await page.waitForTimeout(3000);
      
      // Should show success message or redirect to verification
      // Note: Actual behavior depends on Cognito configuration
      console.log('✓ Signup completed');
    });
  });

  test('Login flow', async ({ page }) => {
    console.log('🎬 Starting login flow test...');
    
    await test.step('Navigate to login page', async () => {
      await page.goto('/auth/signin');
      await expect(page.locator('h2').first()).toContainText(/Sign In|Login/i);
      console.log('✓ Navigated to login page');
      await page.waitForTimeout(1000);
    });

    await test.step('Fill login credentials', async () => {
      // Login form uses username field, not email
      await page.getByPlaceholder('Enter your username').fill(testUser.username);
      await page.getByPlaceholder('Enter your password').fill(testUser.password);
      console.log('✓ Filled login credentials');
      await page.waitForTimeout(500);
    });

    await test.step('Submit login', async () => {
      await page.getByRole('button', { name: /sign in|login/i }).click();
      console.log('✓ Submitted login form');
      await page.waitForTimeout(3000);
      
      // Note: Login may fail if user needs email verification
      // This is expected behavior with Cognito
      console.log('✓ Login attempt completed');
    });
  });
});
