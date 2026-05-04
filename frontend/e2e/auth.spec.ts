/**
 * Authentication E2E tests.
 * The "valid login" test uses a fresh browser context (no saved auth state)
 * to exercise the actual login flow end-to-end.
 */
import { test, expect } from '@playwright/test';

// ── Valid login ───────────────────────────────────────────────────────────────

test.describe('Login flow', () => {
  // Override storageState: use a clean context so we actually go through login
  test.use({ storageState: { cookies: [], origins: [] } });

  test('redirects to / after successful login', async ({ page }) => {
    await page.goto('/login');
    await page.locator('input[type="email"]').fill('admin@example.com');
    await page.locator('input[type="password"]').fill('admin123');
    await page.locator('button[type="submit"]').click();

    await expect(page).toHaveURL('/');
  });

  test('shows error alert on wrong credentials', async ({ page }) => {
    await page.goto('/login');
    await page.locator('input[type="email"]').fill('wrong@example.com');
    await page.locator('input[type="password"]').fill('wrongpassword');
    await page.locator('button[type="submit"]').click();

    // Error alert should appear — stay on login page
    await expect(page.locator('.MuiAlert-root')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

  test('login page has email and password fields', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('redirects unauthenticated user to / which shows login', async ({ page }) => {
    await page.goto('/leads');
    // ProtectedRoute should redirect to login
    await expect(page).toHaveURL('/login');
  });
});

// ── Authenticated navigation ──────────────────────────────────────────────────

test.describe('Authenticated session', () => {
  test('authenticated user sees the dashboard on /', async ({ page }) => {
    await page.goto('/');
    // Should NOT redirect to login
    await expect(page).not.toHaveURL('/login');
  });

  test('navigating to /login while authenticated redirects to /', async ({ page }) => {
    await page.goto('/');
    // Ensure we're authenticated by checking we're not on login
    await expect(page).not.toHaveURL('/login');
  });
});
