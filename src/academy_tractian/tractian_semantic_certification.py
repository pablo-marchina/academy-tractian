from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from research.e2.controller import (
    AgentController,
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ControllerLimits,
    ToolProposal,
)
from research.e2.evaluation_suite import default_suite
from research.e2.hash import sha256_json
from research.e2.models import (
    Decision,
    ExecutionBinding,
    Permission,
    ResponseMode,
    Scenario,
    ToolKind,
    ToolSpec,
)
from research.e2.replay import ReplayStore
from research.e2.runner import HarnessRunner
from research.e2.tool_registry import TOOLS, get_tool
from research.e2.transport import RequestTransport, TransportResponse, build_b0_request

from .hosted_integration_evidence_recorder import HostedIntegrationEvidenceRecorder
from .tractian_campaign_evidence import (
    CampaignEvidenceLedger,
    CampaignProofRecord,
    parse_campaign_evidence_document,
)
from .tractian_integration_evidence import IntegrationEvidenceLedger
from .tractian_transport_campaign import (
    TractianTransportCampaignManifest,
    TractianTransportCampaignRun,
    run_tractian_transport_campaign,
)


_REGISTRY = {tool.name: tool for tool in TOOLS}


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SemanticCertificationSummary(_StrictModel):
    schema_version: str = "tractian-semantic-certification-v1"
    configured_operations: int
    invalid_parameter_passes: int
    response_normalization_passes: int
    agent_evaluator_passes: int
    semantic_record_count: int


class _CapturingTransport:
    """Keep exact live responses only in process memory for immediate deterministic replay."""

    def __init__(self, delegate: RequestTransport) -> None:
        self._delegate = delegate
        self._responses: dict[str, TransportResponse] = {}
        self._ambiguous: set[str] = set()

    @staticmethod
    def _key(request) -> str:
        return ReplayStore.fingerprint(request.model_dump(mode="json"))

    def request(self, request) -> TransportResponse:
        response = self._delegate.request(request)
        key = self._key(request)
        previous = self._responses.get(key)
        if previous is not None and previous != response:
            self._ambiguous.add(key)
        self._responses[key] = response
        return response

    def response_for(self, request) -> TransportResponse | None:
        key = self._key(request)
        if key in self._ambiguous:
            return None
        return self._responses.get(key)


class _NetworkForbiddenTransport:
    def __init__(self) -> None:
        self.calls = 0

    def request(self, request) -> TransportResponse:
        self.calls += 1
        raise AssertionError("semantic invalid-parameter probe reached transport")


class _SingleToolDecisionSource:
    def __init__(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        evidence_id: str,
        expected_success: bool,
    ) -> None:
        self.tool_name = tool_name
        self.arguments = dict(arguments)
        self.evidence_id = evidence_id
        self.expected_success = expected_success
        self.contexts: list[ControllerContext] = []

    def decide(self, context: ControllerContext) -> ControllerDecision:
        self.contexts.append(context)
        if not context.observations:
            return ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name=self.tool_name,
                    arguments=self.arguments,
                    evidence_id=self.evidence_id,
                ),
            )
        decision = Decision.INVESTIGATE if self.expected_success else Decision.ABSTAIN
        response_mode = ResponseMode.COMPLETE if self.expected_success else ResponseMode.UNAVAILABLE
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": decision.value,
                "response_mode": response_mode.value,
                "facts": [],
                "claims": [],
            },
        )


def _safe_record(
    *,
    operation: str,
    dimension: str,
    passed: bool,
    observed_at: datetime,
    safe_details: dict[str, Any],
) -> CampaignProofRecord:
    probe_id = f"semantic-{uuid4().hex}"
    fingerprint = "sha256:" + sha256_json(
        {
            "operation": operation,
            "dimension": dimension,
            "passed": passed,
            "observed_at": observed_at.isoformat(),
            "probe_id": probe_id,
            "details": safe_details,
        }
    )
    return CampaignProofRecord.model_validate(
        {
            "operation": operation,
            "dimension": dimension,
            "passed": passed,
            "observed_at": observed_at,
            "probe_id": probe_id,
            "evidence_ref": f"hosted-runtime-semantic:{dimension}",
            "fingerprint": fingerprint,
        }
    )


