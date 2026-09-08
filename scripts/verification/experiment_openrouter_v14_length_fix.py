from __future__ import annotations

import json
import os
from collections.abc import Mapping

from research.e2.controller import ControllerContext
from research.e2.tool_registry import TOOLS

from academy_tractian.decision_source import ProviderDecisionPayload
from academy_tractian.provider_clients import ProviderHttpClientError, ProviderHttpRequest, UrllibProviderJsonTransport
from academy_tractian.release_provider_v13 import Release0ProviderDecisionSourceV13
from academy_tractian.release_provider_v14 import Release0OpenRouterDecisionClientV14


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing:{name}")
    return value


def run_variant(*, transport, base: ProviderHttpRequest, variant_id: str, max_tokens: int, reasoning: dict | None) -> dict:
    body = dict(base.body)
    body["max_tokens"] = max_tokens
    if reasoning is None:
        body.pop("reasoning", None)
    else:
        body["reasoning"] = reasoning
    request = ProviderHttpRequest(
        method=base.method,
        url=base.url,
        headers=dict(base.headers),
        body=body,
        timeout_seconds=base.timeout_seconds,
    )
    row = {
        "variant_id": variant_id,
        "max_tokens": max_tokens,
        "reasoning": reasoning,
        "http_status": None,
        "served_model": None,
        "choices_count": None,
        "finish_reason": None,
        "content_present": False,
        "payload_valid": False,
        "decision_kind": None,
        "tool_name": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "reasoning_tokens": None,
        "failure_code": None,
        "raw_provider_material_recorded": False,
    }
    try:
        response = transport.post_json(request)
        row["http_status"] = response.status_code
        body = response.body
        row["served_model"] = body.get("model") if isinstance(body.get("model"), str) else None
        choices = body.get("choices")
        row["choices_count"] = len(choices) if isinstance(choices, list) else None
        usage = body.get("usage") if isinstance(body.get("usage"), Mapping) else {}
        details = usage.get("completion_tokens_details") if isinstance(usage.get("completion_tokens_details"), Mapping) else {}
        row["prompt_tokens"] = usage.get("prompt_tokens") if isinstance(usage.get("prompt_tokens"), int) else None
        row["completion_tokens"] = usage.get("completion_tokens") if isinstance(usage.get("completion_tokens"), int) else None
        row["reasoning_tokens"] = details.get("reasoning_tokens") if isinstance(details.get("reasoning_tokens"), int) else None
        if isinstance(choices, list) and len(choices) == 1 and isinstance(choices[0], Mapping):
            choice = choices[0]
            row["finish_reason"] = choice.get("finish_reason") if isinstance(choice.get("finish_reason"), str) else None
            message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
            content = message.get("content")
            row["content_present"] = isinstance(content, str) and bool(content.strip())
            if row["content_present"]:
                try:
                    decoded = json.loads(content)
                    payload = ProviderDecisionPayload.model_validate(decoded)
                    row["payload_valid"] = True
                    row["decision_kind"] = payload.kind.value
                    row["tool_name"] = payload.tool_name
                except Exception:
                    pass
    except ProviderHttpClientError as exc:
        row["failure_code"] = exc.code
        row["http_status"] = exc.status_code
    return row


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
    )
    context = ControllerContext(user_request=prompt, turn_index=0, tool_call_count=0, observations=())
    provider_request = source.build_request(context)
    base = client.build_http_request(provider_request)

    variants = (
        ("control-1024-default-reasoning", 1024, None),
        ("disable-reasoning-1024", 1024, {"effort": "none", "exclude": True}),
        ("default-reasoning-4096", 4096, None),
    )
    rows = [
        run_variant(
            transport=transport,
            base=base,
            variant_id=variant_id,
            max_tokens=max_tokens,
            reasoning=reasoning,
        )
        for variant_id, max_tokens, reasoning in variants
    ]
    print(
        json.dumps(
            {
                "schema_version": "openrouter-v14-length-fix-experiment-v1",
                "provider_id": client.provider_id,
                "model_id": client.model_id,
                "route_id": client.route_id,
                "visible_tools": [tool.name for tool in provider_request.tools],
                "rows": rows,
                "credentials_recorded": False,
                "raw_request_recorded": False,
                "raw_response_recorded": False,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
