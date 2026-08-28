from __future__ import annotations

from hashlib import sha1, sha256
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
from .controlled_actions import (
    ControlledActionRuntime,
    DurableActionAttemptClaimStore,
    StaticActionAuthorizationSource,
)
from .evaluation import ProductionEvaluator
from .runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry


DELIVERY_CAMPAIGN_VERSION = "provider-free-final-delivery-reproduction-v1"
DEMO_SCENARIO_SCHEMA_VERSION = "delivery-demo-scenario-v1"
DEMO_RESULT_SCHEMA_VERSION = "delivery-demo-result-v1"
DEMO_REPORT_SCHEMA_VERSION = "delivery-demo-report-v1"
EVIDENCE_INDEX_SCHEMA_VERSION = "delivery-evidence-index-v1"

DemoProfile = Literal["read_only", "controlled_action"]
DemoKind = Literal["read_investigate", "clarify", "abstain", "escalate", "controlled_action"]
EvidenceCategory = Literal[
    "adr",
    "freeze",
    "result",
    "validator",
    "workflow",
    "demo",
    "provider_plan",
    "scientific_blocker",
]
ReproductionStatus = Literal[
    "PROVIDER_FREE_REPRODUCIBLE",
    "HISTORICAL_IMMUTABLE",
    "EXTERNALLY_BLOCKED",
    "UNEXECUTED_GATED",
]

