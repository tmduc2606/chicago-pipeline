import { test, expect } from "@playwright/test";

test.describe("API security", () => {
  test("CORS blocks unauthorized origins", async ({ request }) => {
    const response = await request.get("/api/overview", {
      headers: {
        "Origin": "https://evil.com",
      },
    });
    const accessControl = response.headers()["access-control-allow-origin"] || "";
    expect(accessControl).not.toBe("https://evil.com");
  });

  test("CORS allows same-origin or configured origins", async ({ request }) => {
    const response = await request.get("/api/overview");
    expect(response.ok()).toBeTruthy();
  });

  test("API does not expose server version", async ({ request }) => {
    const response = await request.get("/api/overview");
    const server = response.headers()["server"] || "";
    expect(server).not.toContain("uvicorn");
    expect(server).not.toContain("Python");
  });
});
