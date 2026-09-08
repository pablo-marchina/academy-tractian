from __future__ import annotations

import json
import os

from research.e2.controller import ControllerContext
from research.e2.tool_registry import TOOLS

from academy_tractian.decision_source import ProviderCallIdentity
from academy_tractian.provider_clients import ProviderHttpClientError, UrllibProviderJsonTransport
from academy_tractian.release_provider import _provider_audit_model_id
from academy_tractian.release_provider_v13 import Release0ProviderDecisionSourceV13
from academy_tractian.release_provider_v14 import Release0OpenRouterDecisionClientV14


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing:{name}")
    return value


def main() -> int:
    asset_label = os.environ.get("QA_ASSET_LABEL", "B204").strip() or "B204"
    prompt = (
        f"For asset {asset_label}, explain its current condition and what evidence supports that conclusion. "
        "Do not ask me for internal IDs that the system can discover."
    )
    client = Release0OpenRouterDecisionClientV14(
        api_key=required("ACADEMY_PROVIDER_API_TOKEN"),
        transport=UrllibProviderJsonTransport(),
        timeout_seconds=60.0,
    )
    source = Release0ProviderDecisionSourceV13(
        client=client,
        registry={tool.name: tool for tool in TOOLS},
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=_provider_audit_model_id(client.model_id),
            route_id=client.route_id,
            live_call=True,
        ),
    )
    context = ControllerContext(
        user_request=prompt,
        turn_index=0,
        tool_call_count=0,
        observations=(),
    )
    request = source.build_request(context)
    visible_tools = tuple(tool.name for tool in request.tools)

    failure_code = None
    http_status = None
    decision_kind = None
    try:
        decision = source.decide(context)
        decision_kind = decision.kind.value
    except ProviderHttpClientError as exc:
        failure_code = exc.code
        http_status = exc.status_code
    except Exception as exc:
        failure_code = type(exc).__name__

    print(
        json.dumps(
            {
                "schema_version": "openrouter-v14-initial-probe-v1",
                "provider_id": client.provider_id,
                "model_id": client.model_id,
                "route_id": client.route_id,
                "visible_tools": visible_tools,
                "decision_kind": decision_kind,
                "failure_code": failure_code,
                "http_status": http_status,
                "raw_request_recorded": False,
                "raw_response_recorded": False,
                "credentials_recorded": False,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if failure_code is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
