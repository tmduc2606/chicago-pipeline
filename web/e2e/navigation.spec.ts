import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
  test("navigate to Crime Types page", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Crime Types" }).click();
    await expect(page).toHaveURL("/crime-types");
    await expect(page.getByRole("heading", { name: "Crime Types", exact: true })).toBeVisible();
  });

  test("navigate to Locations page", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Locations" }).click();
    await expect(page).toHaveURL("/locations");
    await expect(page.getByRole("heading", { name: "Locations", exact: true })).toBeVisible();
  });

  test("navigate to Analysis page", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Analysis" }).click();
    await expect(page).toHaveURL("/analysis");
    await expect(page.getByRole("heading", { name: "Analysis", exact: true })).toBeVisible();
  });
});
