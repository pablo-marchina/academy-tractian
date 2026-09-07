from __future__ import annotations

import math

import pytest

from academy_tractian.tractian_transport import (
    _encode_query,
    _normalize_upstream_response,
)
from research.e2.tool_registry import get_tool


def test_success_status_with_invalid_json_becomes_gateway_failure() -> None:
    response = _normalize_upstream_response(
        200,
        b'{"broken":',
        {"Content-Type": "application/json", "Set-Cookie": "secret"},
    )

    assert response.status_code == 502
    assert response.headers == {"content-type": "application/json"}
    assert response.body == {"error": {"code": "TRACTIAN_RESPONSE_INVALID_JSON"}}
    assert "secret" not in repr(response)


def test_success_status_with_invalid_utf8_becomes_gateway_failure() -> None:
    response = _normalize_upstream_response(
        200,
        b"\xff\xfe",
        {"Content-Type": "application/json"},
    )

    assert response.status_code == 502
    assert response.body == {"error": {"code": "TRACTIAN_RESPONSE_INVALID_UTF8"}}


def test_empty_success_response_remains_empty_success() -> None:
    response = _normalize_upstream_response(204, b"", {})

    assert response.status_code == 204
    assert response.body is None
    assert response.headers == {}


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_query_values_are_rejected(value: float) -> None:
    tool = get_tool("get_baseline")

    with pytest.raises(ValueError, match="must be finite"):
        _encode_query(tool, {"point_id": value})
