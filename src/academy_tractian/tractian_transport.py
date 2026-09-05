from __future__ import annotations

from collections.abc import Mapping
import ipaddress
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request as UrlRequest, build_opener

from research.e2.models import BoundRequest, ToolSpec
from research.e2.tool_registry import TOOLS, validate_registry
from research.e2.transport import TransportResponse


_MAX_QUERY_BYTES = 8 * 1024
_MAX_BODY_BYTES = 128 * 1024
_MAX_RESPONSE_BYTES = 512 * 1024
_MAX_HEADER_VALUE_BYTES = 4 * 1024
_MAX_USER_ID_BYTES = 256
_DEFAULT_TIMEOUT_SECONDS = 10.0
_ALLOWED_BOUND_HEADERS = frozenset({"x-user-id"})
_SAFE_RESPONSE_HEADERS = frozenset(
    {"content-type", "retry-after", "x-request-id", "x-correlation-id", "traceparent"}
)
_FORBIDDEN_SERVER_HEADERS = frozenset(
    {
        "connection",
        "content-length",
        "content-type",
        "cookie",
        "host",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
        "x-forwarded-for",
        "x-forwarded-host",
        "x-forwarded-proto",
        "x-user-id",
    }
)
_HEADER_NAME = re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")


class _NoRedirectHandler(HTTPRedirectHandler):
    """Never replay server-managed credentials to a redirected origin."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201
        return None


def _validate_remote_https_base_url(value: str) -> str:
    normalized = value.strip().rstrip("/")
    parsed = urlsplit(normalized)
    if parsed.scheme != "https" or parsed.hostname is None:
        raise ValueError("TRACTIAN base URL must be a remote HTTPS URL")
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise ValueError("TRACTIAN base URL must not contain credentials, query or fragment")
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "host.docker.internal", "0.0.0.0"} or host.endswith(".localhost"):
        raise ValueError("TRACTIAN base URL must not resolve through a local-only hostname")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and (address.is_loopback or address.is_unspecified):
        raise ValueError("TRACTIAN base URL must not use a loopback or unspecified IP")
    return normalized


def _validate_header_value(value: str, *, label: str, max_bytes: int = _MAX_HEADER_VALUE_BYTES) -> str:
    if not value or value != value.strip():
        raise ValueError(f"invalid {label}")
    if len(value.encode("utf-8")) > max_bytes:
        raise ValueError(f"invalid {label}")
    if "\r" in value or "\n" in value or any(ord(char) == 0x7F for char in value):
        raise ValueError(f"invalid {label}")
    return value


def _validated_server_headers(headers: Mapping[str, str] | None) -> dict[str, str]:
    sanitized: dict[str, str] = {}
    for raw_name, raw_value in (headers or {}).items():
        name = str(raw_name).strip()
        if not _HEADER_NAME.fullmatch(name):
            raise ValueError("invalid TRACTIAN server-managed header name")
        lowered = name.lower()
        if lowered in _FORBIDDEN_SERVER_HEADERS:
            raise ValueError(f"forbidden TRACTIAN server-managed header: {lowered}")
        if lowered in sanitized:
            raise ValueError(f"duplicate TRACTIAN server-managed header: {lowered}")
        sanitized[lowered] = _validate_header_value(
            str(raw_value),
            label=f"TRACTIAN server-managed header {lowered}",
        )
    return sanitized


def _decode_canonical_segment(segment: str) -> str:
    if not segment:
        raise ValueError("TRACTIAN request path contains an empty segment")
    try:
        decoded = unquote(segment, errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("TRACTIAN request path contains invalid percent encoding") from exc
    if decoded in {".", ".."} or "/" in decoded or "\\" in decoded:
        raise ValueError("TRACTIAN request path contains a forbidden segment")
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in decoded):
        raise ValueError("TRACTIAN request path contains a control character")
    if quote(decoded, safe="") != segment:
        raise ValueError("TRACTIAN request path is not canonically encoded")
    return decoded


def _matches_tool_path(tool: ToolSpec, concrete_path: str) -> bool:
    template_parts = tool.path_template.strip("/").split("/")
    concrete_parts = concrete_path.strip("/").split("/")
    if len(template_parts) != len(concrete_parts):
        return False
    for template, concrete in zip(template_parts, concrete_parts, strict=True):
        if template.startswith("{") and template.endswith("}"):
            try:
                _decode_canonical_segment(concrete)
            except ValueError:
                return False
            continue
        if template != concrete:
            return False
    return True


def _match_canonical_tool(request: BoundRequest) -> ToolSpec:
    validate_registry()
    if request.method not in {"GET", "POST", "PATCH", "PUT", "DELETE"}:
        raise ValueError("TRACTIAN request method is not canonical")
    if not request.path.startswith("/") or request.path.startswith("//"):
        raise ValueError("TRACTIAN request path must be an absolute API path")
    if "?" in request.path or "#" in request.path or "\\" in request.path:
        raise ValueError("TRACTIAN request path contains URL-control syntax")

    matches = [
        tool
        for tool in TOOLS
        if tool.method == request.method and _matches_tool_path(tool, request.path)
    ]
    if len(matches) != 1:
        raise ValueError("TRACTIAN request does not match exactly one canonical operation")
    return matches[0]


def _validate_bound_headers(headers: Mapping[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for raw_name, raw_value in headers.items():
        name = raw_name.lower().strip()
        if name not in _ALLOWED_BOUND_HEADERS:
            raise ValueError(f"caller-controlled TRACTIAN header is forbidden: {name}")
        if name in normalized:
            raise ValueError(f"duplicate caller-controlled TRACTIAN header: {name}")
        normalized[name] = _validate_header_value(
            raw_value,
            label=name,
            max_bytes=_MAX_USER_ID_BYTES,
        )
    if set(normalized) != _ALLOWED_BOUND_HEADERS:
        raise ValueError("TRACTIAN request must contain exactly the runner-bound x-user-id header")
    return normalized


def _encode_query(tool: ToolSpec, query: Mapping[str, Any]) -> str:
    declared = {parameter.name for parameter in tool.parameters if parameter.location == "query"}
    if tool.seed_supported:
        declared.add("seed")
    unknown = sorted(set(query) - declared)
    if unknown:
        raise ValueError(f"TRACTIAN request contains undeclared query parameters: {unknown}")

    pairs: list[tuple[str, str]] = []
    for key, value in query.items():
        if value is None or isinstance(value, (dict, list, tuple, set)):
            raise ValueError(f"TRACTIAN query parameter must be a scalar: {key}")
        if not isinstance(value, (str, int, float, bool)):
            raise ValueError(f"TRACTIAN query parameter has unsupported type: {key}")
        rendered = str(value).lower() if isinstance(value, bool) else str(value)
        if len(rendered.encode("utf-8")) > _MAX_QUERY_BYTES:
            raise ValueError(f"TRACTIAN query parameter is too large: {key}")
        pairs.append((key, rendered))

    encoded = urlencode(pairs)
    if len(encoded.encode("ascii")) > _MAX_QUERY_BYTES:
        raise ValueError("TRACTIAN encoded query exceeds the production limit")
    return encoded


def _encode_body(tool: ToolSpec, body: dict[str, Any] | None) -> bytes | None:
    body_parameters = [parameter for parameter in tool.parameters if parameter.location == "body"]
    required = any(parameter.required for parameter in body_parameters)
    if not body_parameters:
        if body is not None:
            raise ValueError("TRACTIAN canonical operation does not accept a request body")
        return None
    if body is None:
        if required:
            raise ValueError("TRACTIAN canonical operation requires a request body")
        return None
    try:
        encoded = json.dumps(
            body,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("TRACTIAN request body must be finite JSON") from exc
    if len(encoded) > _MAX_BODY_BYTES:
        raise ValueError("TRACTIAN request body exceeds the production limit")
    return encoded


def _safe_response_headers(headers: Any) -> dict[str, str]:
    safe: dict[str, str] = {}
    if headers is None:
        return safe
    for name, value in headers.items():
        lowered = str(name).lower()
        if lowered not in _SAFE_RESPONSE_HEADERS:
            continue
        rendered = str(value).strip()
        if not rendered or len(rendered.encode("utf-8")) > _MAX_HEADER_VALUE_BYTES:
            continue
        if "\r" in rendered or "\n" in rendered:
            continue
        safe[lowered] = rendered
    return safe


def _decode_response_body(raw: bytes, headers: Mapping[str, str]) -> Any:
    if not raw:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return {"error": {"code": "TRACTIAN_RESPONSE_INVALID_UTF8"}}
    content_type = headers.get("content-type", "").lower()
    if "json" in content_type:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"error": {"code": "TRACTIAN_RESPONSE_INVALID_JSON"}}
    return text


class ProductionTractianTransport:
    """Fail-closed production HTTP boundary for the canonical TRACTIAN tool registry.

    The transport does not select tools and does not own action authorization. It accepts only
    already-bound requests that still match the hash-pinned canonical tool contract, injects
    server-managed headers only at the network boundary, never follows redirects, never retries
    automatically, caps request/response sizes and exposes only sanitized response headers.

    `server_headers` deliberately has no assumed authentication scheme. The supplied partner
    contract must determine the exact server-managed credential header before live composition.
    """

    def __init__(
        self,
        *,
        base_url: str,
        server_headers: Mapping[str, str] | None = None,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        if not 0.5 <= timeout_seconds <= 30.0:
            raise ValueError("TRACTIAN timeout must be between 0.5 and 30 seconds")
        self._base_url = _validate_remote_https_base_url(base_url)
        self._server_headers = _validated_server_headers(server_headers)
        self._timeout_seconds = timeout_seconds
        self._opener = build_opener(_NoRedirectHandler())

    def request(self, request: BoundRequest) -> TransportResponse:
        tool = _match_canonical_tool(request)
        bound_headers = _validate_bound_headers(request.headers)
        query = _encode_query(tool, request.query)
        body = _encode_body(tool, request.body)

        url = f"{self._base_url}{request.path}"
        if query:
            url = f"{url}?{query}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "academy-tractian-production/1",
            "x-user-id": bound_headers["x-user-id"],
        }
        for name, value in self._server_headers.items():
            headers[name] = value
        if body is not None:
            headers["Content-Type"] = "application/json"

        network_request = UrlRequest(
            url,
            data=body,
            headers=headers,
            method=request.method,
        )
        try:
            with self._opener.open(network_request, timeout=self._timeout_seconds) as response:
                raw = response.read(_MAX_RESPONSE_BYTES + 1)
                response_headers = _safe_response_headers(response.headers)
                if len(raw) > _MAX_RESPONSE_BYTES:
                    return TransportResponse(
                        502,
                        {"content-type": "application/json"},
                        {"error": {"code": "TRACTIAN_RESPONSE_TOO_LARGE"}},
                    )
                return TransportResponse(
                    int(response.status),
                    response_headers,
                    _decode_response_body(raw, response_headers),
                )
        except HTTPError as exc:
            raw = exc.read(_MAX_RESPONSE_BYTES + 1)
            response_headers = _safe_response_headers(exc.headers)
            if len(raw) > _MAX_RESPONSE_BYTES:
                return TransportResponse(
                    502,
                    {"content-type": "application/json"},
                    {"error": {"code": "TRACTIAN_RESPONSE_TOO_LARGE"}},
                )
            return TransportResponse(
                int(exc.code),
                response_headers,
                _decode_response_body(raw, response_headers),
            )
        except (URLError, TimeoutError, OSError):
            return TransportResponse(
                599,
                {"content-type": "application/json"},
                {"error": {"code": "TRACTIAN_TRANSPORT_UNAVAILABLE"}},
            )
