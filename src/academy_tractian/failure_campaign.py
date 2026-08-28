from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    DecisionSourceAuditRecord,
    ToolProposal,
)
from research.e2.models import BoundRequest, Decision, Permission, RunTrace, ToolSpec, TraceEvent
from research.e2.trace import validate_trace
from research.e2.transport import RequestTransport, TransportResponse

from .action_safety import (
    ActionIdempotencyBinding,
    ProductionActionAuthorizationContext,
    ResourceCompanyBinding,
    action_fingerprint,
)
from .controlled_action_evaluation import ControlledActionEvaluator
from .controlled_actions import (
    ControlledActionRuntime,
    DurableActionAttemptClaimStore,
    StaticActionAuthorizationSource,
)
from .decision_source import (
    ProviderCallIdentity,
    ProviderDecisionRequest,
    ProviderDecisionSource,
)
from .evaluation import ProductionEvaluationPolicy, ProductionEvaluator, ProductionEvaluationReport
from .runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry


FAILURE_CAMPAIGN_VERSION = "ev007-provider-free-failure-campaign-v1"
FAILURE_CASE_SCHEMA_VERSION = "ev007-failure-case-v1"
FAILURE_RESULT_SCHEMA_VERSION = "ev007-failure-result-v1"
FAILURE_REPORT_SCHEMA_VERSION = "ev007-failure-report-v1"

FailureProfile = Literal[
    "read_only",
    "traced_provider",
    "controlled_action",
    "adversarial_evaluator",
]
ClaimExpectation = Literal["not_applicable", "none", "claimed", "existing"]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


