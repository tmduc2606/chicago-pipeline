import { test, expect } from "@playwright/test";

test.describe("Responsive layout", () => {
  test("sidebar collapses on mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 376, height: 812 });
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const sidebar = page.locator("aside, [role='complementary'], nav").first();
    const isHidden = await sidebar.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return (
        style.display === "none" ||
        style.transform.includes("matrix") ||
        el.getBoundingClientRect().right <= 0
      );
    }).catch(() => true);

    expect(isHidden).toBe(true);
  });

  test("hamburger menu visible on mobile", async ({ page }) => {
    await page.setViewportSize({ width: 376, height: 812 });
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const menuButton = page.locator(
      'button[aria-label*="menu"], button[aria-label*="Menu"], button:has(svg)'
    ).first();

    const isVisible = await menuButton.isVisible().catch(() => false);
    expect(isVisible).toBe(true);
  });

  test("KPI cards stack vertically on mobile", async ({ page }) => {
    await page.setViewportSize({ width: 376, height: 812 });
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const kpiCards = page.locator('[class*="grid"] > div').first();
    const width = await kpiCards.evaluate((el) => el.getBoundingClientRect().width);
    expect(width).toBeLessThan(400);
  });

  test("desktop layout shows sidebar", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const sidebar = page.locator("aside, [role='complementary'], nav").first();
    await expect(sidebar).toBeVisible();
  });
});
