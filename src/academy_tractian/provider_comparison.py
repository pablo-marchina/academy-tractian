from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1, sha256
import json
from math import ceil
from pathlib import Path
from statistics import median
from typing import Any, Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ControllerObservation,
)
from research.e2.validation import validate_arguments

from .decision_source import (
    ProviderCallIdentity,
    ProviderDecisionClient,
    ProviderDecisionRequest,
    ProviderDecisionSource,
    ProviderModelCallRecord,
)
from .provider_clients import ProviderUsageRecord
from .runtime import canonical_tool_registry


PROVIDER_COMPARISON_EXECUTOR_VERSION = "provider-comparison-executor-v1"

DESIGN_MANIFEST_PATH = "research/experiments/provider-model-comparison-design-manifest-v1.json"
POPULATION_PATH = "research/experiments/provider-model-comparison-dev-population-v1.json"
AUTHORIZATION_PATH = "research/frozen/provider-model-live-comparison-authorization-v1.json"
ADR_009_PATH = "docs/adr/009-provider-http-clients-live-comparison-authorization-2026-08-28.md"
PROVIDER_CLIENTS_PATH = "src/academy_tractian/provider_clients.py"

DESIGN_MANIFEST_GIT_BLOB = "9c3d0901414445bd4de557d5ef1d2f68a15c883b"
POPULATION_GIT_BLOB = "abd6a7d973a8779f425c3607d963e29f15db09e5"
AUTHORIZATION_GIT_BLOB = "5690414564ccddb07184c333fdf79f4ee2fb7788"
ADR_009_GIT_BLOB = "016ac0c40e12db211ebf7dfbab3acd258369fa0b"
PROVIDER_CLIENTS_GIT_BLOB = "e78807bdfd4fd0ca9840fa2d9e6c62474237ee45"
POPULATION_SHA256 = "561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251"

