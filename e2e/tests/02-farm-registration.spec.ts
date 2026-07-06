import { expect, test } from "@playwright/test";

/**
 * Farm Registration Test
 * Demonstrates: Farm setup with geolocation and AI-powered features
 * Note: Uses shared authentication from global-setup.ts
 */

test.describe("Farm Registration with AI Features", () => {
  test("Register farm with geolocation capture", async ({ page }) => {
    console.log("🎬 Starting farm registration test...");

    await test.step("Navigate to farm registration", async () => {
      await page.goto("/farm/register");
      // Wait for the page to load by checking for a unique element
      await expect(page.getByRole("heading", { name: /register.*farm/i }))
        .toBeVisible();
    });

    await test.step("Fill farm basic details", async () => {
      await page.fill('input[name="farm_name"]', "Green Valley Farm");
      await page.fill('input[name="total_area_acres"]', "5.5");
      await page.waitForTimeout(500);
    });

    await test.step("Capture geolocation (optional)", async () => {
      // Grant geolocation permission
      await page.context().grantPermissions(["geolocation"]);
      await page.context().setGeolocation({
        latitude: 28.4595,
        longitude: 77.0266,
      });

      // Try to capture location if button exists
      const captureButton = page.locator('button:has-text("Capture")');
      if (await captureButton.isVisible({ timeout: 2000 }).catch(() => false)) {
        await captureButton.click();
        await page.waitForTimeout(1000);
        console.log("✓ Geolocation capture attempted");
      } else {
        console.log("⚠ Geolocation capture button not found, skipping");
      }
    });

    await test.step("Fill farm address with pincode lookup", async () => {
      // Fill pincode and wait for lookup
      await page.fill('input[name="pincode"]', "122001");

      // Wait for pincode lookup to complete
      await page.waitForTimeout(3000);

      // Check if state and district were auto-filled
      const state = await page.inputValue('input[name="state"]');
      const district = await page.inputValue('input[name="district"]');
      console.log(`✓ Pincode lookup: ${state}, ${district}`);

      // Fill village - using input instead of select
      const villageInput = page.locator('input[name="village"]');
      await villageInput.waitFor({ state: "visible", timeout: 5000 });
      await villageInput.fill("Test Village");
      await page.keyboard.press('Escape'); // to close dropdown
      console.log("✓ Village filled");

      // Fill optional address line
      await page.fill('input[name="address_line"]', "Plot 45");
      await page.waitForTimeout(500);
    });

    await test.step("Submit farm registration", async () => {
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);

      // Check for either success or error message
      const successVisible = await page.locator(
        "text=Farm registered successfully",
      ).isVisible().catch(() => false);
      const errorVisible = await page.locator(".bg-red-50.text-red-800").isVisible().catch(
        () => false
      );

      if (errorVisible) {
        const errorText = await page.locator(".bg-red-50.text-red-800").textContent();
        console.log("❌ Error message found:", errorText);
      }

      if (!successVisible && !errorVisible) {
        console.log(
          "⚠ Neither success nor error message found - checking page state...",
        );
        const pageContent = await page.content();
        console.log("Page title:", await page.title());

        // Take a screenshot for debugging
        await page.screenshot({
          path: "test-results/farm-registration-debug.png",
        });
      }

      // Should show success message with longer timeout
      await expect(page.locator("text=Farm registered successfully"))
        .toBeVisible({ timeout: 10000 });
      await page.waitForTimeout(1000);
    });
  });
});
