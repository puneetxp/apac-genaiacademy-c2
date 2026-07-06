import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * SIMPLIFIED DEMO DATA SEEDING TEST
 * 
 * Creates realistic demo data using ACTUAL application routes.
 * Uses existing authenticated user from global-setup.ts
 * 
 * This test creates:
 * 1. Multiple farms via /farm/register
 * 2. Annual crop strategies via /strategy/request
 * 3. Marketplace browsing and interactions
 * 
 * Duration: ~10-15 minutes
 * Purpose: Data seeding + bug detection + error logging
 */

test.describe('Demo Data Seeding - Simplified & Working', () => {
  let testUser: any;
  let errorLog: string[] = [];
  const logFile = path.join(__dirname, '..', 'test-results', 'seed-data-errors.log');

  // Helper function to log errors
  function logError(step: string, error: any) {
    const timestamp = new Date().toISOString();
    const errorMsg = `[${timestamp}] ERROR in ${step}: ${error.message || error}\n${error.stack || ''}\n`;
    errorLog.push(errorMsg);
    console.error(`\n❌ ERROR in ${step}:`);
    console.error(error);
    
    // Write to file immediately
    try {
      fs.appendFileSync(logFile, errorMsg);
    } catch (e) {
      console.error('Failed to write to log file:', e);
    }
  }

  // Helper function to log success
  function logSuccess(step: string, details?: string) {
    const timestamp = new Date().toISOString();
    const successMsg = `[${timestamp}] SUCCESS: ${step}${details ? ' - ' + details : ''}\n`;
    console.log(`✅ ${step}${details ? ' - ' + details : ''}`);
    try {
      fs.appendFileSync(logFile, successMsg);
    } catch (e) {
      console.error('Failed to write to log file:', e);
    }
  }

  test.beforeAll(async () => {
    console.log('\n🌱 === STARTING SIMPLIFIED DEMO DATA SEEDING ===\n');
    console.log('📊 Creating realistic demo data using actual application routes\n');
    console.log('🔐 Using existing authenticated session from global-setup\n');
    
    // Initialize error log file
    const resultsDir = path.join(__dirname, '..', 'test-results');
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
    fs.writeFileSync(logFile, `=== SIMPLIFIED DEMO DATA SEEDING LOG ===\nStarted: ${new Date().toISOString()}\n\n`);
    
    // Load test user credentials
    const authDir = path.join(__dirname, '..', '.auth');
    const userFile = path.join(authDir, 'test-user.json');
    
    if (fs.existsSync(userFile)) {
      testUser = JSON.parse(fs.readFileSync(userFile, 'utf-8'));
      console.log(`✓ Loaded test user: ${testUser.username}`);
      logSuccess('Load test user', testUser.username);
    } else {
      const error = 'Test user not found. Run global-setup first.';
      logError('Load test user', new Error(error));
      throw new Error(error);
    }
  });

  test.afterAll(async () => {
    console.log('\n📊 === ERROR SUMMARY ===\n');
    if (errorLog.length === 0) {
      console.log('✅ No errors encountered during data seeding!');
      fs.appendFileSync(logFile, '\n=== COMPLETED SUCCESSFULLY - NO ERRORS ===\n');
    } else {
      console.log(`⚠️ Total errors encountered: ${errorLog.length}`);
      console.log(`📄 Full error log saved to: ${logFile}`);
      fs.appendFileSync(logFile, `\n=== COMPLETED WITH ${errorLog.length} ERRORS ===\n`);
    }
  });

  test('Seed demo data using actual application routes', async ({ page, context }) => {
    // Increase timeout for this complex seeding test
    test.setTimeout(180000);
    
    // Grant geolocation permissions
    await context.grantPermissions(['geolocation']);

    
    // Setup page error listeners
    page.on('pageerror', (error) => {
      // Ignore CSP and X-Frame-Options warnings (not critical)
      if (!error.message.includes('X-Frame-Options') && 
          !error.message.includes('Content Security Policy')) {
        logError('Page JavaScript Error', error);
      }
    });
    
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        // Ignore CSP warnings
        if (!msg.text().includes('X-Frame-Options') && 
            !msg.text().includes('Content Security Policy')) {
          logError('Console Error', new Error(msg.text()));
        }
      }
    });
    
    page.on('requestfailed', (request) => {
      logError('Request Failed', new Error(`${request.url()} - ${request.failure()?.errorText}`));
    });

    // ============================================================
    // PART 1: VERIFY AUTHENTICATED SESSION
    // ============================================================
    await test.step('🔐 Verify Authenticated Session', async () => {
      console.log('\n🔐 === PART 1: VERIFYING AUTHENTICATED SESSION ===\n');
      
      try {
        // More robust navigation with retries or explicit waits
        await page.goto('/dashboard', { waitUntil: 'networkidle', timeout: 30000 });
        
        // Wait for potential redirects to finish
        await page.waitForTimeout(2000);
        
        // Check if we were redirected to signin
        if (page.url().includes('/auth/signin')) {
          console.log('⚠️ Session seems invalid, attempting re-login...');
          await page.goto('/auth/signin');
          await page.getByPlaceholder('Enter your username').fill(testUser.username);
          await page.getByPlaceholder('Enter your password').fill(testUser.password);
          await page.getByRole('button', { name: /sign in|login/i }).click();
          await page.waitForURL('**/dashboard', { timeout: 10000 });
        }
        
        // Verify we're logged in with a more resilient check
        const dashboardText = page.getByRole('heading', { name: /Dashboard|Farms/i })
          .or(page.getByText('Dashboard'))
          .or(page.getByText('Farms'))
          .first();
        await expect(dashboardText).toBeVisible({ timeout: 15000 });
        
        console.log(`✅ Authenticated as: ${testUser.username}`);
        logSuccess('Verify authentication', testUser.username);
      } catch (error) {
        logError('Verify authentication', error);
        // Take an extra screenshot for debugging
        await page.screenshot({ path: path.join(__dirname, '..', 'test-results', 'auth-failure.png') });
        throw error;
      }
    });

    // ============================================================
    // PART 2: REGISTER FARMS
    // ============================================================
    await test.step('🏡 Register Multiple Farms', async () => {
      console.log('\n🏡 === PART 2: REGISTERING FARMS ===\n');
      
      const farms = [
        {
          name: 'Green Valley Farm',
          area: '5.5',
          pincode: '122001',
          address: 'Plot 45, Sector 12, Near NH-8',
          latitude: '28.4595',
          longitude: '77.0266'
        },
        {
          name: 'Sunrise Agricultural Land',
          area: '3.2',
          pincode: '122002',
          address: 'Village Wazirabad, Gurugram',
          latitude: '28.4700',
          longitude: '77.0300'
        },
        {
          name: 'Golden Harvest Fields',
          area: '8.0',
          pincode: '122003',
          address: 'Khandsa Road, Near Toll Plaza',
          latitude: '28.4500',
          longitude: '77.0200'
        }
      ];
      
      for (let i = 0; i < farms.length; i++) {
        const farm = farms[i];
        console.log(`\n🌾 Registering Farm ${i + 1}: ${farm.name}`);
        
        try {
          // Navigate to farm registration page
          await page.goto('/farm/register');
          await page.waitForTimeout(2000);
          
          // Wait for form to be visible
          await page.waitForSelector('input[name="farm_name"], input[placeholder*="farm" i], input[type="text"]', { timeout: 10000 });
          
          // Try to find and fill farm name field
          const farmNameInput = await page.locator('input[name="farm_name"], input[placeholder*="farm" i]').first();
          if (await farmNameInput.isVisible()) {
            await farmNameInput.fill(farm.name);
            await page.waitForTimeout(500);
            logSuccess(`Fill farm name ${i + 1}`, farm.name);
          }
          
          // Try to find and fill area field
          const areaInput = await page.locator('input[name="total_area_acres"], input[name="total_area"], input[name="area"], input[placeholder*="area" i]').first();
          if (await areaInput.isVisible()) {
            await areaInput.fill(farm.area);
            await page.waitForTimeout(500);
            logSuccess(`Fill area ${i + 1}`, farm.area);
          }
          
          // Try GPS capture if button exists
          const gpsButton = await page.locator('button:has-text("Capture"), button:has-text("GPS"), button:has-text("Location")').first();
          if (await gpsButton.isVisible().catch(() => false)) {
            await page.context().setGeolocation({ 
              latitude: parseFloat(farm.latitude), 
              longitude: parseFloat(farm.longitude) 
            });
            await gpsButton.click();
            await page.waitForTimeout(2000);
            logSuccess(`GPS capture ${i + 1}`, `${farm.latitude}, ${farm.longitude}`);
          }
          
          // Try to fill pincode
          const pincodeInput = await page.locator('input[name="pincode"], input[placeholder*="pincode" i], input[placeholder*="pin" i]').first();
          if (await pincodeInput.isVisible().catch(() => false)) {
            await pincodeInput.fill(farm.pincode);
            await page.waitForTimeout(1500); // Wait for address lookup
            logSuccess(`Fill pincode ${i + 1}`, farm.pincode);
          }
          
          // Try to fill village
          const villageInput = await page.locator('input[name="village"]').first();
          if (await villageInput.isVisible().catch(() => false)) {
            await villageInput.fill("Test Village");
            await villageInput.press('Escape'); // to close dropdown if any
            logSuccess(`Fill village ${i + 1}`, "Test Village");
          }
          
          // Try to fill address
          const addressInput = await page.locator('input[name="address"], input[name="address_line"], textarea[name="address"]').first();
          if (await addressInput.isVisible().catch(() => false)) {
            await addressInput.fill(farm.address);
            await page.waitForTimeout(500);
            logSuccess(`Fill address ${i + 1}`, farm.address);
          }
          
          // Optionally add a plot
          const addPlotBtn = await page.locator('button:has-text("+ Add Plot")').first();
          if (await addPlotBtn.isVisible().catch(() => false)) {
            await addPlotBtn.click();
            await page.waitForTimeout(500);
            
            // Fill plot name and area
            const plotNameInput = await page.locator('input[type="text"]').last();
            if (await plotNameInput.isVisible()) {
              await plotNameInput.fill(`Main Plot - ${farm.name}`);
            }
            
            // Look for the area input in the plot section
            const plotAreaInput = await page.locator('.border-t.border-gray-200.mt-6.pt-4 input[type="number"]').last();
            if (await plotAreaInput.isVisible()) {
              // Parse out the plot area; let's say roughly half the farm area
              const plotArea = (parseFloat(farm.area) * 0.5).toFixed(1);
              await plotAreaInput.fill(plotArea);
            }
            
            logSuccess(`Add plot to ${farm.name}`);
          }
          
          // Try to submit
          const submitButton = await page.locator('button[type="submit"], button:has-text("Register"), button:has-text("Submit"), button:has-text("Save")').first();
          if (await submitButton.isVisible()) {
            await submitButton.click();
            await page.waitForTimeout(3000);
            logSuccess(`Submit farm ${i + 1}`, farm.name);
          }
          
          console.log(`✅ Farm ${i + 1} registration attempted: ${farm.name}`);
          
        } catch (error) {
          logError(`Register farm ${i + 1} (${farm.name})`, error);
          console.log(`⚠️ Continuing with next farm...`);
        }
      }
      
      console.log('\n✅ Farm registration phase complete\n');
    });

    // ============================================================
    // PART 3: GENERATE AI CROP STRATEGIES
    // ============================================================
    await test.step('🤖 Generate AI Crop Strategies', async () => {
      console.log('\n🤖 === PART 3: GENERATING AI CROP STRATEGIES ===\n');
      
      try {
        // Navigate to strategy request page
        await page.goto('/strategy/request');
        await page.waitForTimeout(2000);
        
        // Check if we need to select a farm first
        const farmSelect = await page.locator('select[name="farm"], select[name="farmId"], select').first();
        if (await farmSelect.isVisible().catch(() => false)) {
          // Select first farm
          await farmSelect.selectOption({ index: 1 });
          await page.waitForTimeout(1000);
          logSuccess('Select farm for strategy');
        }
        
        // Look for generate/request button
        const generateButton = await page.locator(
          'button:has-text("Generate"), button:has-text("Request"), button:has-text("Get"), button[type="submit"]'
        ).first();
        
        if (await generateButton.isVisible()) {
          console.log('⏳ Requesting AI strategy (this may take 5-10 seconds)...');
          await generateButton.click();
          
          // Wait for loading state - Vertex AI API call can be slow
          await page.waitForTimeout(7000);
          
          logSuccess('Generate AI strategy', 'Google Vertex AI called');
          console.log('✨ AI strategy generation attempted');
        }
        
      } catch (error) {
        logError('Generate AI strategy', error);
        console.log('⚠️ Continuing with next step...');
      }
      
      console.log('\n✅ AI strategy phase complete\n');
    });

    // ============================================================
    // PART 4: BROWSE MARKETPLACE
    // ============================================================
    await test.step('🛒 Browse Marketplace', async () => {
      console.log('\n🛒 === PART 4: BROWSING MARKETPLACE ===\n');
      
      try {
        await page.goto('/marketplace');
        await page.waitForTimeout(3000);
        
        // Check if marketplace loaded
        const isMarketplace = await page.locator('text=Marketplace, text=Browse, text=Listings').first().isVisible().catch(() => false);
        if (isMarketplace) {
          logSuccess('Browse marketplace');
          console.log('✅ Marketplace page loaded');
          
          // Try to click on first listing if exists
          const firstListing = await page.locator('.listing-card, [data-testid="listing"], article, .card').first();
          if (await firstListing.isVisible().catch(() => false)) {
            await firstListing.click();
            await page.waitForTimeout(2000);
            logSuccess('View listing detail');
          }
        }
        
      } catch (error) {
        logError('Browse marketplace', error);
      }
      
      console.log('\n✅ Marketplace phase complete\n');
    });

    // ============================================================
    // DEMO DATA SEEDING COMPLETE
    // ============================================================
    await test.step('🎉 Demo Data Seeding Complete', async () => {
      console.log('\n🎉 === DEMO DATA SEEDING COMPLETE ===\n');
      console.log('✅ Summary of attempted data creation:');
      console.log('   📧 Used existing test user');
      console.log('   🏡 Attempted to create 3 farms');
      console.log('   🤖 Attempted to generate AI crop strategy');
      console.log('   🛒 Browsed marketplace');
      console.log('\n📹 Check dashboard to verify data!');
      console.log('🎬 Next: npm test tests/demo-complete-workflow.spec.ts\n');
      
      await page.waitForTimeout(2000);
    });
  });
});
