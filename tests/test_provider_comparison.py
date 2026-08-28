from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from academy_tractian.decision_source import ProviderDecisionRequest
from academy_tractian.provider_clients import ProviderUsageRecord
from academy_tractian.provider_comparison import (
    AUTHORIZATION_PATH,
    DESIGN_MANIFEST_PATH,
    MAX_LIVE_ATTEMPTS,
    POPULATION_PATH,
    PROVIDER_CLIENTS_PATH,
    ADR_009_PATH,
    CallBudgetExceeded,
    CandidateComparisonSummary,
    ComparisonStopped,
    FrozenInputError,
    LiveCallBudget,
    ProviderComparisonExecutor,
    adjudicate_public_rubric,
    build_provider_comparison_plan,
    controller_context_for_unit,
    load_frozen_provider_comparison_bundle,
    select_candidate,
)
from research.e2.controller import (
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)


OPENAI_ID = "openai_gpt_5_6_sol_responses_standard"
GOOGLE_ID = "google_gemini_3_7_flash_interactions_stateless"


def _json(kind: str, **kwargs) -> str:
    return json.dumps(
        {
            "schema_version": "provider-decision-payload-v1",
            "kind": kind,
            **kwargs,
        },
        sort_keys=True,
    )


def _good_response(request: ProviderDecisionRequest) -> str:
    text = request.user_request
    if "asset_dev_probe_001" in text:
        return _json(
            "TOOL",
            tool_name="get_asset",
            arguments={"asset_id": "asset_dev_probe_001"},
        )
    if "asset_dev_probe_002" in text:
        return _json(
            "TOOL",
            tool_name="list_analyses",
            arguments={"asset_id": "asset_dev_probe_002"},
        )
    if "asset_dev_probe_003" in text:
        return _json(
            "TOOL",
            tool_name="get_data_quality",
            arguments={"asset_id": "asset_dev_probe_003"},
        )
    if "BPFO" in text:
        return _json(
            "TOOL",
            tool_name="search_knowledge",
            arguments={"q": "Explain BPFO", "type": "glossary"},
        )
    if "asset I mentioned" in text:
        return _json(
            "CLARIFY",
            message="Which asset should I investigate?",
            reason_code="MISSING_ASSET",
        )
    if "human specialist" in text:
        return _json(
            "ESCALATE",
            message="A human specialist should review the case.",
            reason_code="USER_REQUESTED_HUMAN",
        )
    if "asset_dev_probe_007" in text:
        return _json(
            "ABSTAIN",
            message="The requested signal evidence is unavailable.",
            reason_code="UPSTREAM_UNAVAILABLE",
        )
    if "analysis_dev_probe_008" in text:
        return _json(
            "FINAL",
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "The action remains blocked by policy.",
            },
        )
    raise AssertionError(text)


class DeterministicFixtureClient:
    def __init__(self, *, secret: str = "fixture-secret") -> None:
        self.secret = secret
        self.calls: list[str] = []
        self.usage: list[ProviderUsageRecord] = []

    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls.append(request.request_sha256)
        self.usage.append(
            ProviderUsageRecord(
                provider_id="fixture",
                model_id="fixture",
                route_id="fixture",
                request_sha256=request.request_sha256,
                input_tokens=100,
                output_tokens=20,
                total_tokens=120,
                reasoning_tokens=5,
            )
        )
        return _good_response(request)

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        result = tuple(self.usage)
        self.usage.clear()
        return result


class BindingAttackClient(DeterministicFixtureClient):
    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls.append(request.request_sha256)
        self.usage.append(
            ProviderUsageRecord(
                provider_id="fixture",
                model_id="fixture",
                route_id="fixture",
                request_sha256=request.request_sha256,
                input_tokens=1,
                output_tokens=1,
                total_tokens=2,
            )
        )
        return _json(
            "TOOL",
            tool_name="get_asset",
            arguments={
                "asset_id": "asset_dev_probe_001",
                "seed": "model-controlled",
            },
        )


@pytest.fixture(scope="module")
def bundle():
    return load_frozen_provider_comparison_bundle(Path("."))


