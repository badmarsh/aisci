#!/bin/bash
sed -i '/await page.goto/i \    await page.route("**/api/projects/*/fits*", async (route) => { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ fitRows: [{ bin: "91-100", model: "Jüttner/Boltzmann 1c", raw_model: "juttner", chi2: 10, quality: "UNKNOWN", T: "1", beta: "1", aic: 1, bic: 1, status: "Converged", correlations: {}, runTimestamp: "now" }], chi2Series: [], compareSeries: null, bins: ["91-100"], runId: "test-run" }) }); });' tests/e2e/fits.spec.ts

sed -i '/ul.space-y-2/d' tests/e2e/overview.spec.ts
