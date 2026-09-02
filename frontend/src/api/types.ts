export type ExecutionStatus = "accepted" | "running" | "completed" | "failed";
export type ProviderSelectionState = "NO_SELECTION" | "PROVIDER_FREE" | "SELECTED";
export type ChartType = "table" | "bar" | "line" | "heatmap" | "histogram";

export interface RunAccepted {
  run_id: string;
  status: "accepted";
  stream_path: string;
  run_path: string;
  execution_path: string;
}

export interface SafeRun {
  run_id: string;
  scenario_id: string;
  config_hash: string;
  event_count: number;
  model_calls: number;
  tool_proposals: number;
  tool_calls: number;
  policy_blocks: number;
  errors: number;
  terminal_decision: string | null;
  terminal_response_mode: string | null;
  terminal_reason_code: string | null;
  terminal_message: string | null;
  completed: boolean;
}

export interface SafeEvent {
  event_id: string;
  run_id: string;
  sequence: number;
  event_type: string;
  origin: string;
  timestamp: string | null;
  tool_name: string | null;
  decision_kind: string | null;
  provider_id: string | null;
  model_id: string | null;
  route_id: string | null;
  live_call: boolean | null;
  outcome: string | null;
  failure_code: string | null;
  latency_ms: number | null;
  turn_index: number | null;
  tool_call_count: number | null;
  argument_names: string;
  method: string | null;
  path_template: string | null;
  tool_kind: string | null;
  status_code: number | null;
  policy_stage: string | null;
  policy_allowed: boolean | null;
  policy_contained: boolean | null;
  policy_violation: string | null;
  evidence_id: string | null;
  reason_code: string | null;
  response_mode: string | null;
  message: string | null;
}

export interface SafeEvidenceRef {
  evidence_id: string;
  run_id: string;
  sequence: number;
  tool_name: string | null;
  status_code: number | null;
}

export interface SafeEvaluationCheck {
  run_id: string;
  check_name: string;
  passed: boolean;
  blocking: boolean;
  blocking_pass: boolean;
}

export interface ItemsResponse<T> {
  items: T[];
  count: number;
}

export interface ExecutionStateResponse {
  run_id: string;
  status: ExecutionStatus;
}

export interface ServiceHealth {
  status: string;
  service: string;
  version: string;
}

export interface OverviewMetrics {
  schema_version: string;
  total_runs: number;
  completed_runs: number;
  model_calls: number;
  tool_calls: number;
  policy_blocks: number;
  errors: number;
}

export interface ProductionHealthComponent {
  component: string;
  status: string;
  detail: string;
}

export interface ProductionHealth {
  schema_version: "production-health-v1";
  store_schema_version: string;
  overall_status: string;
  components: ProductionHealthComponent[];
  totals: OverviewMetrics & { incomplete_runs: number };
  measured: { forbidden_field_leakage: number };
  not_measured_yet: string[];
}

export interface ToolMetric {
  tool_name: string;
  proposals: number;
  calls: number;
  results: number;
  observations: number;
  status_codes: Record<string, number>;
}

export interface ToolsMetrics {
  schema_version: string;
  items: ToolMetric[];
  count: number;
}

export interface PolicyMetric {
  policy_stage: string;
  checks: number;
  allowed: number;
  blocked: number;
  contained: number;
  block_rate: number;
  violations: Record<string, number>;
}

export interface PoliciesMetrics {
  schema_version: string;
  items: PolicyMetric[];
  count: number;
}

export interface EvaluationMetricCheck {
  check_name: string;
  evaluations: number;
  passed: number;
  pass_rate: number;
  blocking: boolean;
}

export interface EvaluationMetrics {
  schema_version: string;
  checks: EvaluationMetricCheck[];
  check_count: number;
  rows: number;
  overall_pass_rate: number;
  blocking_pass_rate: number;
}

