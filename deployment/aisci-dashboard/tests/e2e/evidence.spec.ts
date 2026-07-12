import { test, expect } from "@playwright/test";

test.describe("Evidence Ledger", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/projects/*/evidence/search*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: 1,
            claim: "Test",
            status: "Supported",
            nextGate: "Gate",
            run: "Run-1",
            narrative: "",
          },
          {
            id: 2,
            claim: "Test",
            status: "Sanity Checked",
            nextGate: "Gate",
            run: "Run-1",
            narrative: "",
          },
          {
            id: 3,
            claim: "Test",
            status: "Proposed",
            nextGate: "Gate",
            run: "Run-1",
            narrative: "",
          },
        ]),
      });
    });
  });

  test("should display mapped statuses properly", async ({ page }) => {
    await page.goto("/projects/robert-boson-manuscript/evidence");

    // Make sure summary tabs render
    await expect(page.locator("text=Supported").first()).toBeVisible();
    await expect(page.locator("text=Sanity Checked").first()).toBeVisible();
    await expect(page.locator("text=Proposed").first()).toBeVisible();

    // Verify table renders
    await expect(page.locator("table")).toBeVisible();
  });
});
