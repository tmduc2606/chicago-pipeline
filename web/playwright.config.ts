import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: 1,
  fullyParallel: true,
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:5173",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    actionTimeout: 8_000,
    expect: { timeout: 8_000 },
  },
  reporter: [
    ["html", { open: "never" }],
    ["list"],
  ],
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
  ],
});
