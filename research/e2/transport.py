from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import quote

from .binding import bind_request, validate_model_arguments
from .models import BoundRequest, ExecutionBinding, ToolKind, ToolSpec

# Frozen E0 behavior: the supplied API accepts seed on stochastic GETs; /users/me
# and all action endpoints do not use it. This is a contract fact, not an agent policy.
SEED_SUPPORTED_READS = frozenset(
    {
        "get_company",
        "list_assets_by_company",
        "get_asset",
        "list_analyses",
        "get_analysis",
        "get_baseline",
        "get_rms",
        "get_spectrum",
        "get_data_quality",
        "get_model",
        "search_knowledge",
        "get_knowledge_doc",
    }
)


@dataclass(frozen=True)
class TransportResponse:
    status_code: int
    headers: dict[str, str]
    body: Any


class RequestTransport(Protocol):
    def request(self, request: BoundRequest) -> TransportResponse: ...


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def build_b0_request(
    tool: ToolSpec,
    arguments: dict[str, Any],
    binding: ExecutionBinding,
) -> BoundRequest:
    """Build a contract-valid HTTP request without B1/B2/B3 policy layers."""
    validate_model_arguments(arguments)
    path = tool.path_template
    query: dict[str, Any] = {}
    body: dict[str, Any] | None = None
    declared = {parameter.name for parameter in tool.parameters}
    unknown = sorted(set(arguments) - declared)
    if unknown:
        raise ValueError(f"unknown arguments for {tool.name}: {unknown}")

    for parameter in tool.parameters:
        if parameter.name not in arguments:
            if parameter.required:
                raise ValueError(f"missing required argument: {parameter.name}")
            continue
        value = arguments[parameter.name]
        if parameter.location == "path":
            path = path.replace(
                "{" + _snake_to_camel(parameter.name) + "}",
                quote(str(value), safe=""),
            )
        elif parameter.location == "query":
            query[parameter.name] = value
        elif parameter.location == "body":
            if not isinstance(value, dict):
                raise ValueError("body must be an object")
            body = value

    bound = bind_request(
        method=tool.method,
        path=path,
        arguments={"query": query, "body": body} if body is not None else {"query": query},
        binding=ExecutionBinding(
            identity_id=binding.identity_id,
            user_id=binding.user_id,
            seed=None,
        ),
    )
    if tool.kind is ToolKind.READ and tool.name in SEED_SUPPORTED_READS and binding.seed is not None:
        bound = bound.model_copy(update={"query": {**bound.query, "seed": binding.seed}})
    return bound


class HttpxTransport:
    """Thin HTTP transport; it is not an agent-runtime decision."""

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = None

    def request(self, request: BoundRequest) -> TransportResponse:
        import httpx

        if self._client is None:
            self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
        response = self._client.request(
            request.method,
            request.path,
            params=request.query,
            headers=request.headers,
            json=request.body,
        )
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return TransportResponse(response.status_code, dict(response.headers), body)


class B0Executor:
    """Minimal benchmark-valid executor; deliberately excludes B1/B2/B3 guards."""

    def __init__(self, registry: dict[str, ToolSpec], transport: RequestTransport) -> None:
        self.registry = registry
        self.transport = transport

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        binding: ExecutionBinding,
    ) -> TransportResponse:
        tool = self.registry[tool_name]
        request = build_b0_request(tool, arguments, binding)
        return self.transport.request(request)
