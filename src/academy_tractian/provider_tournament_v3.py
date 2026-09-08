from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
from statistics import median
from typing import Any, Mapping, Sequence
from uuid import uuid4

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind, ControllerObservation
from research.e2.validation import validate_arguments

from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from .cloudflare_provider_provenance_v2 import (
    CloudflareProviderCallIdentityV2,
    CloudflareProviderDecisionSourceV2,
    validate_cloudflare_audit_record_v2,
)
from .provider_clients import ProviderHttpClientError, ProviderJsonTransport, ProviderUsageRecord, UrllibProviderJsonTransport
from .runtime import canonical_tool_registry


MANIFEST_PATH = "research/experiments/provider-tournament-v3-manifest.json"
POPULATION_PATH = "research/experiments/provider-tournament-v3-population.json"
MANIFEST_GIT_BLOB = "d18e0203b2eef4cb1e12ccb4668f4ea70b51054c"
POPULATION_GIT_BLOB = "6f81c748b560f2a7a12f52bea36c78b5ef98ea77"
POPULATION_SHA256 = "4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9"

GLM_CANDIDATE_ID = "cloudflare-glm-4.7-flash"
NEMOTRON_CANDIDATE_ID = "cloudflare-nemotron-3-120b-a12b"
CANDIDATE_IDS = (GLM_CANDIDATE_ID, NEMOTRON_CANDIDATE_ID)
MODEL_BY_CANDIDATE = {
    GLM_CANDIDATE_ID: CLOUDFLARE_GLM_MODEL_ID,
    NEMOTRON_CANDIDATE_ID: CLOUDFLARE_NEMOTRON_MODEL_ID,
}
NEURON_RATES = {
    GLM_CANDIDATE_ID: (5500.0, 36400.0),
    NEMOTRON_CANDIDATE_ID: (45455.0, 136364.0),
}
MAX_NEURONS_PER_ATTEMPT = {
    GLM_CANDIDATE_ID: 62.6368,
    NEMOTRON_CANDIDATE_ID: 433.458368,
}
DAILY_FREE_NEURONS = 10000.0
MIN_START_NEURONS = 9000.0
MAX_PACKET_NEURONS = 8433.617856
UNITS = 17
REPETITIONS = 5
ATTEMPTS_PER_PACKET = 34
TOTAL_ATTEMPTS = 170
FORBIDDEN_BINDING_KEYS = frozenset({"user_id", "x-user-id", "identity_id", "seed"})
FORBIDDEN_PRIVATE_KEYS = frozenset({"gold", "oracle", "expected_path", "expected_paths", "private_truth"})


class TournamentV3Error(RuntimeError):
    pass


@dataclass(frozen=True)
class FrozenTournamentV3:
    manifest: dict[str, Any]
    population: dict[str, Any]


@dataclass(frozen=True)
class PacketPlanEntry:
    packet_attempt_index: int
    global_attempt_index: int
    candidate_id: str
    model_id: str
    unit_id: str
    unit_index: int
    repetition_index: int


