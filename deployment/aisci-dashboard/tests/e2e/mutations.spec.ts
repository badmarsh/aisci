import { test, expect } from "@playwright/test";

test.describe("Global Mutations", () => {
  test.beforeEach(async ({ page }) => {
    // Mock the backend mutation endpoints to avoid spawning real jobs during E2E
    await page.route("**/api/ingest*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ message: "Mocked ingest job started", job_id: "mock-ingest-123" }),
      });
    });

    await page.route("**/api/fits/run*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ message: "Mocked fit job started", job_id: "mock-fit-456" }),
      });
    });
  });

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
