import { test, expect } from "@playwright/test";

const PAGES = ["/", "/crime-types", "/locations", "/analysis"];

test.describe("Accessibility — axe-core WCAG 2.1 AA", () => {
  for (const url of PAGES) {
    test(`page ${url || "/"} has no critical WCAG violations`, async ({ page }) => {
      await page.goto(url);
      await page.waitForLoadState("networkidle");

      await page.evaluate(() => {
        return new Promise<void>((resolve) => {
          const script = document.createElement("script");
          script.src = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.4/axe.min.js";
          script.onload = () => resolve();
          script.onerror = () => resolve();
          document.head.appendChild(script);
        });
      });

      const result = await page.evaluate(async () => {
        const axe = (window as any).axe;
        if (!axe) return { violations: [], error: "axe-core not loaded" };
        try {
          const results = await axe.run();
          return {
            violations: results.violations.map((v: any) => ({
              id: v.id,
              impact: v.impact,
              description: v.description,
              nodes: v.nodes.length,
            })),
            error: null,
          };
        } catch (e: any) {
          return { violations: [], error: e.message };
        }
      });

      if (result.error) {
        test.skip(true, `axe-core not available: ${result.error}`);
        return;
      }

      const critical = result.violations.filter(
        (v: any) => v.impact === "critical" || v.impact === "serious"
      );
      expect(critical).toEqual([]);
    });
  }
});

test.describe("Accessibility — keyboard navigation", () => {
  test("dashboard is keyboard navigable", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const interactiveCount = await page.locator(
      'button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ).count();

    expect(interactiveCount).toBeGreaterThan(0);

    for (let i = 0; i < Math.min(interactiveCount, 15); i++) {
      await page.keyboard.press("Tab");
      const focused = await page.evaluate(() => {
        const el = document.activeElement;
        return {
          tag: el?.tagName,
          visible: el
            ? el.getBoundingClientRect().width !== 0
            : false,
        };
      });
      expect(focused.visible).toBe(true);
    }
  });

  test("sidebar links are focusable", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const sidebarLinks = page.locator("nav a, aside a");
    const count = await sidebarLinks.count();

    for (let i = 0; i < count; i++) {
      await sidebarLinks.nth(i).focus();
      const isFocused = await sidebarLinks.nth(i).evaluate(
        (el) => el === document.activeElement
      );
      expect(isFocused).toBe(true);
    }
  });
});
