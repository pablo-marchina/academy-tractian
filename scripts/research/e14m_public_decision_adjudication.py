#!/usr/bin/env python3
"""Public conditional decision adjudication for E14m.

E14m addresses a public mode-collapse pattern observed in E14l: every parseable
DEV draft selected the same fully conservative policy. This module uses only the
model's own draft plus public repository contracts. It never reads private
oracle/scorer data, VALIDATION feedback, or LOCKED_TEST material.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ENDPOINT_NORMALIZER_PATH = HERE / "e14c_public_action_endpoint_normalization.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


endpoint_norm = load_module("e14m_endpoint_norm", ENDPOINT_NORMALIZER_PATH)

SUPPORTED_ACTION_ENDPOINTS = (
    "POST /analyses/{analysis_id}/reprocess",
    "POST /analyses/{analysis_id}/request-specialist",
    "POST /models/{model_id}/request-retraining",
    "PATCH /assets/{asset_id}",
    "POST /cases/{case_id}/escalate",
)

E14F_REPAIR_MARKER = "PUBLIC SEMANTIC CONSISTENCY REPAIR PASS"


def canonical_endpoint(output: dict[str, Any]) -> str | None:
    rubric = output.get("action_escalation_rubric")
    value = rubric.get("action_endpoint") if isinstance(rubric, dict) else None
    return endpoint_norm.canonical_public_endpoint_or_none(value)


def is_public_conservative_collapse_draft(output: dict[str, Any] | None) -> bool:
    """Match only the preregistered public E14l collapse shape."""
    if not isinstance(output, dict):
        return False
    rubric = output.get("action_escalation_rubric")
    if not isinstance(rubric, dict):
        return False
    return bool(
        str(output.get("decision_class") or "").strip().lower() == "investigate_only"
        and output.get("should_take_action_now") is False
        and output.get("requires_human_escalation") is False
        and rubric.get("needs_more_evidence") is True
        and rubric.get("safe_to_act") is False
        and rubric.get("needs_human_escalation") is False
        and canonical_endpoint(output) is None
    )


def is_e14f_repair_prompt(prompt: str) -> bool:
    return E14F_REPAIR_MARKER in prompt


def build_adjudication_prompt(original_prompt: str, draft: dict[str, Any]) -> str:
    if not is_public_conservative_collapse_draft(draft):
        raise AssertionError("E14m adjudication prompt requires the preregistered conservative-collapse draft shape")

    endpoints = "\n".join(f"- {endpoint}" for endpoint in SUPPORTED_ACTION_ENDPOINTS)
    return (
        original_prompt
        + "\n\nPUBLIC DECISION ADJUDICATION PASS\n"
        + "The first draft below is parseable and internally consistent, but it matches a preregistered fully conservative public policy shape. "
          "This trigger comes only from your own draft; it is not evaluator feedback and contains no expected answer. Re-evaluate the final decision once using only the original visible packet.\n\n"
        + "First draft JSON:\n"
        + json.dumps(draft, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n\nSupported public action endpoints:\n"
        + endpoints
        + "\n\nAdjudication rules:\n"
          "- Do not force action or escalation merely to differ from the first draft. The correct result may remain investigate_only.\n"
          "- Distinguish evidence that is genuinely absent from the visible packet from evidence you merely listed as a planned GET. A planned GET is not proof that the corresponding fact is absent, and it is not an observation already made.\n"
          "- Reconsider immediate action only when facts already visible in the packet support one concrete public endpoint and the existing safety semantics. Never invent measurements, statuses, permissions, identifiers, model state, knowledge results, severity, or hidden facts.\n"
          "- Reconsider human/specialist escalation when visible safety risk, material severity, specialist-needed uncertainty, or permission blocking makes human handling the appropriate current step.\n"
          "- If you retain investigate_only or insufficient_evidence, identify in calibration_reason and proposed_next_step the specific visible information gap that blocks both a supported immediate action and a supported human handoff. Generic uncertainty or 'more evidence would be useful' is not enough.\n"
          "- If choosing immediate reprocess, preserve the existing public rule: state a human-readable visible evidence-to-reprocess reason and rely on at least two existing public support-anchor classes. If those anchors are not in the visible packet, do not invent them.\n"
          "- Autonomous state-changing actions remain subject to the existing public evidence minimum and human-review semantics.\n"
          "- Choose at most one primary action endpoint. Do not enumerate alternatives merely to hedge.\n"
          "- Keep evidence_plan grounded and relevant; do not add unrelated GETs to satisfy counts.\n"
          "- Return exactly one JSON object in the original schema, with no Markdown and no commentary outside JSON.\n"
    )


def run_self_checks() -> None:
    collapsed = {
        "decision_class": "investigate_only",
        "evidence_plan": ["GET /assets/asset-selfcheck", "GET /assets/asset-selfcheck/analyses"],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Collect more evidence.",
        "risk_notes": "Uncertainty remains.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": True,
            "safe_to_act": False,
            "action_endpoint": "none",
            "needs_human_escalation": False,
            "calibration_reason": "More evidence is needed.",
        },
    }
    if not is_public_conservative_collapse_draft(collapsed):
        raise AssertionError("registered collapse shape must trigger E14m")

    action = json.loads(json.dumps(collapsed))
    action["decision_class"] = "action_candidate"
    action["should_take_action_now"] = True
    action["action_escalation_rubric"]["needs_more_evidence"] = False
    action["action_escalation_rubric"]["safe_to_act"] = True
    action["action_escalation_rubric"]["action_endpoint"] = "POST /analyses/analysis-selfcheck/reprocess"
    if is_public_conservative_collapse_draft(action):
        raise AssertionError("action candidate must not trigger conservative-collapse adjudication")

    escalation = json.loads(json.dumps(collapsed))
    escalation["decision_class"] = "escalation_candidate"
    escalation["requires_human_escalation"] = True
    escalation["action_escalation_rubric"]["needs_human_escalation"] = True
    escalation["action_escalation_rubric"]["action_endpoint"] = "POST /analyses/analysis-selfcheck/request-specialist"
    if is_public_conservative_collapse_draft(escalation):
        raise AssertionError("escalation candidate must not trigger conservative-collapse adjudication")

    prompt = build_adjudication_prompt("VISIBLE ORIGINAL PROMPT", collapsed)
    required_fragments = (
        "not evaluator feedback",
        "Do not force action or escalation",
        "specific visible information gap",
        "Choose at most one primary action endpoint",
        "POST /analyses/{analysis_id}/request-specialist",
    )
    if not all(fragment in prompt for fragment in required_fragments):
        raise AssertionError("E14m adjudication prompt is missing a frozen public rule")
    forbidden_fragments = ("expected-path", "oracle says", "correct label", "validation feedback", "locked-test answer")
    lower = prompt.lower()
    if any(fragment in lower for fragment in forbidden_fragments):
        raise AssertionError("E14m adjudication prompt contains forbidden evaluator language")

    if not is_e14f_repair_prompt("x PUBLIC SEMANTIC CONSISTENCY REPAIR PASS y"):
        raise AssertionError("E14f repair marker detection must remain stable")


if __name__ == "__main__":
    run_self_checks()
    print("E14M_PUBLIC_DECISION_ADJUDICATION_SELF_CHECK_PASS")
