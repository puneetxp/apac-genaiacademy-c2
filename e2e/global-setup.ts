import { chromium, FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Global Setup - Create authenticated session using existing user
 * This runs once before all tests and creates a reusable auth session
 * Uses existing test user credentials instead of creating new user
 */
async function globalSetup(config: FullConfig) {
  console.log('🔧 Running global setup...');
  
  const baseURL = config.projects[0].use.baseURL || 'http://localhost:3000';
  const storageStatePath = path.join(__dirname, '.auth', 'user.json');
  
  // Ensure .auth directory exists
  const authDir = path.join(__dirname, '.auth');
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  // Use existing test user credentials
  // You can change these to match your test user
  const testUser = {
    username: 'puneetxp',
    password: 'Pa$$w0rd!',
    email: 'puneet@example.com',
    full_name: 'Puneet Sharma',
    phone: '+919876543210',
  };
  
  // Save test user credentials for tests to use
  fs.writeFileSync(
    path.join(authDir, 'test-user.json'),
    JSON.stringify(testUser, null, 2)
  );

  // Launch browser
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  const page = await context.newPage();

  try {
    console.log('🔐 Logging in with existing user...');
    
    // Navigate to login page
    await page.goto(`${baseURL}/auth/signin`);
    await page.waitForTimeout(2000);
    
    // Fill login form
    console.log('✍️  Filling login form...');
    await page.getByPlaceholder('Enter your username').fill(testUser.username);
    await page.getByPlaceholder('Enter your password').fill(testUser.password);
    
    // Submit login
    console.log('📤 Submitting login...');
    await page.getByRole('button', { name: /sign in|login/i }).click();
    await page.waitForTimeout(3000);
    
    // Check if login was successful
    const currentUrl = page.url();
    if (currentUrl.includes('/auth/signin')) {
      console.error('❌ Login failed - still on signin page');
      console.error('Current URL:', currentUrl);
      throw new Error('Login failed - check credentials or backend connection');
    }
    
    console.log('✅ Login successful');
    
    // Save authenticated state
    await context.storageState({ path: storageStatePath });
    console.log('💾 Authentication state saved');
    
    console.log('✅ Global setup complete');
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;
