/**
 * Global setup: logs in once with admin credentials, saves session to
 * e2e/auth-state.json (localStorage + cookies). All test files reuse
 * this state via playwright.config.ts → use.storageState.
 *
 * Requires the app to be running at the configured BASE_URL.
 * Seeded credentials: admin@example.com / admin123
 */
import { chromium, type FullConfig } from '@playwright/test';

export default async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto(`${baseURL}/login`);
  await page.locator('input[type="email"]').fill('admin@example.com');
  await page.locator('input[type="password"]').fill('admin123');
  await page.locator('button[type="submit"]').click();

  // Wait for redirect to dashboard
  await page.waitForURL(`${baseURL}/`, { timeout: 15_000 });

  // Persist localStorage (JWT token) + cookies for all test contexts
  await context.storageState({ path: 'e2e/auth-state.json' });
  await browser.close();
}
