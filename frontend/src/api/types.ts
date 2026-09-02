export type ExecutionStatus = "accepted" | "running" | "completed" | "failed";
export type ProviderSelectionState = "NO_SELECTION" | "PROVIDER_FREE" | "SELECTED";

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
