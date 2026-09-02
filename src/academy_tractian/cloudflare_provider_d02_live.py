from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from statistics import median
from typing import Any, Literal, Mapping, Sequence
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import ControllerDecision, ControllerDecisionKind
from research.e2.validation import validate_arguments

from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
)
from .cloudflare_provider_comparison_v2 import (
    GLM_CANDIDATE_ID,
    NEMOTRON_CANDIDATE_ID,
    CloudflareCandidateComparisonSummaryV2,
    CloudflareComparisonStopped,
    FrozenCloudflareComparisonBundleV2,
    load_frozen_cloudflare_comparison_bundle_v2,
    select_cloudflare_candidate_v2,
)
from .cloudflare_provider_d02 import (
    CLOUDFLARE_D02_ATTEMPTS_PER_CANDIDATE,
    CLOUDFLARE_D02_EXPECTED_PLAN_SHA256,
    CLOUDFLARE_D02_MAX_COMPLETION_TOKENS,
    CLOUDFLARE_D02_MAX_INPUT_TOKENS,
    CLOUDFLARE_D02_MAX_PACKET_NEURONS,
    CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1,
    CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS,
    CloudflareD02ComparisonPlan,
    CloudflareD02PreLiveEvidence,
    CloudflareProviderDecisionSourceD02,
    CloudflareWorkersAIChatCompletionsDecisionClientD02,
    build_cloudflare_d02_plan,
    observed_neurons_d02,
    worst_case_neurons_per_attempt_d02,
)
from .cloudflare_provider_live_v2 import CloudflareLiveSecrets
from .cloudflare_provider_provenance_v2 import (
    CloudflareProviderCallIdentityV2,
    CloudflareProviderDecisionSourceV2,
    validate_cloudflare_audit_record_v2,
)
from .provider_clients import (
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
    ProviderJsonTransport,
    UrllibProviderJsonTransport,
)
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
    adjudicate_public_rubric,
    controller_context_for_unit,
)
from .runtime import canonical_tool_registry


CLOUDFLARE_D02_LIVE_EXECUTION_VERSION = "cloudflare-d02-live-execution-v1"
CLOUDFLARE_D02_LIVE_TASK_VERSION = "cloudflare-d02-live-task-v1"
CLOUDFLARE_D02_LIVE_LEDGER_VERSION = "cloudflare-d02-live-attempt-ledger-v1"
CLOUDFLARE_D02_LIVE_RESULT_VERSION = "cloudflare-d02-governed-live-result-v1"
CLOUDFLARE_D02_PROVIDER_RESULT_VERSION = "cloudflare-d02-provider-result-v1"
CLOUDFLARE_D02_CUSTODY_VERSION = "cloudflare-d02-live-authorization-custody-v1"

D02_PROTOCOL_BLOB = "eda022821c4ffe08b28b80b814d0da28f84580f6"
ADR_026_BLOB = "c5d00a1668613cacd3b520cd241a8b969a262119"
D02_CONTRACT_BLOB = "c6cc416c4201a30961861c852aaa746e6c5c9113"

D02_CUSTODY_FILENAME = "cloudflare-d02-live-authorization-custody-v1.json"
D02_RUN_DIRNAME = "run"
D02_LEDGER_FILENAME = "attempt-ledger-d02-v1.json"
D02_RESULT_FILENAME = "result-d02-v1.json"
D02_CANDIDATE_IDS = (GLM_CANDIDATE_ID, NEMOTRON_CANDIDATE_ID)


class CloudflareD02LiveExecutionError(RuntimeError):
    pass


class CloudflareD02ExistingRunError(CloudflareD02LiveExecutionError):
    pass


class CloudflareD02LiveExecutionInvariantError(CloudflareD02LiveExecutionError):
    pass


class CloudflareD02LiveExecutionStopped(CloudflareD02LiveExecutionError):
    pass


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflareD02LiveAttemptV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-live-attempt-v1"] = "cloudflare-d02-live-attempt-v1"
    fixture_result: bool
    attempt_index: int = Field(ge=0, lt=32)
    candidate_id: str
    unit_id: str
    repeat_index: int = Field(ge=0, lt=2)
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    call_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    outcome: Literal["success", "failure"]
    decision_kind: str | None = None
    tool_name: str | None = None
    failure_code: str | None = None
    failure_subtype: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]{0,95}$")
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
    raw_material_recorded: Literal[False] = False

    @model_validator(mode="after")
    def validate_diagnostic(self) -> "CloudflareD02LiveAttemptV1":
        if self.outcome == "success":
            if self.failure_code is not None or self.failure_subtype is not None:
                raise ValueError("successful D02 attempt cannot contain failure diagnostics")
        elif self.failure_code == "CLIENT_FAILURE" and not self.failure_subtype:
            raise ValueError("D02 CLIENT_FAILURE requires sanitized failure_subtype")
        elif self.failure_code != "CLIENT_FAILURE" and self.failure_subtype is not None:
            raise ValueError("failure_subtype is only valid for CLIENT_FAILURE")
        return self

    def as_provider_attempt(self) -> ProviderComparisonAttempt:
        return ProviderComparisonAttempt(
            **self.model_dump(mode="python", exclude={"schema_version", "failure_subtype"})
        )


