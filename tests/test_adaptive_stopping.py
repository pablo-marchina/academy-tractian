from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.adaptive_stopping import (
    AdaptiveStoppingReplayCase,
    EvidenceRequirementJudgment,
    analyze_adaptive_stopping_case,
    analyze_adaptive_stopping_experiment,
    freeze_adaptive_stopping_judgments,
    freeze_adaptive_stopping_selection,
)
from research.e2.models import (
    AgentCase,
    BoundContext,
    ConclusionOracle,
    DecisionOracle,
    EnvironmentSpec,
    EvaluationSpec,
    EvidenceGroup,
    EvidenceOracle,
    EvidenceRequirement,
    PolicyOracle,
    Provenance,
    RunTrace,
    Scenario,
    ScenarioInput,
    TraceEvent,
    TrajectoryOracle,
)


def _scenario(
    scenario_id: str = "CEN-01",
    *,
    groups: list[EvidenceGroup] | None = None,
) -> Scenario:
    return Scenario(
        scenario_id=scenario_id,
        title="adaptive stopping synthetic case",
        ticket_ids=[f"TKT-{scenario_id}"],
        split_group_id=f"group-{scenario_id}",
        provenance=Provenance(
            review_status="APPROVED",
            benchmark_authoritative=True,
        ),
        input=ScenarioInput(
            cases=[
                AgentCase(
                    id=f"case-{scenario_id}",
                    ticket_id=f"TKT-{scenario_id}",
                    company_id="comp-a",
                    user_id="usr-a",
                    asset_id="asset-a",
                    message="synthetic evaluator-only ticket",
                )
            ]
        ),
        bound_context=BoundContext(
            user_ids=["usr-a"],
            company_ids=["comp-a"],
            asset_ids=["asset-a"],
        ),
        environment=EnvironmentSpec(),
        decision_oracle=DecisionOracle(),
        policy_oracle=PolicyOracle(),
        evidence_oracle=EvidenceOracle(required_groups=groups or []),
        conclusion_oracle=ConclusionOracle(source_resolution_text="synthetic"),
        trajectory_oracle=TrajectoryOracle(),
        evaluation=EvaluationSpec(p1_success_source="synthetic"),
    )


def _trace(scenario_id: str, tool_names: list[str]) -> RunTrace:
    events = [TraceEvent(sequence=0, event_type="run_started")]
    for index, tool_name in enumerate(tool_names, start=1):
        events.append(
            TraceEvent(
                sequence=index,
                event_type="tool_call",
                tool_name=tool_name,
                call_id=f"call-{index}",
            )
        )
    events.append(TraceEvent(sequence=len(events), event_type="run_finished"))
    return RunTrace(
        run_id=f"run-{scenario_id}",
        scenario_id=scenario_id,
        config_hash="a" * 64,
        identity_binding_id="identity-a",
        seed_ref="seed-a",
        events=events,
    )


def _judgment(
    group_id: str,
    index: int,
    source: str,
    predicate: str,
    *,
    status: str,
    ordinal: int | None = None,
) -> EvidenceRequirementJudgment:
    return EvidenceRequirementJudgment(
        group_id=group_id,
        requirement_index=index,
        source=source,
        predicate=predicate,
        status=status,  # type: ignore[arg-type]
        satisfied_at_tool_call_ordinal=ordinal,
    )


def _split(*, dev: list[str], validation: list[str] | None = None, locked: list[str] | None = None):
    return {
        "schema_version": "frozen-split-test-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {"groups": [{"group_id": "dev", "scenarios": dev}]},
            "VALIDATION": {
                "groups": [{"group_id": "validation", "scenarios": validation or []}]
            },
            "LOCKED_TEST": {
                "groups": [{"group_id": "locked", "scenarios": locked or []}]
            },
        },
    }


