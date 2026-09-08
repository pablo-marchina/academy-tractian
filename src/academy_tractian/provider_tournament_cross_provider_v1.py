from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import os
from pathlib import Path
import random
from statistics import mean, median
from typing import Any, Mapping, Sequence
from uuid import uuid4

from research.e2.controller import ControllerDecision, ControllerDecisionKind
from research.e2.validation import validate_arguments

from .decision_source import (
    ProviderCallIdentity,
    ProviderDecisionRequest,
    ProviderDecisionSource,
    ProviderModelCallRecord,
)
from .provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
    ProviderJsonTransport,
    ProviderUsageRecord,
    UrllibProviderJsonTransport,
)
from .provider_tournament_v3 import (
    POPULATION_SHA256,
    REPETITIONS,
    UNITS,
    TournamentV3Error,
    adjudicate_v3_rubric,
    context_for_unit,
    load_frozen_tournament_v3,
)
from .runtime import canonical_tool_registry


MANIFEST_PATH = "research/experiments/provider-tournament-cross-provider-v1-manifest.json"
BASE_MODEL_ID = "openai/gpt-oss-120b"
MAX_INPUT_TOKENS = 8000
MAX_OUTPUT_TOKENS = 512
MATERIAL_IMPROVEMENT = 0.02
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20260908
CONFIDENCE_LEVEL = 0.95
ATTEMPTS_PER_CANDIDATE = UNITS * REPETITIONS
CANDIDATE_COUNT = 3
ATTEMPTS_PER_PACKET = UNITS * CANDIDATE_COUNT
TOTAL_ATTEMPTS = ATTEMPTS_PER_CANDIDATE * CANDIDATE_COUNT
FORBIDDEN_BINDING_KEYS = frozenset({"user_id", "x-user-id", "identity_id", "seed"})
FORBIDDEN_PRIVATE_KEYS = frozenset({"gold", "oracle", "expected_path", "expected_paths", "private_truth"})


class CrossProviderTournamentV1Error(RuntimeError):
    pass


@dataclass(frozen=True)
class CandidateConfig:
    candidate_id: str
    provider_id: str
    model_id: str
    route_id: str
    endpoint: str
    secret_name: str
    max_token_field: str
    openrouter_no_fallback: bool = False


CANDIDATES: tuple[CandidateConfig, ...] = (
    CandidateConfig(
        candidate_id="groq-gpt-oss-120b",
        provider_id="groq",
        model_id=BASE_MODEL_ID,
        route_id="groq.openai_compat.chat_completions.v1",
        endpoint="https://api.groq.com/openai/v1/chat/completions",
        secret_name="GROQ_API_KEY",
        max_token_field="max_completion_tokens",
    ),
    CandidateConfig(
        candidate_id="nvidia-gpt-oss-120b",
        provider_id="nvidia",
        model_id=BASE_MODEL_ID,
        route_id="nvidia.integrate.chat_completions.v1",
        endpoint="https://integrate.api.nvidia.com/v1/chat/completions",
        secret_name="NVIDIA_API_KEY",
        max_token_field="max_tokens",
    ),
    CandidateConfig(
        candidate_id="openrouter-gpt-oss-120b-free",
        provider_id="openrouter",
        model_id=f"{BASE_MODEL_ID}:free",
        route_id="openrouter.chat_completions.v1.free.no_fallback",
        endpoint="https://openrouter.ai/api/v1/chat/completions",
        secret_name="OPENROUTER_API_KEY",
        max_token_field="max_tokens",
        openrouter_no_fallback=True,
    ),
)
CANDIDATE_IDS = tuple(item.candidate_id for item in CANDIDATES)
CANDIDATE_BY_ID = {item.candidate_id: item for item in CANDIDATES}


@dataclass(frozen=True)
class PacketPlanEntry:
    packet_attempt_index: int
    global_attempt_index: int
    candidate_id: str
    unit_id: str
    unit_index: int
    repetition_index: int


def _provider_request_text(request: ProviderDecisionRequest) -> str:
    return json.dumps(
        request.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _schema_copy() -> dict[str, Any]:
    return json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA))


