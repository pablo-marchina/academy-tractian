import type {
  ExecutionStateResponse,
  ItemsResponse,
  RunAccepted,
  SafeEvaluationCheck,
  SafeRun,
  ServiceHealth,
} from "./types";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // Keep the status-only public error when the server does not expose JSON detail.
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export function submitRun(userRequest: string): Promise<RunAccepted> {
  return requestJson<RunAccepted>("/api/runs", {
    method: "POST",
    body: JSON.stringify({ user_request: userRequest }),
  });
}

export function fetchRun(runPath: string): Promise<SafeRun> {
  return requestJson<SafeRun>(runPath);
}

export function fetchExecution(executionPath: string): Promise<ExecutionStateResponse> {
  return requestJson<ExecutionStateResponse>(executionPath);
}

export function fetchEvaluation(runId: string): Promise<ItemsResponse<SafeEvaluationCheck>> {
  return requestJson<ItemsResponse<SafeEvaluationCheck>>(
    `/api/runs/${encodeURIComponent(runId)}/evaluation`,
  );
}

export function fetchHealth(): Promise<ServiceHealth> {
  return requestJson<ServiceHealth>("/health");
}
