from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)
from research.e2.models import (
    BoundRequest,
    Decision,
    ResponseMode,
    RunTrace,
    ToolKind,
    ToolSpec,
)
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
from .evaluation import ProductionEvaluator
from .runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry


STABILITY_CAMPAIGN_VERSION = "ev008-provider-free-stability-campaign-v1"
STABILITY_UNIT_SCHEMA_VERSION = "ev008-stability-unit-v1"
STABILITY_REPETITION_SCHEMA_VERSION = "ev008-stability-repetition-v1"
STABILITY_SUMMARY_SCHEMA_VERSION = "ev008-stability-summary-v1"
STABILITY_REPORT_SCHEMA_VERSION = "ev008-stability-report-v1"

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
FixtureKind = Literal[
    "read_investigate",
    "clarify",
    "abstain",
    "escalate",
    "controlled_action",
    "safe_failure",
]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


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
    def verify_hash(self) -> "StabilityUnitSpec":
        expected = _canonical_sha256(
            self.model_dump(mode="json", exclude={"spec_sha256"})
        )
        if expected != self.spec_sha256:
            raise ValueError("stability unit spec_sha256 mismatch")
        return self

    @classmethod
    def build(
        cls,
        *,
        unit_id: str,
        fixture_kind: FixtureKind,
        profile: StabilityProfile,
        expected_terminal_decision: str,
        expected_reason_code: str | None,
        expected_transport_count: int,
        expected_action_transport_count: int,
        expected_evaluator_pass: bool,
    ) -> "StabilityUnitSpec":
        payload = {
            "schema_version": STABILITY_UNIT_SCHEMA_VERSION,
            "campaign_version": STABILITY_CAMPAIGN_VERSION,
            "unit_id": unit_id,
            "fixture_kind": fixture_kind,
            "profile": profile,
            "repetitions": STABILITY_REPETITIONS_PER_UNIT,
            "expected_terminal_decision": expected_terminal_decision,
            "expected_reason_code": expected_reason_code,
            "expected_transport_count": expected_transport_count,
            "expected_action_transport_count": expected_action_transport_count,
            "expected_evaluator_pass": expected_evaluator_pass,
        }
        return cls(**payload, spec_sha256=_canonical_sha256(payload))


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
    def verify_hash(self) -> "StabilityRepetitionResult":
        expected = _canonical_sha256(
            self.model_dump(mode="json", exclude={"result_sha256"})
        )
        if expected != self.result_sha256:
            raise ValueError("stability repetition result_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "StabilityRepetitionResult":
        payload = {
            "schema_version": STABILITY_REPETITION_SCHEMA_VERSION,
            "campaign_version": STABILITY_CAMPAIGN_VERSION,
            **kwargs,
        }
        return cls(**payload, result_sha256=_canonical_sha256(payload))


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
    def verify_summary(self) -> "StabilityUnitSummary":
        if set(self.stable_dimensions) & set(self.unstable_dimensions):
            raise ValueError("stability dimensions cannot be both stable and unstable")
        if set(self.stable_dimensions) | set(self.unstable_dimensions) != set(STABILITY_DIMENSIONS):
            raise ValueError("stability summary dimensions do not match preregistered dimensions")
        if self.all_dimensions_stable != (len(self.unstable_dimensions) == 0):
            raise ValueError("all_dimensions_stable mismatch")
        expected = _canonical_sha256(
            self.model_dump(mode="json", exclude={"summary_sha256"})
        )
        if expected != self.summary_sha256:
            raise ValueError("stability summary_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "StabilityUnitSummary":
        payload = {
            "schema_version": STABILITY_SUMMARY_SCHEMA_VERSION,
            "campaign_version": STABILITY_CAMPAIGN_VERSION,
            **kwargs,
        }
        return cls(**payload, summary_sha256=_canonical_sha256(payload))


class StabilityCampaignReport(_FrozenModel):
    schema_version: Literal["ev008-stability-report-v1"]
    campaign_version: Literal["ev008-provider-free-stability-campaign-v1"]
    unit_count: Literal[6]
    repetitions_per_unit: Literal[5]
    denominator: Literal[30]
    stable_unit_count: int = Field(ge=0, le=6)
    stable_dimension_checks: int = Field(ge=0)
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
    def verify_report(self) -> "StabilityCampaignReport":
        if len(self.repetitions) != self.denominator:
            raise ValueError("stability campaign repetition denominator mismatch")
        if len(self.summaries) != self.unit_count:
            raise ValueError("stability campaign unit denominator mismatch")
        if self.stable_unit_count != sum(
            1 for summary in self.summaries if summary.all_dimensions_stable
        ):
            raise ValueError("stable_unit_count mismatch")
        if self.stable_dimension_checks != sum(
            len(summary.stable_dimensions) for summary in self.summaries
        ):
            raise ValueError("stable_dimension_checks mismatch")
        if self.contract_expectations_passed != sum(
            1 for result in self.repetitions if result.contract_expectations_met
        ):
            raise ValueError("contract_expectations_passed mismatch")
        if self.sensitive_leak_count != sum(
            result.sensitive_leak_count for result in self.repetitions
        ):
            raise ValueError("sensitive_leak_count mismatch")
        if [summary.unit_id for summary in self.summaries] != sorted(
            summary.unit_id for summary in self.summaries
        ):
            raise ValueError("stability summaries must be unit-id sorted")
        expected_order = [
            (f"STAB-0{unit}", repetition)
            for unit in range(1, 7)
            for repetition in range(1, STABILITY_REPETITIONS_PER_UNIT + 1)
        ]
        if [(result.unit_id, result.repetition) for result in self.repetitions] != expected_order:
            raise ValueError("stability repetitions must use exact unit/repetition order")
        expected = _canonical_sha256(
            self.model_dump(mode="json", exclude={"report_sha256"})
        )
        if expected != self.report_sha256:
            raise ValueError("stability report_sha256 mismatch")
        return self

    @classmethod
    def build(
        cls,
        *,
        repetitions: tuple[StabilityRepetitionResult, ...],
        summaries: tuple[StabilityUnitSummary, ...],
    ) -> "StabilityCampaignReport":
        payload = {
            "schema_version": STABILITY_REPORT_SCHEMA_VERSION,
            "campaign_version": STABILITY_CAMPAIGN_VERSION,
            "unit_count": 6,
            "repetitions_per_unit": STABILITY_REPETITIONS_PER_UNIT,
            "denominator": 30,
            "stable_unit_count": sum(
                1 for summary in summaries if summary.all_dimensions_stable
            ),
            "stable_dimension_checks": sum(
                len(summary.stable_dimensions) for summary in summaries
            ),
            "total_dimension_checks": len(STABILITY_DIMENSIONS) * 6,
            "contract_expectations_passed": sum(
                1 for result in repetitions if result.contract_expectations_met
            ),
            "sensitive_leak_count": sum(
                result.sensitive_leak_count for result in repetitions
            ),
            "automatic_retry_count": 0,
            "replay_count": 0,
            "provider_calls": 0,
            "real_customer_mutations": 0,
            "repetitions": [
                result.model_dump(mode="json") for result in repetitions
            ],
            "summaries": [
                summary.model_dump(mode="json") for summary in summaries
            ],
        }
        return cls(**payload, report_sha256=_canonical_sha256(payload))


class _ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)

    def decide(self, context: ControllerContext) -> ControllerDecision:
        if not self.decisions:
            raise AssertionError("EV-008 scripted decision source exhausted")
        return self.decisions.pop(0)


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
            body={"asset_id": "asset-stability", "status": "ok"},
        )
        self.explode_with = explode_with
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        if self.explode_with is not None:
            raise RuntimeError(self.explode_with)
        return self.response


