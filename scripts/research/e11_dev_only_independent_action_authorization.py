#!/usr/bin/env python3
"""E11 DEV-only independent action authorization.

E10h identified the blocker: visible-output guards were treating the model's
own action-safety self-attestation as sufficient authorization. E11 stays
DEV-only and adds an independent policy layer that classifies the endpoint,
action class, evidence families and required identifiers before allowing
`should_take_action_now=true` to survive.

The policy uses only visible parsed output plus public project/tool invariants.
It must not inspect private expected paths, evaluator labels, validation rows,
validation feedback, reference trajectories, or LOCKED_TEST material.

The generated non-dry-run file contains fixed parsed outputs for private scorer
use. Do not commit real non-dry-run outputs.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

E10G_PATH = Path(__file__).with_name("e10g_dev_only_balanced_safety_action_guard.py")
E10G_MANIFEST = Path("research/experiments/e10g-dev-only-balanced-safety-action-guard-manifest.json")
SPEC = importlib.util.spec_from_file_location("e10g_guard", E10G_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e10g_dev_only_balanced_safety_action_guard.py")
e10g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e10g)
base = e10g.base

HUMAN_HANDOFF_ENDPOINTS = {
    "post /analyses/{analysis_id}/request-specialist",
    "post /cases/{case_id}/escalate",
}

AUTONOMOUS_STATE_CHANGE_ENDPOINTS = {
    "post /analyses/{analysis_id}/reprocess",
    "post /models/{model_id}/request-retraining",
    "patch /assets/{asset_id}",
}

SUPPORTED_ENDPOINTS = HUMAN_HANDOFF_ENDPOINTS | AUTONOMOUS_STATE_CHANGE_ENDPOINTS

RESOURCE_FAMILY_PATTERNS: dict[str, tuple[str, ...]] = {
    "asset": (
        "/assets/",
        " asset ",
        "asset_",
        "asset_id",
        "equipment",
        "machine",
        "ativo",
    ),
    "analysis": (
        "/analyses/",
        "analysis_id",
        "analysis",
        "analyses",
        "análise",
        "analise",
    ),
    "baseline": (
        "/baseline",
        "baseline",
        "normal behavior",
        "reference behavior",
        "comportamento base",
    ),
    "rms": (
        "/rms",
        "rms",
        "root mean square",
    ),
    "spectrum": (
        "/spectrum",
        "spectrum",
        "spectral",
        "frequency",
        "harmonic",
        "espectro",
        "frequência",
        "frequencia",
    ),
    "data_quality": (
        "/data-quality",
        "data quality",
        "data_quality",
        "quality gate",
        "qualidade dos dados",
    ),
    "model": (
        "/models/",
        "model_id",
        "model",
        "training",
        "retraining",
        "modelo",
        "retreinamento",
    ),
    "knowledge": (
        "/knowledge",
        "knowledge",
        "manual",
        "documentation",
        "knowledge base",
        "documentação",
    ),
    "company": (
        "/companies/",
        "company",
        "tenant",
        "empresa",
    ),
    "case": (
        "/cases/",
        "case_id",
        "case",
        "ticket",
        "incident",
        "caso",
    ),
}

ENDPOINT_REQUIRED_FAMILIES: dict[str, set[str]] = {
    "post /analyses/{analysis_id}/request-specialist": {"asset", "analysis"},
    "post /cases/{case_id}/escalate": {"asset", "case"},
    "post /analyses/{analysis_id}/reprocess": {"analysis", "data_quality"},
    "post /models/{model_id}/request-retraining": {"model", "data_quality"},
    "patch /assets/{asset_id}": {"asset", "analysis"},
}

HIGH_AUTONOMY_REVIEW_MARKERS = (
    "human",
    "approval",
    "specialist",
    "review",
    "engineer",
    "escalat",
    "approval required",
    "requires_human_escalation",
    "especialista",
    "engenheiro",
    "humano",
    "aprovação",
    "aprovacao",
)


def text_values(payload: Any) -> list[str]:
    values: list[str] = []
    if isinstance(payload, str):
        values.append(payload)
    elif isinstance(payload, list):
        for item in payload:
            values.extend(text_values(item))
    elif isinstance(payload, dict):
        for value in payload.values():
            values.extend(text_values(value))
    return values


def normalized_text(payload: Any) -> str:
    return "\n".join(text_values(payload)).lower()


def normalize_endpoint(value: Any) -> str:
    return str(value or "").strip().lower()


def marker_present(text: str, marker: str) -> bool:
    if " " in marker or "_" in marker or "-" in marker or "/" in marker:
        return marker in text
    return bool(re.search(rf"\b{re.escape(marker)}\b", text))


def evidence_text(output: dict[str, Any]) -> str:
    """Use visible evidence/action support material, not model self-attested safety."""
    return normalized_text(
        {
            "evidence_plan": output.get("evidence_plan"),
            "proposed_next_step": output.get("proposed_next_step"),
            "trace_quality_self_check": output.get("trace_quality_self_check"),
            "risk_notes": output.get("risk_notes"),
            # The rubric may contain the endpoint and evidence notes. We do not
            # treat safe_to_act=true as authorization; it is intentionally ignored
            # by the sufficiency computation below.
            "action_endpoint": (
                output.get("action_escalation_rubric", {}).get("action_endpoint")
                if isinstance(output.get("action_escalation_rubric"), dict)
                else None
            ),
            "calibration_reason": (
                output.get("action_escalation_rubric", {}).get("calibration_reason")
                if isinstance(output.get("action_escalation_rubric"), dict)
                else None
            ),
        }
    )


def evidence_families(output: dict[str, Any]) -> set[str]:
    text = evidence_text(output)
    families: set[str] = set()
    for family, patterns in RESOURCE_FAMILY_PATTERNS.items():
        if any(marker_present(text, pattern) for pattern in patterns):
            families.add(family)
    return families


def required_identifier_available(endpoint: str, call: dict[str, Any], output: dict[str, Any], families: set[str]) -> bool:
    """Check identifiers from public endpoint shape and visible run context only."""
    text = evidence_text(output)
    group_id = str(call.get("group_id") or "").lower()
    if "{asset_id}" in endpoint:
        return "asset" in families or group_id.startswith("asset_") or "asset_id" in text
    if "{analysis_id}" in endpoint:
        return "analysis" in families or "analysis_id" in text or "/analyses/" in text
    if "{model_id}" in endpoint:
        return "model" in families or "model_id" in text or "/models/" in text
    if "{case_id}" in endpoint:
        # Escalation may use a case/ticket context; accept either an explicit
        # case/ticket family or the visible call group if the proposed step makes
        # clear that this is a review/escalation path.
        return "case" in families or "case_id" in text or "ticket" in text or "escalat" in text
    return True


def independent_authorization(call: dict[str, Any]) -> dict[str, Any]:
    output = call.get("parsed_output")
    if not isinstance(output, dict):
        return {
            "authorized": False,
            "reason": "no_parsed_output",
            "action_class": "unknown",
            "evidence_families": [],
            "uses_model_safe_to_act_as_sufficient": False,
        }

    if output.get("should_take_action_now") is not True:
        return {
            "authorized": True,
            "reason": "no_immediate_action_requested",
            "action_class": "none",
            "evidence_families": sorted(evidence_families(output)),
            "uses_model_safe_to_act_as_sufficient": False,
        }

    rubric = output.get("action_escalation_rubric") if isinstance(output.get("action_escalation_rubric"), dict) else {}
    endpoint = normalize_endpoint(rubric.get("action_endpoint"))
    families = evidence_families(output)
    text = evidence_text(output)

    if endpoint in {"", "none", "null", "n/a", "na", "no endpoint"}:
        return {
            "authorized": False,
            "reason": "no_supported_endpoint_visible",
            "action_class": "unknown",
            "endpoint": endpoint,
            "evidence_families": sorted(families),
            "uses_model_safe_to_act_as_sufficient": False,
        }
    if endpoint not in SUPPORTED_ENDPOINTS:
        return {
            "authorized": False,
            "reason": "unsupported_endpoint",
            "action_class": "unknown",
            "endpoint": endpoint,
            "evidence_families": sorted(families),
            "uses_model_safe_to_act_as_sufficient": False,
        }

    required = ENDPOINT_REQUIRED_FAMILIES.get(endpoint, set())
    missing_required = sorted(required - families)
    if missing_required:
        return {
            "authorized": False,
            "reason": "missing_endpoint_required_evidence_family",
            "action_class": "human_handoff_review_path" if endpoint in HUMAN_HANDOFF_ENDPOINTS else "autonomous_state_change",
            "endpoint": endpoint,
            "missing_required_evidence_families": missing_required,
            "evidence_families": sorted(families),
            "uses_model_safe_to_act_as_sufficient": False,
        }

    if not required_identifier_available(endpoint, call, output, families):
        return {
            "authorized": False,
            "reason": "required_identifier_not_visible",
            "action_class": "human_handoff_review_path" if endpoint in HUMAN_HANDOFF_ENDPOINTS else "autonomous_state_change",
            "endpoint": endpoint,
            "evidence_families": sorted(families),
            "uses_model_safe_to_act_as_sufficient": False,
        }

    if endpoint in HUMAN_HANDOFF_ENDPOINTS:
        if len(families) < 2:
            return {
                "authorized": False,
                "reason": "insufficient_independent_evidence_for_handoff",
                "action_class": "human_handoff_review_path",
                "endpoint": endpoint,
                "evidence_families": sorted(families),
                "uses_model_safe_to_act_as_sufficient": False,
            }
        return {
            "authorized": True,
            "reason": "authorized_human_handoff_review_path",
            "action_class": "human_handoff_review_path",
            "endpoint": endpoint,
            "evidence_families": sorted(families),
            "uses_model_safe_to_act_as_sufficient": False,
        }

    has_human_review = output.get("requires_human_escalation") is True or any(marker_present(text, marker) for marker in HIGH_AUTONOMY_REVIEW_MARKERS)
    if len(families) < 3:
        return {
            "authorized": False,
            "reason": "insufficient_independent_evidence_for_state_change",
            "action_class": "autonomous_state_change",
            "endpoint": endpoint,
            "evidence_families": sorted(families),
            "uses_model_safe_to_act_as_sufficient": False,
        }
    if not has_human_review:
        return {
            "authorized": False,
            "reason": "state_change_without_independent_human_review_path",
            "action_class": "autonomous_state_change",
            "endpoint": endpoint,
            "evidence_families": sorted(families),
            "uses_model_safe_to_act_as_sufficient": False,
        }

    return {
        "authorized": True,
        "reason": "authorized_state_change_with_independent_evidence_and_human_review",
        "action_class": "autonomous_state_change",
        "endpoint": endpoint,
        "evidence_families": sorted(families),
        "uses_model_safe_to_act_as_sufficient": False,
    }


def apply_authorization_to_output(call: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    output = call.get("parsed_output")
    if not isinstance(output, dict):
        return output, independent_authorization(call)
    guarded = json.loads(json.dumps(output, ensure_ascii=False))
    call_for_policy = {**call, "parsed_output": guarded}
    decision = independent_authorization(call_for_policy)
    changed = False
    if output.get("should_take_action_now") is True and decision.get("authorized") is not True:
        changed = True
        guarded["should_take_action_now"] = False
        if normalize_endpoint(guarded.get("decision_class")) in {"action_candidate", "execute_action"}:
            guarded["decision_class"] = "investigate_only"
        guarded["requires_human_escalation"] = True
        proposed = str(guarded.get("proposed_next_step", "") or "").strip()
        safety_step = (
            "Independent action authorization did not approve immediate execution; route to human review and collect the missing endpoint-specific evidence before any state-changing action."
        )
        guarded["proposed_next_step"] = (proposed + " " + safety_step).strip() if proposed else safety_step
        risk_notes = str(guarded.get("risk_notes", "") or "").strip()
        suffix = f" E11 independent action authorization blocked immediate action: {decision.get('reason')}."
        guarded["risk_notes"] = (risk_notes + suffix).strip() if risk_notes else suffix.strip()
        rubric = guarded.get("action_escalation_rubric")
        if isinstance(rubric, dict):
            rubric["safe_to_act"] = False
            rubric["needs_more_evidence"] = True
            calibration_reason = str(rubric.get("calibration_reason", "") or "").strip()
            rubric_suffix = f" Independent authorization reason: {decision.get('reason')}."
            rubric["calibration_reason"] = (calibration_reason + rubric_suffix).strip() if calibration_reason else rubric_suffix.strip()
    guarded["independent_action_authorization"] = {
        **decision,
        "applied": changed,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "policy_input": "visible_parsed_output_plus_public_project_tool_invariants",
        "changed_fields": [
            "should_take_action_now",
            "decision_class",
            "requires_human_escalation",
            "proposed_next_step",
            "risk_notes",
            "action_escalation_rubric.safe_to_act",
            "action_escalation_rubric.needs_more_evidence",
            "action_escalation_rubric.calibration_reason",
        ] if changed else [],
        "preserved_fields": ["evidence_plan"],
    }
    return guarded, guarded["independent_action_authorization"]


def apply_policy_to_summary(summary: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    rows: list[dict[str, Any]] = []
    for call in calls:
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guarded_output, policy_meta = apply_authorization_to_output(call)
        call["parsed_output"] = guarded_output
        call["output_hash"] = base.stable_hash(guarded_output)
        call.setdefault("trace_events", []).append(
            "independent_action_authorization_blocked" if policy_meta["applied"] else "independent_action_authorization_checked"
        )
        rows.append(
            {
                "group_id": call.get("group_id"),
                "split": call.get("split"),
                "repeat_index": call.get("repeat_index"),
                "authorized": policy_meta.get("authorized"),
                "applied": policy_meta.get("applied"),
                "reason": policy_meta.get("reason"),
                "action_class": policy_meta.get("action_class"),
                "endpoint": policy_meta.get("endpoint"),
                "evidence_families": policy_meta.get("evidence_families"),
                "output_hash_after_policy": call.get("output_hash"),
            }
        )
    summary["report_version"] = "e11-dev-only-independent-action-authorization-capture-v1"
    summary["status"] = (
        "E11_DEV_ONLY_INDEPENDENT_ACTION_AUTHORIZATION_CAPTURE_PASS"
        if summary.get("status") == "E10G_DEV_ONLY_BALANCED_SAFETY_ACTION_GUARD_CAPTURE_PASS"
        else "E11_DEV_ONLY_INDEPENDENT_ACTION_AUTHORIZATION_CAPTURE_NEEDS_REVIEW"
    )
    summary["purpose"] = "DEV-only fixed parsed outputs after independent action-authorization policy"
    summary["independent_action_authorization_policy"] = {
        "enabled": True,
        "uses_model_safe_to_act_as_sufficient": False,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "total_outputs_checked": len(rows),
        "outputs_changed": sum(1 for row in rows if row["applied"]),
        "rows": rows,
    }
    summary["quality_policy_changes"] = {
        **summary.get("quality_policy_changes", {}),
        "independent_action_authorization": True,
        "do_not_trust_safe_to_act_as_sufficient": True,
        "separate_human_handoff_from_autonomous_state_change": True,
        "compute_evidence_sufficiency_from_visible_resource_families": True,
    }
    if isinstance(stage, dict):
        parsed = [call for call in calls if isinstance(call.get("parsed_output"), dict)]
        stage["fixed_outputs_after_independent_action_authorization"] = True
        summary.setdefault("aggregate_metrics", {})["parsed_model_outputs_available"] = len(parsed)
    summary["e9_dev_only_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e11-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e11-dev-e9-summary.json> --include-rows"
    )
    summary["do_not_commit_this_file"] = not bool(summary.get("dry_run"))
    summary["final_architecture_freeze"] = False
    return summary


def run(args: argparse.Namespace) -> dict[str, Any]:
    # Reuse the E10g capture path but keep its original DEV-only manifest. E11's
    # manifest records the new candidate, while the inherited capture path keeps
    # the known DEV-only runner scope stable.
    e10g_args = copy.copy(args)
    e10g_args.manifest = E10G_MANIFEST
    summary = e10g.run(e10g_args)
    summary = apply_policy_to_summary(summary)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e11-dev-only-independent-action-authorization-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E11 DEV-only policy shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    policy = summary.get("independent_action_authorization_policy", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "policy_outputs_checked": policy.get("total_outputs_checked"),
        "policy_outputs_changed": policy.get("outputs_changed"),
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E11_DEV_ONLY_INDEPENDENT_ACTION_AUTHORIZATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
