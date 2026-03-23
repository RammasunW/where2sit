import { test, expect } from '@playwright/test';

test('app loads and displays Room List', async ({ page }) => {
  await page.goto('http://localhost:8000');
  await expect(page.locator('text=Room List')).toBeVisible();
});