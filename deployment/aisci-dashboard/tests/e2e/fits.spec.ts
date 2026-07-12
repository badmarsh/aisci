import { test, expect } from "@playwright/test";

test.describe("Physics Fits", () => {
  test.beforeEach(async ({ page }) => {
    // Mock the runs list endpoint
    await page.route("**/api/projects/*/fits/runs", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ runs: ["test-run", "incomplete-run"] }),
      });
    });

    // Mock the fit data endpoint
    await page.route("**/api/projects/*/fits*", async (route, request) => {
      if (!request.url().includes("/runs")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            fitRows: [
              {
                bin: "91-100",
                model: "Jüttner/Boltzmann 1c",
                raw_model: "juttner",
                chi2: 10,
                quality: "UNKNOWN",
                T: "1",
                beta: "1",
                status: "Converged",
              },
              {
                bin: "91-100",
                model: "Tsallis-Pareto 1c",
                raw_model: "tsallis",
                chi2: 2.5,
                quality: "GOOD",
                T: "1.2",
                beta: "0.8",
                status: "Incomplete",
              }
            ],
            chi2Series: [],
            compareSeries: null,
            bins: ["91-100"],
            runId: "test-run",
          }),
        });
      } else {
        route.fallback();
      }
    });
  });

  test("should filter models and show elements", async ({ page }) => {
    await page.goto("/projects/robert-boson-manuscript/fits");

    await expect(page.locator("text=Fit Results").first()).toBeVisible();

    // Check persistent structural warning
    await expect(page.locator("text=Jacobian Correction Required").first()).toBeVisible();

    // Check filters
    await expect(page.getByRole("button", { name: "Jüttner/Boltzmann 1c" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Tsallis-Pareto 1c" })).toBeVisible();
    
    // Incomplete status logic check
    await expect(page.locator("text=Incomplete").first()).toBeVisible();
  });
});