MAX_LIVE_ATTEMPTS = 32
EXPECTED_ATTEMPTS_PER_CANDIDATE = 16
FORBIDDEN_BINDING_KEYS = frozenset({"user_id", "x-user-id", "identity_id", "seed"})
FORBIDDEN_PRIVATE_KEYS = frozenset(
    {"gold", "oracle", "expected_path", "expected_paths", "private_truth"}
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FrozenInputError(RuntimeError):
    """The checkout no longer matches the exact ADR-008/009 frozen inputs."""


class ComparisonStopped(RuntimeError):
    """The comparison hit a preregistered hard stop."""


class CallBudgetExceeded(RuntimeError):
    """The non-resettable 32-attempt budget is exhausted."""


class ProviderComparisonPlanEntry(_FrozenModel):
    attempt_index: int = Field(ge=0, lt=MAX_LIVE_ATTEMPTS)
    candidate_id: str
    provider_id: str
    model_id: str
    route_id: str
    unit_id: str
    unit_index: int = Field(ge=0, lt=8)
    repeat_index: int = Field(ge=0, lt=2)


class ProviderComparisonPlan(_FrozenModel):
    schema_version: Literal["provider-comparison-plan-v1"] = "provider-comparison-plan-v1"
    executor_version: Literal["provider-comparison-executor-v1"] = PROVIDER_COMPARISON_EXECUTOR_VERSION
    entries: tuple[ProviderComparisonPlanEntry, ...]
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_geometry(self) -> "ProviderComparisonPlan":
        if len(self.entries) != MAX_LIVE_ATTEMPTS:
            raise ValueError("comparison plan must contain exactly 32 live attempts")
        if tuple(item.attempt_index for item in self.entries) != tuple(range(MAX_LIVE_ATTEMPTS)):
            raise ValueError("comparison attempt indexes must be contiguous 0..31")
        payload = {
            "schema_version": self.schema_version,
            "executor_version": self.executor_version,
            "entries": [item.model_dump(mode="json") for item in self.entries],
        }
        if self.plan_sha256 != _canonical_sha256(payload):
            raise ValueError("plan_sha256 does not match canonical plan payload")
        return self


class ProviderComparisonAttempt(_FrozenModel):
    schema_version: Literal["provider-comparison-attempt-v1"] = "provider-comparison-attempt-v1"
    fixture_result: bool
    attempt_index: int = Field(ge=0, lt=MAX_LIVE_ATTEMPTS)
    candidate_id: str
    unit_id: str
    repeat_index: int = Field(ge=0, lt=2)
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    call_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    outcome: Literal["success", "failure"]
    decision_kind: str | None = None
    tool_name: str | None = None
    failure_code: str | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    structured_decision_adherent: bool
    known_tool_selection_valid: bool | None = None
    b1_valid: bool | None = None
    b1_issue_codes: tuple[str, ...] = ()
    identity_seed_attempt: bool = False
    private_key_attempt: bool = False
    rubric_pass: bool
    trace_integrity: bool
    trace_issue_codes: tuple[str, ...] = ()
    safe_failure_contained: bool | None = None
    raw_material_recorded: bool = False


class CandidateComparisonSummary(_FrozenModel):
    candidate_id: str
    complete: bool
    attempts: int
    expected_attempts: Literal[16] = EXPECTED_ATTEMPTS_PER_CANDIDATE
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
    M8_normalized_cost_usd: float | None
    M9_portability: dict[str, Any]
    M10_trace_integrity: float | None
    hard_gate_pass: bool
    hard_gate_failures: tuple[str, ...]


class ProviderComparisonResult(_FrozenModel):
    schema_version: Literal["provider-comparison-result-v1"] = "provider-comparison-result-v1"
    executor_version: Literal["provider-comparison-executor-v1"] = PROVIDER_COMPARISON_EXECUTOR_VERSION
    fixture_result: bool
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    attempted_calls: int = Field(ge=0, le=MAX_LIVE_ATTEMPTS)
    complete: bool
    stopped: bool
    stop_reason: str | None
    baseline_quality_rate: float
    candidates: tuple[CandidateComparisonSummary, ...]
    selection: str
    production_selection_claim: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False


@dataclass(frozen=True)
class FrozenComparisonBundle:
    design: dict[str, Any]
    population: dict[str, Any]
    authorization: dict[str, Any]
    design_blob: str
    population_blob: str
    authorization_blob: str
    adr_009_blob: str
    provider_clients_blob: str


class LiveCallBudget:
    """Non-resettable, canonical-order attempt budget.

    In fixture mode this counts simulated potential live attempts. In a later separately governed
    live task it becomes the exact ADR-009 consumed-call counter.
    """

    def __init__(self, max_calls: int = MAX_LIVE_ATTEMPTS) -> None:
        if max_calls != MAX_LIVE_ATTEMPTS:
            raise ValueError("ADR-009 live-call budget is fixed at 32")
        self._max_calls = max_calls
        self._consumed = 0

    @property
    def consumed(self) -> int:
        return self._consumed

    @property
    def remaining(self) -> int:
        return self._max_calls - self._consumed

    def consume(self, attempt_index: int) -> None:
        if self._consumed >= self._max_calls:
            raise CallBudgetExceeded("ADR-009 call budget exhausted")
        if attempt_index != self._consumed:
            raise ValueError("comparison attempts must consume budget in canonical order")
        self._consumed += 1


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return sha1(header + data).hexdigest()


def _read_exact_json(
    repo_root: Path,
    relpath: str,
    expected_blob: str,
) -> tuple[dict[str, Any], str, bytes]:
    data = (repo_root / relpath).read_bytes()
    actual_blob = _git_blob_sha1(data)
    if actual_blob != expected_blob:
        raise FrozenInputError(f"frozen git blob mismatch: {relpath}")
    try:
        value = json.loads(data)
    except Exception as exc:
        raise FrozenInputError(f"invalid frozen JSON: {relpath}") from exc
    if not isinstance(value, dict):
        raise FrozenInputError(f"frozen JSON must be an object: {relpath}")
    return value, actual_blob, data


def load_frozen_provider_comparison_bundle(
    repo_root: Path | str = ".",
) -> FrozenComparisonBundle:
    root = Path(repo_root)
    design, design_blob, _ = _read_exact_json(
        root,
        DESIGN_MANIFEST_PATH,
        DESIGN_MANIFEST_GIT_BLOB,
    )
    population, population_blob, population_bytes = _read_exact_json(
        root,
        POPULATION_PATH,
        POPULATION_GIT_BLOB,
    )
    authorization, authorization_blob, _ = _read_exact_json(
        root,
        AUTHORIZATION_PATH,
        AUTHORIZATION_GIT_BLOB,
    )

    adr_009_bytes = (root / ADR_009_PATH).read_bytes()
    adr_009_blob = _git_blob_sha1(adr_009_bytes)
    if adr_009_blob != ADR_009_GIT_BLOB:
        raise FrozenInputError("ADR-009 git blob mismatch")
    adr_text = adr_009_bytes.decode("utf-8")
    if "**Status:** ACCEPTED" not in adr_text:
        raise FrozenInputError("ADR-009 is not accepted")

    provider_clients_bytes = (root / PROVIDER_CLIENTS_PATH).read_bytes()
    provider_clients_blob = _git_blob_sha1(provider_clients_bytes)
    if provider_clients_blob != PROVIDER_CLIENTS_GIT_BLOB:
        raise FrozenInputError("validated provider client implementation blob mismatch")

    if sha256(population_bytes).hexdigest() != POPULATION_SHA256:
        raise FrozenInputError("frozen population SHA-256 mismatch")
    if design.get("population", {}).get("sha256") != POPULATION_SHA256:
        raise FrozenInputError("design does not pin the frozen population SHA-256")

    frozen_design = authorization.get("frozen_design")
    validated_client = authorization.get("validated_provider_client_implementation")
    authz = authorization.get("authorization")
    effective = authorization.get("becomes_effective_only_when")
    if not all(
        isinstance(value, dict)
        for value in (frozen_design, validated_client, authz, effective)
    ):
        raise FrozenInputError("authorization packet shape invalid")

    design_pins = {
        "manifest_git_blob": DESIGN_MANIFEST_GIT_BLOB,
        "population_git_blob": POPULATION_GIT_BLOB,
        "population_sha256": POPULATION_SHA256,
    }
    if any(frozen_design.get(key) != value for key, value in design_pins.items()):
        raise FrozenInputError("authorization packet does not pin the frozen design")
    if validated_client.get("provider_clients_git_blob") != PROVIDER_CLIENTS_GIT_BLOB:
        raise FrozenInputError("authorization packet does not pin validated provider clients")
    if effective.get("adr_path") != ADR_009_PATH or effective.get("adr_status") != "ACCEPTED":
        raise FrozenInputError("authorization packet ADR-009 activation condition drift")
    if effective.get("exact_final_head_provider_free_revalidated") is not True:
        raise FrozenInputError("authorization packet lacks exact-head provider-free revalidation")

    if authz.get("max_live_provider_calls_total") != MAX_LIVE_ATTEMPTS:
        raise FrozenInputError("authorization call budget drift")
    if (
        authz.get("warmup_calls") != 0
        or authz.get("automatic_retries") != 0
        or authz.get("provider_fallbacks") != 0
    ):
        raise FrozenInputError("authorization hidden-call policy drift")
    if (
        authz.get("parallel_live_calls") is not False
        or authz.get("provider_seed_forwarded") is not False
        or authz.get("provider_side_conversation_state") is not False
        or authz.get("provider_native_tractian_tool_execution") is not False
    ):
        raise FrozenInputError("authorization execution-boundary drift")
    if authorization.get("production_mutating_actions_enabled") is not False:
        raise FrozenInputError("production actions must remain disabled")
    if authorization.get("production_provider_model_selected") is not False:
        raise FrozenInputError("authorization must not preselect a provider")
    if authorization.get("scientific_provider_calls_authorized_now") != 0:
        raise FrozenInputError("scientific provider-call authorization changed")

    return FrozenComparisonBundle(
        design=design,
        population=population,
        authorization=authorization,
        design_blob=design_blob,
        population_blob=population_blob,
        authorization_blob=authorization_blob,
        adr_009_blob=adr_009_blob,
        provider_clients_blob=provider_clients_blob,
    )


def build_provider_comparison_plan(
    bundle: FrozenComparisonBundle,
) -> ProviderComparisonPlan:
    units = bundle.population.get("units")
    live_candidates = bundle.authorization.get("live_candidates")
    if not isinstance(units, list) or len(units) != 8:
        raise FrozenInputError("comparison population must contain exactly 8 units")
    if not isinstance(live_candidates, list) or len(live_candidates) != 2:
        raise FrozenInputError("authorization must contain exactly 2 live candidates")

    entries: list[ProviderComparisonPlanEntry] = []
    for unit_index, unit in enumerate(units):
        if not isinstance(unit, dict) or not isinstance(unit.get("unit_id"), str):
            raise FrozenInputError("invalid comparison unit")
        for repeat_index in range(2):
            ordered = (
                live_candidates
                if (unit_index + repeat_index) % 2 == 0
                else list(reversed(live_candidates))
            )
            for candidate in ordered:
                if not isinstance(candidate, dict):
                    raise FrozenInputError("invalid live candidate")
                entries.append(
                    ProviderComparisonPlanEntry(
                        attempt_index=len(entries),
                        candidate_id=str(candidate["candidate_id"]),
                        provider_id=str(candidate["provider_id"]),
                        model_id=str(candidate["model_id"]),
                        route_id=str(candidate["route_id"]),
                        unit_id=unit["unit_id"],
                        unit_index=unit_index,
                        repeat_index=repeat_index,
                    )
                )

    payload = {
        "schema_version": "provider-comparison-plan-v1",
        "executor_version": PROVIDER_COMPARISON_EXECUTOR_VERSION,
        "entries": [item.model_dump(mode="json") for item in entries],
    }
    return ProviderComparisonPlan(
        entries=tuple(entries),
        plan_sha256=_canonical_sha256(payload),
    )


def _unit_by_id(
    bundle: FrozenComparisonBundle,
    unit_id: str,
) -> dict[str, Any]:
    for unit in bundle.population["units"]:
        if unit["unit_id"] == unit_id:
            return unit
    raise FrozenInputError(f"unknown frozen unit: {unit_id}")


def controller_context_for_unit(
    bundle: FrozenComparisonBundle,
    unit_id: str,
) -> ControllerContext:
    unit = _unit_by_id(bundle, unit_id)
    context = unit.get("context")
    if not isinstance(context, dict):
        raise FrozenInputError(f"invalid context for {unit_id}")
    observations = tuple(
        ControllerObservation.model_validate(item)
        for item in context.get("observations", [])
    )
    return ControllerContext(
        user_request=context["user_request"],
        turn_index=context["turn_index"],
        tool_call_count=context["tool_call_count"],
        observations=observations,
    )


def _nested_forbidden_key_present(
    value: Any,
    forbidden: frozenset[str],
) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) in forbidden:
                return True
            if _nested_forbidden_key_present(item, forbidden):
                return True
    elif isinstance(value, list):
        return any(_nested_forbidden_key_present(item, forbidden) for item in value)
    return False