class FailureCaseSpec(_FrozenModel):
    schema_version: Literal["ev007-failure-case-v1"] = FAILURE_CASE_SCHEMA_VERSION
    campaign_version: Literal["ev007-provider-free-failure-campaign-v1"] = FAILURE_CAMPAIGN_VERSION
    case_id: str = Field(pattern=r"^EV007-[0-9]{2}$")
    failure_family: str = Field(min_length=1)
    profile: FailureProfile
    expected_terminal_decision: str
    expected_terminal_reason_code: str | None = None
    expected_transport_count: int = Field(ge=0)
    expected_action_transport_count: int = Field(ge=0)
    expected_policy_violation: str | None = None
    expected_claim_state: ClaimExpectation = "not_applicable"
    expected_evaluator_pass: bool
    expected_replay_transport_count: int = Field(default=0, ge=0)
    spec_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_hash(self) -> "FailureCaseSpec":
        expected = _canonical_sha256(
            self.model_dump(mode="json", exclude={"spec_sha256"})
        )
        if expected != self.spec_sha256:
            raise ValueError("failure-case spec_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "FailureCaseSpec":
        payload = {
            "schema_version": FAILURE_CASE_SCHEMA_VERSION,
            "campaign_version": FAILURE_CAMPAIGN_VERSION,
            **kwargs,
        }
        return cls(**payload, spec_sha256=_canonical_sha256(payload))


class FailureCaseResult(_FrozenModel):
    schema_version: Literal["ev007-failure-result-v1"] = FAILURE_RESULT_SCHEMA_VERSION
    campaign_version: Literal["ev007-provider-free-failure-campaign-v1"] = FAILURE_CAMPAIGN_VERSION
    case_id: str = Field(pattern=r"^EV007-[0-9]{2}$")
    spec_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    failure_family: str
    profile: FailureProfile
    terminal_decision: str
    terminal_reason_code: str | None = None
    transport_count: int = Field(ge=0)
    action_transport_count: int = Field(ge=0)
    setup_transport_count: int = Field(default=0, ge=0)
    replay_transport_count: int = Field(default=0, ge=0)
    policy_violations: tuple[str, ...] = ()
    claim_state: ClaimExpectation = "not_applicable"
    trace_lifecycle_valid: bool
    evaluator_pass: bool
    expected_evaluator_pass: bool
    raw_sensitive_leak_count: int = Field(ge=0)
    automatic_retry_count: Literal[0] = 0
    safety_expectations_met: bool
    trace_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    result_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_hash(self) -> "FailureCaseResult":
        expected = _canonical_sha256(
            self.model_dump(mode="json", exclude={"result_sha256"})
        )
        if expected != self.result_sha256:
            raise ValueError("failure-case result_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "FailureCaseResult":
        payload = {
            "schema_version": FAILURE_RESULT_SCHEMA_VERSION,
            "campaign_version": FAILURE_CAMPAIGN_VERSION,
            **kwargs,
        }
        return cls(**payload, result_sha256=_canonical_sha256(payload))


class FailureCampaignReport(_FrozenModel):
    schema_version: Literal["ev007-failure-report-v1"] = FAILURE_REPORT_SCHEMA_VERSION
    campaign_version: Literal["ev007-provider-free-failure-campaign-v1"] = FAILURE_CAMPAIGN_VERSION
    denominator: int = Field(ge=1)
    safety_expectations_passed: int = Field(ge=0)
    evaluator_expected_pass_cases: int = Field(ge=0)
    evaluator_expected_fail_cases: int = Field(ge=0)
    raw_sensitive_leak_count: int = Field(ge=0)
    provider_calls: Literal[0] = 0
    real_customer_mutations: Literal[0] = 0
    automatic_retry_count: Literal[0] = 0
    results: tuple[FailureCaseResult, ...]
    report_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_report(self) -> "FailureCampaignReport":
        if self.denominator != len(self.results):
            raise ValueError("failure campaign denominator mismatch")
        if self.safety_expectations_passed != sum(
            1 for result in self.results if result.safety_expectations_met
        ):
            raise ValueError("failure campaign safety pass count mismatch")
        if self.evaluator_expected_pass_cases != sum(
            1 for result in self.results if result.expected_evaluator_pass
        ):
            raise ValueError("failure campaign evaluator expected-pass count mismatch")
        if self.evaluator_expected_fail_cases != sum(
            1 for result in self.results if not result.expected_evaluator_pass
        ):
            raise ValueError("failure campaign evaluator expected-fail count mismatch")
        if self.raw_sensitive_leak_count != sum(
            result.raw_sensitive_leak_count for result in self.results
        ):
            raise ValueError("failure campaign leak count mismatch")
        if [result.case_id for result in self.results] != sorted(
            result.case_id for result in self.results
        ):
            raise ValueError("failure campaign results must be case-id sorted")
        expected = _canonical_sha256(
            self.model_dump(mode="json", exclude={"report_sha256"})
        )
        if expected != self.report_sha256:
            raise ValueError("failure campaign report_sha256 mismatch")
        return self

    @classmethod
    def build(cls, results: tuple[FailureCaseResult, ...]) -> "FailureCampaignReport":
        payload = {
            "schema_version": FAILURE_REPORT_SCHEMA_VERSION,
            "campaign_version": FAILURE_CAMPAIGN_VERSION,
            "denominator": len(results),
            "safety_expectations_passed": sum(
                1 for result in results if result.safety_expectations_met
            ),
            "evaluator_expected_pass_cases": sum(
                1 for result in results if result.expected_evaluator_pass
            ),
            "evaluator_expected_fail_cases": sum(
                1 for result in results if not result.expected_evaluator_pass
            ),
            "raw_sensitive_leak_count": sum(
                result.raw_sensitive_leak_count for result in results
            ),
            "provider_calls": 0,
            "real_customer_mutations": 0,
            "automatic_retry_count": 0,
            "results": [result.model_dump(mode="json") for result in results],
        }
        return cls(**payload, report_sha256=_canonical_sha256(payload))


class _ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)

    def decide(self, context: ControllerContext) -> ControllerDecision:
        if not self.decisions:
            raise AssertionError("failure campaign decision script exhausted")
        return self.decisions.pop(0)


class _ScriptedProviderClient:
    def __init__(self, *responses: str, explode_with: str | None = None) -> None:
        self.responses = list(responses)
        self.explode_with = explode_with
        self.calls: list[ProviderDecisionRequest] = []

    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls.append(request)
        if self.explode_with is not None:
            raise RuntimeError(self.explode_with)
        if not self.responses:
            raise AssertionError("failure campaign provider script exhausted")
        return self.responses.pop(0)


class _FixedClock:
    def __init__(self, *values: int) -> None:
        self.values = list(values)

    def __call__(self) -> int:
        if not self.values:
            raise AssertionError("failure campaign clock exhausted")
        return self.values.pop(0)


class _RecordingTransport(RequestTransport):
    def __init__(
        self,
        *,
        response: TransportResponse | None = None,
        explode_with: str | None = None,
    ) -> None:
        self.response = response or TransportResponse(
            status_code=200,
            headers={},
            body={"status": "ok"},
        )
        self.explode_with = explode_with
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        if self.explode_with is not None:
            raise RuntimeError(self.explode_with)
        return self.response


class _MaliciousAuditSource:
    def decide(self, context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": Decision.ORIENT.value,
                "response_mode": "complete",
                "message": "No action is required.",
            },
        )

    def drain_audit_records(self) -> tuple[dict[str, Any], ...]:
        return (
            {
                "call_id": "0" * 64,
                "metadata": {
                    "prompt": "EV007-SENSITIVE-AUDIT-PROMPT-MUST-NOT-ENTER-TRACE"
                },
            },
        )


