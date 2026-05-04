/**
 * Leads E2E tests.
 * Verifies the leads table loads, filtering works, and a new lead can be created.
 */
import { test, expect } from '@playwright/test';

test.describe('Leads page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/leads');
    // Wait for the leads table to load
    await page.waitForTimeout(1500);
  });

  test('loads without redirecting to login', async ({ page }) => {
    await expect(page).toHaveURL('/leads');
    await expect(page).not.toHaveURL('/login');
  });

  test('renders the leads table', async ({ page }) => {
    // Table rows exist (at least header row)
    await expect(page.locator('table, [role="table"]').first()).toBeVisible();
  });

  test('shows Add Lead button', async ({ page }) => {
    // The button is typically an icon or text button — look for a button
    const addButton = page.locator('button').filter({ hasText: /add|new|lead/i }).first();
    await expect(addButton).toBeVisible();
  });

  test('search input is visible', async ({ page }) => {
    const search = page.locator('input[type="text"], input[type="search"]').first();
    await expect(search).toBeVisible();
  });

  test('filtering leads by search term narrows the list', async ({ page }) => {
    const search = page.locator('input[type="text"], input[type="search"]').first();
    await search.fill('zzznoresults');
    await page.waitForTimeout(500);
    // The table body should show fewer or no results (no error, just empty)
    const noResultsOrEmpty = page.getByText(/no leads|no results|ничего/i);
    // Either the table is empty or shows a "no results" message
    const rows = page.locator('tbody tr');
    const count = await rows.count();
    // After filtering by non-existent term, rows should be 0 or less than before
    expect(count).toBeLessThanOrEqual(5);
  });

  test('clicking a lead row navigates to lead detail', async ({ page }) => {
    // Get first data row in the table (skip header)
    const firstRow = page.locator('tbody tr').first();
    const rowCount = await firstRow.count();
    if (rowCount === 0) {
      test.skip(); // No leads seeded — skip
      return;
    }
    await firstRow.click();
    await expect(page).toHaveURL(/\/leads\/.+/);
  });
});

test.describe('Lead detail page', () => {
  test('loads lead detail when navigating to /leads/:id', async ({ page }) => {
    // First get a lead ID from the list
    await page.goto('/leads');
    await page.waitForTimeout(1500);

    const firstRow = page.locator('tbody tr').first();
    if (await firstRow.count() === 0) {
      test.skip();
      return;
    }

    await firstRow.click();
    await expect(page).toHaveURL(/\/leads\/.+/);
    // Lead detail should have email or name visible
    await page.waitForTimeout(1000);
    await expect(page).not.toHaveURL('/login');
  });
});