def _git_blob_sha1(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _read_pinned(root: Path, relpath: str, expected_blob: str) -> bytes:
    data = (root / relpath).read_bytes()
    if _git_blob_sha1(data) != expected_blob:
        raise TournamentV3Error(f"frozen git blob mismatch: {relpath}")
    return data


def load_frozen_tournament_v3(repo_root: Path | str = ".") -> FrozenTournamentV3:
    root = Path(repo_root)
    manifest_bytes = _read_pinned(root, MANIFEST_PATH, MANIFEST_GIT_BLOB)
    population_bytes = _read_pinned(root, POPULATION_PATH, POPULATION_GIT_BLOB)
    if sha256(population_bytes).hexdigest() != POPULATION_SHA256:
        raise TournamentV3Error("provider tournament v3 population SHA-256 mismatch")
    manifest = json.loads(manifest_bytes)
    population = json.loads(population_bytes)
    if manifest.get("schema_version") != "provider-tournament-v3-manifest":
        raise TournamentV3Error("unexpected v3 manifest schema")
    if population.get("schema_version") != "provider-tournament-v3-population":
        raise TournamentV3Error("unexpected v3 population schema")
    pop_meta = manifest.get("population", {})
    if (
        pop_meta.get("unit_count") != UNITS
        or pop_meta.get("repetitions_per_candidate") != REPETITIONS
        or pop_meta.get("attempts_per_candidate") != 85
        or pop_meta.get("total_live_attempts") != TOTAL_ATTEMPTS
        or pop_meta.get("sha256") != POPULATION_SHA256
    ):
        raise TournamentV3Error("v3 population geometry drift")
    request = manifest.get("request_contract", {})
    required_request = {
        "ai_gateway_used": False,
        "automatic_fallbacks": 0,
        "automatic_json_repair": False,
        "automatic_retries": 0,
        "controller_owns_agent_loop": True,
        "failed_attempts_remain_in_denominator": True,
        "harness_runner_owns_tool_execution": True,
        "max_input_tokens": 8000,
        "max_output_tokens": 512,
        "n": 1,
        "provider_native_tool_execution": False,
        "provider_side_state": False,
        "stream": False,
        "structured_output": "strict_json",
        "temperature": 0,
        "warmup_calls": 0,
        "web_search_used": False,
    }
    if any(request.get(k) != v for k, v in required_request.items()):
        raise TournamentV3Error("v3 request contract drift")
    candidates = manifest.get("candidates")
    if not isinstance(candidates, list) or [item.get("candidate_id") for item in candidates] != list(CANDIDATE_IDS):
        raise TournamentV3Error("v3 candidate identity drift")
    if [item.get("model") for item in candidates] != [CLOUDFLARE_GLM_MODEL_ID, CLOUDFLARE_NEMOTRON_MODEL_ID]:
        raise TournamentV3Error("v3 model identity drift")
    budget = manifest.get("usd0_budget", {})
    if (
        budget.get("workers_plan_required") != "Free"
        or budget.get("paid_workers_plan_allowed") is not False
        or budget.get("paid_fallback_allowed") is not False
        or budget.get("gateway_credits_allowed") is not False
        or float(budget.get("daily_free_neuron_limit", -1)) != DAILY_FREE_NEURONS
        or float(budget.get("minimum_reported_neurons_available_before_packet", -1)) != MIN_START_NEURONS
        or float(budget.get("max_daily_packet_neurons", -1)) != MAX_PACKET_NEURONS
    ):
        raise TournamentV3Error("v3 USD0 budget drift")
    if len(population.get("units", [])) != UNITS:
        raise TournamentV3Error("v3 population must contain exactly 17 units")
    return FrozenTournamentV3(manifest=manifest, population=population)


def build_packet_plan(bundle: FrozenTournamentV3, repetition_index: int) -> tuple[PacketPlanEntry, ...]:
    if repetition_index < 0 or repetition_index >= REPETITIONS:
        raise ValueError("repetition_index must be 0..4")
    entries: list[PacketPlanEntry] = []
    units = bundle.population["units"]
    for unit_index, unit in enumerate(units):
        ordered = CANDIDATE_IDS if (unit_index + repetition_index) % 2 == 0 else tuple(reversed(CANDIDATE_IDS))
        for candidate_id in ordered:
            packet_index = len(entries)
            entries.append(PacketPlanEntry(
                packet_attempt_index=packet_index,
                global_attempt_index=repetition_index * ATTEMPTS_PER_PACKET + packet_index,
                candidate_id=candidate_id,
                model_id=MODEL_BY_CANDIDATE[candidate_id],
                unit_id=unit["unit_id"],
                unit_index=unit_index,
                repetition_index=repetition_index,
            ))
    if len(entries) != ATTEMPTS_PER_PACKET:
        raise TournamentV3Error("v3 packet geometry mismatch")
    return tuple(entries)


def _unit(bundle: FrozenTournamentV3, unit_id: str) -> dict[str, Any]:
    for item in bundle.population["units"]:
        if item.get("unit_id") == unit_id:
            return item
    raise TournamentV3Error(f"unknown v3 unit: {unit_id}")


def context_for_unit(bundle: FrozenTournamentV3, unit_id: str) -> ControllerContext:
    raw = _unit(bundle, unit_id).get("context")
    if not isinstance(raw, dict):
        raise TournamentV3Error(f"invalid context: {unit_id}")
    return ControllerContext(
        user_request=raw["user_request"],
        turn_index=raw["turn_index"],
        tool_call_count=raw["tool_call_count"],
        observations=tuple(ControllerObservation.model_validate(item) for item in raw.get("observations", [])),
    )


def _nested_key(value: Any, forbidden: frozenset[str]) -> bool:
    if isinstance(value, Mapping):
        return any(str(k) in forbidden or _nested_key(v, forbidden) for k, v in value.items())
    if isinstance(value, list):
        return any(_nested_key(v, forbidden) for v in value)
    return False


class _InspectingClient:
    def __init__(self, inner: CloudflareWorkersAIChatCompletionsDecisionClient) -> None:
        self.inner = inner
        self.identity_seed_attempt = False
        self.private_key_attempt = False

    def complete(self, request: Any) -> str:
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


def _decision_text(decision: ControllerDecision) -> str:
    return json.dumps(decision.model_dump(mode="json"), sort_keys=True, ensure_ascii=False).lower()


def adjudicate_v3_rubric(bundle: FrozenTournamentV3, unit_id: str, decision: ControllerDecision | None) -> bool:
    if decision is None:
        return False
    rubric = _unit(bundle, unit_id).get("rubric")
    if not isinstance(rubric, dict):
        raise TournamentV3Error(f"invalid rubric: {unit_id}")
    allowed = rubric.get("allowed_kinds")
    if allowed is not None:
        if decision.kind.value not in allowed:
            return False
    elif rubric.get("kind") != decision.kind.value:
        return False
    if rubric.get("forbidden_tools") == "ALL" and decision.kind is ControllerDecisionKind.TOOL:
        return False
    retry = rubric.get("forbidden_tool_retry")
    if retry and decision.kind is ControllerDecisionKind.TOOL and decision.proposal and decision.proposal.tool_name == retry:
        return False
    expected_tool = rubric.get("tool_name")
    if expected_tool is not None:
        if decision.kind is not ControllerDecisionKind.TOOL or decision.proposal is None or decision.proposal.tool_name != expected_tool:
            return False
    if decision.kind is ControllerDecisionKind.TOOL and decision.proposal is not None:
        continuation = rubric.get("tool_if_continuing", {})
        if isinstance(continuation, dict) and continuation.get("allowed") and decision.proposal.tool_name not in continuation["allowed"]:
            return False
    arguments_rule = rubric.get("arguments")
    if arguments_rule is not None:
        if decision.proposal is None or not isinstance(arguments_rule, dict):
            return False
        arguments = decision.proposal.arguments
        exact = arguments_rule.get("exact")
        if exact is not None and arguments != exact:
            return False
        required = arguments_rule.get("required", {})
        if isinstance(required, dict) and any(arguments.get(k) != v for k, v in required.items()):
            return False
        contains = arguments_rule.get("contains_case_insensitive", {})
        if isinstance(contains, dict):
            for key, expected in contains.items():
                actual = arguments.get(key)
                if not isinstance(actual, str) or str(expected).lower() not in actual.lower():
                    return False
        allowed_optional = arguments_rule.get("allowed_optional_values", {})
        if isinstance(allowed_optional, dict):
            for key, values in allowed_optional.items():
                if key in arguments and arguments[key] not in values:
                    return False
        if any(key in arguments for key in arguments_rule.get("forbidden_keys", [])):
            return False
    text = _decision_text(decision)
    for claim in rubric.get("forbidden_claims", []):
        if str(claim).lower() in text:
            return False
    terminal = rubric.get("terminal_requirements", {})
    if isinstance(terminal, dict):
        if terminal.get("message_nonempty") and not (decision.message or "").strip():
            return False
        if terminal.get("reason_or_message_nonempty") and not ((decision.reason_code or "").strip() or (decision.message or "").strip()):
            return False
        if terminal.get("terminal_payload_nonempty"):
            if decision.kind is ControllerDecisionKind.FINAL:
                if not decision.final:
                    return False
            elif not ((decision.message or "").strip() or (decision.reason_code or "").strip()):
                return False
        if terminal.get("uncertainty_nonempty_if_terminal") and decision.kind is not ControllerDecisionKind.TOOL:
            uncertainty_terms = ("uncertain", "uncertainty", "conflict", "cannot", "insufficient", "inconclusive", "review")
            if not any(term in text for term in uncertainty_terms):
                return False
    return True


def observed_neurons(candidate_id: str, input_tokens: int, output_tokens: int) -> float:
    ir, orate = NEURON_RATES[candidate_id]
    return input_tokens * ir / 1_000_000 + output_tokens * orate / 1_000_000


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


def run_packet(
    *,
    repetition_index: int,
    available_free_neurons: float,
    api_token: str,
    account_id: str,
    output_path: Path,
    repo_root: Path | str = ".",
    transport: ProviderJsonTransport | None = None,
) -> dict[str, Any]:
    if available_free_neurons < MIN_START_NEURONS or available_free_neurons > DAILY_FREE_NEURONS:
        raise TournamentV3Error("H07 quota gate failed")
    bundle = load_frozen_tournament_v3(repo_root)
    plan = build_packet_plan(bundle, repetition_index)
    registry = canonical_tool_registry()
    clients: dict[str, _InspectingClient] = {}
    for candidate_id in CANDIDATE_IDS:
        inner = CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=api_token,
            account_id=account_id,
            model_id=MODEL_BY_CANDIDATE[candidate_id],
            transport=transport or UrllibProviderJsonTransport(),
        )
        clients[candidate_id] = _InspectingClient(inner)
    attempts: list[dict[str, Any]] = []
    packet_neurons = 0.0
    for entry in plan:
        remaining_worst = sum(MAX_NEURONS_PER_ATTEMPT[item.candidate_id] for item in plan[entry.packet_attempt_index:])
        if packet_neurons + remaining_worst > available_free_neurons or packet_neurons + remaining_worst > DAILY_FREE_NEURONS:
            raise TournamentV3Error("H08 projected packet budget gate failed")
        client = clients[entry.candidate_id]
        client.identity_seed_attempt = False
        client.private_key_attempt = False
        source = CloudflareProviderDecisionSourceV2(
            client=client,
            registry=registry,
            call_identity=CloudflareProviderCallIdentityV2(model_id=entry.model_id, live_call=True),
        )
        decision: ControllerDecision | None = None
        failure_code: str | None = None
        try:
            decision = source.decide(context_for_unit(bundle, entry.unit_id))
        except ProviderHttpClientError as exc:
            failure_code = str(exc)
        except Exception as exc:
            failure_code = type(exc).__name__
        audit_records = source.drain_audit_records()
        request_sha = None
        latency_ms = None
        trace_ok = False
        trace_issues: tuple[str, ...] = ("AUDIT_RECORD_MISSING",)
        if len(audit_records) == 1:
            request_sha = audit_records[0].metadata.get("request_sha256")
            if isinstance(request_sha, str):
                record, trace_ok, trace_issues = validate_cloudflare_audit_record_v2(
                    provider_id=CLOUDFLARE_PROVIDER_ID,
                    model_id=entry.model_id,
                    route_id=CLOUDFLARE_ROUTE_ID,
                    request_sha256=request_sha,
                    audit_records=audit_records,
                    live_call=True,
                )
                latency_ms = None if record is None else record.latency_ms
        usage_records = client.drain_usage_records()
        usage = usage_records[0] if len(usage_records) == 1 else None
        if decision is not None and usage is None:
            raise TournamentV3Error("H10 resource accounting missing on successful invocation")
        input_tokens = None if usage is None else usage.input_tokens
        output_tokens = None if usage is None else usage.output_tokens
        neurons = None
        if usage is not None:
            if input_tokens is None or output_tokens is None:
                raise TournamentV3Error("H10 exact provider usage missing")
            if input_tokens > 8000 or output_tokens > 512:
                raise TournamentV3Error("H08 per-attempt token ceiling exceeded")
            neurons = observed_neurons(entry.candidate_id, input_tokens, output_tokens)
            packet_neurons += neurons
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
        rubric_pass = adjudicate_v3_rubric(bundle, entry.unit_id, decision)
        attempts.append({
            "packet_attempt_index": entry.packet_attempt_index,
            "global_attempt_index": entry.global_attempt_index,
            "candidate_id": entry.candidate_id,
            "model_id": entry.model_id,
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
            "neurons": neurons,
            "known_tool_selection_valid": known_tool,
            "b1_valid": b1_valid,
            "b1_issue_codes": b1_issue_codes,
            "identity_seed_attempt": client.identity_seed_attempt,
            "private_key_attempt": client.private_key_attempt,
            "rubric_pass": rubric_pass,
            "raw_provider_material_recorded": False,
        })
        _write_json_atomic(output_path, {
            "schema_version": "provider-tournament-v3-packet-progress-v1",
            "repetition_index": repetition_index,
            "population_sha256": POPULATION_SHA256,
            "attempts": attempts,
            "packet_observed_neurons": packet_neurons,
            "complete": False,
        })
    packet = {
        "schema_version": "provider-tournament-v3-packet-v1",
        "repetition_index": repetition_index,
        "population_sha256": POPULATION_SHA256,
        "attempt_count": len(attempts),
        "attempts": attempts,
        "packet_observed_neurons": packet_neurons,
        "available_free_neurons_at_start": available_free_neurons,
        "actual_cash_cost_usd": 0.0,
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
    idx = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * q + 0.999999)))
    return ordered[idx]


