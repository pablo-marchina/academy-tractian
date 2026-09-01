from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1, sha256
import json
from pathlib import Path
from statistics import median
from typing import Any, Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import ControllerDecision, ControllerDecisionKind
from research.e2.validation import validate_arguments

from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_MAX_ACCOUNTED_PROMPT_TOKENS,
    CLOUDFLARE_MAX_COMPLETION_TOKENS,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from .decision_source import ProviderCallIdentity, ProviderDecisionSource
from .provider_comparison import (
    FORBIDDEN_BINDING_KEYS,
    FORBIDDEN_PRIVATE_KEYS,
    LiveCallBudget,
    ProviderComparisonAttempt,
    _InspectingClient,
    _drain_usage,
    _nearest_rank,
    _nested_forbidden_key_present,
    _rate,
    _signature,
    _validate_audit_record,
    adjudicate_public_rubric,
    controller_context_for_unit,
)
from .runtime import canonical_tool_registry


CLOUDFLARE_PROVIDER_COMPARISON_EXECUTOR_VERSION = "cloudflare-provider-comparison-executor-v2"
CLOUDFLARE_PLAN_SCHEMA_VERSION = "cloudflare-provider-comparison-plan-v2"
CLOUDFLARE_RESULT_SCHEMA_VERSION = "cloudflare-provider-comparison-result-v2"

DESIGN_V2_PATH = "research/experiments/provider-model-comparison-design-manifest-v2.json"
POPULATION_PATH = "research/experiments/provider-model-comparison-dev-population-v1.json"
ADR_018_PATH = "docs/adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md"
ADR_019_PATH = "docs/adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md"
CLOUDFLARE_CLIENT_PATH = "src/academy_tractian/cloudflare_provider_client.py"

DESIGN_V2_GIT_BLOB = "f70837fca46fa8ecf1e63b33ea41dec73fc051e3"
POPULATION_GIT_BLOB = "abd6a7d973a8779f425c3607d963e29f15db09e5"
POPULATION_SHA256 = "561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251"
ADR_018_GIT_BLOB = "e075ab4ff21904b9412769496dd2680c049cdaa8"
ADR_019_GIT_BLOB = "b8f76831aceb13f5f3ffb5d7da0e12b595d9dd1a"
CLOUDFLARE_CLIENT_GIT_BLOB = "a5c814b519584b6d4346e3b0567bbc3da8ba0bf4"

GLM_CANDIDATE_ID = "cloudflare_glm_4_7_flash_workers_free"
NEMOTRON_CANDIDATE_ID = "cloudflare_nemotron_3_120b_a12b_workers_free"
CLOUDFLARE_LIVE_CANDIDATE_IDS = (GLM_CANDIDATE_ID, NEMOTRON_CANDIDATE_ID)

MAX_LIVE_ATTEMPTS_V2 = 32
EXPECTED_ATTEMPTS_PER_CANDIDATE_V2 = 16
MIN_FREE_NEURONS_BEFORE_ATTEMPT_1 = 9000.0
WORKERS_FREE_DAILY_NEURONS = 10000.0
MAX_PACKET_NEURONS = 7937.522688

NEURON_RATES_PER_MILLION: dict[str, tuple[float, float]] = {
    GLM_CANDIDATE_ID: (5500.0, 36400.0),
    NEMOTRON_CANDIDATE_ID: (45455.0, 136364.0),
}

EXPECTED_PLAN_SHA256 = "092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflareFrozenInputError(RuntimeError):
    """Current Cloudflare comparison inputs do not match ADR-018/019 frozen bytes."""


class CloudflareComparisonStopped(RuntimeError):
    """The v2 comparison hit a preregistered hard/resource stop."""


class CloudflareProviderComparisonPlanEntry(_FrozenModel):
    attempt_index: int = Field(ge=0, lt=MAX_LIVE_ATTEMPTS_V2)
    candidate_id: str
    provider_id: str
    model_id: str
    route_id: str
    unit_id: str
    unit_index: int = Field(ge=0, lt=8)
    repeat_index: int = Field(ge=0, lt=2)


class CloudflareProviderComparisonPlan(_FrozenModel):
    schema_version: Literal["cloudflare-provider-comparison-plan-v2"] = CLOUDFLARE_PLAN_SCHEMA_VERSION
    executor_version: Literal["cloudflare-provider-comparison-executor-v2"] = (
        CLOUDFLARE_PROVIDER_COMPARISON_EXECUTOR_VERSION
    )
    entries: tuple[CloudflareProviderComparisonPlanEntry, ...]
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_geometry(self) -> "CloudflareProviderComparisonPlan":
        if len(self.entries) != MAX_LIVE_ATTEMPTS_V2:
            raise ValueError("Cloudflare v2 plan must contain exactly 32 attempts")
        if tuple(item.attempt_index for item in self.entries) != tuple(
            range(MAX_LIVE_ATTEMPTS_V2)
        ):
            raise ValueError("Cloudflare v2 attempt indexes must be canonical 0..31")
        payload = {
            "schema_version": self.schema_version,
            "executor_version": self.executor_version,
            "entries": [item.model_dump(mode="json") for item in self.entries],
        }
        if self.plan_sha256 != _canonical_sha256(payload):
            raise ValueError("Cloudflare v2 plan_sha256 mismatch")
        return self


