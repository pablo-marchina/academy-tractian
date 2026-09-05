from __future__ import annotations

from copy import deepcopy

from academy_tractian.tractian_integration_evidence import (
    load_frozen_integration_evidence,
    parse_integration_evidence_document,
)


FINGERPRINT = "sha256:" + ("a" * 64)


def _record(
    *,
    operation: str = "get_company",
    environment: str = "hosted_live",
    outcome: str = "success",
    method: str = "GET",
    path_template: str = "/companies/{companyId}",
    http_status: int | None = 200,
) -> dict[str, object]:
    record: dict[str, object] = {
        "operation": operation,
        "environment": environment,
        "outcome": outcome,
        "method": method,
        "path_template": path_template,
        "observed_at": "2026-09-04T12:00:00Z",
        "probe_id": "hosted-read-probe-test",
        "evidence_ref": "test-observation",
        "fingerprint": FINGERPRINT,
    }
    if http_status is not None:
        record["http_status"] = http_status
    return record


def _document(record: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "tractian-integration-evidence-v1",
        "records": [record],
    }


def test_packaged_frozen_evidence_is_valid_and_bounded_to_get_asset() -> None:
    ledger = load_frozen_integration_evidence()

    assert ledger.state == "VALID"
    assert ledger.validation_errors == ()
    assert ledger.unique_route_observed_operations("frozen") == {"get_asset"}
    assert ledger.unique_route_observed_operations("hosted_live") == set()


def test_hosted_success_is_trusted_only_after_schema_contract_and_environment_validation() -> None:
    ledger = parse_integration_evidence_document(
        _document(_record()),
        source_label="test",
        expected_environment="hosted_live",
    )

    assert ledger.state == "VALID"
    assert ledger.unique_route_observed_operations("hosted_live") == {"get_company"}
    assert ledger.unique_success_operations("hosted_live") == {"get_company"}


def test_http_error_response_proves_route_observation_but_not_success() -> None:
    ledger = parse_integration_evidence_document(
        _document(_record(outcome="http_error_observed", http_status=503)),
        source_label="test",
        expected_environment="hosted_live",
    )

    assert ledger.state == "VALID"
    assert ledger.unique_route_observed_operations("hosted_live") == {"get_company"}
    assert ledger.unique_success_operations("hosted_live") == set()


def test_safety_blocked_action_does_not_count_as_hosted_route_execution() -> None:
    ledger = parse_integration_evidence_document(
        _document(
            _record(
                operation="update_asset_config",
                outcome="blocked_by_safety",
                method="PATCH",
                path_template="/assets/{assetId}",
                http_status=None,
            )
        ),
        source_label="test",
        expected_environment="hosted_live",
    )

    assert ledger.state == "VALID"
    assert ledger.unique_route_observed_operations("hosted_live") == set()
    assert ledger.unique_outcome_operations("hosted_live", "blocked_by_safety") == {
        "update_asset_config"
    }


def test_unknown_operation_invalidates_whole_document_and_fails_closed() -> None:
    ledger = parse_integration_evidence_document(
        _document(_record(operation="invented_operation")),
        source_label="test",
        expected_environment="hosted_live",
    )

    assert ledger.state == "INVALID"
    assert ledger.records == ()
    assert ledger.validation_errors == ("contract:unknown_operation",)
    assert ledger.unique_route_observed_operations("hosted_live") == set()


def test_route_mismatch_invalidates_whole_document() -> None:
    ledger = parse_integration_evidence_document(
        _document(_record(path_template="/wrong/{companyId}")),
        source_label="test",
        expected_environment="hosted_live",
    )

    assert ledger.state == "INVALID"
    assert ledger.records == ()
    assert ledger.validation_errors == ("contract:route_mismatch",)


def test_wrong_environment_cannot_promote_hosted_live_coverage() -> None:
    ledger = parse_integration_evidence_document(
        _document(_record(environment="frozen")),
        source_label="test",
        expected_environment="hosted_live",
    )

    assert ledger.state == "INVALID"
    assert ledger.records == ()
    assert ledger.validation_errors == ("contract:environment_mismatch",)


def test_extra_raw_payload_field_is_rejected_without_reflecting_secret_value() -> None:
    record = deepcopy(_record())
    record["raw_response"] = "SUPER-SECRET-TOOL-BODY"
    ledger = parse_integration_evidence_document(
        _document(record),
        source_label="test",
        expected_environment="hosted_live",
    )

    assert ledger.state == "INVALID"
    assert ledger.records == ()
    assert any(error.startswith("schema:") for error in ledger.validation_errors)
    assert "SUPER-SECRET-TOOL-BODY" not in repr(ledger.validation_errors)


def test_invalid_http_semantics_fail_closed() -> None:
    ledger = parse_integration_evidence_document(
        _document(_record(outcome="http_error_observed", http_status=200)),
        source_label="test",
        expected_environment="hosted_live",
    )

    assert ledger.state == "INVALID"
    assert ledger.records == ()
