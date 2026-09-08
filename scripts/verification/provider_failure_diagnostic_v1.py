#!/usr/bin/env python3
from __future__ import annotations

"""Causal diagnostic for Groq GPT-OSS provider failures.

This is NOT a promotion benchmark. It records only sanitized structural diagnostics and never
retries, repairs, or persists raw provider content. The frozen V3 population/rubric is reused only
to make diagnostic outcomes interpretable.
"""

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import time
from typing import Any, Mapping
import urllib.error
import urllib.request

from pydantic import ValidationError

from academy_tractian.decision_source import (
    ProviderDecisionPayload,
    build_provider_decision_request,
)
from academy_tractian.provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
)
from academy_tractian.provider_tournament_v3 import (
    POPULATION_SHA256,
    adjudicate_v3_rubric,
    context_for_unit,
    load_frozen_tournament_v3,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerDecision, ControllerDecisionKind, ToolProposal

SCHEMA_VERSION = "provider-failure-diagnostic-v1"
MODEL_ID = "openai/gpt-oss-120b"
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
USER_AGENT = "academy-tractian-provider-diagnostic/1.0"
TPM_LIMIT = 8000.0
PACING_MARGIN_SECONDS = 1.0
TARGET_UNITS = (
    "T3-01-COMPANY-CONTEXT",       # clean control
    "T3-06-ANALYSIS-DETAIL",       # observed payload/finish failures
    "T3-09-SPECTRUM",              # observed payload failure
    "T3-11-MODEL",                 # observed payload failure
    "T3-12-KNOWLEDGE-SEARCH",      # observed payload failure
    "T3-15-UPSTREAM-UNAVAILABLE",  # repeated finish failure / wrong safe terminal
    "T3-17-ACTION-GOVERNANCE",     # repeated payload/finish failure
)


@dataclass(frozen=True)
class Config:
    config_id: str
    max_completion_tokens: int
    reasoning_effort_api: str | None
    reasoning_instruction: str


CONFIGS = (
    Config("baseline-best-effort-medium-512", 512, None, "medium"),
    Config("budget-best-effort-medium-2048", 2048, None, "medium"),
    Config("reasoning-best-effort-low-2048", 2048, "low", "low"),
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _request_text(request: Any) -> str:
    return _canonical_json(request.model_dump(mode="json"))


def _http(body: dict[str, Any], api_key: str) -> tuple[int, dict[str, Any], int, dict[str, str]]:
    encoded = _canonical_json(body).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=encoded,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    started = time.perf_counter_ns()
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8", errors="replace")
            status = int(response.status)
            headers = {k.casefold(): v for k, v in response.headers.items()}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = int(exc.code)
        headers = {k.casefold(): v for k, v in exc.headers.items()}
    elapsed_ms = max(0, time.perf_counter_ns() - started) // 1_000_000
    try:
        decoded = json.loads(raw)
    except Exception:
        decoded = {"_non_json": True, "_body_sha256": sha256(raw.encode("utf-8")).hexdigest()}
    if not isinstance(decoded, dict):
        decoded = {"_non_object": True, "_body_sha256": sha256(raw.encode("utf-8")).hexdigest()}
    return status, decoded, elapsed_ms, headers


def _validation_errors(exc: ValidationError) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in exc.errors(include_url=False, include_context=False, include_input=False):
        result.append({
            "loc": [str(part) for part in item.get("loc", ())],
            "type": str(item.get("type", "unknown")),
        })
    return result[:16]


def _decision_from_payload(payload: ProviderDecisionPayload, registry: Mapping[str, Any]) -> ControllerDecision:
    if payload.kind is ControllerDecisionKind.TOOL:
        assert payload.tool_name is not None
        if payload.tool_name not in registry:
            raise ValueError("unknown_tool")
        return ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name=payload.tool_name,
                arguments=dict(payload.arguments),
                evidence_id=payload.evidence_id,
            ),
        )
    if payload.kind is ControllerDecisionKind.FINAL:
        assert payload.final is not None
        return ControllerDecision(kind=ControllerDecisionKind.FINAL, final=dict(payload.final))
    return ControllerDecision(
        kind=payload.kind,
        message=payload.message,
        reason_code=payload.reason_code,
    )