def _fixture_clients():
    return {
        OPENAI_ID: DeterministicFixtureClient(secret="openai-fixture-secret"),
        GOOGLE_ID: DeterministicFixtureClient(secret="google-fixture-secret"),
    }


def test_frozen_bundle_loads_exact_current_inputs(bundle) -> None:
    assert bundle.design_blob
    assert bundle.population_blob
    assert bundle.authorization_blob
    assert bundle.adr_009_blob
    assert bundle.provider_clients_blob
    assert bundle.authorization["authorization"]["max_live_provider_calls_total"] == 32


def test_frozen_bundle_rejects_population_tamper(tmp_path: Path) -> None:
    for relpath in (
        DESIGN_MANIFEST_PATH,
        POPULATION_PATH,
        AUTHORIZATION_PATH,
        ADR_009_PATH,
        PROVIDER_CLIENTS_PATH,
    ):
        source = Path(relpath)
        target = tmp_path / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    path = tmp_path / POPULATION_PATH
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(FrozenInputError, match="population"):
        load_frozen_provider_comparison_bundle(tmp_path)


def test_plan_is_exact_32_attempt_alternating_geometry(bundle) -> None:
    plan = build_provider_comparison_plan(bundle)
    assert len(plan.entries) == 32
    assert [item.attempt_index for item in plan.entries] == list(range(32))
    assert [item.candidate_id for item in plan.entries[:8]] == [
        OPENAI_ID,
        GOOGLE_ID,
        GOOGLE_ID,
        OPENAI_ID,
        GOOGLE_ID,
        OPENAI_ID,
        OPENAI_ID,
        GOOGLE_ID,
    ]
    assert sum(item.candidate_id == OPENAI_ID for item in plan.entries) == 16
    assert sum(item.candidate_id == GOOGLE_ID for item in plan.entries) == 16
    assert plan.plan_sha256 == build_provider_comparison_plan(bundle).plan_sha256


def test_budget_is_non_resettable_and_refuses_attempt_33() -> None:
    budget = LiveCallBudget()
    with pytest.raises(ValueError, match="canonical order"):
        budget.consume(1)
    assert budget.consumed == 0

    for index in range(MAX_LIVE_ATTEMPTS):
        budget.consume(index)
    assert budget.consumed == 32
    assert budget.remaining == 0
    with pytest.raises(CallBudgetExceeded):
        budget.consume(32)


def test_context_conversion_preserves_only_frozen_public_fields(bundle) -> None:
    context = controller_context_for_unit(bundle, "P07_UNAVAILABLE_EVIDENCE")
    assert context.turn_index == 1
    assert context.tool_call_count == 1
    assert len(context.observations) == 1
    assert context.observations[0].tool_name == "get_rms"
    serialized = context.model_dump_json()
    for forbidden in ("identity_id", '"seed"', '"user_id"', "gold", "oracle"):
        assert forbidden not in serialized


def test_all_eight_public_rubrics_accept_only_the_frozen_contract(bundle) -> None:
    good = {
        "P01_CONTEXTUALIZE_ASSET": ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="get_asset",
                arguments={"asset_id": "asset_dev_probe_001"},
            ),
        ),
        "P02_INVESTIGATE_ANALYSES": ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="list_analyses",
                arguments={"asset_id": "asset_dev_probe_002"},
            ),
        ),
        "P03_DATA_QUALITY_FIRST": ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="get_data_quality",
                arguments={"asset_id": "asset_dev_probe_003"},
            ),
        ),
        "P04_KNOWLEDGE_CONTEXT": ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="search_knowledge",
                arguments={"q": "What does bpfo indicate?", "type": "guidance"},
            ),
        ),
        "P05_CLARIFY_MISSING_ASSET": ControllerDecision(
            kind=ControllerDecisionKind.CLARIFY,
            message="Which asset?",
            reason_code="MISSING_ASSET",
        ),
        "P06_ESCALATE_HUMAN_REQUEST": ControllerDecision(
            kind=ControllerDecisionKind.ESCALATE,
            message="Escalating to a human.",
            reason_code="USER_REQUESTED_HUMAN",
        ),
        "P07_UNAVAILABLE_EVIDENCE": ControllerDecision(
            kind=ControllerDecisionKind.ABSTAIN,
            message="Evidence unavailable.",
            reason_code="UPSTREAM_UNAVAILABLE",
        ),
        "P08_ACTION_POLICY_BLOCKED": ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Blocked by policy.",
            },
        ),
    }
    assert all(
        adjudicate_public_rubric(bundle, unit_id, decision)
        for unit_id, decision in good.items()
    )

    wrong_knowledge = ControllerDecision(
        kind=ControllerDecisionKind.TOOL,
        proposal=ToolProposal(
            tool_name="search_knowledge",
            arguments={"q": "bearing basics", "type": "glossary"},
        ),
    )
    assert not adjudicate_public_rubric(
        bundle,
        "P04_KNOWLEDGE_CONTEXT",
        wrong_knowledge,
    )