def _invalid_parameter_probe(
    *,
    tool: ToolSpec,
    valid_arguments: dict[str, Any],
    binding: ExecutionBinding,
    observed_at: datetime,
) -> CampaignProofRecord:
    invalid_arguments = dict(valid_arguments)
    invalid_arguments["__semantic_probe_unknown_argument__"] = True
    forbidden_transport = _NetworkForbiddenTransport()
    runner = HarnessRunner(
        run_id=f"semantic-invalid-{uuid4().hex}",
        scenario_id="CEN-98",
        config_hash="semantic-invalid-parameter-v1",
        registry=_REGISTRY,
        binding=binding,
        transport=forbidden_transport,
        execution_mode="live",
        strict_arguments=True,
    )
    try:
        execution = runner.execute_tool(tool.name, invalid_arguments)
        passed = (
            execution.executed is False
            and execution.blocked_code == "ARGUMENT_INVALID"
            and forbidden_transport.calls == 0
        )
        blocked_code = execution.blocked_code
    except Exception:
        passed = False
        blocked_code = "SEMANTIC_INVALID_PARAMETER_PROBE_FAILED"

    return _safe_record(
        operation=tool.name,
        dimension="invalid_parameters_rejected",
        passed=passed,
        observed_at=observed_at,
        safe_details={
            "blocked_code": blocked_code,
            "network_calls": forbidden_transport.calls,
        },
    )


def _scenario_for_live_replay(
    *,
    tool: ToolSpec,
    arguments: dict[str, Any],
    binding: ExecutionBinding,
    evidence_id: str,
    expected_success: bool,
) -> Scenario:
    company_id = str(arguments.get("company_id") or "semantic-certification-company")
    asset_id = str(arguments.get("asset_id") or "semantic-certification-resource")
    action_oracle: dict[str, Any] | None = None
    if tool.kind is ToolKind.ACTION:
        required_permission = (
            tool.required_permissions[0].value
            if tool.required_permissions
            else Permission.READ.value
        )
        action_oracle = {
            "execution_expectation": "required",
            "success_semantics": "accepted_event",
            "post_action_read_semantics": "not_applicable",
            "required_action": tool.name,
            "required_permission": required_permission,
            "accepted_required": True,
            "duplicate_action_forbidden": True,
        }

    expected_decision = Decision.INVESTIGATE.value if expected_success else Decision.ABSTAIN.value
    return Scenario.model_validate(
        {
            "scenario_id": "CEN-98",
            "title": f"Hosted semantic certification for {tool.name}",
            "ticket_ids": [f"semantic-{tool.name}"],
            "split_group_id": "hosted-semantic-certification",
            "provenance": {
                "review_status": "APPROVED",
                "benchmark_authoritative": False,
                "source_locations": [
                    {
                        "source": "canonical_tool_registry",
                        "location": f"{tool.method} {tool.path_template}",
                    }
                ],
            },
            "input": {
                "cases": [
                    {
                        "id": f"semantic-{tool.name}",
                        "ticket_id": f"semantic-{tool.name}",
                        "company_id": company_id,
                        "user_id": binding.user_id,
                        "asset_id": asset_id,
                        "message": f"Controlled semantic certification for {tool.name}",
                    }
                ]
            },
            "bound_context": {
                "user_ids": [binding.user_id],
                "company_ids": [company_id],
                "asset_ids": [asset_id],
                "identity_model_controlled": False,
                "seed_model_controlled": False,
            },
            "environment": {},
            "decision_oracle": {"required": [expected_decision]},
            "policy_oracle": {
                "source_rules": ["semantic certification replays one already observed live response"],
                "required_permissions": [],
                "forbidden_actions": [],
                "resource_scope_enforced": True,
                "justification_required": tool.justification_required,
                "minimum_justification_length": tool.minimum_justification_length,
                "confirmation_required": False,
            },
            "evidence_oracle": {
                "required_groups": [
                    {
                        "group_id": "target-tool-observation",
                        "requirements": [
                            {
                                "source": evidence_id,
                                "predicate": "tool observation exists",
                            }
                        ],
                    }
                ],
                "uncertainty_behavior": "not_required",
            },
            "action_oracle": action_oracle,
            "conclusion_oracle": {
                "required_facts": [],
                "forbidden_claims": [],
                "uncertainty_required": False,
                "source_resolution_text": (
                    "Exact live TRACTIAN response was replayed in-memory through the frozen runtime; "
                    "the raw response is not persisted in semantic evidence."
                ),
            },
            "trajectory_oracle": {
                "reference_is_script": False,
                "reference_calls": [],
                "required_calls": [
                    {
                        "method": tool.method,
                        "path": tool.path_template,
                        "purpose": "verify canonical runtime observation handling",
                    }
                ],
                "forbidden_calls": [],
                "ordering_constraints": [],
                "efficiency_is_diagnostic": True,
            },
            "evaluation": {
                "p1_success_source": "hosted semantic certification",
                "p2_metric_sources": ["default EvaluationSuite"],
            },
        }
    )