def test_adaptive_stopping_observes_first_globally_sufficient_prefix_and_headroom():
    scenario = _scenario(
        groups=[
            EvidenceGroup(
                group_id="identity",
                requirements=[
                    EvidenceRequirement(source="get_current_user", predicate="identity is bound"),
                    EvidenceRequirement(source="get_company", predicate="company matches"),
                ],
                minimum_satisfied=1,
            ),
            EvidenceGroup(
                group_id="condition",
                requirements=[
                    EvidenceRequirement(source="get_asset", predicate="asset is identified"),
                    EvidenceRequirement(
                        source="get_data_quality",
                        predicate="data quality is sufficient",
                        required_before_action=True,
                    ),
                ],
                minimum_satisfied=None,
            ),
        ]
    )
    trace = _trace(
        scenario.scenario_id,
        [
            "get_current_user",
            "get_asset",
            "get_company",
            "get_data_quality",
            "reprocess_analysis",
            "get_analysis",
        ],
    )
    judgments = [
        _judgment("identity", 0, "get_current_user", "identity is bound", status="SATISFIED", ordinal=1),
        _judgment("identity", 1, "get_company", "company matches", status="SATISFIED", ordinal=3),
        _judgment("condition", 0, "get_asset", "asset is identified", status="SATISFIED", ordinal=2),
        _judgment(
            "condition",
            1,
            "get_data_quality",
            "data quality is sufficient",
            status="SATISFIED",
            ordinal=4,
        ),
    ]
    packet = freeze_adaptive_stopping_judgments(
        scenario=scenario,
        trace=trace,
        judgments=judgments,
    )
    replay = AdaptiveStoppingReplayCase(scenario=scenario, trace=trace, judgments=packet)

    case = analyze_adaptive_stopping_case(case_index=0, replay_case=replay)
    assert case.status == "SUFFICIENT_PREFIX_OBSERVED"
    assert case.earliest_sufficient_tool_call_ordinal == 4
    assert case.post_sufficiency_tool_calls == 2
    assert case.headroom_fraction == pytest.approx(2 / 6)
    assert case.first_action_tool_call_ordinal == 5
    assert case.required_before_action_violation_count == 0

    selection = freeze_adaptive_stopping_selection([scenario.scenario_id])
    result = analyze_adaptive_stopping_experiment(
        selection=selection,
        replay_cases=[replay],
        frozen_split_payload=_split(dev=[scenario.scenario_id]),
    )
    assert result.status == "HEADROOM_OBSERVED"
    assert result.post_sufficiency_tool_call_count == 2
    assert result.observed_headroom_fraction == pytest.approx(2 / 6)
    assert result.promotion_ready is False
    assert result.runtime_policy_change_authorized is False
    assert result.business_claim_ready is False
    assert result.requires_runtime_challenger_experiment is True


def test_minimum_satisfied_none_requires_every_requirement_in_group():
    scenario = _scenario(
        groups=[
            EvidenceGroup(
                group_id="all-required",
                requirements=[
                    EvidenceRequirement(source="get_asset", predicate="asset found"),
                    EvidenceRequirement(source="get_baseline", predicate="baseline found"),
                ],
            )
        ]
    )
    trace = _trace(scenario.scenario_id, ["get_asset", "get_baseline", "get_rms"])
    packet = freeze_adaptive_stopping_judgments(
        scenario=scenario,
        trace=trace,
        judgments=[
            _judgment("all-required", 0, "get_asset", "asset found", status="SATISFIED", ordinal=1),
            _judgment("all-required", 1, "get_baseline", "baseline found", status="SATISFIED", ordinal=2),
        ],
    )
    result = analyze_adaptive_stopping_case(
        case_index=0,
        replay_case=AdaptiveStoppingReplayCase(scenario=scenario, trace=trace, judgments=packet),
    )
    assert result.earliest_sufficient_tool_call_ordinal == 2
    assert result.post_sufficiency_tool_calls == 1