def _nonnegative_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _nested_key(value: Any, forbidden: frozenset[str]) -> bool:
    if isinstance(value, Mapping):
        return any(str(key).lower() in forbidden or _nested_key(item, forbidden) for key, item in value.items())
    if isinstance(value, list):
        return any(_nested_key(item, forbidden) for item in value)
    return False


class CrossProviderChatCompletionsDecisionClient:
    """One-shot OpenAI-compatible client for DP-005.

    The client performs no environment lookup, retry, model fallback, JSON repair, provider-side
    tool execution, web search, or stateful conversation management. Provider-specific differences
    are limited to endpoint/model identity, the max-token field, and OpenRouter's explicit
    no-fallback routing control.
    """

    def __init__(
        self,
        *,
        candidate: CandidateConfig,
        api_key: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("cross-provider client requires an explicit non-empty api_key")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.candidate = candidate
        self.provider_id = candidate.provider_id
        self.model_id = candidate.model_id
        self.route_id = candidate.route_id
        self._api_key = api_key
        self._transport = transport
        self._timeout_seconds = float(timeout_seconds)
        self._usage_records: list[ProviderUsageRecord] = []

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(candidate_id={self.candidate.candidate_id!r}, "
            f"provider_id={self.provider_id!r}, model_id={self.model_id!r}, "
            f"route_id={self.route_id!r}, api_key=<redacted>)"
        )

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        records = tuple(self._usage_records)
        self._usage_records.clear()
        return records

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        body: dict[str, Any] = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": PROVIDER_DECISION_SYSTEM_INSTRUCTION},
                {"role": "user", "content": _provider_request_text(request)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "provider_decision_payload",
                    "strict": False,
                    "schema": _schema_copy(),
                },
            },
            "temperature": 0,
            "n": 1,
            "stream": False,
            self.candidate.max_token_field: MAX_OUTPUT_TOKENS,
        }
        if self.candidate.openrouter_no_fallback:
            body["provider"] = {
                "allow_fallbacks": False,
                "require_parameters": True,
            }
        return ProviderHttpRequest(
            method="POST",
            url=self.candidate.endpoint,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            body=body,
            timeout_seconds=self._timeout_seconds,
        )

    def complete(self, request: ProviderDecisionRequest) -> str:
        response = self._invoke_once(self.build_http_request(request))
        usage = response.get("usage")
        usage_map = usage if isinstance(usage, Mapping) else {}
        details = usage_map.get("completion_tokens_details")
        details_map = details if isinstance(details, Mapping) else {}
        input_tokens = usage_map.get("prompt_tokens", usage_map.get("input_tokens"))
        output_tokens = usage_map.get("completion_tokens", usage_map.get("output_tokens"))
        total_tokens = usage_map.get("total_tokens")
        self._usage_records.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(input_tokens),
                output_tokens=_nonnegative_int_or_none(output_tokens),
                total_tokens=_nonnegative_int_or_none(total_tokens),
                reasoning_tokens=_nonnegative_int_or_none(details_map.get("reasoning_tokens")),
            )
        )
        return self._extract_output(response)

    def _invoke_once(self, request: ProviderHttpRequest) -> Mapping[str, Any]:
        try:
            response = self._transport.post_json(request)
        except ProviderHttpClientError:
            raise
        except Exception:
            raise ProviderHttpClientError("TRANSPORT_FAILURE") from None
        if not isinstance(response, ProviderHttpResponse):
            raise ProviderHttpClientError("TRANSPORT_RESPONSE_INVALID")
        if response.status_code < 200 or response.status_code >= 300:
            raise ProviderHttpClientError("HTTP_STATUS", status_code=response.status_code)
        if not isinstance(response.body, Mapping):
            raise ProviderHttpClientError("HTTP_JSON_NOT_OBJECT")
        return response.body

    def _extract_output(self, response: Mapping[str, Any]) -> str:
        object_type = response.get("object")
        if object_type not in (None, "chat.completion"):
            raise ProviderHttpClientError("CHAT_COMPLETION_OBJECT_INVALID")
        resolved_model = response.get("model")
        if isinstance(resolved_model, str) and not resolved_model.startswith(BASE_MODEL_ID):
            raise ProviderHttpClientError("MODEL_IDENTITY_MISMATCH")
        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ProviderHttpClientError("CHAT_COMPLETION_CHOICES_INVALID")
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise ProviderHttpClientError("CHAT_COMPLETION_CHOICE_INVALID")
        if choice.get("index") not in (None, 0):
            raise ProviderHttpClientError("CHAT_COMPLETION_CHOICE_INDEX_INVALID")
        if choice.get("finish_reason") != "stop":
            raise ProviderHttpClientError("CHAT_COMPLETION_FINISH_REASON_INVALID")
        message = choice.get("message")
        if not isinstance(message, Mapping):
            raise ProviderHttpClientError("CHAT_COMPLETION_MESSAGE_INVALID")
        if message.get("role") not in (None, "assistant"):
            raise ProviderHttpClientError("CHAT_COMPLETION_ROLE_INVALID")
        if message.get("tool_calls") not in (None, []):
            raise ProviderHttpClientError("PROVIDER_NATIVE_TOOL_CALL_REJECTED")
        if message.get("function_call") is not None:
            raise ProviderHttpClientError("PROVIDER_NATIVE_FUNCTION_CALL_REJECTED")
        refusal = message.get("refusal")
        if refusal not in (None, ""):
            raise ProviderHttpClientError("PROVIDER_REFUSAL_REJECTED")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderHttpClientError("CHAT_COMPLETION_OUTPUT_TEXT_INVALID")
        return content


