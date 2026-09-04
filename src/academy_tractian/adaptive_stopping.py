from __future__ import annotations

from hashlib import sha256
import json
from statistics import mean
from typing import Any, Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.models import EvidenceGroup, EvidenceRequirement, RunTrace, Scenario, ToolKind
from research.e2.tool_registry import get_tool
from research.e2.trace import validate_trace


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _trace_sha256(trace: RunTrace) -> str:
    return _canonical_sha256(trace.model_dump(mode="json"))


def _oracle_sha256(scenario: Scenario) -> str:
    return _canonical_sha256(scenario.evidence_oracle.model_dump(mode="json"))


class EvidenceRequirementJudgment(_FrozenModel):
    """Evaluator-only judgment for one free-text EvidenceRequirement predicate.

    A predicate is never inferred from the tool name or raw result shape. The evaluator must
    explicitly bind the judgment back to the oracle requirement and, when satisfied, identify the
    ordinal tool call at which the predicate first became satisfied.
    """

    group_id: str = Field(min_length=1)
    requirement_index: int = Field(ge=0)
    source: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    status: Literal["SATISFIED", "NOT_SATISFIED", "NOT_ASSESSABLE"]
    satisfied_at_tool_call_ordinal: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_status(self) -> "EvidenceRequirementJudgment":
        if self.status == "SATISFIED" and self.satisfied_at_tool_call_ordinal is None:
            raise ValueError("satisfied judgment requires satisfied_at_tool_call_ordinal")
        if self.status != "SATISFIED" and self.satisfied_at_tool_call_ordinal is not None:
            raise ValueError("non-satisfied judgment cannot carry satisfied_at_tool_call_ordinal")
        return self


class AdaptiveStoppingJudgmentPacket(_FrozenModel):
    schema_version: Literal["adaptive-stopping-judgments-v1"] = "adaptive-stopping-judgments-v1"
    status: Literal["FROZEN"] = "FROZEN"
    scenario_id: str = Field(min_length=1)
    trace_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    oracle_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    judgments: tuple[EvidenceRequirementJudgment, ...]
    packet_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_packet(self) -> "AdaptiveStoppingJudgmentPacket":
        identities = [(item.group_id, item.requirement_index) for item in self.judgments]
        if len(set(identities)) != len(identities):
            raise ValueError("adaptive stopping judgment packet contains duplicate requirements")
        expected = _judgment_packet_hash(
            scenario_id=self.scenario_id,
            trace_sha256=self.trace_sha256,
            oracle_sha256=self.oracle_sha256,
            judgments=self.judgments,
        )
        if self.packet_sha256 != expected:
            raise ValueError("adaptive stopping judgment packet hash mismatch")
        return self


class AdaptiveStoppingSelection(_FrozenModel):
    schema_version: Literal["adaptive-stopping-selection-v1"] = "adaptive-stopping-selection-v1"
    status: Literal["FROZEN"] = "FROZEN"
    scenario_ids: tuple[str, ...] = Field(min_length=1)
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_selection(self) -> "AdaptiveStoppingSelection":
        if len(set(self.scenario_ids)) != len(self.scenario_ids):
            raise ValueError("adaptive stopping selection contains duplicate scenarios")
        if any(not item.strip() for item in self.scenario_ids):
            raise ValueError("adaptive stopping selection scenario ids must be non-empty")
        expected = _canonical_sha256(
            {
                "schema_version": self.schema_version,
                "status": self.status,
                "scenario_ids": list(self.scenario_ids),
            }
        )
        if self.selection_sha256 != expected:
            raise ValueError("adaptive stopping selection hash mismatch")
        return self


class AdaptiveStoppingReplayCase(_FrozenModel):
    scenario: Scenario
    trace: RunTrace
    judgments: AdaptiveStoppingJudgmentPacket


class AdaptiveStoppingCaseResult(_FrozenModel):
    case_index: int = Field(ge=0)
    status: Literal[
        "SUFFICIENT_PREFIX_OBSERVED",
        "SUFFICIENCY_NOT_REACHED",
        "NOT_ASSESSABLE",
    ]
    required_group_count: int = Field(ge=0)
    requirement_count: int = Field(ge=0)
    not_assessable_requirement_count: int = Field(ge=0)
    observed_tool_call_count: int = Field(ge=0)
    earliest_sufficient_tool_call_ordinal: int | None = Field(default=None, ge=1)
    post_sufficiency_tool_calls: int | None = Field(default=None, ge=0)
    headroom_fraction: float | None = Field(default=None, ge=0.0, le=1.0)
    first_action_tool_call_ordinal: int | None = Field(default=None, ge=1)
    required_before_action_violation_count: int = Field(ge=0)
    reason_codes: tuple[str, ...] = ()


