from __future__ import annotations

from datetime import UTC, datetime

from academy_tractian.tractian_campaign_evidence import (
    CampaignEvidenceLedger,
    CampaignProofRecord,
)
from academy_tractian.tractian_integration_campaign import (
    build_tractian_integration_campaign_report,
)
from academy_tractian.tractian_integration_evidence import (
    IntegrationEvidenceLedger,
    OperationEvidence,
)
from research.e2.models import ToolKind
from research.e2.tool_registry import TOOLS


FINGERPRINT = "sha256:" + "0" * 64
_SEMANTIC_DIMENSIONS = (
    "invalid_parameters_rejected",
    "response_normalization_verified",
    "agent_evaluator_behavior_verified",
)


def _record(
    *,
    operation: str,
    method: str,
    path_template: str,
    outcome: str,
    http_status: int | None = None,
) -> OperationEvidence:
    return OperationEvidence.model_validate(
        {
            "operation": operation,
            "environment": "hosted_live",
            "outcome": outcome,
            "method": method,
            "path_template": path_template,
            "observed_at": datetime(2026, 9, 4, tzinfo=UTC),
            "probe_id": f"probe-{operation}-{outcome}",
            "evidence_ref": f"postgres://safe-ledger/{operation}/{outcome}",
            "fingerprint": FINGERPRINT,
            "http_status": http_status,
        }
    )


def _semantic_record(
    *,
    operation: str,
    dimension: str,
    passed: bool = True,
) -> CampaignProofRecord:
    return CampaignProofRecord.model_validate(
        {
            "operation": operation,
            "dimension": dimension,
            "environment": "hosted_live",
            "passed": passed,
            "observed_at": datetime(2026, 9, 4, tzinfo=UTC),
            "probe_id": f"semantic-{operation}-{dimension}-{'pass' if passed else 'fail'}",
            "evidence_ref": f"postgres://semantic/{operation}/{dimension}/{passed}",
            "fingerprint": FINGERPRINT,
        }
    )


def _ledger(*records: OperationEvidence) -> IntegrationEvidenceLedger:
    return IntegrationEvidenceLedger(
        source_label="test:hosted-live",
        state="VALID",
        records=records,
    )


def _semantic_ledger(*records: CampaignProofRecord) -> CampaignEvidenceLedger:
    return CampaignEvidenceLedger(
        source_label="test:semantic",
        state="VALID",
        records=records,
    )


def _fully_proven_transport() -> IntegrationEvidenceLedger:
    records: list[OperationEvidence] = []
    for tool in TOOLS:
        records.append(
            _record(
                operation=tool.name,
                method=tool.method,
                path_template=tool.path_template,
                outcome="success",
                http_status=200,
            )
        )
        records.append(
            _record(
                operation=tool.name,
                method=tool.method,
                path_template=tool.path_template,
                outcome="http_error_observed",
                http_status=400,
            )
        )
        if tool.kind is ToolKind.ACTION:
            records.append(
                _record(
                    operation=tool.name,
                    method=tool.method,
                    path_template=tool.path_template,
                    outcome="blocked_by_safety",
                )
            )
    return _ledger(*records)


def _fully_proven_semantics() -> CampaignEvidenceLedger:
    return _semantic_ledger(
        *(
            _semantic_record(operation=tool.name, dimension=dimension)
            for tool in TOOLS
            for dimension in _SEMANTIC_DIMENSIONS
        )
    )


def _operation(report, name: str):
    return next(item for item in report.operations if item.operation == name)


def _dimension(operation, name: str):
    return next(item for item in operation.dimensions if item.name == name)


def test_campaign_enumerates_exact_canonical_18_and_never_assumes_integration() -> None:
    report = build_tractian_integration_campaign_report()

    assert report.schema_version == "tractian-integration-campaign-v3"
    assert report.normalized_operations == 18
    assert len(report.operations) == 18
    assert report.reads == 13
    assert report.actions == 5
    assert report.transport_complete_operations == 0
    assert report.semantic_complete_operations == 0
    assert report.complete_operations == 0
    assert report.incomplete_operations == 18
    assert report.transport_evidence_state == "VALID"
    assert report.semantic_evidence_state == "VALID"
    assert report.transport_completion_status == "TRANSPORT_NOT_STARTED_0_OF_18"
    assert report.semantic_completion_status == "SEMANTIC_NOT_STARTED_0_OF_18"
    assert len({item.operation for item in report.operations}) == 18
    assert all(not item.transport_complete for item in report.operations)
    assert all(not item.semantic_complete for item in report.operations)


def test_transport_success_only_proves_route_and_success_not_semantic_dimensions() -> None:
    report = build_tractian_integration_campaign_report(
        hosted_evidence=_ledger(
            _record(
                operation="get_asset",
                method="GET",
                path_template="/assets/{assetId}",
                outcome="success",
                http_status=200,
            )
        )
    )
    operation = _operation(report, "get_asset")

    assert _dimension(operation, "canonical_route_observed").state == "PASS"
    assert _dimension(operation, "valid_request_success").state == "PASS"
    assert _dimension(operation, "http_error_behavior_observed").state == "UNPROVEN"
    assert _dimension(operation, "invalid_parameters_rejected").state == "UNPROVEN"
    assert _dimension(operation, "response_normalization_verified").state == "UNPROVEN"
    assert _dimension(operation, "agent_evaluator_behavior_verified").state == "UNPROVEN"
    assert operation.transport_complete is False
    assert operation.semantic_complete is False
    assert operation.complete is False
    assert report.transport_completion_status == "TRANSPORT_PARTIAL_0_OF_18"
    assert report.semantic_completion_status == "SEMANTIC_NOT_STARTED_0_OF_18"


