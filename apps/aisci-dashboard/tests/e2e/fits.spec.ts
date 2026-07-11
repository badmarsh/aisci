import { test, expect } from "@playwright/test";

test.describe("Physics Fits", () => {
  test("should filter models and show elements", async ({ page }) => {
    await page.goto("/fits");

    await expect(page.locator("text=Fit Results")).toBeVisible();

    // Check filters
    await expect(page.getByRole("button", { name: "Jüttner 1c" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Tsallis 2c" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Bose-Einstein 1c" })).toBeVisible();

    await page.getByRole("button", { name: "Jüttner 1c" }).click();
  });
});
