import { test, expect } from "@playwright/test";

test.describe("Filters", () => {
  test("sidebar filters apply date range", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2000);
    const dateInput = page.locator('input[type="date"]').first();
    await dateInput.fill("2025-01-01");
    await page.waitForTimeout(1000);
    await expect(page.getByText("From: 2025-01-01")).toBeVisible();
  });

  test("quick-select buttons change date range", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2000);
    const btn30 = page.getByRole("button", { name: "30 days" });
    await expect(btn30).toBeVisible();
    await btn30.click();
    await page.waitForTimeout(1000);
    await expect(page.getByText(/From:/)).toBeVisible();
  });

  test("URL params update when filters change", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2000);
    const dateInput = page.locator('input[type="date"]').first();
    await dateInput.fill("2025-06-01");
    await page.waitForTimeout(1000);
    await expect(page).toHaveURL(/from_date=2025-06-01/);
  });

  test("reset button clears all filters", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2000);
    const dateInput = page.locator('input[type="date"]').first();
    await dateInput.fill("2025-01-01");
    await page.waitForTimeout(1000);
    const resetBtn = page.getByRole("button", { name: "Reset" });
    await resetBtn.click();
    await page.waitForTimeout(1000);
    await expect(page).not.toHaveURL(/from_date/);
  });
});