def stability_population() -> tuple[StabilityUnitSpec, ...]:
    return (
        StabilityUnitSpec.build(
            unit_id="STAB-01",
            fixture_kind="read_investigate",
            profile="read_only",
            expected_terminal_decision=Decision.ORIENT.value,
            expected_reason_code=None,
            expected_transport_count=1,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
        StabilityUnitSpec.build(
            unit_id="STAB-02",
            fixture_kind="clarify",
            profile="read_only",
            expected_terminal_decision=Decision.ASK_CLARIFICATION.value,
            expected_reason_code="MISSING_CONTEXT",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
        StabilityUnitSpec.build(
            unit_id="STAB-03",
            fixture_kind="abstain",
            profile="read_only",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_reason_code="NO_SAFE_PATH",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
        StabilityUnitSpec.build(
            unit_id="STAB-04",
            fixture_kind="escalate",
            profile="read_only",
            expected_terminal_decision=Decision.ESCALATE_HUMAN.value,
            expected_reason_code="HUMAN_REVIEW_REQUIRED",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
        StabilityUnitSpec.build(
            unit_id="STAB-05",
            fixture_kind="controlled_action",
            profile="controlled_action",
            expected_terminal_decision=Decision.ACT_REPROCESS.value,
            expected_reason_code=None,
            expected_transport_count=1,
            expected_action_transport_count=1,
            expected_evaluator_pass=True,
        ),
        StabilityUnitSpec.build(
            unit_id="STAB-06",
            fixture_kind="safe_failure",
            profile="read_only",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_reason_code="TOOL_BOUNDARY_FAILURE",
            expected_transport_count=1,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
    )


def _final_payload(*, decision: str, message: str) -> dict[str, Any]:
    return {
        "decision": decision,
        "response_mode": ResponseMode.COMPLETE.value,
        "message": message,
    }


def _action_arguments() -> dict[str, Any]:
    return {
        "analysis_id": "analysis-stability",
        "body": {
            "justification": (
                "EV-008 explicit requester confirmation authorizes this exact synthetic "
                "reprocessing action for repeated-run stability testing."
            )
        },
    }


def _source_for(spec: StabilityUnitSpec) -> _ScriptedDecisionSource:
    if spec.fixture_kind == "read_investigate":
        return _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-stability"},
                ),
            ),
            ControllerDecision(
                kind=ControllerDecisionKind.FINAL,
                final=_final_payload(
                    decision=Decision.ORIENT.value,
                    message="The asset state is stable and no mutation is required.",
                ),
            ),
        )
    if spec.fixture_kind == "clarify":
        return _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.CLARIFY,
                message="Additional asset context is required before proceeding.",
                reason_code="MISSING_CONTEXT",
            )
        )
    if spec.fixture_kind == "abstain":
        return _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.ABSTAIN,
                message="No safe deterministic path is available.",
                reason_code="NO_SAFE_PATH",
            )
        )
    if spec.fixture_kind == "escalate":
        return _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.ESCALATE,
                message="Human review is required for this deterministic case.",
                reason_code="HUMAN_REVIEW_REQUIRED",
            )
        )
    if spec.fixture_kind == "controlled_action":
        return _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="reprocess_analysis",
                    arguments=_action_arguments(),
                ),
            ),
            ControllerDecision(
                kind=ControllerDecisionKind.FINAL,
                final=_final_payload(
                    decision=Decision.ACT_REPROCESS.value,
                    message="The authorized synthetic reprocessing request was accepted.",
                ),
            ),
        )
    if spec.fixture_kind == "safe_failure":
        return _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-stability"},
                ),
            )
        )
    raise AssertionError(f"unsupported EV-008 fixture kind: {spec.fixture_kind}")


