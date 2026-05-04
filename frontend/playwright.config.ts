import { defineConfig, devices } from '@playwright/test';

/**
 * Base URL: defaults to Docker prod stack (http://localhost).
 * Override with PLAYWRIGHT_BASE_URL env var for dev server.
 *
 * Run against Docker:  docker compose -f docker-compose.prod.yml up -d
 * Run against dev:     PLAYWRIGHT_BASE_URL=http://localhost:5173 npx playwright test
 */
const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,       // sequential — tests share seeded DB state
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  timeout: 30_000,
  expect: { timeout: 8_000 },

  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],

  globalSetup: './e2e/global-setup.ts',

  use: {
    baseURL: BASE_URL,
    storageState: 'e2e/auth-state.json',  // logged-in session for all tests
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'off',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