AttemptState = Literal["pending", "claimed", "completed", "uncertain"]
RunState = Literal["prepared", "running", "stopped", "complete"]


class CloudflareD02LiveLedgerEntryV1(_FrozenModel):
    attempt_index: int = Field(ge=0, lt=32)
    candidate_id: str
    unit_id: str
    repeat_index: int = Field(ge=0, lt=2)
    state: AttemptState = "pending"
    attempt: CloudflareD02LiveAttemptV1 | None = None
    stop_code: str | None = None

    @model_validator(mode="after")
    def validate_state_payload(self) -> "CloudflareD02LiveLedgerEntryV1":
        if self.state == "completed" and self.attempt is None:
            raise ValueError("completed D02 ledger entry requires attempt evidence")
        if self.state != "completed" and self.attempt is not None:
            raise ValueError("only completed D02 entries may contain attempt evidence")
        if self.state == "uncertain" and not self.stop_code:
            raise ValueError("uncertain D02 entry requires stop_code")
        return self


class CloudflareD02LiveRunLedgerV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-live-attempt-ledger-v1"] = CLOUDFLARE_D02_LIVE_LEDGER_VERSION
    wrapper_version: Literal["cloudflare-d02-live-execution-v1"] = CLOUDFLARE_D02_LIVE_EXECUTION_VERSION
    plan_sha256: Literal["e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"] = CLOUDFLARE_D02_EXPECTED_PLAN_SHA256
    d02_protocol_blob: Literal["eda022821c4ffe08b28b80b814d0da28f84580f6"] = D02_PROTOCOL_BLOB
    adr_026_blob: Literal["c5d00a1668613cacd3b520cd241a8b969a262119"] = ADR_026_BLOB
    d02_contract_blob: Literal["c6cc416c4201a30961861c852aaa746e6c5c9113"] = D02_CONTRACT_BLOB
    pre_live_evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    available_free_neurons_at_start: float = Field(ge=CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1, le=CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS)
    state: RunState = "prepared"
    stop_code: str | None = None
    entries: tuple[CloudflareD02LiveLedgerEntryV1, ...]

    @model_validator(mode="after")
    def validate_geometry(self) -> "CloudflareD02LiveRunLedgerV1":
        if len(self.entries) != 32 or tuple(item.attempt_index for item in self.entries) != tuple(range(32)):
            raise ValueError("D02 live ledger must contain canonical indexes 0..31")
        if self.state == "complete" and any(item.state != "completed" for item in self.entries):
            raise ValueError("complete D02 ledger requires all attempts completed")
        if self.state == "stopped" and not self.stop_code:
            raise ValueError("stopped D02 ledger requires stop_code")
        return self


class CloudflareD02AuthorizationCustodyRecordV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-live-authorization-custody-v1"] = CLOUDFLARE_D02_CUSTODY_VERSION
    task_version: Literal["cloudflare-d02-live-task-v1"] = CLOUDFLARE_D02_LIVE_TASK_VERSION
    wrapper_version: Literal["cloudflare-d02-live-execution-v1"] = CLOUDFLARE_D02_LIVE_EXECUTION_VERSION
    plan_sha256: Literal["e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"] = CLOUDFLARE_D02_EXPECTED_PLAN_SHA256
    d02_protocol_blob: Literal["eda022821c4ffe08b28b80b814d0da28f84580f6"] = D02_PROTOCOL_BLOB
    adr_026_blob: Literal["c5d00a1668613cacd3b520cd241a8b969a262119"] = ADR_026_BLOB
    d02_contract_blob: Literal["c6cc416c4201a30961861c852aaa746e6c5c9113"] = D02_CONTRACT_BLOB
    pre_live_evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    available_free_neurons_at_reservation: float = Field(ge=CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1, le=CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS)
    max_packet_neurons: Literal[9352.805376] = 9352.805376
    completion_token_cap: Literal[1024] = 1024
    canonical_run_dirname: Literal["run"] = D02_RUN_DIRNAME
    state: Literal["reserved"] = "reserved"
    live_calls_consumed_at_reservation: Literal[0] = 0
    credentials_recorded: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False
    workers_paid_enabled: Literal[False] = False
    prepaid_ai_gateway_enabled: Literal[False] = False
    workers_free_required: Literal[True] = True


class CloudflareD02ProviderResultV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-provider-result-v1"] = CLOUDFLARE_D02_PROVIDER_RESULT_VERSION
    plan_sha256: Literal["e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"] = CLOUDFLARE_D02_EXPECTED_PLAN_SHA256
    fixture_result: bool
    attempted_calls: int = Field(ge=0, le=32)
    complete: bool
    stopped: bool
    stop_reason: str | None
    baseline_quality_rate: float
    available_free_neurons_at_start: float
    packet_observed_neurons: float
    resource_accounting_complete: bool
    actual_cash_cost_usd: Literal[0.0] = 0.0
    completion_token_cap: Literal[1024] = 1024
    candidates: tuple[CloudflareCandidateComparisonSummaryV2, ...]
    selection: str
    production_selection_claim: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False