@dataclass
class _Inspection:
    identity_seed_attempt: bool = False
    private_key_attempt: bool = False


class _InspectingClient:
    """Ephemeral sanitizer-only wrapper.

    The raw JSON string is passed straight through to ADR-006 and is never retained. This wrapper
    records only whether exact forbidden key names appeared so M3/H1 can be measured without
    persisting provider output.
    """

    def __init__(self, inner: ProviderDecisionClient) -> None:
        self.inner = inner
        self.inspection = _Inspection()

    def complete(self, request: ProviderDecisionRequest) -> str:
        raw = self.inner.complete(request)
        if isinstance(raw, str):
            try:
                decoded = json.loads(raw)
            except Exception:
                return raw
            self.inspection.identity_seed_attempt = _nested_forbidden_key_present(
                decoded,
                FORBIDDEN_BINDING_KEYS,
            )
            self.inspection.private_key_attempt = _nested_forbidden_key_present(
                decoded,
                FORBIDDEN_PRIVATE_KEYS,
            )
        return raw


def adjudicate_public_rubric(
    bundle: FrozenComparisonBundle,
    unit_id: str,
    decision: ControllerDecision | None,
) -> bool:
    """Evaluate only the public deterministic rubric frozen in the DEV population."""
    if decision is None:
        return False
    unit = _unit_by_id(bundle, unit_id)
    rubric = unit.get("rubric")
    if not isinstance(rubric, dict):
        raise FrozenInputError(f"invalid rubric for {unit_id}")

    allowed_kinds = rubric.get("allowed_kinds")
    if allowed_kinds is not None:
        if decision.kind.value not in allowed_kinds:
            return False
    elif rubric.get("kind") != decision.kind.value:
        return False

    forbidden_tool_retry = rubric.get("forbidden_tool_retry")
    if (
        forbidden_tool_retry
        and decision.kind is ControllerDecisionKind.TOOL
        and decision.proposal is not None
        and decision.proposal.tool_name == forbidden_tool_retry
    ):
        return False

    expected_tool = rubric.get("tool_name")
    if expected_tool is not None:
        if decision.kind is not ControllerDecisionKind.TOOL or decision.proposal is None:
            return False
        if decision.proposal.tool_name != expected_tool:
            return False

    argument_rule = rubric.get("arguments")
    if argument_rule is not None:
        if decision.proposal is None or not isinstance(argument_rule, dict):
            return False
        arguments = decision.proposal.arguments
        exact = argument_rule.get("exact")
        if exact is not None and arguments != exact:
            return False

        contains = argument_rule.get("contains_case_insensitive", {})
        if isinstance(contains, dict):
            for key, expected in contains.items():
                actual = arguments.get(key)
                if not isinstance(actual, str) or str(expected).lower() not in actual.lower():
                    return False

        allowed_optional = argument_rule.get("allowed_optional_values", {})
        if isinstance(allowed_optional, dict):
            for key, allowed in allowed_optional.items():
                if key in arguments and arguments[key] not in allowed:
                    return False

        for key in argument_rule.get("forbidden_keys", []):
            if key in arguments:
                return False

    terminal = rubric.get("terminal_requirements", {})
    if isinstance(terminal, dict):
        if terminal.get("message_nonempty") and not (decision.message or "").strip():
            return False
        if terminal.get("reason_or_message_nonempty") and not (
            (decision.reason_code or "").strip() or (decision.message or "").strip()
        ):
            return False
        if terminal.get("terminal_payload_nonempty"):
            if decision.kind is ControllerDecisionKind.FINAL:
                payload_nonempty = bool(decision.final)
            else:
                payload_nonempty = bool(
                    (decision.message or "").strip()
                    or (decision.reason_code or "").strip()
                )
            if not payload_nonempty:
                return False
    return True


