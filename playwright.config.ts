import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: 'http://127.0.0.1:8000',
  },
  webServer: {
    command: 'python manage.py runserver',
    url: 'http://127.0.0.1:8000',
    reuseExistingServer: !process.env.CI,
  },
});