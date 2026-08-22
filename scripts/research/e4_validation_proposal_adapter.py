from __future__ import annotations

"""E4 VALIDATION proposal adapter.

This adapter executes recorded model/agent proposal plans on the frozen VALIDATION
split only. It intentionally rejects LOCKED_TEST and DEV so validation selection
cannot be mixed with debugging or final holdout data.

It reuses the E4 B0-B3 boundary machinery and emits boundary metrics only. The
private VALIDATION evaluator is combined separately and must not commit gold.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.research.e4_model_proposal_adapter import (  # noqa: E402
    VARIANTS,
    load_json,
    load_split_manifest,
    parse_run,
    require_model_agent_source,
    run_variant,
)

VALIDATION_ONLY = {"VALIDATION"}
LOCKED_SPLITS = {"LOCKED_TEST"}


def assert_validation_split_only(manifest: dict[str, Any], split: str) -> set[str]:
    if split in LOCKED_SPLITS:
        raise ValueError("LOCKED_TEST is forbidden for E4 validation proposal adapter")
    if split not in VALIDATION_ONLY:
        raise ValueError(f"E4 validation proposal adapter is VALIDATION-only, got {split!r}")
    groups = manifest.get("splits", {}).get(split, {}).get("groups") or []
    if not groups:
        raise ValueError(f"split {split!r} not found or empty")
    return {group["group_id"] for group in groups}


def run_adapter(*, split_manifest: Path, proposal_plan: Path, split: str) -> dict[str, Any]:
    manifest = load_split_manifest(split_manifest)
    allowed_groups = assert_validation_split_only(manifest, split)
    plan = load_json(proposal_plan)
    source = require_model_agent_source(plan)
    if plan.get("split") != split:
        raise ValueError(f"proposal plan split {plan.get('split')!r} does not match requested split {split!r}")
    runs = [parse_run(raw, allowed_groups=allowed_groups) for raw in plan.get("runs", [])]
    if not runs:
        raise ValueError("validation proposal plan contains no runs")
    variant_metrics = [run_variant(run=run, variant=variant, split=split, source=source) for run in runs for variant in VARIANTS]
    return {
        "report_version": "e4-validation-proposal-adapter-v1",
        "split": split,
        "locked_test_accessed": False,
        "proposal_source": source,
        "agent_quality_evidence": True,
        "task_success_evidence": False,
        "task_success_evidence_reason": "The adapter exports B0-B3 boundary metrics only. Full task/conclusion success is combined with the private VALIDATION evaluator locally.",
        "runs": len(runs),
        "variants": [metric.__dict__ for metric in variant_metrics],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--proposal-plan", type=Path, required=True)
    parser.add_argument("--split", default="VALIDATION")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    report = run_adapter(split_manifest=args.split_manifest, proposal_plan=args.proposal_plan, split=args.split)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "report_version": report["report_version"],
        "split": report["split"],
        "runs": report["runs"],
        "variant_rows": len(report["variants"]),
        "agent_quality_evidence": report["agent_quality_evidence"],
        "task_success_evidence": report["task_success_evidence"],
        "locked_test_accessed": report["locked_test_accessed"],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
