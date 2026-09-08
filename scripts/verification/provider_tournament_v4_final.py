#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
from typing import Any, Mapping, Sequence

from research.e2.controller import ControllerDecision, ControllerDecisionKind
from research.e2.validation import validate_arguments

from academy_tractian.decision_source import ProviderCallIdentity, ProviderDecisionRequest, ProviderDecisionSource
from academy_tractian.provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderJsonTransport,
    ProviderUsageRecord,
    UrllibProviderJsonTransport,
)
from academy_tractian.provider_tournament_v3 import (
    POPULATION_SHA256,
    adjudicate_v3_rubric,
    context_for_unit,
    load_frozen_tournament_v3,
)
from academy_tractian.runtime import canonical_tool_registry

TOURNAMENT_SCHEMA = "provider-tournament-v4-final-result-v1"
ATTEMPT_SCHEMA = "provider-tournament-v4-final-attempt-v1"
MANIFEST_REL = "research/experiments/provider-tournament-v4-final-manifest.json"
EXPECTED_MANIFEST_SCHEMA = "provider-tournament-v4-final-manifest-v1"
EXPECTED_BASELINE_SHA = "4364364266c6a88d4affd85cb3a734c774cd42c8"
REPETITIONS = 5
UNITS = 17
ATTEMPTS_PER_CANDIDATE = 85
BOOTSTRAP_SEED = 20260908
BOOTSTRAP_ITERATIONS = 20_000
QUALITY_MARGIN = 0.02
STABILITY_MARGIN = 0.05
RELIABILITY_MARGIN = 0.02
LATENCY_RATIO_MARGIN = 0.10
COST_RATIO_MARGIN = 0.10

CANDIDATE_IDS = ("cloudflare-gpt-oss-120b", "groq-gpt-oss-120b")
FORBIDDEN_BINDING_KEYS = frozenset({"user_id", "x-user-id", "identity_id", "seed"})
FORBIDDEN_PRIVATE_KEYS = frozenset({"gold", "oracle", "expected_path", "expected_paths", "private_truth"})


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _nested_key(value: Any, forbidden: frozenset[str]) -> bool:
    if isinstance(value, Mapping):
        return any(str(k) in forbidden or _nested_key(v, forbidden) for k, v in value.items())
    if isinstance(value, list):
        return any(_nested_key(v, forbidden) for v in value)
    return False


def _nonnegative_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _request_text(request: ProviderDecisionRequest) -> str:
    return _canonical_json(request.model_dump(mode="json"))


def _schema_copy() -> dict[str, Any]:
    return json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA))


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    provider_id: str
    model_id: str
    route_id: str
    endpoint: str
    input_rate: float
    output_rate: float
    api_key: str


