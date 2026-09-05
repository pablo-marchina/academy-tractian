from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from research.e2.models import ToolKind
from research.e2.tool_registry import NORMALIZED_OPERATION_COUNT, TOOLS

from .tractian_campaign_evidence import (
    CampaignEvidenceLedger,
    CampaignProofDimension,
    empty_campaign_evidence,
)
from .tractian_integration_evidence import (
    IntegrationEvidenceLedger,
    empty_hosted_integration_evidence,
)


CampaignDimensionState = Literal["PASS", "FAIL", "UNPROVEN"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CampaignDimension(_StrictModel):
    name: str
    state: CampaignDimensionState
    evidence_source: str


class OperationCampaignStatus(_StrictModel):
    operation: str
    operation_id: str
    kind: str
    method: str
    path_template: str
    dimensions: tuple[CampaignDimension, ...]
    transport_complete: bool
    semantic_complete: bool
    complete: bool


class TractianIntegrationCampaignReport(_StrictModel):
    schema_version: Literal["tractian-integration-campaign-v3"] = "tractian-integration-campaign-v3"
    transport_evidence_state: str
    semantic_evidence_state: str
    transport_completion_status: str
    semantic_completion_status: str
    normalized_operations: int
    reads: int
    actions: int
    transport_complete_operations: int
    transport_incomplete_operations: int
    semantic_complete_operations: int
    semantic_incomplete_operations: int
    complete_operations: int
    incomplete_operations: int
    operations: tuple[OperationCampaignStatus, ...]
    claim_boundary: str


_BASE_DIMENSIONS = (
    "canonical_route_observed",
    "valid_request_success",
    "http_error_behavior_observed",
    "invalid_parameters_rejected",
    "response_normalization_verified",
    "agent_evaluator_behavior_verified",
)
_TRANSPORT_DIMENSIONS = (
    "canonical_route_observed",
    "valid_request_success",
    "http_error_behavior_observed",
)
_SEMANTIC_DIMENSIONS: tuple[CampaignProofDimension, ...] = (
    "invalid_parameters_rejected",
    "response_normalization_verified",
    "agent_evaluator_behavior_verified",
)
_ACTION_DIMENSION = "safe_action_control_observed"


def _semantic_dimension_state(
    *,
    ledger: CampaignEvidenceLedger,
    operation: str,
    dimension: CampaignProofDimension,
) -> tuple[CampaignDimensionState, str]:
    if not ledger.valid:
        return "UNPROVEN", "semantic_evidence_invalid"
    records = ledger.records_for(operation, dimension)
    if not records:
        return "UNPROVEN", "campaign_proof_required"

    # EDD recertification semantics: the newest controlled observation governs the active gate.
    # If PASS and FAIL share the newest timestamp, fail closed because ordering is ambiguous.
    latest_observed_at = max(record.observed_at for record in records)
    latest = tuple(record for record in records if record.observed_at == latest_observed_at)
    if any(not record.passed for record in latest):
        return "FAIL", ledger.source_label
    if any(record.passed for record in latest):
        return "PASS", ledger.source_label
    return "UNPROVEN", "campaign_proof_required"


def _completion_status(
    *,
    prefix: str,
    evidence_state: str,
    complete_operations: int,
    evidence_record_count: int,
) -> str:
    if evidence_state != "VALID":
        return f"{prefix}_INVALID_EVIDENCE"
    if complete_operations == NORMALIZED_OPERATION_COUNT:
        return f"{prefix}_COMPLETE_18_OF_18"
    if complete_operations == 0 and evidence_record_count == 0:
        return f"{prefix}_NOT_STARTED_0_OF_18"
    return f"{prefix}_PARTIAL_{complete_operations}_OF_18"


def build_tractian_integration_campaign_report(
    *,
    hosted_evidence: IntegrationEvidenceLedger | None = None,
    campaign_evidence: CampaignEvidenceLedger | None = None,
) -> TractianIntegrationCampaignReport:
    """Expose separate empirical transport and semantic proof gates for all 18 operations.

    A route definition or registered schema never counts as empirical integration proof. Transport
    requires observed canonical route behavior, successful valid execution and HTTP-error behavior;
    hosted actions additionally require an observed safety block. Semantic completion independently
    requires invalid-parameter rejection, response normalization and agent/evaluator behavior. Any
    invalid ledger fails closed. Semantic recertification uses the newest controlled observation for
    each operation/dimension, with timestamp ties containing any FAIL resolved fail-closed. This lets
    EDD fixes be recertified without deleting historical pass/fail aggregates. Neither route
    registration nor transport telemetry can substitute for semantic proof.
    """

    hosted = hosted_evidence or empty_hosted_integration_evidence()
    semantic = campaign_evidence or empty_campaign_evidence()
    route_observed = hosted.unique_route_observed_operations("hosted_live")
    successes = hosted.unique_success_operations("hosted_live")
    http_errors = hosted.unique_outcome_operations("hosted_live", "http_error_observed")
    safety_blocks = hosted.unique_outcome_operations("hosted_live", "blocked_by_safety")

    operations: list[OperationCampaignStatus] = []
    for tool in TOOLS:
        dimension_states: dict[str, tuple[CampaignDimensionState, str]] = {
            "canonical_route_observed": (
                "PASS" if tool.name in route_observed else "UNPROVEN",
                "hosted_transport_ledger" if tool.name in route_observed else "not_observed",
            ),
            "valid_request_success": (
                "PASS" if tool.name in successes else "UNPROVEN",
                "hosted_transport_ledger" if tool.name in successes else "not_observed",
            ),
            "http_error_behavior_observed": (
                "PASS" if tool.name in http_errors else "UNPROVEN",
                "hosted_transport_ledger" if tool.name in http_errors else "not_observed",
            ),
        }
        for dimension in _SEMANTIC_DIMENSIONS:
            dimension_states[dimension] = _semantic_dimension_state(
                ledger=semantic,
                operation=tool.name,
                dimension=dimension,
            )

        names = list(_BASE_DIMENSIONS)
        transport_names = list(_TRANSPORT_DIMENSIONS)
        if tool.kind is ToolKind.ACTION:
            names.append(_ACTION_DIMENSION)
            transport_names.append(_ACTION_DIMENSION)
            dimension_states[_ACTION_DIMENSION] = (
                "PASS" if tool.name in safety_blocks else "UNPROVEN",
                "hosted_transport_ledger" if tool.name in safety_blocks else "not_observed",
            )

        dimensions = tuple(
            CampaignDimension(
                name=name,
                state=dimension_states[name][0],
                evidence_source=dimension_states[name][1],
            )
            for name in names
        )
        states = {dimension.name: dimension.state for dimension in dimensions}
        transport_complete = all(states[name] == "PASS" for name in transport_names)
        semantic_complete = all(states[name] == "PASS" for name in _SEMANTIC_DIMENSIONS)
        operations.append(
            OperationCampaignStatus(
                operation=tool.name,
                operation_id=tool.operation_id,
                kind=tool.kind.value,
                method=tool.method,
                path_template=tool.path_template,
                dimensions=dimensions,
                transport_complete=transport_complete,
                semantic_complete=semantic_complete,
                complete=transport_complete and semantic_complete,
            )
        )

    transport_complete = sum(operation.transport_complete for operation in operations)
    semantic_complete = sum(operation.semantic_complete for operation in operations)
    complete = sum(operation.complete for operation in operations)
    actions = sum(operation.kind == ToolKind.ACTION.value for operation in operations)
    return TractianIntegrationCampaignReport(
        transport_evidence_state=hosted.state,
        semantic_evidence_state=semantic.state,
        transport_completion_status=_completion_status(
            prefix="TRANSPORT",
            evidence_state=hosted.state,
            complete_operations=transport_complete,
            evidence_record_count=len(hosted.records),
        ),
        semantic_completion_status=_completion_status(
            prefix="SEMANTIC",
            evidence_state=semantic.state,
            complete_operations=semantic_complete,
            evidence_record_count=len(semantic.records),
        ),
        normalized_operations=NORMALIZED_OPERATION_COUNT,
        reads=NORMALIZED_OPERATION_COUNT - actions,
        actions=actions,
        transport_complete_operations=transport_complete,
        transport_incomplete_operations=NORMALIZED_OPERATION_COUNT - transport_complete,
        semantic_complete_operations=semantic_complete,
        semantic_incomplete_operations=NORMALIZED_OPERATION_COUNT - semantic_complete,
        complete_operations=complete,
        incomplete_operations=NORMALIZED_OPERATION_COUNT - complete,
        operations=tuple(operations),
        claim_boundary=(
            "TRANSPORT_COMPLETE_18_OF_18 is emitted only when every canonical operation has empirical "
            "route, valid-success and HTTP-error evidence, with explicit safety control for actions. "
            "SEMANTIC_COMPLETE_18_OF_18 is independent and requires invalid-parameter rejection, response "
            "normalization and agent/evaluator proof for every operation. The active semantic state is "
            "the newest controlled observation per operation/dimension; timestamp ties containing a FAIL "
            "fail closed. Neither route registration nor transport telemetry can substitute for semantic "
            "proof."
        ),
    )
