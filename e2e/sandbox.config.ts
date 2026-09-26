import { defineConfig, devices } from "@playwright/test";

/**
 * Sandbox E2E suite: runs the real app against a throwaway database (cropsense_e2e),
 * so nothing touches production or your local dev data.
 *
 *   npm run sandbox           headless, fast
 *   npm run sandbox:headed    watch the browser (300 ms between actions)
 *   npm run sandbox:watch     slow motion (800 ms) for demos
 *   npm run sandbox:ui        Playwright UI: pick tests, time-travel through steps
 *   npm run sandbox:debug     step through one action at a time with the inspector
 *
 * See sandbox/README.md for details.
 */
const BACKEND_PORT = Number(process.env.E2E_BACKEND_PORT || 8100);
const FRONTEND_PORT = Number(process.env.E2E_FRONTEND_PORT || 3100);
const slowMo = Number(process.env.SLOWMO || 0);

export default defineConfig({
  testDir: "./specs",
  globalSetup: require.resolve("./specs/global-setup"),
  timeout: 90_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  outputDir: "sandbox-results",
  reporter: [
    ["list"],
    ["html", { outputFolder: "sandbox-report", open: "never" }],
  ],
  use: {
    baseURL: `http://localhost:${FRONTEND_PORT}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: process.env.VIDEO === "on" ? "on" : "retain-on-failure",
    viewport: { width: 1440, height: 900 },
    actionTimeout: 15_000,
    navigationTimeout: 45_000,
  },
  projects: [
    {
      name: "desktop",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 }, launchOptions: { slowMo } },
    },
  ],
  webServer: [
    {
      command: "./sandbox/start-backend.sh",
      url: `http://127.0.0.1:${BACKEND_PORT}/health`,
      reuseExistingServer: true,
      timeout: 120_000,
      stdout: "ignore",
      stderr: "pipe",
    },
    {
      command: "./sandbox/start-frontend.sh",
      url: `http://localhost:${FRONTEND_PORT}`,
      reuseExistingServer: true,
      timeout: 120_000,
      stdout: "ignore",
      stderr: "pipe",
    },
  ],
});