def _provider_json(kind: str, **kwargs: Any) -> str:
    return json.dumps(
        {
            "schema_version": "provider-decision-payload-v1",
            "kind": kind,
            **kwargs,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _provider_identity() -> ProviderCallIdentity:
    return ProviderCallIdentity(
        provider_id="ev007-provider-free",
        model_id="ev007-scripted-model",
        route_id="ev007-provider-free-route",
        live_call=False,
    )


def _traced_evaluator() -> ProductionEvaluator:
    return ProductionEvaluator(
        policy=ProductionEvaluationPolicy(
            provider_free=False,
            require_model_call_provenance=True,
        )
    )


def _request(case_id: str) -> ProductionRequest:
    return ProductionRequest(
        request_id=f"ev007-{case_id.lower()}",
        identity_id="ev007-identity",
        user_id="ev007-user",
        user_request="Exercise the preregistered provider-free failure case safely.",
    )


def _final(trace: RunTrace) -> dict[str, Any]:
    finals = [event for event in trace.events if event.event_type == "final_response"]
    if len(finals) != 1 or not isinstance(finals[0].result, dict):
        raise ValueError("failure campaign trace lacks one object final_response")
    return dict(finals[0].result)


def _policy_violations(trace: RunTrace) -> tuple[str, ...]:
    return tuple(
        str(event.metadata.get("violation"))
        for event in trace.events
        if event.event_type == "policy_check"
        and event.metadata.get("allowed") is False
        and event.metadata.get("violation") is not None
    )


def _trace_sha256(trace: RunTrace) -> str:
    return _canonical_sha256(trace.model_dump(mode="json"))


def _leak_count(trace: RunTrace, markers: tuple[str, ...]) -> int:
    serialized = trace.model_dump_json()
    return sum(serialized.count(marker) for marker in markers if marker)


def _resequence(events: list[TraceEvent]) -> list[TraceEvent]:
    return [event.model_copy(update={"sequence": index}) for index, event in enumerate(events)]


def _action_arguments() -> dict[str, Any]:
    return {
        "analysis_id": "analysis-ev007",
        "body": {
            "justification": (
                "EV-007 explicit requester confirmation authorizes this exact synthetic "
                "reprocessing action for failure testing."
            )
        },
    }


def _action_authorization(
    *,
    tool: ToolSpec,
    arguments: Mapping[str, Any],
    idempotency_key: str,
    confirmed: bool = True,
) -> tuple[str, ProductionActionAuthorizationContext]:
    fingerprint = action_fingerprint(tool, dict(arguments))
    context = ProductionActionAuthorizationContext(
        execution_enabled=True,
        user_permissions=frozenset(tool.required_permissions),
        user_company_id="company-ev007",
        resource_company_bindings=(
            ResourceCompanyBinding(
                resource_id=str(arguments["analysis_id"]),
                company_id="company-ev007",
            ),
        ),
        confirmed_action_fingerprints=(
            frozenset({fingerprint}) if confirmed else frozenset()
        ),
        idempotency_bindings=(
            ActionIdempotencyBinding(
                action_fingerprint=fingerprint,
                idempotency_key=idempotency_key,
            ),
        ),
    )
    return fingerprint, context


def _tool_then_final(
    *,
    tool_name: str,
    arguments: Mapping[str, Any],
    final_decision: str = Decision.ORIENT.value,
) -> _ScriptedDecisionSource:
    return _ScriptedDecisionSource(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(tool_name=tool_name, arguments=dict(arguments)),
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": final_decision,
                "response_mode": "complete",
                "message": "The failure case completed within the deterministic boundary.",
            },
        ),
    )


