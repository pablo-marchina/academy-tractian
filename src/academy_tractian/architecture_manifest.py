from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


ProviderSelectionState = Literal["NO_SELECTION", "PROVIDER_FREE", "SELECTED"]


class ArchitectureComponent(_FrozenModel):
    component_id: str = Field(pattern=r"^[a-z0-9_]+$")
    label: str = Field(min_length=1)
    layer: Literal[
        "browser",
        "api",
        "runtime",
        "safety",
        "external",
        "evaluator",
        "observability",
    ]
    responsibility: str = Field(min_length=1)
    trust_boundary: str = Field(min_length=1)
    input_contracts: tuple[str, ...] = ()
    output_contracts: tuple[str, ...] = ()
    activates_on_event_types: tuple[str, ...] = ()
    execution_role: Literal[
        "presentation",
        "control_plane",
        "adaptive_intelligence",
        "deterministic_boundary",
        "external_system",
        "post_runtime_only",
        "telemetry",
    ]


class ArchitectureEdge(_FrozenModel):
    source: str
    target: str
    label: str = Field(min_length=1)


class ArchitectureManifest(_FrozenModel):
    schema_version: Literal["architecture-manifest-v1"] = "architecture-manifest-v1"
    architecture_version: Literal["tractian-production-architecture-v1"] = (
        "tractian-production-architecture-v1"
    )
    provider_selection_state: ProviderSelectionState
    components: tuple[ArchitectureComponent, ...]
    edges: tuple[ArchitectureEdge, ...]
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def _components() -> tuple[ArchitectureComponent, ...]:
    return (
        ArchitectureComponent(
            component_id="operator_frontend",
            label="Operator Frontend",
            layer="browser",
            responsibility="Submit product requests and visualize only sanitized operational state.",
            trust_boundary="browser-safe observability boundary",
            input_contracts=("RunAccepted", "SafeRun", "SafeEvent", "SafeEvaluation"),
            output_contracts=("RunSubmission",),
            execution_role="presentation",
        ),
        ArchitectureComponent(
            component_id="product_api",
            label="FastAPI Product / BFF Boundary",
            layer="api",
            responsibility="Accept product requests, resolve trusted server-side context and own the request/run lifecycle.",
            trust_boundary="trusted server application boundary",
            input_contracts=("RunSubmission", "AuthenticatedRuntimeContext"),
            output_contracts=("RunAccepted", "ExecutionStateResponse"),
            activates_on_event_types=("run_started",),
            execution_role="control_plane",
        ),
        ArchitectureComponent(
            component_id="runtime_identity",
            label="Trusted Runtime Identity",
            layer="safety",
            responsibility="Validate the current signed server-trusted identity envelope before tenant, user and permission context is accepted.",
            trust_boundary="identity verification boundary; not yet a complete browser OIDC claim",
            input_contracts=("Authorization bearer",),
            output_contracts=("AuthenticatedRuntimeContext",),
            execution_role="deterministic_boundary",
        ),
        ArchitectureComponent(
            component_id="postgres_operational_store",
            label="PostgreSQL Operational Core",
            layer="runtime",
            responsibility="Persist run ownership/execution, tenant-scoped operational state and server-owned product state.",
            trust_boundary="durable PostgreSQL operational and tenant-authorization boundary",
            input_contracts=("AuthenticatedRuntimeContext", "RunState", "ActionState"),
            output_contracts=("OwnedRun", "ExecutionState", "TenantScopedRows"),
            activates_on_event_types=("run_started", "state_change", "run_finished"),
            execution_role="deterministic_boundary",
        ),
        ArchitectureComponent(
            component_id="runtime_handoff",
            label="PostgreSQL Runtime Handoff",
            layer="runtime",
            responsibility="Coordinate transferable read-only work using durable leases, monotonic generations and stale-owner fencing.",
            trust_boundary="generation-fenced distributed read-work boundary",
            input_contracts=("RuntimeWorkItem",),
            output_contracts=("RuntimeLease", "RecoveredWorkItem"),
            activates_on_event_types=("run_started", "state_change", "run_finished"),
            execution_role="deterministic_boundary",
        ),
        ArchitectureComponent(
            component_id="realtime_runtime",
            label="Realtime Production Runtime",
            layer="runtime",
            responsibility="Compose the accepted controller/tool boundary with durable runtime state, bounded execution and safe telemetry.",
            trust_boundary="runtime-owned identity and execution boundary",
            input_contracts=("ProductionRequest", "RuntimeLease"),
            output_contracts=("PreparedRealtimeRun", "RunTrace"),
            activates_on_event_types=("run_started", "run_finished"),
            execution_role="control_plane",
        ),
        ArchitectureComponent(
            component_id="decision_source",
            label="Decision Source / Provider",
            layer="runtime",
            responsibility="Produce typed controller decisions without owning tool execution, identity, runtime-controlled fields or evaluator truth.",
            trust_boundary="replaceable provider-neutral decision boundary",
            input_contracts=("ControllerContext",),
            output_contracts=("ControllerDecision", "DecisionSourceAuditRecord"),
            activates_on_event_types=("model_call", "decision"),
            execution_role="adaptive_intelligence",
        ),
        ArchitectureComponent(
            component_id="agent_controller",
            label="Agent Controller",
            layer="runtime",
            responsibility="Run the bounded single-agent loop and terminate with final, clarify, escalate, abstain or action-proposal outcomes.",
            trust_boundary="application-owned bounded orchestration",
            input_contracts=("ControllerDecision", "ControllerObservation"),
            output_contracts=("ToolProposal", "RunTrace"),
            activates_on_event_types=("decision", "state_change", "escalation", "final_response"),
            execution_role="control_plane",
        ),
        ArchitectureComponent(
            component_id="harness_runner",
            label="HarnessRunner",
            layer="runtime",
            responsibility="Own the exclusive real tool execution boundary and canonical execution-trace emission.",
            trust_boundary="exclusive real tool execution boundary",
            input_contracts=("ToolProposal", "ExecutionBinding"),
            output_contracts=("ToolExecution", "RunTrace"),
            activates_on_event_types=("tool_proposal", "tool_call", "tool_result", "observation"),
            execution_role="deterministic_boundary",
        ),
        ArchitectureComponent(
            component_id="tool_registry",
            label="Typed Tool Registry",
            layer="safety",
            responsibility="Expose the canonical 18-operation TRACTIAN ToolSpec contract and validate model-visible tool shape.",
            trust_boundary="typed contract boundary",
            input_contracts=("ToolSpec",),
            output_contracts=("Validated ToolSpec",),
            activates_on_event_types=("tool_proposal", "tool_call"),
            execution_role="deterministic_boundary",
        ),
        ArchitectureComponent(
            component_id="safety_envelope",
            label="B1 / B2 / B3 Safety Envelope",
            layer="safety",
            responsibility="Deterministically enforce argument, permission/resource and evidence-aware action policy outside model control.",
            trust_boundary="deterministic safety boundary",
            input_contracts=("ToolSpec", "ToolProposal", "AuthorizationContext"),
            output_contracts=("PolicyDecision",),
            activates_on_event_types=("policy_check", "confirmation"),
            execution_role="deterministic_boundary",
        ),
        ArchitectureComponent(
            component_id="action_control",
            label="Governed Action Control",
            layer="safety",
            responsibility="Persist private action custody, explicit confirmation, idempotency and non-transferable execution leases; ambiguous ownership becomes UNCERTAIN.",
            trust_boundary="consequential-action custody and execution boundary",
            input_contracts=("ActionProposal", "ConfirmedAction", "AuthorizationContext"),
            output_contracts=("ActionState", "ActionExecutionLease"),
            activates_on_event_types=("confirmation", "state_change", "error"),
            execution_role="deterministic_boundary",
        ),
        ArchitectureComponent(
            component_id="tractian_transport",
            label="TRACTIAN API Transport",
            layer="external",
            responsibility="Execute bound HTTP requests against the supplied TRACTIAN API after deterministic gates pass.",
            trust_boundary="external partner API boundary",
            input_contracts=("BoundRequest",),
            output_contracts=("TransportResponse",),
            activates_on_event_types=("tool_call", "tool_result"),
            execution_role="external_system",
        ),
        ArchitectureComponent(
            component_id="normalized_evidence",
            label="Normalized Evidence",
            layer="runtime",
            responsibility="Return controller-visible observations while browser telemetry receives only sanitized evidence references.",
            trust_boundary="runtime evidence boundary",
            input_contracts=("TransportResponse",),
            output_contracts=("ControllerObservation", "SafeEvidenceRef"),
            activates_on_event_types=("observation",),
            execution_role="control_plane",
        ),
        ArchitectureComponent(
            component_id="run_trace",
            label="Canonical RunTrace",
            layer="runtime",
            responsibility="Maintain ordered operational provenance for the production run without exposing hidden chain-of-thought.",
            trust_boundary="raw runtime trace; never directly browser serialized",
            input_contracts=("TraceEvent",),
            output_contracts=("RunTrace",),
            activates_on_event_types=(
                "run_started",
                "model_call",
                "decision",
                "tool_proposal",
                "policy_check",
                "tool_call",
                "tool_result",
                "observation",
                "state_change",
                "escalation",
                "final_response",
                "error",
                "run_finished",
            ),
            execution_role="deterministic_boundary",
        ),
        ArchitectureComponent(
            component_id="production_evaluator",
            label="Production Evaluator",
            layer="evaluator",
            responsibility="Evaluate completed traces post-runtime using deterministic structural, provenance and safety checks.",
            trust_boundary="post-runtime evaluator isolation boundary",
            input_contracts=("RunTrace",),
            output_contracts=("ProductionEvaluationReport",),
            execution_role="post_runtime_only",
        ),
        ArchitectureComponent(
            component_id="semantic_review",
            label="Human Semantic Review",
            layer="evaluator",
            responsibility="Collect blinded human semantic labels for calibration without exposing evaluator-private truth to the runtime.",
            trust_boundary="blinded human-evaluation boundary",
            input_contracts=("SemanticReviewTask",),
            output_contracts=("SemanticReviewAssignment", "SemanticReviewResult"),
            execution_role="post_runtime_only",
        ),
        ArchitectureComponent(
            component_id="operational_value",
            label="Operational Value Study",
            layer="evaluator",
            responsibility="Collect paired manual versus agent-assisted operational evidence before any productivity/value claim.",
            trust_boundary="human operational-study boundary",
            input_contracts=("OperationalPilotTask",),
            output_contracts=("OperationalPilotResult",),
            execution_role="post_runtime_only",
        ),
        ArchitectureComponent(
            component_id="observability_projector",
            label="Safe Observability Projector",
            layer="observability",
            responsibility="Project raw runtime/evaluation state into allow-listed browser-safe schemas.",
            trust_boundary="raw-to-safe serialization boundary",
            input_contracts=("RunTrace", "ProductionEvaluationReport"),
            output_contracts=("SafeRun", "SafeEvent", "SafeEvidenceRef", "SafeEvaluation"),
            activates_on_event_types=(
                "run_started",
                "model_call",
                "decision",
                "tool_proposal",
                "policy_check",
                "tool_call",
                "tool_result",
                "observation",
                "state_change",
                "escalation",
                "final_response",
                "error",
                "run_finished",
            ),
            execution_role="telemetry",
        ),
        ArchitectureComponent(
            component_id="observability_store",
            label="PostgreSQL Safe Observability Store",
            layer="observability",
            responsibility="Persist sanitized run, event, evidence and evaluation projections in the promoted PostgreSQL serving substrate.",
            trust_boundary="persistent sanitized telemetry boundary",
            input_contracts=("SafeRun", "SafeEvent", "SafeEvidenceRef", "SafeEvaluation"),
            output_contracts=("Sanitized query rows", "Durable event cursor"),
            activates_on_event_types=(
                "run_started",
                "model_call",
                "decision",
                "tool_proposal",
                "policy_check",
                "tool_call",
                "tool_result",
                "observation",
                "state_change",
                "escalation",
                "final_response",
                "error",
                "run_finished",
            ),
            execution_role="telemetry",
        ),
        ArchitectureComponent(
            component_id="realtime_wakeup",
            label="PostgreSQL Realtime Wake-up",
            layer="observability",
            responsibility="Use LISTEN/NOTIFY only as a wake-up while durable PostgreSQL rows and sequence cursors remain authoritative for catch-up.",
            trust_boundary="non-authoritative realtime wake-up boundary",
            input_contracts=("Committed SafeEvent",),
            output_contracts=("WakeupSignal",),
            activates_on_event_types=("run_started", "state_change", "run_finished"),
            execution_role="telemetry",
        ),
        ArchitectureComponent(
            component_id="observability_api",
            label="Observability REST / SSE API",
            layer="api",
            responsibility="Serve safe historical telemetry, release/health state, architecture metadata and persisted SSE catch-up to the frontend.",
            trust_boundary="browser-facing sanitized API boundary",
            input_contracts=("Sanitized query rows", "Durable event cursor", "WakeupSignal"),
            output_contracts=("REST JSON", "trace_event SSE"),
            activates_on_event_types=(
                "run_started",
                "model_call",
                "decision",
                "tool_proposal",
                "policy_check",
                "tool_call",
                "tool_result",
                "observation",
                "state_change",
                "escalation",
                "final_response",
                "error",
                "run_finished",
            ),
            execution_role="telemetry",
        ),
    )


