from __future__ import annotations

import pytest

from academy_tractian.hosted_integration_evidence_recorder import (
    EvidenceRecordingTractianTransport,
    HostedIntegrationEvidenceRecorder,
)
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse


class StaticTransport:
    def __init__(self, response: TransportResponse) -> None:
        self.response = response

    def request(self, request: BoundRequest) -> TransportResponse:
        return self.response


class BrokenTransport:
    def request(self, request: BoundRequest) -> TransportResponse:
        raise RuntimeError("SUPER-SECRET-TRANSPORT-FAILURE")


def _request(
    *,
    method: str = "GET",
    path: str = "/companies/acme",
    body: dict[str, object] | None = None,
) -> BoundRequest:
    return BoundRequest(method=method, path=path, body=body)


def test_successful_canonical_request_records_safe_hosted_success() -> None:
    recorder = HostedIntegrationEvidenceRecorder()
    transport = EvidenceRecordingTractianTransport(
        StaticTransport(TransportResponse(status_code=200, headers={}, body={"secret": "raw"})),
        recorder,
    )

    response = transport.request(_request())
    ledger = recorder.ledger()

    assert response.status_code == 200
    assert ledger.state == "VALID"
    assert ledger.unique_route_observed_operations("hosted_live") == {"get_company"}
    assert ledger.unique_success_operations("hosted_live") == {"get_company"}
    assert "raw" not in repr(ledger.records)


def test_http_error_records_route_observation_without_success() -> None:
    recorder = HostedIntegrationEvidenceRecorder()
    transport = EvidenceRecordingTractianTransport(
        StaticTransport(TransportResponse(status_code=503, headers={}, body={"detail": "down"})),
        recorder,
    )

    transport.request(_request())
    ledger = recorder.ledger()

    assert ledger.unique_route_observed_operations("hosted_live") == {"get_company"}
    assert ledger.unique_success_operations("hosted_live") == set()
    assert ledger.unique_outcome_operations("hosted_live", "http_error_observed") == {
        "get_company"
    }


def test_transport_failure_is_recorded_but_does_not_prove_route_observation() -> None:
    recorder = HostedIntegrationEvidenceRecorder()
    transport = EvidenceRecordingTractianTransport(BrokenTransport(), recorder)

    with pytest.raises(RuntimeError, match="SUPER-SECRET-TRANSPORT-FAILURE"):
        transport.request(_request())

    ledger = recorder.ledger()
    assert ledger.state == "VALID"
    assert ledger.unique_route_observed_operations("hosted_live") == set()
    assert ledger.unique_outcome_operations("hosted_live", "transport_failure") == {
        "get_company"
    }
    assert "SUPER-SECRET-TRANSPORT-FAILURE" not in repr(ledger)


def test_recorder_never_stores_request_query_headers_or_body() -> None:
    recorder = HostedIntegrationEvidenceRecorder()
    transport = EvidenceRecordingTractianTransport(
        StaticTransport(TransportResponse(status_code=202, headers={}, body=None)),
        recorder,
    )
    request = BoundRequest(
        method="PATCH",
        path="/assets/asset-1",
        query={"token": "QUERY-SECRET"},
        headers={"Authorization": "Bearer HEADER-SECRET"},
        body={"justification": "BODY-SECRET"},
    )

    transport.request(request)
    text = repr(recorder.ledger())

    assert "update_asset_config" in text
    assert "QUERY-SECRET" not in text
    assert "HEADER-SECRET" not in text
    assert "BODY-SECRET" not in text


def test_unknown_runtime_route_invalidates_live_ledger_fail_closed() -> None:
    recorder = HostedIntegrationEvidenceRecorder()
    transport = EvidenceRecordingTractianTransport(
        StaticTransport(TransportResponse(status_code=200, headers={}, body=None)),
        recorder,
    )

    transport.request(_request(path="/not-a-canonical-route"))
    ledger = recorder.ledger()

    assert ledger.state == "INVALID"
    assert ledger.records == ()
    assert ledger.validation_errors == ("runtime:canonical_route_resolution_failed",)


def test_records_are_coalesced_by_operation_and_outcome_for_bounded_memory() -> None:
    recorder = HostedIntegrationEvidenceRecorder()
    transport = EvidenceRecordingTractianTransport(
        StaticTransport(TransportResponse(status_code=200, headers={}, body=None)),
        recorder,
    )

    for _ in range(50):
        transport.request(_request())

    ledger = recorder.ledger()
    assert ledger.state == "VALID"
    assert len(ledger.records) == 1
    assert ledger.records[0].operation == "get_company"
