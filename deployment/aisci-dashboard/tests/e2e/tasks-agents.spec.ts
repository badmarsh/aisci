import { test, expect } from "@playwright/test";

test.describe("Task Queue, Agents & Jobs", () => {
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
    await page.route("**/api/projects/*/jobs", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { pipeline_id: "ingest", status: "completed", created_at: "now", exit_code: 0 },
          { pipeline_id: "fit", status: "failed", created_at: "now", exit_code: 1 },
          { pipeline_id: "report", status: "running", created_at: "now", exit_code: null },
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
    
    // Jobs
    await page.goto("/projects/robert-boson-manuscript/jobs");
    await expect(page.locator("text=completed").first()).toBeVisible();
    await expect(page.locator("text=failed").first()).toBeVisible();
    await expect(page.locator("text=running").first()).toBeVisible();
  });
});