EXPECTED_EV007_REPORT_SHA256 = "7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9"
EXPECTED_EV008_REPORT_SHA256 = "1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8"
EXPECTED_EV011_REPORT_SHA256 = "cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e"
EXPECTED_PROVIDER_PLAN_SHA256 = "69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f"
EXPECTED_C4_ARTIFACT_SHA256 = "b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c"
EXPECTED_C4_ARTIFACT_BYTES = 177350
EXPECTED_C4_ARTIFACT_ROWS = 144


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def git_blob_sha1(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return sha1(header + content).hexdigest()


class DemoScenarioSpec(_FrozenModel):
    schema_version: Literal["delivery-demo-scenario-v1"] = DEMO_SCENARIO_SCHEMA_VERSION
    campaign_version: Literal["provider-free-final-delivery-reproduction-v1"] = DELIVERY_CAMPAIGN_VERSION
    scenario_id: str = Field(pattern=r"^DEMO-0[1-5]$")
    fixture_kind: DemoKind
    profile: DemoProfile
    expected_terminal_decision: str
    expected_reason_code: str | None = None
    expected_transport_count: int = Field(ge=0)
    expected_action_transport_count: int = Field(ge=0)
    expected_evaluator_pass: bool
    spec_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_hash(self) -> "DemoScenarioSpec":
        expected = canonical_sha256(self.model_dump(mode="json", exclude={"spec_sha256"}))
        if self.spec_sha256 != expected:
            raise ValueError("delivery demo spec_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "DemoScenarioSpec":
        payload = {
            "schema_version": DEMO_SCENARIO_SCHEMA_VERSION,
            "campaign_version": DELIVERY_CAMPAIGN_VERSION,
            **kwargs,
        }
        return cls(**payload, spec_sha256=canonical_sha256(payload))


class DemoScenarioResult(_FrozenModel):
    schema_version: Literal["delivery-demo-result-v1"] = DEMO_RESULT_SCHEMA_VERSION
    campaign_version: Literal["provider-free-final-delivery-reproduction-v1"] = DELIVERY_CAMPAIGN_VERSION
    scenario_id: str = Field(pattern=r"^DEMO-0[1-5]$")
    spec_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    terminal_decision: str
    terminal_reason_code: str | None = None
    tool_selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    canonical_arguments_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_outcomes_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    action_fingerprint_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evaluator_pass: bool
    behavioral_trace_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    trace_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    transport_count: int = Field(ge=0)
    action_transport_count: int = Field(ge=0)
    durable_claim_count: int = Field(ge=0)
    trace_lifecycle_valid: bool
    contract_expectations_met: bool
    result_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_hash(self) -> "DemoScenarioResult":
        expected = canonical_sha256(self.model_dump(mode="json", exclude={"result_sha256"}))
        if self.result_sha256 != expected:
            raise ValueError("delivery demo result_sha256 mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "DemoScenarioResult":
        payload = {
            "schema_version": DEMO_RESULT_SCHEMA_VERSION,
            "campaign_version": DELIVERY_CAMPAIGN_VERSION,
            **kwargs,
        }
        return cls(**payload, result_sha256=canonical_sha256(payload))


class DeliveryDemoReport(_FrozenModel):
    schema_version: Literal["delivery-demo-report-v1"] = DEMO_REPORT_SCHEMA_VERSION
    campaign_version: Literal["provider-free-final-delivery-reproduction-v1"] = DELIVERY_CAMPAIGN_VERSION
    denominator: Literal[5] = 5
    exact_traces_evaluated: int = Field(ge=0, le=5)
    contract_expectations_passed: int = Field(ge=0, le=5)
    provider_calls: Literal[0] = 0
    credential_account_probes: Literal[0] = 0
    real_customer_mutations: Literal[0] = 0
    semantic_private_blind_access: Literal[0] = 0
    automatic_retry_count: Literal[0] = 0
    replay_count: Literal[0] = 0
    results: tuple[DemoScenarioResult, ...]
    report_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_report(self) -> "DeliveryDemoReport":
        if len(self.results) != 5:
            raise ValueError("delivery demo denominator mismatch")
        if [result.scenario_id for result in self.results] != [f"DEMO-0{i}" for i in range(1, 6)]:
            raise ValueError("delivery demo result order mismatch")
        if self.exact_traces_evaluated != len(self.results):
            raise ValueError("exact_traces_evaluated mismatch")
        if self.contract_expectations_passed != sum(result.contract_expectations_met for result in self.results):
            raise ValueError("contract_expectations_passed mismatch")
        expected = canonical_sha256(self.model_dump(mode="json", exclude={"report_sha256"}))
        if self.report_sha256 != expected:
            raise ValueError("delivery demo report_sha256 mismatch")
        return self

    @classmethod
    def build(cls, results: tuple[DemoScenarioResult, ...]) -> "DeliveryDemoReport":
        payload = {
            "schema_version": DEMO_REPORT_SCHEMA_VERSION,
            "campaign_version": DELIVERY_CAMPAIGN_VERSION,
            "denominator": 5,
            "exact_traces_evaluated": len(results),
            "contract_expectations_passed": sum(result.contract_expectations_met for result in results),
            "provider_calls": 0,
            "credential_account_probes": 0,
            "real_customer_mutations": 0,
            "semantic_private_blind_access": 0,
            "automatic_retry_count": 0,
            "replay_count": 0,
            "results": [result.model_dump(mode="json") for result in results],
        }
        return cls(**payload, report_sha256=canonical_sha256(payload))


class EvidenceEntry(_FrozenModel):
    evidence_id: str = Field(min_length=1)
    category: EvidenceCategory
    title: str = Field(min_length=1)
    repository_path: str | None = None
    git_blob_sha1: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    canonical_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    issue_number: int | None = Field(default=None, ge=1)
    pull_request_number: int | None = Field(default=None, ge=1)
    adr_number: int | None = Field(default=None, ge=1)
    reproduction_status: ReproductionStatus
    authorization_boundary: str = Field(min_length=1)

    @model_validator(mode="after")
    def verify_location_contract(self) -> "EvidenceEntry":
        if self.repository_path is None and self.git_blob_sha1 is not None:
            raise ValueError("external evidence cannot declare a repository blob")
        if self.repository_path is not None and self.git_blob_sha1 is None:
            raise ValueError("repository-resident evidence must declare its Git blob SHA-1")
        return self


class EvidenceIndex(_FrozenModel):
    schema_version: Literal["delivery-evidence-index-v1"] = EVIDENCE_INDEX_SCHEMA_VERSION
    entries: tuple[EvidenceEntry, ...]

    @model_validator(mode="after")
    def verify_unique_ids(self) -> "EvidenceIndex":
        ids = [entry.evidence_id for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence_id values must be unique")
        if ids != sorted(ids):
            raise ValueError("evidence index entries must be evidence-id sorted")
        return self


class EvidenceIndexValidation(_FrozenModel):
    entry_count: int = Field(ge=1)
    repository_resident_count: int = Field(ge=0)
    resolved_repository_entries: int = Field(ge=0)
    violations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations and self.repository_resident_count == self.resolved_repository_entries


class _ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)

    def decide(self, context: ControllerContext) -> ControllerDecision:
        if not self.decisions:
            raise AssertionError("delivery demo decision source exhausted")
        return self.decisions.pop(0)


class _RecordingTransport(RequestTransport):
    def __init__(self, *, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return self.response


def demo_population() -> tuple[DemoScenarioSpec, ...]:
    build = DemoScenarioSpec.build
    return (
        build(
            scenario_id="DEMO-01",
            fixture_kind="read_investigate",
            profile="read_only",
            expected_terminal_decision=Decision.ORIENT.value,
            expected_reason_code=None,
            expected_transport_count=1,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
        build(
            scenario_id="DEMO-02",
            fixture_kind="clarify",
            profile="read_only",
            expected_terminal_decision=Decision.ASK_CLARIFICATION.value,
            expected_reason_code="MISSING_CONTEXT",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
        build(
            scenario_id="DEMO-03",
            fixture_kind="abstain",
            profile="read_only",
            expected_terminal_decision=Decision.ABSTAIN.value,
            expected_reason_code="NO_SAFE_PATH",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
        build(
            scenario_id="DEMO-04",
            fixture_kind="escalate",
            profile="read_only",
            expected_terminal_decision=Decision.ESCALATE_HUMAN.value,
            expected_reason_code="HUMAN_REVIEW_REQUIRED",
            expected_transport_count=0,
            expected_action_transport_count=0,
            expected_evaluator_pass=True,
        ),
        build(
            scenario_id="DEMO-05",
            fixture_kind="controlled_action",
            profile="controlled_action",
            expected_terminal_decision=Decision.ACT_REPROCESS.value,
            expected_reason_code=None,
            expected_transport_count=1,
            expected_action_transport_count=1,
            expected_evaluator_pass=True,
        ),
    )


def _action_arguments() -> dict[str, Any]:
    return {
        "analysis_id": "analysis-delivery-demo",
        "body": {
            "justification": (
                "Issue 57 preregistered this exact synthetic reprocessing action for the "
                "provider-free final-delivery demonstration."
            )
        },
    }


def _final_decision(decision: str, message: str) -> ControllerDecision:
    return ControllerDecision(
        kind=ControllerDecisionKind.FINAL,
        final={
            "decision": decision,
            "response_mode": ResponseMode.COMPLETE.value,
            "message": message,
        },
    )


def _source(spec: DemoScenarioSpec) -> _ScriptedDecisionSource:
    if spec.fixture_kind == "read_investigate":
        return _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-delivery-demo"},
                ),
            ),
            _final_decision(
                Decision.ORIENT.value,
                "The supplied asset evidence was read successfully; no mutation is required.",
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
                message="No safe deterministic path is available for this supplied request.",
                reason_code="NO_SAFE_PATH",
            )
        )
    if spec.fixture_kind == "escalate":
        return _ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.ESCALATE,
                message="Human review is required for this supplied request.",
                reason_code="HUMAN_REVIEW_REQUIRED",
            )
        )
    return _ScriptedDecisionSource(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="reprocess_analysis",
                arguments=_action_arguments(),
            ),
        ),
        _final_decision(
            Decision.ACT_REPROCESS.value,
            "The explicitly authorized synthetic reprocessing request was accepted.",
        ),
    )


