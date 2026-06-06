import { test, expect } from "@playwright/test";

test.describe("Locations page", () => {
  test("location search filters list", async ({ page }) => {
    await page.goto("/locations");
    await page.waitForTimeout(3000);
    const searchInput = page.getByPlaceholder("Search locations...");
    await expect(searchInput).toBeVisible();
    await searchInput.fill("STREET");
    await page.waitForTimeout(500);
    await expect(page.getByText("No locations match")).not.toBeVisible();
    await searchInput.fill("ZZZZNONEXISTENT");
    await page.waitForTimeout(500);
    await expect(page.getByText(/No locations match/)).toBeVisible();
  });
});
