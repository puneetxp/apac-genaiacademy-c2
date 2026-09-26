import { test as base, expect, Page, APIRequestContext, request } from "@playwright/test";
import * as path from "path";

export const BACKEND = `http://localhost:${process.env.E2E_BACKEND_PORT || 8100}`;
export const API = `${BACKEND}/api/v1`;
export const PASSWORD = process.env.E2E_PASSWORD || "E2e-Test-Pass1!";

export const USERS = {
  farmer: { id: 1, username: "e2e_farmer", email: "e2e.farmer@example.com" },
  buyer: { id: 2, username: "e2e_buyer", email: "e2e.buyer@example.com" },
  admin: { id: 3, username: "e2e_admin", email: "e2e.admin@example.com" },
} as const;
export type Role = keyof typeof USERS;

export const authState = (role: Role) => path.join(__dirname, "..", ".auth", `sandbox-${role}.json`);

/** Bearer token the e2e backend accepts for a seeded user (mock auth, E2E mode only). */
export const tokenFor = (role: Role) => `mock-token-${USERS[role].email}`;

export async function apiAs(role: Role | null): Promise<APIRequestContext> {
  return request.newContext({
    baseURL: API + "/",
    extraHTTPHeaders: role ? { Authorization: `Bearer ${tokenFor(role)}` } : {},
  });
}

export interface PageProblems {
  pageErrors: string[];
  consoleErrors: string[];
  failedApi: string[];
}

/**
 * Records uncaught exceptions, console errors and failing API calls (4xx/5xx/network) for a page,
 * so a spec can assert the page actually works rather than just rendering a shell.
 */
export function watchProblems(page: Page): PageProblems {
  const problems: PageProblems = { pageErrors: [], consoleErrors: [], failedApi: [] };
  page.on("pageerror", (err) => problems.pageErrors.push(err.message));
  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const text = msg.text();
    // Noise that doesn't indicate a broken feature in the sandbox.
    if (/favicon|Download the .* DevTools|service worker|ServiceWorker|manifest|net::ERR_ABORTED|Failed to load resource/i.test(text)) return;
    problems.consoleErrors.push(text.slice(0, 300));
  });
  page.on("response", (res) => {
    const url = res.url();
    if (!url.startsWith(BACKEND) || res.status() < 400) return;
    problems.failedApi.push(`${res.status()} ${res.request().method()} ${url.replace(BACKEND, "")}`);
  });
  page.on("requestfailed", (req) => {
    if (req.url().startsWith(BACKEND) && req.failure()?.errorText !== "net::ERR_ABORTED") {
      problems.failedApi.push(`FAILED ${req.method()} ${req.url().replace(BACKEND, "")} ${req.failure()?.errorText}`);
    }
  });
  return problems;
}

export function expectNoProblems(p: PageProblems, allow: RegExp[] = []) {
  const keep = (list: string[]) => list.filter((x) => !allow.some((re) => re.test(x)));
  expect.soft(keep(p.pageErrors), "uncaught page errors").toEqual([]);
  expect.soft(keep(p.failedApi), "failed API calls").toEqual([]);
  expect.soft(keep(p.consoleErrors), "console errors").toEqual([]);
}

/** Wait for in-flight API calls to settle after navigation. */
export async function settle(page: Page) {
  await page.waitForLoadState("networkidle", { timeout: 20_000 }).catch(() => {});
}

export const test = base.extend<{ role: Role }>({
  role: ["farmer", { option: true }],
});
export { expect };
