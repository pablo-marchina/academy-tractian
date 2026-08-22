#!/usr/bin/env python3
"""E14r full-DEV deterministic public visible-case evidence route selector.

Single-class intervention over the fixed E14q2 full-DEV outputs. The guard may
change only evidence_plan. Route selection uses the exact runner-selected
agent-visible case, the already-fixed public action state, and the public tool
registry/signature parser. It never reads private expected paths, scorer rows,
semantic judge rows, VALIDATION feedback, LOCKED_TEST content, split coverage
tags, or group/ticket-specific evidence rules.

E14r is intentionally a planner/serializer layer experiment, not a claim that
the underlying model reasoning improved.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).parent
Q2_PATH = HERE / "e14q2_full_dev_public_route_role_purpose_consistency_guard.py"
Q2_SPEC = importlib.util.spec_from_file_location("e14q2_parent_for_e14r", Q2_PATH)
if Q2_SPEC is None or Q2_SPEC.loader is None:
    raise RuntimeError("failed to load E14q2 parent")
q2 = importlib.util.module_from_spec(Q2_SPEC)
Q2_SPEC.loader.exec_module(q2)

BASE_PATH = HERE / "e8_free_anywhere_model_runner.py"
BASE_SPEC = importlib.util.spec_from_file_location("e8_visible_case_loader_for_e14r", BASE_PATH)
if BASE_SPEC is None or BASE_SPEC.loader is None:
    raise RuntimeError("failed to load agent-visible case loader")
base = importlib.util.module_from_spec(BASE_SPEC)
BASE_SPEC.loader.exec_module(base)

v41 = q2.v41
v4 = q2.v4
EXPECTED_CALLS = 10
PASS_STATUS = "E14R_FULL_DEV_PUBLIC_VISIBLE_CASE_EVIDENCE_ROUTE_SELECTION_GUARD_PASS"
FAIL_STATUS = "E14R_FULL_DEV_PUBLIC_VISIBLE_CASE_EVIDENCE_ROUTE_SELECTION_GUARD_NEEDS_REVIEW"
MAX_SELECTED_READS = 8

READ_ORDER = [
    "GET /users/me",
    "GET /assets/{assetId}",
    "GET /assets/{assetId}/analyses",
    "GET /analyses/{analysisId}",
    "GET /assets/{assetId}/baseline",
    "GET /assets/{assetId}/data-quality",
    "GET /assets/{assetId}/rms",
    "GET /assets/{assetId}/spectrum",
    "GET /models/{modelId}",
    "GET /knowledge/search",
    "GET /knowledge/{docId}",
]
READ_SET = set(READ_ORDER)

CORE_NON_CONTEXTUAL = {
    "GET /assets/{assetId}",
    "GET /assets/{assetId}/analyses",
    "GET /analyses/{analysisId}",
}
CONTEXTUAL_CORE = {
    "GET /knowledge/search",
    "GET /knowledge/{docId}",
}

CONTEXTUALIZE_CUES = (
    "contextualize",
    "contextualise",
    "contextualization",
    "contextualisation",
    "glossary",
    "procedure",
    "meaning of",
    "what does",
    "source fidelity",
)

CUE_FAMILIES: dict[str, tuple[str, ...]] = {
    "baseline": (
        "baseline",
        "alarm threshold",
        "threshold",
        "learn baseline",
        "learning baseline",
        "baseline invalid",
        "baseline stale",
    ),
    "data_quality": (
        "data quality",
        "missing data",
        "data missing",
        "unavailable",
        "incomplete data",
        "partial data",
        "signal quality",
        "low quality",
        "confidence",
    ),
    "rms": (
        "rms",
        "vibration trend",
        "amplitude",
        "time series",
        "severity trend",
    ),
    "spectrum": (
        "spectrum",
        "frequency",
        "frequency band",
        "band missing",
        "bands missing",
        "harmonic",
        "electrical",
        "mechanical",
    ),
    "model": (
        "model",
        "drift",
        "retrain",
        "retraining",
        "false positive",
        "false negative",
        "coverage",
        "model delayed",
    ),
    "knowledge": (
        "procedure",
        "glossary",
        "knowledge",
        "guidance",
        "documentation",
        "source fidelity",
        "meaning of",
    ),
}

CUE_ROUTES: dict[str, tuple[str, ...]] = {
    "baseline": ("GET /assets/{assetId}/baseline",),
    "data_quality": ("GET /assets/{assetId}/data-quality",),
    "rms": ("GET /assets/{assetId}/rms",),
    "spectrum": ("GET /assets/{assetId}/spectrum",),
    "model": ("GET /models/{modelId}",),
    "knowledge": ("GET /knowledge/search", "GET /knowledge/{docId}"),
}

ACTION_DEPENDENCY_READS: dict[str, tuple[str, ...]] = {
    "POST /analyses/{analysisId}/reprocess": ("GET /analyses/{analysisId}",),
    "POST /analyses/{analysisId}/request-specialist": ("GET /analyses/{analysisId}",),
    "POST /models/{modelId}/request-retraining": ("GET /models/{modelId}",),
    "PATCH /assets/{assetId}": ("GET /assets/{assetId}",),
    "POST /cases/{caseId}/escalate": (),
}

EVIDENCE_ITEM_TEXT: dict[str, str] = {
    "GET /users/me": "GET /users/me to verify the current user's public authorization context before an active state-changing step.",
    "GET /assets/{assetId}": "GET /assets/{assetId} to inspect the asset state relevant to the visible case.",
    "GET /assets/{assetId}/analyses": "GET /assets/{assetId}/analyses to identify the analyses relevant to the visible case.",
    "GET /analyses/{analysisId}": "GET /analyses/{analysisId} to inspect the relevant analysis before drawing a conclusion or taking an action.",
    "GET /assets/{assetId}/baseline": "GET /assets/{assetId}/baseline to inspect baseline or threshold context explicitly implicated by the visible case.",
    "GET /assets/{assetId}/data-quality": "GET /assets/{assetId}/data-quality to inspect data completeness and trustworthiness implicated by the visible case.",
    "GET /assets/{assetId}/rms": "GET /assets/{assetId}/rms to inspect the RMS or time-series signal evidence implicated by the visible case.",
    "GET /assets/{assetId}/spectrum": "GET /assets/{assetId}/spectrum to inspect frequency-domain evidence implicated by the visible case.",
    "GET /models/{modelId}": "GET /models/{modelId} to inspect model state when model behavior, coverage, drift, or retraining is implicated by the visible case.",
    "GET /knowledge/search": "GET /knowledge/search to locate public guidance or procedural material implicated by the visible case.",
    "GET /knowledge/{docId}": "GET /knowledge/{docId} to inspect the selected public knowledge source before relying on its guidance.",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _string_values(child)


def _visible_text(case: dict[str, Any]) -> str:
    return "\n".join(_string_values(case)).lower()


def _non_evidence_signature(output: dict[str, Any]) -> dict[str, Any]:
    cloned = copy.deepcopy(output)
    cloned.pop("evidence_plan", None)
    return cloned


def _observed_read_signatures(output: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    plan = output.get("evidence_plan")
    if not isinstance(plan, list):
        return result
    for item in plan:
        if not isinstance(item, str):
            continue
        for signature, kind in v41.canonical_tool_signatures(item, require_method=True):
            if kind == "read":
                result.add(signature)
    return result


def _active_action_endpoint(output: dict[str, Any]) -> str | None:
    if output.get("should_take_action_now") is not True:
        return None
    return q2.parent._action_endpoint(output)


def _has_any(text: str, cues: tuple[str, ...]) -> bool:
    return any(cue in text for cue in cues)


def selected_read_signatures(visible_case: dict[str, Any], output: dict[str, Any]) -> tuple[list[str], list[str]]:
    text = _visible_text(visible_case)
    contextualize = _has_any(text, CONTEXTUALIZE_CUES)
    selected: set[str] = set(CONTEXTUAL_CORE if contextualize else CORE_NON_CONTEXTUAL)
    reasons: list[str] = ["contextualize_core" if contextualize else "non_contextual_core"]

    for family, cues in CUE_FAMILIES.items():
        if _has_any(text, cues):
            selected.update(CUE_ROUTES[family])
            reasons.append(f"visible_case_cue:{family}")

    endpoint = _active_action_endpoint(output)
    if endpoint:
        selected.add("GET /users/me")
        reasons.append("active_action:authorization")
        for signature in ACTION_DEPENDENCY_READS.get(endpoint, ()):
            selected.add(signature)
            reasons.append("active_action:target_read")

    # This intervention intentionally excludes company/list-assets routes and
    # any unknown read route. The stable order is public-registry-derived and
    # the preregistered cap prevents broad evidence expansion.
    ordered = [signature for signature in READ_ORDER if signature in selected]
    ordered = ordered[:MAX_SELECTED_READS]
    return ordered, reasons


def _evidence_items(signatures: list[str]) -> list[str]:
    return [EVIDENCE_ITEM_TEXT[signature] for signature in signatures]


def transform_output(output: dict[str, Any], visible_case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    before = copy.deepcopy(output)
    result = copy.deepcopy(output)
    before_reads = _observed_read_signatures(before)
    selected, reasons = selected_read_signatures(visible_case, before)
    result["evidence_plan"] = _evidence_items(selected)
    after_reads = _observed_read_signatures(result)

    non_evidence_preserved = _non_evidence_signature(before) == _non_evidence_signature(result)
    selected_set = set(selected)
    exact_selected_routes = after_reads == selected_set
    each_item_exactly_one_read = all(
        len([pair for pair in v41.canonical_tool_signatures(item, require_method=True) if pair[1] == "read"]) == 1
        and not any(pair[1] == "action" for pair in v41.canonical_tool_signatures(item, require_method=True))
        for item in result.get("evidence_plan", [])
        if isinstance(item, str)
    )
    return result, {
        "changed": before.get("evidence_plan") != result.get("evidence_plan"),
        "before_read_count": len(before_reads),
        "after_read_count": len(after_reads),
        "added_read_count": len(after_reads - before_reads),
        "removed_read_count": len(before_reads - after_reads),
        "non_evidence_preserved": non_evidence_preserved,
        "exact_selected_routes": exact_selected_routes,
        "each_item_exactly_one_read": each_item_exactly_one_read,
        "selected_read_count_within_cap": len(after_reads) <= MAX_SELECTED_READS,
        "reasons": reasons,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    fixed = _load(args.fixed_output_file)
    split_manifest = _load(args.split_manifest)
    if not isinstance(fixed, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("fixed output and split manifest must be objects")

    transformed = copy.deepcopy(fixed)
    calls = v4.collect_calls(transformed)
    v4.assert_fixed_scope(transformed, calls, split_manifest)
    if len(calls) != EXPECTED_CALLS:
        raise AssertionError(f"E14r requires exactly {EXPECTED_CALLS} fixed full-DEV calls")

    visible_cases = base.load_agent_visible_cases(args.agent_input_cases)
    fixed_groups = {str(call.get("group_id")) for call in calls if call.get("group_id")}
    selected_cases = {group: visible_cases.get(group) for group in fixed_groups}
    missing_visible = sorted(group for group, case in selected_cases.items() if not isinstance(case, dict))
    if missing_visible:
        raise AssertionError("E14r requires one runner-selected visible case for every fixed DEV group")

    parsed = 0
    calls_changed = 0
    before_reads_total = 0
    after_reads_total = 0
    added_reads_total = 0
    removed_reads_total = 0
    non_evidence_changes = 0
    route_contract_failures = 0
    cap_failures = 0
    reason_counts: Counter[str] = Counter()

    for call in calls:
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        group = str(call.get("group_id") or "")
        visible_case = selected_cases.get(group)
        if not isinstance(visible_case, dict):
            continue
        parsed += 1
        guarded, meta = transform_output(output, visible_case)
        calls_changed += int(meta["changed"])
        before_reads_total += int(meta["before_read_count"])
        after_reads_total += int(meta["after_read_count"])
        added_reads_total += int(meta["added_read_count"])
        removed_reads_total += int(meta["removed_read_count"])
        non_evidence_changes += int(not meta["non_evidence_preserved"])
        route_contract_failures += int(not (meta["exact_selected_routes"] and meta["each_item_exactly_one_read"]))
        cap_failures += int(not meta["selected_read_count_within_cap"])
        for reason in meta["reasons"]:
            reason_counts[str(reason)] += 1
        call["parsed_output"] = guarded

    complete = parsed == EXPECTED_CALLS and len(fixed_groups) == 5 and not missing_visible
    passed = complete and non_evidence_changes == 0 and route_contract_failures == 0 and cap_failures == 0
    status = PASS_STATUS if passed else FAIL_STATUS

    transformed["report_version"] = "e14r-full-dev-public-visible-case-evidence-route-selection-v1"
    transformed["status"] = status
    transformed["e14r_public_visible_case_evidence_route_selection"] = {
        "provider_calls_made": 0,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "fixed_groups_found": len(fixed_groups),
        "runner_selected_visible_cases_for_fixed_groups": len(selected_cases) - len(missing_visible),
        "complete_fixed_transform": complete,
        "calls_changed": calls_changed,
        "public_read_signatures_before_total": before_reads_total,
        "public_read_signatures_after_total": after_reads_total,
        "public_read_signatures_added_total": added_reads_total,
        "public_read_signatures_removed_total": removed_reads_total,
        "route_selection_reason_counts": dict(sorted(reason_counts.items())),
        "max_selected_reads_per_call": MAX_SELECTED_READS,
        "non_evidence_field_changes": non_evidence_changes,
        "route_contract_failures": route_contract_failures,
        "selected_read_cap_failures": cap_failures,
        "group_or_ticket_specific_rules_used": False,
        "split_coverage_tags_used": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "semantic_judge_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "validation_gate_authorized": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(transformed, indent=2), encoding="utf-8")

    return {
        "report_version": transformed["report_version"],
        "status": status,
        **transformed["e14r_public_visible_case_evidence_route_selection"],
        "raw_outputs_printed": False,
        "visible_case_values_printed": False,
        "evidence_items_printed": False,
        "identifiers_printed": False,
        "group_ids_printed": False,
        "hashes_printed": False,
        "private_paths_printed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--agent-input-cases", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
