#!/usr/bin/env python3
"""E8 free-anywhere candidate discovery guard.

This runner does not call external model APIs in default/CI mode. It only checks
which remote-free or local candidate slots are explicitly enabled in the current
environment while preserving the project-wide USD 0 constraint.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


DATE = "2026-08-16"
STATUS = "E8_FREE_ANYWHERE_CANDIDATE_DISCOVERY_PASS"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def env_flag(name: str) -> bool:
    return os.getenv(name, "").strip() == "1"


def has_env(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def candidate(slot_id: str, kind: str, available: bool, reason: str, *, external: bool, cost_usd: float | None = 0.0, blocked: bool = False) -> dict[str, Any]:
    return {
        "slot_id": slot_id,
        "kind": kind,
        "available": available,
        "blocked": blocked,
        "reason": reason,
        "external_model_calls_if_executed": external,
        "cost_usd": cost_usd,
    }


def discover_candidates() -> list[dict[str, Any]]:
    zero_confirmed = env_flag("E8_CONFIRM_ZERO_COST")

    candidates: list[dict[str, Any]] = [
        candidate(
            "no_model_policy_baseline",
            "built_in_baseline",
            True,
            "always available, deterministic and USD 0",
            external=False,
            cost_usd=0.0,
        )
    ]

    groq_ready = has_env("GROQ_API_KEY") and env_flag("E8_ENABLE_GROQ") and zero_confirmed
    candidates.append(
        candidate(
            "groq_free_api",
            "remote_hosted_api",
            groq_ready,
            "available only with GROQ_API_KEY, E8_ENABLE_GROQ=1 and E8_CONFIRM_ZERO_COST=1" if not groq_ready else "explicit free Groq opt-in detected",
            external=True,
            cost_usd=0.0,
        )
    )

    gemini_key = has_env("GEMINI_API_KEY") or has_env("GOOGLE_API_KEY")
    gemini_ready = gemini_key and env_flag("E8_ENABLE_GEMINI") and zero_confirmed
    candidates.append(
        candidate(
            "gemini_free_api",
            "remote_hosted_api",
            gemini_ready,
            "available only with GEMINI_API_KEY or GOOGLE_API_KEY, E8_ENABLE_GEMINI=1 and E8_CONFIRM_ZERO_COST=1" if not gemini_ready else "explicit free Gemini opt-in detected",
            external=True,
            cost_usd=0.0,
        )
    )

    openrouter_ready = has_env("OPENROUTER_API_KEY") and env_flag("E8_ENABLE_OPENROUTER_FREE") and zero_confirmed
    candidates.append(
        candidate(
            "openrouter_free_router",
            "remote_free_model_router",
            openrouter_ready,
            "available only with OPENROUTER_API_KEY, E8_ENABLE_OPENROUTER_FREE=1 and E8_CONFIRM_ZERO_COST=1" if not openrouter_ready else "explicit OpenRouter free-model opt-in detected",
            external=True,
            cost_usd=0.0,
        )
    )

    hf_ready = has_env("HF_TOKEN") and env_flag("E8_ENABLE_HUGGINGFACE") and zero_confirmed
    candidates.append(
        candidate(
            "huggingface_free_inference",
            "remote_inference_provider_credits",
            hf_ready,
            "available only with HF_TOKEN, E8_ENABLE_HUGGINGFACE=1 and E8_CONFIRM_ZERO_COST=1; must be bounded to free credits" if not hf_ready else "explicit Hugging Face free-credit opt-in detected",
            external=True,
            cost_usd=0.0,
        )
    )

    ollama_ready = has_env("OLLAMA_HOST") and env_flag("E8_ENABLE_OLLAMA")
    candidates.append(
        candidate(
            "ollama_local_optional",
            "local_runtime",
            ollama_ready,
            "available only with OLLAMA_HOST and E8_ENABLE_OLLAMA=1" if not ollama_ready else "explicit local Ollama opt-in detected",
            external=False,
            cost_usd=0.0,
        )
    )

    candidates.append(
        candidate(
            "openai_reference_optional",
            "paid_reference",
            False,
            "blocked because the project must remain completely free",
            external=False,
            cost_usd=None,
            blocked=True,
        )
    )
    candidates.append(
        candidate(
            "anthropic_reference_optional",
            "paid_reference",
            False,
            "blocked because the project must remain completely free",
            external=False,
            cost_usd=None,
            blocked=True,
        )
    )

    return candidates


def run(manifest_path: Path, split_manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    split_manifest = load_json(split_manifest_path)

    split_keys = set(split_manifest.get("splits", {}).keys())
    allowed = ["DEV", "VALIDATION"]
    forbidden = ["LOCKED_TEST"]
    if not set(allowed).issubset(split_keys):
        raise ValueError(f"missing required allowed splits: {allowed}; found {sorted(split_keys)}")
    if not set(forbidden).issubset(split_keys):
        raise ValueError(f"missing forbidden split metadata: {forbidden}; found {sorted(split_keys)}")

    candidates = discover_candidates()
    available = [c["slot_id"] for c in candidates if c["available"]]
    enabled_remote = [c["slot_id"] for c in candidates if c["available"] and c["external_model_calls_if_executed"]]
    blocked_paid = [c["slot_id"] for c in candidates if c.get("blocked")]

    # In this discovery guard, no external model calls are made. An actual model
    # benchmark must be executed by a user-controlled run after enabling a free
    # provider explicitly.
    external_calls_made = False
    project_cost_limit_usd = manifest.get("budget_policy", {}).get("project_cost_limit_usd", 0)
    if project_cost_limit_usd != 0:
        raise ValueError("E8 free-anywhere discovery requires project_cost_limit_usd == 0")

    paid_enabled = bool(env_flag("E8_ENABLE_OPENAI") or env_flag("E8_ENABLE_ANTHROPIC"))
    if paid_enabled:
        raise ValueError("paid candidates are blocked under the completely-free project constraint")

    return {
        "report_version": "e8-free-anywhere-candidate-discovery-summary-v1",
        "date": DATE,
        "status": STATUS,
        "free_anywhere_scope": True,
        "locality_required": False,
        "remote_free_apis_allowed": True,
        "local_systems_allowed": True,
        "project_cost_limit_usd": 0,
        "paid_models_enabled": False,
        "external_model_calls_made": external_calls_made,
        "default_ci_makes_external_model_calls": False,
        "candidate_availability": candidates,
        "available_candidate_slots": available,
        "available_remote_free_candidate_slots": enabled_remote,
        "blocked_paid_candidate_slots": blocked_paid,
        "scope": {
            "allowed_splits": allowed,
            "forbidden_splits": forbidden,
            "locked_test_accessed": False,
            "dev_smoke_before_validation": True,
        },
        "constants_preserved": manifest.get("constants_preserved", {}),
        "next_gate": "Run E8 DEV smoke with any actually available free remote API or local system, then VALIDATION after DEV pass.",
        "interpretation_limits": [
            "This discovery guard broadens E8 beyond local candidates.",
            "It does not prove external model quality because default CI makes no external model calls.",
            "Groq, Gemini, OpenRouter or Hugging Face can be used only with explicit free/zero-cost opt-in.",
            "OpenAI and Anthropic remain blocked by the completely-free project constraint.",
        ],
        "final_architecture_freeze": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    summary = run(args.manifest, args.split_manifest)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