def _live_response_semantic_records(
    *,
    tool: ToolSpec,
    valid_arguments: dict[str, Any],
    binding: ExecutionBinding,
    response: TransportResponse,
    observed_at: datetime,
) -> tuple[CampaignProofRecord, CampaignProofRecord]:
    request = build_b0_request(tool, valid_arguments, binding)
    replay = ReplayStore()
    replay.record(
        request.model_dump(mode="json"),
        {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.body,
        },
    )
    expected_success = 200 <= response.status_code < 400
    evidence_id = f"semantic-live-{tool.name}"
    source = _SingleToolDecisionSource(
        tool_name=tool.name,
        arguments=valid_arguments,
        evidence_id=evidence_id,
        expected_success=expected_success,
    )
    runner = HarnessRunner(
        run_id=f"semantic-replay-{uuid4().hex}",
        scenario_id="CEN-98",
        config_hash="semantic-live-response-replay-v1",
        registry=_REGISTRY,
        binding=binding,
        transport=None,
        replay=replay,
        execution_mode="replay",
        strict_arguments=True,
    )
    scenario = _scenario_for_live_replay(
        tool=tool,
        arguments=valid_arguments,
        binding=binding,
        evidence_id=evidence_id,
        expected_success=expected_success,
    )

    normalization_passed = False
    evaluator_passed = False
    evaluator_count = 0
    try:
        trace = AgentController(
            runner=runner,
            decision_source=source,
            limits=ControllerLimits(max_turns=3, max_tool_calls=1),
        ).run(f"Controlled semantic certification for {tool.name}")
        if len(source.contexts) >= 2:
            observations = source.contexts[-1].observations
            if len(observations) == 1:
                observation = observations[0]
                expected_status = "success" if expected_success else "failure"
                normalization_passed = (
                    observation.tool_name == tool.name
                    and observation.executed is True
                    and observation.status == expected_status
                    and observation.status_code == response.status_code
                    and observation.body == response.body
                )

        final_events = [event for event in trace.events if event.event_type == "final_response"]
        if len(final_events) == 1 and isinstance(final_events[0].result, dict):
            bundle = default_suite(_REGISTRY).evaluate(
                scenario=scenario,
                trace=list(trace.events),
                final=dict(final_events[0].result),
            )
            evaluator_count = len(bundle.results)
            evaluator_passed = bundle.passed
    except Exception:
        normalization_passed = False
        evaluator_passed = False

    normalization_record = _safe_record(
        operation=tool.name,
        dimension="response_normalization_verified",
        passed=normalization_passed,
        observed_at=observed_at,
        safe_details={
            "http_status": response.status_code,
            "expected_runtime_status": "success" if expected_success else "failure",
        },
    )
    evaluator_record = _safe_record(
        operation=tool.name,
        dimension="agent_evaluator_behavior_verified",
        passed=evaluator_passed,
        observed_at=observed_at,
        safe_details={
            "http_status": response.status_code,
            "evaluator_count": evaluator_count,
            "expected_decision": (
                Decision.INVESTIGATE.value if expected_success else Decision.ABSTAIN.value
            ),
        },
    )
    return normalization_record, evaluator_record


