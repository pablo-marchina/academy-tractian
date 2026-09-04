export type IntegrationEvidenceState = "VALID" | "INVALID" | "MISSING";

export type ToolCoverageStatus =
  | "EVIDENCE_INVALID_FAIL_CLOSED"
  | "HOSTED_LIVE_FULLY_EXERCISED"
  | "PARTIAL_HOSTED_LIVE_EVIDENCE"
  | "PARTIAL_INTEGRATED_ROUTE_EVIDENCE"
  | "NO_INTEGRATION_EVIDENCE";

export interface ToolCoverageEvidenceSource {
  state: IntegrationEvidenceState;
  source: string;
  validation_errors: string[];
}

export interface ToolCoverageSummary {
  normalized_operations: number;
  contract_registered: number;
  implementation_routes_present: number;
  integrated_route_execution_evidenced: number;
  integrated_route_execution_not_yet_evidenced: number;
  frozen_route_execution_evidenced: number;
  hosted_live_exercised: number;
  hosted_live_success: number;
  hosted_live_http_error_observed: number;
  hosted_live_transport_failure: number;
  hosted_live_unavailable: number;
  hosted_live_blocked_by_safety: number;
  hosted_live_not_exercised: number;
  actions: number;
  reads: number;
}

export interface ToolCoverageOperation {
  tool_name: string;
  operation_id: string;
  method: string;
  path_template: string;
  kind: string;
  impact: string | null;
  required_permissions: string[];
  parameter_count: number;
  required_parameter_count: number;
  identity_required: boolean;
  justification_required: boolean;
  seed_supported: boolean;
  contract_registered: boolean;
  implementation_route_present: boolean;
  integrated_route_execution_evidenced: boolean;
  integration_evidence_scope: string;
  frozen_route_execution_evidenced: boolean;
  hosted_live_exercised: boolean;
  hosted_live_success: boolean;
  hosted_live_blocked_by_safety: boolean;
  hosted_live_outcomes: string[];
}

export interface ToolCoverageResponse {
  schema_version: "tractian-tool-coverage-v2";
  status: ToolCoverageStatus;
  claim_boundary: string;
  evidence: {
    frozen: ToolCoverageEvidenceSource;
    hosted_live: ToolCoverageEvidenceSource;
  };
  summary: ToolCoverageSummary;
  operations: ToolCoverageOperation[];
}
