import { test, expect } from '@playwright/test';

test.describe('Dashboard Navigation', () => {
  test('should navigate to all primary routes from sidebar', async ({ page }) => {
    await page.goto('/');
    
    // Check Overview
    await expect(page).toHaveTitle(/Overview/);
    
    // Navigate to Literature
    await page.getByRole('link', { name: /Literature/i }).click();
    await expect(page).toHaveTitle(/Literature/);
    
    // Navigate to Physics Fits
    await page.getByRole('link', { name: /Physics Fits/i }).click();
    await expect(page).toHaveTitle(/Physics Fits/);
    
    // Navigate to Evidence Ledger
    await page.getByRole('link', { name: /Evidence Ledger/i }).click();
    await expect(page).toHaveTitle(/Evidence Ledger/);
    
    // Navigate to Task Queue
    await page.getByRole('link', { name: /Task Queue/i }).click();
    await expect(page).toHaveTitle(/Task Queue/);
    
    // Navigate to Agents
    await page.getByRole('link', { name: /Agents/i }).click();
    await expect(page).toHaveTitle(/Agents/);
  });
});
