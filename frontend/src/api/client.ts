import type {
  AnalyticsQuerySpec,
  ArchitectureManifest,
  DynamicAnalyticsResult,
  DynamicAnalyticsSchema,
  EvaluationMetrics,
  ExecutionStateResponse,
  ItemsResponse,
  OutputLineage,
  PoliciesMetrics,
  ProductionHealth,
  ProviderExperimentRegistry,
  RunAccepted,
  SafeEvaluationCheck,
  SafeEvent,
  SafeEvidenceRef,
  SafeRun,
  ServiceHealth,
  ToolsMetrics,
  OverviewMetrics,
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
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // Keep status-only public error when JSON detail is unavailable.
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

export function fetchRunById(runId: string): Promise<SafeRun> {
  return requestJson<SafeRun>(`/api/runs/${encodeURIComponent(runId)}`);
}

export function fetchRuns(limit = 100): Promise<ItemsResponse<SafeRun>> {
  return requestJson<ItemsResponse<SafeRun>>(`/api/runs?limit=${limit}`);
}

export function fetchRunEvents(runId: string): Promise<ItemsResponse<SafeEvent>> {
  return requestJson<ItemsResponse<SafeEvent>>(`/api/runs/${encodeURIComponent(runId)}/events`);
}

export function fetchEvidence(runId: string): Promise<ItemsResponse<SafeEvidenceRef>> {
  return requestJson<ItemsResponse<SafeEvidenceRef>>(`/api/runs/${encodeURIComponent(runId)}/evidence`);
}

export function fetchLineage(runId: string): Promise<OutputLineage> {
  return requestJson<OutputLineage>(`/api/runs/${encodeURIComponent(runId)}/lineage`);
}

export function fetchExecution(executionPath: string): Promise<ExecutionStateResponse> {
  return requestJson<ExecutionStateResponse>(executionPath);
}

export function fetchEvaluation(runId: string): Promise<ItemsResponse<SafeEvaluationCheck>> {
  return requestJson<ItemsResponse<SafeEvaluationCheck>>(`/api/runs/${encodeURIComponent(runId)}/evaluation`);
}

export function fetchArchitecture(): Promise<ArchitectureManifest> {
  return requestJson<ArchitectureManifest>("/api/architecture");
}

export function fetchHealth(): Promise<ServiceHealth> {
  return requestJson<ServiceHealth>("/health");
}

export function fetchOverview(): Promise<OverviewMetrics> {
  return requestJson<OverviewMetrics>("/api/overview");
}

export function fetchProductionHealth(): Promise<ProductionHealth> {
  return requestJson<ProductionHealth>("/api/production/health");
}

export function fetchToolsMetrics(): Promise<ToolsMetrics> {
  return requestJson<ToolsMetrics>("/api/tools/metrics");
}

export function fetchPoliciesMetrics(): Promise<PoliciesMetrics> {
  return requestJson<PoliciesMetrics>("/api/policies/metrics");
}

export function fetchEvaluationMetrics(): Promise<EvaluationMetrics> {
  return requestJson<EvaluationMetrics>("/api/evaluations/metrics");
}

export function fetchProviderExperiments(): Promise<ProviderExperimentRegistry> {
  return requestJson<ProviderExperimentRegistry>("/api/providers/experiments");
}

export function fetchDynamicAnalyticsSchema(): Promise<DynamicAnalyticsSchema> {
  return requestJson<DynamicAnalyticsSchema>("/api/query/schema");
}

export function executeAnalyticsQuery(spec: AnalyticsQuerySpec): Promise<DynamicAnalyticsResult> {
  return requestJson<DynamicAnalyticsResult>("/api/query", {
    method: "POST",
    body: JSON.stringify(spec),
  });
}