def _edges() -> tuple[ArchitectureEdge, ...]:
    return (
        ArchitectureEdge(source="operator_frontend", target="product_api", label="RunSubmission / authenticated product traffic"),
        ArchitectureEdge(source="product_api", target="runtime_identity", label="Verify trusted request context"),
        ArchitectureEdge(source="runtime_identity", target="postgres_operational_store", label="Server-owned user/org/permission scope"),
        ArchitectureEdge(source="product_api", target="postgres_operational_store", label="Persist ownership / execution state"),
        ArchitectureEdge(source="postgres_operational_store", target="runtime_handoff", label="Durable work item / lease"),
        ArchitectureEdge(source="product_api", target="realtime_runtime", label="ProductionRequest"),
        ArchitectureEdge(source="runtime_handoff", target="realtime_runtime", label="Generation-fenced RuntimeLease"),
        ArchitectureEdge(source="realtime_runtime", target="decision_source", label="ControllerContext"),
        ArchitectureEdge(source="decision_source", target="agent_controller", label="ControllerDecision"),
        ArchitectureEdge(source="agent_controller", target="harness_runner", label="ToolProposal"),
        ArchitectureEdge(source="harness_runner", target="tool_registry", label="ToolSpec lookup"),
        ArchitectureEdge(source="tool_registry", target="safety_envelope", label="Validated proposal"),
        ArchitectureEdge(source="safety_envelope", target="action_control", label="Govern consequential write"),
        ArchitectureEdge(source="safety_envelope", target="tractian_transport", label="Authorized read BoundRequest"),
        ArchitectureEdge(source="action_control", target="tractian_transport", label="Confirmed lease-fenced write BoundRequest"),
        ArchitectureEdge(source="tractian_transport", target="normalized_evidence", label="TransportResponse"),
        ArchitectureEdge(source="normalized_evidence", target="agent_controller", label="ControllerObservation"),
        ArchitectureEdge(source="harness_runner", target="run_trace", label="TraceEvent"),
        ArchitectureEdge(source="agent_controller", target="run_trace", label="Controller TraceEvent"),
        ArchitectureEdge(source="action_control", target="postgres_operational_store", label="Custody / idempotency / action state"),
        ArchitectureEdge(source="run_trace", target="production_evaluator", label="Completed RunTrace"),
        ArchitectureEdge(source="run_trace", target="observability_projector", label="Runtime projection"),
        ArchitectureEdge(source="production_evaluator", target="observability_projector", label="Post-runtime evaluation projection"),
        ArchitectureEdge(source="observability_projector", target="observability_store", label="Safe projection"),
        ArchitectureEdge(source="observability_store", target="realtime_wakeup", label="Commit then wake"),
        ArchitectureEdge(source="observability_store", target="observability_api", label="Durable sanitized query / cursor catch-up"),
        ArchitectureEdge(source="realtime_wakeup", target="observability_api", label="Wake-up only"),
        ArchitectureEdge(source="observability_api", target="operator_frontend", label="REST / SSE"),
        ArchitectureEdge(source="semantic_review", target="postgres_operational_store", label="Human calibration state"),
        ArchitectureEdge(source="operational_value", target="postgres_operational_store", label="Paired operational-study state"),
    )


def architecture_manifest(
    *,
    provider_selection_state: ProviderSelectionState = "NO_SELECTION",
) -> ArchitectureManifest:
    components = _components()
    edges = _edges()
    component_ids = {component.component_id for component in components}
    for edge in edges:
        if edge.source not in component_ids or edge.target not in component_ids:
            raise ValueError("architecture edge references unknown component")

    payload = {
        "schema_version": "architecture-manifest-v1",
        "architecture_version": "tractian-production-architecture-v1",
        "provider_selection_state": provider_selection_state,
        "components": [component.model_dump(mode="json") for component in components],
        "edges": [edge.model_dump(mode="json") for edge in edges],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return ArchitectureManifest(
        provider_selection_state=provider_selection_state,
        components=components,
        edges=edges,
        manifest_sha256=sha256(raw.encode("utf-8")).hexdigest(),
    )