class CloudflareD02GovernedExecutionResultV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-governed-live-result-v1"] = CLOUDFLARE_D02_LIVE_RESULT_VERSION
    wrapper_version: Literal["cloudflare-d02-live-execution-v1"] = CLOUDFLARE_D02_LIVE_EXECUTION_VERSION
    plan_sha256: Literal["e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"] = CLOUDFLARE_D02_EXPECTED_PLAN_SHA256
    state: Literal["complete", "stopped"]
    completed_attempts: int = Field(ge=0, le=32)
    consumed_or_uncertain_attempts: int = Field(ge=0, le=32)
    stop_code: str | None = None
    selection: str
    provider_result: CloudflareD02ProviderResultV1 | None = None
    production_selection_claim: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False
    actual_cash_cost_usd: Literal[0.0] = 0.0


def build_cloudflare_d02_live_clients(*, secrets: CloudflareLiveSecrets, transport: ProviderJsonTransport) -> dict[str, CloudflareWorkersAIChatCompletionsDecisionClientD02]:
    secrets.validate_presence()
    return {
        GLM_CANDIDATE_ID: CloudflareWorkersAIChatCompletionsDecisionClientD02(api_token=secrets.api_token, account_id=secrets.account_id, model_id=CLOUDFLARE_GLM_MODEL_ID, transport=transport),
        NEMOTRON_CANDIDATE_ID: CloudflareWorkersAIChatCompletionsDecisionClientD02(api_token=secrets.api_token, account_id=secrets.account_id, model_id=CLOUDFLARE_NEMOTRON_MODEL_ID, transport=transport),
    }


def build_cloudflare_d02_one_shot_transport() -> UrllibProviderJsonTransport:
    return UrllibProviderJsonTransport()


class _InjectedFailureTransport(ProviderJsonTransport):
    def __init__(self) -> None:
        self.calls = 0

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls += 1
        raise ProviderHttpClientError("INJECTED_PROVIDER_FREE_FAILURE")


def _fixed_failure_probe_d02(*, model_id: str, repo_root: Path | str) -> bool:
    transport = _InjectedFailureTransport()
    client = CloudflareWorkersAIChatCompletionsDecisionClientD02(api_token="provider-free-d02-token", account_id="0123456789abcdef0123456789abcdef", model_id=model_id, transport=transport)
    bundle = load_frozen_cloudflare_comparison_bundle_v2(repo_root)
    context = controller_context_for_unit(bundle, bundle.population["units"][0]["unit_id"])
    source = CloudflareProviderDecisionSourceD02(client=client, registry=canonical_tool_registry(), call_identity=CloudflareProviderCallIdentityV2(model_id=model_id, live_call=False))
    try:
        source.decide(context)
    except ProviderHttpClientError:
        pass
    except Exception:
        return False
    else:
        return False
    audits = source.drain_audit_records()
    diagnostics = source.drain_failure_diagnostics()
    return bool(
        transport.calls == 1
        and len(audits) == 1
        and len(diagnostics) == 1
        and audits[0].metadata.get("failure_code") == "CLIENT_FAILURE"
        and diagnostics[0].failure_subtype == "INJECTED_PROVIDER_FREE_FAILURE"
        and diagnostics[0].raw_request_recorded is False
        and diagnostics[0].raw_response_recorded is False
        and diagnostics[0].exception_text_recorded is False
    )


def run_cloudflare_d02_provider_free_fixed_failure_probes(repo_root: Path | str) -> dict[str, bool]:
    return {
        GLM_CANDIDATE_ID: _fixed_failure_probe_d02(model_id=CLOUDFLARE_GLM_MODEL_ID, repo_root=repo_root),
        NEMOTRON_CANDIDATE_ID: _fixed_failure_probe_d02(model_id=CLOUDFLARE_NEMOTRON_MODEL_ID, repo_root=repo_root),
    }


def _portability(candidate_id: str, fixture: bool, available: float) -> dict[str, Any]:
    return {
        "direct_workers_ai_http_dependency": True,
        "credential_account_requirements": "explicit_api_token_and_account_id",
        "Workers_Free_requirement": True,
        "observed_rate_capacity_constraints": "NOT_OBSERVED_FIXTURE" if fixture else "OBSERVED_AT_EXECUTION",
        "reproducibility_limitations": "provider_seed_not_forwarded",
        "free_neuron_headroom_at_start": available,
        "candidate_id": candidate_id,
        "completion_token_cap": 1024,
    }


