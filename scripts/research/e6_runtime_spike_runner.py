from __future__ import annotations

"""E6 runtime discriminating spike runner.

This script evaluates a preregistered runtime scorecard under the frozen project
constraints. It does not import runtime frameworks, call models, inspect private
gold, or touch LOCKED_TEST. It produces ADR-direction evidence only.
"""

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_CRITERIA = {
    "trace_completeness",
    "guard_integration",
    "replay_determinism",
    "pause_resume_hitl",
    "lower_complexity",
    "portability",
    "lower_overhead",
}

FORBIDDEN_DECISIONS = {
    "freeze_model_provider",
    "freeze_mcp_topology",
    "freeze_rag_or_vector_db",
    "freeze_multi_agent_decomposition",
    "freeze_ui_or_demo_flow",
    "touch_locked_test",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != "e6-runtime-spike-manifest-v1":
        raise ValueError("expected e6-runtime-spike-manifest-v1")
    scope = manifest.get("scope") or {}
    if scope.get("locked_test_accessed") is not False:
        raise ValueError("E6 manifest must not access LOCKED_TEST")
    if "LOCKED_TEST" not in set(scope.get("forbidden_splits") or []):
        raise ValueError("LOCKED_TEST must be explicitly forbidden")
    if scope.get("tool_spec_constant") is not True:
        raise ValueError("ToolSpec must remain constant")
    if scope.get("boundary_candidate") != "B3":
        raise ValueError("E6 must carry B3 as the current guarded-boundary candidate")
    if scope.get("stopping_policy_candidate") != "evidence_sufficiency_policy":
        raise ValueError("E6 must carry the E5 evidence-sufficiency policy")
    for key in ["model_provider_freeze", "mcp_topology_freeze", "rag_freeze", "multi_agent_freeze", "ui_freeze"]:
        if scope.get(key) is not False:
            raise ValueError(f"E6 must not freeze {key}")

    weights = manifest.get("criteria_weights") or {}
    if set(weights) != REQUIRED_CRITERIA:
        raise ValueError(f"criteria weights mismatch: {sorted(set(weights) ^ REQUIRED_CRITERIA)}")
    total = sum(float(value) for value in weights.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"criteria weights must sum to 1.0, got {total}")

    forbidden = set((manifest.get("decision_rules") or {}).get("forbidden_decisions") or [])
    missing = FORBIDDEN_DECISIONS - forbidden
    if missing:
        raise ValueError(f"missing forbidden decision rules: {sorted(missing)}")

    candidates = manifest.get("candidates") or []
    if {candidate.get("candidate_id") for candidate in candidates} != {"langgraph", "pydantic_ai_graph", "openai_agents_sdk"}:
        raise ValueError("E6 must compare LangGraph, Pydantic AI/Graph and OpenAI Agents SDK")
    for candidate in candidates:
        scores = candidate.get("scores") or {}
        if set(scores) != REQUIRED_CRITERIA:
            raise ValueError(f"candidate {candidate.get('candidate_id')} score keys mismatch")
        for criterion, value in scores.items():
            numeric = float(value)
            if numeric < 0 or numeric > 5:
                raise ValueError(f"candidate {candidate.get('candidate_id')} has out-of-range score for {criterion}")


def score_candidate(candidate: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    scores = candidate["scores"]
    weighted_score = sum(float(scores[key]) * float(weights[key]) for key in REQUIRED_CRITERIA)
    return {
        "candidate_id": candidate["candidate_id"],
        "display_name": candidate["display_name"],
        "weighted_score": round(weighted_score, 3),
        "scores": scores,
        "rationale": candidate.get("rationale", []),
        "evidence_anchors": candidate.get("evidence_anchors", []),
    }


def run(manifest: dict[str, Any]) -> dict[str, Any]:
    validate_manifest(manifest)
    weights = {key: float(value) for key, value in manifest["criteria_weights"].items()}
    ranked = sorted((score_candidate(candidate, weights) for candidate in manifest["candidates"]), key=lambda row: row["weighted_score"], reverse=True)
    preferred = ranked[0]
    return {
        "report_version": "e6-runtime-spike-summary-v1",
        "date": manifest["date"],
        "scope": manifest["scope"],
        "locked_test_accessed": False,
        "runtime_candidate_selected": preferred["candidate_id"],
        "runtime_candidate_display_name": preferred["display_name"],
        "runtime_model_mcp_ui_freeze": False,
        "weights": weights,
        "ranking": ranked,
        "decision": {
            "langgraph": "promote as current runtime candidate for the next integration stage",
            "pydantic_ai_graph": "retain as typed/schema-native fallback and useful design comparator",
            "openai_agents_sdk": "retain as provider-native comparator; revisit if model/provider later becomes OpenAI-centered"
        },
        "interpretation": [
            "LangGraph ranks first because replay/checkpointing, pause/resume and HITL are the strongest discriminators for the current B3 + evidence-sufficiency bundle.",
            "Pydantic AI/Graph remains close and valuable because typed validation, graph support and OpenTelemetry/eval alignment match the existing Pydantic-heavy harness.",
            "OpenAI Agents SDK is attractive for low ceremony, built-in tracing, guardrails, HITL and MCP, but provider portability is weaker while model/provider remains intentionally unfrozen.",
            "This selects a current runtime candidate only; it does not freeze model, MCP topology, RAG/vector DB, multi-agent design, observability backend or UI.",
            "LOCKED_TEST remains blocked."
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    summary = run(load_json(args.manifest))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "runtime_candidate": summary["runtime_candidate_selected"],
        "weighted_score": summary["ranking"][0]["weighted_score"],
        "locked_test_accessed": False,
        "runtime_model_mcp_ui_freeze": False,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