class CloudflareCandidateComparisonSummaryV2(_FrozenModel):
    candidate_id: str
    complete: bool
    attempts: int
    expected_attempts: Literal[16] = EXPECTED_ATTEMPTS_PER_CANDIDATE_V2
    M1_structured_decision_adherence: float | None
    M2_known_tool_selection_validity: float | None
    M3_b1_argument_validity: float | None
    M3_identity_seed_attempts: int
    M4_public_task_quality: float
    M5_safe_failure_behavior: float | None
    M6_latency_count: int
    M6_median_ms: float | None
    M6_p90_ms: int | None
    M6_p95_ms: int | None
    M6_max_ms: int | None
    M7_success_rate: float
    M7_signature_stability: float
    M8_usage_records: int
    M8_usage_complete: bool
    M8_total_observed_neurons: float | None
    M8_actual_cash_cost_usd: float | None
    M9_portability: dict[str, Any]
    M10_trace_integrity: float | None
    hard_gate_pass: bool
    hard_gate_failures: tuple[str, ...]


class CloudflareProviderComparisonResultV2(_FrozenModel):
    schema_version: Literal["cloudflare-provider-comparison-result-v2"] = (
        CLOUDFLARE_RESULT_SCHEMA_VERSION
    )
    executor_version: Literal["cloudflare-provider-comparison-executor-v2"] = (
        CLOUDFLARE_PROVIDER_COMPARISON_EXECUTOR_VERSION
    )
    fixture_result: bool
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    attempted_calls: int = Field(ge=0, le=MAX_LIVE_ATTEMPTS_V2)
    complete: bool
    stopped: bool
    stop_reason: str | None
    baseline_quality_rate: float
    available_free_neurons_at_start: float = Field(ge=0)
    packet_observed_neurons: float
    resource_accounting_complete: bool
    actual_cash_cost_usd: float | None
    candidates: tuple[CloudflareCandidateComparisonSummaryV2, ...]
    selection: str
    production_selection_claim: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False


@dataclass(frozen=True)
class FrozenCloudflareComparisonBundleV2:
    design: dict[str, Any]
    population: dict[str, Any]
    design_blob: str
    population_blob: str
    adr_018_blob: str
    adr_019_blob: str
    cloudflare_client_blob: str


def _canonical_sha256(payload: Any) -> str:
    data = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(data).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _read_exact_bytes(root: Path, relpath: str, expected_blob: str) -> bytes:
    data = (root / relpath).read_bytes()
    actual = _git_blob_sha1(data)
    if actual != expected_blob:
        raise CloudflareFrozenInputError(f"frozen git blob mismatch: {relpath}")
    return data


def _read_exact_json(root: Path, relpath: str, expected_blob: str) -> dict[str, Any]:
    data = _read_exact_bytes(root, relpath, expected_blob)
    try:
        payload = json.loads(data)
    except Exception as exc:
        raise CloudflareFrozenInputError(f"invalid frozen JSON: {relpath}") from exc
    if not isinstance(payload, dict):
        raise CloudflareFrozenInputError(f"frozen JSON must be object: {relpath}")
    return payload