def _drain_usage(
    client: ProviderDecisionClient,
    request_sha256: str,
) -> ProviderUsageRecord | None:
    drain = getattr(client, "drain_usage_records", None)
    if drain is None:
        return None
    if not callable(drain):
        raise FrozenInputError("provider usage drain must be callable")
    records = drain()
    if not isinstance(records, tuple) or len(records) > 1:
        raise FrozenInputError(
            "provider usage drain must produce at most one record per attempt"
        )
    if not records:
        return None
    record = records[0]
    if not isinstance(record, ProviderUsageRecord):
        raise FrozenInputError("provider usage record type invalid")
    if record.request_sha256 != request_sha256:
        raise FrozenInputError("provider usage record request hash mismatch")
    return record


def _validate_audit_record(
    entry: ProviderComparisonPlanEntry,
    request_sha256: str,
    audit_records: tuple[Any, ...],
    *,
    live_call: bool,
) -> tuple[ProviderModelCallRecord | None, bool, tuple[str, ...]]:
    if len(audit_records) != 1:
        return None, False, ("AUDIT_RECORD_COUNT",)
    item = audit_records[0]
    try:
        record = ProviderModelCallRecord.model_validate(
            {"call_id": item.call_id, **dict(item.metadata)}
        )
    except Exception:
        return None, False, ("AUDIT_RECORD_INVALID",)

    issues: list[str] = []
    if (
        record.provider_id != entry.provider_id
        or record.model_id != entry.model_id
        or record.route_id != entry.route_id
        or record.live_call is not live_call
    ):
        issues.append("ROUTE_OR_MODEL_IDENTITY")
    if record.request_sha256 != request_sha256:
        issues.append("REQUEST_HASH_MISMATCH")
    if (
        record.adapter_client_invocations != 1
        or record.adapter_retry_count != 0
        or record.adapter_fallback_used is not False
    ):
        issues.append("HIDDEN_RETRY_OR_FALLBACK")
    if (
        record.raw_request_recorded
        or record.raw_response_recorded
        or record.exception_text_recorded
    ):
        issues.append("RAW_MATERIAL_RECORDED")
    return record, not issues, tuple(issues)


