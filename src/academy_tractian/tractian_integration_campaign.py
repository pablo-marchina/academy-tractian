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
    complete: bool


class TractianIntegrationCampaignReport(_StrictModel):
    schema_version: Literal["tractian-integration-campaign-v2"] = "tractian-integration-campaign-v2"
    transport_evidence_state: str
    semantic_evidence_state: str
    normalized_operations: int
    reads: int
    actions: int
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
    if any(not record.passed for record in records):
        return "FAIL", ledger.source_label
    if any(record.passed for record in records):
        return "PASS", ledger.source_label
    return "UNPROVEN", "campaign_proof_required"


def build_tractian_integration_campaign_report(
    *,
    hosted_evidence: IntegrationEvidenceLedger | None = None,
    campaign_evidence: CampaignEvidenceLedger | None = None,
) -> TractianIntegrationCampaignReport:
    """Expose exactly what remains to prove for each of the 18 TRACTIAN operations.

    Transport evidence and semantic campaign evidence have separate trust units.
    A semantic failure dominates a prior pass for the same operation/dimension,
    and either invalid ledger fails closed without increasing completion claims.
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
        if tool.kind is ToolKind.ACTION:
            names.append(_ACTION_DIMENSION)
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
        operations.append(
            OperationCampaignStatus(
                operation=tool.name,
                operation_id=tool.operation_id,
                kind=tool.kind.value,
                method=tool.method,
                path_template=tool.path_template,
                dimensions=dimensions,
                complete=all(dimension.state == "PASS" for dimension in dimensions),
            )
        )

    complete = sum(operation.complete for operation in operations)
    actions = sum(operation.kind == ToolKind.ACTION.value for operation in operations)
    return TractianIntegrationCampaignReport(
        transport_evidence_state=hosted.state,
        semantic_evidence_state=semantic.state,
        normalized_operations=NORMALIZED_OPERATION_COUNT,
        reads=NORMALIZED_OPERATION_COUNT - actions,
        actions=actions,
        complete_operations=complete,
        incomplete_operations=NORMALIZED_OPERATION_COUNT - complete,
        operations=tuple(operations),
        claim_boundary=(
            "Transport evidence proves route/success/error observations and explicit safety blocks; "
            "bounded semantic campaign evidence separately proves invalid-parameter handling, response "
            "normalization, and agent/evaluator behavior. A missing, invalid, or failing proof never "
            "increases the 18/18 claim."
        ),
    )
