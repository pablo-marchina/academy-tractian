from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI

from .semantic_human_calibration import SemanticAnnotationSource, build_semantic_reviewer_packet
from .semantic_review_collection import SEMANTIC_REVIEW_PERMISSION


_E2E_FLAG = "ACADEMY_E2E_SEMANTIC_REVIEW"
_E2E_ORGANIZATION = "e2e-org-a"


def provider_free_semantic_review_enabled() -> bool:
    return os.environ.get(_E2E_FLAG, "0") == "1"


def provider_free_semantic_review_permissions() -> frozenset[str]:
    if not provider_free_semantic_review_enabled():
        return frozenset()
    return frozenset({SEMANTIC_REVIEW_PERMISSION})


def _frozen_split() -> dict[str, Any]:
    # Synthetic acceptance-only split. It is never project calibration evidence.
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {
                "groups": [{"group_id": "semantic-e2e-dev", "scenarios": ["SEM-E2E-DEV"]}]
            },
            "VALIDATION": {
                "groups": [
                    {"group_id": "semantic-e2e-val-a", "scenarios": ["SEM-E2E-VAL-A"]},
                    {"group_id": "semantic-e2e-val-b", "scenarios": ["SEM-E2E-VAL-B"]},
                ]
            },
            "LOCKED_TEST": {
                "groups": [{"group_id": "semantic-e2e-lock", "scenarios": ["SEM-E2E-LOCK"]}]
            },
        },
    }


def _sources() -> tuple[SemanticAnnotationSource, ...]:
    return (
        SemanticAnnotationSource(
            scenario_id="SEM-E2E-VAL-A",
            terminal_decision="ORIENT",
            response_mode="complete",
            terminal_message="The sanitized asset evidence supports monitoring without corrective action.",
            safe_evidence_context=(
                "Evidence EV-semantic-e2e-a: tool=get_asset; status=200.",
            ),
        ),
        SemanticAnnotationSource(
            scenario_id="SEM-E2E-VAL-B",
            terminal_decision="ESCALATE_HUMAN",
            response_mode="partial",
            terminal_message="The sanitized evidence remains incomplete, so an engineer should continue the investigation.",
            safe_evidence_context=(
                "Evidence EV-semantic-e2e-b: tool=get_analysis; status=206.",
            ),
        ),
    )


def register_provider_free_semantic_review_packet(app: FastAPI) -> None:
    if not provider_free_semantic_review_enabled():
        return
    packet, manifest = build_semantic_reviewer_packet(
        sources=_sources(),
        frozen_split_payload=_frozen_split(),
        purpose="HELD_OUT_CALIBRATION",
        deterministic_shuffle_seed=20260903,
        minimum_distinct_groups=2,
    )
    app.state.semantic_review_collection_store.register_packet(
        organization_id=_E2E_ORGANIZATION,
        packet=packet,
        manifest=manifest,
    )