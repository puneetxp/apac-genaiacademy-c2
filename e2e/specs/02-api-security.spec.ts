import { test, expect, apiAs } from "./fixtures";

/**
 * API-level access rules. These run without a browser and are the regression guard for the
 * 2026-09-26 finding that /api/v1/isuper/* was readable by anyone.
 */
test.describe("Generated CRUD access control", () => {
  test("admin tables need a signed-in admin", async () => {
    const anon = await apiAs(null);
    expect((await anon.get("isuper/user/")).status()).toBe(401);

    const farmer = await apiAs("farmer");
    expect((await farmer.get("isuper/user/")).status()).toBe(403);

    const admin = await apiAs("admin");
    const res = await admin.get("isuper/user/");
    expect(res.status()).toBe(200);
    expect((await res.json()).length).toBeGreaterThanOrEqual(3);
  });

  test("signed-in tables need a login", async () => {
    const anon = await apiAs(null);
    expect((await anon.get("islogin/farm/")).status()).toBe(401);
  });

  test("a user only sees their own rows in signed-in tables", async () => {
    const buyer = await apiAs("buyer");
    const farms = await (await buyer.get("islogin/farm/")).json();
    expect(Array.isArray(farms) ? farms : farms.items ?? []).toHaveLength(0);

    const farmer = await apiAs("farmer");
    const own = await (await farmer.get("islogin/farm/")).json();
    expect((Array.isArray(own) ? own : own.items).length).toBeGreaterThan(0);
  });

  test("a user cannot read, edit or delete someone else's row by id", async () => {
    const farmer = await apiAs("farmer");
    const farm = await (await farmer.get("islogin/farm/1")).json();
    expect(farm.name).toBe("E2E Green Acres");

    const buyer = await apiAs("buyer");
    expect((await buyer.get("islogin/farm/1")).status()).toBe(404);
    expect((await buyer.put("islogin/farm/1", { data: { ...farm, name: "hijacked" } })).status()).toBe(404);
    expect((await buyer.delete("islogin/farm/1")).status()).toBe(404);
    expect((await (await farmer.get("islogin/farm/1")).json()).name).toBe("E2E Green Acres");
  });

  test("scoping follows parent chains (crop -> plot -> farm)", async () => {
    const buyer = await apiAs("buyer");
    expect(await (await buyer.get("islogin/crop/")).json()).toHaveLength(0);
    expect((await buyer.get("islogin/crop/1")).status()).toBe(404);
    const farmer = await apiAs("farmer");
    const crops = await (await farmer.get("islogin/crop/")).json();
    expect(crops.map((c: any) => c.crop_name)).toContain("Soybean");
  });

  test("create stamps the signed-in user as owner", async () => {
    const buyer = await apiAs("buyer");
    const res = await buyer.post("islogin/farm/", {
      data: { name: "Buyer Test Farm", location_state: "Maharashtra", location_district: "Mumbai",
              total_area: 1, user_id: 1, owner_id: 1 },
    });
    expect(res.status()).toBe(201);
    const farm = await res.json();
    expect(farm.user_id).toBe(2);
    expect(farm.owner_id).toBe(2);
    expect((await buyer.delete(`islogin/farm/${farm.id}`)).status()).toBe(200);
  });

  test("cannot attach a row to someone else's parent", async () => {
    const buyer = await apiAs("buyer");
    const res = await buyer.post("islogin/farm_plot/", {
      data: { farm_id: 1, plot_name: "Sneaky", area: 1, soil_type: "black", irrigation_type: "drip",
              state: "Maharashtra", district: "Pune" },
    });
    expect(res.status()).toBe(404);
  });

  test("public tables stay open", async () => {
    const anon = await apiAs(null);
    const res = await anon.get("marketplace/listings");
    expect(res.status()).toBe(200);
  });
});

test.describe("Admin-only and self-only custom endpoints", () => {
  test("quota reset and limits need an admin", async () => {
    const farmer = await apiAs("farmer");
    expect((await farmer.post("ai-quota/reset")).status()).toBe(403);
    expect((await farmer.put("ai-quota/limit/1?new_limit=999")).status()).toBe(403);
    const admin = await apiAs("admin");
    expect((await admin.get("ai-quota/statistics")).status()).not.toBe(403);
  });

  test("a user can only read their own quota", async () => {
    const farmer = await apiAs("farmer");
    expect((await farmer.get("ai-quota/status/1")).status()).not.toBe(403);
    expect((await farmer.get("ai-quota/status/2")).status()).toBe(403);
  });

  test("analytics for another farmer or farm are refused", async () => {
    const buyer = await apiAs("buyer");
    expect((await buyer.get("analytics/farmer/1")).status()).toBe(403);
    expect((await buyer.get("analytics/farm/1")).status()).toBe(404);
    expect((await buyer.get("analytics/platform")).status()).toBe(403);
  });

  test("market data collection is admin-only", async () => {
    const farmer = await apiAs("farmer");
    expect((await farmer.post("market-intelligence/collect/listing/1")).status()).toBe(403);
  });
});

test.describe("Custom endpoints that change data need auth", () => {
  const writes: Array<[string, string]> = [
    ["post", "ai-quota/reset"],
    ["delete", "upload/photo/x.png"],
    ["post", "model-training/deploy-model"],
    ["post", "market-intelligence/collect/listing/1"],
    ["post", "livestock-transactions"],
    ["post", "transport/bookings"],
  ];
  for (const [method, url] of writes) {
    test(`${method.toUpperCase()} /${url} rejects anonymous callers`, async () => {
      const anon = await apiAs(null);
      const res = await (anon as any)[method](url, method === "delete" ? {} : { data: {} });
      expect([401, 403]).toContain(res.status());
    });
  }
});