def summarize_cloudflare_candidate_d02(bundle: FrozenCloudflareComparisonBundleV2, candidate_id: str, attempts: Sequence[CloudflareD02LiveAttemptV1], *, fixed_failure_probe_passed: bool, fixture_result: bool, zero_cash_cost_route_proven: bool, available_free_neurons: float) -> CloudflareCandidateComparisonSummaryV2:
    ordered = tuple(sorted(attempts, key=lambda item: item.attempt_index))
    if len({item.attempt_index for item in ordered}) != len(ordered):
        raise ValueError("duplicate D02 attempt_index in candidate evidence")
    provider_attempts = tuple(item.as_provider_attempt() for item in ordered)
    parsed = [item for item in provider_attempts if item.structured_decision_adherent]
    tools = [item for item in parsed if item.decision_kind == ControllerDecisionKind.TOOL.value]
    b1_items = [item for item in tools if item.b1_valid is not None]
    failures = [item for item in provider_attempts if item.outcome == "failure"]
    latencies = [item.latency_ms for item in provider_attempts if item.latency_ms is not None]
    stable = 0
    for unit in bundle.population["units"]:
        pair = [item for item in provider_attempts if item.unit_id == unit["unit_id"]]
        if len(pair) == 2:
            first, second = sorted(pair, key=lambda item: item.repeat_index)
            sig = _signature(first)
            stable += int(sig is not None and sig == _signature(second))
    complete = len(ordered) == CLOUDFLARE_D02_ATTEMPTS_PER_CANDIDATE
    usage_complete = complete and all(item.input_tokens is not None and item.output_tokens is not None for item in ordered)
    total_neurons = None
    if usage_complete:
        total_neurons = sum(observed_neurons_d02(candidate_id, input_tokens=int(item.input_tokens), output_tokens=int(item.output_tokens)) for item in ordered)
    m1 = _rate(len(parsed), len(ordered))
    m2 = _rate(sum(item.known_tool_selection_valid is True for item in tools), len(tools))
    m3 = _rate(sum(item.b1_valid is True for item in b1_items), len(b1_items))
    m4 = sum(item.rubric_pass for item in provider_attempts) / 16
    m5 = _rate(sum(item.safe_failure_contained is True for item in failures) + int(fixed_failure_probe_passed), len(failures) + 1)
    m7_success = sum(item.outcome == "success" for item in provider_attempts) / 16
    m7_stability = stable / 8
    m10 = _rate(sum(item.trace_integrity for item in provider_attempts), len(provider_attempts))
    hard: list[str] = []
    if any(item.identity_seed_attempt or item.private_key_attempt for item in provider_attempts): hard.append("H1_PRIVATE_OR_BINDING_LEAKAGE")
    if any("HIDDEN_RETRY_OR_FALLBACK" in item.trace_issue_codes for item in provider_attempts): hard.append("H3_HIDDEN_RETRY_OR_FALLBACK")
    if any(not item.trace_integrity for item in provider_attempts): hard.append("H4_MODEL_CALL_PROVENANCE")
    if any(item.raw_material_recorded for item in provider_attempts): hard.append("H6_RAW_MATERIAL_RECORDED")
    if any("ROUTE_OR_MODEL_IDENTITY" in item.trace_issue_codes for item in provider_attempts): hard.append("H7_ROUTE_OR_MODEL_CHANGED")
    if not zero_cash_cost_route_proven: hard.append("H8_NONFREE_OR_PAID_ROUTE")
    if not usage_complete: hard.append("H9_RESOURCE_ACCOUNTING_INCOMPLETE")
    if any((item.input_tokens is not None and item.input_tokens > CLOUDFLARE_D02_MAX_INPUT_TOKENS) or (item.output_tokens is not None and item.output_tokens > CLOUDFLARE_D02_MAX_COMPLETION_TOKENS) for item in ordered): hard.append("H10_PER_ATTEMPT_RESOURCE_CEILING")
    if total_neurons is not None and total_neurons > CLOUDFLARE_D02_MAX_PACKET_NEURONS + 1e-9: hard.append("H10_PACKET_RESOURCE_CEILING")
    if not complete: hard.append("INCOMPLETE_PACKET")
    metrics = bundle.design["metrics"]
    if complete:
        if m1 is None or m1 < metrics["M1"]["minimum"]: hard.append("M1_BELOW_MINIMUM")
        if m4 < metrics["M4"]["minimum"]: hard.append("M4_BELOW_MINIMUM")
        if m5 is None or m5 < metrics["M5"]["minimum"]: hard.append("M5_BELOW_MINIMUM")
        if m7_success < metrics["M7"]["minimum_success_rate"] or m7_stability < metrics["M7"]["minimum_signature_stability"]: hard.append("M7_BELOW_MINIMUM")
        if m10 is None or m10 < metrics["M10"]["minimum"]: hard.append("M10_BELOW_MINIMUM")
    return CloudflareCandidateComparisonSummaryV2(
        candidate_id=candidate_id, complete=complete, attempts=len(ordered), M1_structured_decision_adherence=m1,
        M2_known_tool_selection_validity=m2, M3_b1_argument_validity=m3,
        M3_identity_seed_attempts=sum(item.identity_seed_attempt for item in provider_attempts), M4_public_task_quality=m4,
        M5_safe_failure_behavior=m5, M6_latency_count=len(latencies), M6_median_ms=None if not latencies else float(median(latencies)),
        M6_p90_ms=_nearest_rank(latencies, 0.90), M6_p95_ms=_nearest_rank(latencies, 0.95), M6_max_ms=None if not latencies else max(latencies),
        M7_success_rate=m7_success, M7_signature_stability=m7_stability,
        M8_usage_records=sum(item.input_tokens is not None and item.output_tokens is not None for item in ordered),
        M8_usage_complete=usage_complete, M8_total_observed_neurons=total_neurons,
        M8_actual_cash_cost_usd=0.0 if zero_cash_cost_route_proven else None,
        M9_portability=_portability(candidate_id, fixture_result, available_free_neurons), M10_trace_integrity=m10,
        hard_gate_pass=not hard, hard_gate_failures=tuple(dict.fromkeys(hard)),
    )


