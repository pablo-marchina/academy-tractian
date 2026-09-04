import { afterEach, describe, expect, it } from "vitest";

import {
  authorizationHeaders,
  clearAccessTokenProvider,
  setAccessTokenProvider,
} from "./auth";

afterEach(() => clearAccessTokenProvider());

describe("provider-neutral browser bearer boundary", () => {
  it("keeps provider-free requests unauthenticated when no token provider is configured", async () => {
    expect(await authorizationHeaders()).toEqual({});
  });

  it("attaches a token returned by a synchronous or asynchronous identity adapter", async () => {
    setAccessTokenProvider(() => "header.payload.signature");
    expect(await authorizationHeaders()).toEqual({
      Authorization: "Bearer header.payload.signature",
    });

    setAccessTokenProvider(async () => "second.token.value");
    expect(await authorizationHeaders()).toEqual({ Authorization: "Bearer second.token.value" });
  });

  it("allows an identity adapter to report no active session without inventing credentials", async () => {
    setAccessTokenProvider(() => null);
    expect(await authorizationHeaders()).toEqual({});
  });

  it.each(["", " token", "token ", "token with spaces", "token\nvalue", "á-token"])(
    "rejects malformed bearer material: %j",
    async (token) => {
      setAccessTokenProvider(() => token);
      await expect(authorizationHeaders()).rejects.toThrow("invalid_access_token");
    },
  );
});