def _request(spec: DemoScenarioSpec) -> ProductionRequest:
    return ProductionRequest(
        request_id=f"delivery-{spec.scenario_id.lower()}",
        identity_id="delivery-demo-identity",
        user_id="delivery-demo-user",
        user_request=f"Execute preregistered final-delivery fixture {spec.fixture_kind}.",
        seed="delivery-demo-fixed-seed",
    )


def _action_authorization(tool: ToolSpec) -> tuple[str, ProductionActionAuthorizationContext]:
    arguments = _action_arguments()
    fingerprint = action_fingerprint(tool, arguments)
    context = ProductionActionAuthorizationContext(
        execution_enabled=True,
        user_permissions=frozenset(tool.required_permissions),
        user_company_id="company-delivery-demo",
        resource_company_bindings=(
            ResourceCompanyBinding(
                resource_id="analysis-delivery-demo",
                company_id="company-delivery-demo",
            ),
        ),
        confirmed_action_fingerprints=frozenset({fingerprint}),
        idempotency_bindings=(
            ActionIdempotencyBinding(
                action_fingerprint=fingerprint,
                idempotency_key="delivery-demo-action-idempotency",
            ),
        ),
    )
    return fingerprint, context


def _final_payload(trace: RunTrace) -> dict[str, Any]:
    finals = [
        event.result
        for event in trace.events
        if event.event_type == "final_response" and isinstance(event.result, dict)
    ]
    if len(finals) != 1:
        raise ValueError("delivery demo trace must contain exactly one object final_response")
    return dict(finals[0])


