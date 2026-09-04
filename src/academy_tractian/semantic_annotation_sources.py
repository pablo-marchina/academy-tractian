from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .observability_store import ObservabilityStore
from .semantic_human_calibration import SemanticAnnotationSource


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


class SemanticSourceSelection(_FrozenModel):
    """Predeclared safe-run selection for held-out semantic source materialization."""

    schema_version: Literal["semantic-source-selection-v1"] = "semantic-source-selection-v1"
    status: Literal["FROZEN"] = "FROZEN"
    run_ids: tuple[str, ...] = Field(min_length=1)
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_selection(self) -> "SemanticSourceSelection":
        if len(set(self.run_ids)) != len(self.run_ids):
            raise ValueError("semantic source selection contains duplicate run ids")
        if any(not run_id.strip() for run_id in self.run_ids):
            raise ValueError("semantic source selection run ids must be non-empty")
        expected = _canonical_sha256(
            {
                "schema_version": self.schema_version,
                "status": self.status,
                "run_ids": list(self.run_ids),
            }
        )
        if self.selection_sha256 != expected:
            raise ValueError("semantic source selection hash mismatch")
        return self


class SemanticSourceBinding(_FrozenModel):
    scenario_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class SemanticAnnotationSourceManifest(_FrozenModel):
    """Evaluator-private integrity manifest for generated VALIDATION sources."""

    schema_version: Literal["semantic-annotation-source-manifest-v1"] = (
        "semantic-annotation-source-manifest-v1"
    )
    source_split: Literal["VALIDATION"] = "VALIDATION"
    frozen_split_schema_version: str = Field(min_length=1)
    frozen_split_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_count: int = Field(ge=1)
    bindings: tuple[SemanticSourceBinding, ...]
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_manifest(self) -> "SemanticAnnotationSourceManifest":
        if self.source_count != len(self.bindings):
            raise ValueError("semantic source manifest count does not match bindings")
        if len({item.run_id for item in self.bindings}) != len(self.bindings):
            raise ValueError("semantic source manifest contains duplicate run ids")
        if len({item.scenario_id for item in self.bindings}) != len(self.bindings):
            raise ValueError("semantic source manifest contains duplicate scenarios")
        expected = _manifest_hash(
            split_schema_version=self.frozen_split_schema_version,
            split_sha256=self.frozen_split_sha256,
            selection_sha256=self.selection_sha256,
            bindings=self.bindings,
        )
        if self.manifest_sha256 != expected:
            raise ValueError("semantic source manifest hash mismatch")
        return self


def freeze_semantic_source_selection(run_ids: Sequence[str]) -> SemanticSourceSelection:
    canonical = tuple(str(run_id).strip() for run_id in run_ids)
    payload = {
        "schema_version": "semantic-source-selection-v1",
        "status": "FROZEN",
        "run_ids": list(canonical),
    }
    return SemanticSourceSelection(
        run_ids=canonical,
        selection_sha256=_canonical_sha256(payload),
    )


def _validation_scenarios(
    frozen_split_payload: Mapping[str, Any],
) -> tuple[set[str], str, str]:
    schema_version = str(frozen_split_payload.get("schema_version") or "")
    if not schema_version:
        raise ValueError("split manifest missing schema_version")
    if frozen_split_payload.get("status") != "FROZEN":
        raise ValueError("semantic source generation requires a FROZEN split manifest")
    splits = frozen_split_payload.get("splits")
    if not isinstance(splits, Mapping):
        raise ValueError("split manifest missing splits object")

    assignments: dict[str, str] = {}
    for split_name in ("DEV", "VALIDATION", "LOCKED_TEST"):
        section = splits.get(split_name)
        if not isinstance(section, Mapping):
            raise ValueError(f"split manifest missing {split_name}")
        groups = section.get("groups")
        if not isinstance(groups, list):
            raise ValueError(f"split manifest {split_name} groups must be a list")
        for group in groups:
            if not isinstance(group, Mapping) or not isinstance(group.get("scenarios"), list):
                raise ValueError("split group missing scenarios")
            for scenario in group["scenarios"]:
                scenario_id = str(scenario)
                if scenario_id in assignments:
                    raise ValueError(f"scenario assigned more than once: {scenario_id}")
                assignments[scenario_id] = split_name

    validation = {scenario for scenario, split in assignments.items() if split == "VALIDATION"}
    return validation, schema_version, _canonical_sha256(frozen_split_payload)