class _InspectingClient:
    def __init__(self, inner: CrossProviderChatCompletionsDecisionClient) -> None:
        self.inner = inner
        self.identity_seed_attempt = False
        self.private_key_attempt = False

    def complete(self, request: ProviderDecisionRequest) -> str:
        raw = self.inner.complete(request)
        try:
            decoded = json.loads(raw)
        except Exception:
            return raw
        self.identity_seed_attempt = _nested_key(decoded, FORBIDDEN_BINDING_KEYS)
        self.private_key_attempt = _nested_key(decoded, FORBIDDEN_PRIVATE_KEYS)
        return raw

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        return self.inner.drain_usage_records()


def load_dp005_manifest(repo_root: Path | str = ".") -> dict[str, Any]:
    path = Path(repo_root) / MANIFEST_PATH
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "provider-tournament-cross-provider-v1-manifest":
        raise CrossProviderTournamentV1Error("DP-005 manifest schema mismatch")
    if manifest.get("status") != "PREREGISTERED_BEFORE_ANY_DP005_LIVE_CALL":
        raise CrossProviderTournamentV1Error("DP-005 manifest status mismatch")
    source = manifest.get("source_contract", {})
    if source.get("population_sha256") != POPULATION_SHA256 or source.get("contract_mutation_allowed") is not False:
        raise CrossProviderTournamentV1Error("DP-005 source-contract drift")
    request = manifest.get("request_contract", {})
    frozen_request = {
        "ai_gateway_used": False,
        "automatic_fallbacks": 0,
        "automatic_json_repair": False,
        "automatic_retries": 0,
        "controller_owns_agent_loop": True,
        "failed_attempts_remain_in_denominator": True,
        "harness_runner_owns_tool_execution": True,
        "max_input_tokens": MAX_INPUT_TOKENS,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "n": 1,
        "provider_native_tool_execution": False,
        "provider_side_state": False,
        "stream": False,
        "structured_output": "strict_json",
        "temperature": 0,
        "warmup_calls": 0,
        "web_search_used": False,
    }
    if any(request.get(key) != value for key, value in frozen_request.items()):
        raise CrossProviderTournamentV1Error("DP-005 request-contract drift")
    if [item.get("candidate_id") for item in manifest.get("candidates", [])] != list(CANDIDATE_IDS):
        raise CrossProviderTournamentV1Error("DP-005 candidate identity drift")
    return manifest


