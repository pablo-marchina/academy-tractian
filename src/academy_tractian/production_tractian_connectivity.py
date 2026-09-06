from __future__ import annotations

import json
import os
from typing import Protocol

from research.e2.models import BoundRequest, ExecutionBinding
from research.e2.tool_registry import get_tool
from research.e2.transport import build_b0_request

from .production_config import RemoteProductionConfig
from .tractian_transport import ProductionTractianTransport


PROBE_OPERATION = "search_knowledge"
PROBE_QUERY = {"q": "bearing"}
_PROBE_IDENTITY_ID = "production-tractian-connectivity"
_PROBE_USER_ID = "academy-production-connectivity-probe"


class _Transport(Protocol):
    def request(self, request: BoundRequest): ...  # noqa: ANN201


def build_probe_request() -> BoundRequest:
    """Build the read-only probe through the same deterministic binder as runtime tool calls."""

    return build_b0_request(
        get_tool(PROBE_OPERATION),
        dict(PROBE_QUERY),
        ExecutionBinding(
            identity_id=_PROBE_IDENTITY_ID,
            user_id=_PROBE_USER_ID,
            seed=None,
        ),
    )


def run_probe(transport: _Transport) -> dict[str, object]:
    """Prove authenticated TRACTIAN reachability without retaining upstream content."""

    response = transport.request(build_probe_request())
    if response.status_code != 200:
        raise RuntimeError(f"tractian_connectivity_probe_failed:http_{response.status_code}")

    return {
        "schema_version": "production-tractian-connectivity-smoke-v2",
        "status": "PASS",
        "operation": PROBE_OPERATION,
        "http_status": 200,
        "request_bound_by_runtime_contract": True,
        "synthetic_probe_identity": True,
        "response_body_recorded": False,
        "response_headers_recorded": False,
        "credentials_recorded": False,
    }


def main() -> None:
    config = RemoteProductionConfig.from_env(os.environ)
    if not config.tractian_transport_enabled:
        raise RuntimeError("tractian_connectivity_probe_failed:transport_disabled")
    if config.tractian_base_url is None:
        raise RuntimeError("tractian_connectivity_probe_failed:base_url_missing")

    transport = ProductionTractianTransport(
        base_url=config.tractian_base_url,
        server_headers=config.tractian_server_headers(),
    )
    print(json.dumps(run_probe(transport), sort_keys=True))


if __name__ == "__main__":
    main()
