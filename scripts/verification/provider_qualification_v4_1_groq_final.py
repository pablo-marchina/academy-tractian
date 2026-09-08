#!/usr/bin/env python3
from __future__ import annotations

"""Final single-provider qualification for Groq GPT-OSS-120B.

This runner intentionally reuses the frozen V4 population, attempt function, rubric, candidate
summary, hard gates, and V4 single-eligible-candidate selection semantics. It removes Cloudflare
from execution because the user explicitly chose to proceed without it. Therefore the resulting
claim is a Groq qualification, not a comparative provider tournament result.
"""

from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any

ENTRY_PATH = Path(__file__).with_name("provider_tournament_v4_final_frozen.py")
SPEC = importlib.util.spec_from_file_location("provider_tournament_v4_final_frozen_entry", ENTRY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load frozen V4 entry")
entry = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = entry
SPEC.loader.exec_module(entry)
core = entry.core

MANIFEST_REL = "research/experiments/provider-qualification-v4-1-groq-final-manifest.json"
EXPECTED_MANIFEST_SCHEMA = "provider-qualification-v4-1-groq-final-manifest-v1"
EXPECTED_POPULATION_SHA256 = "4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9"
CANDIDATE_ID = "groq-gpt-oss-120b"
ATTEMPTS = 85
RESULT_SCHEMA = "provider-qualification-v4-1-groq-final-result-v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _load_qualification_manifest(root: Path) -> dict[str, Any]:
    payload = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
    if payload.get("schema_version") != EXPECTED_MANIFEST_SCHEMA:
        raise RuntimeError("qualification manifest schema drift")
    if payload.get("status") != "FROZEN":
        raise RuntimeError("qualification manifest is not frozen")
    inherited = payload.get("inherits_from") or {}
    if inherited.get("population_sha256") != EXPECTED_POPULATION_SHA256:
        raise RuntimeError("qualification population hash drift")
    candidate = payload.get("candidate") or {}
    if candidate.get("candidate_id") != CANDIDATE_ID:
        raise RuntimeError("qualification candidate drift")
    population = payload.get("population") or {}
    if population.get("attempt_count") != ATTEMPTS:
        raise RuntimeError("qualification attempt geometry drift")
    if payload.get("pre_scored_attempts") != 0:
        raise RuntimeError("qualification requires zero pre-scored attempts")
    return payload


def _install_frozen_serving_normalizations() -> None:
    # Same serving-boundary normalizations used by the frozen V4 entry. No scoring changes.
    entry._install_tournament_specific_cloudflare_credentials()
    core.ProviderCallIdentity = entry._safe_provider_call_identity
    core._audit_integrity = entry._safe_audit_integrity
    core.OpenAICompatTournamentClient.build_http_request = entry._build_http_request_with_explicit_user_agent
    core._attempt = entry._attempt_with_provider_pacing


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    qualification_manifest = _load_qualification_manifest(root)
    comparative_manifest = core._load_manifest(root)
    bundle = core.load_frozen_tournament_v3(root)
    registry = core.canonical_tool_registry()

    _install_frozen_serving_normalizations()

    item = next(
        item for item in comparative_manifest["candidates"] if item["candidate_id"] == CANDIDATE_ID
    )
    candidate = core._candidate_from_manifest(item, env=os.environ)

    plan = [row for row in core._plan() if row[0] == CANDIDATE_ID]
    if len(plan) != ATTEMPTS:
        raise RuntimeError(f"qualification plan geometry mismatch: {len(plan)}")

    output_dir = Path(os.environ.get("TOURNAMENT_OUTPUT_DIR", "/tmp/provider-qualification-v4-1-groq"))
    output_dir.mkdir(parents=True, exist_ok=True)
    attempts_path = output_dir / "attempts.jsonl"
    result_path = output_dir / "result.json"
    if attempts_path.exists() or result_path.exists():
        raise RuntimeError("qualification output directory must be empty; resume/rerun is forbidden")

    attempts: list[dict[str, Any]] = []
    for attempt_index, (_, unit_index, repetition_index) in enumerate(plan):
        unit_id = bundle.population["units"][unit_index]["unit_id"]
        row = core._attempt(
            bundle=bundle,
            registry=registry,
            candidate=candidate,
            unit_id=unit_id,
            unit_index=unit_index,
            repetition_index=repetition_index,
            attempt_index=attempt_index,
        )
        attempts.append(row)
        with attempts_path.open("a", encoding="utf-8") as handle:
            handle.write(core._canonical_json(row) + "\n")
        print("PROVIDER_QUALIFICATION_ATTEMPT=" + core._canonical_json(row), flush=True)

    if len(attempts) != ATTEMPTS:
        raise RuntimeError("qualification attempt count mismatch")

    summary = core._candidate_summary(CANDIDATE_ID, attempts)
    selection, reason = core._select({CANDIDATE_ID: summary})
    if summary["hard_gate_pass"] and selection != f"PROMOTE:{CANDIDATE_ID}":
        raise RuntimeError("single-candidate selection semantics drift")
    if not summary["hard_gate_pass"] and selection != "NO_SELECTION":
        raise RuntimeError("failed hard gates must produce NO_SELECTION")

    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA,
        "status": "COMPLETE",
        "qualification_id": qualification_manifest["qualification_id"],
        "baseline_git_sha": comparative_manifest["source_baseline"]["git_sha"],
        "qualification_manifest_sha256": _sha(qualification_manifest),
        "population_sha256": EXPECTED_POPULATION_SHA256,
        "attempt_count": len(attempts),
        "candidate_summary": summary,
        "selection": selection,
        "selection_reason": reason,
        "comparative_provider_claim": False,
        "production_promotion_authorized": False,
        "winner_e2e_required": selection.startswith("PROMOTE:"),
        "raw_provider_material_recorded": False,
    }
    result["attempts_sha256"] = sha256(attempts_path.read_bytes()).hexdigest()
    result["evidence_sha256"] = _sha(result)
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PROVIDER_QUALIFICATION_RESULT=" + _canonical(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
