import { defineConfig, devices } from "@playwright/test";
import * as path from "path";

/**
 * Playwright Configuration for Rural Farming Platform E2E Tests
 * Includes video recording for demo purposes and shared authentication
 */
export default defineConfig({
  testDir: "./tests",

  // Global setup for authentication
  globalSetup: require.resolve("./global-setup"),

  // Maximum time one test can run
  timeout: 60 * 1000,

  // Test execution settings
  fullyParallel: false, // Run tests sequentially for demo recording
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker for consistent demo recording

  // Reporter configuration
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["json", { outputFile: "test-results/results.json" }],
    ["list"],
  ],

  // Shared settings for all tests
  use: {
    // Base URL for the application
    baseURL: "http://localhost:3001",

    // Use saved authentication state
    storageState: path.join(__dirname, ".auth", "user.json"),

    // Collect trace on every run to record every request
    trace: "on",

    // Screenshot on failure
    screenshot: "only-on-failure",

    // Video recording for demo
    video: {
      mode: "on", // Always record video
      size: { width: 1920, height: 1080 },
    },

    // Viewport size
    viewport: { width: 1920, height: 1080 },

    // Ignore HTTPS errors (for local development)
    ignoreHTTPSErrors: true,

    // Slow down actions for better demo visibility
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // Configure projects for different browsers
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        launchOptions: {
          slowMo: 500, // Slow down by 500ms for demo
        },
      },
    },
    // Uncomment for cross-browser testing
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    // Mobile viewports for responsive testing
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],
  // Note: Servers should be running before tests
  // Backend: cd cropsense-ai/python && uvicorn app.main:app --reload
  // Frontend: cd cropsense-ai/solidjs && npm run dev
});
