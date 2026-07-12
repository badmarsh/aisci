import { test, expect } from "@playwright/test";

test.describe("Physics Fits", () => {
  test("should filter models and show elements", async ({ page }) => {
    await page.route("**/api/projects/*/fits*", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ fitRows: [{ bin: "91-100", model: "Jüttner/Boltzmann 1c", raw_model: "juttner", chi2: 10, quality: "UNKNOWN", T: "1", beta: "1", aic: 1, bic: 1, status: "Converged", correlations: {}, runTimestamp: "now" }], chi2Series: [], compareSeries: null, bins: ["91-100"], runId: "test-run" }) }); });
    await page.goto("/projects/robert-boson-manuscript/fits");

    await expect(page.locator("text=Fit Results")).toBeVisible();

    // Check persistent structural warning
    await expect(page.locator("text=Jacobian Correction Required")).toBeVisible();

    // Check filters
    await expect(page.getByRole("button", { name: "Jüttner/Boltzmann 1c" })).toBeVisible();
  });
});
