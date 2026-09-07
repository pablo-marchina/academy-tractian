export const MANAGED_AUTH_EVENT = "academy:managed-auth-state";

export type ManagedAuthSignal = "invalid" | "unavailable";

export function emitManagedAuthSignal(signal: ManagedAuthSignal): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<ManagedAuthSignal>(MANAGED_AUTH_EVENT, { detail: signal }));
}

export function managedAuthSignalForResponse(status: number, detail: string): ManagedAuthSignal | null {
  if (
    status === 401 &&
    (detail === "managed_session_required" || detail === "managed_session_invalid")
  ) {
    return "invalid";
  }
  if (status === 503 && detail === "managed_session_unavailable") {
    return "unavailable";
  }
  return null;
}