def _evidence_context(store: ObservabilityStore, run_id: str) -> tuple[str, ...]:
    rows = store.get_evidence(run_id)
    context: list[str] = []
    for row in rows:
        evidence_id = str(row.get("evidence_id") or "").strip()
        if not evidence_id:
            raise RuntimeError("safe observability evidence row missing evidence_id")
        tool = str(row.get("tool_name") or "unknown")
        status = row.get("status_code")
        status_text = "unknown" if status is None else str(status)
        context.append(f"Evidence {evidence_id}: tool={tool}; status={status_text}.")
    return tuple(context)


def _manifest_hash(
    *,
    split_schema_version: str,
    split_sha256: str,
    selection_sha256: str,
    bindings: Sequence[SemanticSourceBinding],
) -> str:
    return _canonical_sha256(
        {
            "schema_version": "semantic-annotation-source-manifest-v1",
            "source_split": "VALIDATION",
            "frozen_split_schema_version": split_schema_version,
            "frozen_split_sha256": split_sha256,
            "selection_sha256": selection_sha256,
            "bindings": [item.model_dump(mode="json") for item in bindings],
        }
    )


def build_validation_semantic_annotation_sources(
    *,
    store: ObservabilityStore,
    selection: SemanticSourceSelection,
    frozen_split_payload: Mapping[str, Any],
) -> tuple[tuple[SemanticAnnotationSource, ...], SemanticAnnotationSourceManifest]:
    """Materialize held-out sources exclusively from the persisted browser-safe read model.

    Raw RunTrace/provider payloads are intentionally not accepted. The exact safe run IDs must be
    frozen in ``selection`` and every persisted scenario must belong to VALIDATION in the frozen
    benchmark split. DEV and LOCKED_TEST therefore fail closed before reviewer packet creation.
    """

    if not store.ready():
        raise RuntimeError("observability_store_not_ready")
    validation_scenarios, split_schema_version, split_sha256 = _validation_scenarios(
        frozen_split_payload
    )

    sources: list[SemanticAnnotationSource] = []
    bindings: list[SemanticSourceBinding] = []
    seen_scenarios: set[str] = set()
    for run_id in selection.run_ids:
        row = store.get_run(run_id)
        if row is None:
            raise KeyError(f"safe observability run not found: {run_id}")
        scenario_id = str(row.get("scenario_id") or "")
        if scenario_id not in validation_scenarios:
            raise ValueError(
                f"semantic held-out source requires VALIDATION scenario; {scenario_id or '<missing>'} is not eligible"
            )
        if scenario_id in seen_scenarios:
            raise ValueError(f"semantic source selection contains multiple runs for scenario: {scenario_id}")
        if row.get("completed") is not True:
            raise ValueError(f"semantic source run is not complete: {run_id}")

        decision = row.get("terminal_decision")
        response_mode = row.get("terminal_response_mode")
        message = row.get("terminal_message")
        if not isinstance(decision, str) or not decision.strip():
            raise ValueError(f"semantic source run has no terminal decision: {run_id}")
        if not isinstance(response_mode, str) or not response_mode.strip():
            raise ValueError(f"semantic source run has no terminal response mode: {run_id}")
        if not isinstance(message, str) or not message.strip():
            raise ValueError(f"semantic source run has no terminal message: {run_id}")

        source = SemanticAnnotationSource(
            scenario_id=scenario_id,
            terminal_decision=decision,
            response_mode=response_mode,
            terminal_message=message,
            safe_evidence_context=_evidence_context(store, run_id),
        )
        sources.append(source)
        bindings.append(
            SemanticSourceBinding(
                scenario_id=scenario_id,
                run_id=run_id,
                output_sha256=source.output_sha256,
                context_sha256=source.context_sha256,
            )
        )
        seen_scenarios.add(scenario_id)

    ordered_bindings = tuple(bindings)
    manifest = SemanticAnnotationSourceManifest(
        frozen_split_schema_version=split_schema_version,
        frozen_split_sha256=split_sha256,
        selection_sha256=selection.selection_sha256,
        source_count=len(sources),
        bindings=ordered_bindings,
        manifest_sha256=_manifest_hash(
            split_schema_version=split_schema_version,
            split_sha256=split_sha256,
            selection_sha256=selection.selection_sha256,
            bindings=ordered_bindings,
        ),
    )
    return tuple(sources), manifest