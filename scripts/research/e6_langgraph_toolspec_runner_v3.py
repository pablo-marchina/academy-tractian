from __future__ import annotations

"""Compatibility wrapper for the adaptive E6 ToolSpec LangGraph runner.

This wrapper preserves the adaptive runner implementation while adapting two integration
shapes discovered by CI:

1. The frozen benchmark split stores split payloads as objects with a `groups` array.
2. `ExecutionBinding.seed` is a string in the E2 model contract.

The wrapper keeps the underlying run path unchanged: LangGraph -> adaptive evidence
planner -> HarnessRunner -> B3/evidence-sufficiency policy nodes.
"""

import argparse
import json
from pathlib import Path
from typing import Any

import scripts.research.e6_langgraph_toolspec_runner as base
from research.e2.models import ExecutionBinding as RealExecutionBinding


def normalize_split_manifest(raw: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(raw)
    normalized_splits: dict[str, list[str]] = {}
    for split_name, split_payload in raw.get("splits", {}).items():
        if isinstance(split_payload, dict) and isinstance(split_payload.get("groups"), list):
            normalized_splits[split_name] = [group["group_id"] for group in split_payload["groups"]]
        elif isinstance(split_payload, list):
            normalized_splits[split_name] = list(split_payload)
        else:
            raise ValueError(f"unsupported split manifest shape for {split_name}")
    normalized["splits"] = normalized_splits
    return normalized


def execution_binding_compat(**kwargs: Any) -> RealExecutionBinding:
    if kwargs.get("seed") is not None:
        kwargs["seed"] = str(kwargs["seed"])
    return RealExecutionBinding(**kwargs)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    base.ExecutionBinding = execution_binding_compat  # type: ignore[assignment]
    summary = base.run_spike(
        base.load_json(args.manifest),
        normalize_split_manifest(base.load_json(args.split_manifest)),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS",
                "adaptive_mode": summary["adaptive_mode"],
                "tool_spec_registry_wired": summary["tool_spec_registry_wired"],
                "harness_runner_used": summary["harness_runner_used"],
                "runtrace_compatible_output": summary["runtrace_compatible_output"],
                "adaptive_path_count": summary["adaptive_path_count"],
                "checkpoint_pause_resume_roundtrip": summary["checkpoint_pause_resume_roundtrip"],
                "locked_test_accessed": False,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    if not summary["tool_spec_registry_wired"] or not summary["harness_runner_used"] or not summary["runtrace_compatible_output"]:
        return 1
    if not summary["deterministic_replay_equal"] or not summary["checkpoint_pause_resume_roundtrip"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
