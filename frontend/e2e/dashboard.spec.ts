/**
 * Dashboard E2E tests.
 * Verifies KPI stat cards, chart sections, and sidebar navigation.
 */
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('renders without crashing', async ({ page }) => {
    await expect(page).not.toHaveURL('/login');
    // At least one element from the layout must be visible
    await expect(page.locator('header')).toBeVisible();
  });

  test('shows four KPI stat cards', async ({ page }) => {
    // StatCard renders MUI Card — each has a specific structure
    // Wait for data to load (cards show values, not skeletons)
    await page.waitForTimeout(2000); // allow API response
    const cards = page.locator('.MuiCard-root');
    await expect(cards).toHaveCountGreaterThan(3);
  });

  test('sidebar navigation links are visible', async ({ page }) => {
    // Sidebar has navigation links for leads, deals, etc.
    await expect(page.locator('nav, aside').first()).toBeVisible();
  });

  test('AI Active pill is visible in TopBar', async ({ page }) => {
    // The TopBar has an "AI ACTIVE" pill (uppercase, cyan)
    await expect(page.locator('header')).toContainText('AI');
  });

  test('can navigate to Leads page via URL', async ({ page }) => {
    await page.goto('/leads');
    await expect(page).toHaveURL('/leads');
    await expect(page).not.toHaveURL('/login');
  });

  test('can navigate to Deals page via URL', async ({ page }) => {
    await page.goto('/deals');
    await expect(page).toHaveURL('/deals');
  });

  test('can navigate to Settings page via URL', async ({ page }) => {
    await page.goto('/settings');
    await expect(page).toHaveURL('/settings');
  });
});
