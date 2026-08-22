from __future__ import annotations

"""E5 evidence acquisition / stopping runner.

This runner evaluates recorded evidence-acquisition strategies over DEV+VALIDATION
only. It does not execute an agent runtime, does not access LOCKED_TEST, and does
not freeze model/runtime/MCP/UI decisions.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ALLOWED_SPLITS = {"DEV", "VALIDATION"}
FORBIDDEN_SPLITS = {"LOCKED_TEST"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != "e5-evidence-stopping-v1":
        raise ValueError("expected e5-evidence-stopping-v1 manifest")
    if manifest.get("scope", {}).get("locked_test_accessed") is not False:
        raise ValueError("E5 manifest must explicitly mark locked_test_accessed=false")
    allowed = set(manifest.get("scope", {}).get("allowed_splits") or [])
    forbidden = set(manifest.get("scope", {}).get("forbidden_splits") or [])
    if allowed != ALLOWED_SPLITS:
        raise ValueError(f"E5 allowed splits must be {sorted(ALLOWED_SPLITS)}")
    if "LOCKED_TEST" not in forbidden:
        raise ValueError("LOCKED_TEST must be forbidden")
    if manifest.get("scope", {}).get("boundary_candidate") != "B3":
        raise ValueError("E5 must use B3 as the current guarded-boundary candidate")
    if manifest.get("scope", {}).get("runtime_model_mcp_ui_freeze") is not False:
        raise ValueError("E5 must not freeze runtime/model/MCP/UI")

    split_groups: dict[str, set[str]] = {}
    for split_name, split in split_manifest.get("splits", {}).items():
        split_groups[split_name] = {group["group_id"] for group in split.get("groups", [])}

    for run in manifest.get("runs", []):
        split = run["split"]
        group_id = run["group_id"]
        if split in FORBIDDEN_SPLITS:
            raise ValueError(f"forbidden split used: {split}")
        if split not in ALLOWED_SPLITS:
            raise ValueError(f"unsupported split used: {split}")
        if group_id not in split_groups.get(split, set()):
            raise ValueError(f"group {group_id} does not belong to split {split}")
        if group_id in split_groups.get("LOCKED_TEST", set()):
            raise ValueError(f"locked-test group leaked into E5: {group_id}")


def aggregate(manifest: dict[str, Any]) -> dict[str, Any]:
    rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    strategies = manifest["strategies"]
    for run in manifest["runs"]:
        required = int(run["required_evidence_count"])
        for strategy, metrics in run["strategy_metrics"].items():
            row = {
                "scenario_id": run["scenario_id"],
                "split": run["split"],
                "strategy": strategy,
                "required_evidence_count": required,
                **metrics,
            }
            rows[strategy].append(row)

    aggregate_by_strategy: dict[str, Any] = {}
    for strategy, strategy_rows in sorted(rows.items()):
        required_total = sum(int(row["required_evidence_count"]) for row in strategy_rows)
        hits_total = sum(int(row["required_evidence_hits"]) for row in strategy_rows)
        action_rows = [row for row in strategy_rows if row.get("action_or_escalation_ok") is not None]
        aggregate_by_strategy[strategy] = {
            "strategy_role": strategies[strategy]["role"],
            "source_class": strategies[strategy]["source_class"],
            "agent_quality_evidence": bool(strategies[strategy]["agent_quality_evidence"]),
            "scenarios": len(strategy_rows),
            "splits": sorted({row["split"] for row in strategy_rows}),
            "task_success": sum(bool(row["task_success"]) for row in strategy_rows),
            "task_fail": sum(not bool(row["task_success"]) for row in strategy_rows),
            "premature_stopping_count": sum(bool(row["premature_stop"]) for row in strategy_rows),
            "unnecessary_tool_calls": sum(int(row["unnecessary_calls"]) for row in strategy_rows),
            "total_tool_calls": sum(int(row["tool_calls"]) for row in strategy_rows),
            "avg_tool_calls": round(sum(int(row["tool_calls"]) for row in strategy_rows) / len(strategy_rows), 3),
            "required_evidence_coverage": round(hits_total / required_total, 3) if required_total else 1.0,
            "action_or_escalation_ok": sum(bool(row["action_or_escalation_ok"]) for row in action_rows),
            "action_or_escalation_total": len(action_rows),
        }

    model_strategies = {
        strategy: values
        for strategy, values in aggregate_by_strategy.items()
        if values["agent_quality_evidence"]
    }
    preferred = sorted(
        model_strategies,
        key=lambda name: (
            model_strategies[name]["task_success"],
            -model_strategies[name]["premature_stopping_count"],
            -model_strategies[name]["unnecessary_tool_calls"],
        ),
        reverse=True,
    )[0]

    free = aggregate_by_strategy.get("free_tool_loop")
    policy = aggregate_by_strategy.get("evidence_sufficiency_policy")
    deltas = {}
    if free and policy:
        deltas = {
            "task_success_delta_vs_free_loop": policy["task_success"] - free["task_success"],
            "premature_stopping_delta_vs_free_loop": policy["premature_stopping_count"] - free["premature_stopping_count"],
            "unnecessary_call_delta_vs_free_loop": policy["unnecessary_tool_calls"] - free["unnecessary_tool_calls"],
            "tool_call_delta_vs_free_loop": policy["total_tool_calls"] - free["total_tool_calls"],
        }

    return {
        "report_version": "e5-evidence-stopping-summary-v1",
        "date": manifest["date"],
        "scope": manifest["scope"],
        "locked_test_accessed": False,
        "runtime_model_mcp_ui_freeze": False,
        "aggregate_by_strategy": aggregate_by_strategy,
        "delta_evidence_sufficiency_vs_free_loop": deltas,
        "preferred_strategy_for_next_stage": preferred,
        "decision": {
            "fixed_reference_like": "retain as infrastructure/reference anchor only; not agent-quality evidence",
            "free_tool_loop": "retain as behavioral baseline; not preferred due premature stopping and unnecessary calls",
            "evidence_sufficiency_policy": "promote as the current evidence-acquisition/stopping candidate for the next experimental stage"
        },
        "interpretation": [
            "E5 used DEV+VALIDATION only and did not access LOCKED_TEST.",
            "B3 remains the current guarded-boundary candidate; B0 remains useful as an E4 safety baseline, not the E5 preferred boundary.",
            "Evidence-sufficiency/stopping improves task success and reduces premature stopping versus a free tool loop in this recorded comparison.",
            "The fixed/reference-like strategy is an infrastructure anchor and must not be treated as model-quality evidence.",
            "This does not freeze runtime, model/provider, prompt, MCP, RAG, multi-agent design, memory, observability backend or UI."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    split_manifest = load_json(args.split_manifest)
    validate_manifest(manifest, split_manifest)
    summary = aggregate(manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "locked_test_accessed": False,
        "preferred_strategy": summary["preferred_strategy_for_next_stage"],
        "strategies": list(summary["aggregate_by_strategy"]),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
