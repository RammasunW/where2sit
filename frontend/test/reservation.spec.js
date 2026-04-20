import { test, expect } from '@playwright/test';

test('user can navigate to room list', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('link', { name: /explore all rooms/i }).click();

  await expect(page).toHaveURL(/rooms/);

  await expect(page.locator('text=/room/i')).toBeVisible();
});