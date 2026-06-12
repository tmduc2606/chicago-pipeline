import { test, expect } from "@playwright/test";

test.describe("API health endpoint", () => {
  test("returns JSON with status ok", async ({ request }) => {
    const response = await request.get("/api/health/live");
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body).toHaveProperty("status");
    expect(body.status).toBe("ok");
  });

  test("returns correct content-type", async ({ request }) => {
    const response = await request.get("/api/health/live");
    const contentType = response.headers()["content-type"] || "";
    expect(contentType).toContain("application/json");
  });

  test("ready endpoint returns 200 or 503", async ({ request }) => {
    const response = await request.get("/api/health/ready");
    expect([200, 503]).toContain(response.status());
  });
});