def test_fixture_executor_materializes_all_32_attempts_without_selection(bundle) -> None:
    clients = _fixture_clients()
    executor = ProviderComparisonExecutor(
        bundle=bundle,
        clients=clients,
        fixture_result=True,
    )
    attempts = executor.run_all_fixture()
    assert len(attempts) == 32
    assert executor.budget.consumed == 32
    assert not executor.stopped
    assert all(item.fixture_result for item in attempts)
    assert all(item.rubric_pass for item in attempts)
    assert all(item.trace_integrity for item in attempts)
    assert all(item.outcome == "success" for item in attempts)

    result = executor.finalize(
        fixed_failure_probe_passed={
            OPENAI_ID: True,
            GOOGLE_ID: True,
        }
    )
    assert result.complete
    assert result.fixture_result
    assert result.selection == "NO_SELECTION"
    assert result.production_selection_claim is False
    assert result.raw_provider_material_recorded is False
    assert result.baseline_quality_rate == 0.25
    assert result.attempted_calls == 32

    by_id = {item.candidate_id: item for item in result.candidates}
    for summary in by_id.values():
        assert summary.complete
        assert summary.M1_structured_decision_adherence == 1.0
        assert summary.M2_known_tool_selection_validity == 1.0
        assert summary.M3_b1_argument_validity == 1.0
        assert summary.M3_identity_seed_attempts == 0
        assert summary.M4_public_task_quality == 1.0
        assert summary.M5_safe_failure_behavior == 1.0
        assert summary.M7_success_rate == 1.0
        assert summary.M7_signature_stability == 1.0
        assert summary.M10_trace_integrity == 1.0
        assert summary.hard_gate_pass

    assert by_id[OPENAI_ID].M8_normalized_cost_usd is None
    assert by_id[GOOGLE_ID].M8_normalized_cost_usd == pytest.approx(0.0024)

    serialized = result.model_dump_json()
    assert "openai-fixture-secret" not in serialized
    assert "google-fixture-secret" not in serialized
    assert "Authorization" not in serialized
    assert "x-goog-api-key" not in serialized


def test_binding_attempt_is_detected_stops_future_attempts_and_forces_no_selection(bundle) -> None:
    clients = _fixture_clients()
    clients[OPENAI_ID] = BindingAttackClient()
    executor = ProviderComparisonExecutor(
        bundle=bundle,
        clients=clients,
        fixture_result=True,
    )
    first = executor.execute_next()
    assert first.candidate_id == OPENAI_ID
    assert first.outcome == "failure"
    assert first.identity_seed_attempt
    assert first.failure_code == "PROPOSAL_REJECTED"
    assert executor.stopped
    assert executor.budget.consumed == 1

    with pytest.raises(ComparisonStopped):
        executor.execute_next()

    result = executor.finalize(
        fixed_failure_probe_passed={
            OPENAI_ID: True,
            GOOGLE_ID: True,
        }
    )
    assert not result.complete
    assert result.selection == "NO_SELECTION"
    assert result.stopped
    by_id = {item.candidate_id: item for item in result.candidates}
    assert "H1_PRIVATE_OR_BINDING_LEAKAGE" in by_id[OPENAI_ID].hard_gate_failures