def build_packet_plan(bundle: Any, repetition_index: int) -> tuple[PacketPlanEntry, ...]:
    if repetition_index < 0 or repetition_index >= REPETITIONS:
        raise ValueError("repetition_index must be 0..4")
    entries: list[PacketPlanEntry] = []
    units = bundle.population["units"]
    for unit_index, unit in enumerate(units):
        rotation = (unit_index + repetition_index) % CANDIDATE_COUNT
        order = CANDIDATE_IDS[rotation:] + CANDIDATE_IDS[:rotation]
        for candidate_id in order:
            packet_index = len(entries)
            entries.append(
                PacketPlanEntry(
                    packet_attempt_index=packet_index,
                    global_attempt_index=repetition_index * ATTEMPTS_PER_PACKET + packet_index,
                    candidate_id=candidate_id,
                    unit_id=unit["unit_id"],
                    unit_index=unit_index,
                    repetition_index=repetition_index,
                )
            )
    if len(entries) != ATTEMPTS_PER_PACKET:
        raise CrossProviderTournamentV1Error("DP-005 packet geometry mismatch")
    return tuple(entries)


def _write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def _validate_audit(
    *,
    audit_records: tuple[object, ...],
    candidate: CandidateConfig,
) -> tuple[str | None, int | None, bool, tuple[str, ...]]:
    if len(audit_records) != 1:
        return None, None, False, ("AUDIT_RECORD_COUNT",)
    item = audit_records[0]
    call_id = getattr(item, "call_id", None)
    metadata = getattr(item, "metadata", None)
    if call_id is None or metadata is None:
        return None, None, False, ("AUDIT_RECORD_INVALID",)
    try:
        record = ProviderModelCallRecord.from_trace_event(call_id=call_id, metadata=dict(metadata))
    except Exception:
        return None, None, False, ("AUDIT_RECORD_INVALID",)
    issues: list[str] = []
    if record.provider_id != candidate.provider_id or record.model_id != candidate.model_id or record.route_id != candidate.route_id or record.live_call is not True:
        issues.append("ROUTE_OR_MODEL_IDENTITY")
    if record.adapter_client_invocations != 1 or record.adapter_retry_count != 0 or record.adapter_fallback_used is not False:
        issues.append("HIDDEN_RETRY_OR_FALLBACK")
    if record.raw_request_recorded or record.raw_response_recorded or record.exception_text_recorded:
        issues.append("RAW_MATERIAL_RECORDED")
    return record.request_sha256, record.latency_ms, not issues, tuple(issues)


