from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

E13_PATH = Path(__file__).with_name("e13_dev_only_reprocess_authorization_boundary.py")
SPEC = importlib.util.spec_from_file_location("e13_policy", E13_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e13_dev_only_reprocess_authorization_boundary.py")
e13 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e13)
e11 = e13.e11
base = e13.base
capture = e11.e10g.e10e.e10d.e10c.e10b.capture
REPROCESS_ENDPOINT = e13.REPROCESS_ENDPOINT

CAUSAL_MARKERS = (
    "because", "based on", "due to", "therefore", "to resolve", "to recompute",
    "to verify", "to reconcile", "devido", "porque", "para resolver", "para recomputar",
)
REPROCESS_TERMS = ("reprocess", "recompute", "rerun", "reprocessar", "recalcular")
HIGHER_RISK_MUTATIONS = (
    "patch /assets/{asset_id}", "patch /assets/", "post /models/{model_id}/request-retraining",
    "/request-retraining", "request retraining", "retrain the model", "retreinamento",
)
CONCRETE_OBSERVATIONS = (
    "rms increased", "rms spike", "rms deviation", "spectrum shows", "spectrum indicates",
    "spectral peak", "frequency peak", "harmonic", "baseline deviation", "baseline mismatch",
    "outside baseline", "data quality issue", "data-quality issue", "data quality degraded",
    "data-quality degraded", "sensor anomaly", "sensor dropout", "sensor gap", "sensor invalid",
    "signal anomaly", "signal mismatch", "qualidade dos dados degradada", "anomalia de sensor",
    "desvio de baseline",
)
UNCERTAINTY = (
    "uncertain diagnosis", "diagnosis uncertain", "diagnosis incomplete", "incomplete diagnosis",
    "inconclusive diagnosis", "cannot confirm diagnosis", "uncertainty remains", "diagnóstico incerto",
    "diagnostico incerto", "diagnóstico incompleto", "diagnostico incompleto",
)
STALE_FAILED = tuple(sorted({p for patterns in e13.REPROCESS_DEFECT_PATTERNS.values() for p in patterns}))
MISMATCH = (
    "mismatch between", "conflicts with the current analysis", "conflict with the current analysis",
    "inconsistent with the current analysis", "does not match the current analysis",
    "evidence contradicts the analysis", "signal contradicts the analysis", "analysis conclusion conflicts",
    "diverge da análise", "diverge da analise", "inconsistente com a análise", "inconsistente com a analise",
)
REQUEST_CONTEXT = (
    "request asks for updated analysis", "request asks for a recomputed analysis", "user asks for updated analysis",
    "user asks to recompute", "case asks for updated analysis", "case requests reprocess",
    "ticket requests reprocess", "requested updated analysis", "requested recomputation",
    "solicita análise atualizada", "solicita analise atualizada", "solicita reprocessamento",
)
LOW_RISK_CONTEXT = (
    "low-risk next diagnostic action", "low risk next diagnostic action", "low-risk diagnostic step",
    "low risk diagnostic step", "diagnostic reprocess", "reprocess is the next diagnostic",
    "reprocessing is the next diagnostic", "knowledge supports reprocess", "knowledge base supports reprocess",
    "model context supports reprocess", "próxima ação diagnóstica de baixo risco",
    "proxima acao diagnostica de baixo risco",
)


def marker_present(text: str, marker: str) -> bool:
    if any(ch in marker for ch in (" ", "_", "-", "/")):
        return marker in text
    return bool(re.search(rf"\b{re.escape(marker)}\b", text))


def output_rubric(output: dict[str, Any]) -> dict[str, Any]:
    return e13.output_rubric(output)


def output_endpoint(output: dict[str, Any]) -> str:
    return e13.output_endpoint(output)


def support_text(output: dict[str, Any]) -> str:
    return e11.normalized_text({
        "proposed_next_step": output.get("proposed_next_step"),
        "risk_notes": output.get("risk_notes"),
        "calibration_reason": output_rubric(output).get("calibration_reason"),
    })


def visible_text(output: dict[str, Any]) -> str:
    return e11.evidence_text(output)


def has_analysis_reference(output: dict[str, Any]) -> bool:
    text = visible_text(output)
    return any(x in text for x in ("analysis_id", "/analyses/", "analysis resource", "analysis reference"))


def has_asset_or_case_reference(call: dict[str, Any], output: dict[str, Any]) -> bool:
    text = visible_text(output)
    group_id = str(call.get("group_id") or "").lower()
    return group_id.startswith("asset_") or any(x in text for x in ("asset_id", "/assets/", "case_id", "/cases/", "ticket"))


def action_limited_to_reprocess(output: dict[str, Any]) -> bool:
    if output_endpoint(output) != REPROCESS_ENDPOINT:
        return False
    text = e11.normalized_text({
        "proposed_next_step": output.get("proposed_next_step"),
        "action_endpoint": output_rubric(output).get("action_endpoint"),
    })
    return not any(marker_present(text, marker) for marker in HIGHER_RISK_MUTATIONS)