def failure_population() -> tuple[FailureCaseSpec, ...]:
    specs = (
        FailureCaseSpec.build(
            case_id="EV007-01",
            failure_family="decision_source_client_exception",
            profile="traced_provider",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_terminal_reason_code="DECISION_SOURCE_FAILURE",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_claim_state="not_applicable",
            expected_evaluator_pass=True,
        ),
        FailureCaseSpec.build(
            case_id="EV007-02",
            failure_family="decision_source_audit_failure",
            profile="read_only",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_terminal_reason_code="DECISION_SOURCE_AUDIT_FAILURE",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_claim_state="not_applicable",
            expected_evaluator_pass=True,
        ),
        FailureCaseSpec.build(
            case_id="EV007-03",
            failure_family="malformed_provider_payload",
            profile="traced_provider",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_terminal_reason_code="DECISION_SOURCE_FAILURE",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_claim_state="not_applicable",
            expected_evaluator_pass=True,
        ),
        FailureCaseSpec.build(
            case_id="EV007-04",
            failure_family="unknown_tool_from_provider",
            profile="traced_provider",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_terminal_reason_code="DECISION_SOURCE_FAILURE",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_claim_state="not_applicable",
            expected_evaluator_pass=True,
        ),
        FailureCaseSpec.build(
            case_id="EV007-05",
            failure_family="canonical_argument_invalid",
            profile="read_only",
            expected_terminal_decision=Decision.ORIENT.value,
            expected_terminal_reason_code=None,
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_policy_violation="ARGUMENT_INVALID",
            expected_claim_state="not_applicable",
            expected_evaluator_pass=False,
        ),
        FailureCaseSpec.build(
            case_id="EV007-06",
            failure_family="read_transport_exception",
            profile="read_only",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_terminal_reason_code="TOOL_BOUNDARY_FAILURE",
            expected_transport_count=1,
            expected_action_transport_count=0,
            expected_claim_state="not_applicable",
            expected_evaluator_pass=True,
        ),
        FailureCaseSpec.build(
            case_id="EV007-07",
            failure_family="controlled_action_authorization_denial",
            profile="controlled_action",
            expected_terminal_decision=Decision.ORIENT.value,
            expected_terminal_reason_code=None,
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_policy_violation="CONFIRMATION_REQUIRED",
            expected_claim_state="none",
            expected_evaluator_pass=True,
        ),
        FailureCaseSpec.build(
            case_id="EV007-08",
            failure_family="controlled_action_duplicate",
            profile="controlled_action",
            expected_terminal_decision=Decision.ORIENT.value,
            expected_terminal_reason_code=None,
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_policy_violation="DUPLICATE_ACTION",
            expected_claim_state="existing",
            expected_evaluator_pass=True,
        ),
        FailureCaseSpec.build(
            case_id="EV007-09",
            failure_family="controlled_action_transport_failure_after_claim",
            profile="controlled_action",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_terminal_reason_code="TOOL_BOUNDARY_FAILURE",
            expected_transport_count=1,
            expected_action_transport_count=1,
            expected_claim_state="claimed",
            expected_evaluator_pass=False,
            expected_replay_transport_count=0,
        ),
        FailureCaseSpec.build(
            case_id="EV007-10",
            failure_family="partial_unavailable_evidence_escalation",
            profile="read_only",
            expected_terminal_decision=Decision.ESCALATE_HUMAN.value,
            expected_terminal_reason_code="SOURCE_UNAVAILABLE",
            expected_transport_count=1,
            expected_action_transport_count=0,
            expected_claim_state="not_applicable",
            expected_evaluator_pass=True,
        ),
        FailureCaseSpec.build(
            case_id="EV007-11",
            failure_family="tampered_model_call_provenance",
            profile="adversarial_evaluator",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_terminal_reason_code="NO_SAFE_PATH",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_claim_state="not_applicable",
            expected_evaluator_pass=False,
        ),
    )
    if [spec.case_id for spec in specs] != sorted(spec.case_id for spec in specs):
        raise AssertionError("EV-007 population must remain case-id sorted")
    return specs


