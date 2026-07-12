import { test, expect } from "@playwright/test";

test.describe("Task Queue & Agents", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/projects/*/tasks", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });
    await page.route("**/api/projects/*/agents", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { name: "FastAPI Backend", status: "ACTIVE", last: "now", summary: "", log: [] },
          { name: "Ingest Pipeline", status: "IDLE", last: "now", summary: "", log: [] },
          { name: "Fit Pipeline", status: "WAITING", last: "now", summary: "", log: [] },
        ]),
      });
    });
  });

  test("tasks should have tabs and agents should show logs", async ({ page }) => {
    // Tasks
    await page.goto("/projects/robert-boson-manuscript/tasks");
    await expect(page.getByRole("button", { name: /Active/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Blocked/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Proposed/i })).toBeVisible();

    // Agents
    await page.goto("/projects/robert-boson-manuscript/agents");
    await expect(page.locator("text=FastAPI Backend")).toBeVisible();
    await expect(page.locator("text=Ingest Pipeline")).toBeVisible();
    await expect(page.locator("text=Fit Pipeline")).toBeVisible();
  });
});