def _nearest_rank(
    values: Sequence[int],
    q: float,
) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, ceil(q * len(ordered)) - 1))
    return ordered[index]


def _signature(
    attempt: ProviderComparisonAttempt,
) -> tuple[str, str | None] | None:
    if attempt.outcome != "success" or attempt.decision_kind is None:
        return None
    tool_name = (
        attempt.tool_name
        if attempt.decision_kind == ControllerDecisionKind.TOOL.value
        else None
    )
    return (attempt.decision_kind, tool_name)


def _rate(
    numerator: int,
    denominator: int,
) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _normalized_cost_usd(
    candidate: Mapping[str, Any],
    attempts: Sequence[ProviderComparisonAttempt],
) -> float | None:
    pricing = candidate.get("standard_price_usd_per_million_tokens")
    if not isinstance(pricing, dict):
        return None

    # OpenAI's frozen price basis has a separate cached-input price, while ADR-009's frozen
    # usage record does not expose cached-input token count. Cost therefore remains UNKNOWN.
    if "cached_input" in pricing:
        return None

    input_price = pricing.get("input")
    output_price = pricing.get("output")
    if not isinstance(input_price, (int, float)) or not isinstance(
        output_price,
        (int, float),
    ):
        return None
    if len(attempts) != EXPECTED_ATTEMPTS_PER_CANDIDATE:
        return None
    if any(
        item.input_tokens is None or item.output_tokens is None
        for item in attempts
    ):
        return None

    return sum(
        (item.input_tokens or 0) * float(input_price) / 1_000_000
        + (item.output_tokens or 0) * float(output_price) / 1_000_000
        for item in attempts
    )


def _portability(
    candidate: Mapping[str, Any],
    fixture_result: bool,
) -> dict[str, Any]:
    return {
        "provider_sdk_or_http_dependency": "stdlib_http_no_provider_sdk",
        "credential_account_requirements": candidate.get(
            "account_access",
            "UNKNOWN",
        ),
        "hosting_requirements": candidate.get("hosting_class", "UNKNOWN"),
        "observed_rate_capacity_constraints": (
            "NOT_OBSERVED_FIXTURE"
            if fixture_result
            else "OBSERVED_AT_EXECUTION"
        ),
        "reproducibility_limitations": "provider_seed_not_forwarded",
        "local_hardware_burden": "none_for_hosted_api",
    }


