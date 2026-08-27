#!/usr/bin/env python3
"""P12-C1 prospective evidence-route candidate implementations.

This module contains only the deterministic C0/C1 route-selection policies
preregistered for P12-C1. It never reads evaluator/private oracle data and it
never touches FRESH_BLIND or LEGACY_LOCKED_TEST.

C0 is a rate-normalized prospective port of the historical E14t reference:
recompute the frozen E14s public candidate-pool selection, then restore at most
floor(0.4 * N) omitted original public reads globally, max one per output and
max seven reads/output.

C1 is the materially simpler parent-top7 baseline:
keep canonical public GET signatures already present in the parent evidence
plan, first-occurrence order, deduplicated, max seven. It adds no route.
"""

from __future__ import annotations

import copy
import importlib.util
import math
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
S_PATH = HERE / "e14s_full_dev_public_evidence_candidate_pool_consensus_guard.py"
S_SPEC = importlib.util.spec_from_file_location("e14s_parent_for_p12_c1", S_PATH)
if S_SPEC is None or S_SPEC.loader is None:
    raise RuntimeError("failed to load frozen E14s parent")
e14s = importlib.util.module_from_spec(S_SPEC)
S_SPEC.loader.exec_module(e14s)

MAX_FINAL_READS_PER_OUTPUT = 7
C0_ADDITION_RATE = 0.4
MAX_ADDITIONAL_READS_PER_OUTPUT = 1

C0_ID = "E14T_REFERENCE_PORT_V1"
C1_ID = "PARENT_TOP7_CANONICAL_V1"


def _non_evidence_signature(output: dict[str, Any]) -> dict[str, Any]:
    cloned = copy.deepcopy(output)
    cloned.pop("evidence_plan", None)
    return cloned


def canonical_parent_reads(output: dict[str, Any]) -> list[str]:
    """Return canonical public GETs already present in parent evidence_plan."""
    return list(e14s._ordered_observed_reads(output))


def _first_omitted_original(original: list[str], selected: list[str]) -> str | None:
    selected_set = set(selected)
    for signature in original:
        if signature not in selected_set:
            return signature
    return None


def c0_global_addition_budget(output_count: int) -> int:
    if output_count < 0:
        raise ValueError("output_count must be non-negative")
    return math.floor(C0_ADDITION_RATE * output_count)


def apply_c1(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply C1. Only evidence_plan may change; no new route may be introduced."""
    before = copy.deepcopy(output)
    selected = canonical_parent_reads(before)[:MAX_FINAL_READS_PER_OUTPUT]
    result = copy.deepcopy(before)
    result["evidence_plan"] = e14s._evidence_items(selected)

    after = canonical_parent_reads(result)
    original = canonical_parent_reads(before)
    if after != selected:
        raise AssertionError("C1 route serialization changed selected order")
    if not set(after).issubset(set(original)):
        raise AssertionError("C1 introduced a route absent from parent evidence_plan")
    if _non_evidence_signature(before) != _non_evidence_signature(result):
        raise AssertionError("C1 changed a non-evidence field")

    return result, {
        "candidate_id": C1_ID,
        "parent_read_count": len(original),
        "final_read_count": len(after),
        "added_read_count": len(set(after) - set(original)),
        "max_final_reads": MAX_FINAL_READS_PER_OUTPUT,
        "non_evidence_preserved": True,
        "private_oracle_used": False,
    }


def apply_c0_batch(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Apply C0 to matched records using one global preregistered budget.

    Each record must contain:
      - ``visible_case``: agent-visible public case object
      - ``output``: fixed common-parent parsed output

    The function intentionally has no group/ticket selectors.
    """
    entries: list[dict[str, Any]] = []
    for stable_index, record in enumerate(records):
        visible_case = record.get("visible_case")
        output = record.get("output")
        if not isinstance(visible_case, dict) or not isinstance(output, dict):
            raise AssertionError("C0 requires visible_case and fixed output objects")

        original = canonical_parent_reads(output)
        base_selected, base_meta = e14s.selected_read_signatures(visible_case, output)
        base_selected = list(base_selected)
        restoration_candidate = _first_omitted_original(original, base_selected)

        entries.append(
            {
                "stable_index": stable_index,
                "before": copy.deepcopy(output),
                "original": original,
                "base_selected": base_selected,
                "original_candidate_count": len(set(original)),
                "candidate_pool_count": int(base_meta.get("candidate_pool_count", 0)),
                "restoration_candidate": restoration_candidate,
            }
        )

    global_budget = c0_global_addition_budget(len(entries))
    eligible = [
        entry
        for entry in entries
        if entry["restoration_candidate"] is not None
        and len(entry["base_selected"]) < MAX_FINAL_READS_PER_OUTPUT
    ]
    eligible.sort(
        key=lambda entry: (
            -int(entry["original_candidate_count"]),
            -int(entry["candidate_pool_count"]),
            int(entry["stable_index"]),
        )
    )
    chosen = {
        int(entry["stable_index"])
        for entry in eligible[:global_budget]
    }

    transformed: list[dict[str, Any]] = []
    additions_total = 0
    for entry in entries:
        selected = list(entry["base_selected"])
        additions_this_output = 0
        if int(entry["stable_index"]) in chosen:
            candidate = entry["restoration_candidate"]
            if candidate is None or candidate not in set(entry["original"]):
                raise AssertionError("C0 restoration candidate left original public route pool")
            if candidate not in selected:
                selected.append(candidate)
                additions_this_output = 1

        if additions_this_output > MAX_ADDITIONAL_READS_PER_OUTPUT:
            raise AssertionError("C0 exceeded per-output restoration budget")
        if len(selected) > MAX_FINAL_READS_PER_OUTPUT:
            raise AssertionError("C0 exceeded per-output read cap")

        before = entry["before"]
        result = copy.deepcopy(before)
        result["evidence_plan"] = e14s._evidence_items(selected)
        after = canonical_parent_reads(result)

        if after != selected:
            raise AssertionError("C0 route serialization changed selected order")
        if not set(after).issubset(set(entry["original"]) | set(entry["base_selected"])):
            raise AssertionError("C0 introduced route outside frozen public candidate sources")
        if _non_evidence_signature(before) != _non_evidence_signature(result):
            raise AssertionError("C0 changed a non-evidence field")

        additions_total += additions_this_output
        transformed.append(result)

    if additions_total > global_budget:
        raise AssertionError("C0 exceeded global rate-normalized restoration budget")

    return transformed, {
        "candidate_id": C0_ID,
        "output_count": len(entries),
        "global_addition_budget": global_budget,
        "additions_total": additions_total,
        "max_additional_reads_per_output": MAX_ADDITIONAL_READS_PER_OUTPUT,
        "max_final_reads_per_output": MAX_FINAL_READS_PER_OUTPUT,
        "non_evidence_preserved": True,
        "private_oracle_used": False,
    }
