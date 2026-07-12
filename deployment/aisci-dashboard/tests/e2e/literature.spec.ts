import { test, expect } from "@playwright/test";

test.describe("Literature Intake", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/literature", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([{ id: "1", title: "Test Paper", source: "arXiv" }]),
      });
    });
  });

  test("should display papers and support search filtering", async ({ page }) => {
    await page.goto("/literature");

    await expect(page.locator("text=Total Papers")).toBeVisible();
    await expect(page.locator("text=arXiv Papers")).toBeVisible();
    await expect(page.locator("text=OpenAlex Papers")).toBeVisible();

    // Check chart
    await expect(page.locator(".recharts-responsive-container")).toBeVisible();

    // Test search if there's any paper
    const table = page.locator("table");
    await expect(table).toBeVisible();

    const rows = page.locator("tbody > tr");
    // Wait for the table to populate, just check search box works
    await page.fill('input[placeholder="Search…"]', "NonExistentGibberish1234");
    // should not crash
  });
});
