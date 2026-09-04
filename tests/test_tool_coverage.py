from __future__ import annotations

from academy_tractian.tool_coverage import build_tractian_tool_coverage
from academy_tractian.tractian_integration_evidence import parse_integration_evidence_document


FINGERPRINT = "sha256:" + ("b" * 64)


def _hosted_ledger(records: list[dict[str, object]]):
    return parse_integration_evidence_document(
        {
            "schema_version": "tractian-integration-evidence-v1",
            "records": records,
        },
        source_label="test:hosted",
        expected_environment="hosted_live",
    )


def _record(
    operation: str,
    method: str,
    path_template: str,
    outcome: str,
    *,
    http_status: int | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "operation": operation,
        "environment": "hosted_live",
        "outcome": outcome,
        "method": method,
        "path_template": path_template,
        "observed_at": "2026-09-04T12:00:00Z",
        "probe_id": "coverage-test",
        "evidence_ref": "coverage-test-observation",
        "fingerprint": FINGERPRINT,
    }
    if http_status is not None:
        record["http_status"] = http_status
    return record


def test_tool_coverage_preserves_truthful_18_operation_claim_boundary() -> None:
    payload = build_tractian_tool_coverage()
    summary = payload["summary"]

    assert payload["schema_version"] == "tractian-tool-coverage-v2"
    assert payload["status"] == "PARTIAL_INTEGRATED_ROUTE_EVIDENCE"
    assert summary == {
        "normalized_operations": 18,
        "contract_registered": 18,
        "implementation_routes_present": 18,
        "integrated_route_execution_evidenced": 1,
        "integrated_route_execution_not_yet_evidenced": 17,
        "frozen_route_execution_evidenced": 1,
        "hosted_live_exercised": 0,
        "hosted_live_success": 0,
        "hosted_live_http_error_observed": 0,
        "hosted_live_transport_failure": 0,
        "hosted_live_unavailable": 0,
        "hosted_live_blocked_by_safety": 0,
        "hosted_live_not_exercised": 18,
        "actions": 5,
        "reads": 13,
    }

    assert payload["evidence"]["frozen"]["state"] == "VALID"
    assert payload["evidence"]["hosted_live"]["state"] == "VALID"
    operations = payload["operations"]
    assert len(operations) == 18
    assert {item["tool_name"] for item in operations if item["integrated_route_execution_evidenced"]} == {
        "get_asset"
    }
    assert not any(item["hosted_live_exercised"] for item in operations)
    assert all(item["contract_registered"] for item in operations)
    assert all(item["implementation_route_present"] for item in operations)


def test_hosted_evidence_counts_unique_route_observations_without_overclaiming_success() -> None:
    hosted = _hosted_ledger(
        [
            _record("get_company", "GET", "/companies/{companyId}", "success", http_status=200),
            _record("get_company", "GET", "/companies/{companyId}", "success", http_status=200),
            _record("get_asset", "GET", "/assets/{assetId}", "http_error_observed", http_status=503),
            _record(
                "update_asset_config",
                "PATCH",
                "/assets/{assetId}",
                "blocked_by_safety",
            ),
            _record(
                "get_analysis",
                "GET",
                "/analyses/{analysisId}",
                "transport_failure",
            ),
        ]
    )
    assert hosted.state == "VALID"

    payload = build_tractian_tool_coverage(hosted_evidence=hosted)
    summary = payload["summary"]

    assert payload["status"] == "PARTIAL_HOSTED_LIVE_EVIDENCE"
    assert summary["hosted_live_exercised"] == 2
    assert summary["hosted_live_success"] == 1
    assert summary["hosted_live_http_error_observed"] == 1
    assert summary["hosted_live_transport_failure"] == 1
    assert summary["hosted_live_blocked_by_safety"] == 1
    assert summary["hosted_live_not_exercised"] == 16
    # get_asset is present in frozen and hosted evidence, so union coverage is 2,
    # not 3. Duplicate observations also never inflate unique-operation counts.
    assert summary["integrated_route_execution_evidenced"] == 2

    by_name = {item["tool_name"]: item for item in payload["operations"]}
    assert by_name["get_company"]["hosted_live_success"] is True
    assert by_name["get_asset"]["hosted_live_exercised"] is True
    assert by_name["get_asset"]["hosted_live_success"] is False
    assert by_name["update_asset_config"]["hosted_live_blocked_by_safety"] is True
    assert by_name["update_asset_config"]["hosted_live_exercised"] is False
    assert by_name["get_analysis"]["hosted_live_exercised"] is False


def test_invalid_hosted_evidence_is_visible_and_cannot_inflate_coverage() -> None:
    hosted = _hosted_ledger(
        [_record("unknown_operation", "GET", "/unknown", "success", http_status=200)]
    )
    assert hosted.state == "INVALID"

    payload = build_tractian_tool_coverage(hosted_evidence=hosted)

    assert payload["status"] == "EVIDENCE_INVALID_FAIL_CLOSED"
    assert payload["evidence"]["hosted_live"]["state"] == "INVALID"
    assert payload["summary"]["hosted_live_exercised"] == 0
    assert payload["summary"]["hosted_live_success"] == 0
    assert payload["summary"]["integrated_route_execution_evidenced"] == 1
