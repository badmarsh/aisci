import { test, expect } from "@playwright/test";

test.describe("Overview Page", () => {
  test("should load dynamic KPI cards and Activity feed", async ({ page }) => {
    await page.goto("/");

    // Verify KPIs
    await expect(page.locator("text=Papers Ingested")).toBeVisible();
    await expect(page.locator("text=Active Fits")).toBeVisible();
    await expect(page.locator("text=Claims Tracked")).toBeVisible();
    await expect(page.locator("text=Open Tasks")).toBeVisible();

    // Verify Recent Activity
    await expect(page.locator("text=Recent Activity")).toBeVisible();
    await expect(page.locator("ul.space-y-2")).toBeVisible();

    // Verify Chart
    await expect(page.locator(".recharts-responsive-container")).toBeVisible();
  });
});