class AdaptiveStoppingAnalysisResult(_FrozenModel):
    schema_version: Literal["adaptive-stopping-analysis-v1"] = "adaptive-stopping-analysis-v1"
    status: Literal[
        "NOT_READY",
        "PARTIAL_DIAGNOSTIC",
        "HEADROOM_OBSERVED",
        "NO_HEADROOM_OBSERVED",
    ]
    promotion_ready: Literal[False] = False
    runtime_policy_change_authorized: Literal[False] = False
    business_claim_ready: Literal[False] = False
    requires_runtime_challenger_experiment: Literal[True] = True
    source_split: Literal["DEV"] = "DEV"
    frozen_split_schema_version: str = Field(min_length=1)
    frozen_split_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selected_case_count: int = Field(ge=1)
    sufficient_prefix_case_count: int = Field(ge=0)
    insufficiency_case_count: int = Field(ge=0)
    not_assessable_case_count: int = Field(ge=0)
    observed_tool_call_count: int = Field(ge=0)
    post_sufficiency_tool_call_count: int = Field(ge=0)
    mean_post_sufficiency_tool_calls: float | None = Field(default=None, ge=0.0)
    observed_headroom_fraction: float | None = Field(default=None, ge=0.0, le=1.0)
    required_before_action_violation_count: int = Field(ge=0)
    cases: tuple[AdaptiveStoppingCaseResult, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_result(self) -> "AdaptiveStoppingAnalysisResult":
        if self.selected_case_count != len(self.cases):
            raise ValueError("adaptive stopping selected_case_count does not match case results")
        expected = _analysis_hash(self.model_dump(mode="json", exclude={"evidence_sha256"}))
        if self.evidence_sha256 != expected:
            raise ValueError("adaptive stopping analysis evidence hash mismatch")
        return self


def _judgment_packet_hash(
    *,
    scenario_id: str,
    trace_sha256: str,
    oracle_sha256: str,
    judgments: Sequence[EvidenceRequirementJudgment],
) -> str:
    return _canonical_sha256(
        {
            "schema_version": "adaptive-stopping-judgments-v1",
            "status": "FROZEN",
            "scenario_id": scenario_id,
            "trace_sha256": trace_sha256,
            "oracle_sha256": oracle_sha256,
            "judgments": [item.model_dump(mode="json") for item in judgments],
        }
    )


def _analysis_hash(payload: Mapping[str, Any]) -> str:
    return _canonical_sha256(payload)


def _oracle_requirements(
    scenario: Scenario,
) -> tuple[tuple[str, int, EvidenceRequirement], ...]:
    rows: list[tuple[str, int, EvidenceRequirement]] = []
    seen_groups: set[str] = set()
    for group in scenario.evidence_oracle.required_groups:
        if group.group_id in seen_groups:
            raise ValueError(f"duplicate evidence group id: {group.group_id}")
        seen_groups.add(group.group_id)
        if not group.requirements:
            raise ValueError(f"required evidence group has no requirements: {group.group_id}")
        minimum = group.minimum_satisfied or len(group.requirements)
        if minimum > len(group.requirements):
            raise ValueError(
                f"evidence group minimum_satisfied exceeds requirement count: {group.group_id}"
            )
        for index, requirement in enumerate(group.requirements):
            rows.append((group.group_id, index, requirement))
    return tuple(rows)


def freeze_adaptive_stopping_selection(scenario_ids: Sequence[str]) -> AdaptiveStoppingSelection:
    canonical = tuple(sorted(str(item).strip() for item in scenario_ids))
    payload = {
        "schema_version": "adaptive-stopping-selection-v1",
        "status": "FROZEN",
        "scenario_ids": list(canonical),
    }
    return AdaptiveStoppingSelection(
        scenario_ids=canonical,
        selection_sha256=_canonical_sha256(payload),
    )


def freeze_adaptive_stopping_judgments(
    *,
    scenario: Scenario,
    trace: RunTrace,
    judgments: Sequence[EvidenceRequirementJudgment],
) -> AdaptiveStoppingJudgmentPacket:
    if trace.scenario_id != scenario.scenario_id:
        raise ValueError("adaptive stopping trace/scenario mismatch")
    trace_errors = validate_trace(trace)
    if trace_errors:
        raise ValueError("invalid adaptive stopping trace: " + "; ".join(trace_errors))

    expected = _oracle_requirements(scenario)
    supplied = {(item.group_id, item.requirement_index): item for item in judgments}
    if len(supplied) != len(judgments):
        raise ValueError("adaptive stopping judgments contain duplicate requirements")
    if set(supplied) != {(group_id, index) for group_id, index, _ in expected}:
        raise ValueError("adaptive stopping judgments must cover every oracle requirement exactly once")

    tool_call_count = sum(event.event_type == "tool_call" for event in trace.events)
    ordered: list[EvidenceRequirementJudgment] = []
    for group_id, index, requirement in expected:
        judgment = supplied[(group_id, index)]
        if judgment.source != requirement.source or judgment.predicate != requirement.predicate:
            raise ValueError(
                f"adaptive stopping judgment binding mismatch: {group_id}[{index}]"
            )
        ordinal = judgment.satisfied_at_tool_call_ordinal
        if ordinal is not None and ordinal > tool_call_count:
            raise ValueError(
                f"adaptive stopping judgment ordinal exceeds trace tool calls: {group_id}[{index}]"
            )
        ordered.append(judgment)

    trace_hash = _trace_sha256(trace)
    oracle_hash = _oracle_sha256(scenario)
    ordered_tuple = tuple(ordered)
    return AdaptiveStoppingJudgmentPacket(
        scenario_id=scenario.scenario_id,
        trace_sha256=trace_hash,
        oracle_sha256=oracle_hash,
        judgments=ordered_tuple,
        packet_sha256=_judgment_packet_hash(
            scenario_id=scenario.scenario_id,
            trace_sha256=trace_hash,
            oracle_sha256=oracle_hash,
            judgments=ordered_tuple,
        ),
    )


def _group_minimum(group: EvidenceGroup) -> int:
    if not group.requirements:
        raise ValueError(f"required evidence group has no requirements: {group.group_id}")
    minimum = group.minimum_satisfied or len(group.requirements)
    if minimum > len(group.requirements):
        raise ValueError(
            f"evidence group minimum_satisfied exceeds requirement count: {group.group_id}"
        )
    return minimum


def _first_action_tool_call_ordinal(trace: RunTrace) -> int | None:
    ordinal = 0
    for event in trace.events:
        if event.event_type != "tool_call":
            continue
        ordinal += 1
        if not event.tool_name:
            raise ValueError("tool_call event missing tool_name")
        try:
            tool = get_tool(event.tool_name)
        except KeyError as exc:
            raise ValueError(f"unknown tool in adaptive stopping trace: {event.tool_name}") from exc
        if tool.kind is ToolKind.ACTION:
            return ordinal
    return None


def analyze_adaptive_stopping_case(
    *,
    case_index: int,
    replay_case: AdaptiveStoppingReplayCase,
) -> AdaptiveStoppingCaseResult:
    scenario = replay_case.scenario
    trace = replay_case.trace
    packet = replay_case.judgments

    if trace.scenario_id != scenario.scenario_id or packet.scenario_id != scenario.scenario_id:
        raise ValueError("adaptive stopping replay case scenario binding mismatch")
    trace_errors = validate_trace(trace)
    if trace_errors:
        raise ValueError("invalid adaptive stopping trace: " + "; ".join(trace_errors))
    if packet.trace_sha256 != _trace_sha256(trace):
        raise ValueError("adaptive stopping judgment packet does not bind current trace")
    if packet.oracle_sha256 != _oracle_sha256(scenario):
        raise ValueError("adaptive stopping judgment packet does not bind current evidence oracle")

    expected = _oracle_requirements(scenario)
    supplied = {(item.group_id, item.requirement_index): item for item in packet.judgments}
    if set(supplied) != {(group_id, index) for group_id, index, _ in expected}:
        raise ValueError("adaptive stopping packet no longer covers the current oracle exactly")
    for group_id, index, requirement in expected:
        judgment = supplied[(group_id, index)]
        if judgment.source != requirement.source or judgment.predicate != requirement.predicate:
            raise ValueError(f"adaptive stopping judgment binding mismatch: {group_id}[{index}]")

    tool_call_count = sum(event.event_type == "tool_call" for event in trace.events)
    if not scenario.evidence_oracle.required_groups:
        return AdaptiveStoppingCaseResult(
            case_index=case_index,
            status="NOT_ASSESSABLE",
            required_group_count=0,
            requirement_count=0,
            not_assessable_requirement_count=0,
            observed_tool_call_count=tool_call_count,
            required_before_action_violation_count=0,
            reason_codes=("oracle_has_no_required_evidence_groups",),
        )

    group_prefixes: list[int] = []
    blocked_by_unassessable = False
    insufficient = False
    for group in scenario.evidence_oracle.required_groups:
        minimum = _group_minimum(group)
        group_judgments = [
            supplied[(group.group_id, index)] for index in range(len(group.requirements))
        ]
        satisfied_ordinals = sorted(
            item.satisfied_at_tool_call_ordinal
            for item in group_judgments
            if item.status == "SATISFIED" and item.satisfied_at_tool_call_ordinal is not None
        )
        if len(satisfied_ordinals) >= minimum:
            group_prefixes.append(satisfied_ordinals[minimum - 1])
        elif any(item.status == "NOT_ASSESSABLE" for item in group_judgments):
            blocked_by_unassessable = True
        else:
            insufficient = True

    first_action = _first_action_tool_call_ordinal(trace)
    required_before_action_violations = 0
    if first_action is not None:
        for group_id, index, requirement in expected:
            if not requirement.required_before_action:
                continue
            judgment = supplied[(group_id, index)]
            if (
                judgment.status != "SATISFIED"
                or judgment.satisfied_at_tool_call_ordinal is None
                or judgment.satisfied_at_tool_call_ordinal >= first_action
            ):
                required_before_action_violations += 1

    not_assessable_count = sum(item.status == "NOT_ASSESSABLE" for item in packet.judgments)
    if len(group_prefixes) == len(scenario.evidence_oracle.required_groups):
        earliest = max(group_prefixes)
        if earliest > tool_call_count:
            raise ValueError("adaptive stopping sufficient prefix exceeds trace tool calls")
        post = tool_call_count - earliest
        return AdaptiveStoppingCaseResult(
            case_index=case_index,
            status="SUFFICIENT_PREFIX_OBSERVED",
            required_group_count=len(scenario.evidence_oracle.required_groups),
            requirement_count=len(expected),
            not_assessable_requirement_count=not_assessable_count,
            observed_tool_call_count=tool_call_count,
            earliest_sufficient_tool_call_ordinal=earliest,
            post_sufficiency_tool_calls=post,
            headroom_fraction=(post / tool_call_count) if tool_call_count else 0.0,
            first_action_tool_call_ordinal=first_action,
            required_before_action_violation_count=required_before_action_violations,
            reason_codes=(),
        )

    reason_codes: list[str] = []
    if blocked_by_unassessable:
        reason_codes.append("required_group_contains_unassessable_predicate")
    if insufficient:
        reason_codes.append("required_group_not_satisfied_in_full_trace")
    status: Literal["SUFFICIENCY_NOT_REACHED", "NOT_ASSESSABLE"] = (
        "NOT_ASSESSABLE" if blocked_by_unassessable else "SUFFICIENCY_NOT_REACHED"
    )
    return AdaptiveStoppingCaseResult(
        case_index=case_index,
        status=status,
        required_group_count=len(scenario.evidence_oracle.required_groups),
        requirement_count=len(expected),
        not_assessable_requirement_count=not_assessable_count,
        observed_tool_call_count=tool_call_count,
        first_action_tool_call_ordinal=first_action,
        required_before_action_violation_count=required_before_action_violations,
        reason_codes=tuple(reason_codes),
    )


def _dev_scenarios(
    frozen_split_payload: Mapping[str, Any],
) -> tuple[set[str], str, str]:
    schema_version = str(frozen_split_payload.get("schema_version") or "")
    if not schema_version:
        raise ValueError("split manifest missing schema_version")
    if frozen_split_payload.get("status") != "FROZEN":
        raise ValueError("adaptive stopping analysis requires a FROZEN split manifest")
    splits = frozen_split_payload.get("splits")
    if not isinstance(splits, Mapping):
        raise ValueError("split manifest missing splits object")

    assignments: dict[str, str] = {}
    for split_name in ("DEV", "VALIDATION", "LOCKED_TEST"):
        section = splits.get(split_name)
        if not isinstance(section, Mapping):
            raise ValueError(f"split manifest missing {split_name}")
        groups = section.get("groups")
        if not isinstance(groups, list):
            raise ValueError(f"split manifest {split_name} groups must be a list")
        for group in groups:
            if not isinstance(group, Mapping) or not isinstance(group.get("scenarios"), list):
                raise ValueError("split group missing scenarios")
            for scenario in group["scenarios"]:
                scenario_id = str(scenario)
                if scenario_id in assignments:
                    raise ValueError(f"scenario assigned more than once: {scenario_id}")
                assignments[scenario_id] = split_name

    dev = {scenario for scenario, split in assignments.items() if split == "DEV"}
    return dev, schema_version, _canonical_sha256(frozen_split_payload)


def analyze_adaptive_stopping_experiment(
    *,
    selection: AdaptiveStoppingSelection,
    replay_cases: Sequence[AdaptiveStoppingReplayCase],
    frozen_split_payload: Mapping[str, Any],
) -> AdaptiveStoppingAnalysisResult:
    dev_scenarios, split_schema_version, split_sha256 = _dev_scenarios(frozen_split_payload)

    cases_by_scenario: dict[str, AdaptiveStoppingReplayCase] = {}
    for replay_case in replay_cases:
        scenario_id = replay_case.scenario.scenario_id
        if scenario_id in cases_by_scenario:
            raise ValueError(f"adaptive stopping replay contains duplicate scenario: {scenario_id}")
        cases_by_scenario[scenario_id] = replay_case

    if set(cases_by_scenario) != set(selection.scenario_ids):
        raise ValueError("adaptive stopping replay cases must exactly match the frozen selection")
    for scenario_id in selection.scenario_ids:
        if scenario_id not in dev_scenarios:
            raise ValueError(
                f"adaptive stopping experiment is DEV-only; {scenario_id} is not eligible"
            )

    case_results = tuple(
        analyze_adaptive_stopping_case(
            case_index=index,
            replay_case=cases_by_scenario[scenario_id],
        )
        for index, scenario_id in enumerate(selection.scenario_ids)
    )

    sufficient = [item for item in case_results if item.status == "SUFFICIENT_PREFIX_OBSERVED"]
    insufficiency_count = sum(item.status == "SUFFICIENCY_NOT_REACHED" for item in case_results)
    not_assessable_count = sum(item.status == "NOT_ASSESSABLE" for item in case_results)
    total_calls = sum(item.observed_tool_call_count for item in case_results)
    post_calls = sum(item.post_sufficiency_tool_calls or 0 for item in sufficient)
    sufficient_calls = sum(item.observed_tool_call_count for item in sufficient)

    if not sufficient:
        status: Literal[
            "NOT_READY", "PARTIAL_DIAGNOSTIC", "HEADROOM_OBSERVED", "NO_HEADROOM_OBSERVED"
        ] = "NOT_READY"
    elif len(sufficient) != len(case_results):
        status = "PARTIAL_DIAGNOSTIC"
    elif post_calls > 0:
        status = "HEADROOM_OBSERVED"
    else:
        status = "NO_HEADROOM_OBSERVED"

    payload: dict[str, Any] = {
        "schema_version": "adaptive-stopping-analysis-v1",
        "status": status,
        "promotion_ready": False,
        "runtime_policy_change_authorized": False,
        "business_claim_ready": False,
        "requires_runtime_challenger_experiment": True,
        "source_split": "DEV",
        "frozen_split_schema_version": split_schema_version,
        "frozen_split_sha256": split_sha256,
        "selection_sha256": selection.selection_sha256,
        "selected_case_count": len(case_results),
        "sufficient_prefix_case_count": len(sufficient),
        "insufficiency_case_count": insufficiency_count,
        "not_assessable_case_count": not_assessable_count,
        "observed_tool_call_count": total_calls,
        "post_sufficiency_tool_call_count": post_calls,
        "mean_post_sufficiency_tool_calls": (
            float(mean(item.post_sufficiency_tool_calls or 0 for item in sufficient))
            if sufficient
            else None
        ),
        "observed_headroom_fraction": (post_calls / sufficient_calls) if sufficient_calls else None,
        "required_before_action_violation_count": sum(
            item.required_before_action_violation_count for item in case_results
        ),
        "cases": [item.model_dump(mode="json") for item in case_results],
    }
    return AdaptiveStoppingAnalysisResult(
        **payload,
        evidence_sha256=_analysis_hash(payload),
    )
