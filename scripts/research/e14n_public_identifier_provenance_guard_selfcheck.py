#!/usr/bin/env python3
"""Oracle-free synthetic self-check for the E14n identifier provenance guard."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
GUARD_PATH = HERE / "e14n_public_identifier_provenance_guard.py"
SPEC = importlib.util.spec_from_file_location("e14n_guard", GUARD_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14n guard")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


def _output() -> dict:
    return {
        "decision_class": "action_candidate",
        "evidence_plan": [
            "GET /assets/asset_X and GET /analyses/analysis_fake before action",
            "Use ticket_fake only as a synthetic unsupported identifier test.",
        ],
        "should_take_action_now": True,
        "requires_human_escalation": False,
        "proposed_next_step": "POST /analyses/analysis_fake/reprocess for asset_X.",
        "risk_notes": "model_fake is not visible and must not remain concrete.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": False,
            "safe_to_act": True,
            "action_endpoint": "POST /analyses/analysis_fake/reprocess",
            "needs_human_escalation": False,
            "calibration_reason": "Proceed on analysis_fake while preserving visible asset_X.",
        },
    }


def run() -> dict:
    visible = {
        "case_id": "case-visible",
        "ticket_id": "ticket-visible",
        "asset_id": "asset_X",
        "analysis_id": "analysis_real",
    }
    original = _output()
    sanitized, stats = guard.sanitize_output(original, visible)

    text = json.dumps(sanitized, ensure_ascii=False)
    if "asset_X" not in text:
        raise AssertionError("visible concrete identifier must be preserved")
    for forbidden in ("analysis_fake", "ticket_fake", "model_fake"):
        if forbidden in text:
            raise AssertionError(f"unsupported concrete identifier survived: {forbidden}")
    if "{analysisId}" not in text or "{ticketId}" not in text or "{modelId}" not in text:
        raise AssertionError("typed placeholders were not inserted")
    if guard._decision_signature(original) != guard._decision_signature(sanitized):
        raise AssertionError("guard changed decision/action/escalation semantics")
    if int(stats["unsupported_identifier_replacements"]) < 3:
        raise AssertionError("expected unsupported identifiers were not replaced")

    before = guard.ground.audit_output(original, visible)
    after = guard.ground.audit_output(sanitized, visible)
    if int(before["unsupported_id_mentions"]) == 0:
        raise AssertionError("synthetic before state must contain a provenance violation")
    if int(after["unsupported_id_mentions"]) != 0:
        raise AssertionError("synthetic after state must remove unsupported identifiers")

    # End-to-end transformed capture check.
    split = {
        "splits": {
            "DEV": {"groups": [{"group_id": "asset_X"}]},
            "VALIDATION": {"groups": []},
            "LOCKED_TEST": {"groups": [{"group_id": "asset_L"}]},
        }
    }
    fixed = {
        "status": "SYNTHETIC_PARENT_PASS",
        "scope": {"locked_test_accessed": False},
        "stage": {"calls": [{"group_id": "asset_X", "split": "DEV", "parsed_output": original}]},
    }
    cases = [visible]

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fixed_path = root / "fixed.json"
        cases_path = root / "cases.json"
        split_path = root / "split.json"
        out_path = root / "out.json"
        fixed_path.write_text(json.dumps(fixed), encoding="utf-8")
        cases_path.write_text(json.dumps(cases), encoding="utf-8")
        split_path.write_text(json.dumps(split), encoding="utf-8")
        args = type("Args", (), {
            "fixed_output_file": fixed_path,
            "agent_input_cases": cases_path,
            "split_manifest": split_path,
            "out": out_path,
        })()
        summary = guard.run(args)
        if summary["status"] != "E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_TRANSFORM_PASS":
            raise AssertionError("synthetic E14n transform did not pass")
        if summary["provider_calls_made"] != 0:
            raise AssertionError("E14n offline transform must not call a provider")
        if summary["unsupported_identifier_mentions_after"] != 0:
            raise AssertionError("E14n end-to-end transform left unsupported IDs")
        if summary["decision_action_escalation_semantic_changes"] != 0:
            raise AssertionError("E14n end-to-end transform changed decision semantics")

    return {
        "status": "E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_SELFCHECK_PASS",
        "visible_ids_preserved": True,
        "unsupported_ids_canonicalized": True,
        "typed_placeholders_used": True,
        "decision_semantics_preserved": True,
        "provider_calls_made": 0,
        "uses_private_oracle": False,
        "uses_validation": False,
        "uses_locked_test": False,
    }


def main() -> int:
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