def _tool_calls(trace: RunTrace) -> tuple[Any, ...]:
    return tuple(event for event in trace.events if event.event_type == "tool_call")


def _policy_outcomes(trace: RunTrace) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "sequence": event.sequence,
            "tool_name": event.tool_name,
            "stage": event.metadata.get("stage"),
            "allowed": event.metadata.get("allowed"),
            "violation": event.metadata.get("violation"),
        }
        for event in trace.events
        if event.event_type == "policy_check"
    )


def _normalized_behavioral_trace_sha256(trace: RunTrace) -> str:
    return canonical_sha256(
        {
            "config_hash": trace.config_hash,
            "identity_binding_id": trace.identity_binding_id,
            "seed_ref": trace.seed_ref,
            "events": [event.model_dump(mode="json") for event in trace.events],
        }
    )


def _trace_sha256(trace: RunTrace) -> str:
    return canonical_sha256(trace.model_dump(mode="json"))


def _action_fingerprint_signature(
    trace: RunTrace,
    registry: Mapping[str, ToolSpec],
) -> str:
    values: list[str] = []
    for event in _tool_calls(trace):
        if event.tool_name in registry and registry[event.tool_name].kind is ToolKind.ACTION:
            values.append(
                action_fingerprint(
                    registry[event.tool_name],
                    dict(event.arguments or {}),
                )
            )
    return canonical_sha256(values)


