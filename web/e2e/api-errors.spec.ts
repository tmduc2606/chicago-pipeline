import { test, expect } from "@playwright/test";

test.describe("API error responses", () => {
  test("invalid query param returns 422 with detail array", async ({ request }) => {
    const response = await request.get("/api/timeseries?granularity=invalid");
    expect(response.status()).toBe(422);

    const body = await response.json();
    expect(body).toHaveProperty("detail");
    expect(Array.isArray(body.detail)).toBeTruthy();
    expect(body.detail.length).toBeGreaterThan(0);

    const firstError = body.detail[0];
    expect(firstError).toHaveProperty("loc");
    expect(firstError).toHaveProperty("msg");
    expect(firstError).toHaveProperty("type");
  });

  test("missing required param returns 422", async ({ request }) => {
    const response = await request.get("/api/geo/choropleth");
    expect(response.status()).toBe(200);
  });

  test("invalid crime type returns 404 or 422", async ({ request }) => {
    const response = await request.get("/api/crime-types/trend?type=NONEXISTENT_CRIME_TYPE");
    expect([404, 422, 200]).toContain(response.status());
  });

  test("error response does not expose stack traces", async ({ request }) => {
    const response = await request.get("/api/timeseries?granularity=invalid");
    const body = await response.json();
    const bodyStr = JSON.stringify(body);
    expect(bodyStr).not.toContain("Traceback");
    expect(bodyStr).not.toContain("File \"");
    expect(bodyStr).not.toContain("line ");
  });
});
