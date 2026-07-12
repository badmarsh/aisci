import { test, expect } from "@playwright/test";

test.describe("Evidence Ledger", () => {
  test("should display mapped statuses properly", async ({ page }) => {
    await page.goto("/evidence");

    // Make sure summary tabs render
    await expect(page.locator("text=Supported").first()).toBeVisible();
    await expect(page.locator("text=Sanity Checked").first()).toBeVisible();
    await expect(page.locator("text=Proposed").first()).toBeVisible();

    // Verify table renders
    await expect(page.locator("table")).toBeVisible();
  });
});