class OpenAICompatTournamentClient:
    def __init__(
        self,
        *,
        candidate: Candidate,
        transport: ProviderJsonTransport | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not candidate.api_key.strip():
            raise ValueError(f"{candidate.candidate_id} requires an API key")
        self.candidate = candidate
        self.provider_id = candidate.provider_id
        self.model_id = candidate.model_id
        self.route_id = candidate.route_id
        self._transport = transport or UrllibProviderJsonTransport()
        self._timeout_seconds = timeout_seconds
        self._usage: list[ProviderUsageRecord] = []
        self.identity_seed_attempt = False
        self.private_key_attempt = False

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        result = tuple(self._usage)
        self._usage.clear()
        return result

    def _response_format(self) -> dict[str, Any]:
        schema = _schema_copy()
        if self.provider_id == "cloudflare":
            return {"type": "json_schema", "json_schema": schema}
        if self.provider_id == "groq":
            # Best-effort schema mode preserves the provider-neutral open `arguments`
            # and `final` objects used by ADR-006. Application validation stays strict;
            # malformed/schema-invalid outputs remain failures and are never repaired.
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": "provider_decision_payload",
                    "strict": False,
                    "schema": schema,
                },
            }
        raise ValueError(f"unsupported provider: {self.provider_id}")

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        body: dict[str, Any] = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "system",
                    "content": "Reasoning: medium\n\n" + PROVIDER_DECISION_SYSTEM_INSTRUCTION,
                },
                {"role": "user", "content": _request_text(request)},
            ],
            "response_format": self._response_format(),
            "temperature": 0,
            "n": 1,
            "stream": False,
            "max_completion_tokens": 512,
            "tool_choice": "none",
            "parallel_tool_calls": False,
        }
        if self.provider_id == "groq":
            body["include_reasoning"] = False
        return ProviderHttpRequest(
            method="POST",
            url=self.candidate.endpoint,
            headers={
                "Authorization": f"Bearer {self.candidate.api_key}",
                "Content-Type": "application/json",
            },
            body=body,
            timeout_seconds=self._timeout_seconds,
        )

    def complete(self, request: ProviderDecisionRequest) -> str:
        http_request = self.build_http_request(request)
        try:
            response = self._transport.post_json(http_request)
        except ProviderHttpClientError:
            raise
        except Exception:
            raise ProviderHttpClientError("TRANSPORT_FAILURE") from None

        body = response.body
        if response.status_code < 200 or response.status_code >= 300:
            raise ProviderHttpClientError("HTTP_STATUS", status_code=response.status_code)
        if not isinstance(body, Mapping):
            raise ProviderHttpClientError("HTTP_JSON_NOT_OBJECT")
        if body.get("object") != "chat.completion":
            raise ProviderHttpClientError("OBJECT_INVALID")
        if body.get("model") != self.model_id:
            raise ProviderHttpClientError("MODEL_MISMATCH")

        choices = body.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ProviderHttpClientError("CHOICES_INVALID")
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise ProviderHttpClientError("CHOICE_INVALID")
        if choice.get("finish_reason") != "stop":
            raise ProviderHttpClientError("FINISH_REASON_INVALID")

        message = choice.get("message")
        if not isinstance(message, Mapping) or message.get("role") != "assistant":
            raise ProviderHttpClientError("MESSAGE_INVALID")
        if message.get("tool_calls") not in (None, []):
            raise ProviderHttpClientError("PROVIDER_NATIVE_TOOL_CALL_REJECTED")
        if message.get("function_call") is not None:
            raise ProviderHttpClientError("PROVIDER_NATIVE_FUNCTION_CALL_REJECTED")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderHttpClientError("OUTPUT_TEXT_INVALID")

        try:
            decoded = json.loads(content)
        except Exception:
            decoded = None
        self.identity_seed_attempt = _nested_key(decoded, FORBIDDEN_BINDING_KEYS)
        self.private_key_attempt = _nested_key(decoded, FORBIDDEN_PRIVATE_KEYS)

        usage = body.get("usage")
        usage_map = usage if isinstance(usage, Mapping) else {}
        details = usage_map.get("completion_tokens_details")
        details_map = details if isinstance(details, Mapping) else {}
        self._usage.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(usage_map.get("prompt_tokens")),
                output_tokens=_nonnegative_int_or_none(usage_map.get("completion_tokens")),
                total_tokens=_nonnegative_int_or_none(usage_map.get("total_tokens")),
                reasoning_tokens=_nonnegative_int_or_none(details_map.get("reasoning_tokens")),
            )
        )
        return content


def _load_manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST_REL
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != EXPECTED_MANIFEST_SCHEMA or payload.get("status") != "FROZEN":
        raise RuntimeError("V4 manifest is not frozen")
    population = payload.get("population", {})
    if population.get("sha256") != POPULATION_SHA256:
        raise RuntimeError("V4 manifest population hash drift")
    if payload.get("source_baseline", {}).get("git_sha") != EXPECTED_BASELINE_SHA:
        raise RuntimeError("V4 baseline SHA drift")
    if [item.get("candidate_id") for item in payload.get("candidates", [])] != list(CANDIDATE_IDS):
        raise RuntimeError("V4 candidate order/identity drift")
    return payload


