from __future__ import annotations

from datetime import UTC, datetime

from academy_tractian.tractian_integration_campaign import (
    build_tractian_integration_campaign_report,
)
from academy_tractian.tractian_integration_evidence import (
    IntegrationEvidenceLedger,
    OperationEvidence,
)


FINGERPRINT = "sha256:" + "0" * 64


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
            "probe_id": f"probe-{operation}",
            "evidence_ref": f"postgres://safe-ledger/{operation}/{outcome}",
            "fingerprint": FINGERPRINT,
            "http_status": http_status,
        }
    )


def _ledger(*records: OperationEvidence) -> IntegrationEvidenceLedger:
    return IntegrationEvidenceLedger(
        source_label="test:hosted-live",
        state="VALID",
        records=records,
    )


def _operation(report, name: str):
    return next(item for item in report.operations if item.operation == name)


def _dimension(operation, name: str):
    return next(item for item in operation.dimensions if item.name == name)


def test_campaign_enumerates_exact_canonical_18_and_never_assumes_integration() -> None:
    report = build_tractian_integration_campaign_report()

    assert report.normalized_operations == 18
    assert len(report.operations) == 18
    assert report.reads == 13
    assert report.actions == 5
    assert report.complete_operations == 0
    assert report.incomplete_operations == 18
    assert report.transport_evidence_state == "VALID"
    assert report.semantic_evidence_state == "VALID"
    assert len({item.operation for item in report.operations}) == 18


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
    assert operation.complete is False


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


def test_safety_block_is_action_evidence_but_not_route_execution() -> None:
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
    assert operation.complete is False


def test_invalid_evidence_ledger_fails_closed_to_zero_transport_claims() -> None:
    report = build_tractian_integration_campaign_report(
        hosted_evidence=IntegrationEvidenceLedger(
            source_label="test:tampered",
            state="INVALID",
            validation_errors=("contract:route_mismatch",),
        )
    )

    assert report.transport_evidence_state == "INVALID"
    assert report.complete_operations == 0
    assert all(
        _dimension(operation, "canonical_route_observed").state == "UNPROVEN"
        for operation in report.operations
    )
