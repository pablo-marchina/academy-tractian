import { describe, expect, it } from "vitest";

import { managedAuthSignalForResponse } from "./managedAuthEvents";

describe("managedAuthSignalForResponse", () => {
  it.each([
    [401, "managed_session_required", "invalid"],
    [401, "managed_session_invalid", "invalid"],
    [503, "managed_session_unavailable", "unavailable"],
  ] as const)("maps %s %s to %s", (status, detail, expected) => {
    expect(managedAuthSignalForResponse(status, detail)).toBe(expected);
  });

  it.each([
    [401, "other"],
    [500, "managed_session_unavailable"],
    [503, "other"],
    [200, "managed_session_invalid"],
  ] as const)("does not reinterpret unrelated response %s %s", (status, detail) => {
    expect(managedAuthSignalForResponse(status, detail)).toBeNull();
  });
});
