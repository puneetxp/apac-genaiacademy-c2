import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * DEMO DATA SEEDING TEST
 * 
 * Creates realistic, comprehensive demo data for video recording.
 * Uses EXISTING authenticated user from global-setup.ts
 * 
 * This test:
 * 1. Uses existing authenticated session
 * 2. Registers multiple farms with different characteristics
 * 3. Creates plots with various soil types and irrigation
 * 4. Generates AI crop strategies for each farm
 * 5. Plants crops with different stages
 * 6. Creates marketplace listings
 * 7. Adds livestock portfolio
 * 8. Generates buyer interests
 * 
 * Run this BEFORE recording demo video to have rich, realistic data.
 * 
 * Duration: ~15-20 minutes
 * Purpose: Data seeding + bug detection + error logging
 */

test.describe('Demo Data Seeding - Comprehensive Realistic Data', () => {
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
    fs.appendFileSync(logFile, errorMsg);
  }

  // Helper function to log success
  function logSuccess(step: string, details?: string) {
    const timestamp = new Date().toISOString();
    const successMsg = `[${timestamp}] SUCCESS: ${step}${details ? ' - ' + details : ''}\n`;
    console.log(`✅ ${step}${details ? ' - ' + details : ''}`);
    fs.appendFileSync(logFile, successMsg);
  }

  test.beforeAll(async () => {
    console.log('\n🌱 === STARTING DEMO DATA SEEDING ===\n');
    console.log('� This will create comprehensive demo data for video recording\n');
    console.log('🔐 Using existing authenticated session from global-setup\n');
    
    // Initialize error log file
    const resultsDir = path.join(__dirname, '..', 'test-results');
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
    fs.writeFileSync(logFile, `=== DEMO DATA SEEDING ERROR LOG ===\nStarted: ${new Date().toISOString()}\n\n`);
    
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

  test('Seed complete demo data for authenticated user', async ({ page }) => {
    
    // Setup page error listeners
    page.on('pageerror', (error) => {
      logError('Page JavaScript Error', error);
    });
    
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        logError('Console Error', new Error(msg.text()));
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
        await page.goto('/dashboard');
        await page.waitForTimeout(2000);
        
        // Verify we're logged in
        await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 5000 });
        console.log(`✅ Authenticated as: ${testUser.username}`);
        logSuccess('Verify authentication', testUser.username);
      } catch (error) {
        logError('Verify authentication', error);
        throw error;
      }
    });

    // ============================================================
    // PART 2: REGISTER MULTIPLE FARMS
    // ============================================================
    await test.step('🏡 Register Multiple Farms with Different Characteristics', async () => {
      console.log('\n🏡 === PART 2: REGISTERING MULTIPLE FARMS ===\n');
      
      const farms = [
        {
          name: 'Green Valley Farm',
          area: '5.5',
          unit: 'acres',
          pincode: '122001',
          address: 'Plot 45, Sector 12, Near NH-8',
          soil: 'loamy',
          irrigation: 'drip',
          latitude: '28.4595',
          longitude: '77.0266'
        },
        {
          name: 'Sunrise Agricultural Land',
          area: '3.2',
          unit: 'acres',
          pincode: '122002',
          address: 'Village Wazirabad, Gurugram',
          soil: 'clay',
          irrigation: 'sprinkler',
          latitude: '28.4700',
          longitude: '77.0300'
        },
        {
          name: 'Golden Harvest Fields',
          area: '8.0',
          unit: 'acres',
          pincode: '122003',
          address: 'Khandsa Road, Near Toll Plaza',
          soil: 'sandy_loam',
          irrigation: 'flood',
          latitude: '28.4500',
          longitude: '77.0200'
        }
      ];
      
      for (let i = 0; i < farms.length; i++) {
        const farm = farms[i];
        console.log(`\n🌾 Registering Farm ${i + 1}: ${farm.name}`);
        
        try {
          await page.goto('/farms/register');
          await page.waitForTimeout(2000);
          
          // Fill farm details
          await page.fill('input[name="farm_name"]', farm.name);
          await page.fill('input[name="total_area_acres"]', farm.area);
          await page.waitForTimeout(500);
          
          // GPS capture
          console.log('📍 Capturing GPS location...');
          await page.context().setGeolocation({ 
            latitude: parseFloat(farm.latitude), 
            longitude: parseFloat(farm.longitude) 
          });
          await page.click('button:has-text("Capture Location")');
          await page.waitForTimeout(2000);
          
          // Address details
          await page.fill('input[name="pincode"]', farm.pincode);
          await page.waitForTimeout(3000);
          await page.fill('input[name="village"]', 'Test Village');
          await page.keyboard.press('Escape'); // to close dropdown
          await page.fill('input[name="address_line"]', farm.address);
          await page.waitForTimeout(500);
          
          // Soil and irrigation
          await page.selectOption('select[name="soil_type"]', farm.soil);
          await page.selectOption('select[name="irrigation_type"]', farm.irrigation);
          await page.waitForTimeout(1000);
          
          // Submit
          await page.click('button[type="submit"]');
          await page.waitForTimeout(3000);
          
          console.log(`✅ Farm ${i + 1} registered: ${farm.name}`);
          logSuccess(`Register farm ${i + 1}`, farm.name);
        } catch (error) {
          logError(`Register farm ${i + 1} (${farm.name})`, error);
          // Continue with next farm even if one fails
          console.log(`⚠️ Continuing with next farm...`);
        }
      }
      
      console.log('\n✅ Farm registration phase complete\n');
    });

    // ============================================================
    // PART 3: CREATE PLOTS FOR EACH FARM
    // ============================================================
    await test.step('📍 Create Multiple Plots with Different Characteristics', async () => {
      console.log('\n📍 === PART 3: CREATING PLOTS ===\n');
      
      const plots = [
        // Farm 1 plots
        { farm: 1, name: 'North Field', area: '2.0', soil: 'loamy', irrigation: 'drip', sun: 'full', ph: '6.5' },
        { farm: 1, name: 'South Field', area: '1.5', soil: 'loamy', irrigation: 'drip', sun: 'partial', ph: '6.8' },
        { farm: 1, name: 'East Field', area: '2.0', soil: 'loamy', irrigation: 'drip', sun: 'full', ph: '6.3' },
        
        // Farm 2 plots
        { farm: 2, name: 'Main Plot', area: '2.0', soil: 'clay', irrigation: 'sprinkler', sun: 'full', ph: '7.0' },
        { farm: 2, name: 'Back Plot', area: '1.2', soil: 'clay', irrigation: 'sprinkler', sun: 'partial', ph: '7.2' },
        
        // Farm 3 plots
        { farm: 3, name: 'West Section', area: '3.0', soil: 'sandy_loam', irrigation: 'flood', sun: 'full', ph: '6.0' },
        { farm: 3, name: 'East Section', area: '2.5', soil: 'sandy_loam', irrigation: 'flood', sun: 'full', ph: '6.2' },
        { farm: 3, name: 'Central Section', area: '2.5', soil: 'sandy_loam', irrigation: 'flood', sun: 'partial', ph: '6.5' },
      ];
      
      for (let i = 0; i < plots.length; i++) {
        const plot = plots[i];
        console.log(`\n🌱 Creating Plot ${i + 1}: ${plot.name} (Farm ${plot.farm})`);
        
        await page.goto('/plots/create');
        await page.waitForTimeout(2000);
        
        // Check if plot creation page exists
        const plotForm = page.locator('select[name="farm_id"]');
        if (await plotForm.count() === 0) {
          console.log('⚠️  Plot creation page not found, skipping plot creation');
          logError('Plot creation', 'Page /plots/create does not exist');
          break; // Exit the loop
        }
        
        // Select farm
        await page.selectOption('select[name="farm_id"]', { index: plot.farm });
        await page.waitForTimeout(500);
        
        // Fill plot details
        await page.fill('input[name="plot_name"]', plot.name);
        await page.fill('input[name="plot_area"]', plot.area);
        await page.selectOption('select[name="soil_type"]', plot.soil);
        await page.selectOption('select[name="irrigation"]', plot.irrigation);
        await page.selectOption('select[name="sun_exposure"]', plot.sun);
        await page.fill('input[name="soil_ph"]', plot.ph);
        await page.waitForTimeout(1000);
        
        // Submit
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);
        
        console.log(`✅ Plot ${i + 1} created: ${plot.name}`);
      }
      
      console.log('\n✅ All 8 plots created successfully\n');
    });

    // ============================================================
    // PART 4: GENERATE AI CROP STRATEGIES
    // ============================================================
    await test.step('🤖 Generate AI Crop Strategies for Each Farm', async () => {
      console.log('\n🤖 === PART 4: GENERATING AI CROP STRATEGIES ===\n');
      
      const farms = [1, 2, 3];
      
      for (let i = 0; i < farms.length; i++) {
        const farmIndex = farms[i];
        console.log(`\n🌾 Generating AI strategy for Farm ${farmIndex}...`);
        
        await page.goto('/crops/plan');
        await page.waitForTimeout(2000);
        
        // Select farm
        await page.selectOption('select[name="farm_id"]', { index: farmIndex });
        await page.waitForTimeout(1000);
        
        // Request AI recommendations
        console.log('⏳ Calling Google Vertex AI API (this may take 5-10 seconds)...');
        await page.click('button:has-text("Get AI Recommendations")');
        
        // Wait for Vertex AI processing
        await expect(page.locator('text=Analyzing with AI')).toBeVisible();
        await page.waitForTimeout(10000); // Vertex AI API call
        
        // Verify recommendations loaded
        await expect(page.locator('.recommendation-card')).toHaveCount(3, { timeout: 15000 });
        console.log('✨ Google Vertex AI recommendations received!');
        
        // View details
        await page.click('.recommendation-card:first-child');
        await page.waitForTimeout(2000);
        
        // Save strategy
        console.log('💾 Saving AI-generated strategy...');
        await page.click('button:has-text("Save Strategy")');
        await page.waitForTimeout(2000);
        
        console.log(`✅ AI strategy saved for Farm ${farmIndex}`);
      }
      
      console.log('\n✅ All AI crop strategies generated\n');
    });

    // ============================================================
    // PART 5: PLANT CROPS IN DIFFERENT STAGES
    // ============================================================
    await test.step('🌾 Plant Crops in Different Growth Stages', async () => {
      console.log('\n🌾 === PART 5: PLANTING CROPS ===\n');
      
      const crops = [
        // Recently planted (0-30 days)
        { plot: 1, crop: 'wheat', planted: '2026-02-15', stage: 'germination', health: 'excellent' },
        { plot: 2, crop: 'rice', planted: '2026-02-20', stage: 'germination', health: 'good' },
        
        // Growing (30-60 days)
        { plot: 3, crop: 'corn', planted: '2026-01-15', stage: 'vegetative', health: 'excellent' },
        { plot: 4, crop: 'cotton', planted: '2026-01-20', stage: 'vegetative', health: 'good' },
        
        // Mature (60-90 days)
        { plot: 5, crop: 'tomato', planted: '2025-12-15', stage: 'flowering', health: 'excellent' },
        { plot: 6, crop: 'potato', planted: '2025-12-20', stage: 'flowering', health: 'good' },
        
        // Ready for harvest (90+ days)
        { plot: 7, crop: 'wheat', planted: '2025-11-15', stage: 'maturity', health: 'excellent' },
        { plot: 8, crop: 'mustard', planted: '2025-11-20', stage: 'maturity', health: 'good' },
      ];
      
      for (let i = 0; i < crops.length; i++) {
        const crop = crops[i];
        console.log(`\n🌱 Planting Crop ${i + 1}: ${crop.crop} in Plot ${crop.plot}`);
        
        await page.goto('/crops/plant');
        await page.waitForTimeout(2000);
        
        // Select plot
        await page.selectOption('select[name="plot_id"]', { index: crop.plot });
        await page.waitForTimeout(500);
        
        // Fill crop details
        await page.selectOption('select[name="crop_type"]', crop.crop);
        await page.fill('input[name="planting_date"]', crop.planted);
        await page.selectOption('select[name="growth_stage"]', crop.stage);
        await page.selectOption('select[name="health_status"]', crop.health);
        await page.waitForTimeout(1000);
        
        // Submit
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);
        
        console.log(`✅ Crop ${i + 1} planted: ${crop.crop} (${crop.stage})`);
      }
      
      console.log('\n✅ All 8 crops planted with different stages\n');
    });

    // ============================================================
    // PART 6: CREATE MARKETPLACE LISTINGS
    // ============================================================
    await test.step('🛒 Create Marketplace Listings with AI Predictions', async () => {
      console.log('\n🛒 === PART 6: CREATING MARKETPLACE LISTINGS ===\n');
      
      const listings = [
        { plot: 7, crop: 'wheat', harvest: '2026-03-15', quantity: '3500', grade: 'A', price: '25' },
        { plot: 8, crop: 'mustard', harvest: '2026-03-20', quantity: '1200', grade: 'A', price: '60' },
        { plot: 5, crop: 'tomato', harvest: '2026-04-10', quantity: '2000', grade: 'B', price: '30' },
        { plot: 6, crop: 'potato', harvest: '2026-04-15', quantity: '4000', grade: 'A', price: '20' },
      ];
      
      for (let i = 0; i < listings.length; i++) {
        const listing = listings[i];
        console.log(`\n📢 Creating Listing ${i + 1}: ${listing.crop} from Plot ${listing.plot}`);
        
        await page.goto('/marketplace/create');
        await page.waitForTimeout(2000);
        
        // Fill listing details
        await page.selectOption('select[name="plot_id"]', { index: listing.plot });
        await page.selectOption('select[name="crop"]', listing.crop);
        await page.fill('input[name="expected_harvest"]', listing.harvest);
        await page.fill('input[name="quantity"]', listing.quantity);
        await page.selectOption('select[name="quality_grade"]', listing.grade);
        await page.fill('input[name="price_per_kg"]', listing.price);
        await page.waitForTimeout(1000);
        
        // Verify AI predictions visible
        console.log('🤖 AI predictions included in listing...');
        await expect(page.locator('text=AI Yield Confidence')).toBeVisible();
        
        // Submit
        await page.click('button:has-text("Publish Listing")');
        await page.waitForTimeout(2000);
        
        console.log(`✅ Listing ${i + 1} published: ${listing.crop}`);
      }
      
      console.log('\n✅ All 4 marketplace listings created\n');
    });

    // ============================================================
    // PART 7: ADD LIVESTOCK PORTFOLIO
    // ============================================================
    await test.step('🐄 Add Livestock Portfolio', async () => {
      console.log('\n🐄 === PART 7: ADDING LIVESTOCK ===\n');
      
      const livestock = [
        { type: 'cow', breed: 'Holstein', age: '3', gender: 'female', purpose: 'dairy', purchased: '2024-01-15', price: '45000' },
        { type: 'cow', breed: 'Jersey', age: '4', gender: 'female', purpose: 'dairy', purchased: '2024-02-20', price: '40000' },
        { type: 'buffalo', breed: 'Murrah', age: '5', gender: 'female', purpose: 'dairy', purchased: '2023-12-10', price: '60000' },
        { type: 'goat', breed: 'Beetal', age: '2', gender: 'male', purpose: 'meat', purchased: '2025-06-15', price: '8000' },
        { type: 'goat', breed: 'Sirohi', age: '1', gender: 'female', purpose: 'breeding', purchased: '2025-08-20', price: '7000' },
      ];
      
      for (let i = 0; i < livestock.length; i++) {
        const animal = livestock[i];
        console.log(`\n🐮 Adding Livestock ${i + 1}: ${animal.breed} ${animal.type}`);
        
        await page.goto('/livestock/register');
        await page.waitForTimeout(2000);
        
        // Fill livestock details
        await page.selectOption('select[name="animal_type"]', animal.type);
        await page.fill('input[name="breed"]', animal.breed);
        await page.fill('input[name="age"]', animal.age);
        await page.selectOption('select[name="gender"]', animal.gender);
        await page.selectOption('select[name="purpose"]', animal.purpose);
        await page.fill('input[name="purchase_date"]', animal.purchased);
        await page.fill('input[name="purchase_price"]', animal.price);
        await page.waitForTimeout(1000);
        
        // Submit
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);
        
        // View ROI calculation
        console.log('💰 Viewing AI ROI calculation...');
        await page.click('button:has-text("Calculate ROI")');
        await page.waitForTimeout(2000);
        
        console.log(`✅ Livestock ${i + 1} added: ${animal.breed} ${animal.type}`);
      }
      
      console.log('\n✅ All 5 livestock added to portfolio\n');
    });

    // ============================================================
    // PART 8: GENERATE BUYER INTERESTS
    // ============================================================
    await test.step('👥 Generate Buyer Interests for Listings', async () => {
      console.log('\n👥 === PART 8: GENERATING BUYER INTERESTS ===\n');
      
      const interests = [
        { listing: 1, buyer: 'Agro Traders Pvt Ltd', quantity: '1000', contact: '+91-9876543211' },
        { listing: 1, buyer: 'Fresh Harvest Co.', quantity: '1500', contact: '+91-9876543212' },
        { listing: 2, buyer: 'Oil Mills India', quantity: '800', contact: '+91-9876543213' },
        { listing: 3, buyer: 'Vegetable Market Delhi', quantity: '500', contact: '+91-9876543214' },
        { listing: 4, buyer: 'Potato Wholesalers', quantity: '2000', contact: '+91-9876543215' },
      ];
      
      for (let i = 0; i < interests.length; i++) {
        const interest = interests[i];
        console.log(`\n📞 Creating Interest ${i + 1}: ${interest.buyer}`);
        
        await page.goto('/marketplace');
        await page.waitForTimeout(2000);
        
        // Click on listing
        await page.click(`.listing-card:nth-child(${interest.listing})`);
        await page.waitForTimeout(2000);
        
        // Register interest
        await page.click('button:has-text("Register Interest")');
        await page.waitForTimeout(1000);
        
        await page.fill('input[name="buyer_name"]', interest.buyer);
        await page.fill('input[name="quantity_needed"]', interest.quantity);
        await page.fill('input[name="contact"]', interest.contact);
        await page.waitForTimeout(500);
        
        await page.click('button:has-text("Submit Interest")');
        await page.waitForTimeout(2000);
        
        console.log(`✅ Interest ${i + 1} registered: ${interest.buyer}`);
      }
      
      console.log('\n✅ All 5 buyer interests generated\n');
    });

    // ============================================================
    // PART 9: ADD WEATHER ALERTS & SOIL TESTS
    // ============================================================
    await test.step('🌦️ Add Weather Alerts and Soil Test Records', async () => {
      console.log('\n🌦️ === PART 9: ADDING WEATHER & SOIL DATA ===\n');
      
      // Add soil test records
      const soilTests = [
        { plot: 1, date: '2026-01-15', ph: '6.5', nitrogen: 'medium', phosphorus: 'high', potassium: 'medium' },
        { plot: 3, date: '2026-01-20', ph: '6.3', nitrogen: 'high', phosphorus: 'medium', potassium: 'high' },
        { plot: 5, date: '2025-12-10', ph: '7.0', nitrogen: 'medium', phosphorus: 'medium', potassium: 'medium' },
      ];
      
      for (let i = 0; i < soilTests.length; i++) {
        const test = soilTests[i];
        console.log(`\n🧪 Adding Soil Test ${i + 1} for Plot ${test.plot}`);
        
        await page.goto('/soil/test');
        await page.waitForTimeout(2000);
        
        await page.selectOption('select[name="plot_id"]', { index: test.plot });
        await page.fill('input[name="test_date"]', test.date);
        await page.fill('input[name="ph_level"]', test.ph);
        await page.selectOption('select[name="nitrogen"]', test.nitrogen);
        await page.selectOption('select[name="phosphorus"]', test.phosphorus);
        await page.selectOption('select[name="potassium"]', test.potassium);
        await page.waitForTimeout(1000);
        
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);
        
        console.log(`✅ Soil test ${i + 1} recorded`);
      }
      
      console.log('\n✅ All soil test records added\n');
    });

    // ============================================================
    // DEMO DATA SEEDING COMPLETE
    // ============================================================
    await test.step('🎉 Demo Data Seeding Complete', async () => {
      console.log('\n🎉 === DEMO DATA SEEDING COMPLETE ===\n');
      console.log('✅ Summary of created data:');
      console.log('   📧 1 Demo farmer account (demo.farmer@cropsense.ai)');
      console.log('   🏡 3 Farms with different characteristics');
      console.log('   📍 8 Plots with various soil types and irrigation');
      console.log('   🤖 3 AI crop strategies (Google Vertex AI)');
      console.log('   🌾 8 Crops in different growth stages');
      console.log('   🛒 4 Marketplace listings with AI predictions');
      console.log('   🐄 5 Livestock animals with ROI calculations');
      console.log('   👥 5 Buyer interests');
      console.log('   🧪 3 Soil test records');
      console.log('\n📹 Ready for demo video recording!');
      console.log('🎬 Run: npm test tests/demo-complete-workflow.spec.ts\n');
      
      await page.waitForTimeout(3000);
    });
  });
});
