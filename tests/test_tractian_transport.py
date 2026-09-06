from __future__ import annotations

from io import BytesIO
import json
from urllib.error import HTTPError, URLError

import pytest

import academy_tractian.tractian_transport as tractian_transport
from academy_tractian.tractian_transport import ProductionTractianTransport
from research.e2.models import BoundRequest


class FakeResponse:
    def __init__(
        self,
        *,
        status: int = 200,
        body: bytes = b"{}",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self._body = body
        self.headers = headers or {"Content-Type": "application/json"}

    def read(self, _limit: int = -1) -> bytes:
        return self._body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args) -> None:
        return None


class RecordingOpener:
    def __init__(self, outcome) -> None:  # noqa: ANN001
        self.outcome = outcome
        self.calls: list[tuple[object, float]] = []

    def open(self, request, timeout):  # noqa: ANN001, ANN201
        self.calls.append((request, timeout))
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome


def _transport(monkeypatch: pytest.MonkeyPatch, opener: RecordingOpener, **kwargs) -> ProductionTractianTransport:
    monkeypatch.setattr(tractian_transport, "build_opener", lambda *_handlers: opener)
    return ProductionTractianTransport(
        base_url="https://partner.example.com/api",
        server_headers={"Authorization": "Bearer server-only-secret"},
        **kwargs,
    )


def _get_asset(**overrides) -> BoundRequest:
    values = {
        "method": "GET",
        "path": "/assets/asset-1",
        "query": {"seed": "seed-1"},
        "headers": {"x-user-id": "user-a"},
        "body": None,
    }
    values.update(overrides)
    return BoundRequest.model_validate(values)


def _search_knowledge(**overrides) -> BoundRequest:
    values = {
        "method": "GET",
        "path": "/knowledge/search",
        "query": {"q": "bearing"},
        "headers": {"x-user-id": "probe-user"},
        "body": None,
    }
    values.update(overrides)
    return BoundRequest.model_validate(values)


def _reprocess(**overrides) -> BoundRequest:
    values = {
        "method": "POST",
        "path": "/analyses/analysis-1/reprocess",
        "query": {},
        "headers": {"x-user-id": "user-a"},
        "body": {
            "action": "reprocess",
            "justification": "Reprocess because the current analysis is stale.",
        },
    }
    values.update(overrides)
    return BoundRequest.model_validate(values)


def test_canonical_read_injects_server_header_only_at_network_boundary_and_sanitizes_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opener = RecordingOpener(
        FakeResponse(
            body=json.dumps({"id": "asset-1"}).encode(),
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": "req-1",
                "Set-Cookie": "upstream-secret=must-not-enter-trace",
                "Authorization": "must-not-enter-trace",
            },
        )
    )
    transport = _transport(monkeypatch, opener)
    request = _get_asset()

    response = transport.request(request)

    assert response.status_code == 200
    assert response.body == {"id": "asset-1"}
    assert response.headers == {
        "content-type": "application/json",
        "x-request-id": "req-1",
    }
    assert len(opener.calls) == 1
    network_request, timeout = opener.calls[0]
    assert network_request.full_url == "https://partner.example.com/api/assets/asset-1?seed=seed-1"
    assert network_request.get_method() == "GET"
    assert network_request.get_header("X-user-id") == "user-a"
    assert network_request.get_header("Authorization") == "Bearer server-only-secret"
    assert timeout == 10.0
    assert request.headers == {"x-user-id": "user-a"}
    assert "Authorization" not in request.headers
    assert "server-only-secret" not in repr(response)


def test_static_route_is_preferred_over_parameter_route(monkeypatch: pytest.MonkeyPatch) -> None:
    opener = RecordingOpener(FakeResponse(body=b'{"results":[]}'))
    transport = _transport(monkeypatch, opener)

    response = transport.request(_search_knowledge())

    assert response.status_code == 200
    assert response.body == {"results": []}
    assert len(opener.calls) == 1
    network_request, _timeout = opener.calls[0]
    assert network_request.full_url == "https://partner.example.com/api/knowledge/search?q=bearing"
    assert network_request.get_method() == "GET"
    assert network_request.get_header("X-user-id") == "probe-user"


def test_canonical_action_sends_json_once_and_never_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    opener = RecordingOpener(
        HTTPError(
            "https://partner.example.com/api/analyses/analysis-1/reprocess",
            503,
            "unavailable",
            {"Content-Type": "application/json", "Retry-After": "2"},
            BytesIO(b'{"error":"temporarily unavailable"}'),
        )
    )
    transport = _transport(monkeypatch, opener)

    response = transport.request(_reprocess())

    assert response.status_code == 503
    assert response.headers == {
        "content-type": "application/json",
        "retry-after": "2",
    }
    assert response.body == {"error": "temporarily unavailable"}
    assert len(opener.calls) == 1, "consequential writes must never receive blind retry"
    network_request, _timeout = opener.calls[0]
    assert network_request.get_method() == "POST"
    assert network_request.get_header("Content-type") == "application/json"
    assert json.loads(network_request.data.decode()) == _reprocess().body


