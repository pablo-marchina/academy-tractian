#!/usr/bin/env python3
"""P12-C2 deterministic factorial candidate transforms.

Provider-free candidate logic for:
- E0: retained P12-C1 E14t-style reference evidence policy.
- E1: bounded public intent/dependency closure.
- S0: retained E14q -> E14q2 safety policy.
- S1: strict public authorization certificate layered after S0.

This module never reads evaluator/private oracle data, FRESH_BLIND, or
LEGACY_LOCKED_TEST. Group/ticket identity is not used for candidate decisions.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
INTENT_MAP_PATH = ROOT / "research/frozen/p12-c2-public-intent-map-v1.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c1 = _load_module("p12_c1_reference_for_c2", HERE / "p12_c1_evidence_route_candidates.py")
q = _load_module("e14q_for_p12_c2", HERE / "e14q_full_dev_public_action_authorization_consistency_guard.py")
q2 = _load_module("e14q2_for_p12_c2", HERE / "e14q2_full_dev_public_route_role_purpose_consistency_guard.py")
n11 = _load_module("e14n_v11_for_p12_c2", HERE / "e14n_public_identifier_provenance_guard_v1_1.py")

E0_ID = "E14T_REFERENCE_PORT_V1_RETAINED"
E1_ID = "BOUNDED_PUBLIC_INTENT_DEPENDENCY_CLOSURE_V1"
S0_ID = "RETAINED_E14Q_E14Q2"
S1_ID = "STRICT_PUBLIC_AUTHORIZATION_CERTIFICATE_V1"
MAX_FINAL_READS = 7

_INTENT = json.loads(INTENT_MAP_PATH.read_text(encoding="utf-8"))
ROUTE_CONFIG: dict[str, dict[str, Any]] = dict(_INTENT["routes"])
PUBLIC_READ_ROUTES = frozenset(ROUTE_CONFIG)
REQUIRED_ACTION_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    str(action): tuple(str(x) for x in reads)
    for action, reads in _INTENT["action_dependencies"].items()
}

_ALLOWED_MUTABLE_S1 = frozenset(
    {
        "decision_class",
        "should_take_action_now",
        "requires_human_escalation",
        "action_escalation_rubric.action_endpoint",
        "action_escalation_rubric.safe_to_act",
        "action_escalation_rubric.needs_more_evidence",
    }
)


def _lower(value: Any) -> str:
    return str(value or "").casefold()


def _message_matches(route: str, visible_case: dict[str, Any]) -> bool:
    text = _lower(visible_case.get("message"))
    markers = tuple(_lower(x) for x in ROUTE_CONFIG[route].get("markers", ()))
    return any(marker and marker in text for marker in markers)


def _output_text(output: dict[str, Any]) -> str:
    return json.dumps(output, ensure_ascii=False, sort_keys=True).casefold()


def _route_identifiers_grounded(
    route: str,
    visible_case: dict[str, Any],
    output: dict[str, Any],
    action_endpoint: str | None,
) -> bool:
    required = tuple(ROUTE_CONFIG[route].get("required_placeholders", ()))
    if not required:
        return True
    blob = _output_text(output)
    visible_blob = json.dumps(visible_case, ensure_ascii=False, sort_keys=True).casefold()

    for placeholder in required:
        p = str(placeholder)
        if p == "{assetId}":
            if not visible_case.get("asset_id"):
                return False
        elif p == "{companyId}":
            if not visible_case.get("company_id"):
                return False
        elif p == "{analysisId}":
            if "{analysisid}" not in blob and not (
                action_endpoint and "{analysisId}" in action_endpoint
            ):
                return False
        elif p == "{modelId}":
            if "{modelid}" not in blob and not (
                action_endpoint and "{modelId}" in action_endpoint
            ):
                return False
        elif p == "{docId}":
            if "{docid}" not in blob:
                return False
        else:
            return False

    return bool(visible_blob)


def _canonical_existing_reads(output: dict[str, Any]) -> list[str]:
    reads = c1.canonical_parent_reads(output)
    return [route for route in reads if route in PUBLIC_READ_ROUTES]


def _proposed_action(output: dict[str, Any]) -> str | None:
    return q._action_endpoint(output)


def _stable_add(out: list[str], route: str) -> None:
    if route in PUBLIC_READ_ROUTES and route not in out and len(out) < MAX_FINAL_READS:
        out.append(route)


def apply_e1(
    visible_case: dict[str, Any],
    output: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply bounded public intent/dependency closure; only evidence_plan changes."""
    before = copy.deepcopy(output)
    existing = _canonical_existing_reads(before)
    endpoint = _proposed_action(before)

    selected: list[str] = []

    for route in existing:
        if _message_matches(route, visible_case):
            _stable_add(selected, route)

    if endpoint:
        for route in REQUIRED_ACTION_DEPENDENCIES.get(endpoint, ()):
            if _route_identifiers_grounded(route, visible_case, before, endpoint):
                _stable_add(selected, route)

    for route in _INTENT["stable_route_order"]:
        route = str(route)
        if (
            route in PUBLIC_READ_ROUTES
            and _message_matches(route, visible_case)
            and _route_identifiers_grounded(route, visible_case, before, endpoint)
        ):
            _stable_add(selected, route)

    for route in existing:
        _stable_add(selected, route)

    result = copy.deepcopy(before)
    result["evidence_plan"] = c1.e14s._evidence_items(selected)
    after = c1.canonical_parent_reads(result)

    if after != selected:
        raise AssertionError("E1 serialization changed selected route order")
    if len(after) > MAX_FINAL_READS:
        raise AssertionError("E1 exceeded max-seven read cap")
    if any(route not in PUBLIC_READ_ROUTES for route in after):
        raise AssertionError("E1 emitted unknown/non-public read route")
    if c1._non_evidence_signature(before) != c1._non_evidence_signature(result):
        raise AssertionError("E1 changed a non-evidence field")

    added = [route for route in after if route not in existing]
    return result, {
        "candidate_id": E1_ID,
        "parent_read_count": len(existing),
        "final_read_count": len(after),
        "added_reads": added,
        "added_read_count": len(added),
        "max_final_reads": MAX_FINAL_READS,
        "only_evidence_plan_changed": True,
        "private_oracle_used": False,
    }


