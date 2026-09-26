import { chromium, FullConfig } from "@playwright/test";
import { execFileSync } from "child_process";
import * as fs from "fs";
import * as path from "path";
import { authState, PASSWORD, Role, USERS } from "./fixtures";

/**
 * 1. Rebuild + seed cropsense_e2e (skip with E2E_SKIP_RESET=1 to keep data between runs).
 * 2. Sign in each seeded user through the real sign-in page and save the session per role.
 */
export default async function globalSetup(config: FullConfig) {
  if (!process.env.E2E_SKIP_RESET) {
    execFileSync(path.join(__dirname, "..", "sandbox", "reset-db.sh"), { stdio: "inherit" });
  }

  fs.mkdirSync(path.join(__dirname, "..", ".auth"), { recursive: true });
  const baseURL = config.projects[0].use.baseURL!;
  const browser = await chromium.launch();

  try {
    for (const role of Object.keys(USERS) as Role[]) {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(`${baseURL}/auth/signin`);
      await page.getByPlaceholder("Enter your username").fill(USERS[role].username);
      await page.getByPlaceholder("Enter your password").fill(PASSWORD);
      await page.getByRole("button", { name: "Sign In", exact: true }).click();
      await page.waitForURL(/\/dashboard/, { timeout: 45_000 });
      await context.storageState({ path: authState(role) });
      await context.close();
      console.log(`  signed in as ${role}`);
    }
  } finally {
    await browser.close();
  }
}
