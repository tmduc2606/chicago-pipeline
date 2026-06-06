import { test, expect } from "@playwright/test";

test.describe("Dashboard page", () => {
  test("loads and shows heading", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Dashboard", exact: true })).toBeVisible();
  });

  test("KPI cards display formatted values", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("57,931").first()).toBeVisible({ timeout: 15000 });
    await expect(page.getByText("Total Crimes").first()).toBeVisible();
  });

  test("about section is collapsible", async ({ page }) => {
    await page.goto("/");
    const button = page.getByText("About this dashboard");
    await expect(button).toBeVisible();
    await button.click();
    await expect(page.getByText("This dashboard visualizes synthetic Chicago crime data")).toBeVisible();
    await button.click();
    await expect(page.getByText("This dashboard visualizes synthetic Chicago crime data")).not.toBeVisible();
  });

  test("timeseries chart renders SVG", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Daily Crime Trend")).toBeVisible();
    const chart = page.locator(".recharts-responsive-container").first();
    await expect(chart).toBeVisible({ timeout: 15000 });
  });

  test("heatmap renders canvas", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Crimes by Hour of Day")).toBeVisible();
    const canvas = page.locator("canvas").first();
    await expect(canvas).toBeVisible({ timeout: 15000 });
  });

  test("offense bar chart shows bars", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Top Crime Types")).toBeVisible();
    const bars = page.locator(".recharts-bar-rectangle");
    await expect(bars.first()).toBeVisible({ timeout: 15000 });
  });
});
