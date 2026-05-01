const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './test',
  use: {
    baseURL: 'http://127.0.0.1:3000',
  },
  webServer: {
    command: 'python ../manage.py runserver 3000',
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