def _candidate_from_manifest(item: Mapping[str, Any], *, env: Mapping[str, str]) -> Candidate:
    provider_id = str(item["provider_id"])
    if provider_id == "cloudflare":
        account_id = env.get("ACADEMY_PROVIDER_ACCOUNT_ID", "").strip()
        api_key = env.get("ACADEMY_PROVIDER_API_TOKEN", "").strip()
        if not account_id or not api_key:
            raise RuntimeError("Cloudflare credentials are not configured")
        endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions"
    elif provider_id == "groq":
        api_key = env.get("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        endpoint = "https://api.groq.com/openai/v1/chat/completions"
    else:
        raise RuntimeError(f"unsupported provider: {provider_id}")
    return Candidate(
        candidate_id=str(item["candidate_id"]),
        provider_id=provider_id,
        model_id=str(item["model_id"]),
        route_id=str(item["route_id"]),
        endpoint=endpoint,
        input_rate=float(item["list_price_usd_per_m_input_tokens"]),
        output_rate=float(item["list_price_usd_per_m_output_tokens"]),
        api_key=api_key,
    )


def _audit_integrity(
    *,
    source: ProviderDecisionSource,
    candidate: Candidate,
) -> tuple[bool, dict[str, Any]]:
    records = source.drain_audit_records()
    if len(records) != 1:
        return False, {"audit_record_count": len(records)}
    record = records[0]
    metadata = dict(record.metadata)
    required = {
        "provider_id": candidate.provider_id,
        "model_id": candidate.model_id,
        "route_id": candidate.route_id,
        "live_call": True,
        "adapter_client_invocations": 1,
        "adapter_retry_count": 0,
        "adapter_fallback_used": False,
        "raw_request_recorded": False,
        "raw_response_recorded": False,
        "exception_text_recorded": False,
    }
    ok = all(metadata.get(k) == v for k, v in required.items())
    return ok, {
        "call_id": record.call_id,
        "request_sha256": metadata.get("request_sha256"),
        "response_sha256": metadata.get("response_sha256"),
        "latency_ms": metadata.get("latency_ms"),
        "audit_outcome": metadata.get("outcome"),
        "audit_failure_code": metadata.get("failure_code"),
    }


def _argument_hash(decision: ControllerDecision | None) -> str | None:
    if decision is None or decision.kind is not ControllerDecisionKind.TOOL or decision.proposal is None:
        return None
    return _sha256(decision.proposal.arguments)


def _attempt(
    *,
    bundle: Any,
    registry: Mapping[str, Any],
    candidate: Candidate,
    unit_id: str,
    unit_index: int,
    repetition_index: int,
    attempt_index: int,
) -> dict[str, Any]:
    client = OpenAICompatTournamentClient(candidate=candidate)
    source = ProviderDecisionSource(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=candidate.provider_id,
            model_id=candidate.model_id,
            route_id=candidate.route_id,
            live_call=True,
        ),
    )
    decision: ControllerDecision | None = None
    exception_code: str | None = None
    try:
        decision = source.decide(context_for_unit(bundle, unit_id))
    except ProviderHttpClientError as exc:
        exception_code = str(exc)
    except Exception as exc:
        exception_code = type(exc).__name__

    audit_ok, audit = _audit_integrity(source=source, candidate=candidate)
    usage_records = client.drain_usage_records()
    usage = usage_records[0] if len(usage_records) == 1 else None

    known_tool: bool | None = None
    arguments_valid: bool | None = None
    argument_issue_codes: list[str] = []
    if decision is not None and decision.kind is ControllerDecisionKind.TOOL and decision.proposal is not None:
        known_tool = decision.proposal.tool_name in registry
        if known_tool:
            issues = validate_arguments(registry[decision.proposal.tool_name], decision.proposal.arguments)
            argument_issue_codes = [issue.code for issue in issues]
            arguments_valid = not issues
        else:
            arguments_valid = False

    input_tokens = usage.input_tokens if usage is not None else None
    output_tokens = usage.output_tokens if usage is not None else None
    estimated_cost = None
    if input_tokens is not None and output_tokens is not None:
        estimated_cost = (
            input_tokens * candidate.input_rate + output_tokens * candidate.output_rate
        ) / 1_000_000

    row = {
        "schema_version": ATTEMPT_SCHEMA,
        "attempt_index": attempt_index,
        "candidate_id": candidate.candidate_id,
        "provider_id": candidate.provider_id,
        "model_id": candidate.model_id,
        "route_id": candidate.route_id,
        "unit_id": unit_id,
        "unit_index": unit_index,
        "repetition_index": repetition_index,
        "outcome": "success" if decision is not None else "failure",
        "exception_code": exception_code,
        "decision_kind": None if decision is None else decision.kind.value,
        "tool_name": None if decision is None or decision.proposal is None else decision.proposal.tool_name,
        "arguments_sha256": _argument_hash(decision),
        "rubric_pass": adjudicate_v3_rubric(bundle, unit_id, decision),
        "known_tool_selection_valid": known_tool,
        "argument_valid": arguments_valid,
        "argument_issue_codes": argument_issue_codes,
        "identity_seed_attempt": client.identity_seed_attempt,
        "private_key_attempt": client.private_key_attempt,
        "trace_integrity": audit_ok,
        **audit,
        "usage_record_count": len(usage_records),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": None if usage is None else usage.total_tokens,
        "reasoning_tokens": None if usage is None else usage.reasoning_tokens,
        "estimated_list_price_cost_usd": estimated_cost,
        "raw_provider_material_recorded": False,
    }
    row["attempt_sha256"] = _sha256(row)
    return row


