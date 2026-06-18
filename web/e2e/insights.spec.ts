import { test, expect } from "@playwright/test";

test.describe("Insights Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/insights");
    await page.waitForLoadState("networkidle");
  });

  test("page loads with heading", async ({ page }) => {
    await expect(page.locator("h2", { hasText: "Insights" })).toBeVisible();
  });

  test("14 insight cards render", async ({ page }) => {
    const cards = page.locator("h3").filter({ hasText: /^(Arrest|Domestic|Hotspot|Month|District|Location|Crime|Neighborhood|Correlation)/ });
    await expect(cards).toHaveCount(14);
  });

  test("topic filter buttons work", async ({ page }) => {
    await expect(page.locator("button", { hasText: "All" })).toBeVisible();
    await expect(page.locator("button", { hasText: "temporal" })).toBeVisible();
    await expect(page.locator("button", { hasText: "spatial" })).toBeVisible();
    await expect(page.locator("button", { hasText: "categorical" })).toBeVisible();
    await expect(page.locator("button", { hasText: "relational" })).toBeVisible();
  });

  test("filtering by topic reduces card count", async ({ page }) => {
    const allCards = page.locator("h3").filter({ hasText: /^(Arrest|Domestic|Hotspot|Month|District|Location|Crime|Neighborhood|Correlation)/ });
    const totalCount = await allCards.count();
    expect(totalCount).toBe(14);

    // Click "temporal" filter
    await page.locator("button", { hasText: "temporal" }).click();
    await page.waitForTimeout(500);

    const filteredCount = await allCards.count();
    expect(filteredCount).toBeLessThan(totalCount);
  });

  test("tag dropdown works", async ({ page }) => {
    const tagSelect = page.locator("combobox").first();
    await expect(tagSelect).toBeVisible();
  });

  test("difficulty range selector works", async ({ page }) => {
    const difficultyFrom = page.locator("combobox").nth(1);
    const difficultyTo = page.locator("combobox").nth(2);
    await expect(difficultyFrom).toBeVisible();
    await expect(difficultyTo).toBeVisible();
  });

  test("insight cards have More buttons", async ({ page }) => {
    const moreButtons = page.locator("button", { hasText: "More" });
    await expect(moreButtons).toHaveCount(14);
  });

  test("Data Notes section present", async ({ page }) => {
    await expect(page.locator("h3", { hasText: "Data Notes" })).toBeVisible();
  });
});
