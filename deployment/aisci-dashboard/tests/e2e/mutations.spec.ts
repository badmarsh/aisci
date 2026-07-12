import { test, expect } from "@playwright/test";

test.describe("Global Mutations", () => {
  test("Run Ingest and Run Fits buttons should execute without crashing", async ({ page }) => {
    await page.goto("/");

    // Trigger Ingest
    const runIngestBtn = page.getByRole("button", { name: /Run Ingest/ });
    await expect(runIngestBtn).toBeEnabled();
    await runIngestBtn.click();

    // Wait for the mutation to finish (button returns to original text)
    await expect(page.getByRole("button", { name: "Run Ingest" })).toBeVisible();

    // Trigger Fits
    const runFitsBtn = page.getByRole("button", { name: /Run Fits/ });
    await expect(runFitsBtn).toBeEnabled();
    await runFitsBtn.click();
    await expect(page.getByRole("button", { name: "Run Fits" })).toBeVisible();
  });
});
