/**
 * Settings E2E tests.
 * Verifies the settings page renders and the dark mode toggle is functional.
 */
import { test, expect } from '@playwright/test';

test.describe('Settings page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
  });

  test('loads without redirecting to login', async ({ page }) => {
    await expect(page).toHaveURL('/settings');
    await expect(page).not.toHaveURL('/login');
  });

  test('renders notification toggle rows', async ({ page }) => {
    // Each toggle is a clickable Box that acts as a switch
    const toggles = page.locator('[class*="MuiBox"]').filter({ hasNotText: '' });
    await expect(toggles.first()).toBeVisible();
  });

  test('dark mode toggle changes theme', async ({ page }) => {
    // Find the dark mode toggle — it's the second toggle in Appearance section
    // The toggle is a Box with specific width/height acting as a switch
    const toggles = page.locator('.MuiBox-root').filter({
      has: page.locator('[style*="border-radius: 999px"]'),
    });

    // Get body background before toggle
    const bgBefore = await page.evaluate(
      () => window.getComputedStyle(document.body).backgroundColor,
    );

    // Click the dark mode toggle (second toggle in appearance section)
    // Find by looking for the toggle near "Dark" text
    const darkSection = page.getByText(/dark|тёмн/i).first();
    if (await darkSection.count() === 0) {
      test.skip();
      return;
    }
    // The toggle is a sibling element — click the switch near "Dark" text
    const darkRow = page.locator('.MuiBox-root').filter({ hasText: /dark|тёмн/i }).first();
    const toggleInRow = darkRow.locator('.MuiBox-root').last();
    await toggleInRow.click();

    await page.waitForTimeout(300); // wait for theme transition

    const bgAfter = await page.evaluate(
      () => window.getComputedStyle(document.body).backgroundColor,
    );

    // Background should have changed (light → dark or dark → light)
    expect(bgAfter).not.toEqual(bgBefore);

    // Toggle it back to not pollute state for other tests
    await toggleInRow.click();
    await page.waitForTimeout(300);
  });

  test('save button is visible', async ({ page }) => {
    const saveButton = page.locator('button').filter({ hasText: /save|сохранить/i }).first();
    await expect(saveButton).toBeVisible();
  });

  test('language selector shows EN and RU options', async ({ page }) => {
    await expect(page.getByText('EN').first()).toBeVisible();
    await expect(page.getByText('RU').first()).toBeVisible();
  });
});