def has_reprocess_reason(output: dict[str, Any]) -> bool:
    text = support_text(output)
    has_action = any(marker_present(text, x) for x in REPROCESS_TERMS) or REPROCESS_ENDPOINT in text
    has_cause = any(marker_present(text, x) for x in CAUSAL_MARKERS)
    return has_action and has_cause and len(text.strip()) >= 40


def support_anchors(output: dict[str, Any]) -> set[str]:
    text = support_text(output)
    anchors: set[str] = set()
    if any(marker_present(text, x) for x in CONCRETE_OBSERVATIONS):
        anchors.add("concrete_sensor_rms_spectrum_baseline_or_data_quality_observation")
    if any(marker_present(text, x) for x in UNCERTAINTY):
        anchors.add("diagnosis_uncertainty_or_incompleteness")
    if any(marker_present(text, x) for x in STALE_FAILED):
        anchors.add("stale_failed_unreliable_or_incomplete_analysis_signal")
    if any(marker_present(text, x) for x in MISMATCH):
        anchors.add("evidence_analysis_conclusion_mismatch")
    if any(marker_present(text, x) for x in REQUEST_CONTEXT):
        anchors.add("case_or_user_requests_updated_analysis")
    if any(marker_present(text, x) for x in LOW_RISK_CONTEXT):
        anchors.add("knowledge_or_model_context_supports_low_risk_reprocess")
    return anchors


def authorize(call: dict[str, Any]) -> dict[str, Any]:
    output = call.get("parsed_output")
    if not isinstance(output, dict):
        return {
            "authorized": False, "reason": "no_parsed_output", "is_target_reprocess_action": False,
            "support_anchor_count": 0, "support_anchors": [], "uses_private_oracle": False,
            "uses_validation_feedback": False, "uses_locked_test": False,
        }
    endpoint = output_endpoint(output)
    requested = output.get("should_take_action_now") is True
    is_target = requested and endpoint == REPROCESS_ENDPOINT
    anchors = sorted(support_anchors(output))
    common = {
        "target_endpoint": REPROCESS_ENDPOINT,
        "is_target_reprocess_action": is_target,
        "endpoint": endpoint,
        "support_anchor_count": len(anchors),
        "support_anchors": anchors,
        "uses_generic_evidence_family_count_as_sufficient": False,
        "uses_generic_human_review_markers_as_sufficient": False,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    }
    if not requested:
        return {**common, "authorized": True, "reason": "no_immediate_action_requested"}
    if endpoint != REPROCESS_ENDPOINT:
        return {**common, "authorized": True, "reason": "not_reprocess_endpoint_boundary_target"}
    if not has_analysis_reference(output):
        return {**common, "authorized": False, "reason": "missing_visible_analysis_resource_reference"}
    if not has_asset_or_case_reference(call, output):
        return {**common, "authorized": False, "reason": "missing_visible_asset_or_case_reference"}
    if not action_limited_to_reprocess(output):
        return {**common, "authorized": False, "reason": "reprocess_action_not_limited_to_reprocess"}
    if not has_reprocess_reason(output):
        return {**common, "authorized": False, "reason": "missing_human_readable_evidence_to_reprocess_reason"}
    if len(anchors) < 2:
        return {**common, "authorized": False, "reason": "fewer_than_two_concrete_reprocess_support_anchors"}
    return {**common, "authorized": True, "reason": "authorized_reprocess_with_selective_visible_support"}


def apply(call: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    output = call.get("parsed_output")
    if not isinstance(output, dict):
        return None, authorize(call)
    guarded = json.loads(json.dumps(output, ensure_ascii=False))
    decision = authorize({**call, "parsed_output": guarded})
    changed = decision.get("is_target_reprocess_action") is True and decision.get("authorized") is not True
    if changed:
        guarded["should_take_action_now"] = False
        guarded["requires_human_escalation"] = True
        if e11.normalize_endpoint(guarded.get("decision_class")) in {"action_candidate", "execute_action", "autonomous_state_change"}:
            guarded["decision_class"] = "investigate_only"
        proposed = str(guarded.get("proposed_next_step", "") or "").strip()
        suffix = "E14 selective reprocess authorization did not approve immediate reprocess; collect concrete endpoint support or route to human review before POST /analyses/{analysis_id}/reprocess."
        guarded["proposed_next_step"] = f"{proposed} {suffix}".strip()
        risk = str(guarded.get("risk_notes", "") or "").strip()
        guarded["risk_notes"] = f"{risk} E14 blocked autonomous reprocess: {decision.get('reason')}.".strip()
        rubric = output_rubric(guarded)
        if rubric:
            rubric["safe_to_act"] = False
            rubric["needs_more_evidence"] = True
            reason = str(rubric.get("calibration_reason", "") or "").strip()
            rubric["calibration_reason"] = f"{reason} E14 selective reprocess reason: {decision.get('reason')}.".strip()
    guarded["selective_reprocess_authorization_boundary"] = {
        **decision,
        "applied": changed,
        "policy_input": "visible_parsed_output_plus_visible_dev_call_context_and_public_tool_invariants",
        "preregistered_candidate": "completeness_preserving_selective_reprocess_authorization",
        "required_anchor_count": 2,
        "semantic_fields_invented": False,
        "preserved_fields": ["evidence_plan"],
    }
    return guarded, guarded["selective_reprocess_authorization_boundary"]