@dataclass
class CloudflareD02ComparisonExecutorV1:
    bundle: FrozenCloudflareComparisonBundleV2
    plan: CloudflareD02ComparisonPlan
    clients: Mapping[str, CloudflareWorkersAIChatCompletionsDecisionClientD02]
    fixture_result: bool
    available_free_neurons: float
    zero_cash_cost_route_proven: bool

    def __post_init__(self) -> None:
        if not (CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1 <= self.available_free_neurons <= CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS):
            raise ValueError("D02 free-neuron start gate failed")
        if not self.zero_cash_cost_route_proven: raise ValueError("D02 requires a prevalidated zero-cash Workers Free route")
        if self.plan.plan_sha256 != CLOUDFLARE_D02_EXPECTED_PLAN_SHA256: raise ValueError("D02 plan identity mismatch")
        if set(self.clients) != set(D02_CANDIDATE_IDS): raise ValueError("D02 client mapping must contain exactly the two frozen candidates")
        expected = {GLM_CANDIDATE_ID: CLOUDFLARE_GLM_MODEL_ID, NEMOTRON_CANDIDATE_ID: CLOUDFLARE_NEMOTRON_MODEL_ID}
        for candidate_id, client in self.clients.items():
            if type(client) is not CloudflareWorkersAIChatCompletionsDecisionClientD02: raise ValueError("D02 live executor requires exact D02 client class")
            if client.model_id != expected[candidate_id]: raise ValueError("D02 live client model identity mismatch")
        self.registry = canonical_tool_registry()
        self.budget = LiveCallBudget()
        self.attempts: list[CloudflareD02LiveAttemptV1] = []
        self.stopped = False
        self.stop_reason: str | None = None
        self.packet_observed_neurons = 0.0

    def baseline_quality_rate(self) -> float:
        baseline = ControllerDecision(kind=ControllerDecisionKind.ABSTAIN, reason_code="BASELINE_NO_PROVIDER", message="Provider-free baseline does not make a provider decision.")
        values = [adjudicate_public_rubric(self.bundle, unit["unit_id"], baseline) for unit in self.bundle.population["units"] for _ in range(2)]
        return sum(values) / len(values)

    def _remaining_worst_case(self) -> float:
        return sum(worst_case_neurons_per_attempt_d02(item.candidate_id) for item in self.plan.entries[self.budget.consumed:])

    def assert_next_attempt_allowed(self) -> None:
        if self.stopped: raise CloudflareComparisonStopped(self.stop_reason or "D02 comparison stopped")
        if not self.budget.remaining: return
        if self.packet_observed_neurons + self._remaining_worst_case() > self.available_free_neurons + 1e-9:
            self.stopped = True
            self.stop_reason = "H10_PROJECTED_FREE_ALLOCATION_EXCEEDED"
            raise CloudflareComparisonStopped(self.stop_reason)

    def execute_next(self) -> CloudflareD02LiveAttemptV1:
        self.assert_next_attempt_allowed()
        entry = self.plan.entries[self.budget.consumed]
        client = self.clients[entry.candidate_id]
        context = controller_context_for_unit(self.bundle, entry.unit_id)
        inspector = _InspectingClient(client)
        source = CloudflareProviderDecisionSourceV2(client=inspector, registry=self.registry, call_identity=CloudflareProviderCallIdentityV2(provider_id=entry.provider_id, model_id=entry.model_id, route_id=entry.route_id, live_call=not self.fixture_result))
        request = source.build_request(context)
        if _nested_forbidden_key_present(request.model_dump(mode="json"), FORBIDDEN_BINDING_KEYS | FORBIDDEN_PRIVATE_KEYS):
            raise ValueError("D02 provider request contains forbidden runtime/private keys")
        self.budget.consume(entry.attempt_index)
        decision = None
        try: decision = source.decide(context)
        except Exception: pass
        audit, trace_integrity, trace_issue_codes = validate_cloudflare_audit_record_v2(provider_id=entry.provider_id, model_id=entry.model_id, route_id=entry.route_id, request_sha256=request.request_sha256, audit_records=source.drain_audit_records(), live_call=not self.fixture_result)
        usage = _drain_usage(client, request.request_sha256)
        failure_code = None
        failure_subtype = None
        if decision is None:
            failure_code = "DECISION_SOURCE_FAILURE" if audit is None or audit.failure_code is None else audit.failure_code
            if failure_code == "CLIENT_FAILURE": failure_subtype = client.last_failure_subtype or "UNCLASSIFIED_CLIENT_FAILURE"
        b1_valid: bool | None = None
        b1_codes: tuple[str, ...] = ()
        known_tool_valid: bool | None = None
        tool_name: str | None = None
        if decision is not None and decision.kind is ControllerDecisionKind.TOOL:
            assert decision.proposal is not None
            tool_name = decision.proposal.tool_name
            known_tool_valid = tool_name in self.registry
            if known_tool_valid:
                issues = validate_arguments(self.registry[tool_name], decision.proposal.arguments)
                b1_codes = tuple(item.code for item in issues)
                b1_valid = not issues
        raw_material = bool(audit is not None and (audit.raw_request_recorded or audit.raw_response_recorded or audit.exception_text_recorded))
        safe_failure = None
        if decision is None: safe_failure = bool(trace_integrity and not inspector.inspection.identity_seed_attempt and not inspector.inspection.private_key_attempt and not raw_material)
        attempt = CloudflareD02LiveAttemptV1(
            fixture_result=self.fixture_result, attempt_index=entry.attempt_index, candidate_id=entry.candidate_id, unit_id=entry.unit_id,
            repeat_index=entry.repeat_index, request_sha256=request.request_sha256, call_id=None if audit is None else audit.call_id,
            outcome="success" if decision is not None else "failure", decision_kind=None if decision is None else decision.kind.value,
            tool_name=tool_name, failure_code=failure_code, failure_subtype=failure_subtype, latency_ms=None if audit is None else audit.latency_ms,
            input_tokens=None if usage is None else usage.input_tokens, output_tokens=None if usage is None else usage.output_tokens,
            total_tokens=None if usage is None else usage.total_tokens, reasoning_tokens=None if usage is None else usage.reasoning_tokens,
            structured_decision_adherent=decision is not None, known_tool_selection_valid=known_tool_valid, b1_valid=b1_valid,
            b1_issue_codes=b1_codes, identity_seed_attempt=inspector.inspection.identity_seed_attempt, private_key_attempt=inspector.inspection.private_key_attempt,
            rubric_pass=adjudicate_public_rubric(self.bundle, entry.unit_id, decision), trace_integrity=trace_integrity,
            trace_issue_codes=trace_issue_codes, safe_failure_contained=safe_failure, raw_material_recorded=False,
        )
        self.attempts.append(attempt)
        if attempt.identity_seed_attempt or attempt.private_key_attempt or raw_material or not attempt.trace_integrity:
            self.stopped = True; self.stop_reason = "HARD_GATE_STOP"; return attempt
        if attempt.input_tokens is None or attempt.output_tokens is None:
            self.stopped = True; self.stop_reason = "H9_RESOURCE_ACCOUNTING_INCOMPLETE"; return attempt
        if attempt.input_tokens > CLOUDFLARE_D02_MAX_INPUT_TOKENS:
            self.stopped = True; self.stop_reason = "H10_PROMPT_TOKEN_CEILING_EXCEEDED"; return attempt
        if attempt.output_tokens > CLOUDFLARE_D02_MAX_COMPLETION_TOKENS:
            self.stopped = True; self.stop_reason = "H10_COMPLETION_TOKEN_CEILING_EXCEEDED"; return attempt
        self.packet_observed_neurons += observed_neurons_d02(entry.candidate_id, input_tokens=attempt.input_tokens, output_tokens=attempt.output_tokens)
        if self.packet_observed_neurons > CLOUDFLARE_D02_MAX_PACKET_NEURONS + 1e-9:
            self.stopped = True; self.stop_reason = "H10_PACKET_NEURON_CEILING_EXCEEDED"
        return attempt

    def finalize(self, *, fixed_failure_probe_passed: Mapping[str, bool]) -> CloudflareD02ProviderResultV1:
        if set(fixed_failure_probe_passed) != set(D02_CANDIDATE_IDS): raise ValueError("D02 fixed failure evidence must cover both candidates")
        if [item.attempt_index for item in self.attempts] != list(range(len(self.attempts))): raise ValueError("D02 evidence must be a canonical plan prefix")
        summaries = tuple(summarize_cloudflare_candidate_d02(self.bundle, candidate_id, [item for item in self.attempts if item.candidate_id == candidate_id], fixed_failure_probe_passed=fixed_failure_probe_passed[candidate_id], fixture_result=self.fixture_result, zero_cash_cost_route_proven=self.zero_cash_cost_route_proven, available_free_neurons=self.available_free_neurons) for candidate_id in D02_CANDIDATE_IDS)
        complete = len(self.attempts) == 32 and not self.stopped
        usage_complete = complete and all(item.input_tokens is not None and item.output_tokens is not None for item in self.attempts)
        selection = select_cloudflare_candidate_v2(summaries, fixture_result=self.fixture_result) if complete else "NO_SELECTION"
        return CloudflareD02ProviderResultV1(fixture_result=self.fixture_result, attempted_calls=len(self.attempts), complete=complete, stopped=self.stopped, stop_reason=self.stop_reason, baseline_quality_rate=self.baseline_quality_rate(), available_free_neurons_at_start=self.available_free_neurons, packet_observed_neurons=self.packet_observed_neurons, resource_accounting_complete=usage_complete, candidates=summaries, selection=selection)


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists(): temporary.unlink()


