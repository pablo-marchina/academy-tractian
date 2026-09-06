from __future__ import annotations

import pytest

from research.e2.transport import TransportResponse
from scripts.production_tractian_connectivity_smoke import build_probe_request, run_probe


class FakeTransport:
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.requests = []

    def request(self, request):  # noqa: ANN001, ANN201
        self.requests.append(request)
        return self.response


def test_probe_uses_only_canonical_read_only_knowledge_search_and_records_no_payload() -> None:
    transport = FakeTransport(
        TransportResponse(
            status_code=200,
            body={"results": [{"id": "private-upstream-body-must-not-be-recorded"}]},
            headers={"x-request-id": "private-upstream-header-must-not-be-recorded"},
        )
    )

    result = run_probe(transport)

    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert request == build_probe_request()
    assert request.method == "GET"
    assert request.path == "/knowledge/search"
    assert request.query == {"q": "bearing"}
    assert request.headers == {}
    assert request.body is None
    assert result == {
        "schema_version": "production-tractian-connectivity-smoke-v1",
        "status": "PASS",
        "operation": "search_knowledge",
        "http_status": 200,
        "response_body_recorded": False,
        "response_headers_recorded": False,
        "credentials_recorded": False,
    }
    rendered = repr(result)
    assert "private-upstream" not in rendered
    assert "results" not in rendered
    assert "x-request-id" not in rendered


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500, 503, 599])
def test_probe_fails_closed_on_every_non_200_without_recording_upstream_content(status: int) -> None:
    transport = FakeTransport(
        TransportResponse(
            status_code=status,
            body={"secret": "must-not-leak"},
            headers={"authorization": "must-not-leak"},
        )
    )

    with pytest.raises(RuntimeError) as exc_info:
        run_probe(transport)

    assert str(exc_info.value) == f"tractian_connectivity_probe_failed:http_{status}"
    assert "must-not-leak" not in str(exc_info.value)
    assert len(transport.requests) == 1