def test_unassessable_predicate_blocks_sufficiency_without_guessing_from_tool_presence():
    scenario = _scenario(
        groups=[
            EvidenceGroup(
                group_id="quality",
                requirements=[
                    EvidenceRequirement(
                        source="get_data_quality",
                        predicate="quality crosses scenario-specific threshold",
                    )
                ],
            )
        ]
    )
    trace = _trace(scenario.scenario_id, ["get_data_quality"])
    packet = freeze_adaptive_stopping_judgments(
        scenario=scenario,
        trace=trace,
        judgments=[
            _judgment(
                "quality",
                0,
                "get_data_quality",
                "quality crosses scenario-specific threshold",
                status="NOT_ASSESSABLE",
            )
        ],
    )
    result = analyze_adaptive_stopping_case(
        case_index=0,
        replay_case=AdaptiveStoppingReplayCase(scenario=scenario, trace=trace, judgments=packet),
    )
    assert result.status == "NOT_ASSESSABLE"
    assert result.earliest_sufficient_tool_call_ordinal is None
    assert result.post_sufficiency_tool_calls is None
    assert "required_group_contains_unassessable_predicate" in result.reason_codes


def test_full_trace_insufficiency_is_distinct_from_unassessable():
    scenario = _scenario(
        groups=[
            EvidenceGroup(
                group_id="quality",
                requirements=[EvidenceRequirement(source="get_data_quality", predicate="quality is good")],
            )
        ]
    )
    trace = _trace(scenario.scenario_id, ["get_data_quality"])
    packet = freeze_adaptive_stopping_judgments(
        scenario=scenario,
        trace=trace,
        judgments=[
            _judgment(
                "quality",
                0,
                "get_data_quality",
                "quality is good",
                status="NOT_SATISFIED",
            )
        ],
    )
    result = analyze_adaptive_stopping_case(
        case_index=0,
        replay_case=AdaptiveStoppingReplayCase(scenario=scenario, trace=trace, judgments=packet),
    )
    assert result.status == "SUFFICIENCY_NOT_REACHED"
    assert "required_group_not_satisfied_in_full_trace" in result.reason_codes


def test_required_before_action_violation_is_reported_but_does_not_authorize_policy_change():
    scenario = _scenario(
        groups=[
            EvidenceGroup(
                group_id="safety",
                requirements=[
                    EvidenceRequirement(
                        source="get_analysis",
                        predicate="analysis supports action",
                        required_before_action=True,
                    )
                ],
            )
        ]
    )
    trace = _trace(scenario.scenario_id, ["reprocess_analysis", "get_analysis"])
    packet = freeze_adaptive_stopping_judgments(
        scenario=scenario,
        trace=trace,
        judgments=[
            _judgment(
                "safety",
                0,
                "get_analysis",
                "analysis supports action",
                status="SATISFIED",
                ordinal=2,
            )
        ],
    )
    replay = AdaptiveStoppingReplayCase(scenario=scenario, trace=trace, judgments=packet)
    case = analyze_adaptive_stopping_case(case_index=0, replay_case=replay)
    assert case.first_action_tool_call_ordinal == 1
    assert case.required_before_action_violation_count == 1

    result = analyze_adaptive_stopping_experiment(
        selection=freeze_adaptive_stopping_selection([scenario.scenario_id]),
        replay_cases=[replay],
        frozen_split_payload=_split(dev=[scenario.scenario_id]),
    )
    assert result.required_before_action_violation_count == 1
    assert result.runtime_policy_change_authorized is False


