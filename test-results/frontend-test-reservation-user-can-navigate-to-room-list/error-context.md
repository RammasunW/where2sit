# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: frontend\test\reservation.spec.js >> user can navigate to room list
- Location: frontend\test\reservation.spec.js:3:5

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:8000/
Call log:
  - navigating to "http://127.0.0.1:8000/", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('user can navigate to room list', async ({ page }) => {
> 4  |   await page.goto('http://127.0.0.1:8000/');
     |              ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:8000/
  5  | 
  6  |   await page.getByRole('link', { name: /explore all rooms/i }).click();
  7  | 
  8  |   await expect(page).toHaveURL(/rooms/);
  9  | 
  10 |   await expect(page.locator('text=/room/i')).toBeVisible();
  11 | });
```