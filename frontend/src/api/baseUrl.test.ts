import { describe, expect, it } from "vitest";

import { normalizeApiBaseUrlForTest } from "./baseUrl";

describe("hosted API base URL", () => {
  it("keeps the local same-origin mode when no base URL is configured", () => {
    expect(normalizeApiBaseUrlForTest("  ")).toBe("");
  });

  it("normalizes a public backend origin", () => {
    expect(normalizeApiBaseUrlForTest("https://api.example.app/")).toBe(
      "https://api.example.app",
    );
  });

  it("rejects non-http protocols and path-bearing values", () => {
    expect(() => normalizeApiBaseUrlForTest("ftp://api.example.app")).toThrow(
      "invalid_api_base_url_protocol",
    );
    expect(() => normalizeApiBaseUrlForTest("https://api.example.app/v1")).toThrow(
      "api_base_url_must_be_origin_only",
    );
  });
});