def test_experiment_rejects_validation_locked_test_and_non_frozen_splits():
    scenario = _scenario()
    trace = _trace(scenario.scenario_id, ["get_asset"])
    empty_oracle_packet = freeze_adaptive_stopping_judgments(
        scenario=scenario,
        trace=trace,
        judgments=[],
    )
    replay = AdaptiveStoppingReplayCase(
        scenario=scenario,
        trace=trace,
        judgments=empty_oracle_packet,
    )
    selection = freeze_adaptive_stopping_selection([scenario.scenario_id])

    with pytest.raises(ValueError, match="DEV-only"):
        analyze_adaptive_stopping_experiment(
            selection=selection,
            replay_cases=[replay],
            frozen_split_payload=_split(dev=[], validation=[scenario.scenario_id]),
        )
    with pytest.raises(ValueError, match="DEV-only"):
        analyze_adaptive_stopping_experiment(
            selection=selection,
            replay_cases=[replay],
            frozen_split_payload=_split(dev=[], locked=[scenario.scenario_id]),
        )
    payload = _split(dev=[scenario.scenario_id])
    payload["status"] = "DRAFT"
    with pytest.raises(ValueError, match="FROZEN"):
        analyze_adaptive_stopping_experiment(
            selection=selection,
            replay_cases=[replay],
            frozen_split_payload=payload,
        )


def test_frozen_packet_rejects_partial_binding_wrong_predicate_and_trace_tampering():
    scenario = _scenario(
        groups=[
            EvidenceGroup(
                group_id="evidence",
                requirements=[EvidenceRequirement(source="get_asset", predicate="asset found")],
            )
        ]
    )
    trace = _trace(scenario.scenario_id, ["get_asset", "get_rms"])
    with pytest.raises(ValueError, match="cover every oracle requirement"):
        freeze_adaptive_stopping_judgments(scenario=scenario, trace=trace, judgments=[])
    with pytest.raises(ValueError, match="binding mismatch"):
        freeze_adaptive_stopping_judgments(
            scenario=scenario,
            trace=trace,
            judgments=[
                _judgment(
                    "evidence",
                    0,
                    "get_asset",
                    "different predicate",
                    status="SATISFIED",
                    ordinal=1,
                )
            ],
        )

    packet = freeze_adaptive_stopping_judgments(
        scenario=scenario,
        trace=trace,
        judgments=[
            _judgment("evidence", 0, "get_asset", "asset found", status="SATISFIED", ordinal=1)
        ],
    )
    mutated_trace = _trace(scenario.scenario_id, ["get_asset", "get_baseline"])
    with pytest.raises(ValueError, match="does not bind current trace"):
        analyze_adaptive_stopping_case(
            case_index=0,
            replay_case=AdaptiveStoppingReplayCase(
                scenario=scenario,
                trace=mutated_trace,
                judgments=packet,
            ),
        )


def test_selection_hash_tampering_and_duplicate_selection_fail_closed():
    selection = freeze_adaptive_stopping_selection(["CEN-02", "CEN-01"])
    assert selection.scenario_ids == ("CEN-01", "CEN-02")
    with pytest.raises(ValidationError, match="hash mismatch"):
        selection.model_copy(update={"selection_sha256": "0" * 64}).model_validate(
            {
                **selection.model_dump(mode="json"),
                "selection_sha256": "0" * 64,
            }
        )
    with pytest.raises(ValidationError, match="duplicate"):
        freeze_adaptive_stopping_selection(["CEN-01", "CEN-01"])


def test_oracle_without_required_groups_is_not_assessable_not_zero_headroom():
    scenario = _scenario(groups=[])
    trace = _trace(scenario.scenario_id, ["get_asset"])
    packet = freeze_adaptive_stopping_judgments(scenario=scenario, trace=trace, judgments=[])
    replay = AdaptiveStoppingReplayCase(scenario=scenario, trace=trace, judgments=packet)
    case = analyze_adaptive_stopping_case(case_index=0, replay_case=replay)
    assert case.status == "NOT_ASSESSABLE"
    assert case.reason_codes == ("oracle_has_no_required_evidence_groups",)

    result = analyze_adaptive_stopping_experiment(
        selection=freeze_adaptive_stopping_selection([scenario.scenario_id]),
        replay_cases=[replay],
        frozen_split_payload=_split(dev=[scenario.scenario_id]),
    )
    assert result.status == "NOT_READY"
    assert result.observed_headroom_fraction is None
