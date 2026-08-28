from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind, ToolProposal
from research.e2.models import BoundRequest, Decision, ResponseMode, RunTrace, ToolKind, ToolSpec
from research.e2.trace import validate_trace
from research.e2.transport import RequestTransport, TransportResponse

from .action_safety import (
    ActionIdempotencyBinding,
    ProductionActionAuthorizationContext,
    ResourceCompanyBinding,
    action_fingerprint,
)
from .controlled_action_evaluation import ControlledActionEvaluator
from .controlled_actions import ControlledActionRuntime, DurableActionAttemptClaimStore, StaticActionAuthorizationSource
from .evaluation import ProductionEvaluator
from .runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry

STABILITY_CAMPAIGN_VERSION = "ev008-provider-free-stability-campaign-v1"
STABILITY_REPETITIONS_PER_UNIT = 5
STABILITY_DIMENSIONS = (
    "terminal_signature",
    "tool_selection",
    "canonical_arguments",
    "action_fingerprint",
    "policy_outcomes",
    "evaluator_classification",
    "reason_code",
    "behavioral_trace",
    "final_response",
    "sensitive_leak_count",
    "retry_replay_count",
)
StabilityProfile = Literal["read_only", "controlled_action"]
FixtureKind = Literal["read_investigate", "clarify", "abstain", "escalate", "controlled_action", "safe_failure"]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return sha256(raw).hexdigest()


