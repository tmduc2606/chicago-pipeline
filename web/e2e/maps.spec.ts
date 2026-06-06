import { test, expect } from "@playwright/test";

test.describe("Maps", () => {
  test("choropleth map card is visible", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Choropleth by District")).toBeVisible();
    await expect(page.locator(".card").filter({ hasText: "Choropleth by District" })).toBeVisible({ timeout: 15000 });
  });

  test("cluster map card is visible", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Crime Clusters")).toBeVisible();
    await expect(page.locator(".card").filter({ hasText: "Crime Clusters" })).toBeVisible({ timeout: 15000 });
  });

  test("map legend is visible on locations page", async ({ page }) => {
    await page.goto("/locations");
    await expect(page.getByText("Choropleth: crime count by district")).toBeVisible();
    await expect(page.getByText("Clusters: individual crime locations")).toBeVisible();
  });

  test("both map cards render on dashboard", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Choropleth by District")).toBeVisible({ timeout: 15000 });
    await expect(page.getByText("Crime Clusters")).toBeVisible({ timeout: 15000 });
  });
});
