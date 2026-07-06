import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * ADAPTIVE DEMO DATA SEEDING TEST
 * 
 * Intelligently seeds data by:
 * 1. Checking what elements actually exist on each page
 * 2. Logging detailed information about page state
 * 3. Adapting to actual form fields and buttons
 * 4. Continuing even when elements are missing
 * 5. Taking screenshots on errors
 * 6. Logging all issues for debugging
 * 
 * This test will help identify frontend issues and still create data where possible.
 */

test.describe('Adaptive Demo Data Seeding', () => {
  let testUser: any;
  let errorLog: string[] = [];
  const logFile = path.join(__dirname, '..', 'test-results', 'seed-data-adaptive.log');
  const screenshotDir = path.join(__dirname, '..', 'test-results', 'screenshots');

  // Helper to take screenshot
  async function takeScreenshot(page: any, name: string) {
    try {
      const filename = `${name}-${Date.now()}.png`;
      const filepath = path.join(screenshotDir, filename);
      await page.screenshot({ path: filepath, fullPage: true });
      return filename;
    } catch (e) {
      return null;
    }
  }

  // Helper to log with details
  function log(level: 'INFO' | 'SUCCESS' | 'ERROR' | 'WARNING', step: string, details?: any) {
    const timestamp = new Date().toISOString();
    const emoji = {
      'INFO': 'ℹ️',
      'SUCCESS': '✅',
      'ERROR': '❌',
      'WARNING': '⚠️'
    }[level];
    
    let message = `[${timestamp}] ${level}: ${step}`;
    if (details) {
      if (typeof details === 'string') {
        message += ` - ${details}`;
      } else if (details instanceof Error) {
        message += `\n  Error: ${details.message}\n  Stack: ${details.stack}`;
      } else {
        message += `\n  ${JSON.stringify(details, null, 2)}`;
      }
    }
    message += '\n';
    
    console.log(`${emoji} ${step}${details && typeof details === 'string' ? ' - ' + details : ''}`);
    
    try {
      fs.appendFileSync(logFile, message);
    } catch (e) {
      console.error('Failed to write to log:', e);
    }
    
    if (level === 'ERROR') {
      errorLog.push(message);
    }
  }

  // Helper to inspect page and log available elements
  async function inspectPage(page: any, pageName: string) {
    log('INFO', `Inspecting page: ${pageName}`);
    
    try {
      // Get page title
      const title = await page.title();
      log('INFO', `Page title: ${title}`);
      
      // Get all input fields
      const inputs = await page.locator('input').all();
      log('INFO', `Found ${inputs.length} input fields`);
      
      for (let i = 0; i < Math.min(inputs.length, 10); i++) {
        const input = inputs[i];
        const name = await input.getAttribute('name').catch(() => null);
        const placeholder = await input.getAttribute('placeholder').catch(() => null);
        const type = await input.getAttribute('type').catch(() => null);
        log('INFO', `  Input ${i + 1}: name="${name}", placeholder="${placeholder}", type="${type}"`);
      }
      
      // Get all buttons
      const buttons = await page.locator('button').all();
      log('INFO', `Found ${buttons.length} buttons`);
      
      for (let i = 0; i < Math.min(buttons.length, 10); i++) {
        const button = buttons[i];
        const text = await button.textContent().catch(() => null);
        const type = await button.getAttribute('type').catch(() => null);
        log('INFO', `  Button ${i + 1}: text="${text?.trim()}", type="${type}"`);
      }
      
      // Get all select elements
      const selects = await page.locator('select').all();
      log('INFO', `Found ${selects.length} select elements`);
      
      for (let i = 0; i < selects.length; i++) {
        const select = selects[i];
        const name = await select.getAttribute('name').catch(() => null);
        log('INFO', `  Select ${i + 1}: name="${name}"`);
      }
      
      // Get current URL
      const url = page.url();
      log('INFO', `Current URL: ${url}`);
      
    } catch (error) {
      log('ERROR', `Failed to inspect page: ${pageName}`, error);
    }
  }

  // Helper to find and fill input field
  async function findAndFillInput(page: any, fieldName: string, value: string, possibleSelectors: string[]) {
    log('INFO', `Attempting to fill field: ${fieldName}`);
    
    for (const selector of possibleSelectors) {
      try {
        const element = page.locator(selector).first();
        const isVisible = await element.isVisible({ timeout: 2000 }).catch(() => false);
        
        if (isVisible) {
          await element.fill(value);
          log('SUCCESS', `Filled ${fieldName}`, `selector: ${selector}, value: ${value}`);
          return true;
        }
      } catch (error) {
        // Try next selector
      }
    }
    
    log('WARNING', `Could not find field: ${fieldName}`, `Tried selectors: ${possibleSelectors.join(', ')}`);
    return false;
  }

  // Helper to find and click button
  async function findAndClickButton(page: any, buttonName: string, possibleSelectors: string[]) {
    log('INFO', `Attempting to click button: ${buttonName}`);
    
    for (const selector of possibleSelectors) {
      try {
        const element = page.locator(selector).first();
        const isVisible = await element.isVisible({ timeout: 2000 }).catch(() => false);
        
        if (isVisible) {
          await element.click();
          log('SUCCESS', `Clicked ${buttonName}`, `selector: ${selector}`);
          return true;
        }
      } catch (error) {
        // Try next selector
      }
    }
    
    log('WARNING', `Could not find button: ${buttonName}`, `Tried selectors: ${possibleSelectors.join(', ')}`);
    return false;
  }

  test.beforeAll(async () => {
    console.log('\n🌱 === STARTING ADAPTIVE DEMO DATA SEEDING ===\n');
    
    // Create directories
    const resultsDir = path.join(__dirname, '..', 'test-results');
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    
    // Initialize log
    fs.writeFileSync(logFile, `=== ADAPTIVE DEMO DATA SEEDING LOG ===\nStarted: ${new Date().toISOString()}\n\n`);
    
    // Load test user
    const authDir = path.join(__dirname, '..', '.auth');
    const userFile = path.join(authDir, 'test-user.json');
    
    if (fs.existsSync(userFile)) {
      testUser = JSON.parse(fs.readFileSync(userFile, 'utf-8'));
      log('SUCCESS', 'Loaded test user', testUser.username);
    } else {
      log('ERROR', 'Test user not found', 'Run global-setup first');
      throw new Error('Test user not found');
    }
  });

  test.afterAll(async () => {
    console.log('\n📊 === SEEDING SUMMARY ===\n');
    if (errorLog.length === 0) {
      console.log('✅ No errors encountered!');
      fs.appendFileSync(logFile, '\n=== COMPLETED SUCCESSFULLY ===\n');
    } else {
      console.log(`⚠️ Errors encountered: ${errorLog.length}`);
      console.log(`📄 Log: ${logFile}`);
      console.log(`📸 Screenshots: ${screenshotDir}`);
      fs.appendFileSync(logFile, `\n=== COMPLETED WITH ${errorLog.length} ERRORS ===\n`);
    }
  });

  test('Adaptive data seeding with detailed logging', async ({ page }) => {
    
    // Setup error listeners
    page.on('pageerror', (error) => {
      if (!error.message.includes('X-Frame-Options') && 
          !error.message.includes('Content Security Policy')) {
        log('ERROR', 'Page JavaScript Error', error);
      }
    });
    
    page.on('requestfailed', (request) => {
      log('ERROR', 'Request Failed', `${request.url()} - ${request.failure()?.errorText}`);
    });

    // ============================================================
    // STEP 1: VERIFY AUTHENTICATION
    // ============================================================
    await test.step('🔐 Verify Authentication', async () => {
      log('INFO', 'STEP 1: Verifying authentication');
      
      try {
        await page.goto('/dashboard', { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(2000);
        
        await inspectPage(page, 'Dashboard');
        
        const screenshot = await takeScreenshot(page, 'dashboard');
        log('INFO', 'Screenshot taken', screenshot);
        
        // Check if authenticated
        const isDashboard = await page.locator('text=Dashboard, h1:has-text("Dashboard"), [data-testid="dashboard"]').first().isVisible({ timeout: 5000 }).catch(() => false);
        
        if (isDashboard) {
          log('SUCCESS', 'Authenticated successfully', testUser.username);
        } else {
          log('WARNING', 'Dashboard not clearly visible', 'May not be authenticated');
        }
        
      } catch (error) {
        log('ERROR', 'Authentication verification failed', error);
        await takeScreenshot(page, 'auth-error');
        throw error;
      }
    });

    // ============================================================
    // STEP 2: REGISTER FIRST FARM
    // ============================================================
    await test.step('🏡 Register Farm 1', async () => {
      log('INFO', 'STEP 2: Registering first farm');
      
      const farmData = {
        name: 'Green Valley Farm',
        area: '5.5',
        pincode: '122001',
        address: 'Plot 45, Sector 12',
        latitude: '28.4595',
        longitude: '77.0266'
      };
      
      let farmId: string | null = null;
      
      // Set up request/response logging BEFORE navigation
      page.on('request', (request) => {
        if (request.url().includes('/farms') && request.method() === 'POST') {
          log('INFO', 'Farm creation request', {
            url: request.url(),
            method: request.method(),
            postData: request.postData()
          });
        }
      });
      
      page.on('response', async (response) => {
        if (response.url().includes('/farms') && response.request().method() === 'POST') {
          log('INFO', 'Farm creation response', {
            url: response.url(),
            status: response.status(),
            statusText: response.statusText()
          });
          
          if (response.status() >= 400) {
            try {
              const body = await response.json();
              log('ERROR', 'Backend API Error Response', JSON.stringify(body, null, 2));
            } catch (e) {
              try {
                const text = await response.text();
                log('ERROR', 'Backend API Error Response (text)', text);
              } catch (e2) {
                log('ERROR', 'Could not read response body', e2);
              }
            }
          }
        }
      });
      
      try {
        // Navigate to farm registration
        log('INFO', 'Navigating to /farm/register');
        await page.goto('/farm/register', { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);
        
        await inspectPage(page, 'Farm Registration');
        await takeScreenshot(page, 'farm-register-page');
        
        // Try to fill farm name
        const farmNameFilled = await findAndFillInput(
          page,
          'Farm Name',
          farmData.name,
          [
            'input[name="farm_name"]',
            'input[name="farmName"]',
            'input[name="name"]',
            'input[placeholder*="farm" i][placeholder*="name" i]',
            'input[placeholder*="name" i]'
          ]
        );
        
        if (farmNameFilled) {
          await page.waitForTimeout(500);
        }
        
        // Try to fill area
        const areaFilled = await findAndFillInput(
          page,
          'Area',
          farmData.area,
          [
            'input[name="total_area_acres"]',
            'input[name="total_area"]',
            'input[name="area"]',
            'input[name="farmArea"]',
            'input[placeholder*="area" i]',
            'input[type="number"]'
          ]
        );
        
        if (areaFilled) {
          await page.waitForTimeout(500);
        }
        
        // Try GPS capture
        log('INFO', 'Setting geolocation');
        await page.context().setGeolocation({ 
          latitude: parseFloat(farmData.latitude), 
          longitude: parseFloat(farmData.longitude) 
        });
        
        const gpsClicked = await findAndClickButton(
          page,
          'GPS Capture',
          [
            'button:has-text("Capture Location")',
            'button:has-text("Capture")',
            'button:has-text("GPS")',
            'button:has-text("Get Location")',
            'button[aria-label*="location" i]'
          ]
        );
        
        if (gpsClicked) {
          await page.waitForTimeout(2000);
          await takeScreenshot(page, 'after-gps-capture');
        }
        
        // Try to fill pincode
        const pincodeFilled = await findAndFillInput(
          page,
          'Pincode',
          farmData.pincode,
          [
            'input[name="pincode"]',
            'input[name="pin"]',
            'input[name="zipcode"]',
            'input[placeholder*="pincode" i]',
            'input[placeholder*="pin" i]'
          ]
        );
        
        if (pincodeFilled) {
          log('INFO', 'Waiting for address lookup (3 seconds)');
          await page.waitForTimeout(3000);
          await takeScreenshot(page, 'after-pincode-lookup');
          
          // Check if state, district, village were auto-filled
          const stateValue = await page.locator('input[name="state"]').inputValue().catch(() => '');
          const districtValue = await page.locator('input[name="district"]').inputValue().catch(() => '');
          
          log('INFO', 'Address lookup results', `State: "${stateValue}", District: "${districtValue}"`);
          
          // Check if village is a select dropdown or input
          const villageSelect = page.locator('select[name="village"]').first();
          const villageInput = page.locator('input[name="village"]').first();
          
          const isSelectVisible = await villageSelect.isVisible({ timeout: 2000 }).catch(() => false);
          const isInputVisible = await villageInput.isVisible({ timeout: 2000 }).catch(() => false);
          
          if (isSelectVisible) {
            // Village is a dropdown, select first option
            try {
              const options = await villageSelect.locator('option').all();
              log('INFO', `Found ${options.length} village options in dropdown`);
              
              if (options.length > 1) {
                await villageSelect.selectOption({ index: 1 }); // Select first non-empty option
                const selectedValue = await villageSelect.inputValue();
                log('SUCCESS', 'Selected village from dropdown', selectedValue);
              }
            } catch (error) {
              log('ERROR', 'Failed to select village from dropdown', error);
            }
          } else if (isInputVisible) {
            // Village is an input field
            const villageValue = await villageInput.inputValue().catch(() => '');
            
            if (!villageValue) {
              log('WARNING', 'Village input is empty', 'Attempting manual fill');
              await villageInput.fill('Gurgaon');
              log('SUCCESS', 'Filled village input manually', 'Gurgaon');
            } else {
              log('INFO', 'Village already filled', villageValue);
            }
          } else {
            log('WARNING', 'Village field not found', 'Neither select nor input visible');
          }
        }
        
        // Try to fill address line 1
        const addressFilled = await findAndFillInput(
          page,
          'Address Line 1',
          farmData.address,
          [
            'input[name="address_line"]',
            'input[name="address"]',
            'input[name="address_line"]',
            'input[name="addressLine"]',
            'textarea[name="address"]',
            'input[placeholder*="house" i]',
            'input[placeholder*="street" i]'
          ]
        );
        
        if (addressFilled) {
          await page.waitForTimeout(500);
        }
        
        // Take screenshot before submit
        await takeScreenshot(page, 'before-farm-submit');
        
        // Try to submit
        const submitted = await findAndClickButton(
          page,
          'Submit Farm',
          [
            'button[type="submit"]',
            'button:has-text("Register")',
            'button:has-text("Submit")',
            'button:has-text("Save")',
            'button:has-text("Create")'
          ]
        );
        
        if (submitted) {
          log('INFO', 'Waiting for submission to complete');
          await page.waitForTimeout(5000); // Increased wait time
          await takeScreenshot(page, 'after-farm-submit');
          
          // Check for validation errors or error messages
          const errorMessages = await page.locator('.text-red-600, .text-red-500, .text-red-800, [class*="error"]').allTextContents();
          if (errorMessages.length > 0) {
            log('ERROR', 'Validation errors found', errorMessages.join(', '));
          }
          
          // Check for success message or redirect
          const currentUrl = page.url();
          log('INFO', 'Current URL after submit', currentUrl);
          
          // Extract farm ID from URL if redirected to /farm/:id
          const farmIdMatch = currentUrl.match(/\/farm\/(\d+)/);
          if (farmIdMatch) {
            farmId = farmIdMatch[1];
            log('SUCCESS', 'Farm registration successful', `Farm ID: ${farmId}`);
          } else if (currentUrl.includes('/dashboard')) {
            log('WARNING', 'Redirected to dashboard', 'Farm may have been created but ID unknown');
            
            // Try to get farm ID from dashboard
            await page.waitForTimeout(2000);
            const farmLinks = await page.locator('a[href*="/farm/"]').all();
            if (farmLinks.length > 0) {
              const href = await farmLinks[0].getAttribute('href');
              const match = href?.match(/\/farm\/(\d+)/);
              if (match) {
                farmId = match[1];
                log('SUCCESS', 'Found farm ID from dashboard', `Farm ID: ${farmId}`);
              }
            }
          } else {
            log('WARNING', 'Farm registration status unclear', 'No redirect detected');
          }
        } else {
          log('WARNING', 'Could not submit farm form', 'Submit button not found');
        }
        
        // Store farmId for next step
        if (farmId) {
          (page as any).farmId = farmId;
        }
        
      } catch (error) {
        log('ERROR', 'Farm registration failed', error);
        await takeScreenshot(page, 'farm-register-error');
      }
    });

    // ============================================================
    // STEP 3: REQUEST AI CROP STRATEGY
    // ============================================================
    await test.step('🤖 Request AI Crop Strategy', async () => {
      log('INFO', 'STEP 3: Requesting AI crop strategy');
      
      try {
        // Get farmId from previous step
        const farmId = (page as any).farmId;
        
        if (!farmId) {
          log('WARNING', 'No farm ID available', 'Skipping strategy request');
          return;
        }
        
        log('INFO', `Navigating to /strategy/request?farmId=${farmId}`);
        await page.goto(`/strategy/request?farmId=${farmId}`, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);
        
        await inspectPage(page, 'Strategy Request');
        await takeScreenshot(page, 'strategy-request-page');
        
        // Take screenshot before generating
        await takeScreenshot(page, 'before-strategy-generate');
        
        // Try to click generate button
        const generated = await findAndClickButton(
          page,
          'Generate Strategy',
          [
            'button:has-text("Generate")',
            'button:has-text("Request")',
            'button:has-text("Get Strategy")',
            'button:has-text("Get Recommendations")',
            'button[type="submit"]'
          ]
        );
        
        if (generated) {
          log('INFO', 'Waiting for AI strategy generation (10 seconds)');
          await page.waitForTimeout(10000);
          await takeScreenshot(page, 'after-strategy-generate');
          
          // Check for results
          const hasResults = await page.locator('.recommendation, .strategy, .result, [data-testid="strategy-result"]').first().isVisible({ timeout: 5000 }).catch(() => false);
          
          if (hasResults) {
            log('SUCCESS', 'AI strategy generated successfully');
          } else {
            log('WARNING', 'AI strategy results not clearly visible');
          }
        } else {
          log('WARNING', 'Could not click generate button');
        }
        
      } catch (error) {
        log('ERROR', 'AI strategy request failed', error);
        await takeScreenshot(page, 'strategy-error');
      }
    });

    // ============================================================
    // STEP 4: BROWSE MARKETPLACE
    // ============================================================
    await test.step('🛒 Browse Marketplace', async () => {
      log('INFO', 'STEP 4: Browsing marketplace');
      
      try {
        log('INFO', 'Navigating to /marketplace');
        await page.goto('/marketplace', { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);
        
        await inspectPage(page, 'Marketplace');
        await takeScreenshot(page, 'marketplace-page');
        
        // Check for listings
        const listings = await page.locator('.listing, .card, article, [data-testid="listing"]').all();
        log('INFO', `Found ${listings.length} marketplace listings`);
        
        if (listings.length > 0) {
          log('SUCCESS', 'Marketplace has listings');
          
          // Try to click first listing
          try {
            await listings[0].click();
            await page.waitForTimeout(2000);
            await takeScreenshot(page, 'listing-detail');
            log('SUCCESS', 'Viewed listing detail');
          } catch (error) {
            log('WARNING', 'Could not click listing', error);
          }
        } else {
          log('INFO', 'No marketplace listings found', 'This is expected for new account');
        }
        
      } catch (error) {
        log('ERROR', 'Marketplace browsing failed', error);
        await takeScreenshot(page, 'marketplace-error');
      }
    });

    // ============================================================
    // STEP 5: RETURN TO DASHBOARD
    // ============================================================
    await test.step('📊 Return to Dashboard', async () => {
      log('INFO', 'STEP 5: Returning to dashboard');
      
      try {
        await page.goto('/dashboard', { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(2000);
        
        await inspectPage(page, 'Dashboard Final');
        await takeScreenshot(page, 'dashboard-final');
        
        log('SUCCESS', 'Returned to dashboard');
        
      } catch (error) {
        log('ERROR', 'Dashboard navigation failed', error);
      }
    });

    // ============================================================
    // SEEDING COMPLETE
    // ============================================================
    await test.step('🎉 Seeding Complete', async () => {
      log('INFO', '=== SEEDING COMPLETE ===');
      log('INFO', 'Check the following:');
      log('INFO', `  - Log file: ${logFile}`);
      log('INFO', `  - Screenshots: ${screenshotDir}`);
      log('INFO', '  - Dashboard at http://localhost:3000/dashboard');
      log('INFO', 'Review logs to identify and fix frontend issues');
    });
  });
});