def test_http_error_proves_route_and_error_behavior_but_not_success() -> None:
    report = build_tractian_integration_campaign_report(
        hosted_evidence=_ledger(
            _record(
                operation="get_asset",
                method="GET",
                path_template="/assets/{assetId}",
                outcome="http_error_observed",
                http_status=401,
            )
        )
    )
    operation = _operation(report, "get_asset")

    assert _dimension(operation, "canonical_route_observed").state == "PASS"
    assert _dimension(operation, "http_error_behavior_observed").state == "PASS"
    assert _dimension(operation, "valid_request_success").state == "UNPROVEN"
    assert operation.transport_complete is False


def test_safety_block_is_action_evidence_but_not_transport_completion() -> None:
    report = build_tractian_integration_campaign_report(
        hosted_evidence=_ledger(
            _record(
                operation="update_asset_config",
                method="PATCH",
                path_template="/assets/{assetId}",
                outcome="blocked_by_safety",
            )
        )
    )
    operation = _operation(report, "update_asset_config")

    assert operation.kind == "action"
    assert _dimension(operation, "safe_action_control_observed").state == "PASS"
    assert _dimension(operation, "canonical_route_observed").state == "UNPROVEN"
    assert _dimension(operation, "valid_request_success").state == "UNPROVEN"
    assert operation.transport_complete is False
    assert operation.complete is False


def test_invalid_transport_ledger_fails_closed_to_zero_transport_claims() -> None:
    report = build_tractian_integration_campaign_report(
        hosted_evidence=IntegrationEvidenceLedger(
            source_label="test:tampered",
            state="INVALID",
            validation_errors=("contract:route_mismatch",),
        )
    )

    assert report.transport_evidence_state == "INVALID"
    assert report.transport_completion_status == "TRANSPORT_INVALID_EVIDENCE"
    assert report.transport_complete_operations == 0
    assert report.complete_operations == 0
    assert all(
        _dimension(operation, "canonical_route_observed").state == "UNPROVEN"
        for operation in report.operations
    )


def test_semantic_proof_is_independent_and_cannot_upgrade_missing_transport() -> None:
    semantic = _semantic_ledger(
        *(
            _semantic_record(operation="get_asset", dimension=dimension)
            for dimension in _SEMANTIC_DIMENSIONS
        )
    )
    report = build_tractian_integration_campaign_report(campaign_evidence=semantic)
    operation = _operation(report, "get_asset")

    assert operation.semantic_complete is True
    assert operation.transport_complete is False
    assert operation.complete is False
    assert report.semantic_complete_operations == 1
    assert report.transport_complete_operations == 0
    assert report.complete_operations == 0
    assert report.semantic_completion_status == "SEMANTIC_PARTIAL_1_OF_18"


def test_invalid_semantic_ledger_fails_closed() -> None:
    report = build_tractian_integration_campaign_report(
        campaign_evidence=CampaignEvidenceLedger(
            source_label="test:invalid-semantic",
            state="INVALID",
            validation_errors=("contract:unknown_operation",),
        )
    )

    assert report.semantic_evidence_state == "INVALID"
    assert report.semantic_completion_status == "SEMANTIC_INVALID_EVIDENCE"
    assert report.semantic_complete_operations == 0
    assert all(not operation.semantic_complete for operation in report.operations)


def test_semantic_failure_dominates_prior_pass_for_same_dimension() -> None:
    records = [
        _semantic_record(operation="get_asset", dimension=dimension)
        for dimension in _SEMANTIC_DIMENSIONS
    ]
    records.append(
        _semantic_record(
            operation="get_asset",
            dimension="response_normalization_verified",
            passed=False,
        )
    )
    report = build_tractian_integration_campaign_report(
        campaign_evidence=_semantic_ledger(*records)
    )
    operation = _operation(report, "get_asset")

    assert _dimension(operation, "response_normalization_verified").state == "FAIL"
    assert operation.semantic_complete is False
    assert report.semantic_complete_operations == 0


def test_exact_18_of_18_requires_both_transport_and_semantic_proof_for_every_operation() -> None:
    report = build_tractian_integration_campaign_report(
        hosted_evidence=_fully_proven_transport(),
        campaign_evidence=_fully_proven_semantics(),
    )

    assert report.transport_complete_operations == 18
    assert report.semantic_complete_operations == 18
    assert report.complete_operations == 18
    assert report.incomplete_operations == 0
    assert report.transport_completion_status == "TRANSPORT_COMPLETE_18_OF_18"
    assert report.semantic_completion_status == "SEMANTIC_COMPLETE_18_OF_18"
    assert all(operation.transport_complete for operation in report.operations)
    assert all(operation.semantic_complete for operation in report.operations)
    assert all(operation.complete for operation in report.operations)