def test_read_transport_failure_is_normalized_without_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    opener = RecordingOpener(URLError("network down; do not leak exception text"))
    transport = _transport(monkeypatch, opener)

    response = transport.request(_get_asset())

    assert response.status_code == 599
    assert response.body == {"error": {"code": "TRACTIAN_TRANSPORT_UNAVAILABLE"}}
    assert response.headers == {"content-type": "application/json"}
    assert len(opener.calls) == 1, "read retry requires future measured proof instead of implicit policy"
    assert "network down" not in repr(response)


@pytest.mark.parametrize(
    "bound_request",
    [
        _get_asset(method="POST"),
        _get_asset(path="/unknown/asset-1"),
        _get_asset(path="/assets/../companies"),
        _get_asset(path="/assets/%2e%2e"),
        _get_asset(path="/assets/%2Fadmin"),
        _get_asset(path="//assets/asset-1"),
        _get_asset(path="/assets/asset-1?admin=true"),
        _get_asset(headers={"x-user-id": "user-a", "Authorization": "attacker"}),
        _get_asset(headers={"Authorization": "attacker"}),
        _get_asset(headers={"x-user-id": "user-a\nX-Admin: true"}),
        _get_asset(query={"seed": "seed-1", "admin": "true"}),
        _get_asset(body={"unexpected": True}),
    ],
)
def test_forged_bound_request_is_rejected_before_network(
    monkeypatch: pytest.MonkeyPatch,
    bound_request: BoundRequest,
) -> None:
    opener = RecordingOpener(FakeResponse())
    transport = _transport(monkeypatch, opener)

    with pytest.raises(ValueError):
        transport.request(bound_request)

    assert opener.calls == []


def test_action_missing_body_is_rejected_before_network(monkeypatch: pytest.MonkeyPatch) -> None:
    opener = RecordingOpener(FakeResponse())
    transport = _transport(monkeypatch, opener)

    with pytest.raises(ValueError, match="requires a request body"):
        transport.request(_reprocess(body=None))

    assert opener.calls == []


def test_server_managed_headers_cannot_override_identity_or_http_framing() -> None:
    for header in (
        "x-user-id",
        "Host",
        "Content-Length",
        "Content-Type",
        "Cookie",
        "Transfer-Encoding",
        "X-Forwarded-For",
    ):
        with pytest.raises(ValueError, match="forbidden TRACTIAN server-managed header"):
            ProductionTractianTransport(
                base_url="https://partner.example.com",
                server_headers={header: "attacker-controlled"},
            )


def test_server_managed_secret_header_rejects_newline_injection() -> None:
    with pytest.raises(ValueError, match="server-managed header"):
        ProductionTractianTransport(
            base_url="https://partner.example.com",
            server_headers={"Authorization": "Bearer good\r\nX-Evil: true"},
        )


@pytest.mark.parametrize(
    "base_url",
    [
        "http://partner.example.com",
        "https://localhost/api",
        "https://127.0.0.1/api",
        "https://0.0.0.0/api",
        "https://host.docker.internal/api",
        "https://user:password@partner.example.com/api",
        "https://partner.example.com/api?token=secret",
        "https://partner.example.com/api#fragment",
    ],
)
def test_base_url_must_be_remote_https_without_embedded_credentials(base_url: str) -> None:
    with pytest.raises(ValueError):
        ProductionTractianTransport(base_url=base_url)


def test_response_size_limit_fails_closed_without_exposing_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    opener = RecordingOpener(
        FakeResponse(
            body=b"x" * (tractian_transport._MAX_RESPONSE_BYTES + 1),
            headers={"Content-Type": "text/plain", "Set-Cookie": "secret"},
        )
    )
    transport = _transport(monkeypatch, opener)

    response = transport.request(_get_asset())

    assert response.status_code == 502
    assert response.body == {"error": {"code": "TRACTIAN_RESPONSE_TOO_LARGE"}}
    assert response.headers == {"content-type": "application/json"}
    assert len(opener.calls) == 1


def test_redirect_handler_never_builds_a_followup_request() -> None:
    handler = tractian_transport._NoRedirectHandler()
    assert handler.redirect_request(None, None, 302, "redirect", {}, "https://attacker.example") is None