def run_tractian_semantic_certification(
    *,
    manifest: TractianTransportCampaignManifest,
    transport: RequestTransport,
    allow_actions: bool = False,
    recorder: HostedIntegrationEvidenceRecorder | None = None,
    now: Callable[[], datetime] | None = None,
) -> tuple[
    TractianTransportCampaignRun,
    IntegrationEvidenceLedger,
    CampaignEvidenceLedger,
    SemanticCertificationSummary,
]:
    """Run one live transport campaign and derive bounded semantic proof without duplicate I/O.

    Exact live responses are retained only in memory long enough to replay the already observed
    request through HarnessRunner -> AgentController -> default EvaluationSuite. Consequential
    actions are never re-sent during semantic certification. Invalid-parameter probes use a
    transport that raises on any call and therefore prove deterministic rejection with zero network
    I/O. The returned semantic ledger contains only safe proof metadata.
    """

    clock = now or (lambda: datetime.now(UTC))
    captured = _CapturingTransport(transport)
    transport_run, transport_ledger = run_tractian_transport_campaign(
        manifest=manifest,
        transport=captured,
        allow_actions=allow_actions,
        recorder=recorder,
    )
    binding = ExecutionBinding(
        identity_id=manifest.identity_id,
        user_id=manifest.user_id,
        seed=manifest.seed,
    )

    semantic_records: list[CampaignProofRecord] = []
    fixture_by_operation = {fixture.operation: fixture for fixture in manifest.fixtures}
    for result in transport_run.results:
        fixture = fixture_by_operation[result.operation]
        tool = get_tool(result.operation)
        invalid_observed_at = clock()
        semantic_records.append(
            _invalid_parameter_probe(
                tool=tool,
                valid_arguments=fixture.valid_arguments,
                binding=binding,
                observed_at=invalid_observed_at,
            )
        )

        if result.valid_probe not in {"success", "http_error_observed"}:
            continue
        request = build_b0_request(tool, fixture.valid_arguments, binding)
        live_response = captured.response_for(request)
        if live_response is None:
            observed_at = clock()
            semantic_records.extend(
                (
                    _safe_record(
                        operation=tool.name,
                        dimension="response_normalization_verified",
                        passed=False,
                        observed_at=observed_at,
                        safe_details={"reason": "live_response_capture_ambiguous_or_missing"},
                    ),
                    _safe_record(
                        operation=tool.name,
                        dimension="agent_evaluator_behavior_verified",
                        passed=False,
                        observed_at=observed_at,
                        safe_details={"reason": "live_response_capture_ambiguous_or_missing"},
                    ),
                )
            )
            continue
        semantic_records.extend(
            _live_response_semantic_records(
                tool=tool,
                valid_arguments=fixture.valid_arguments,
                binding=binding,
                response=live_response,
                observed_at=clock(),
            )
        )

    semantic_payload = {
        "schema_version": "tractian-campaign-evidence-v1",
        "records": [record.model_dump(mode="json") for record in semantic_records],
    }
    semantic_ledger = parse_campaign_evidence_document(
        semantic_payload,
        source_label="hosted_live:semantic_certification",
    )
    if not semantic_ledger.valid:
        return (
            transport_run,
            transport_ledger,
            semantic_ledger,
            SemanticCertificationSummary(
                configured_operations=len(transport_run.results),
                invalid_parameter_passes=0,
                response_normalization_passes=0,
                agent_evaluator_passes=0,
                semantic_record_count=0,
            ),
        )

    summary = SemanticCertificationSummary(
        configured_operations=len(transport_run.results),
        invalid_parameter_passes=sum(
            record.dimension == "invalid_parameters_rejected" and record.passed
            for record in semantic_ledger.records
        ),
        response_normalization_passes=sum(
            record.dimension == "response_normalization_verified" and record.passed
            for record in semantic_ledger.records
        ),
        agent_evaluator_passes=sum(
            record.dimension == "agent_evaluator_behavior_verified" and record.passed
            for record in semantic_ledger.records
        ),
        semantic_record_count=len(semantic_ledger.records),
    )
    return transport_run, transport_ledger, semantic_ledger, summary
