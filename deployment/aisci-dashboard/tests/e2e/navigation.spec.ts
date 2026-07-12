import { test, expect } from "@playwright/test";

test.describe("Dashboard Navigation", () => {
  test.beforeEach(async ({ page }) => {
    // Mock the specific project first so it takes precedence if globs overlap
    await page.route("**/api/projects/phd-audit", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
            id: "phd-audit",
            title: "PhD Audit — Literature Review",
            capabilities: ["evidence", "tasks", "literature"]
        }),
      });
    });

    await page.route("**/api/projects/robert-boson-manuscript", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
            id: "robert-boson-manuscript",
            title: "Robert — Boson probability function for the moving system",
            capabilities: ["evidence", "tasks", "literature", "symbolic_validation", "fit_validation", "reports"]
        }),
      });
    });

    // Mock the projects list (this will match exact `/api/projects`)
    await page.route("**/api/projects", async (route, request) => {
      if (request.url().endsWith("/api/projects")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            {
              id: "robert-boson-manuscript",
              title: "Robert — Boson probability function for the moving system",
              capabilities: ["evidence", "tasks", "literature", "symbolic_validation", "fit_validation", "reports"]
            },
            {
              id: "phd-audit",
              title: "PhD Audit — Literature Review",
              capabilities: ["evidence", "tasks", "literature"]
            }
          ]),
        });
      } else {
        route.fallback();
      }
    });
  });

  test("should navigate to all primary routes for robert-boson-manuscript", async ({ page }) => {
    await page.goto("/projects/robert-boson-manuscript");

    // Check Overview
    await expect(page).toHaveTitle(/AiSci — Autonomous Research System/);

    // Navigate to Literature
    await page.getByRole("link", { name: /Literature/i }).click();
    await expect(page).toHaveURL(/.*\/literature/);

    // Navigate to Physics Fits
    await page.getByRole("link", { name: /Physics Fits/i }).click();
    await expect(page).toHaveURL(/.*\/fits/);
  });

  test("should hide capabilities and deny access for phd-audit", async ({ page }) => {
    await page.goto("/projects/phd-audit");

    // Overview should load
    await expect(page).toHaveTitle(/AiSci — Autonomous Research System/);

    // Links to fits and anomalies should not exist
    await expect(page.getByRole("link", { name: /Physics Fits/i })).not.toBeVisible();
    await expect(page.getByRole("link", { name: /Anomalies/i })).not.toBeVisible();

    // Direct navigation should show capability denied state or redirect
    await page.goto("/projects/phd-audit/fits");
    
    // Check for an unavailable state or redirect back
    await expect(page.locator("text=not available").or(page.locator("text=Dashboard"))).toBeVisible();
  });
  
  test("portfolio selection test", async ({ page }) => {
    await page.goto("/");
    // Click project link
    await expect(page.locator("text=PhD Audit — Literature Review")).toBeVisible();
    await page.getByRole("link", { name: /PhD Audit — Literature Review/i }).click();
    await expect(page).toHaveURL(/.*\/projects\/phd-audit/);
  });
});
