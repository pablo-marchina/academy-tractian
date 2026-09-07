export type Release0ToolAvailability = "LIVE_READ" | "PROPOSAL_ONLY" | "UNAVAILABLE";

export interface Release0CapabilityParameter {
  name: string;
  location: "path" | "query" | "header" | "body";
  required: boolean;
}

export interface Release0ToolCapability {
  name: string;
  operation_id: string;
  method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  path_template: string;
  kind: "read" | "action";
  impact: "none" | "workflow" | "low" | "high";
  availability: Release0ToolAvailability;
  parameters: Release0CapabilityParameter[];
  required_permissions: string[];
  justification_required: boolean;
  minimum_justification_length: number | null;
  identity_required: boolean;
  seed_supported: boolean;
}

export interface Release0GuidedIntent {
  intent_id: "CONTEXTUALIZE" | "INVESTIGATE" | "EXECUTE";
  label: string;
  runtime_mapping: string;
  release0_behavior: string;
  prompt_template: string;
}

export interface Release0ExpectedOutput {
  output_id: string;
  label: string;
  description: string;
}

export interface Release0CapabilityManifest {
  schema_version: "release0-capabilities-v1";
  release: {
    git_sha: string;
    read_only_user_path_enabled: boolean;
    cost_policy: string;
    paid_fallback_enabled: boolean;
    local_serving_enabled: boolean;
  };
  provider: {
    calls_enabled: boolean;
    selection_state: string;
    provider_id: string | null;
    model_id: string | null;
    provisional: boolean;
  };
  tractian: {
    transport_enabled: boolean;
    transport_state: string;
    read_path_enabled: boolean;
  };
  action_execution: {
    enabled: false;
    mode: "PROPOSAL_ONLY";
    external_side_effects_allowed: false;
    explanation: string;
  };
  tool_summary: {
    total: number;
    reads: number;
    actions: number;
    live_reads: number;
    proposal_only_actions: number;
  };
  read_semantics: Array<"complete" | "partial" | "inconclusive" | "conflict" | "unavailable">;
  guided_intents: Release0GuidedIntent[];
  expected_outputs: Release0ExpectedOutput[];
  tools: Release0ToolCapability[];
  server_owned: true;
  raw_secrets_exposed: false;
  raw_api_payloads_exposed: false;
  chain_of_thought_exposed: false;
}
