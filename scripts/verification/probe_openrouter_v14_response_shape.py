from __future__ import annotations

import json
import os
from collections.abc import Mapping

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


def scalar(value):
    return value if isinstance(value, (str, int, float, bool)) or value is None else type(value).__name__


def main() -> int:
    asset_label = os.environ.get("QA_ASSET_LABEL", "B204").strip() or "B204"
    prompt = (
        f"For asset {asset_label}, explain its current condition and what evidence supports that conclusion. "
        "Do not ask me for internal IDs that the system can discover."
    )
    transport = UrllibProviderJsonTransport()
    client = Release0OpenRouterDecisionClientV14(
        api_key=required("ACADEMY_PROVIDER_API_TOKEN"),
        transport=transport,
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
    http_request = client.build_http_request(request)

    result = {
        "schema_version": "openrouter-v14-response-shape-v1",
        "provider_id": client.provider_id,
        "model_id": client.model_id,
        "route_id": client.route_id,
        "visible_tools": [tool.name for tool in request.tools],
        "http_status": None,
        "top_level_keys": [],
        "served_model": None,
        "object": None,
        "choices_type": None,
        "choices_count": None,
        "choice_types": [],
        "finish_reasons": [],
        "message_types": [],
        "message_roles": [],
        "content_types": [],
        "content_present": [],
        "error_present": False,
        "error_type": None,
        "error_keys": [],
        "error_code": None,
        "error_metadata_keys": [],
        "raw_request_recorded": False,
        "raw_response_recorded": False,
        "credentials_recorded": False,
    }

    try:
        response = transport.post_json(http_request)
        result["http_status"] = response.status_code
        body = response.body
        result["top_level_keys"] = sorted(str(key) for key in body.keys())
        result["served_model"] = scalar(body.get("model"))
        result["object"] = scalar(body.get("object"))
        choices = body.get("choices")
        result["choices_type"] = type(choices).__name__
        if isinstance(choices, list):
            result["choices_count"] = len(choices)
            for choice in choices[:3]:
                result["choice_types"].append(type(choice).__name__)
                if isinstance(choice, Mapping):
                    result["finish_reasons"].append(scalar(choice.get("finish_reason")))
                    message = choice.get("message")
                    result["message_types"].append(type(message).__name__)
                    if isinstance(message, Mapping):
                        result["message_roles"].append(scalar(message.get("role")))
                        content = message.get("content")
                        result["content_types"].append(type(content).__name__)
                        result["content_present"].append(isinstance(content, str) and bool(content.strip()))
        error = body.get("error")
        if error is not None:
            result["error_present"] = True
            result["error_type"] = type(error).__name__
            if isinstance(error, Mapping):
                result["error_keys"] = sorted(str(key) for key in error.keys())
                result["error_code"] = scalar(error.get("code"))
                metadata = error.get("metadata")
                if isinstance(metadata, Mapping):
                    result["error_metadata_keys"] = sorted(str(key) for key in metadata.keys())
    except ProviderHttpClientError as exc:
        result["transport_failure_code"] = exc.code
        result["transport_http_status"] = exc.status_code

    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