def run_packet(
    *,
    repetition_index: int,
    api_keys: Mapping[str, str],
    output_path: Path,
    repo_root: Path | str = ".",
    transport: ProviderJsonTransport | None = None,
) -> dict[str, Any]:
    load_dp005_manifest(repo_root)
    bundle = load_frozen_tournament_v3(repo_root)
    plan = build_packet_plan(bundle, repetition_index)
    registry = canonical_tool_registry()
    shared_transport = transport or UrllibProviderJsonTransport()
    clients: dict[str, _InspectingClient] = {}
    for candidate in CANDIDATES:
        key = api_keys.get(candidate.candidate_id, "")
        if not isinstance(key, str) or not key.strip():
            raise CrossProviderTournamentV1Error(f"missing secret for {candidate.candidate_id}")
        clients[candidate.candidate_id] = _InspectingClient(
            CrossProviderChatCompletionsDecisionClient(
                candidate=candidate,
                api_key=key,
                transport=shared_transport,
            )
        )

    attempts: list[dict[str, Any]] = []
    for entry in plan:
        candidate = CANDIDATE_BY_ID[entry.candidate_id]
        client = clients[entry.candidate_id]
        client.identity_seed_attempt = False
        client.private_key_attempt = False
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
        failure_code: str | None = None
        try:
            decision = source.decide(context_for_unit(bundle, entry.unit_id))
        except ProviderHttpClientError as exc:
            failure_code = str(exc)
        except Exception as exc:
            failure_code = type(exc).__name__

        request_sha, latency_ms, trace_ok, trace_issues = _validate_audit(
            audit_records=source.drain_audit_records(),
            candidate=candidate,
        )
        usage_records = client.drain_usage_records()
        usage = usage_records[0] if len(usage_records) == 1 else None
        input_tokens = None if usage is None else usage.input_tokens
        output_tokens = None if usage is None else usage.output_tokens
        token_ceiling_violation = bool(
            (input_tokens is not None and input_tokens > MAX_INPUT_TOKENS)
            or (output_tokens is not None and output_tokens > MAX_OUTPUT_TOKENS)
        )

        known_tool = None
        b1_valid = None
        b1_issue_codes: list[str] = []
        if decision is not None and decision.kind is ControllerDecisionKind.TOOL and decision.proposal is not None:
            known_tool = decision.proposal.tool_name in registry
            if known_tool:
                issues = validate_arguments(registry[decision.proposal.tool_name], decision.proposal.arguments)
                b1_issue_codes = [item.code for item in issues]
                b1_valid = not issues
            else:
                b1_valid = False

        attempts.append(
            {
                "packet_attempt_index": entry.packet_attempt_index,
                "global_attempt_index": entry.global_attempt_index,
                "candidate_id": entry.candidate_id,
                "provider_id": candidate.provider_id,
                "model_id": candidate.model_id,
                "route_id": candidate.route_id,
                "unit_id": entry.unit_id,
                "unit_index": entry.unit_index,
                "repetition_index": entry.repetition_index,
                "outcome": "success" if decision is not None else "failure",
                "failure_code": failure_code,
                "decision_kind": None if decision is None else decision.kind.value,
                "tool_name": None if decision is None or decision.proposal is None else decision.proposal.tool_name,
                "request_sha256": request_sha,
                "trace_integrity": trace_ok,
                "trace_issue_codes": list(trace_issues),
                "latency_ms": latency_ms,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": None if usage is None else usage.total_tokens,
                "reasoning_tokens": None if usage is None else usage.reasoning_tokens,
                "usage_accounted": usage is not None and input_tokens is not None and output_tokens is not None,
                "token_ceiling_violation": token_ceiling_violation,
                "known_tool_selection_valid": known_tool,
                "b1_valid": b1_valid,
                "b1_issue_codes": b1_issue_codes,
                "identity_seed_attempt": client.identity_seed_attempt,
                "private_key_attempt": client.private_key_attempt,
                "rubric_pass": adjudicate_v3_rubric(bundle, entry.unit_id, decision),
                "raw_provider_material_recorded": False,
                "automatic_retry_count": 0,
                "automatic_fallback_count": 0,
            }
        )
        _write_json_atomic(
            output_path,
            {
                "schema_version": "provider-tournament-cross-provider-v1-packet-progress",
                "decision_id": "DP-005",
                "repetition_index": repetition_index,
                "population_sha256": POPULATION_SHA256,
                "attempts": attempts,
                "complete": False,
                "raw_provider_material_recorded": False,
            },
        )

    packet = {
        "schema_version": "provider-tournament-cross-provider-v1-packet",
        "decision_id": "DP-005",
        "repetition_index": repetition_index,
        "population_sha256": POPULATION_SHA256,
        "attempt_count": len(attempts),
        "attempts": attempts,
        "complete": len(attempts) == ATTEMPTS_PER_PACKET,
        "raw_provider_material_recorded": False,
    }
    _write_json_atomic(output_path, packet)
    return packet


def _rate(values: Sequence[bool]) -> float:
    return sum(1 for value in values if value) / len(values) if values else 0.0


