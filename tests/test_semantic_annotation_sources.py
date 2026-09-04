from __future__ import annotations

import pytest

from academy_tractian.observability import SafeEvidenceRef, SafeRun
from academy_tractian.observability_store import ObservabilityStore
from academy_tractian.semantic_annotation_sources import (
    SemanticAnnotationSourceManifest,
    build_validation_semantic_annotation_sources,
    freeze_semantic_source_selection,
)


def _split_payload() -> dict:
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {"groups": [{"group_id": "dev", "scenarios": ["CEN-DEV-A"]}]},
            "VALIDATION": {
                "groups": [
                    {"group_id": "val-a", "scenarios": ["CEN-VAL-A"]},
                    {"group_id": "val-b", "scenarios": ["CEN-VAL-B"]},
                ]
            },
            "LOCKED_TEST": {
                "groups": [{"group_id": "lock", "scenarios": ["CEN-LOCK-A"]}]
            },
        },
    }


def _persist(
    store: ObservabilityStore,
    *,
    run_id: str,
    scenario_id: str,
    completed: bool = True,
    message: str = "The sanitized evidence supports the operational conclusion.",
) -> None:
    run = SafeRun(
        run_id=run_id,
        scenario_id=scenario_id,
        config_hash="cfg",
        event_count=1,
        model_calls=1,
        tool_proposals=0,
        tool_calls=1,
        policy_blocks=0,
        errors=0,
        terminal_decision="ORIENT",
        terminal_response_mode="complete",
        terminal_reason_code=None,
        terminal_message=message,
        completed=completed,
    )
    evidence = (
        SafeEvidenceRef(
            evidence_id=f"EV-{scenario_id}",
            run_id=run_id,
            sequence=0,
            tool_name="get_analysis",
            status_code=200,
        ),
    )
    store.persist_projection(run, (), evidence)


def test_builds_hash_bound_sources_only_from_safe_validation_runs(tmp_path) -> None:
    store = ObservabilityStore(tmp_path / "safe.duckdb")
    _persist(store, run_id="run_val_a", scenario_id="CEN-VAL-A")
    _persist(store, run_id="run_val_b", scenario_id="CEN-VAL-B")
    selection = freeze_semantic_source_selection(("run_val_a", "run_val_b"))

    sources, manifest = build_validation_semantic_annotation_sources(
        store=store,
        selection=selection,
        frozen_split_payload=_split_payload(),
    )

    assert [source.scenario_id for source in sources] == ["CEN-VAL-A", "CEN-VAL-B"]
    assert sources[0].safe_evidence_context == (
        "Evidence EV-CEN-VAL-A: tool=get_analysis; status=200.",
    )
    assert manifest.source_split == "VALIDATION"
    assert manifest.selection_sha256 == selection.selection_sha256
    assert manifest.source_count == 2
    assert len(manifest.manifest_sha256) == 64
    assert SemanticAnnotationSourceManifest.model_validate_json(manifest.model_dump_json()) == manifest


def test_selection_and_manifest_hashes_reject_tampering(tmp_path) -> None:
    selection = freeze_semantic_source_selection(("run_a", "run_b"))
    payload = selection.model_dump(mode="json")
    payload["run_ids"] = ["run_a", "run_c"]
    with pytest.raises(ValueError, match="selection hash mismatch"):
        type(selection).model_validate(payload)

    store = ObservabilityStore(tmp_path / "safe.duckdb")
    _persist(store, run_id="run_a", scenario_id="CEN-VAL-A")
    _persist(store, run_id="run_b", scenario_id="CEN-VAL-B")
    sources, manifest = build_validation_semantic_annotation_sources(
        store=store,
        selection=selection,
        frozen_split_payload=_split_payload(),
    )
    assert len(sources) == 2
    tampered = manifest.model_dump(mode="json")
    tampered["bindings"][0]["run_id"] = "run_other"
    with pytest.raises(ValueError, match="manifest hash mismatch"):
        SemanticAnnotationSourceManifest.model_validate(tampered)


def test_dev_locked_incomplete_missing_terminal_and_duplicate_scenarios_fail_closed(tmp_path) -> None:
    store = ObservabilityStore(tmp_path / "safe.duckdb")
    _persist(store, run_id="run_dev", scenario_id="CEN-DEV-A")
    _persist(store, run_id="run_lock", scenario_id="CEN-LOCK-A")
    _persist(store, run_id="run_incomplete", scenario_id="CEN-VAL-A", completed=False)
    _persist(store, run_id="run_val_a_1", scenario_id="CEN-VAL-A")
    _persist(store, run_id="run_val_a_2", scenario_id="CEN-VAL-A")

    for run_id in ("run_dev", "run_lock"):
        with pytest.raises(ValueError, match="requires VALIDATION"):
            build_validation_semantic_annotation_sources(
                store=store,
                selection=freeze_semantic_source_selection((run_id,)),
                frozen_split_payload=_split_payload(),
            )

    with pytest.raises(ValueError, match="not complete"):
        build_validation_semantic_annotation_sources(
            store=store,
            selection=freeze_semantic_source_selection(("run_incomplete",)),
            frozen_split_payload=_split_payload(),
        )

    with pytest.raises(ValueError, match="multiple runs for scenario"):
        build_validation_semantic_annotation_sources(
            store=store,
            selection=freeze_semantic_source_selection(("run_val_a_1", "run_val_a_2")),
            frozen_split_payload=_split_payload(),
        )


def test_split_must_be_frozen_and_unknown_run_fails_closed(tmp_path) -> None:
    store = ObservabilityStore(tmp_path / "safe.duckdb")
    split = _split_payload()
    split["status"] = "DRAFT"
    with pytest.raises(ValueError, match="requires a FROZEN split manifest"):
        build_validation_semantic_annotation_sources(
            store=store,
            selection=freeze_semantic_source_selection(("run_missing",)),
            frozen_split_payload=split,
        )

    with pytest.raises(KeyError, match="safe observability run not found"):
        build_validation_semantic_annotation_sources(
            store=store,
            selection=freeze_semantic_source_selection(("run_missing",)),
            frozen_split_payload=_split_payload(),
        )