export interface LineageCard {
  lineage_id: string;
  sequence: number;
  origin: string;
  event_type: string;
  tool_name?: string | null;
  decision_kind?: string | null;
  policy_stage?: string | null;
  policy_allowed?: boolean | null;
  status_code?: number | null;
  evidence_id?: string | null;
  reason_code?: string | null;
  response_mode?: string | null;
  message?: string | null;
  evidence_ref?: SafeEvidenceRef;
  evaluation?: SafeEvaluationCheck[];
}

export interface OutputLineage {
  schema_version: "safe-output-lineage-v1";
  run_id: string;
  runtime_card_count: number;
  evaluation_card_count: number;
  cards: LineageCard[];
}

export interface ProviderCandidateSummary {
  candidate_id: string;
  attempts: number;
  hard_gate_pass: boolean;
  hard_gate_failures: string[];
  structured_decision_adherence: number;
  public_task_quality: number;
  safe_failure_behavior: number;
  trace_integrity: number;
  success_rate: number;
  signature_stability: number;
  median_latency_ms: number;
  p95_latency_ms: number;
  observed_neurons: number;
  cash_cost_usd: number;
  usage_complete: boolean;
}

export interface ProviderExperimentSummary {
  experiment_id: "D01" | "D02";
  status: "COMPLETE" | "NOT_EXECUTED";
  selection: string | null;
  production_selection_claim: boolean;
  attempted_calls: number;
  expected_calls: number;
  cash_cost_usd: number | null;
  packet_observed_neurons: number | null;
  packet_max_neurons: number;
  completion_cap_tokens: number;
  raw_provider_material_recorded: boolean;
  resource_accounting_complete: boolean;
  attempt_matrix_available: boolean;
  candidates: ProviderCandidateSummary[];
  diagnostic: {
    client_failures: number;
    client_failures_at_completion_cap: number;
    completion_cap_tokens: number;
    response_payload_invalid: number;
    clean_public_rubric_passes: number;
    interpretation: string;
  } | null;
  note: string;
}

export interface ProviderExperimentRegistry {
  schema_version: "safe-provider-experiments-v1";
  registry_sha256: string;
  experiments: ProviderExperimentSummary[];
}

export interface DynamicDatasetSchema {
  dimensions: string[];
  measures: string[];
}

export interface DynamicAnalyticsSchema {
  schema_version: "dynamic-analytics-schema-v1";
  datasets: Record<string, DynamicDatasetSchema>;
  filter_operators: string[];
  chart_types: Record<string, { dimension_count: number[]; measures?: string[] }>;
  limits: Record<string, number>;
}

export interface AnalyticsFilter {
  field: string;
  operator: "eq" | "ne" | "in";
  value: string | number | boolean | string[] | number[] | boolean[];
}

export interface AnalyticsQuerySpec {
  dataset: "runs" | "events" | "evaluations";
  dimensions: string[];
  measure: string;
  filters?: AnalyticsFilter[];
  chart_type: ChartType;
  limit?: number;
}

export interface DynamicAnalyticsResult {
  schema_version: "dynamic-analytics-result-v1";
  dataset: string;
  dimensions: string[];
  measure: string;
  chart_type: ChartType;
  source_row_count: number;
  rows: Record<string, string | number | boolean | null>[];
  truncated: boolean;
}

export interface ArchitectureComponent {
  component_id: string;
  label: string;
  layer:
    | "browser"
    | "api"
    | "runtime"
    | "safety"
    | "external"
    | "evaluator"
    | "observability";
  responsibility: string;
  trust_boundary: string;
  input_contracts: string[];
  output_contracts: string[];
  activates_on_event_types: string[];
  execution_role:
    | "presentation"
    | "control_plane"
    | "adaptive_intelligence"
    | "deterministic_boundary"
    | "external_system"
    | "post_runtime_only"
    | "telemetry";
}

export interface ArchitectureEdge {
  source: string;
  target: string;
  label: string;
}

export interface ArchitectureManifest {
  schema_version: "architecture-manifest-v1";
  architecture_version: "tractian-production-architecture-v1";
  provider_selection_state: ProviderSelectionState;
  components: ArchitectureComponent[];
  edges: ArchitectureEdge[];
  manifest_sha256: string;
}
