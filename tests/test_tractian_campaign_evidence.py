from __future__ import annotations

from datetime import UTC, datetime, timedelta

from academy_tractian.tractian_campaign_evidence import (
    CampaignEvidenceLedger,
    CampaignProofRecord,
    parse_campaign_evidence_document,
)
from academy_tractian.tractian_integration_campaign import (
    build_tractian_integration_campaign_report,
)
from academy_tractian.tractian_integration_evidence import (
    IntegrationEvidenceLedger,
    OperationEvidence,
)


FINGERPRINT = "sha256:" + "1" * 64
NOW = datetime(2026, 9, 4, tzinfo=UTC)


def _semantic(dimension: str, *, passed: bool = True) -> CampaignProofRecord:
    return CampaignProofRecord.model_validate(
        {
            "operation": "get_asset",
            "dimension": dimension,
            "passed": passed,
            "observed_at": NOW,
            "probe_id": f"semantic-{dimension}",
            "evidence_ref": f"safe://campaign/get_asset/{dimension}",
            "fingerprint": FINGERPRINT,
        }
    )


def _transport(outcome: str, status: int) -> OperationEvidence:
    return OperationEvidence.model_validate(
        {
            "operation": "get_asset",
            "environment": "hosted_live",
            "outcome": outcome,
            "method": "GET",
            "path_template": "/assets/{assetId}",
            "observed_at": NOW,
            "probe_id": f"transport-{outcome}",
            "evidence_ref": f"safe://transport/get_asset/{outcome}",
            "fingerprint": FINGERPRINT,
            "http_status": status,
        }
    )


def _dimension(report, name: str):
    operation = next(item for item in report.operations if item.operation == "get_asset")
    return next(item for item in operation.dimensions if item.name == name)


def test_parser_rejects_unknown_operation_atomically() -> None:
    payload = {
        "schema_version": "tractian-campaign-evidence-v1",
        "records": [
            {
                **_semantic("response_normalization_verified").model_dump(mode="json"),
                "operation": "invented_tool",
            }
        ],
    }

    ledger = parse_campaign_evidence_document(payload, source_label="test")

    assert ledger.state == "INVALID"
    assert ledger.records == ()
    assert ledger.validation_errors == ("contract:unknown_operation",)


def test_parser_rejects_raw_payload_fields_without_echoing_secret_value() -> None:
    payload = {
        "schema_version": "tractian-campaign-evidence-v1",
        "records": [
            {
                **_semantic("response_normalization_verified").model_dump(mode="json"),
                "raw_response": "Bearer secret-that-must-not-be-reflected",
            }
        ],
    }

    ledger = parse_campaign_evidence_document(payload, source_label="test")

    assert ledger.state == "INVALID"
    assert ledger.records == ()
    assert all("secret-that-must-not-be-reflected" not in error for error in ledger.validation_errors)


def test_transport_plus_three_semantic_proofs_can_complete_a_read_operation() -> None:
    transport = IntegrationEvidenceLedger(
        source_label="test:transport",
        state="VALID",
        records=(
            _transport("success", 200),
            _transport("http_error_observed", 401),
        ),
    )
    semantic = CampaignEvidenceLedger(
        source_label="test:semantic",
        state="VALID",
        records=(
            _semantic("invalid_parameters_rejected"),
            _semantic("response_normalization_verified"),
            _semantic("agent_evaluator_behavior_verified"),
        ),
    )

    report = build_tractian_integration_campaign_report(
        hosted_evidence=transport,
        campaign_evidence=semantic,
    )
    operation = next(item for item in report.operations if item.operation == "get_asset")

    assert operation.complete is True
    assert all(dimension.state == "PASS" for dimension in operation.dimensions)
    assert report.complete_operations == 1


def test_failed_semantic_proof_dominates_a_pass_at_the_same_timestamp() -> None:
    semantic = CampaignEvidenceLedger(
        source_label="test:semantic",
        state="VALID",
        records=(
            _semantic("response_normalization_verified", passed=True),
            _semantic("response_normalization_verified", passed=False),
        ),
    )

    report = build_tractian_integration_campaign_report(campaign_evidence=semantic)

    assert _dimension(report, "response_normalization_verified").state == "FAIL"
    assert report.complete_operations == 0


def test_newer_pass_recertifies_an_older_failure_without_deleting_history() -> None:
    older_failure = _semantic("response_normalization_verified", passed=False)
    newer_pass = _semantic("response_normalization_verified", passed=True).model_copy(
        update={
            "observed_at": NOW + timedelta(minutes=1),
            "probe_id": "semantic-response-normalization-recertified",
        }
    )
    semantic = CampaignEvidenceLedger(
        source_label="test:semantic",
        state="VALID",
        records=(older_failure, newer_pass),
    )

    report = build_tractian_integration_campaign_report(campaign_evidence=semantic)

    assert _dimension(report, "response_normalization_verified").state == "PASS"
    assert len(semantic.records) == 2


def test_newer_failure_revokes_an_older_pass() -> None:
    older_pass = _semantic("response_normalization_verified", passed=True)
    newer_failure = _semantic("response_normalization_verified", passed=False).model_copy(
        update={
            "observed_at": NOW + timedelta(minutes=1),
            "probe_id": "semantic-response-normalization-regressed",
        }
    )
    semantic = CampaignEvidenceLedger(
        source_label="test:semantic",
        state="VALID",
        records=(older_pass, newer_failure),
    )

    report = build_tractian_integration_campaign_report(campaign_evidence=semantic)

    assert _dimension(report, "response_normalization_verified").state == "FAIL"


def test_invalid_semantic_ledger_never_contributes_a_pass() -> None:
    report = build_tractian_integration_campaign_report(
        campaign_evidence=CampaignEvidenceLedger(
            source_label="test:tampered",
            state="INVALID",
            validation_errors=("schema:extra_forbidden",),
        )
    )

    assert report.semantic_evidence_state == "INVALID"
    assert _dimension(report, "response_normalization_verified").state == "UNPROVEN"
