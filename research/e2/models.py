from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Decision(str, Enum):
    ORIENT = "ORIENT"
    INVESTIGATE = "INVESTIGATE"
    ACT_REPROCESS = "ACT_REPROCESS"
    ACT_REQUEST_SPECIALIST = "ACT_REQUEST_SPECIALIST"
    ACT_UPDATE_CONFIG = "ACT_UPDATE_CONFIG"
    ACT_REQUEST_RETRAINING = "ACT_REQUEST_RETRAINING"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"
    ASK_CLARIFICATION = "ASK_CLARIFICATION"
    ABSTAIN = "ABSTAIN"


class Permission(str, Enum):
    READ = "read"
    ACTION_LOW = "action_low"
    ACTION_HIGH = "action_high"
    ESCALATE = "escalate"


class ResponseMode(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    INCONCLUSIVE = "inconclusive"
    CONFLICT = "conflict"
    UNAVAILABLE = "unavailable"


class ToolKind(str, Enum):
    READ = "read"
    ACTION = "action"


class ActionImpact(str, Enum):
    NONE = "none"
    WORKFLOW = "workflow"
    LOW = "low"
    HIGH = "high"


class ExtraForbidModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class ReviewStatus(str, Enum):
    UNREVIEWED = "UNREVIEWED"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED_NEEDS_SOURCE_CLARIFICATION = "REJECTED_NEEDS_SOURCE_CLARIFICATION"


class Provenance(ExtraForbidModel):
    source_hashes: dict[str, str] = Field(default_factory=dict)
    source_locations: list[dict[str, str]] = Field(default_factory=list)
    review_status: ReviewStatus
    review_notes: list[str] = Field(default_factory=list)
    benchmark_authoritative: bool


class AgentCase(ExtraForbidModel):
    id: str
    ticket_id: str
    company_id: str
    user_id: str
    asset_id: str
    message: str


class ScenarioInput(ExtraForbidModel):
    cases: list[AgentCase] = Field(min_length=1)


class BoundContext(ExtraForbidModel):
    user_ids: list[str]
    company_ids: list[str]
    asset_ids: list[str]
    identity_model_controlled: Literal[False] = False
    seed_model_controlled: Literal[False] = False


class ResponseModeProfile(ExtraForbidModel):
    resource: str
    category: str
    mode: ResponseMode | None = None
    mode_source: Literal["fixed_override", "runner_seed", "not_applicable", "unresolved"]
    seed_ref: str | None = None


class EnvironmentSpec(ExtraForbidModel):
    scenario_condition: str | None = None
    response_mode_profile: list[ResponseModeProfile] = Field(default_factory=list)
    action_persistence_semantics: Literal["accepted_event_non_persistent"] = "accepted_event_non_persistent"


class DecisionOracle(ExtraForbidModel):
    required: list[Decision] = Field(default_factory=list)
    acceptable: list[Decision] = Field(default_factory=list)
    forbidden: list[Decision] = Field(default_factory=list)


class PolicyOracle(ExtraForbidModel):
    source_rules: list[str] = Field(default_factory=list)
    required_permissions: list[Permission] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    resource_scope_enforced: bool = True
    justification_required: bool = False
    minimum_justification_length: int | None = Field(default=None, ge=0)
    confirmation_required: bool = False


class EvidenceRequirement(ExtraForbidModel):
    source: str
    predicate: str
    required_before_action: bool = False


class EvidenceGroup(ExtraForbidModel):
    group_id: str
    requirements: list[EvidenceRequirement] = Field(default_factory=list)
    minimum_satisfied: int | None = Field(default=None, ge=1)


class EvidenceOracle(ExtraForbidModel):
    required_groups: list[EvidenceGroup] = Field(default_factory=list)
    forbidden_unsupported_inferences: list[str] = Field(default_factory=list)
    uncertainty_behavior: Literal[
        "not_required", "report_partial", "report_inconclusive", "resolve_conflict", "escalate_if_unresolved", "source_review_required"
    ] = "not_required"


class ActionOracle(ExtraForbidModel):
    execution_expectation: Literal["required", "forbidden", "optional"]
    success_semantics: Literal["accepted_event", "blocked_by_policy", "no_action_expected"]
    post_action_read_semantics: Literal["diagnostic_only", "required_observation", "not_applicable"]
    final_state_equality_required: bool = False
    required_action: str | None = None
    target_resource: str | None = None
    required_permission: Permission | None = None
    accepted_required: bool = True
    duplicate_action_forbidden: bool = True
    argument_constraints: list[str] = Field(default_factory=list)
    justification_facts: list[str] = Field(default_factory=list)


class ConclusionOracle(ExtraForbidModel):
    required_facts: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    uncertainty_required: bool = False
    source_resolution_text: str


class CommunicationOracle(ExtraForbidModel):
    source_citation_required: bool = False
    forbidden_internal_disclosures: list[str] = Field(default_factory=list)
    handoff_requirements: list[str] = Field(default_factory=list)


class CallReference(ExtraForbidModel):
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"]
    path: str
    purpose: str | None = None


class TrajectoryOracle(ExtraForbidModel):
    reference_is_script: Literal[False] = False
    reference_calls: list[CallReference] = Field(default_factory=list)
    required_calls: list[CallReference] = Field(default_factory=list)
    forbidden_calls: list[CallReference] = Field(default_factory=list)
    ordering_constraints: list[str] = Field(default_factory=list)
    efficiency_is_diagnostic: bool = True


class EvaluationSpec(ExtraForbidModel):
    p1_success_source: str
    p2_metric_sources: list[str] = Field(default_factory=list)
    known_variations_source: str | None = None


class Scenario(ExtraForbidModel):
    schema_version: Literal["scenario-v1"] = "scenario-v1"
    scenario_id: str = Field(pattern=r"^CEN-[0-9]{2}$")
    title: str
    ticket_ids: list[str] = Field(min_length=1)
    split_group_id: str
    provenance: Provenance
    input: ScenarioInput
    bound_context: BoundContext
    environment: EnvironmentSpec
    decision_oracle: DecisionOracle
    policy_oracle: PolicyOracle
    evidence_oracle: EvidenceOracle
    action_oracle: ActionOracle | None = None
    conclusion_oracle: ConclusionOracle
    communication_oracle: CommunicationOracle = Field(default_factory=CommunicationOracle)
    trajectory_oracle: TrajectoryOracle
    evaluation: EvaluationSpec


class ToolParameter(ExtraForbidModel):
    name: str
    location: Literal["path", "query", "header", "body"]
    required: bool = False
    parameter_schema: dict[str, Any] = Field(default_factory=dict, alias="schema")


class ToolSpec(ExtraForbidModel):
    spec_version: Literal["tool-spec-v1"] = "tool-spec-v1"
    name: str
    operation_id: str
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"]
    path_template: str
    kind: ToolKind
    impact: ActionImpact = ActionImpact.NONE
    description: str | None = None
    parameters: list[ToolParameter] = Field(default_factory=list)
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    required_permissions: list[Permission] = Field(default_factory=list)
    target_scope: Literal["none", "resource", "company_resource"] = "none"
    justification_required: bool = False
    minimum_justification_length: int | None = Field(default=None, ge=0)
    confirmation_required: bool = False
    identity_required: bool = False
    identity_binding: Literal["runner"] = "runner"
    seed_binding: Literal["runner"] = "runner"
    action_persistence: Literal["accepted_event_non_persistent", "unknown"] = "unknown"


class TraceEvent(ExtraForbidModel):
    sequence: int = Field(ge=0)
    event_type: Literal[
        "run_started", "model_call", "decision", "tool_proposal", "policy_check", "confirmation", "tool_call", "tool_result", "observation", "state_change", "escalation", "final_response", "error", "run_finished"
    ]
    timestamp: datetime | None = None
    call_id: str | None = None
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None
    result: Any = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunTrace(ExtraForbidModel):
    trace_version: Literal["trace-v1"] = "trace-v1"
    run_id: str
    scenario_id: str
    config_hash: str
    identity_binding_id: str
    seed_ref: str
    events: list[TraceEvent] = Field(default_factory=list)


class ExecutionBinding(ExtraForbidModel):
    identity_id: str
    user_id: str
    seed: str | None = None


class BoundRequest(ExtraForbidModel):
    method: str
    path: str
    query: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] | None = None