def _build_result(
    *,
    spec: FailureCaseSpec,
    trace: RunTrace,
    evaluation: ProductionEvaluationReport,
    transport_count: int,
    action_transport_count: int,
    claim_state: ClaimExpectation,
    sensitive_markers: tuple[str, ...] = (),
    setup_transport_count: int = 0,
    replay_transport_count: int = 0,
) -> FailureCaseResult:
    final = _final(trace)
    violations = _policy_violations(trace)
    leak_count = _leak_count(trace, sensitive_markers)
    lifecycle_valid = not validate_trace(trace)
    terminal_decision = str(final.get("decision"))
    terminal_reason = final.get("reason_code")
    policy_match = (
        spec.expected_policy_violation is None
        or spec.expected_policy_violation in violations
    )
    expectations_met = all(
        (
            terminal_decision == spec.expected_terminal_decision,
            terminal_reason == spec.expected_terminal_reason_code,
            transport_count == spec.expected_transport_count,
            action_transport_count == spec.expected_action_transport_count,
            policy_match,
            claim_state == spec.expected_claim_state,
            evaluation.passed == spec.expected_evaluator_pass,
            replay_transport_count == spec.expected_replay_transport_count,
            lifecycle_valid,
            leak_count == 0,
        )
    )
    return FailureCaseResult.build(
        case_id=spec.case_id,
        spec_sha256=spec.spec_sha256,
        failure_family=spec.failure_family,
        profile=spec.profile,
        terminal_decision=terminal_decision,
        terminal_reason_code=(None if terminal_reason is None else str(terminal_reason)),
        transport_count=transport_count,
        action_transport_count=action_transport_count,
        setup_transport_count=setup_transport_count,
        replay_transport_count=replay_transport_count,
        policy_violations=violations,
        claim_state=claim_state,
        trace_lifecycle_valid=lifecycle_valid,
        evaluator_pass=evaluation.passed,
        expected_evaluator_pass=spec.expected_evaluator_pass,
        raw_sensitive_leak_count=leak_count,
        automatic_retry_count=0,
        safety_expectations_met=expectations_met,
        trace_sha256=_trace_sha256(trace),
    )