def _one(*, bundle: Any, registry: Mapping[str, Any], unit_id: str, config: Config, api_key: str, attempt_index: int) -> dict[str, Any]:
    context = context_for_unit(bundle, unit_id)
    request = build_provider_decision_request(context=context, registry=registry)
    body: dict[str, Any] = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": f"Reasoning: {config.reasoning_instruction}\n\n{PROVIDER_DECISION_SYSTEM_INSTRUCTION}",
            },
            {"role": "user", "content": _request_text(request)},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "provider_decision_payload",
                "strict": False,
                "schema": json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA)),
            },
        },
        "temperature": 0,
        "n": 1,
        "stream": False,
        "max_completion_tokens": config.max_completion_tokens,
        "tool_choice": "none",
        "parallel_tool_calls": False,
        "include_reasoning": False,
    }
    if config.reasoning_effort_api is not None:
        body["reasoning_effort"] = config.reasoning_effort_api

    status, response, latency_ms, headers = _http(body, api_key)
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "attempt_index": attempt_index,
        "unit_id": unit_id,
        "config_id": config.config_id,
        "max_completion_tokens": config.max_completion_tokens,
        "reasoning_effort_api": config.reasoning_effort_api,
        "reasoning_instruction": config.reasoning_instruction,
        "structured_output_strict": False,
        "http_status": status,
        "latency_ms": latency_ms,
        "request_sha256": request.request_sha256,
        "response_body_sha256": _sha(response),
        "finish_reason": None,
        "input_tokens": None,
        "output_tokens": None,
        "reasoning_tokens": None,
        "total_tokens": None,
        "content_present": False,
        "json_parse_ok": False,
        "payload_validation_ok": False,
        "validation_errors": [],
        "decision_kind": None,
        "tool_name": None,
        "rubric_pass": False,
        "rate_remaining_tokens": headers.get("x-ratelimit-remaining-tokens"),
        "raw_provider_material_recorded": False,
    }

    usage = response.get("usage") if isinstance(response.get("usage"), Mapping) else {}
    details = usage.get("completion_tokens_details") if isinstance(usage.get("completion_tokens_details"), Mapping) else {}
    row["input_tokens"] = usage.get("prompt_tokens") if isinstance(usage.get("prompt_tokens"), int) else None
    row["output_tokens"] = usage.get("completion_tokens") if isinstance(usage.get("completion_tokens"), int) else None
    row["total_tokens"] = usage.get("total_tokens") if isinstance(usage.get("total_tokens"), int) else None
    row["reasoning_tokens"] = details.get("reasoning_tokens") if isinstance(details.get("reasoning_tokens"), int) else None

    choices = response.get("choices")
    if status == 200 and isinstance(choices, list) and len(choices) == 1 and isinstance(choices[0], Mapping):
        choice = choices[0]
        row["finish_reason"] = choice.get("finish_reason")
        message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            row["content_present"] = True
            try:
                decoded = json.loads(content)
                row["json_parse_ok"] = isinstance(decoded, dict)
            except Exception:
                decoded = None
            if isinstance(decoded, dict):
                try:
                    payload = ProviderDecisionPayload.model_validate(decoded)
                    row["payload_validation_ok"] = True
                    decision = _decision_from_payload(payload, registry)
                    row["decision_kind"] = decision.kind.value
                    row["tool_name"] = None if decision.proposal is None else decision.proposal.tool_name
                    row["rubric_pass"] = bool(adjudicate_v3_rubric(bundle, unit_id, decision))
                except ValidationError as exc:
                    row["validation_errors"] = _validation_errors(exc)
                except Exception as exc:
                    row["validation_errors"] = [{"loc": [], "type": type(exc).__name__}]

    row["attempt_sha256"] = _sha(row)
    return row


def main() -> int:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY missing")
    root = Path(__file__).resolve().parents[2]
    bundle = load_frozen_tournament_v3(root)
    if POPULATION_SHA256 != "4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9":
        raise RuntimeError("population hash drift")
    registry = canonical_tool_registry()

    rows: list[dict[str, Any]] = []
    plan: list[tuple[str, Config]] = []
    # Rotate config order by unit to reduce temporal confounding.
    for unit_index, unit_id in enumerate(TARGET_UNITS):
        ordered = CONFIGS[unit_index % len(CONFIGS):] + CONFIGS[:unit_index % len(CONFIGS)]
        plan.extend((unit_id, config) for config in ordered)

    for attempt_index, (unit_id, config) in enumerate(plan):
        row = _one(
            bundle=bundle,
            registry=registry,
            unit_id=unit_id,
            config=config,
            api_key=api_key,
            attempt_index=attempt_index,
        )
        rows.append(row)
        print("PROVIDER_DIAGNOSTIC_ATTEMPT=" + _canonical_json(row), flush=True)
        total = row.get("total_tokens")
        if isinstance(total, int) and total > 0:
            time.sleep((float(total) / TPM_LIMIT) * 60.0 + PACING_MARGIN_SECONDS)
        elif row.get("http_status") == 429:
            time.sleep(60.0)

    by_config: dict[str, dict[str, Any]] = {}
    for config in CONFIGS:
        subset = [row for row in rows if row["config_id"] == config.config_id]
        by_config[config.config_id] = {
            "attempts": len(subset),
            "http_200": sum(row["http_status"] == 200 for row in subset),
            "finish_stop": sum(row["finish_reason"] == "stop" for row in subset),
            "finish_nonstop": sum(row["finish_reason"] not in (None, "stop") for row in subset),
            "payload_valid": sum(bool(row["payload_validation_ok"]) for row in subset),
            "rubric_pass": sum(bool(row["rubric_pass"]) for row in subset),
            "mean_reasoning_tokens": (
                sum(row["reasoning_tokens"] for row in subset if isinstance(row["reasoning_tokens"], int))
                / max(1, sum(isinstance(row["reasoning_tokens"], int) for row in subset))
            ),
        }
    result = {
        "schema_version": SCHEMA_VERSION,
        "status": "COMPLETE",
        "population_sha256": POPULATION_SHA256,
        "target_units": list(TARGET_UNITS),
        "attempt_count": len(rows),
        "configs": by_config,
        "attempts_sha256": _sha([row["attempt_sha256"] for row in rows]),
        "promotion_authorized": False,
        "raw_provider_material_recorded": False,
    }
    result["evidence_sha256"] = _sha(result)
    print("PROVIDER_DIAGNOSTIC_RESULT=" + _canonical_json(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