def _action_authorization(
    *,
    tool: ToolSpec,
    arguments: Mapping[str, Any],
) -> tuple[str, ProductionActionAuthorizationContext]:
    fingerprint = action_fingerprint(tool, dict(arguments))
    context = ProductionActionAuthorizationContext(
        execution_enabled=True,
        user_permissions=frozenset(tool.required_permissions),
        user_company_id="company-stability",
        resource_company_bindings=(
            ResourceCompanyBinding(
                resource_id=str(arguments["analysis_id"]),
                company_id="company-stability",
            ),
        ),
        confirmed_action_fingerprints=frozenset({fingerprint}),
        idempotency_bindings=(
            ActionIdempotencyBinding(
                action_fingerprint=fingerprint,
                idempotency_key="ev008-stability-action-idempotency",
            ),
        ),
    )
    return fingerprint, context


def _request(spec: StabilityUnitSpec, repetition: int) -> ProductionRequest:
    return ProductionRequest(
        request_id=f"ev008-{spec.unit_id.lower()}-r{repetition}",
        identity_id="ev008-identity",
        user_id="ev008-user",
        user_request=f"Execute deterministic stability fixture {spec.fixture_kind}.",
        seed="ev008-fixed-seed",
    )


def _final(trace: RunTrace) -> dict[str, Any]:
    finals = [
        event.result
        for event in trace.events
        if event.event_type == "final_response" and isinstance(event.result, dict)
    ]
    if len(finals) != 1:
        raise ValueError("EV-008 trace must contain exactly one object final_response")
    return dict(finals[0])


def _normalized_trace_payload(trace: RunTrace) -> dict[str, Any]:
    # Only per-execution top-level identity is excluded. Behavioral content stays intact.
    return {
        "config_hash": trace.config_hash,
        "identity_binding_id": trace.identity_binding_id,
        "seed_ref": trace.seed_ref,
        "events": [event.model_dump(mode="json") for event in trace.events],
    }


def _tool_calls(trace: RunTrace) -> tuple[Any, ...]:
    return tuple(event for event in trace.events if event.event_type == "tool_call")