def _execute_demo_scenario(
    spec: DemoScenarioSpec,
    root: Path,
) -> DemoScenarioResult:
    registry = canonical_tool_registry()
    if spec.profile == "controlled_action":
        transport = _RecordingTransport(
            response=TransportResponse(status_code=202, headers={}, body={"accepted": True})
        )
        fingerprint, context = _action_authorization(registry["reprocess_analysis"])
        claim_root = root / spec.scenario_id / "claims"
        runtime = ControlledActionRuntime(
            decision_source=_source(spec),
            transport=transport,
            authorization_source=StaticActionAuthorizationSource.from_contexts(
                {fingerprint: context}
            ),
            claim_store=DurableActionAttemptClaimStore(claim_root),
            registry=registry,
        )
        trace = runtime.run(_request(spec))
        evaluation = ControlledActionEvaluator(registry=registry).evaluate(trace)
        durable_claim_count = len(list(claim_root.glob("*.json")))
        action_transport_count = len(transport.calls)
    else:
        transport = _RecordingTransport(
            response=TransportResponse(
                status_code=200,
                headers={},
                body={"asset_id": "asset-delivery-demo", "status": "ok"},
            )
        )
        runtime = ProductionRuntime(
            decision_source=_source(spec),
            transport=transport,
            registry=registry,
        )
        trace = runtime.run(_request(spec))
        evaluation = ProductionEvaluator(registry=registry).evaluate(trace)
        durable_claim_count = 0
        action_transport_count = 0

    final = _final_payload(trace)
    terminal_decision = str(final.get("decision"))
    reason_code = None if final.get("reason_code") is None else str(final.get("reason_code"))
    tool_calls = _tool_calls(trace)
    tool_selection = tuple(str(event.tool_name) for event in tool_calls)
    argument_records = tuple(
        {"tool_name": event.tool_name, "arguments": event.arguments}
        for event in tool_calls
    )
    policies = _policy_outcomes(trace)
    lifecycle_valid = not validate_trace(trace)
    contract = all(
        (
            terminal_decision == spec.expected_terminal_decision,
            reason_code == spec.expected_reason_code,
            len(transport.calls) == spec.expected_transport_count,
            action_transport_count == spec.expected_action_transport_count,
            evaluation.passed == spec.expected_evaluator_pass,
            lifecycle_valid,
            durable_claim_count == (1 if spec.profile == "controlled_action" else 0),
        )
    )

    return DemoScenarioResult.build(
        scenario_id=spec.scenario_id,
        spec_sha256=spec.spec_sha256,
        terminal_decision=terminal_decision,
        terminal_reason_code=reason_code,
        tool_selection_sha256=canonical_sha256(tool_selection),
        canonical_arguments_sha256=canonical_sha256(argument_records),
        policy_outcomes_sha256=canonical_sha256(policies),
        action_fingerprint_sha256=_action_fingerprint_signature(trace, registry),
        evaluator_pass=evaluation.passed,
        behavioral_trace_sha256=_normalized_behavioral_trace_sha256(trace),
        trace_sha256=_trace_sha256(trace),
        transport_count=len(transport.calls),
        action_transport_count=action_transport_count,
        durable_claim_count=durable_claim_count,
        trace_lifecycle_valid=lifecycle_valid,
        contract_expectations_met=contract,
    )


def run_provider_free_delivery_demo(root: Path | str) -> DeliveryDemoReport:
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)
    results = tuple(
        _execute_demo_scenario(spec, root_path)
        for spec in demo_population()
    )
    return DeliveryDemoReport.build(results)


def _expected_adr_paths() -> dict[int, str]:
    return {
        4: "docs/adr/004-p0-agent-controller-2026-08-27.md",
        5: "docs/adr/005-p0-action-safety-2026-08-27.md",
        6: "docs/adr/006-provider-neutral-decision-source-2026-08-27.md",
        7: "docs/adr/007-model-call-provenance-2026-08-27.md",
        8: "docs/adr/008-production-provider-model-comparison-design-2026-08-28.md",
        9: "docs/adr/009-production-provider-client-identity-and-authorization-2026-08-28.md",
        10: "docs/adr/010-provider-comparison-executor-2026-08-28.md",
        11: "docs/adr/011-governed-live-provider-comparison-execution-2026-08-28.md",
        12: "docs/adr/012-controlled-action-execution-profile-2026-08-28.md",
        13: "docs/adr/013-provider-free-failure-performance-campaign-2026-08-28.md",
        14: "docs/adr/014-provider-free-repeated-run-stability-2026-08-28.md",
        15: "docs/adr/015-provider-free-customer-safe-communication-2026-08-28.md",
    }


