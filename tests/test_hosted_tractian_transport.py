from __future__ import annotations

from email.message import Message
import io
import json
import urllib.error

import pytest

from research.e2.models import BoundRequest

from academy_tractian.hosted_tractian_transport import HostedTractianTransport


class _Response:
    def __init__(self, *, status: int, payload: object) -> None:
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = "application/json"
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self._body


def test_hosted_tractian_transport_builds_https_request_without_leaking_credentials(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["authorization"] = request.get_header("Authorization")
        captured["body"] = request.data
        captured["timeout"] = timeout
        return _Response(status=200, payload={"assetId": "asset-1"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    transport = HostedTractianTransport(
        base_url="https://tractian.example.com",
        bearer_token="secret-token",
        timeout_seconds=12,
    )
    response = transport.request(
        BoundRequest(
            method="GET",
            path="/assets/asset-1",
            query={"seed": "safe-seed-ref"},
            headers={},
            body=None,
        )
    )

    assert response.status_code == 200
    assert response.body == {"assetId": "asset-1"}
    assert captured == {
        "url": "https://tractian.example.com/assets/asset-1?seed=safe-seed-ref",
        "method": "GET",
        "authorization": "Bearer secret-token",
        "body": None,
        "timeout": 12.0,
    }
    assert "secret-token" not in repr(transport)


def test_hosted_tractian_transport_returns_http_error_as_observation(monkeypatch) -> None:
    def fake_urlopen(request, timeout):
        del timeout
        body = io.BytesIO(b'{"error":"temporary"}')
        raise urllib.error.HTTPError(
            request.full_url,
            503,
            "Service Unavailable",
            Message(),
            body,
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    response = HostedTractianTransport(base_url="https://tractian.example.com").request(
        BoundRequest(method="GET", path="/assets/asset-1", query={}, headers={}, body=None)
    )

    assert response.status_code == 503
    assert response.body == {"error": "temporary"}


def test_hosted_tractian_transport_rejects_non_https_or_embedded_credentials() -> None:
    with pytest.raises(ValueError, match="absolute HTTPS"):
        HostedTractianTransport(base_url="http://tractian.example.com")
    with pytest.raises(ValueError, match="forbidden components"):
        HostedTractianTransport(base_url="https://user:pass@tractian.example.com")
