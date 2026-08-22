#!/usr/bin/env python3
"""E14v isolated public evidence-route planner.

The planner is a narrow architecture-stage experiment. It sees only the exact
runner-selected visible case, public action-state fields, and a frozen public
GET-route catalog. It never sees the parent evidence_plan, private expected
paths, scorer rows, semantic labels, VALIDATION, or LOCKED_TEST.

Two modes exist:
- synthetic: qualify the planner on the frozen public synthetic suite;
- dev: replace only evidence_plan in the fixed E14p full-DEV parent.

Real provider outputs are local artifacts and must not be committed.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
REPO = HERE.parent.parent

# Reuse only public case-loading/signature/serialization helpers.
import importlib.util

E14R_PATH = HERE / "e14r_full_dev_public_visible_case_evidence_route_selection_guard.py"
SPEC = importlib.util.spec_from_file_location("e14r_public_helpers_for_e14v", E14R_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14r public helpers")
e14r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14r)

v4 = e14r.v4
q2 = e14r.q2
base = e14r.base

PREREG = Path("research/experiments/e14v-full-dev-isolated-public-evidence-route-planner-preregistration.json")
SYNTHETIC_FIXTURE = Path("research/fixtures/e14v-public-evidence-route-planner-synthetic-v1.json")
MODEL = "openai/gpt-oss-120b"
REASONING_EFFORT = "medium"
TEMPERATURE = 0.0
MAX_COMPLETION_TOKENS = 1024
BETWEEN_CALL_DELAY_SECONDS = 25.0
MAX_RETRIES = 2
MAX_READS = 7
EXPECTED_DEV_CALLS = 10
EXPECTED_DEV_GROUPS = 5
LOCK_SUFFIX = ".attempt-lock.json"

PASS_SYNTHETIC = "E14V_PUBLIC_SYNTHETIC_ROUTE_PLANNER_QUALIFICATION_PASS"
FAIL_SYNTHETIC = "E14V_PUBLIC_SYNTHETIC_ROUTE_PLANNER_QUALIFICATION_FAIL"
PASS_DEV = "E14V_FULL_DEV_ISOLATED_PUBLIC_EVIDENCE_ROUTE_PLANNER_PASS"
FAIL_DEV = "E14V_FULL_DEV_ISOLATED_PUBLIC_EVIDENCE_ROUTE_PLANNER_NEEDS_REVIEW"

READ_ORDER = list(e14r.READ_ORDER)
READ_SET = set(READ_ORDER)
EVIDENCE_ITEM_TEXT = dict(e14r.EVIDENCE_ITEM_TEXT)

PAID_ENV_MARKERS = (
    "E8_ENABLE_OPENAI",
    "E8_ENABLE_ANTHROPIC",
    "OPENAI_API_KEY_FOR_E8",
    "ANTHROPIC_API_KEY_FOR_E8",
)

SYSTEM_PROMPT = """You are a route-selection planner for a public maintenance API.
Return JSON only with exactly one key: reads.
reads must be a JSON array containing the smallest complete set of canonical GET METHOD+path strings needed to resolve the visible task and support the supplied public action state.
Use only routes in the supplied catalog. Never emit action routes. Never emit identifiers or concrete values. Never emit more than 7 distinct reads.
Do not use a route merely because it exists. Each selected route must resolve a concrete dependency in the visible task or a required dependency of an active state-changing action.
For an active action, include GET /users/me plus the public target-state read required by that action. For knowledge grounding, select GET /knowledge/search before GET /knowledge/{docId}. Return no explanation outside the JSON object."""

ROUTE_PURPOSE = {
    "GET /users/me": "current-user authorization context for an active state-changing action",
    "GET /assets/{assetId}": "current asset state",
    "GET /assets/{assetId}/analyses": "identify analyses belonging to an asset",
    "GET /analyses/{analysisId}": "inspect a specific analysis state/result",
    "GET /assets/{assetId}/baseline": "baseline, threshold, or reference-state evidence",
    "GET /assets/{assetId}/data-quality": "input completeness, reliability, or data-quality evidence",
    "GET /assets/{assetId}/rms": "RMS, amplitude, time-domain, or trend evidence",
    "GET /assets/{assetId}/spectrum": "frequency-domain, harmonic, or spectrum evidence",
    "GET /models/{modelId}": "model state, drift, coverage, performance, or retraining target state",
    "GET /knowledge/search": "find public procedural/domain guidance",
    "GET /knowledge/{docId}": "inspect a selected public knowledge document"
}

ACTION_TARGET_READ = {
    "POST /analyses/{analysisId}/reprocess": "GET /analyses/{analysisId}",
    "POST /analyses/{analysisId}/request-specialist": "GET /analyses/{analysisId}",
    "POST /models/{modelId}/request-retraining": "GET /models/{modelId}",
    "PATCH /assets/{assetId}": "GET /assets/{assetId}",
    "POST /cases/{caseId}/escalate": None,
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def assert_preregistration(path: Path = PREREG) -> dict[str, Any]:
    manifest = _load(path)
    if not isinstance(manifest, dict):
        raise AssertionError("E14v preregistration must be an object")
    if manifest.get("experiment_id") != "E14v-full-DEV-isolated-public-evidence-route-planner":
        raise AssertionError("wrong E14v preregistration")
    if manifest.get("intervention_class") != "isolated_public_evidence_route_planner_only":
        raise AssertionError("E14v intervention class changed")
    planner = manifest.get("planner")
    if not isinstance(planner, dict) or planner.get("model") != MODEL:
        raise AssertionError("E14v planner model changed")
    if planner.get("temperature") != 0 or planner.get("reasoning_effort") != REASONING_EFFORT:
        raise AssertionError("E14v planner generation configuration changed")
    response = planner.get("response_contract")
    if not isinstance(response, dict) or int(response.get("max_distinct_reads") or 0) != MAX_READS:
        raise AssertionError("E14v route cap changed")
    if manifest.get("public_read_catalog") != READ_ORDER:
        raise AssertionError("E14v public read catalog changed")
    scope = manifest.get("scope")
    if not isinstance(scope, dict) or scope.get("measurement_splits") != ["DEV"]:
        raise AssertionError("E14v must remain DEV-only")
    if set(scope.get("forbidden_splits") or []) != {"VALIDATION", "LOCKED_TEST"}:
        raise AssertionError("E14v must forbid VALIDATION and LOCKED_TEST")
    return manifest


def assert_zero_cost_real() -> None:
    enabled_paid = [name for name in PAID_ENV_MARKERS if os.getenv(name)]
    if enabled_paid:
        raise AssertionError(f"paid provider envs must be disabled: {enabled_paid}")
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise AssertionError("E14v real provider call requires E8_CONFIRM_ZERO_COST=1")
    if os.getenv("E8_ENABLE_GROQ") != "1":
        raise AssertionError("E14v requires E8_ENABLE_GROQ=1")
    if not os.getenv("GROQ_API_KEY"):
        raise AssertionError("E14v requires GROQ_API_KEY")
    configured = os.getenv("E8_GROQ_MODEL", MODEL)
    if configured != MODEL:
        raise AssertionError(f"E14v requires E8_GROQ_MODEL={MODEL}")
    temp = float(os.getenv("E8_MODEL_TEMPERATURE", "0"))
    if temp != TEMPERATURE:
        raise AssertionError("E14v requires E8_MODEL_TEMPERATURE=0")


def _attempt_lock(out: Path, mode: str) -> Path:
    return Path(str(out) + LOCK_SUFFIX)


def consume_attempt(out: Path, mode: str) -> Path:
    lock = _attempt_lock(out, mode)
    if out.exists():
        raise SystemExit("E14v output already exists; rerun is forbidden")
    if lock.exists():
        raise SystemExit("E14v attempt already consumed; rerun requires an explicit amendment")
    _write(lock, {
        "report_version": "e14v-attempt-lock-v1",
        "experiment_id": "E14v-full-DEV-isolated-public-evidence-route-planner",
        "mode": mode,
        "status": "E14V_ATTEMPT_CONSUMED",
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "temperature": TEMPERATURE,
        "rerun_allowed": False,
        "contains_raw_output": False,
        "contains_private_oracle": False,
        "contains_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    })
    return lock


def _request_json(payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _provider_call(user_payload: dict[str, Any], timeout: int) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, separators=(",", ":"))},
        ],
        "temperature": TEMPERATURE,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "reasoning_effort": REASONING_EFFORT,
        "response_format": {"type": "json_object"},
    }
    last_error: str | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = _request_json(payload, timeout)
            content = response["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else None, {
                "transport_attempts": attempt + 1,
                "model": MODEL,
                "usage": response.get("usage", {}),
                "error": None,
            }
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
            last_error = type(exc).__name__
            if attempt >= MAX_RETRIES:
                break
            time.sleep(2.0 * (attempt + 1))
    return None, {"transport_attempts": MAX_RETRIES + 1, "model": MODEL, "usage": {}, "error": last_error}


def _action_state(output: dict[str, Any]) -> dict[str, Any]:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    endpoint = rubric.get("action_endpoint")
    return {
        "decision_class": output.get("decision_class"),
        "should_take_action_now": output.get("should_take_action_now"),
        "requires_human_escalation": output.get("requires_human_escalation"),
        "action_endpoint": endpoint if isinstance(endpoint, str) else "none",
    }


def _planner_packet(visible_case: dict[str, Any], action_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "visible_case": visible_case,
        "public_action_state": action_state,
        "public_get_routes": [{"route": route, "purpose": ROUTE_PURPOSE[route]} for route in READ_ORDER],
        "output_contract": {"reads": "array of unique canonical GET routes", "max_distinct_reads": MAX_READS},
    }


def validate_reads(parsed: dict[str, Any] | None) -> tuple[list[str] | None, dict[str, Any]]:
    if not isinstance(parsed, dict) or set(parsed.keys()) != {"reads"}:
        return None, {"valid": False, "reason": "wrong_object_shape"}
    reads = parsed.get("reads")
    if not isinstance(reads, list) or not all(isinstance(item, str) for item in reads):
        return None, {"valid": False, "reason": "reads_not_string_array"}
    duplicate_count = len(reads) - len(set(reads))
    unknown = [item for item in reads if item not in READ_SET]
    action_like = [item for item in reads if not item.startswith("GET ")]
    over_cap = len(reads) > MAX_READS
    valid = duplicate_count == 0 and not unknown and not action_like and not over_cap
    return (list(reads) if valid else None), {
        "valid": valid,
        "reason": None if valid else "route_contract_failure",
        "duplicate_count": duplicate_count,
        "unknown_count": len(unknown),
        "action_like_count": len(action_like),
        "over_cap": over_cap,
    }


def _synthetic_action_dependencies(case: dict[str, Any]) -> set[str]:
    action = case.get("action_state")
    action = action if isinstance(action, dict) else {}
    if action.get("should_take_action_now") is not True:
        return set()
    endpoint = action.get("action_endpoint")
    deps = {"GET /users/me"}
    target = ACTION_TARGET_READ.get(str(endpoint))
    if target:
        deps.add(target)
    return deps


def run_synthetic(args: argparse.Namespace) -> dict[str, Any]:
    manifest = assert_preregistration(args.manifest)
    fixture = _load(args.synthetic_fixture)
    cases = fixture.get("cases") if isinstance(fixture, dict) else None
    if not isinstance(cases, list) or len(cases) != 14:
        raise AssertionError("E14v synthetic fixture must contain exactly 14 cases")

    if not args.dry_run:
        assert_zero_cost_real()
        consume_attempt(args.out, "synthetic")

    rows: list[dict[str, Any]] = []
    valid_count = 0
    exact_count = 0
    expected_total = 0
    expected_hit_total = 0
    extras_total = 0
    action_dep_total = 0
    action_dep_hit_total = 0
    unknown_total = 0
    duplicate_total = 0
    cap_failures = 0

    for index, case in enumerate(cases):
        if index and not args.dry_run:
            time.sleep(BETWEEN_CALL_DELAY_SECONDS)
        visible = case.get("visible_case")
        action = case.get("action_state")
        expected = case.get("expected_reads")
        if not isinstance(visible, dict) or not isinstance(action, dict) or not isinstance(expected, list):
            raise AssertionError("malformed E14v synthetic case")
        if args.dry_run:
            parsed = {"reads": list(expected)}
            provider_meta = {"transport_attempts": 0, "model": MODEL, "usage": {}, "error": None, "dry_run": True}
        else:
            parsed, provider_meta = _provider_call(_planner_packet(visible, action), args.timeout_seconds)
        reads, meta = validate_reads(parsed)
        selected = set(reads or [])
        expected_set = set(str(item) for item in expected)
        deps = _synthetic_action_dependencies(case)
        valid_count += int(meta["valid"])
        exact_count += int(meta["valid"] and selected == expected_set)
        expected_total += len(expected_set)
        expected_hit_total += len(selected & expected_set)
        extras_total += len(selected - expected_set)
        action_dep_total += len(deps)
        action_dep_hit_total += len(selected & deps)
        unknown_total += int(meta.get("unknown_count") or 0)
        duplicate_total += int(meta.get("duplicate_count") or 0)
        cap_failures += int(bool(meta.get("over_cap")))
        rows.append({
            "case_id": case.get("id"),
            "selected_reads": reads,
            "expected_reads": expected,
            "route_contract": meta,
            "provider_meta": provider_meta,
        })

    n = len(cases)
    valid_rate = valid_count / n
    exact_rate = exact_count / n
    recall = expected_hit_total / expected_total if expected_total else 1.0
    action_recall = action_dep_hit_total / action_dep_total if action_dep_total else 1.0
    mean_extras = extras_total / n
    gate = manifest["synthetic_qualification"]
    passed = (
        valid_rate >= float(gate["required_valid_output_rate"])
        and recall >= float(gate["required_route_recall"])
        and action_recall >= float(gate["required_action_dependency_recall"])
        and exact_rate >= float(gate["required_exact_set_match_rate_min"])
        and mean_extras <= float(gate["required_mean_extra_reads_max"])
        and unknown_total == 0
        and duplicate_total == 0
        and cap_failures == 0
    )
    result = {
        "report_version": "e14v-public-synthetic-route-planner-qualification-v1",
        "status": PASS_SYNTHETIC if passed else FAIL_SYNTHETIC,
        "dry_run": args.dry_run,
        "provider": "groq_zero_cost" if not args.dry_run else "none",
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "temperature": TEMPERATURE,
        "synthetic_cases": n,
        "valid_output_rate": round(valid_rate, 4),
        "route_recall": round(recall, 4),
        "action_dependency_recall": round(action_recall, 4),
        "exact_set_match_rate": round(exact_rate, 4),
        "mean_extra_reads": round(mean_extras, 4),
        "unknown_route_count": unknown_total,
        "duplicate_route_count": duplicate_total,
        "read_cap_violations": cap_failures,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "rows": rows,
    }
    _write(args.out, result)
    return result


def _non_evidence_signature(output: dict[str, Any]) -> dict[str, Any]:
    clone = copy.deepcopy(output)
    clone.pop("evidence_plan", None)
    return clone


def run_dev(args: argparse.Namespace) -> dict[str, Any]:
    if args.dry_run:
        raise AssertionError("DEV dry-run is intentionally unsupported; use synthetic dry-run/selfcheck before real DEV")
    assert_preregistration(args.manifest)
    assert_zero_cost_real()
    if args.fixed_output_file is None or args.agent_input_cases is None:
        raise AssertionError("DEV mode requires --fixed-output-file and --agent-input-cases")

    fixed = _load(args.fixed_output_file)
    split_manifest = _load(args.split_manifest)
    if not isinstance(fixed, dict) or fixed.get("status") != "E14P_FULL_DEV_PUBLIC_EPISTEMIC_SERIALIZATION_GUARD_PASS":
        raise AssertionError("E14v DEV parent must be the fixed E14p full-DEV serialized output")
    if not isinstance(split_manifest, dict):
        raise AssertionError("split manifest must be an object")

    transformed = copy.deepcopy(fixed)
    calls = v4.collect_calls(transformed)
    v4.assert_fixed_scope(transformed, calls, split_manifest)
    if len(calls) != EXPECTED_DEV_CALLS:
        raise AssertionError("E14v requires exactly 10 fixed DEV calls")

    visible_cases = base.load_agent_visible_cases(args.agent_input_cases)
    groups = [str(call.get("group_id") or "") for call in calls]
    counts = Counter(groups)
    if len(counts) != EXPECTED_DEV_GROUPS or any(value != 2 for value in counts.values()):
        raise AssertionError("E14v requires 5 DEV groups x 2 repeats")
    for group in counts:
        if not isinstance(visible_cases.get(group), dict):
            raise AssertionError("E14v requires one runner-selected visible case for every fixed DEV group")

    consume_attempt(args.out, "dev")

    parsed = 0
    valid = 0
    calls_changed = 0
    non_evidence_changes = 0
    selected_total = 0
    max_selected = 0
    min_selected = MAX_READS
    route_contract_failures = 0
    provider_failures = 0

    for index, call in enumerate(calls):
        if index:
            time.sleep(BETWEEN_CALL_DELAY_SECONDS)
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            route_contract_failures += 1
            continue
        parsed += 1
        group = str(call.get("group_id") or "")
        visible = visible_cases[group]
        action_state = _action_state(output)
        planner_output, provider_meta = _provider_call(_planner_packet(visible, action_state), args.timeout_seconds)
        reads, meta = validate_reads(planner_output)
        if provider_meta.get("error") is not None:
            provider_failures += 1
        if reads is None:
            route_contract_failures += 1
            continue
        valid += 1
        before_non_evidence = _non_evidence_signature(output)
        before_plan = copy.deepcopy(output.get("evidence_plan"))
        output["evidence_plan"] = [EVIDENCE_ITEM_TEXT[route] for route in reads]
        if before_plan != output.get("evidence_plan"):
            calls_changed += 1
        if before_non_evidence != _non_evidence_signature(output):
            non_evidence_changes += 1
        selected_total += len(reads)
        max_selected = max(max_selected, len(reads))
        min_selected = min(min_selected, len(reads))

    complete = parsed == EXPECTED_DEV_CALLS and valid == EXPECTED_DEV_CALLS
    passed = complete and route_contract_failures == 0 and provider_failures == 0 and non_evidence_changes == 0 and max_selected <= MAX_READS
    status = PASS_DEV if passed else FAIL_DEV
    transformed["report_version"] = "e14v-full-dev-isolated-public-evidence-route-planner-v1"
    transformed["status"] = status
    transformed["e14v_isolated_public_evidence_route_planner"] = {
        "provider": "groq_zero_cost",
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "temperature": TEMPERATURE,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "valid_planner_outputs": valid,
        "fixed_groups_found": len(counts),
        "repeats_per_group": 2,
        "complete_fixed_transform": complete,
        "calls_changed": calls_changed,
        "selected_read_signatures_total": selected_total,
        "mean_selected_reads_per_call": round(selected_total / EXPECTED_DEV_CALLS, 4),
        "max_selected_reads_observed": max_selected,
        "min_selected_reads_observed": 0 if min_selected == MAX_READS and valid == 0 else min_selected,
        "max_selected_reads_allowed": MAX_READS,
        "route_contract_failures": route_contract_failures,
        "provider_failures": provider_failures,
        "non_evidence_field_changes": non_evidence_changes,
        "existing_parent_evidence_plan_exposed_to_planner": False,
        "group_or_ticket_specific_rules_used": False,
        "split_coverage_tags_used": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "semantic_judge_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "validation_gate_authorized": False,
    }
    _write(args.out, transformed)
    return {
        "report_version": transformed["report_version"],
        "status": status,
        **transformed["e14v_isolated_public_evidence_route_planner"],
        "raw_outputs_printed": False,
        "visible_case_values_printed": False,
        "selected_routes_printed": False,
        "identifiers_printed": False,
        "group_ids_printed": False,
        "private_paths_printed": False,
    }


def run_self_checks() -> None:
    manifest = assert_preregistration(PREREG)
    fixture = _load(SYNTHETIC_FIXTURE)
    cases = fixture.get("cases") if isinstance(fixture, dict) else None
    if not isinstance(cases, list) or len(cases) != manifest["synthetic_qualification"]["required_cases"]:
        raise AssertionError("synthetic case count does not match preregistration")
    if set(ROUTE_PURPOSE) != READ_SET:
        raise AssertionError("route-purpose catalog mismatch")
    for case in cases:
        expected = case.get("expected_reads")
        if not isinstance(expected, list) or not expected or len(expected) > MAX_READS:
            raise AssertionError("invalid synthetic expected read set")
        if len(expected) != len(set(expected)) or any(route not in READ_SET for route in expected):
            raise AssertionError("synthetic expected routes violate public catalog")
        parsed, meta = validate_reads({"reads": expected})
        if parsed != expected or not meta["valid"]:
            raise AssertionError("route validator rejected valid synthetic expectation")
    invalids = [
        {"reads": ["POST /cases/{caseId}/escalate"]},
        {"reads": ["GET /not-public"]},
        {"reads": ["GET /assets/{assetId}", "GET /assets/{assetId}"]},
        {"reads": READ_ORDER[:8]},
        {"reads": [1]},
        {"reads": [] , "extra": true} if False else {"reads": [], "extra": True},
    ]
    for item in invalids:
        _reads, meta = validate_reads(item)
        if meta["valid"]:
            raise AssertionError("route validator accepted an invalid output")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("synthetic", "dev"), required=True)
    parser.add_argument("--manifest", type=Path, default=PREREG)
    parser.add_argument("--synthetic-fixture", type=Path, default=SYNTHETIC_FIXTURE)
    parser.add_argument("--fixed-output-file", type=Path, default=None)
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        run_self_checks()
        print(json.dumps({"status": "E14V_ISOLATED_PUBLIC_EVIDENCE_ROUTE_PLANNER_SELFCHECK_PASS"}, indent=2))
        return 0

    result = run_synthetic(args) if args.mode == "synthetic" else run_dev(args)
    if args.mode == "synthetic":
        printable = {key: value for key, value in result.items() if key != "rows"}
    else:
        printable = result
    print(json.dumps(printable, indent=2))
    expected = PASS_SYNTHETIC if args.mode == "synthetic" else PASS_DEV
    return 0 if result.get("status") == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
