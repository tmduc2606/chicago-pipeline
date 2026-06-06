import { test, expect } from "@playwright/test";

test.describe("Crime Types page", () => {
  test("crime types table sorts by column", async ({ page }) => {
    await page.goto("/crime-types");
    await page.waitForTimeout(3000);
    const typeHeader = page.locator("th").filter({ hasText: "Type" });
    await expect(typeHeader).toBeVisible();
    await typeHeader.click();
    await page.waitForTimeout(500);
    const countHeader = page.locator("th").filter({ hasText: "Count" });
    await expect(countHeader).toBeVisible();
    await countHeader.click();
    await page.waitForTimeout(500);
  });

  test("Top 3 summary displays", async ({ page }) => {
    await page.goto("/crime-types");
    await page.waitForTimeout(3000);
    await expect(page.getByText("Top 3 Crime Types")).toBeVisible();
  });
});