def _live_candidates_from_design(design: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw = design.get("candidate_set")
    if not isinstance(raw, list):
        raise CloudflareFrozenInputError("design candidate_set invalid")
    live = [
        item
        for item in raw
        if isinstance(item, dict)
        and item.get("eligible_for_production_selection") is True
        and item.get("live_call") is True
    ]
    if [item.get("candidate_id") for item in live] != list(CLOUDFLARE_LIVE_CANDIDATE_IDS):
        raise CloudflareFrozenInputError("Cloudflare v2 live candidate identity drift")
    expected_models = [CLOUDFLARE_GLM_MODEL_ID, CLOUDFLARE_NEMOTRON_MODEL_ID]
    if [item.get("model_id") for item in live] != expected_models:
        raise CloudflareFrozenInputError("Cloudflare v2 model identity drift")
    if any(
        item.get("provider_id") != CLOUDFLARE_PROVIDER_ID
        or item.get("route_id") != CLOUDFLARE_ROUTE_ID
        for item in live
    ):
        raise CloudflareFrozenInputError("Cloudflare v2 provider/route drift")
    return live


def load_frozen_cloudflare_comparison_bundle_v2(
    repo_root: Path | str = ".",
) -> FrozenCloudflareComparisonBundleV2:
    root = Path(repo_root)
    design = _read_exact_json(root, DESIGN_V2_PATH, DESIGN_V2_GIT_BLOB)
    population_bytes = _read_exact_bytes(root, POPULATION_PATH, POPULATION_GIT_BLOB)
    try:
        population = json.loads(population_bytes)
    except Exception as exc:
        raise CloudflareFrozenInputError("invalid frozen comparison population JSON") from exc
    if not isinstance(population, dict):
        raise CloudflareFrozenInputError("comparison population must be an object")
    if sha256(population_bytes).hexdigest() != POPULATION_SHA256:
        raise CloudflareFrozenInputError("comparison population SHA-256 mismatch")

    adr018 = _read_exact_bytes(root, ADR_018_PATH, ADR_018_GIT_BLOB).decode("utf-8")
    adr019 = _read_exact_bytes(root, ADR_019_PATH, ADR_019_GIT_BLOB).decode("utf-8")
    _read_exact_bytes(root, CLOUDFLARE_CLIENT_PATH, CLOUDFLARE_CLIENT_GIT_BLOB)

    if "**Status:** ACCEPTED" not in adr018 or "FROZEN_PREREGISTRATION / LIVE_NOT_AUTHORIZED" not in adr018:
        raise CloudflareFrozenInputError("ADR-018 is not in the frozen preregistration state")
    if "**Status:** ACCEPTED" not in adr019 or "FROZEN_IMPLEMENTATION / LIVE_NOT_AUTHORIZED" not in adr019:
        raise CloudflareFrozenInputError("ADR-019 is not in the frozen implementation state")

    population_meta = design.get("population")
    execution = design.get("execution")
    resource = design.get("zero_cost_resource_budget")
    request_contract = design.get("request_contract")
    if not all(isinstance(item, dict) for item in (population_meta, execution, resource, request_contract)):
        raise CloudflareFrozenInputError("Cloudflare v2 design shape invalid")

    if population_meta.get("sha256") != POPULATION_SHA256 or population_meta.get("unit_count") != 8:
        raise CloudflareFrozenInputError("Cloudflare v2 population pin drift")
    if (
        execution.get("max_live_provider_calls_total") != MAX_LIVE_ATTEMPTS_V2
        or execution.get("attempts_per_live_candidate") != EXPECTED_ATTEMPTS_PER_CANDIDATE_V2
        or execution.get("automatic_retries") != 0
        or execution.get("provider_fallbacks") != 0
        or execution.get("warmup_calls") != 0
        or execution.get("parallel_live_calls") is not False
    ):
        raise CloudflareFrozenInputError("Cloudflare v2 execution contract drift")
    if (
        resource.get("required_workers_plan") != "Workers Free"
        or resource.get("workers_paid_plan_allowed") is not False
        or resource.get("prepaid_ai_gateway_credits_allowed") is not False
        or float(resource.get("published_free_neurons_per_day", -1)) != WORKERS_FREE_DAILY_NEURONS
        or float(resource.get("minimum_free_neurons_remaining_before_attempt_1", -1))
        != MIN_FREE_NEURONS_BEFORE_ATTEMPT_1
        or float(resource.get("max_packet_neurons", -1)) != MAX_PACKET_NEURONS
        or int(resource.get("max_accounted_input_tokens_per_attempt", -1))
        != CLOUDFLARE_MAX_ACCOUNTED_PROMPT_TOKENS
        or int(resource.get("max_completion_tokens_per_attempt", -1))
        != CLOUDFLARE_MAX_COMPLETION_TOKENS
    ):
        raise CloudflareFrozenInputError("Cloudflare v2 resource contract drift")
    if (
        request_contract.get("provider_native_tool_execution_enabled") is not False
        or request_contract.get("provider_side_conversation_state_enabled") is not False
        or request_contract.get("ai_gateway_enabled") is not False
        or request_contract.get("automatic_repair") is not False
    ):
        raise CloudflareFrozenInputError("Cloudflare v2 request boundary drift")

    _live_candidates_from_design(design)
    return FrozenCloudflareComparisonBundleV2(
        design=design,
        population=population,
        design_blob=DESIGN_V2_GIT_BLOB,
        population_blob=POPULATION_GIT_BLOB,
        adr_018_blob=ADR_018_GIT_BLOB,
        adr_019_blob=ADR_019_GIT_BLOB,
        cloudflare_client_blob=CLOUDFLARE_CLIENT_GIT_BLOB,
    )


def build_cloudflare_provider_comparison_plan_v2(
    bundle: FrozenCloudflareComparisonBundleV2,
) -> CloudflareProviderComparisonPlan:
    units = bundle.population.get("units")
    if not isinstance(units, list) or len(units) != 8:
        raise CloudflareFrozenInputError("comparison population must contain exactly 8 units")
    candidates = _live_candidates_from_design(bundle.design)

    entries: list[CloudflareProviderComparisonPlanEntry] = []
    for unit_index, unit in enumerate(units):
        if not isinstance(unit, dict) or not isinstance(unit.get("unit_id"), str):
            raise CloudflareFrozenInputError("invalid comparison unit")
        for repeat_index in range(2):
            ordered = candidates if (unit_index + repeat_index) % 2 == 0 else list(reversed(candidates))
            for candidate in ordered:
                entries.append(
                    CloudflareProviderComparisonPlanEntry(
                        attempt_index=len(entries),
                        candidate_id=str(candidate["candidate_id"]),
                        provider_id=str(candidate["provider_id"]),
                        model_id=str(candidate["model_id"]),
                        route_id=str(candidate["route_id"]),
                        unit_id=str(unit["unit_id"]),
                        unit_index=unit_index,
                        repeat_index=repeat_index,
                    )
                )

    payload = {
        "schema_version": CLOUDFLARE_PLAN_SCHEMA_VERSION,
        "executor_version": CLOUDFLARE_PROVIDER_COMPARISON_EXECUTOR_VERSION,
        "entries": [item.model_dump(mode="json") for item in entries],
    }
    plan = CloudflareProviderComparisonPlan(
        entries=tuple(entries),
        plan_sha256=_canonical_sha256(payload),
    )
    if plan.plan_sha256 != EXPECTED_PLAN_SHA256:
        raise CloudflareFrozenInputError("Cloudflare v2 canonical plan SHA drift")
    return plan


def observed_neurons(
    candidate_id: str,
    *,
    input_tokens: int,
    output_tokens: int,
) -> float:
    if candidate_id not in NEURON_RATES_PER_MILLION:
        raise ValueError("unknown Cloudflare v2 candidate")
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token usage must be nonnegative")
    input_rate, output_rate = NEURON_RATES_PER_MILLION[candidate_id]
    return (
        input_tokens * input_rate / 1_000_000
        + output_tokens * output_rate / 1_000_000
    )


def worst_case_neurons_for_candidate(candidate_id: str) -> float:
    return observed_neurons(
        candidate_id,
        input_tokens=CLOUDFLARE_MAX_ACCOUNTED_PROMPT_TOKENS,
        output_tokens=CLOUDFLARE_MAX_COMPLETION_TOKENS,
    )


def _portability_v2(
    *,
    candidate_id: str,
    fixture_result: bool,
    available_free_neurons: float,
) -> dict[str, Any]:
    return {
        "direct_workers_ai_http_dependency": True,
        "credential_account_requirements": "explicit_api_token_and_account_id",
        "Workers_Free_requirement": True,
        "observed_rate_capacity_constraints": (
            "NOT_OBSERVED_FIXTURE" if fixture_result else "OBSERVED_AT_EXECUTION"
        ),
        "reproducibility_limitations": "provider_seed_not_forwarded",
        "free_neuron_headroom_at_start": available_free_neurons,
        "candidate_id": candidate_id,
    }


def summarize_cloudflare_candidate_v2(
    bundle: FrozenCloudflareComparisonBundleV2,
    candidate_id: str,
    attempts: Sequence[ProviderComparisonAttempt],
    *,
    fixed_failure_probe_passed: bool,
    fixture_result: bool,
    zero_cash_cost_route_proven: bool,
    available_free_neurons: float,
) -> CloudflareCandidateComparisonSummaryV2:
    if len({item.attempt_index for item in attempts}) != len(attempts):
        raise ValueError("duplicate attempt_index in candidate evidence")
    ordered = tuple(sorted(attempts, key=lambda item: item.attempt_index))
    parsed = [item for item in ordered if item.structured_decision_adherent]
    tool_items = [
        item for item in parsed if item.decision_kind == ControllerDecisionKind.TOOL.value
    ]
    b1_items = [item for item in tool_items if item.b1_valid is not None]
    failures = [item for item in ordered if item.outcome == "failure"]
    safe_failure_num = (
        sum(item.safe_failure_contained is True for item in failures)
        + int(fixed_failure_probe_passed)
    )
    safe_failure_den = len(failures) + 1
    latencies = [item.latency_ms for item in ordered if item.latency_ms is not None]

    stable = 0
    for unit in bundle.population["units"]:
        pair = [item for item in ordered if item.unit_id == unit["unit_id"]]
        if len(pair) != 2:
            continue
        first, second = sorted(pair, key=lambda item: item.repeat_index)
        signature = _signature(first)
        if signature is not None and signature == _signature(second):
            stable += 1

    complete = len(ordered) == EXPECTED_ATTEMPTS_PER_CANDIDATE_V2
    usage_complete = complete and all(
        item.input_tokens is not None and item.output_tokens is not None for item in ordered
    )
    total_neurons = (
        sum(
            observed_neurons(
                candidate_id,
                input_tokens=int(item.input_tokens),
                output_tokens=int(item.output_tokens),
            )
            for item in ordered
        )
        if usage_complete
        else None
    )

    m1 = _rate(len(parsed), len(ordered))
    m2 = _rate(sum(item.known_tool_selection_valid is True for item in tool_items), len(tool_items))
    m3 = _rate(sum(item.b1_valid is True for item in b1_items), len(b1_items))
    m4 = sum(item.rubric_pass for item in ordered) / EXPECTED_ATTEMPTS_PER_CANDIDATE_V2
    m5 = _rate(safe_failure_num, safe_failure_den)
    m7_success = sum(item.outcome == "success" for item in ordered) / EXPECTED_ATTEMPTS_PER_CANDIDATE_V2
    m7_stability = stable / 8
    m10 = _rate(sum(item.trace_integrity for item in ordered), len(ordered))

    hard_failures: list[str] = []
    if any(item.identity_seed_attempt or item.private_key_attempt for item in ordered):
        hard_failures.append("H1_PRIVATE_OR_BINDING_LEAKAGE")
    if any("HIDDEN_RETRY_OR_FALLBACK" in item.trace_issue_codes for item in ordered):
        hard_failures.append("H3_HIDDEN_RETRY_OR_FALLBACK")
    if any(not item.trace_integrity for item in ordered):
        hard_failures.append("H4_MODEL_CALL_PROVENANCE")
    if any(item.raw_material_recorded for item in ordered):
        hard_failures.append("H6_RAW_MATERIAL_RECORDED")
    if any("ROUTE_OR_MODEL_IDENTITY" in item.trace_issue_codes for item in ordered):
        hard_failures.append("H7_ROUTE_OR_MODEL_CHANGED")
    if not zero_cash_cost_route_proven:
        hard_failures.append("H8_NONFREE_OR_PAID_ROUTE")
    if not usage_complete:
        hard_failures.append("H9_RESOURCE_ACCOUNTING_INCOMPLETE")
    if any(
        (item.input_tokens is not None and item.input_tokens > CLOUDFLARE_MAX_ACCOUNTED_PROMPT_TOKENS)
        or (item.output_tokens is not None and item.output_tokens > CLOUDFLARE_MAX_COMPLETION_TOKENS)
        for item in ordered
    ):
        hard_failures.append("H10_PER_ATTEMPT_RESOURCE_CEILING")
    if total_neurons is not None and total_neurons > MAX_PACKET_NEURONS:
        hard_failures.append("H10_PACKET_RESOURCE_CEILING")
    if not complete:
        hard_failures.append("INCOMPLETE_PACKET")

    metrics = bundle.design["metrics"]
    if complete:
        if m1 is None or m1 < metrics["M1"]["minimum"]:
            hard_failures.append("M1_BELOW_MINIMUM")
        if m4 < metrics["M4"]["minimum"]:
            hard_failures.append("M4_BELOW_MINIMUM")
        if m5 is None or m5 < metrics["M5"]["minimum"]:
            hard_failures.append("M5_BELOW_MINIMUM")
        if (
            m7_success < metrics["M7"]["minimum_success_rate"]
            or m7_stability < metrics["M7"]["minimum_signature_stability"]
        ):
            hard_failures.append("M7_BELOW_MINIMUM")
        if m10 is None or m10 < metrics["M10"]["minimum"]:
            hard_failures.append("M10_BELOW_MINIMUM")

    return CloudflareCandidateComparisonSummaryV2(
        candidate_id=candidate_id,
        complete=complete,
        attempts=len(ordered),
        M1_structured_decision_adherence=m1,
        M2_known_tool_selection_validity=m2,
        M3_b1_argument_validity=m3,
        M3_identity_seed_attempts=sum(item.identity_seed_attempt for item in ordered),
        M4_public_task_quality=m4,
        M5_safe_failure_behavior=m5,
        M6_latency_count=len(latencies),
        M6_median_ms=None if not latencies else float(median(latencies)),
        M6_p90_ms=_nearest_rank(latencies, 0.90),
        M6_p95_ms=_nearest_rank(latencies, 0.95),
        M6_max_ms=None if not latencies else max(latencies),
        M7_success_rate=m7_success,
        M7_signature_stability=m7_stability,
        M8_usage_records=sum(
            item.input_tokens is not None and item.output_tokens is not None for item in ordered
        ),
        M8_usage_complete=usage_complete,
        M8_total_observed_neurons=total_neurons,
        M8_actual_cash_cost_usd=0.0 if zero_cash_cost_route_proven else None,
        M9_portability=_portability_v2(
            candidate_id=candidate_id,
            fixture_result=fixture_result,
            available_free_neurons=available_free_neurons,
        ),
        M10_trace_integrity=m10,
        hard_gate_pass=not hard_failures,
        hard_gate_failures=tuple(dict.fromkeys(hard_failures)),
    )


def _dominates_v2(
    left: CloudflareCandidateComparisonSummaryV2,
    right: CloudflareCandidateComparisonSummaryV2,
) -> bool:
    if (
        left.M6_p95_ms is None
        or right.M6_p95_ms is None
        or left.M8_total_observed_neurons is None
        or right.M8_total_observed_neurons is None
    ):
        return False
    dimensions = (
        (left.M4_public_task_quality, right.M4_public_task_quality, True),
        (left.M7_success_rate, right.M7_success_rate, True),
        (left.M7_signature_stability, right.M7_signature_stability, True),
        (float(left.M6_p95_ms), float(right.M6_p95_ms), False),
        (left.M8_total_observed_neurons, right.M8_total_observed_neurons, False),
    )
    no_worse = all(
        a >= b if maximize else a <= b for a, b, maximize in dimensions
    )
    strictly_better = any(
        a > b if maximize else a < b for a, b, maximize in dimensions
    )
    return no_worse and strictly_better


def select_cloudflare_candidate_v2(
    summaries: Sequence[CloudflareCandidateComparisonSummaryV2],
    *,
    fixture_result: bool,
) -> str:
    if fixture_result:
        return "NO_SELECTION"
    eligible = [item for item in summaries if item.hard_gate_pass and item.complete]
    if not eligible:
        return "NO_SELECTION"
    if len(eligible) == 1:
        return eligible[0].candidate_id

    pareto = [
        item
        for item in eligible
        if not any(
            _dominates_v2(other, item)
            for other in eligible
            if other.candidate_id != item.candidate_id
        )
    ]
    if len(pareto) == 1:
        return pareto[0].candidate_id

    ranked_quality = sorted(pareto, key=lambda item: (-item.M4_public_task_quality, item.candidate_id))
    top_quality = ranked_quality[0]
    if all(
        top_quality.M4_public_task_quality - other.M4_public_task_quality >= 0.125
        for other in ranked_quality[1:]
    ):
        return top_quality.candidate_id

    if all(item.M8_total_observed_neurons is not None for item in pareto):
        by_neurons = sorted(
            pareto,
            key=lambda item: (float(item.M8_total_observed_neurons), item.candidate_id),
        )
        unique_lowest = (
            len(by_neurons) == 1
            or float(by_neurons[0].M8_total_observed_neurons)
            < float(by_neurons[1].M8_total_observed_neurons)
        )
        best_stability = max(item.M7_signature_stability for item in pareto)
        if (
            unique_lowest
            and by_neurons[0].M7_signature_stability >= best_stability - 0.125
        ):
            return by_neurons[0].candidate_id

    if all(item.M6_p95_ms is not None for item in pareto):
        by_latency = sorted(pareto, key=lambda item: (int(item.M6_p95_ms), item.candidate_id))
        if len(by_latency) == 1 or int(by_latency[0].M6_p95_ms) < int(by_latency[1].M6_p95_ms):
            return by_latency[0].candidate_id
    return "NO_SELECTION"


class CloudflareProviderComparisonExecutorV2:
    """ADR-018/019 bounded comparison executor.

    The provider-free task validates this class only with local fake clients/transports.
    Capability is not live authorization.
    """

    def __init__(
        self,
        *,
        bundle: FrozenCloudflareComparisonBundleV2,
        clients: Mapping[str, Any],
        fixture_result: bool,
        available_free_neurons: float,
        zero_cash_cost_route_proven: bool,
    ) -> None:
        if available_free_neurons < MIN_FREE_NEURONS_BEFORE_ATTEMPT_1:
            raise ValueError("Cloudflare v2 requires at least 9000 free neurons before attempt 1")
        if available_free_neurons > WORKERS_FREE_DAILY_NEURONS:
            raise ValueError("free-neuron evidence exceeds Workers Free daily allocation")
        if not zero_cash_cost_route_proven:
            raise ValueError("Cloudflare v2 requires a prevalidated zero-cash Workers Free route")

        self.bundle = bundle
        self.plan = build_cloudflare_provider_comparison_plan_v2(bundle)
        self.clients = dict(clients)
        self.fixture_result = fixture_result
        self.available_free_neurons = float(available_free_neurons)
        self.zero_cash_cost_route_proven = zero_cash_cost_route_proven
        self.registry = canonical_tool_registry()
        self.budget = LiveCallBudget()
        self.attempts: list[ProviderComparisonAttempt] = []
        self.stopped = False
        self.stop_reason: str | None = None
        self.packet_observed_neurons = 0.0

        if set(self.clients) != set(CLOUDFLARE_LIVE_CANDIDATE_IDS):
            raise ValueError("client mapping must match the two ADR-018 Cloudflare candidates")
        if not fixture_result:
            expected_models = {
                GLM_CANDIDATE_ID: CLOUDFLARE_GLM_MODEL_ID,
                NEMOTRON_CANDIDATE_ID: CLOUDFLARE_NEMOTRON_MODEL_ID,
            }
            for candidate_id, client in self.clients.items():
                if not isinstance(client, CloudflareWorkersAIChatCompletionsDecisionClient):
                    raise ValueError("live v2 execution requires the exact ADR-019 Cloudflare client")
                if client.model_id != expected_models[candidate_id]:
                    raise ValueError("live v2 client model identity mismatch")

    def baseline_quality_rate(self) -> float:
        baseline = ControllerDecision(
            kind=ControllerDecisionKind.ABSTAIN,
            reason_code="BASELINE_NO_PROVIDER",
            message="Provider-free baseline does not make a provider decision.",
        )
        total = 0
        passed = 0
        for unit in self.bundle.population["units"]:
            for _ in range(2):
                total += 1
                passed += int(adjudicate_public_rubric(self.bundle, unit["unit_id"], baseline))
        return passed / total

    def _remaining_worst_case(self) -> float:
        return sum(
            worst_case_neurons_for_candidate(item.candidate_id)
            for item in self.plan.entries[self.budget.consumed :]
        )

    def assert_next_attempt_allowed(self) -> None:
        if self.stopped:
            raise CloudflareComparisonStopped(self.stop_reason or "comparison stopped")
        if self.budget.remaining <= 0:
            return
        projected = self.packet_observed_neurons + self._remaining_worst_case()
        if projected > self.available_free_neurons + 1e-9:
            self.stopped = True
            self.stop_reason = "H10_PROJECTED_FREE_ALLOCATION_EXCEEDED"
            raise CloudflareComparisonStopped(self.stop_reason)

    def execute_next(self) -> ProviderComparisonAttempt:
        self.assert_next_attempt_allowed()
        entry = self.plan.entries[self.budget.consumed]
        client = self.clients[entry.candidate_id]
        context = controller_context_for_unit(self.bundle, entry.unit_id)
        inspector = _InspectingClient(client)
        source = ProviderDecisionSource(
            client=inspector,
            registry=self.registry,
            call_identity=ProviderCallIdentity(
                provider_id=entry.provider_id,
                model_id=entry.model_id,
                route_id=entry.route_id,
                live_call=not self.fixture_result,
            ),
        )
        request = source.build_request(context)
        if _nested_forbidden_key_present(
            request.model_dump(mode="json"),
            FORBIDDEN_BINDING_KEYS | FORBIDDEN_PRIVATE_KEYS,
        ):
            raise CloudflareFrozenInputError(
                "provider request contains forbidden runtime/private keys"
            )

        self.budget.consume(entry.attempt_index)
        decision = None
        try:
            decision = source.decide(context)
        except Exception:
            pass

        audit_items = source.drain_audit_records()
        audit, trace_integrity, trace_issue_codes = _validate_audit_record(
            entry,
            request.request_sha256,
            audit_items,
            live_call=not self.fixture_result,
        )
        usage = _drain_usage(client, request.request_sha256)

        b1_valid: bool | None = None
        b1_codes: tuple[str, ...] = ()
        known_tool_valid: bool | None = None
        tool_name: str | None = None
        if decision is not None and decision.kind is ControllerDecisionKind.TOOL:
            assert decision.proposal is not None
            tool_name = decision.proposal.tool_name
            known_tool_valid = tool_name in self.registry
            if known_tool_valid:
                issues = validate_arguments(
                    self.registry[tool_name],
                    decision.proposal.arguments,
                )
                b1_codes = tuple(item.code for item in issues)
                b1_valid = not issues

        raw_material_recorded = bool(
            audit is not None
            and (
                audit.raw_request_recorded
                or audit.raw_response_recorded
                or audit.exception_text_recorded
            )
        )
        safe_failure: bool | None = None
        if decision is None:
            safe_failure = bool(
                trace_integrity
                and not inspector.inspection.identity_seed_attempt
                and not inspector.inspection.private_key_attempt
                and not raw_material_recorded
            )

        attempt = ProviderComparisonAttempt(
            fixture_result=self.fixture_result,
            attempt_index=entry.attempt_index,
            candidate_id=entry.candidate_id,
            unit_id=entry.unit_id,
            repeat_index=entry.repeat_index,
            request_sha256=request.request_sha256,
            call_id=None if audit is None else audit.call_id,
            outcome="success" if decision is not None else "failure",
            decision_kind=None if decision is None else decision.kind.value,
            tool_name=tool_name,
            failure_code=(
                None
                if decision is not None
                else (
                    "DECISION_SOURCE_FAILURE"
                    if audit is None or audit.failure_code is None
                    else audit.failure_code
                )
            ),
            latency_ms=None if audit is None else audit.latency_ms,
            input_tokens=None if usage is None else usage.input_tokens,
            output_tokens=None if usage is None else usage.output_tokens,
            total_tokens=None if usage is None else usage.total_tokens,
            reasoning_tokens=None if usage is None else usage.reasoning_tokens,
            structured_decision_adherent=decision is not None,
            known_tool_selection_valid=known_tool_valid,
            b1_valid=b1_valid,
            b1_issue_codes=b1_codes,
            identity_seed_attempt=inspector.inspection.identity_seed_attempt,
            private_key_attempt=inspector.inspection.private_key_attempt,
            rubric_pass=adjudicate_public_rubric(self.bundle, entry.unit_id, decision),
            trace_integrity=trace_integrity,
            trace_issue_codes=trace_issue_codes,
            safe_failure_contained=safe_failure,
            raw_material_recorded=raw_material_recorded,
        )
        self.attempts.append(attempt)

        if (
            attempt.identity_seed_attempt
            or attempt.private_key_attempt
            or attempt.raw_material_recorded
            or not attempt.trace_integrity
        ):
            self.stopped = True
            self.stop_reason = "HARD_GATE_STOP"
            return attempt

        if attempt.input_tokens is None or attempt.output_tokens is None:
            self.stopped = True
            self.stop_reason = "H9_RESOURCE_ACCOUNTING_INCOMPLETE"
            return attempt
        if attempt.input_tokens > CLOUDFLARE_MAX_ACCOUNTED_PROMPT_TOKENS:
            self.stopped = True
            self.stop_reason = "H10_PROMPT_TOKEN_CEILING_EXCEEDED"
            return attempt
        if attempt.output_tokens > CLOUDFLARE_MAX_COMPLETION_TOKENS:
            self.stopped = True
            self.stop_reason = "H10_COMPLETION_TOKEN_CEILING_EXCEEDED"
            return attempt

        self.packet_observed_neurons += observed_neurons(
            entry.candidate_id,
            input_tokens=attempt.input_tokens,
            output_tokens=attempt.output_tokens,
        )
        if self.packet_observed_neurons > MAX_PACKET_NEURONS + 1e-9:
            self.stopped = True
            self.stop_reason = "H10_PACKET_NEURON_CEILING_EXCEEDED"
        return attempt

    def run_all_fixture(self) -> tuple[ProviderComparisonAttempt, ...]:
        if not self.fixture_result:
            raise ValueError("run_all_fixture is provider-free only")
        while self.budget.remaining and not self.stopped:
            self.execute_next()
        return tuple(self.attempts)

    def finalize(
        self,
        *,
        fixed_failure_probe_passed: Mapping[str, bool],
    ) -> CloudflareProviderComparisonResultV2:
        if set(fixed_failure_probe_passed) != set(CLOUDFLARE_LIVE_CANDIDATE_IDS):
            raise ValueError("fixed failure evidence must cover both Cloudflare candidates")
        seen = [item.attempt_index for item in self.attempts]
        if seen != list(range(len(seen))):
            raise ValueError("comparison evidence must be a canonical plan prefix")

        summaries = tuple(
            summarize_cloudflare_candidate_v2(
                self.bundle,
                candidate_id,
                [item for item in self.attempts if item.candidate_id == candidate_id],
                fixed_failure_probe_passed=bool(fixed_failure_probe_passed[candidate_id]),
                fixture_result=self.fixture_result,
                zero_cash_cost_route_proven=self.zero_cash_cost_route_proven,
                available_free_neurons=self.available_free_neurons,
            )
            for candidate_id in CLOUDFLARE_LIVE_CANDIDATE_IDS
        )
        complete = len(self.attempts) == MAX_LIVE_ATTEMPTS_V2 and not self.stopped
        accounting_complete = complete and all(item.M8_usage_complete for item in summaries)
        selection = select_cloudflare_candidate_v2(
            summaries,
            fixture_result=self.fixture_result or not complete or not accounting_complete,
        )
        return CloudflareProviderComparisonResultV2(
            fixture_result=self.fixture_result,
            plan_sha256=self.plan.plan_sha256,
            attempted_calls=len(self.attempts),
            complete=complete,
            stopped=self.stopped,
            stop_reason=self.stop_reason,
            baseline_quality_rate=self.baseline_quality_rate(),
            available_free_neurons_at_start=self.available_free_neurons,
            packet_observed_neurons=self.packet_observed_neurons,
            resource_accounting_complete=accounting_complete,
            actual_cash_cost_usd=0.0 if self.zero_cash_cost_route_proven else None,
            candidates=summaries,
            selection=selection,
        )
