import { emitManagedAuthSignal, managedAuthSignalForResponse } from "../auth/managedAuthEvents";
import type { RunVerificationReport } from "./verificationTypes";

export async function fetchRunVerification(runId: string): Promise<RunVerificationReport> {
  const response = await fetch(`/api/runs/${encodeURIComponent(runId)}/verification`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // Keep status-only error when JSON is unavailable.
    }
    const signal = managedAuthSignalForResponse(response.status, detail);
    if (signal !== null) emitManagedAuthSignal(signal);
    throw new Error(detail);
  }
  return (await response.json()) as RunVerificationReport;
}
