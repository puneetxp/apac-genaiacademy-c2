import { test, expect, PASSWORD, USERS, authState } from "./fixtures";

test.describe("Sign in", () => {
  test("farmer signs in with username and lands on the dashboard", async ({ page }) => {
    await page.goto("/auth/signin");
    await page.getByPlaceholder("Enter your username").fill(USERS.farmer.username);
    await page.getByPlaceholder("Enter your password").fill(PASSWORD);
    await page.getByRole("button", { name: "Sign In", exact: true }).click();
    await expect(page).toHaveURL(/\/dashboard/);
    const token = await page.evaluate(() => localStorage.getItem("access_token"));
    expect(token).toBeTruthy();
  });

  test("signing in with an email address works", async ({ page }) => {
    await page.goto("/auth/signin");
    await page.getByPlaceholder("Enter your username").fill(USERS.buyer.email);
    await page.getByPlaceholder("Enter your password").fill(PASSWORD);
    await page.getByRole("button", { name: "Sign In", exact: true }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("wrong password shows an error and stays on sign-in", async ({ page }) => {
    await page.goto("/auth/signin");
    await page.getByPlaceholder("Enter your username").fill(USERS.farmer.username);
    await page.getByPlaceholder("Enter your password").fill("Wrong-Pass-123");
    await page.getByRole("button", { name: "Sign In", exact: true }).click();
    await expect(page.getByText(/sign in failed|invalid|incorrect/i).first()).toBeVisible();
    await expect(page).toHaveURL(/\/auth\/signin/);
  });

  test("unknown user shows an error", async ({ page }) => {
    await page.goto("/auth/signin");
    await page.getByPlaceholder("Enter your username").fill("nobody_here");
    await page.getByPlaceholder("Enter your password").fill(PASSWORD);
    await page.getByRole("button", { name: "Sign In", exact: true }).click();
    await expect(page.getByText(/sign in failed|not found|invalid/i).first()).toBeVisible();
  });

  test("protected pages send signed-out visitors to sign-in", async ({ page }) => {
    await page.goto("/farm");
    await expect(page).toHaveURL(/\/auth\/signin|\/$/);
  });
});

test.describe("Signed-in session", () => {
  test.use({ storageState: authState("farmer") });

  test("profile shows the signed-in farmer", async ({ page }) => {
    await page.goto("/users/profile");
    await expect(page.getByText("E2E Farmer").first()).toBeVisible();
  });
});