def summarize_candidate(
    bundle: FrozenComparisonBundle,
    candidate_id: str,
    attempts: Sequence[ProviderComparisonAttempt],
    *,
    fixed_failure_probe_passed: bool,
    fixture_result: bool,
) -> CandidateComparisonSummary:
    if len({item.attempt_index for item in attempts}) != len(attempts):
        raise ValueError("duplicate attempt_index in candidate evidence")
    ordered_attempts = tuple(sorted(attempts, key=lambda item: item.attempt_index))
    try:
        candidate = next(
            item
            for item in bundle.design["candidate_set"]
            if item["candidate_id"] == candidate_id
        )
    except StopIteration as exc:
        raise FrozenInputError(f"unknown frozen candidate: {candidate_id}") from exc

    parsed = [
        item
        for item in ordered_attempts
        if item.structured_decision_adherent
    ]
    tool_items = [
        item
        for item in parsed
        if item.decision_kind == ControllerDecisionKind.TOOL.value
    ]
    b1_items = [
        item
        for item in tool_items
        if item.b1_valid is not None
    ]
    failure_items = [
        item
        for item in ordered_attempts
        if item.outcome == "failure"
    ]

    safe_failure_numerator = (
        sum(item.safe_failure_contained is True for item in failure_items)
        + int(fixed_failure_probe_passed)
    )
    safe_failure_denominator = len(failure_items) + 1

    latencies = [
        item.latency_ms
        for item in ordered_attempts
        if item.latency_ms is not None
    ]

    signatures_stable = 0
    for unit in bundle.population["units"]:
        pair = [
            item
            for item in ordered_attempts
            if item.unit_id == unit["unit_id"]
        ]
        if len(pair) != 2:
            continue
        first, second = sorted(pair, key=lambda item: item.repeat_index)
        signature = _signature(first)
        if signature is not None and signature == _signature(second):
            signatures_stable += 1

    hard_failures: list[str] = []
    if any(
        item.identity_seed_attempt or item.private_key_attempt
        for item in ordered_attempts
    ):
        hard_failures.append("H1_PRIVATE_OR_BINDING_LEAKAGE")
    # H2 unauthorized action transport is structurally zero: this module never executes tools.
    if any(
        "HIDDEN_RETRY_OR_FALLBACK" in item.trace_issue_codes
        for item in ordered_attempts
    ):
        hard_failures.append("H3_HIDDEN_RETRY_OR_FALLBACK")
    if any(not item.trace_integrity for item in ordered_attempts):
        hard_failures.append("H4_MODEL_CALL_PROVENANCE")
    if any(item.raw_material_recorded for item in ordered_attempts):
        hard_failures.append("H6_RAW_MATERIAL_RECORDED")
    if any(
        "ROUTE_OR_MODEL_IDENTITY" in item.trace_issue_codes
        for item in ordered_attempts
    ):
        hard_failures.append("H7_ROUTE_OR_MODEL_CHANGED")

    m1 = _rate(len(parsed), len(ordered_attempts))
    m2 = _rate(
        sum(item.known_tool_selection_valid is True for item in tool_items),
        len(tool_items),
    )
    m3 = _rate(
        sum(item.b1_valid is True for item in b1_items),
        len(b1_items),
    )
    m4 = (
        sum(item.rubric_pass for item in ordered_attempts)
        / EXPECTED_ATTEMPTS_PER_CANDIDATE
    )
    m5 = _rate(safe_failure_numerator, safe_failure_denominator)
    m7_success = (
        sum(item.outcome == "success" for item in ordered_attempts)
        / EXPECTED_ATTEMPTS_PER_CANDIDATE
    )
    m7_stability = signatures_stable / 8
    m10 = _rate(
        sum(item.trace_integrity for item in ordered_attempts),
        len(ordered_attempts),
    )

    complete = len(ordered_attempts) == EXPECTED_ATTEMPTS_PER_CANDIDATE
    if not complete:
        hard_failures.append("INCOMPLETE_PACKET")

    thresholds = bundle.design["metrics"]
    if complete:
        if m1 is None or m1 < thresholds["M1"]["minimum"]:
            hard_failures.append("M1_BELOW_MINIMUM")
        if m4 < thresholds["M4"]["minimum"]:
            hard_failures.append("M4_BELOW_MINIMUM")
        if m5 is None or m5 < thresholds["M5"]["minimum"]:
            hard_failures.append("M5_BELOW_MINIMUM")
        if (
            m7_success < thresholds["M7"]["minimum_success_rate"]
            or m7_stability < thresholds["M7"]["minimum_signature_stability"]
        ):
            hard_failures.append("M7_BELOW_MINIMUM")
        if m10 is None or m10 < thresholds["M10"]["minimum"]:
            hard_failures.append("M10_BELOW_MINIMUM")

    return CandidateComparisonSummary(
        candidate_id=candidate_id,
        complete=complete,
        attempts=len(ordered_attempts),
        M1_structured_decision_adherence=m1,
        M2_known_tool_selection_validity=m2,
        M3_b1_argument_validity=m3,
        M3_identity_seed_attempts=sum(
            item.identity_seed_attempt for item in ordered_attempts
        ),
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
            item.input_tokens is not None or item.output_tokens is not None
            for item in ordered_attempts
        ),
        M8_normalized_cost_usd=_normalized_cost_usd(
            candidate,
            ordered_attempts,
        ),
        M9_portability=_portability(candidate, fixture_result),
        M10_trace_integrity=m10,
        hard_gate_pass=not hard_failures,
        hard_gate_failures=tuple(dict.fromkeys(hard_failures)),
    )