def apply_e0_batch(records: list[dict[str, Any]]):
    """Retain exact P12-C1 C0 evidence semantics under a new P12-C2 measurement."""
    outputs, meta = c1.apply_c0_batch(records)
    meta = dict(meta)
    meta["candidate_id"] = E0_ID
    return outputs, meta


def apply_s0(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply the retained E14q then E14q2 transforms unchanged."""
    q_out, q_meta = q.transform_output(output)
    q2_out, q2_meta = q2.transform_output(q_out)
    return q2_out, {
        "safety_id": S0_ID,
        "e14q": q_meta,
        "e14q2": q2_meta,
        "private_oracle_used": False,
    }


def _raw_action_endpoint(output: dict[str, Any]) -> str:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    return str(rubric.get("action_endpoint") or "")


def _identifier_provenance_ok(
    output: dict[str, Any],
    visible_case: dict[str, Any],
) -> bool:
    raw = _raw_action_endpoint(output)
    if not raw or raw.casefold() == "none":
        return True
    visible_blob = n11.parent.ground._case_visible_blob(visible_case)
    _, unsupported_distinct, _ = n11._sanitize_text_v1_1(raw, visible_blob)
    return int(unsupported_distinct) == 0


def s1_certificate_failure_reason(
    output: dict[str, Any],
    visible_case: dict[str, Any],
) -> str | None:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    endpoint = q._action_endpoint(output)
    action_now = output.get("should_take_action_now") is True
    escalation = output.get("requires_human_escalation") is True
    decision = str(output.get("decision_class") or "")

    if not action_now:
        if endpoint is not None:
            return "inactive_output_has_action_endpoint"
        if escalation:
            return "inactive_output_has_escalation"
        return None

    if endpoint not in q.SUPPORTED_ACTIONS:
        return "unsupported_or_missing_public_action_endpoint"

    if q2.public_consistency_failure_reason(output) is not None:
        return "retained_q2_role_or_purpose_inconsistency"

    if endpoint in q.HANDOFF_ACTIONS:
        if not escalation or decision != "escalation_candidate":
            return "handoff_role_state_incoherent"
    else:
        if escalation or decision != "action_candidate":
            return "non_handoff_role_state_incoherent"

    if rubric.get("safe_to_act") is not True:
        return "safe_to_act_not_true"
    if rubric.get("needs_more_evidence") is not False:
        return "needs_more_evidence_not_false"

    reads = q._observed_reads(output)
    if q.COMMON_AUTH_READ not in reads:
        return "missing_users_me_authorization_read"

    target_read = q.TARGET_READ_REQUIRED.get(endpoint)
    if target_read is not None and target_read not in reads:
        return "missing_endpoint_specific_target_read"

    if not _identifier_provenance_ok(output, visible_case):
        return "action_endpoint_identifier_not_publicly_grounded"

    if endpoint in q.HANDOFF_ACTIONS and not q._visible_human_reason(output):
        return "handoff_missing_explicit_public_human_review_reason"

    return None


def _s1_nonmutable_signature(output: dict[str, Any]) -> dict[str, Any]:
    clone = copy.deepcopy(output)
    clone.pop("decision_class", None)
    clone.pop("should_take_action_now", None)
    clone.pop("requires_human_escalation", None)
    rubric = clone.get("action_escalation_rubric")
    if isinstance(rubric, dict):
        for key in ("action_endpoint", "safe_to_act", "needs_more_evidence"):
            rubric.pop(key, None)
    return clone


def apply_s1(
    output: dict[str, Any],
    visible_case: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply strict public authorization certificate after retained S0."""
    before = copy.deepcopy(output)
    result = copy.deepcopy(output)
    reason = s1_certificate_failure_reason(before, visible_case)

    if reason is not None:
        rubric = result.get("action_escalation_rubric")
        if not isinstance(rubric, dict):
            rubric = {}
            result["action_escalation_rubric"] = rubric
        result["decision_class"] = "investigate_only"
        result["should_take_action_now"] = False
        result["requires_human_escalation"] = False
        rubric["action_endpoint"] = "none"
        rubric["safe_to_act"] = False
        rubric["needs_more_evidence"] = True

    if before.get("should_take_action_now") is not True and result.get("should_take_action_now") is True:
        raise AssertionError("S1 promoted a non-action")
    if q._action_endpoint(before) is None and q._action_endpoint(result) is not None:
        raise AssertionError("S1 invented an action endpoint")
    if before.get("requires_human_escalation") is not True and result.get("requires_human_escalation") is True:
        raise AssertionError("S1 invented a human handoff")
    if _s1_nonmutable_signature(before) != _s1_nonmutable_signature(result):
        raise AssertionError("S1 changed a field outside the frozen mutable set")

    return result, {
        "safety_id": S1_ID,
        "certificate_pass": reason is None,
        "certificate_failure_reason": reason,
        "promotions_made": 0,
        "invented_endpoints": 0,
        "invented_handoffs": 0,
        "mutable_fields_only": sorted(_ALLOWED_MUTABLE_S1),
        "private_oracle_used": False,
    }


def apply_factorial_arms(
    visible_case: dict[str, Any],
    parent_output: dict[str, Any],
    *,
    e0_output: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build four factorial arms from one already-fixed common parent."""
    e1_output, _ = apply_e1(visible_case, parent_output)

    a00, _ = apply_s0(e0_output)
    a10, _ = apply_s0(e1_output)

    a01_base, _ = apply_s0(e0_output)
    a01, _ = apply_s1(a01_base, visible_case)

    a11_base, _ = apply_s0(e1_output)
    a11, _ = apply_s1(a11_base, visible_case)

    return {"A00": a00, "A10": a10, "A01": a01, "A11": a11}