def _run_case(spec: FailureCaseSpec, root: Path) -> FailureCaseResult:
    registry = canonical_tool_registry()

    if spec.case_id == "EV007-01":
        marker = "EV007-PRIVATE-PROVIDER-EXCEPTION"
        client = _ScriptedProviderClient(explode_with=marker)
        transport = _RecordingTransport()
        source = ProviderDecisionSource(
            client=client,
            registry=registry,
            call_identity=_provider_identity(),
            clock_ns=_FixedClock(0, 3_000_000),
        )
        trace = ProductionRuntime(decision_source=source, transport=transport).run(
            _request(spec.case_id)
        )
        evaluation = _traced_evaluator().evaluate(trace)
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=0,
            claim_state="not_applicable",
            sensitive_markers=(marker,),
        )

    if spec.case_id == "EV007-02":
        transport = _RecordingTransport()
        trace = ProductionRuntime(
            decision_source=_MaliciousAuditSource(),
            transport=transport,
        ).run(_request(spec.case_id))
        evaluation = ProductionEvaluator().evaluate(trace)
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=0,
            claim_state="not_applicable",
            sensitive_markers=("EV007-SENSITIVE-AUDIT-PROMPT-MUST-NOT-ENTER-TRACE",),
        )

    if spec.case_id == "EV007-03":
        marker = "EV007-SENSITIVE-MALFORMED-PROVIDER-BODY"
        client = _ScriptedProviderClient(marker)
        transport = _RecordingTransport()
        source = ProviderDecisionSource(
            client=client,
            registry=registry,
            call_identity=_provider_identity(),
            clock_ns=_FixedClock(0, 2_000_000),
        )
        trace = ProductionRuntime(decision_source=source, transport=transport).run(
            _request(spec.case_id)
        )
        evaluation = _traced_evaluator().evaluate(trace)
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=0,
            claim_state="not_applicable",
            sensitive_markers=(marker,),
        )

    if spec.case_id == "EV007-04":
        raw = _provider_json("TOOL", tool_name="ev007_unknown_tool", arguments={})
        client = _ScriptedProviderClient(raw)
        transport = _RecordingTransport()
        source = ProviderDecisionSource(
            client=client,
            registry=registry,
            call_identity=_provider_identity(),
            clock_ns=_FixedClock(0, 2_000_000),
        )
        trace = ProductionRuntime(decision_source=source, transport=transport).run(
            _request(spec.case_id)
        )
        evaluation = _traced_evaluator().evaluate(trace)
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=0,
            claim_state="not_applicable",
            sensitive_markers=(raw,),
        )

    if spec.case_id == "EV007-05":
        transport = _RecordingTransport()
        source = _tool_then_final(tool_name="get_asset", arguments={})
        trace = ProductionRuntime(decision_source=source, transport=transport).run(
            _request(spec.case_id)
        )
        evaluation = ProductionEvaluator().evaluate(trace)
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=0,
            claim_state="not_applicable",
        )

    if spec.case_id == "EV007-06":
        marker = "EV007-PRIVATE-READ-TRANSPORT-EXCEPTION"
        transport = _RecordingTransport(explode_with=marker)
        source = _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-ev007"},
                ),
            )
        )
        trace = ProductionRuntime(decision_source=source, transport=transport).run(
            _request(spec.case_id)
        )
        evaluation = ProductionEvaluator().evaluate(trace)
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=0,
            claim_state="not_applicable",
            sensitive_markers=(marker,),
        )

    if spec.case_id == "EV007-07":
        tool = registry["reprocess_analysis"]
        arguments = _action_arguments()
        key = "ev007-idempotency-auth-denial"
        fingerprint, context = _action_authorization(
            tool=tool,
            arguments=arguments,
            idempotency_key=key,
            confirmed=False,
        )
        claim_store = DurableActionAttemptClaimStore(root / spec.case_id / "claims")
        transport = _RecordingTransport(
            response=TransportResponse(status_code=202, headers={}, body={"accepted": True})
        )
        trace = ControlledActionRuntime(
            decision_source=_tool_then_final(
                tool_name=tool.name,
                arguments=arguments,
            ),
            transport=transport,
            authorization_source=StaticActionAuthorizationSource.from_contexts(
                {fingerprint: context}
            ),
            claim_store=claim_store,
        ).run(_request(spec.case_id))
        evaluation = ControlledActionEvaluator().evaluate(trace)
        claim_state: ClaimExpectation = (
            "claimed" if claim_store.claim_path(key).exists() else "none"
        )
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=len(transport.calls),
            claim_state=claim_state,
        )

    if spec.case_id == "EV007-08":
        tool = registry["reprocess_analysis"]
        arguments = _action_arguments()
        key = "ev007-idempotency-duplicate"
        fingerprint, context = _action_authorization(
            tool=tool,
            arguments=arguments,
            idempotency_key=key,
        )
        claim_store = DurableActionAttemptClaimStore(root / spec.case_id / "claims")
        authorization = StaticActionAuthorizationSource.from_contexts({fingerprint: context})
        setup_transport = _RecordingTransport(
            response=TransportResponse(status_code=202, headers={}, body={"accepted": True})
        )
        ControlledActionRuntime(
            decision_source=_tool_then_final(
                tool_name=tool.name,
                arguments=arguments,
                final_decision=Decision.ACT_REPROCESS.value,
            ),
            transport=setup_transport,
            authorization_source=authorization,
            claim_store=claim_store,
        ).run(_request(f"{spec.case_id}-setup"))

        duplicate_transport = _RecordingTransport(
            response=TransportResponse(status_code=202, headers={}, body={"accepted": True})
        )
        duplicate_trace = ControlledActionRuntime(
            decision_source=_tool_then_final(
                tool_name=tool.name,
                arguments=arguments,
            ),
            transport=duplicate_transport,
            authorization_source=authorization,
            claim_store=DurableActionAttemptClaimStore(root / spec.case_id / "claims"),
        ).run(_request(spec.case_id))
        evaluation = ControlledActionEvaluator().evaluate(duplicate_trace)
        return _build_result(
            spec=spec,
            trace=duplicate_trace,
            evaluation=evaluation,
            transport_count=len(duplicate_transport.calls),
            action_transport_count=len(duplicate_transport.calls),
            setup_transport_count=len(setup_transport.calls),
            claim_state=(
                "existing" if claim_store.claim_path(key).exists() else "none"
            ),
        )

    if spec.case_id == "EV007-09":
        marker = "EV007-PRIVATE-ACTION-TRANSPORT-EXCEPTION"
        tool = registry["reprocess_analysis"]
        arguments = _action_arguments()
        key = "ev007-idempotency-post-claim-failure"
        fingerprint, context = _action_authorization(
            tool=tool,
            arguments=arguments,
            idempotency_key=key,
        )
        claim_root = root / spec.case_id / "claims"
        claim_store = DurableActionAttemptClaimStore(claim_root)
        authorization = StaticActionAuthorizationSource.from_contexts({fingerprint: context})
        failing_transport = _RecordingTransport(explode_with=marker)
        trace = ControlledActionRuntime(
            decision_source=_ScriptedDecisionSource(
                ControllerDecision(
                    kind=ControllerDecisionKind.TOOL,
                    proposal=ToolProposal(tool_name=tool.name, arguments=arguments),
                )
            ),
            transport=failing_transport,
            authorization_source=authorization,
            claim_store=claim_store,
        ).run(_request(spec.case_id))
        evaluation = ControlledActionEvaluator().evaluate(trace)

        replay_transport = _RecordingTransport(
            response=TransportResponse(status_code=202, headers={}, body={"accepted": True})
        )
        ControlledActionRuntime(
            decision_source=_tool_then_final(tool_name=tool.name, arguments=arguments),
            transport=replay_transport,
            authorization_source=authorization,
            claim_store=DurableActionAttemptClaimStore(claim_root),
        ).run(_request(f"{spec.case_id}-replay"))
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(failing_transport.calls),
            action_transport_count=len(failing_transport.calls),
            replay_transport_count=len(replay_transport.calls),
            claim_state=(
                "claimed" if claim_store.claim_path(key).exists() else "none"
            ),
            sensitive_markers=(marker,),
        )

    if spec.case_id == "EV007-10":
        transport = _RecordingTransport(
            response=TransportResponse(
                status_code=503,
                headers={},
                body={"status": "unavailable"},
            )
        )
        source = _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-ev007"},
                ),
            ),
            ControllerDecision(
                kind=ControllerDecisionKind.ESCALATE,
                message="The required source is unavailable; human review is required.",
                reason_code="SOURCE_UNAVAILABLE",
            ),
        )
        trace = ProductionRuntime(decision_source=source, transport=transport).run(
            _request(spec.case_id)
        )
        evaluation = ProductionEvaluator().evaluate(trace)
        return _build_result(
            spec=spec,
            trace=trace,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=0,
            claim_state="not_applicable",
        )

    if spec.case_id == "EV007-11":
        raw = _provider_json(
            "ABSTAIN",
            message="No safe path is available.",
            reason_code="NO_SAFE_PATH",
        )
        client = _ScriptedProviderClient(raw)
        transport = _RecordingTransport()
        source = ProviderDecisionSource(
            client=client,
            registry=registry,
            call_identity=_provider_identity(),
            clock_ns=_FixedClock(0, 1_000_000),
        )
        trace = ProductionRuntime(decision_source=source, transport=transport).run(
            _request(spec.case_id)
        )
        events = list(trace.events)
        index = next(
            i for i, event in enumerate(events) if event.event_type == "model_call"
        )
        events[index] = events[index].model_copy(update={"call_id": "0" * 64})
        tampered = trace.model_copy(update={"events": _resequence(events)})
        evaluation = _traced_evaluator().evaluate(tampered)
        return _build_result(
            spec=spec,
            trace=tampered,
            evaluation=evaluation,
            transport_count=len(transport.calls),
            action_transport_count=0,
            claim_state="not_applicable",
            sensitive_markers=(raw,),
        )

    raise AssertionError(f"unimplemented EV-007 case: {spec.case_id}")


def run_provider_free_failure_campaign(root: Path | str) -> FailureCampaignReport:
    """Execute the exact provider-free EV-007 population and return sanitized evidence only."""

    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)
    results = tuple(_run_case(spec, root_path) for spec in failure_population())
    return FailureCampaignReport.build(results)