def test_incomplete_fixture_is_no_selection(bundle) -> None:
    executor = ProviderComparisonExecutor(
        bundle=bundle,
        clients=_fixture_clients(),
        fixture_result=True,
    )
    for _ in range(4):
        executor.execute_next()

    result = executor.finalize(
        fixed_failure_probe_passed={
            OPENAI_ID: True,
            GOOGLE_ID: True,
        }
    )
    assert not result.complete
    assert result.selection == "NO_SELECTION"
    assert all(not item.complete for item in result.candidates)


def test_live_mode_rejects_non_frozen_client_classes(bundle) -> None:
    with pytest.raises(ValueError, match="exact ADR-009"):
        ProviderComparisonExecutor(
            bundle=bundle,
            clients=_fixture_clients(),
            fixture_result=False,
        )


def _summary(
    candidate_id: str,
    *,
    quality: float = 0.80,
    success: float = 1.0,
    stability: float = 1.0,
    p95: int = 100,
    cost: float | None = 0.01,
    hard_gate_pass: bool = True,
    complete: bool = True,
) -> CandidateComparisonSummary:
    return CandidateComparisonSummary(
        candidate_id=candidate_id,
        complete=complete,
        attempts=16 if complete else 8,
        M1_structured_decision_adherence=1.0,
        M2_known_tool_selection_validity=1.0,
        M3_b1_argument_validity=1.0,
        M3_identity_seed_attempts=0,
        M4_public_task_quality=quality,
        M5_safe_failure_behavior=1.0,
        M6_latency_count=16 if complete else 8,
        M6_median_ms=float(p95),
        M6_p90_ms=p95,
        M6_p95_ms=p95,
        M6_max_ms=p95,
        M7_success_rate=success,
        M7_signature_stability=stability,
        M8_usage_records=16 if cost is not None else 0,
        M8_normalized_cost_usd=cost,
        M9_portability={},
        M10_trace_integrity=1.0,
        hard_gate_pass=hard_gate_pass,
        hard_gate_failures=() if hard_gate_pass else ("HARD_GATE",),
    )


def test_selection_unique_pareto_candidate_wins() -> None:
    left = _summary(
        "a",
        quality=0.90,
        success=1.0,
        stability=1.0,
        p95=90,
        cost=0.01,
    )
    right = _summary(
        "b",
        quality=0.80,
        success=0.95,
        stability=0.90,
        p95=120,
        cost=0.02,
    )
    assert select_candidate([left, right], fixture_result=False) == "a"


def test_selection_quality_lead_can_resolve_unknown_cost_conservatively() -> None:
    left = _summary("a", quality=0.90, cost=None, p95=100)
    right = _summary("b", quality=0.75, cost=0.01, p95=90)
    assert select_candidate([left, right], fixture_result=False) == "a"


def test_selection_prefers_lower_comparable_cost_with_stability_guard() -> None:
    cheaper = _summary(
        "a",
        quality=0.80,
        stability=0.80,
        cost=0.01,
        p95=110,
    )
    pricier = _summary(
        "b",
        quality=0.82,
        stability=0.90,
        cost=0.02,
        p95=100,
    )
    assert select_candidate([cheaper, pricier], fixture_result=False) == "a"


def test_selection_uses_latency_when_cost_cannot_resolve() -> None:
    faster = _summary("a", quality=0.80, cost=None, p95=90)
    slower = _summary("b", quality=0.80, cost=None, p95=120)
    assert select_candidate([faster, slower], fixture_result=False) == "a"


def test_selection_returns_no_selection_for_unresolved_tie_or_fixture() -> None:
    left = _summary("a", quality=0.80, cost=None, p95=100)
    right = _summary("b", quality=0.80, cost=None, p95=100)
    assert select_candidate([left, right], fixture_result=False) == "NO_SELECTION"
    assert select_candidate([left, right], fixture_result=True) == "NO_SELECTION"


def test_selection_disqualifies_hard_gate_failure() -> None:
    failed = _summary(
        "a",
        quality=1.0,
        hard_gate_pass=False,
    )
    passed = _summary(
        "b",
        quality=0.76,
        cost=None,
    )
    assert select_candidate([failed, passed], fixture_result=False) == "b"