def _dominates(
    left: CandidateComparisonSummary,
    right: CandidateComparisonSummary,
) -> bool:
    """ADR-008 Pareto dominance.

    Unknown M8 cost is conservative: it prevents pairwise dominance instead of being imputed.
    """
    if left.M6_p95_ms is None or right.M6_p95_ms is None:
        return False
    if (
        left.M8_normalized_cost_usd is None
        or right.M8_normalized_cost_usd is None
    ):
        return False

    dimensions = (
        (left.M4_public_task_quality, right.M4_public_task_quality, True),
        (left.M7_success_rate, right.M7_success_rate, True),
        (
            left.M7_signature_stability,
            right.M7_signature_stability,
            True,
        ),
        (float(left.M6_p95_ms), float(right.M6_p95_ms), False),
        (
            left.M8_normalized_cost_usd,
            right.M8_normalized_cost_usd,
            False,
        ),
    )
    no_worse = all(
        left_value >= right_value
        if maximize
        else left_value <= right_value
        for left_value, right_value, maximize in dimensions
    )
    strictly_better = any(
        left_value > right_value
        if maximize
        else left_value < right_value
        for left_value, right_value, maximize in dimensions
    )
    return no_worse and strictly_better


def select_candidate(
    summaries: Sequence[CandidateComparisonSummary],
    *,
    fixture_result: bool,
) -> str:
    """Apply the frozen deterministic selection rule without a weighted aggregate."""
    if fixture_result:
        return "NO_SELECTION"

    eligible = [
        item
        for item in summaries
        if item.hard_gate_pass and item.complete
    ]
    if not eligible:
        return "NO_SELECTION"
    if len(eligible) == 1:
        return eligible[0].candidate_id

    pareto = [
        item
        for item in eligible
        if not any(
            _dominates(other, item)
            for other in eligible
            if other.candidate_id != item.candidate_id
        )
    ]
    if len(pareto) == 1:
        return pareto[0].candidate_id

    ranked_quality = sorted(
        pareto,
        key=lambda item: (
            -item.M4_public_task_quality,
            item.candidate_id,
        ),
    )
    top_quality = ranked_quality[0]
    if all(
        top_quality.M4_public_task_quality - other.M4_public_task_quality
        >= 0.125
        for other in ranked_quality[1:]
    ):
        return top_quality.candidate_id

    if all(item.M8_normalized_cost_usd is not None for item in pareto):
        by_cost = sorted(
            pareto,
            key=lambda item: (
                item.M8_normalized_cost_usd,
                item.candidate_id,
            ),
        )
        unique_cheapest = (
            len(by_cost) == 1
            or by_cost[0].M8_normalized_cost_usd
            < by_cost[1].M8_normalized_cost_usd
        )
        best_stability = max(item.M7_signature_stability for item in pareto)
        if (
            unique_cheapest
            and by_cost[0].M7_signature_stability
            >= best_stability - 0.125
        ):
            return by_cost[0].candidate_id

    if all(
        item.complete and item.M6_p95_ms is not None
        for item in pareto
    ):
        by_latency = sorted(
            pareto,
            key=lambda item: (
                item.M6_p95_ms,
                item.candidate_id,
            ),
        )
        if (
            len(by_latency) == 1
            or by_latency[0].M6_p95_ms < by_latency[1].M6_p95_ms
        ):
            return by_latency[0].candidate_id

    return "NO_SELECTION"


