import { test, expect, authState, watchProblems, expectNoProblems, settle, Role } from "./fixtures";

/**
 * Opens every routed page as the right user and fails on uncaught errors, failing API calls,
 * console errors, or an error screen. This is the quick "is anything broken" sweep; feature
 * specs (10-*.spec.ts) check that the data on each page is actually right.
 */
// allow: problems that are expected in the sandbox (e.g. no external weather source -> 503).
const PAGES: Array<{ path: string; role: Role; expectText?: RegExp; allow?: RegExp[] }> = [
  { path: "/", role: "farmer" },
  { path: "/dashboard", role: "farmer" },
  { path: "/farm", role: "farmer", expectText: /E2E Green Acres/ },
  { path: "/farm/register", role: "farmer" },
  { path: "/farm/1", role: "farmer", expectText: /E2E Green Acres/ },
  { path: "/plots/create", role: "farmer" },
  { path: "/plots/analyze", role: "farmer" },
  { path: "/plots/compare", role: "farmer" },
  { path: "/crops/plan", role: "farmer" },
  { path: "/crops/plant", role: "farmer" },
  { path: "/crops/my-crops", role: "farmer", expectText: /Soybean/ },
  { path: "/strategy/select-farm", role: "farmer", expectText: /E2E Green Acres/ },
  { path: "/strategy/request", role: "farmer" },
  { path: "/strategy/results?farmId=1", role: "farmer" },
  { path: "/quota/history", role: "farmer" },
  { path: "/marketplace/buyer-dashboard", role: "buyer" },
  { path: "/livestock-marketplace", role: "buyer" },
  { path: "/marketplace", role: "buyer", expectText: /Soybean/ },
  { path: "/marketplace/1", role: "buyer", expectText: /Soybean/ },
  { path: "/marketplace/my-listings", role: "farmer", expectText: /Soybean/ },
  { path: "/marketplace/bookings", role: "buyer" },
  { path: "/marketplace/intelligence", role: "farmer" },
  { path: "/marketplace/supply-planning", role: "farmer" },
  { path: "/analytics/farm/1", role: "farmer" },
  { path: "/climate/hub", role: "farmer", allow: [/503 GET \/api\/v1\/weather\/forecast/, /status: 503/] },
  { path: "/soil/hub", role: "farmer" },
  { path: "/pest-disease/hub", role: "farmer" },
  { path: "/livestock/hub", role: "farmer", expectText: /Gir|cattle/i },
  { path: "/livestock/doctors", role: "farmer", expectText: /Dr\. E2E Vet/ },
  { path: "/transport/tracking", role: "farmer" },
  { path: "/notifications", role: "farmer" },
  { path: "/users/profile", role: "farmer", expectText: /E2E Farmer/ },
  { path: "/users/security", role: "farmer" },
  { path: "/admin/analytics", role: "admin" },
];

const ERROR_SCREEN = /something went wrong|failed to load|unexpected error|page not found|404/i;

for (const { path, role, expectText, allow } of PAGES) {
  test.describe(`${path} as ${role}`, () => {
    test.use({ storageState: authState(role) });

    test("loads without errors", async ({ page }) => {
      const problems = watchProblems(page);
      await page.goto(path);
      await settle(page);
      await expect(page.locator("body")).not.toHaveText(/^\s*$/);
      await expect.soft(page.getByText(ERROR_SCREEN).first(), "error screen shown").toBeHidden();
      // toContainText also covers data rendered inside <select> options, which never count as "visible".
      if (expectText) await expect.soft(page.locator("body"), "seeded data shown").toContainText(expectText);
      expectNoProblems(problems, allow);
    });
  });
}
