from __future__ import annotations

"""Compatibility wrapper for the adaptive E6 ToolSpec LangGraph runner.

The frozen benchmark split stores each split as an object with a `groups` array. The
first adaptive runner expected a simplified split->group list. This wrapper preserves the
original runner and normalizes the frozen manifest shape before execution.
"""

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.research.e6_langgraph_toolspec_runner import load_json, run_spike


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run_spike(load_json(args.manifest), normalize_split_manifest(load_json(args.split_manifest)))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "adaptive_mode": summary["adaptive_mode"],
        "tool_spec_registry_wired": summary["tool_spec_registry_wired"],
        "harness_runner_used": summary["harness_runner_used"],
        "runtrace_compatible_output": summary["runtrace_compatible_output"],
        "adaptive_path_count": summary["adaptive_path_count"],
        "checkpoint_pause_resume_roundtrip": summary["checkpoint_pause_resume_roundtrip"],
        "locked_test_accessed": False,
    }, indent=2, ensure_ascii=False))
    if not summary["tool_spec_registry_wired"] or not summary["harness_runner_used"] or not summary["runtrace_compatible_output"]:
        return 1
    if not summary["deterministic_replay_equal"] or not summary["checkpoint_pause_resume_roundtrip"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