def validate_evidence_index(index: EvidenceIndex, root: Path | str) -> EvidenceIndexValidation:
    root_path = Path(root).resolve()
    violations: list[str] = []
    resident_count = 0
    resolved_count = 0
    by_id = {entry.evidence_id: entry for entry in index.entries}

    for entry in index.entries:
        if entry.repository_path is None:
            continue
        resident_count += 1
        candidate = (root_path / entry.repository_path).resolve()
        try:
            candidate.relative_to(root_path)
        except ValueError:
            violations.append(f"{entry.evidence_id}: repository path escapes root")
            continue
        if not candidate.is_file():
            violations.append(f"{entry.evidence_id}: repository path missing")
            continue
        actual_blob = git_blob_sha1(candidate)
        if actual_blob != entry.git_blob_sha1:
            violations.append(f"{entry.evidence_id}: Git blob SHA-1 mismatch")
            continue
        resolved_count += 1

    for adr_number, expected_path in _expected_adr_paths().items():
        evidence_id = f"ADR-{adr_number:03d}"
        entry = by_id.get(evidence_id)
        if entry is None:
            violations.append(f"{evidence_id}: required ADR entry missing")
            continue
        if entry.category != "adr" or entry.adr_number != adr_number:
            violations.append(f"{evidence_id}: ADR metadata mismatch")
        if entry.repository_path != expected_path:
            violations.append(f"{evidence_id}: canonical ADR path mismatch")

    required_reports = {
        "EV007-RESULT": EXPECTED_EV007_REPORT_SHA256,
        "EV008-RESULT": EXPECTED_EV008_REPORT_SHA256,
        "EV011-RESULT": EXPECTED_EV011_REPORT_SHA256,
    }
    for evidence_id, expected_sha in required_reports.items():
        entry = by_id.get(evidence_id)
        if entry is None:
            violations.append(f"{evidence_id}: required frozen result missing")
        elif entry.canonical_sha256 != expected_sha:
            violations.append(f"{evidence_id}: canonical report SHA-256 mismatch")

    provider = by_id.get("PROVIDER-COMPARISON-PLAN")
    if provider is None:
        violations.append("PROVIDER-COMPARISON-PLAN: required entry missing")
    else:
        if provider.canonical_sha256 != EXPECTED_PROVIDER_PLAN_SHA256:
            violations.append("PROVIDER-COMPARISON-PLAN: canonical plan SHA-256 mismatch")
        if provider.reproduction_status != "UNEXECUTED_GATED":
            violations.append("PROVIDER-COMPARISON-PLAN: live execution must remain UNEXECUTED_GATED")

    c4 = by_id.get("C4-SCORE-ROW-ARTIFACT")
    if c4 is None:
        violations.append("C4-SCORE-ROW-ARTIFACT: required blocker entry missing")
    else:
        if c4.repository_path is not None or c4.git_blob_sha1 is not None:
            violations.append("C4-SCORE-ROW-ARTIFACT: missing external artifact must not claim repository residency")
        if c4.canonical_sha256 != EXPECTED_C4_ARTIFACT_SHA256:
            violations.append("C4-SCORE-ROW-ARTIFACT: expected SHA-256 mismatch")
        if c4.reproduction_status != "EXTERNALLY_BLOCKED":
            violations.append("C4-SCORE-ROW-ARTIFACT: must remain EXTERNALLY_BLOCKED")
        boundary = c4.authorization_boundary
        if str(EXPECTED_C4_ARTIFACT_BYTES) not in boundary or str(EXPECTED_C4_ARTIFACT_ROWS) not in boundary:
            violations.append("C4-SCORE-ROW-ARTIFACT: blocker byte/row identity missing from boundary")

    required_frozen_ids = {
        "EV007-FREEZE",
        "EV007-VALIDATOR",
        "EV008-FREEZE",
        "EV008-VALIDATOR",
        "EV011-FREEZE",
        "EV011-VALIDATOR",
    }
    for evidence_id in sorted(required_frozen_ids):
        if evidence_id not in by_id:
            violations.append(f"{evidence_id}: required evidence missing")

    demo_ids = {f"DEMO-0{i}" for i in range(1, 6)} | {"DELIVERY-DEMO-CAMPAIGN"}
    for evidence_id in sorted(demo_ids):
        if evidence_id not in by_id:
            violations.append(f"{evidence_id}: required demo evidence missing")

    return EvidenceIndexValidation(
        entry_count=len(index.entries),
        repository_resident_count=resident_count,
        resolved_repository_entries=resolved_count,
        violations=tuple(violations),
    )


def load_evidence_index(path: Path | str) -> EvidenceIndex:
    return EvidenceIndex.model_validate_json(Path(path).read_text(encoding="utf-8"))