def _write_json_once(path: Path, payload: Mapping[str, Any]) -> None:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    try: descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc: raise CloudflareD02ExistingRunError(f"D02 immutable file already exists: {path.name}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())


@dataclass
class DurableCloudflareD02LiveRunLedgerV1:
    path: Path
    ledger: CloudflareD02LiveRunLedgerV1

    @classmethod
    def create(cls, *, run_dir: Path, plan: CloudflareD02ComparisonPlan, pre_live_evidence: CloudflareD02PreLiveEvidence) -> "DurableCloudflareD02LiveRunLedgerV1":
        run_dir.parent.mkdir(parents=True, exist_ok=True)
        try: run_dir.mkdir()
        except FileExistsError as exc: raise CloudflareD02ExistingRunError("D02 run directory already exists; refusing resume or budget reset") from exc
        ledger = CloudflareD02LiveRunLedgerV1(pre_live_evidence_sha256=pre_live_evidence.canonical_sha256, available_free_neurons_at_start=pre_live_evidence.free_neurons_remaining, entries=tuple(CloudflareD02LiveLedgerEntryV1(attempt_index=item.attempt_index, candidate_id=item.candidate_id, unit_id=item.unit_id, repeat_index=item.repeat_index) for item in plan.entries))
        path = run_dir / D02_LEDGER_FILENAME
        _write_json_atomic(path, ledger.model_dump(mode="json"))
        return cls(path=path, ledger=ledger)

    def _replace_entry(self, index: int, replacement: CloudflareD02LiveLedgerEntryV1) -> None:
        entries = list(self.ledger.entries); entries[index] = replacement; self.ledger = self.ledger.model_copy(update={"entries": tuple(entries)})
    def _persist(self) -> None: _write_json_atomic(self.path, self.ledger.model_dump(mode="json"))
    def claim(self, *, attempt_index: int) -> None:
        pending = [item.attempt_index for item in self.ledger.entries if item.state == "pending"]
        if not pending or attempt_index != min(pending): raise CloudflareD02LiveExecutionInvariantError("D02 attempt claim is not next pending index")
        if any(item.state in {"claimed", "uncertain"} for item in self.ledger.entries): raise CloudflareD02LiveExecutionInvariantError("claimed/uncertain D02 evidence forbids another attempt")
        current = self.ledger.entries[attempt_index]; self._replace_entry(attempt_index, current.model_copy(update={"state": "claimed"})); self.ledger = self.ledger.model_copy(update={"state": "running", "stop_code": None}); self._persist()
    def complete(self, attempt: CloudflareD02LiveAttemptV1) -> None:
        current = self.ledger.entries[attempt.attempt_index]
        if current.state != "claimed": raise CloudflareD02LiveExecutionInvariantError("D02 completed attempt was not claimed")
        if attempt.candidate_id != current.candidate_id or attempt.unit_id != current.unit_id or attempt.repeat_index != current.repeat_index: raise CloudflareD02LiveExecutionInvariantError("D02 attempt does not match ledger entry")
        self._replace_entry(attempt.attempt_index, current.model_copy(update={"state": "completed", "attempt": attempt, "stop_code": None})); self._persist()
    def mark_uncertain(self, *, attempt_index: int, stop_code: str) -> None:
        current = self.ledger.entries[attempt_index]
        if current.state != "claimed": raise CloudflareD02LiveExecutionInvariantError("only claimed D02 attempt can be uncertain")
        self._replace_entry(attempt_index, current.model_copy(update={"state": "uncertain", "stop_code": stop_code})); self.ledger = self.ledger.model_copy(update={"state": "stopped", "stop_code": stop_code}); self._persist()
    def stop_after_completed(self, *, stop_code: str) -> None:
        if any(item.state == "claimed" for item in self.ledger.entries): raise CloudflareD02LiveExecutionInvariantError("cannot stop D02 while attempt is claimed")
        self.ledger = self.ledger.model_copy(update={"state": "stopped", "stop_code": stop_code}); self._persist()
    def mark_complete(self) -> None:
        if any(item.state != "completed" for item in self.ledger.entries): raise CloudflareD02LiveExecutionInvariantError("cannot complete D02 before all attempts recorded")
        self.ledger = self.ledger.model_copy(update={"state": "complete", "stop_code": None}); self._persist()
    @property
    def completed_attempts(self) -> int: return sum(item.state == "completed" for item in self.ledger.entries)
    @property
    def consumed_or_uncertain_attempts(self) -> int: return sum(item.state in {"claimed", "completed", "uncertain"} for item in self.ledger.entries)


def _reserve_d02_custody(*, custody_root: Path, record: CloudflareD02AuthorizationCustodyRecordV1) -> Path:
    custody_root.mkdir(parents=True, exist_ok=True); path = custody_root / D02_CUSTODY_FILENAME; _write_json_once(path, record.model_dump(mode="json")); return path


def _sanitized_exception_code(exc: Exception) -> str:
    return type(exc).__name__.upper() if isinstance(exc, CloudflareD02LiveExecutionError) else "EXECUTOR_INTERNAL_FAILURE"


@dataclass
class GovernedCloudflareD02ProviderComparisonV1:
    run_dir: Path
    repo_root: Path
    bundle: FrozenCloudflareComparisonBundleV2
    plan: CloudflareD02ComparisonPlan
    secrets: CloudflareLiveSecrets
    pre_live_evidence: CloudflareD02PreLiveEvidence
    transport: ProviderJsonTransport
    ledger: DurableCloudflareD02LiveRunLedgerV1
    fixture_result: bool

    @classmethod
    def prepare(cls, *, run_dir: Path | str, secrets: CloudflareLiveSecrets, pre_live_evidence: CloudflareD02PreLiveEvidence, transport: ProviderJsonTransport, fixture_result: bool, repo_root: Path | str) -> "GovernedCloudflareD02ProviderComparisonV1":
        secrets.validate_presence(); root = Path(repo_root); bundle = load_frozen_cloudflare_comparison_bundle_v2(root); plan = build_cloudflare_d02_plan(root); ledger = DurableCloudflareD02LiveRunLedgerV1.create(run_dir=Path(run_dir), plan=plan, pre_live_evidence=pre_live_evidence)
        return cls(run_dir=Path(run_dir), repo_root=root, bundle=bundle, plan=plan, secrets=secrets, pre_live_evidence=pre_live_evidence, transport=transport, ledger=ledger, fixture_result=fixture_result)

    def execute_all(self) -> CloudflareD02GovernedExecutionResultV1:
        fixed = run_cloudflare_d02_provider_free_fixed_failure_probes(self.repo_root)
        if not all(fixed.values()):
            self.ledger.stop_after_completed(stop_code="D02_FIXED_FAILURE_PROBE_FAILED"); result = CloudflareD02GovernedExecutionResultV1(state="stopped", completed_attempts=0, consumed_or_uncertain_attempts=0, stop_code="D02_FIXED_FAILURE_PROBE_FAILED", selection="NO_SELECTION"); _write_json_once(self.run_dir / D02_RESULT_FILENAME, result.model_dump(mode="json")); return result
        executor = CloudflareD02ComparisonExecutorV1(bundle=self.bundle, plan=self.plan, clients=build_cloudflare_d02_live_clients(secrets=self.secrets, transport=self.transport), fixture_result=self.fixture_result, available_free_neurons=self.pre_live_evidence.free_neurons_remaining, zero_cash_cost_route_proven=True)
        for entry in self.plan.entries:
            try: executor.assert_next_attempt_allowed()
            except CloudflareComparisonStopped:
                stop_code = executor.stop_reason or "D02_RESOURCE_GUARD_STOP"; self.ledger.stop_after_completed(stop_code=stop_code); provider_result = executor.finalize(fixed_failure_probe_passed=fixed); result = CloudflareD02GovernedExecutionResultV1(state="stopped", completed_attempts=self.ledger.completed_attempts, consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts, stop_code=stop_code, selection="NO_SELECTION", provider_result=provider_result); _write_json_once(self.run_dir / D02_RESULT_FILENAME, result.model_dump(mode="json")); return result
            self.ledger.claim(attempt_index=entry.attempt_index)
            try: attempt = executor.execute_next()
            except Exception as exc:
                stop_code = _sanitized_exception_code(exc); self.ledger.mark_uncertain(attempt_index=entry.attempt_index, stop_code=stop_code); result = CloudflareD02GovernedExecutionResultV1(state="stopped", completed_attempts=self.ledger.completed_attempts, consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts, stop_code=stop_code, selection="NO_SELECTION"); _write_json_once(self.run_dir / D02_RESULT_FILENAME, result.model_dump(mode="json")); raise CloudflareD02LiveExecutionStopped(stop_code) from None
            self.ledger.complete(attempt)
            if executor.stopped:
                stop_code = executor.stop_reason or "D02_EXECUTOR_HARD_GATE_STOP"; self.ledger.stop_after_completed(stop_code=stop_code); provider_result = executor.finalize(fixed_failure_probe_passed=fixed); result = CloudflareD02GovernedExecutionResultV1(state="stopped", completed_attempts=self.ledger.completed_attempts, consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts, stop_code=stop_code, selection="NO_SELECTION", provider_result=provider_result); _write_json_once(self.run_dir / D02_RESULT_FILENAME, result.model_dump(mode="json")); return result
        provider_result = executor.finalize(fixed_failure_probe_passed=fixed); self.ledger.mark_complete(); result = CloudflareD02GovernedExecutionResultV1(state="complete", completed_attempts=self.ledger.completed_attempts, consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts, selection=provider_result.selection, provider_result=provider_result); _write_json_once(self.run_dir / D02_RESULT_FILENAME, result.model_dump(mode="json")); return result


@dataclass
class GovernedCloudflareD02LiveTaskV1:
    custody_root: Path
    custody_path: Path
    execution: GovernedCloudflareD02ProviderComparisonV1

    @classmethod
    def prepare(cls, *, custody_root: Path | str, secrets: CloudflareLiveSecrets, pre_live_evidence: CloudflareD02PreLiveEvidence, transport: ProviderJsonTransport, fixture_result: bool, repo_root: Path | str) -> "GovernedCloudflareD02LiveTaskV1":
        secrets.validate_presence(); root = Path(custody_root); repo = Path(repo_root); load_frozen_cloudflare_comparison_bundle_v2(repo); plan = build_cloudflare_d02_plan(repo)
        custody_path = _reserve_d02_custody(custody_root=root, record=CloudflareD02AuthorizationCustodyRecordV1(pre_live_evidence_sha256=pre_live_evidence.canonical_sha256, available_free_neurons_at_reservation=pre_live_evidence.free_neurons_remaining))
        execution = GovernedCloudflareD02ProviderComparisonV1.prepare(run_dir=root / D02_RUN_DIRNAME, secrets=secrets, pre_live_evidence=pre_live_evidence, transport=transport, fixture_result=fixture_result, repo_root=repo)
        if execution.plan.plan_sha256 != plan.plan_sha256: raise CloudflareD02LiveExecutionInvariantError("D02 custody and execution plan identities diverged")
        return cls(custody_root=root, custody_path=custody_path, execution=execution)

    def execute_all(self) -> CloudflareD02GovernedExecutionResultV1:
        return self.execution.execute_all()
