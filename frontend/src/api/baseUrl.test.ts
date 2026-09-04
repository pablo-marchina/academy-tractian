import { describe, expect, it } from "vitest";

import { normalizeApiBaseUrl, resolveApiUrl } from "./baseUrl";

describe("hosted API URL boundary", () => {
  it("keeps same-origin mode when no hosted API base is configured", () => {
    expect(normalizeApiBaseUrl(undefined)).toBe("");
    expect(normalizeApiBaseUrl("   ")).toBe("");
    expect(resolveApiUrl("/health", "")).toBe("/health");
  });

  it("normalizes a hosted origin and optional path prefix", () => {
    expect(normalizeApiBaseUrl("https://api.example.com/")).toBe("https://api.example.com");
    expect(normalizeApiBaseUrl("https://api.example.com/academy/")).toBe(
      "https://api.example.com/academy",
    );
    expect(resolveApiUrl("/api/runs", "https://api.example.com/academy")).toBe(
      "https://api.example.com/academy/api/runs",
    );
  });

  it("rejects malformed or unsafe API base URLs", () => {
    expect(() => normalizeApiBaseUrl("api.example.com")).toThrow("invalid_api_base_url");
    expect(() => normalizeApiBaseUrl("ftp://api.example.com")).toThrow(
      "invalid_api_base_url_protocol",
    );
    expect(() => normalizeApiBaseUrl("https://user:secret@api.example.com")).toThrow(
      "api_base_url_credentials_forbidden",
    );
    expect(() => normalizeApiBaseUrl("https://api.example.com?tenant=a")).toThrow(
      "api_base_url_query_or_hash_forbidden",
    );
    expect(() => normalizeApiBaseUrl("https://api.example.com#fragment")).toThrow(
      "api_base_url_query_or_hash_forbidden",
    );
  });

  it("rejects non-absolute API paths", () => {
    expect(() => resolveApiUrl("api/runs", "https://api.example.com")).toThrow(
      "api_path_must_be_absolute",
    );
  });
});