def _percentile(values: Sequence[int], q: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    return ordered[min(len(ordered) - 1, max(0, int(position + 0.999999)))]


def _quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires values")
    position = q * (len(ordered) - 1)
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    fraction = position - lo
    return ordered[lo] * (1.0 - fraction) + ordered[hi] * fraction


def _scenario_matrix(attempts: Sequence[dict[str, Any]], candidate_id: str) -> list[list[float]]:
    matrix: list[list[float]] = []
    for unit_index in range(UNITS):
        row: list[float] = []
        for repetition_index in range(REPETITIONS):
            matches = [
                item
                for item in attempts
                if item.get("candidate_id") == candidate_id
                and item.get("unit_index") == unit_index
                and item.get("repetition_index") == repetition_index
            ]
            if len(matches) != 1:
                raise CrossProviderTournamentV1Error("scenario/repetition pairing failure")
            row.append(1.0 if matches[0].get("rubric_pass") is True else 0.0)
        matrix.append(row)
    return matrix


def hierarchical_paired_bootstrap(
    attempts: Sequence[dict[str, Any]],
    *,
    candidate_a: str,
    candidate_b: str,
) -> dict[str, float]:
    a = _scenario_matrix(attempts, candidate_a)
    b = _scenario_matrix(attempts, candidate_b)
    observed = mean([mean(a[index]) - mean(b[index]) for index in range(UNITS)])
    seed_offset = sum(ord(char) for char in f"{candidate_a}|{candidate_b}")
    rng = random.Random(BOOTSTRAP_SEED + seed_offset)
    samples: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        scenario_deltas: list[float] = []
        for _scenario_draw in range(UNITS):
            scenario = rng.randrange(UNITS)
            repetition_deltas: list[float] = []
            for _rep_draw in range(REPETITIONS):
                repetition = rng.randrange(REPETITIONS)
                repetition_deltas.append(a[scenario][repetition] - b[scenario][repetition])
            scenario_deltas.append(mean(repetition_deltas))
        samples.append(mean(scenario_deltas))
    alpha = 1.0 - CONFIDENCE_LEVEL
    return {
        "observed_delta": observed,
        "ci_low": _quantile(samples, alpha / 2.0),
        "ci_high": _quantile(samples, 1.0 - alpha / 2.0),
    }


def analyze_tournament(packet_paths: Sequence[Path]) -> dict[str, Any]:
    if len(packet_paths) != REPETITIONS:
        raise CrossProviderTournamentV1Error("exactly five DP-005 packet artifacts are required")
    packets = [json.loads(path.read_text(encoding="utf-8")) for path in packet_paths]
    if sorted(item.get("repetition_index") for item in packets) != list(range(REPETITIONS)):
        raise CrossProviderTournamentV1Error("DP-005 repetition set must be exactly 0..4")
    if any(
        item.get("population_sha256") != POPULATION_SHA256
        or item.get("complete") is not True
        or item.get("attempt_count") != ATTEMPTS_PER_PACKET
        for item in packets
    ):
        raise CrossProviderTournamentV1Error("DP-005 packet identity/completeness failure")
    attempts = [attempt for packet in packets for attempt in packet["attempts"]]
    if len(attempts) != TOTAL_ATTEMPTS:
        raise CrossProviderTournamentV1Error("DP-005 total attempt geometry mismatch")

    summaries: dict[str, Any] = {}
    eligible: list[str] = []
    for candidate_id in CANDIDATE_IDS:
        rows = [item for item in attempts if item.get("candidate_id") == candidate_id]
        if len(rows) != ATTEMPTS_PER_CANDIDATE:
            raise CrossProviderTournamentV1Error("DP-005 candidate attempt geometry mismatch")
        failures: list[str] = []
        if any(item.get("private_key_attempt") for item in rows):
            failures.append("H02_PRIVATE_GOLD")
        if any(item.get("identity_seed_attempt") for item in rows):
            failures.append("H04_POLICY_BINDING_BYPASS")
        if any(not item.get("trace_integrity") for item in rows):
            failures.append("H06_H10_PROVENANCE")
        if any(item.get("raw_provider_material_recorded") for item in rows):
            failures.append("H10_RAW_PROVIDER_MATERIAL")
        if any(item.get("automatic_retry_count") != 0 for item in rows):
            failures.append("HIDDEN_RETRY")
        if any(item.get("automatic_fallback_count") != 0 for item in rows):
            failures.append("HIDDEN_FALLBACK")
        success_rate = _rate([item.get("outcome") == "success" for item in rows])
        if success_rate < 0.9375:
            failures.append("H11_RELIABILITY")
        if any(item.get("outcome") == "success" and not item.get("usage_accounted") for item in rows):
            failures.append("H10_RESOURCE_ACCOUNTING")
        if any(item.get("token_ceiling_violation") for item in rows):
            failures.append("H08_TOKEN_CEILING")

        tool_rows = [item for item in rows if item.get("decision_kind") == "TOOL"]
        known_tool_rows = [item for item in tool_rows if item.get("known_tool_selection_valid")]
        latencies = [int(item["latency_ms"]) for item in rows if item.get("latency_ms") is not None]
        per_unit_stable: list[bool] = []
        for unit_index in range(UNITS):
            unit_rows = [item for item in rows if item.get("unit_index") == unit_index]
            signatures = {
                (item.get("decision_kind"), item.get("tool_name") if item.get("decision_kind") == "TOOL" else None)
                for item in unit_rows
                if item.get("outcome") == "success"
            }
            per_unit_stable.append(len(unit_rows) == REPETITIONS and len(signatures) == 1)
        failure_codes = Counter(str(item.get("failure_code")) for item in rows if item.get("failure_code"))
        summaries[candidate_id] = {
            "attempt_count": len(rows),
            "operational_outcome_accuracy": _rate([item.get("rubric_pass") is True for item in rows]),
            "structured_response_success_rate": success_rate,
            "canonical_tool_selection_validity": _rate([bool(item.get("known_tool_selection_valid")) for item in tool_rows]) if tool_rows else 1.0,
            "canonical_argument_validity": _rate([bool(item.get("b1_valid")) for item in known_tool_rows]) if known_tool_rows else 1.0,
            "repeat_stability": _rate(per_unit_stable),
            "latency_p50_ms": median(latencies) if latencies else None,
            "latency_p95_ms": _percentile(latencies, 0.95),
            "latency_p99_ms": _percentile(latencies, 0.99),
            "input_tokens_total": sum(int(item.get("input_tokens") or 0) for item in rows),
            "output_tokens_total": sum(int(item.get("output_tokens") or 0) for item in rows),
            "failure_code_distribution": dict(sorted(failure_codes.items())),
            "hard_gate_pass": not failures,
            "hard_gate_failures": failures,
        }
        if not failures:
            eligible.append(candidate_id)

    pairwise: dict[str, Any] = {}
    for candidate_a in eligible:
        for candidate_b in eligible:
            if candidate_a >= candidate_b:
                continue
            result = hierarchical_paired_bootstrap(attempts, candidate_a=candidate_a, candidate_b=candidate_b)
            pairwise[f"{candidate_a}__vs__{candidate_b}"] = {
                **result,
                "method": "hierarchical_paired_bootstrap",
                "resamples": BOOTSTRAP_RESAMPLES,
                "confidence_level": CONFIDENCE_LEVEL,
                "material_improvement_absolute": MATERIAL_IMPROVEMENT,
            }

    if not eligible:
        selection = "NO_SELECTION"
        reason = "NO_CANDIDATE_PASSED_HARD_GATES"
    elif len(eligible) == 1:
        selection = f"PROMOTE:{eligible[0]}"
        reason = "SOLE_HARD_GATE_ELIGIBLE_CANDIDATE"
    else:
        promotable: list[str] = []
        for candidate in eligible:
            beats_all = True
            for other in eligible:
                if other == candidate:
                    continue
                comparison = hierarchical_paired_bootstrap(attempts, candidate_a=candidate, candidate_b=other)
                if comparison["observed_delta"] < MATERIAL_IMPROVEMENT or comparison["ci_low"] <= 0.0:
                    beats_all = False
                    break
            if beats_all:
                promotable.append(candidate)
        if len(promotable) == 1:
            selection = f"PROMOTE:{promotable[0]}"
            reason = "CONFIDENT_MATERIAL_PRIMARY_QUALITY_ADVANTAGE_AGAINST_ALL_ELIGIBLE"
        else:
            selection = "INCONCLUSIVE"
            reason = "PRIMARY_NOT_CONFIDENTLY_MATERIAL_AGAINST_ALL_ELIGIBLE"

    return {
        "schema_version": "provider-tournament-cross-provider-v1-final-analysis",
        "decision_id": "DP-005",
        "population_sha256": POPULATION_SHA256,
        "experimental_unit": "scenario",
        "repetitions_nested_within_scenario": True,
        "controlled_base_model": BASE_MODEL_ID,
        "candidate_summaries": summaries,
        "eligible_candidates": eligible,
        "pairwise_bootstrap": pairwise,
        "selection": selection,
        "selection_reason": reason,
        "automatic_production_promotion": False,
        "production_config_changed": False,
        "raw_provider_material_recorded": False,
    }
