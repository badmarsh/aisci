import { test, expect } from '@playwright/test';

test.describe('Task Queue & Agents', () => {
  test('tasks should have tabs and agents should show logs', async ({ page }) => {
    // Tasks
    await page.goto('/tasks');
    await expect(page.getByRole('tab', { name: /Active/ })).toBeVisible();
    await expect(page.getByRole('tab', { name: /Blocked/ })).toBeVisible();
    await expect(page.getByRole('tab', { name: /Agent-Proposed/ })).toBeVisible();
    
    // Agents
    await page.goto('/agents');
    await expect(page.locator('text=FastAPI Backend')).toBeVisible();
    await expect(page.locator('text=Ingest Pipeline')).toBeVisible();
    await expect(page.locator('text=Fit Pipeline')).toBeVisible();
  });
});