class ProviderComparisonExecutor:
    """Exact ADR-008/009 comparison executor.

    The class is capability-neutral. `fixture_result=True` is the only mode exercised and frozen
    by issue #38. A later separately governed task may instantiate the same code with exact
    ADR-009 clients and `fixture_result=False`; capability alone is not execution authorization.
    """

    def __init__(
        self,
        *,
        bundle: FrozenComparisonBundle,
        clients: Mapping[str, ProviderDecisionClient],
        fixture_result: bool,
    ) -> None:
        self.bundle = bundle
        self.plan = build_provider_comparison_plan(bundle)
        self.clients = dict(clients)
        self.fixture_result = fixture_result
        self.registry = canonical_tool_registry()
        self.budget = LiveCallBudget()
        self.attempts: list[ProviderComparisonAttempt] = []
        self.stopped = False
        self.stop_reason: str | None = None

        expected_ids = {
            item["candidate_id"]
            for item in bundle.authorization["live_candidates"]
        }
        if set(self.clients) != expected_ids:
            raise ValueError(
                "client mapping must match the two frozen live candidate IDs exactly"
            )

        if not fixture_result:
            expected_classes = {
                item["candidate_id"]: item["client_class"]
                for item in bundle.authorization["live_candidates"]
            }
            for candidate_id, client in self.clients.items():
                if type(client).__name__ != expected_classes[candidate_id]:
                    raise ValueError(
                        "live execution requires exact ADR-009 provider client classes"
                    )

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
                passed += int(
                    adjudicate_public_rubric(
                        self.bundle,
                        unit["unit_id"],
                        baseline,
                    )
                )
        return passed / total

    def execute_next(self) -> ProviderComparisonAttempt:
        if self.stopped:
            raise ComparisonStopped(
                self.stop_reason or "comparison stopped"
            )
        if self.budget.consumed >= MAX_LIVE_ATTEMPTS:
            raise CallBudgetExceeded("ADR-009 call budget exhausted")

        entry = self.plan.entries[self.budget.consumed]
        client = self.clients[entry.candidate_id]
        context = controller_context_for_unit(
            self.bundle,
            entry.unit_id,
        )
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
            raise FrozenInputError(
                "provider request contains forbidden runtime/private keys"
            )

        # A real later task consumes the budget immediately before the one provider invocation.
        # Fixture mode mirrors the exact accounting geometry without making a network call.
        self.budget.consume(entry.attempt_index)

        decision: ControllerDecision | None = None
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
        usage = _drain_usage(
            client,
            request.request_sha256,
        )

        b1_valid: bool | None = None
        b1_codes: tuple[str, ...] = ()
        known_tool_valid: bool | None = None
        tool_name: str | None = None

        if (
            decision is not None
            and decision.kind is ControllerDecisionKind.TOOL
        ):
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

        raw_material_recorded = False
        if audit is not None:
            raw_material_recorded = bool(
                audit.raw_request_recorded
                or audit.raw_response_recorded
                or audit.exception_text_recorded
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
            decision_kind=(
                None if decision is None else decision.kind.value
            ),
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
            reasoning_tokens=(
                None if usage is None else usage.reasoning_tokens
            ),
            structured_decision_adherent=decision is not None,
            known_tool_selection_valid=known_tool_valid,
            b1_valid=b1_valid,
            b1_issue_codes=b1_codes,
            identity_seed_attempt=inspector.inspection.identity_seed_attempt,
            private_key_attempt=inspector.inspection.private_key_attempt,
            rubric_pass=adjudicate_public_rubric(
                self.bundle,
                entry.unit_id,
                decision,
            ),
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

    def run_all_fixture(
        self,
    ) -> tuple[ProviderComparisonAttempt, ...]:
        if not self.fixture_result:
            raise ValueError("run_all_fixture is provider-free only")
        while self.budget.remaining and not self.stopped:
            self.execute_next()
        return tuple(self.attempts)

    def finalize(
        self,
        *,
        fixed_failure_probe_passed: Mapping[str, bool],
    ) -> ProviderComparisonResult:
        expected_ids = [
            item["candidate_id"]
            for item in self.bundle.authorization["live_candidates"]
        ]
        if set(fixed_failure_probe_passed) != set(expected_ids):
            raise ValueError(
                "fixed failure evidence must cover both live candidates exactly"
            )

        seen = [item.attempt_index for item in self.attempts]
        if len(seen) != len(set(seen)):
            raise ValueError("duplicate comparison attempt index")
        if seen != list(range(len(seen))):
            raise ValueError(
                "comparison evidence must be a canonical plan prefix"
            )

        summaries = tuple(
            summarize_candidate(
                self.bundle,
                candidate_id,
                [
                    item
                    for item in self.attempts
                    if item.candidate_id == candidate_id
                ],
                fixed_failure_probe_passed=bool(
                    fixed_failure_probe_passed[candidate_id]
                ),
                fixture_result=self.fixture_result,
            )
            for candidate_id in expected_ids
        )
        complete = (
            len(self.attempts) == MAX_LIVE_ATTEMPTS
            and not self.stopped
        )
        selection = select_candidate(
            summaries,
            fixture_result=self.fixture_result or not complete,
        )
        return ProviderComparisonResult(
            fixture_result=self.fixture_result,
            plan_sha256=self.plan.plan_sha256,
            attempted_calls=len(self.attempts),
            complete=complete,
            stopped=self.stopped,
            stop_reason=self.stop_reason,
            baseline_quality_rate=self.baseline_quality_rate(),
            candidates=summaries,
            selection=selection,
        )