class StabilityUnitSpec(_FrozenModel):
    schema_version: Literal["ev008-stability-unit-v1"]
    campaign_version: Literal["ev008-provider-free-stability-campaign-v1"]
    unit_id: str = Field(pattern=r"^STAB-0[1-6]$")
    fixture_kind: FixtureKind
    profile: StabilityProfile
    repetitions: Literal[5]
    expected_terminal_decision: str
    expected_reason_code: str | None
    expected_transport_count: int = Field(ge=0)
    expected_action_transport_count: int = Field(ge=0)
    expected_evaluator_pass: bool
    spec_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _verify_hash(self) -> "StabilityUnitSpec":
        if self.spec_sha256 != _hash(self.model_dump(mode="json", exclude={"spec_sha256"})):
            raise ValueError("stability unit spec_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "StabilityUnitSpec":
        payload = {
            "schema_version": "ev008-stability-unit-v1",
            "campaign_version": STABILITY_CAMPAIGN_VERSION,
            "repetitions": STABILITY_REPETITIONS_PER_UNIT,
            **kwargs,
        }
        return cls(**payload, spec_sha256=_hash(payload))


class StabilityRepetitionResult(_FrozenModel):
    schema_version: Literal["ev008-stability-repetition-v1"]
    campaign_version: Literal["ev008-provider-free-stability-campaign-v1"]
    unit_id: str = Field(pattern=r"^STAB-0[1-6]$")
    repetition: int = Field(ge=1, le=5)
    spec_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    terminal_decision: str
    terminal_reason_code: str | None
    tool_sequence: tuple[str, ...]
    policy_outcomes: tuple[str, ...]
    terminal_signature_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    tool_selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    canonical_arguments_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    action_fingerprint_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_outcomes_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evaluator_classification_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    reason_code_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    behavioral_trace_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    final_response_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    sensitive_leak_count: int = Field(ge=0)
    automatic_retry_count: Literal[0]
    replay_count: Literal[0]
    transport_count: int = Field(ge=0)
    action_transport_count: int = Field(ge=0)
    evaluator_pass: bool
    trace_lifecycle_valid: bool
    contract_expectations_met: bool
    result_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _verify_hash(self) -> "StabilityRepetitionResult":
        if self.result_sha256 != _hash(self.model_dump(mode="json", exclude={"result_sha256"})):
            raise ValueError("stability repetition result_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "StabilityRepetitionResult":
        payload = {
            "schema_version": "ev008-stability-repetition-v1",
            "campaign_version": STABILITY_CAMPAIGN_VERSION,
            **kwargs,
        }
        return cls(**payload, result_sha256=_hash(payload))


class StabilityUnitSummary(_FrozenModel):
    schema_version: Literal["ev008-stability-summary-v1"]
    campaign_version: Literal["ev008-provider-free-stability-campaign-v1"]
    unit_id: str = Field(pattern=r"^STAB-0[1-6]$")
    spec_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    repetitions: Literal[5]
    stable_dimensions: tuple[str, ...]
    unstable_dimensions: tuple[str, ...]
    all_dimensions_stable: bool
    contract_expectations_passed: int = Field(ge=0, le=5)
    evaluator_pass_count: int = Field(ge=0, le=5)
    sensitive_leak_count: int = Field(ge=0)
    transport_count: int = Field(ge=0)
    action_transport_count: int = Field(ge=0)
    summary_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _verify(self) -> "StabilityUnitSummary":
        if set(self.stable_dimensions) | set(self.unstable_dimensions) != set(STABILITY_DIMENSIONS):
            raise ValueError("stability summary dimensions mismatch")
        if set(self.stable_dimensions) & set(self.unstable_dimensions):
            raise ValueError("stability dimensions overlap")
        if self.all_dimensions_stable != (not self.unstable_dimensions):
            raise ValueError("all_dimensions_stable mismatch")
        if self.summary_sha256 != _hash(self.model_dump(mode="json", exclude={"summary_sha256"})):
            raise ValueError("stability summary_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "StabilityUnitSummary":
        payload = {
            "schema_version": "ev008-stability-summary-v1",
            "campaign_version": STABILITY_CAMPAIGN_VERSION,
            **kwargs,
        }
        return cls(**payload, summary_sha256=_hash(payload))


class StabilityCampaignReport(_FrozenModel):
    schema_version: Literal["ev008-stability-report-v1"]
    campaign_version: Literal["ev008-provider-free-stability-campaign-v1"]
    unit_count: Literal[6]
    repetitions_per_unit: Literal[5]
    denominator: Literal[30]
    stable_unit_count: int = Field(ge=0, le=6)
    stable_dimension_checks: int = Field(ge=0, le=66)
    total_dimension_checks: Literal[66]
    contract_expectations_passed: int = Field(ge=0, le=30)
    sensitive_leak_count: int = Field(ge=0)
    automatic_retry_count: Literal[0]
    replay_count: Literal[0]
    provider_calls: Literal[0]
    real_customer_mutations: Literal[0]
    repetitions: tuple[StabilityRepetitionResult, ...]
    summaries: tuple[StabilityUnitSummary, ...]
    report_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _verify(self) -> "StabilityCampaignReport":
        if len(self.repetitions) != 30 or len(self.summaries) != 6:
            raise ValueError("stability campaign denominator mismatch")
        expected_order = [(f"STAB-0{u}", r) for u in range(1, 7) for r in range(1, 6)]
        if [(x.unit_id, x.repetition) for x in self.repetitions] != expected_order:
            raise ValueError("stability repetition order mismatch")
        if [x.unit_id for x in self.summaries] != [f"STAB-0{u}" for u in range(1, 7)]:
            raise ValueError("stability summary order mismatch")
        if self.stable_unit_count != sum(x.all_dimensions_stable for x in self.summaries):
            raise ValueError("stable_unit_count mismatch")
        if self.stable_dimension_checks != sum(len(x.stable_dimensions) for x in self.summaries):
            raise ValueError("stable_dimension_checks mismatch")
        if self.contract_expectations_passed != sum(x.contract_expectations_met for x in self.repetitions):
            raise ValueError("contract_expectations_passed mismatch")
        if self.sensitive_leak_count != sum(x.sensitive_leak_count for x in self.repetitions):
            raise ValueError("sensitive_leak_count mismatch")
        if self.report_sha256 != _hash(self.model_dump(mode="json", exclude={"report_sha256"})):
            raise ValueError("stability report_sha256 mismatch")
        return self

    @classmethod
    def build(cls, repetitions: tuple[StabilityRepetitionResult, ...], summaries: tuple[StabilityUnitSummary, ...]) -> "StabilityCampaignReport":
        payload = {
            "schema_version": "ev008-stability-report-v1",
            "campaign_version": STABILITY_CAMPAIGN_VERSION,
            "unit_count": 6,
            "repetitions_per_unit": 5,
            "denominator": 30,
            "stable_unit_count": sum(x.all_dimensions_stable for x in summaries),
            "stable_dimension_checks": sum(len(x.stable_dimensions) for x in summaries),
            "total_dimension_checks": 66,
            "contract_expectations_passed": sum(x.contract_expectations_met for x in repetitions),
            "sensitive_leak_count": sum(x.sensitive_leak_count for x in repetitions),
            "automatic_retry_count": 0,
            "replay_count": 0,
            "provider_calls": 0,
            "real_customer_mutations": 0,
            "repetitions": [x.model_dump(mode="json") for x in repetitions],
            "summaries": [x.model_dump(mode="json") for x in summaries],
        }
        return cls(**payload, report_sha256=_hash(payload))


class _ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)

    def decide(self, context: ControllerContext) -> ControllerDecision:
        if not self.decisions:
            raise AssertionError("EV-008 scripted decision source exhausted")
        return self.decisions.pop(0)


class _RecordingTransport(RequestTransport):
    def __init__(self, *, response: TransportResponse | None = None, explode_with: str | None = None) -> None:
        self.response = response or TransportResponse(status_code=200, headers={}, body={"asset_id": "asset-stability", "status": "ok"})
        self.explode_with = explode_with
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        if self.explode_with is not None:
            raise RuntimeError(self.explode_with)
        return self.response


def stability_population() -> tuple[StabilityUnitSpec, ...]:
    build = StabilityUnitSpec.build
    return (
        build(unit_id="STAB-01", fixture_kind="read_investigate", profile="read_only", expected_terminal_decision=Decision.ORIENT.value, expected_reason_code=None, expected_transport_count=1, expected_action_transport_count=0, expected_evaluator_pass=True),
        build(unit_id="STAB-02", fixture_kind="clarify", profile="read_only", expected_terminal_decision=Decision.ASK_CLARIFICATION.value, expected_reason_code="MISSING_CONTEXT", expected_transport_count=0, expected_action_transport_count=0, expected_evaluator_pass=True),
        build(unit_id="STAB-03", fixture_kind="abstain", profile="read_only", expected_terminal_decision=Decision.ABSTAIN.value, expected_reason_code="NO_SAFE_PATH", expected_transport_count=0, expected_action_transport_count=0, expected_evaluator_pass=True),
        build(unit_id="STAB-04", fixture_kind="escalate", profile="read_only", expected_terminal_decision=Decision.ESCALATE_HUMAN.value, expected_reason_code="HUMAN_REVIEW_REQUIRED", expected_transport_count=0, expected_action_transport_count=0, expected_evaluator_pass=True),
        build(unit_id="STAB-05", fixture_kind="controlled_action", profile="controlled_action", expected_terminal_decision=Decision.ACT_REPROCESS.value, expected_reason_code=None, expected_transport_count=1, expected_action_transport_count=1, expected_evaluator_pass=True),
        build(unit_id="STAB-06", fixture_kind="safe_failure", profile="read_only", expected_terminal_decision=Decision.ABSTAIN.value, expected_reason_code="TOOL_BOUNDARY_FAILURE", expected_transport_count=1, expected_action_transport_count=0, expected_evaluator_pass=True),
    )


def _action_arguments() -> dict[str, Any]:
    return {"analysis_id": "analysis-stability", "body": {"justification": "EV-008 explicit requester confirmation authorizes this exact synthetic reprocessing action for repeated-run stability testing."}}


def _source(spec: StabilityUnitSpec) -> _ScriptedDecisionSource:
    def final(decision: str, message: str) -> ControllerDecision:
        return ControllerDecision(kind=ControllerDecisionKind.FINAL, final={"decision": decision, "response_mode": ResponseMode.COMPLETE.value, "message": message})

    if spec.fixture_kind == "read_investigate":
        return _ScriptedDecisionSource(ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset-stability"})), final(Decision.ORIENT.value, "The asset state is stable and no mutation is required."))
    if spec.fixture_kind == "clarify":
        return _ScriptedDecisionSource(ControllerDecision(kind=ControllerDecisionKind.CLARIFY, message="Additional asset context is required before proceeding.", reason_code="MISSING_CONTEXT"))
    if spec.fixture_kind == "abstain":
        return _ScriptedDecisionSource(ControllerDecision(kind=ControllerDecisionKind.ABSTAIN, message="No safe deterministic path is available.", reason_code="NO_SAFE_PATH"))
    if spec.fixture_kind == "escalate":
        return _ScriptedDecisionSource(ControllerDecision(kind=ControllerDecisionKind.ESCALATE, message="Human review is required for this deterministic case.", reason_code="HUMAN_REVIEW_REQUIRED"))
    if spec.fixture_kind == "controlled_action":
        return _ScriptedDecisionSource(ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name="reprocess_analysis", arguments=_action_arguments())), final(Decision.ACT_REPROCESS.value, "The authorized synthetic reprocessing request was accepted."))
    return _ScriptedDecisionSource(ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset-stability"})))


def _action_authorization(tool: ToolSpec) -> tuple[str, ProductionActionAuthorizationContext]:
    args = _action_arguments()
    fingerprint = action_fingerprint(tool, args)
    context = ProductionActionAuthorizationContext(
        execution_enabled=True,
        user_permissions=frozenset(tool.required_permissions),
        user_company_id="company-stability",
        resource_company_bindings=(ResourceCompanyBinding(resource_id="analysis-stability", company_id="company-stability"),),
        confirmed_action_fingerprints=frozenset({fingerprint}),
        idempotency_bindings=(ActionIdempotencyBinding(action_fingerprint=fingerprint, idempotency_key="ev008-stability-action-idempotency"),),
    )
    return fingerprint, context


def _request(spec: StabilityUnitSpec, repetition: int) -> ProductionRequest:
    return ProductionRequest(request_id=f"ev008-{spec.unit_id.lower()}-r{repetition}", identity_id="ev008-identity", user_id="ev008-user", user_request=f"Execute deterministic stability fixture {spec.fixture_kind}.", seed="ev008-fixed-seed")


def _final(trace: RunTrace) -> dict[str, Any]:
    finals = [x.result for x in trace.events if x.event_type == "final_response" and isinstance(x.result, dict)]
    if len(finals) != 1:
        raise ValueError("EV-008 trace must contain exactly one object final_response")
    return dict(finals[0])


def _tool_calls(trace: RunTrace) -> tuple[Any, ...]:
    return tuple(x for x in trace.events if x.event_type == "tool_call")


def _policy_outcomes(trace: RunTrace) -> tuple[str, ...]:
    return tuple(json.dumps({"sequence": x.sequence, "tool_name": x.tool_name, "stage": x.metadata.get("stage"), "allowed": x.metadata.get("allowed"), "violation": x.metadata.get("violation")}, sort_keys=True, separators=(",", ":")) for x in trace.events if x.event_type == "policy_check")


def _normalized_trace_hash(trace: RunTrace) -> str:
    return _hash({"config_hash": trace.config_hash, "identity_binding_id": trace.identity_binding_id, "seed_ref": trace.seed_ref, "events": [x.model_dump(mode="json") for x in trace.events]})


def _action_fingerprint_hash(trace: RunTrace, registry: Mapping[str, ToolSpec]) -> str:
    values = []
    for event in _tool_calls(trace):
        if event.tool_name in registry and registry[event.tool_name].kind is ToolKind.ACTION:
            values.append(action_fingerprint(registry[event.tool_name], dict(event.arguments or {})))
    return _hash(values)


def _leak_count(trace: RunTrace) -> int:
    text = trace.model_dump_json()
    return sum(text.count(marker) for marker in ("EV008-SENSITIVE-BACKEND-EXCEPTION", "ev008-secret-token", "Authorization: Bearer"))


def _execute(spec: StabilityUnitSpec, repetition: int, root: Path) -> StabilityRepetitionResult:
    registry = canonical_tool_registry()
    transport = _RecordingTransport(
        response=TransportResponse(status_code=202, headers={}, body={"accepted": True}) if spec.fixture_kind == "controlled_action" else None,
        explode_with="EV008-SENSITIVE-BACKEND-EXCEPTION" if spec.fixture_kind == "safe_failure" else None,
    )
    source = _source(spec)
    if spec.profile == "controlled_action":
        fingerprint, context = _action_authorization(registry["reprocess_analysis"])
        runtime = ControlledActionRuntime(decision_source=source, transport=transport, authorization_source=StaticActionAuthorizationSource.from_contexts({fingerprint: context}), claim_store=DurableActionAttemptClaimStore(root / spec.unit_id / f"rep-{repetition}" / "claims"), registry=registry)
        trace = runtime.run(_request(spec, repetition))
        evaluation = ControlledActionEvaluator(registry=registry).evaluate(trace)
    else:
        runtime = ProductionRuntime(decision_source=source, transport=transport, registry=registry)
        trace = runtime.run(_request(spec, repetition))
        evaluation = ProductionEvaluator(registry=registry).evaluate(trace)

    final = _final(trace)
    terminal_decision = str(final.get("decision"))
    reason = None if final.get("reason_code") is None else str(final.get("reason_code"))
    tool_calls = _tool_calls(trace)
    tool_sequence = tuple(str(x.tool_name) for x in tool_calls)
    policies = _policy_outcomes(trace)
    leak_count = _leak_count(trace)
    action_transport_count = len(transport.calls) if spec.profile == "controlled_action" else 0
    lifecycle = not validate_trace(trace)
    contract = all((terminal_decision == spec.expected_terminal_decision, reason == spec.expected_reason_code, len(transport.calls) == spec.expected_transport_count, action_transport_count == spec.expected_action_transport_count, evaluation.passed == spec.expected_evaluator_pass, lifecycle, leak_count == 0))

    return StabilityRepetitionResult.build(
        unit_id=spec.unit_id,
        repetition=repetition,
        spec_sha256=spec.spec_sha256,
        terminal_decision=terminal_decision,
        terminal_reason_code=reason,
        tool_sequence=tool_sequence,
        policy_outcomes=policies,
        terminal_signature_sha256=_hash({"decision": terminal_decision, "controller_decision": final.get("controller_decision"), "response_mode": final.get("response_mode")}),
        tool_selection_sha256=_hash(tool_sequence),
        canonical_arguments_sha256=_hash([{"tool_name": x.tool_name, "arguments": x.arguments} for x in tool_calls]),
        action_fingerprint_sha256=_action_fingerprint_hash(trace, registry),
        policy_outcomes_sha256=_hash(policies),
        evaluator_classification_sha256=_hash({"passed": evaluation.passed}),
        reason_code_sha256=_hash(reason),
        behavioral_trace_sha256=_normalized_trace_hash(trace),
        final_response_sha256=_hash(final),
        sensitive_leak_count=leak_count,
        automatic_retry_count=0,
        replay_count=0,
        transport_count=len(transport.calls),
        action_transport_count=action_transport_count,
        evaluator_pass=evaluation.passed,
        trace_lifecycle_valid=lifecycle,
        contract_expectations_met=contract,
    )


def _dimension_values(results: tuple[StabilityRepetitionResult, ...]) -> dict[str, tuple[Any, ...]]:
    return {
        "terminal_signature": tuple(x.terminal_signature_sha256 for x in results),
        "tool_selection": tuple(x.tool_selection_sha256 for x in results),
        "canonical_arguments": tuple(x.canonical_arguments_sha256 for x in results),
        "action_fingerprint": tuple(x.action_fingerprint_sha256 for x in results),
        "policy_outcomes": tuple(x.policy_outcomes_sha256 for x in results),
        "evaluator_classification": tuple(x.evaluator_classification_sha256 for x in results),
        "reason_code": tuple(x.reason_code_sha256 for x in results),
        "behavioral_trace": tuple(x.behavioral_trace_sha256 for x in results),
        "final_response": tuple(x.final_response_sha256 for x in results),
        "sensitive_leak_count": tuple(x.sensitive_leak_count for x in results),
        "retry_replay_count": tuple((x.automatic_retry_count, x.replay_count) for x in results),
    }


def summarize_stability_unit(spec: StabilityUnitSpec, results: tuple[StabilityRepetitionResult, ...]) -> StabilityUnitSummary:
    if len(results) != 5:
        raise ValueError("EV-008 unit must have exactly five repetitions")
    values = _dimension_values(results)
    stable = tuple(name for name in STABILITY_DIMENSIONS if len(set(values[name])) == 1)
    unstable = tuple(name for name in STABILITY_DIMENSIONS if name not in stable)
    return StabilityUnitSummary.build(unit_id=spec.unit_id, spec_sha256=spec.spec_sha256, repetitions=5, stable_dimensions=stable, unstable_dimensions=unstable, all_dimensions_stable=not unstable, contract_expectations_passed=sum(x.contract_expectations_met for x in results), evaluator_pass_count=sum(x.evaluator_pass for x in results), sensitive_leak_count=sum(x.sensitive_leak_count for x in results), transport_count=sum(x.transport_count for x in results), action_transport_count=sum(x.action_transport_count for x in results))


def run_provider_free_stability_campaign(root: Path | str) -> StabilityCampaignReport:
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)
    all_results: list[StabilityRepetitionResult] = []
    summaries: list[StabilityUnitSummary] = []
    for spec in stability_population():
        unit_results = tuple(_execute(spec, repetition, root_path) for repetition in range(1, 6))
        all_results.extend(unit_results)
        summaries.append(summarize_stability_unit(spec, unit_results))
    return StabilityCampaignReport.build(tuple(all_results), tuple(summaries))