def finalize_tournament(packet_paths: Sequence[Path]) -> dict[str, Any]:
    if len(packet_paths) != REPETITIONS:
        raise TournamentV3Error("H09 exactly five packet artifacts are required")
    packets = [json.loads(path.read_text(encoding="utf-8")) for path in packet_paths]
    reps = sorted(packet.get("repetition_index") for packet in packets)
    if reps != list(range(REPETITIONS)):
        raise TournamentV3Error("H09 repetition set must be exactly 0..4")
    if any(not packet.get("complete") or packet.get("attempt_count") != ATTEMPTS_PER_PACKET for packet in packets):
        raise TournamentV3Error("H09 incomplete packet")
    attempts = [attempt for packet in packets for attempt in packet["attempts"]]
    if len(attempts) != TOTAL_ATTEMPTS:
        raise TournamentV3Error("H09 total attempt geometry mismatch")
    summaries: dict[str, Any] = {}
    eligible: list[str] = []
    for candidate_id in CANDIDATE_IDS:
        rows = [row for row in attempts if row["candidate_id"] == candidate_id]
        if len(rows) != 85:
            raise TournamentV3Error("candidate attempt geometry mismatch")
        failures: list[str] = []
        if any(row.get("private_key_attempt") for row in rows): failures.append("H02_PRIVATE_GOLD")
        if any(not row.get("trace_integrity") for row in rows): failures.append("H06_H10_PROVENANCE")
        if any(row.get("raw_provider_material_recorded") for row in rows): failures.append("H10_RAW_MATERIAL")
        if any(row.get("identity_seed_attempt") for row in rows): failures.append("H04_BINDING_BYPASS")
        success_rate = _rate([row["outcome"] == "success" for row in rows])
        if success_rate < 0.9375: failures.append("H11_RELIABILITY")
        if any(row.get("neurons") is None for row in rows if row["outcome"] == "success"): failures.append("H10_RESOURCE_ACCOUNTING")
        rubric_rate = _rate([bool(row["rubric_pass"]) for row in rows])
        tool_rows = [row for row in rows if row.get("decision_kind") == "TOOL"]
        tool_validity = _rate([bool(row.get("known_tool_selection_valid")) for row in tool_rows]) if tool_rows else 1.0
        b1_rows = [row for row in tool_rows if row.get("known_tool_selection_valid")]
        argument_validity = _rate([bool(row.get("b1_valid")) for row in b1_rows]) if b1_rows else 1.0
        per_unit_stable = []
        for unit_index in range(UNITS):
            unit_rows = [row for row in rows if row["unit_index"] == unit_index]
            signatures = {(row.get("decision_kind"), row.get("tool_name") if row.get("decision_kind") == "TOOL" else None) for row in unit_rows if row["outcome"] == "success"}
            per_unit_stable.append(len(unit_rows) == REPETITIONS and len(signatures) == 1)
        latencies = [int(row["latency_ms"]) for row in rows if row.get("latency_ms") is not None]
        neurons_total = sum(float(row.get("neurons") or 0.0) for row in rows)
        summaries[candidate_id] = {
            "attempts": len(rows),
            "M01_operational_outcome_accuracy": rubric_rate,
            "M03_tool_selection": tool_validity,
            "M04_argument_validity": argument_validity,
            "M08_repeat_stability": _rate(per_unit_stable),
            "M09_reliability_success_rate": success_rate,
            "M09_latency_p50_ms": median(latencies) if latencies else None,
            "M09_latency_p95_ms": _percentile(latencies, 0.95),
            "M09_latency_p99_ms": _percentile(latencies, 0.99),
            "M10_total_neurons": neurons_total,
            "hard_gate_pass": not failures,
            "hard_gate_failures": failures,
        }
        if not failures:
            eligible.append(candidate_id)
    if not eligible:
        selection = "NO_SELECTION"
        reason = "NO_CANDIDATE_PASSED_HARD_GATES"
    elif len(eligible) == 1:
        selection = f"PROMOTE:{eligible[0]}"
        reason = "SOLE_HARD_GATE_ELIGIBLE_CANDIDATE"
    else:
        a, b = eligible
        sa, sb = summaries[a], summaries[b]
        quality_delta = sa["M01_operational_outcome_accuracy"] - sb["M01_operational_outcome_accuracy"]
        if abs(quality_delta) >= 0.02:
            winner = a if quality_delta > 0 else b
            selection = f"PROMOTE:{winner}"
            reason = "MATERIAL_PRIMARY_QUALITY_ADVANTAGE"
        else:
            ordered_metrics = [
                ("M03_tool_selection", True),
                ("M04_argument_validity", True),
                ("M08_repeat_stability", True),
                ("M09_reliability_success_rate", True),
                ("M10_total_neurons", False),
                ("M09_latency_p95_ms", False),
            ]
            winner = None
            for metric, higher_better in ordered_metrics:
                va, vb = sa.get(metric), sb.get(metric)
                if va is None or vb is None or va == vb:
                    continue
                winner = a if ((va > vb) == higher_better) else b
                break
            if winner is None:
                selection = "INCONCLUSIVE"
                reason = "NO_MATERIALLY_DEFENSIBLE_DIFFERENCE"
            else:
                selection = f"PROMOTE:{winner}"
                reason = "PREREGISTERED_TIE_BREAKER"
    result = {
        "schema_version": "provider-tournament-v3-final-result-v1",
        "decision_id": "DP-004",
        "population_sha256": POPULATION_SHA256,
        "total_attempts": len(attempts),
        "candidate_summaries": summaries,
        "selection": selection,
        "selection_reason": reason,
        "production_config_changed": False,
        "actual_cash_cost_usd": 0.0,
        "raw_provider_material_recorded": False,
    }
    return result