def _policy_outcomes(trace: RunTrace) -> tuple[str, ...]:
    outcomes: list[str] = []
    for event in trace.events:
        if event.event_type != "policy_check":
            continue
        outcomes.append(
            json.dumps(
                {
                    "sequence": event.sequence,
                    "tool_name": event.tool_name,
                    "stage": event.metadata.get("stage"),
                    "allowed": event.metadata.get("allowed"),
                    "violation": event.metadata.get("violation"),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    return tuple(outcomes)


def _arguments_signature(trace: RunTrace) -> str:
    return _canonical_sha256(
        [
            {"tool_name": event.tool_name, "arguments": event.arguments}
            for event in _tool_calls(trace)
        ]
    )


def _action_fingerprint_signature(
    trace: RunTrace,
    registry: Mapping[str, ToolSpec],
) -> str:
    fingerprints: list[str] = []
    for event in _tool_calls(trace):
        if event.tool_name in registry and registry[event.tool_name].kind is ToolKind.ACTION:
            fingerprints.append(
                action_fingerprint(
                    registry[event.tool_name],
                    dict(event.arguments or {}),
                )
            )
    return _canonical_sha256(fingerprints)


def _count_action_transports(
    transport: _RecordingTransport,
    registry: Mapping[str, ToolSpec],
) -> int:
    action_operation_ids = {
        tool.operation_id for tool in registry.values() if tool.kind is ToolKind.ACTION
    }
    return sum(1 for call in transport.calls if call.operation_id in action_operation_ids)


def _leak_count(trace: RunTrace) -> int:
    serialized = trace.model_dump_json()
    markers = (
        "EV008-SENSITIVE-BACKEND-EXCEPTION",
        "ev008-secret-token",
        "Authorization: Bearer",
    )
    return sum(serialized.count(marker) for marker in markers)


def _execute_repetition(
    *,
    spec: StabilityUnitSpec,
    repetition: int,
    root: Path,
) -> StabilityRepetitionResult:
    registry = canonical_tool_registry()
    source = _source_for(spec)

    if spec.fixture_kind == "safe_failure":
        transport = _RecordingTransport(explode_with="EV008-SENSITIVE-BACKEND-EXCEPTION")
    elif spec.fixture_kind == "controlled_action":
        transport = _RecordingTransport(
            response=TransportResponse(
                status_code=202,
                headers={},
                body={"accepted": True},
            )
        )
    else:
        transport = _RecordingTransport()

    if spec.profile == "controlled_action":
        action_tool = registry["reprocess_analysis"]
        fingerprint, context = _action_authorization(
            tool=action_tool,
            arguments=_action_arguments(),
        )
        runtime = ControlledActionRuntime(
            decision_source=source,
            transport=transport,
            authorization_source=StaticActionAuthorizationSource.from_contexts(
                {fingerprint: context}
            ),
            claim_store=DurableActionAttemptClaimStore(
                root / spec.unit_id / f"rep-{repetition}" / "claims"
            ),
            registry=registry,
        )
        trace = runtime.run(_request(spec, repetition))
        evaluation = ControlledActionEvaluator(registry=registry).evaluate(trace)
    else:
        runtime = ProductionRuntime(
            decision_source=source,
            transport=transport,
            registry=registry,
        )
        trace = runtime.run(_request(spec, repetition))
        evaluation = ProductionEvaluator(registry=registry).evaluate(trace)

    final = _final(trace)
    terminal_decision = str(final.get("decision"))
    terminal_reason_code = None if final.get("reason_code") is None else str(final.get("reason_code"))
    tool_calls = _tool_calls(trace)
    tool_sequence = tuple(str(event.tool_name) for event in tool_calls)
    policy_outcomes = _policy_outcomes(trace)
    action_transport_count = _count_action_transports(transport, registry)
    leak_count = _leak_count(trace)
    trace_lifecycle_valid = not validate_trace(trace)

    terminal_signature = _canonical_sha256(
        {
            "decision": terminal_decision,
            "controller_decision": final.get("controller_decision"),
            "response_mode": final.get("response_mode"),
        }
    )
    tool_selection = _canonical_sha256(tool_sequence)
    arguments = _arguments_signature(trace)
    action_fingerprints = _action_fingerprint_signature(trace, registry)
    policies = _canonical_sha256(policy_outcomes)
    evaluator_classification = _canonical_sha256({"passed": evaluation.passed})
    reason_code = _canonical_sha256(terminal_reason_code)
    behavioral_trace = _canonical_sha256(_normalized_trace_payload(trace))
    final_response = _canonical_sha256(final)

    contract_expectations_met = all(
        (
            terminal_decision == spec.expected_terminal_decision,
            terminal_reason_code == spec.expected_reason_code,
            len(transport.calls) == spec.expected_transport_count,
            action_transport_count == spec.expected_action_transport_count,
            evaluation.passed == spec.expected_evaluator_pass,
            trace_lifecycle_valid,
            leak_count == 0,
        )
    )

    return StabilityRepetitionResult.build(
        unit_id=spec.unit_id,
        repetition=repetition,
        spec_sha256=spec.spec_sha256,
        terminal_decision=terminal_decision,
        terminal_reason_code=terminal_reason_code,
        tool_sequence=tool_sequence,
        policy_outcomes=policy_outcomes,
        terminal_signature_sha256=terminal_signature,
        tool_selection_sha256=tool_selection,
        canonical_arguments_sha256=arguments,
        action_fingerprint_sha256=action_fingerprints,
        policy_outcomes_sha256=policies,
        evaluator_classification_sha256=evaluator_classification,
        reason_code_sha256=reason_code,
        behavioral_trace_sha256=behavioral_trace,
        final_response_sha256=final_response,
        sensitive_leak_count=leak_count,
        automatic_retry_count=0,
        replay_count=0,
        transport_count=len(transport.calls),
        action_transport_count=action_transport_count,
        evaluator_pass=evaluation.passed,
        trace_lifecycle_valid=trace_lifecycle_valid,
        contract_expectations_met=contract_expectations_met,
    )


def _dimension_values(
    results: tuple[StabilityRepetitionResult, ...],
) -> dict[str, tuple[Any, ...]]:
    return {
        "terminal_signature": tuple(result.terminal_signature_sha256 for result in results),
        "tool_selection": tuple(result.tool_selection_sha256 for result in results),
        "canonical_arguments": tuple(result.canonical_arguments_sha256 for result in results),
        "action_fingerprint": tuple(result.action_fingerprint_sha256 for result in results),
        "policy_outcomes": tuple(result.policy_outcomes_sha256 for result in results),
        "evaluator_classification": tuple(result.evaluator_classification_sha256 for result in results),
        "reason_code": tuple(result.reason_code_sha256 for result in results),
        "behavioral_trace": tuple(result.behavioral_trace_sha256 for result in results),
        "final_response": tuple(result.final_response_sha256 for result in results),
        "sensitive_leak_count": tuple(result.sensitive_leak_count for result in results),
        "retry_replay_count": tuple(
            (result.automatic_retry_count, result.replay_count) for result in results
        ),
    }


def summarize_stability_unit(
    spec: StabilityUnitSpec,
    results: tuple[StabilityRepetitionResult, ...],
) -> StabilityUnitSummary:
    if len(results) != STABILITY_REPETITIONS_PER_UNIT:
        raise ValueError("EV-008 unit must have exactly five repetitions")
    dimensions = _dimension_values(results)
    stable = tuple(
        name for name in STABILITY_DIMENSIONS if len(set(dimensions[name])) == 1
    )
    unstable = tuple(name for name in STABILITY_DIMENSIONS if name not in stable)
    return StabilityUnitSummary.build(
        unit_id=spec.unit_id,
        spec_sha256=spec.spec_sha256,
        repetitions=STABILITY_REPETITIONS_PER_UNIT,
        stable_dimensions=stable,
        unstable_dimensions=unstable,
        all_dimensions_stable=not unstable,
        contract_expectations_passed=sum(
            1 for result in results if result.contract_expectations_met
        ),
        evaluator_pass_count=sum(1 for result in results if result.evaluator_pass),
        sensitive_leak_count=sum(result.sensitive_leak_count for result in results),
        transport_count=sum(result.transport_count for result in results),
        action_transport_count=sum(result.action_transport_count for result in results),
    )


def run_provider_free_stability_campaign(root: Path | str) -> StabilityCampaignReport:
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)

    all_results: list[StabilityRepetitionResult] = []
    summaries: list[StabilityUnitSummary] = []

    for spec in stability_population():
        unit_results = tuple(
            _execute_repetition(
                spec=spec,
                repetition=repetition,
                root=root_path,
            )
            for repetition in range(1, STABILITY_REPETITIONS_PER_UNIT + 1)
        )
        all_results.extend(unit_results)
        summaries.append(summarize_stability_unit(spec, unit_results))

    return StabilityCampaignReport.build(
        repetitions=tuple(all_results),
        summaries=tuple(summaries),
    )