def _wilson(passes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    phat = passes / total
    denom = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt(phat * (1 - phat) / total + z * z / (4 * total * total)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def _percentile(values: Sequence[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    pos = (len(ordered) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(ordered[lo])
    frac = pos - lo
    return float(ordered[lo] * (1 - frac) + ordered[hi] * frac)


def _mcnemar(rows_by_pair: Mapping[tuple[str, int], Mapping[str, dict[str, Any]]]) -> dict[str, Any]:
    cf_only = 0
    groq_only = 0
    for pair in rows_by_pair.values():
        cf = bool(pair["cloudflare-gpt-oss-120b"]["rubric_pass"])
        gr = bool(pair["groq-gpt-oss-120b"]["rubric_pass"])
        cf_only += int(cf and not gr)
        groq_only += int(gr and not cf)
    n = cf_only + groq_only
    if n == 0:
        p = 1.0
    else:
        k = min(cf_only, groq_only)
        tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
        p = min(1.0, 2 * tail)
    return {"cloudflare_only_pass": cf_only, "groq_only_pass": groq_only, "exact_two_sided_p": p}


def _paired_bootstrap(rows_by_pair: Mapping[tuple[str, int], Mapping[str, dict[str, Any]]]) -> dict[str, float]:
    diffs = [
        float(bool(pair["cloudflare-gpt-oss-120b"]["rubric_pass"]))
        - float(bool(pair["groq-gpt-oss-120b"]["rubric_pass"]))
        for pair in rows_by_pair.values()
    ]
    observed = sum(diffs) / len(diffs)
    rng = random.Random(BOOTSTRAP_SEED)
    means: list[float] = []
    n = len(diffs)
    for _ in range(BOOTSTRAP_ITERATIONS):
        means.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    return {
        "cloudflare_minus_groq": observed,
        "ci95_lower": float(_percentile(means, 0.025)),
        "ci95_upper": float(_percentile(means, 0.975)),
    }


def _candidate_summary(candidate_id: str, rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(bool(r["rubric_pass"]) for r in rows)
    success = sum(r["outcome"] == "success" for r in rows)
    tool_rows = [r for r in rows if r["decision_kind"] == "TOOL"]
    known_tool_failures = sum(r["known_tool_selection_valid"] is False for r in tool_rows)
    invalid_args = sum(
        r["known_tool_selection_valid"] is True and r["argument_valid"] is not True
        for r in tool_rows
    )
    contract_failures = sum(
        r.get("audit_failure_code") in {
            "RESPONSE_TYPE_INVALID",
            "RESPONSE_JSON_INVALID",
            "RESPONSE_PAYLOAD_INVALID",
            "UNKNOWN_TOOL",
            "PROPOSAL_REJECTED",
        }
        for r in rows
    )
    trace_failures = sum(not bool(r["trace_integrity"]) for r in rows)
    usage_missing_success = sum(
        r["outcome"] == "success"
        and (r["usage_record_count"] != 1 or r["input_tokens"] is None or r["output_tokens"] is None)
        for r in rows
    )
    identity_attempts = sum(bool(r["identity_seed_attempt"]) for r in rows)
    private_attempts = sum(bool(r["private_key_attempt"]) for r in rows)

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["unit_id"], []).append(row)
    stable_units = 0
    for unit_rows in grouped.values():
        signatures = {
            (
                row["decision_kind"],
                row["tool_name"] if row["decision_kind"] == "TOOL" else None,
                row["arguments_sha256"] if row["decision_kind"] == "TOOL" else None,
            )
            for row in unit_rows
            if row["outcome"] == "success"
        }
        if len(unit_rows) == REPETITIONS and len(signatures) == 1 and all(r["outcome"] == "success" for r in unit_rows):
            stable_units += 1

    latencies = [float(r["latency_ms"]) for r in rows if isinstance(r.get("latency_ms"), int)]
    costs = [
        float(r["estimated_list_price_cost_usd"])
        for r in rows
        if r.get("estimated_list_price_cost_usd") is not None
    ]
    ci_low, ci_high = _wilson(passed, len(rows))
    hard_failures: list[str] = []
    success_rate = success / len(rows)
    if identity_attempts or private_attempts:
        hard_failures.append("PRIVATE_OR_BINDING_MATERIAL_ATTEMPT")
    if known_tool_failures:
        hard_failures.append("UNKNOWN_TOOL_PROPOSAL")
    if invalid_args:
        hard_failures.append("INVALID_KNOWN_TOOL_ARGUMENTS")
    if contract_failures:
        hard_failures.append("SCHEMA_OR_ADAPTER_CONTRACT_FAILURE")
    if trace_failures:
        hard_failures.append("TRACE_PROVENANCE_FAILURE")
    if usage_missing_success:
        hard_failures.append("SUCCESS_USAGE_ACCOUNTING_MISSING")
    if success_rate < 0.9375:
        hard_failures.append("RELIABILITY_BELOW_93_75_PERCENT")

    total_cost = sum(costs)
    return {
        "candidate_id": candidate_id,
        "attempts": len(rows),
        "rubric_pass_count": passed,
        "operational_outcome_accuracy": passed / len(rows),
        "operational_outcome_accuracy_wilson95": [ci_low, ci_high],
        "success_count": success,
        "reliability_success_rate": success_rate,
        "repeat_stability": stable_units / UNITS,
        "stable_units": stable_units,
        "tool_unknown_count": known_tool_failures,
        "invalid_argument_count": invalid_args,
        "schema_or_adapter_contract_failure_count": contract_failures,
        "trace_failure_count": trace_failures,
        "identity_seed_attempt_count": identity_attempts,
        "private_material_attempt_count": private_attempts,
        "latency_p50_ms": _percentile(latencies, 0.50),
        "latency_p95_ms": _percentile(latencies, 0.95),
        "latency_p99_ms": _percentile(latencies, 0.99),
        "estimated_list_price_cost_usd": total_cost,
        "estimated_list_price_cost_per_rubric_pass_usd": None if passed == 0 else total_cost / passed,
        "hard_gate_pass": not hard_failures,
        "hard_gate_failures": hard_failures,
    }


def _select(summaries: Mapping[str, dict[str, Any]]) -> tuple[str, str]:
    eligible = [cid for cid, summary in summaries.items() if summary["hard_gate_pass"]]
    if not eligible:
        return "NO_SELECTION", "NO_CANDIDATE_PASSED_HARD_GATES"
    if len(eligible) == 1:
        return f"PROMOTE:{eligible[0]}", "SOLE_HARD_GATE_ELIGIBLE_CANDIDATE"

    cf = summaries["cloudflare-gpt-oss-120b"]
    gr = summaries["groq-gpt-oss-120b"]
    delta = cf["operational_outcome_accuracy"] - gr["operational_outcome_accuracy"]
    if abs(delta) >= QUALITY_MARGIN:
        winner = "cloudflare-gpt-oss-120b" if delta > 0 else "groq-gpt-oss-120b"
        return f"PROMOTE:{winner}", "MATERIAL_PRIMARY_QUALITY_ADVANTAGE"

    stability_delta = cf["repeat_stability"] - gr["repeat_stability"]
    if abs(stability_delta) >= STABILITY_MARGIN:
        winner = "cloudflare-gpt-oss-120b" if stability_delta > 0 else "groq-gpt-oss-120b"
        return f"PROMOTE:{winner}", "QUALITY_TIE_STABILITY_ADVANTAGE"

    reliability_delta = cf["reliability_success_rate"] - gr["reliability_success_rate"]
    if abs(reliability_delta) >= RELIABILITY_MARGIN:
        winner = "cloudflare-gpt-oss-120b" if reliability_delta > 0 else "groq-gpt-oss-120b"
        return f"PROMOTE:{winner}", "QUALITY_TIE_RELIABILITY_ADVANTAGE"

    cf_p95, gr_p95 = cf["latency_p95_ms"], gr["latency_p95_ms"]
    if cf_p95 is not None and gr_p95 is not None and max(cf_p95, gr_p95) > 0:
        ratio_gap = abs(cf_p95 - gr_p95) / max(cf_p95, gr_p95)
        if ratio_gap >= LATENCY_RATIO_MARGIN:
            winner = "cloudflare-gpt-oss-120b" if cf_p95 < gr_p95 else "groq-gpt-oss-120b"
            return f"PROMOTE:{winner}", "QUALITY_RELIABILITY_TIE_P95_LATENCY_ADVANTAGE"

    cf_cost = cf["estimated_list_price_cost_per_rubric_pass_usd"]
    gr_cost = gr["estimated_list_price_cost_per_rubric_pass_usd"]
    if cf_cost is not None and gr_cost is not None and max(cf_cost, gr_cost) > 0:
        ratio_gap = abs(cf_cost - gr_cost) / max(cf_cost, gr_cost)
        if ratio_gap >= COST_RATIO_MARGIN:
            winner = "cloudflare-gpt-oss-120b" if cf_cost < gr_cost else "groq-gpt-oss-120b"
            return f"PROMOTE:{winner}", "QUALITY_RELIABILITY_LATENCY_TIE_COST_ADVANTAGE"

    return "INCONCLUSIVE", "NO_PREREGISTERED_MATERIAL_ADVANTAGE"


def _finalize(manifest: dict[str, Any], attempts: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if len(attempts) != 170:
        raise RuntimeError(f"final tournament requires 170 attempts, got {len(attempts)}")
    summaries: dict[str, dict[str, Any]] = {}
    rows_by_pair: dict[tuple[str, int], dict[str, dict[str, Any]]] = {}
    for cid in CANDIDATE_IDS:
        rows = [r for r in attempts if r["candidate_id"] == cid]
        if len(rows) != ATTEMPTS_PER_CANDIDATE:
            raise RuntimeError(f"{cid} attempt geometry mismatch: {len(rows)}")
        summaries[cid] = _candidate_summary(cid, rows)
        for row in rows:
            key = (row["unit_id"], row["repetition_index"])
            rows_by_pair.setdefault(key, {})[cid] = row
    if len(rows_by_pair) != 85 or any(set(pair) != set(CANDIDATE_IDS) for pair in rows_by_pair.values()):
        raise RuntimeError("paired geometry mismatch")

    paired = {
        "mcnemar": _mcnemar(rows_by_pair),
        "paired_bootstrap_accuracy_delta": _paired_bootstrap(rows_by_pair),
    }
    selection, reason = _select(summaries)
    result = {
        "schema_version": TOURNAMENT_SCHEMA,
        "status": "COMPLETE",
        "tournament_id": manifest["tournament_id"],
        "baseline_git_sha": EXPECTED_BASELINE_SHA,
        "manifest_sha256": _sha256(manifest),
        "population_sha256": POPULATION_SHA256,
        "attempt_count": len(attempts),
        "summaries": summaries,
        "paired_statistics": paired,
        "selection": selection,
        "selection_reason": reason,
        "production_promotion_authorized": False,
        "winner_e2e_required": selection.startswith("PROMOTE:"),
        "raw_provider_material_recorded": False,
    }
    result["evidence_sha256"] = _sha256(result)
    return result


def _plan() -> list[tuple[str, int, int]]:
    rows: list[tuple[str, int, int]] = []
    for repetition_index in range(REPETITIONS):
        for unit_index in range(UNITS):
            order = CANDIDATE_IDS if (unit_index + repetition_index) % 2 == 0 else tuple(reversed(CANDIDATE_IDS))
            rows.extend((cid, unit_index, repetition_index) for cid in order)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", choices=["both", *CANDIDATE_IDS], default="both")
    parser.add_argument("--max-attempts", type=int, default=0, help="smoke-only cap; 0 means full plan")
    parser.add_argument("--output-dir", default="/tmp/provider-tournament-v4")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    manifest = _load_manifest(root)
    bundle = load_frozen_tournament_v3(root)
    registry = canonical_tool_registry()
    candidates = {
        item["candidate_id"]: _candidate_from_manifest(item, env=os.environ)
        for item in manifest["candidates"]
        if args.candidate == "both" or item["candidate_id"] == args.candidate
    }

    plan = [row for row in _plan() if row[0] in candidates]
    if args.max_attempts:
        if args.max_attempts < 1:
            raise RuntimeError("--max-attempts must be positive")
        plan = plan[: args.max_attempts]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    attempts_path = output_dir / "attempts.jsonl"
    attempts: list[dict[str, Any]] = []

    for attempt_index, (candidate_id, unit_index, repetition_index) in enumerate(plan):
        unit_id = bundle.population["units"][unit_index]["unit_id"]
        row = _attempt(
            bundle=bundle,
            registry=registry,
            candidate=candidates[candidate_id],
            unit_id=unit_id,
            unit_index=unit_index,
            repetition_index=repetition_index,
            attempt_index=attempt_index,
        )
        attempts.append(row)
        with attempts_path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical_json(row) + "\n")
        print("TOURNAMENT_ATTEMPT=" + _canonical_json(row), flush=True)

    if args.candidate == "both" and not args.max_attempts:
        result = _finalize(manifest, attempts)
    else:
        result = {
            "schema_version": "provider-tournament-v4-partial-run-v1",
            "status": "PARTIAL_SMOKE" if args.max_attempts else "CANDIDATE_COMPLETE",
            "candidate": args.candidate,
            "attempt_count": len(attempts),
            "population_sha256": POPULATION_SHA256,
            "production_promotion_authorized": False,
            "raw_provider_material_recorded": False,
        }
        result["evidence_sha256"] = _sha256(result)

    result_path = output_dir / "result.json"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("TOURNAMENT_RESULT=" + _canonical_json(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
