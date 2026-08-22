#!/usr/bin/env python3
"""Oracle-free synthetic checks for the E9 v4.1 groundedness surface audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
AUDIT_PATH = HERE / "e9_v4_1_groundedness_surface_diagnostic.py"
SPEC = importlib.util.spec_from_file_location("e9_v41_ground_surface", AUDIT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load groundedness surface diagnostic")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def _output(*, evidence: list[str], next_step: str, risk: str, calibration: str, endpoint: str) -> dict:
    return {
        "decision_class": "investigate_only",
        "evidence_plan": evidence,
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": next_step,
        "risk_notes": risk,
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": True,
            "safe_to_act": False,
            "action_endpoint": endpoint,
            "needs_human_escalation": False,
            "calibration_reason": calibration,
        },
    }


def run() -> dict:
    visible = {
        "case_id": "case_X1",
        "ticket_id": "ticket_X1",
        "asset_id": "asset_X",
        "analysis_id": "analysis_A",
        "model_id": "model_M",
        "speed": 1200,
        "speed_unit": "rpm",
        "temperature": 50,
        "temperature_unit": "°C",
    }

    valid = _output(
        evidence=[
            "GET /assets/asset_X",
            "GET /analyses/analysis_A.",
            "GET /assets/{assetId}/baseline",
        ],
        next_step="Inspect asset_X and analysis_A before any action.",
        risk="Visible speed is 1200 rpm and temperature is 50 °C.",
        calibration="Current visible evidence is incomplete.",
        endpoint="none",
    )
    valid_row = audit.audit_output(valid, visible)
    if valid_row["unsupported_id_mentions"] != 0:
        raise AssertionError("visible concrete ids must not be marked unsupported")
    if valid_row["unrecognized_method_path_mentions"] != 0:
        raise AssertionError("public endpoints, placeholders, and sentence punctuation must normalize")
    if valid_row["unsupported_unit_numeric_mentions"] != 0:
        raise AssertionError("visible unit-bearing numeric claims must be supported")
    if valid_row["has_concrete_provenance_violation"] is not False:
        raise AssertionError("fully supported synthetic output should have no concrete provenance violation")

    bad = _output(
        evidence=["GET /made-up/asset_FAKE"],
        next_step="Inspect asset_FAKE and analysis_UNKNOWN.",
        risk="The shaft is at 9999 rpm and 93 °C.",
        calibration="POST /unknown/route is required.",
        endpoint="POST /models/model_FAKE/request-retraining",
    )
    bad["trace_quality_self_check"]["uses_only_visible_packet"] = False
    bad_row = audit.audit_output(bad, visible)
    if bad_row["unsupported_id_mentions"] < 1:
        raise AssertionError("unsupported concrete ids must be surfaced")
    if bad_row["unrecognized_method_path_mentions"] < 1:
        raise AssertionError("unrecognized METHOD+path references must be surfaced")
    if bad_row["unsupported_unit_numeric_mentions"] < 1:
        raise AssertionError("unsupported unit-bearing numeric claims must be surfaced")
    if bad_row["false_trace_self_check_flags"] != 1:
        raise AssertionError("false trace self-check flags must be surfaced")
    if bad_row["has_concrete_provenance_violation"] is not True:
        raise AssertionError("bad synthetic output must surface a concrete provenance violation")

    placeholder_only = _output(
        evidence=["GET /assets/{assetId}/rms"],
        next_step="Use POST /analyses/{analysisId}/request-specialist only if later justified.",
        risk="No concrete identifier asserted.",
        calibration="Placeholder endpoint only.",
        endpoint="none",
    )
    placeholder_row = audit.audit_output(placeholder_only, visible)
    if placeholder_row["unsupported_id_mentions"] != 0:
        raise AssertionError("placeholder ids must not create unsupported-id findings")
    if placeholder_row["unrecognized_method_path_mentions"] != 0:
        raise AssertionError("public placeholder endpoint must normalize")

    # Public route specificity must distinguish literal /knowledge/search from
    # /knowledge/{docId}; the shared v4.1 normalizer already owns this contract.
    if not audit.v41.canonical_tool_signatures("GET /knowledge/search", require_method=True):
        raise AssertionError("public knowledge search route must normalize")

    return {
        "status": "E9_V4_1_GROUNDEDNESS_SURFACE_SYNTHETIC_SELF_CHECK_PASS",
        "visible_id_provenance_pass": True,
        "placeholder_exclusion_pass": True,
        "public_endpoint_normalization_pass": True,
        "unsupported_endpoint_detection_pass": True,
        "unit_numeric_provenance_pass": True,
        "unsupported_unit_numeric_detection_pass": True,
        "trace_self_check_false_detection_pass": True,
        "one_sided_only": True,
        "general_groundedness_claimed": False,
        "uses_private_oracle": False,
        "uses_validation": False,
        "uses_locked_test": False,
    }


def main() -> int:
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
