from __future__ import annotations

import json
from pathlib import Path

from academy_tractian.adaptive_experiment_preflight import run_adaptive_experiment_preflight


DEV_CASES = {
    "asset_G501": ("TKT-INV-04", "TKT-EXE-16"),
    "asset_C710": ("TKT-INV-05", "TKT-EXE-13"),
    "asset_S420": ("TKT-INV-06", "TKT-EXE-15"),
    "asset_M208": ("TKT-INV-11b",),
    "asset_M101": ("TKT-CTX-01",),
}
VALIDATION_CASES = {
    "asset_B204": ("TKT-INV-09", "TKT-EXE-12", "TKT-CTX-02"),
    "asset_M102": ("TKT-INV-11",),
}
LOCKED_CASES = {
    "asset_V301": ("TKT-INV-10", "TKT-CTX-03", "TKT-EXE-14"),
    "asset_M605": ("TKT-INV-07",),
    "asset_M205": ("TKT-INV-08",),
}
DEV_GROUPS = tuple(DEV_CASES)
DEV_TICKETS = tuple(ticket for tickets in DEV_CASES.values() for ticket in tickets)
ALL_CASES = {**DEV_CASES, **VALIDATION_CASES, **LOCKED_CASES}


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _split_groups(mapping: dict[str, tuple[str, ...]]) -> list[dict[str, object]]:
    return [
        {
            "group_id": group_id,
            "tickets": list(tickets),
            "scenarios": [f"scenario-{ticket}" for ticket in tickets],
        }
        for group_id, tickets in mapping.items()
    ]


def _manifest(tmp_path: Path, *, locked_forbidden: bool = True) -> Path:
    forbidden = ["prompt tuning", "model selection", "threshold fitting"]
    if locked_forbidden:
        forbidden.extend(["runtime selection", "agent policy debugging"])
    return _write_json(
        tmp_path / "benchmark-split-v1.json",
        {
            "schema_version": "benchmark-split-v1",
            "status": "FROZEN",
            "unit_of_assignment": "asset_story_group",
            "source_group_count": len(ALL_CASES),
            "ticket_count": sum(len(tickets) for tickets in ALL_CASES.values()),
            "rules": {
                "no_storyline_split": True,
                "locked_test_available_for_architecture_selection": False,
                "locked_test_available_for_prompt_or_model_selection": False,
                "gold_is_evaluator_only": True,
            },
            "splits": {
                "DEV": {"groups": _split_groups(DEV_CASES)},
                "VALIDATION": {"groups": _split_groups(VALIDATION_CASES)},
                "LOCKED_TEST": {"groups": _split_groups(LOCKED_CASES)},
            },
            "aggregate_counts": {
                "DEV": {"groups": len(DEV_CASES)},
                "VALIDATION": {"groups": len(VALIDATION_CASES)},
                "LOCKED_TEST": {"groups": len(LOCKED_CASES)},
            },
            "locked_test_policy": {
                "allowed_before_final": ["counting groups", "leakage assertion"],
                "forbidden_before_final": forbidden,
            },
        },
    )


def _canonical_records(*, locked_message: str = "public locked case") -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    index = 0
    for asset_id, tickets in ALL_CASES.items():
        for ticket_id in tickets:
            index += 1
            rows.append(
                {
                    "id": f"case_{index:02d}",
                    "ticket_id": ticket_id,
                    "company_id": f"company_{index:02d}",
                    "user_id": f"user_{index:02d}",
                    "asset_id": asset_id,
                    "message": locked_message if asset_id in LOCKED_CASES else f"public message {ticket_id}",
                }
            )
    return rows


def _cases(tmp_path: Path, rows: list[dict[str, str]] | None = None) -> Path:
    return _write_json(tmp_path / "cases.json", rows if rows is not None else _canonical_records())


def test_missing_canonical_source_fails_closed_with_exact_reason(tmp_path: Path) -> None:
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=tmp_path / "not-materialized.json",
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.experiment_id == "ADAPT-A-001"
    assert result.execution_status == "NOT_READY"
    assert result.decision == "INCONCLUSIVE"
    assert result.reason == "CANONICAL_DEV_CASE_SOURCE_NOT_MATERIALIZED"
    assert result.source_materialized is False
    assert result.source_sha256 is None
    assert result.required_dev_groups == DEV_GROUPS
    assert result.observed_group_ids == ()


def test_legacy_alias_container_is_rejected_instead_of_guessed(tmp_path: Path) -> None:
    legacy = {
        "cases": [
            {"asset_group": group_id, "prompt": "not canonical", "oracle": "private"}
            for group_id in DEV_GROUPS
        ]
    }
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=_write_json(tmp_path / "legacy.json", legacy),
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.execution_status == "NOT_READY"
    assert result.reason == "CANONICAL_AGENT_INPUT_SCHEMA_MISMATCH"


def test_extra_oracle_field_is_rejected_by_exact_public_input_contract(tmp_path: Path) -> None:
    rows = _canonical_records()
    rows[0]["oracle"] = "private-gold"  # type: ignore[index]
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=_cases(tmp_path, rows),
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.execution_status == "NOT_READY"
    assert result.reason == "CANONICAL_AGENT_INPUT_SCHEMA_MISMATCH"


def test_missing_manifest_ticket_makes_source_incomplete(tmp_path: Path) -> None:
    rows = [row for row in _canonical_records() if row["ticket_id"] != "TKT-CTX-01"]
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=_cases(tmp_path, rows),
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.execution_status == "NOT_READY"
    assert result.reason == "CANONICAL_CASE_SOURCE_INCOMPLETE"
    assert "TKT-CTX-01" not in result.selected_dev_ticket_ids


def test_duplicate_ticket_or_case_id_fails_closed(tmp_path: Path) -> None:
    rows = _canonical_records()
    duplicate = dict(rows[0])
    duplicate["id"] = "different-id-same-ticket"
    rows.append(duplicate)
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=_cases(tmp_path, rows),
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.execution_status == "NOT_READY"
    assert result.reason == "DUPLICATE_CANONICAL_CASE"


def test_dev_ticket_mapped_to_locked_group_is_explicit_contamination(tmp_path: Path) -> None:
    rows = _canonical_records()
    target = next(row for row in rows if row["ticket_id"] == "TKT-INV-04")
    target["asset_id"] = "asset_V301"
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=_cases(tmp_path, rows),
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.execution_status == "NOT_READY"
    assert result.reason == "FORBIDDEN_SPLIT_CONTAMINATION"


def test_unfrozen_or_weakened_locked_policy_invalidates_preflight(tmp_path: Path) -> None:
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=_cases(tmp_path),
        split_manifest_path=_manifest(tmp_path, locked_forbidden=False),
    )

    assert result.execution_status == "NOT_READY"
    assert result.reason == "INVALID_STRUCTURAL_METADATA"


def test_full_canonical_source_projects_exactly_eight_dev_cases_across_five_groups(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    source = _cases(tmp_path)

    first = run_adaptive_experiment_preflight(
        agent_input_cases_path=source,
        split_manifest_path=manifest,
    )
    second = run_adaptive_experiment_preflight(
        agent_input_cases_path=source,
        split_manifest_path=manifest,
    )

    assert first.execution_status == "READY"
    assert first.decision == "INCONCLUSIVE"
    assert first.reason is None
    assert first.source_materialized is True
    assert first.source_contract_version == "tractian-agent-input-cases-v1"
    assert first.source_case_count == 17
    assert first.selected_dev_case_count == 8
    assert first.required_dev_groups == DEV_GROUPS
    assert set(first.observed_group_ids) == set(DEV_GROUPS)
    assert set(first.selected_dev_ticket_ids) == set(DEV_TICKETS)
    assert not (set(first.selected_dev_ticket_ids) & set(ticket for tickets in LOCKED_CASES.values() for ticket in tickets))
    assert first.source_sha256 is not None and len(first.source_sha256) == 64
    assert first.manifest_sha256 is not None and len(first.manifest_sha256) == 64
    assert first.dev_projection_sha256 is not None and len(first.dev_projection_sha256) == 64
    assert first.source_sha256 == second.source_sha256
    assert first.manifest_sha256 == second.manifest_sha256
    assert first.dev_projection_sha256 == second.dev_projection_sha256


def test_safe_result_never_exposes_case_messages_or_protected_ticket_ids(tmp_path: Path) -> None:
    source = _cases(tmp_path, _canonical_records(locked_message="private-locked-message"))
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=source,
        split_manifest_path=_manifest(tmp_path),
    )

    serialized = json.dumps(result.model_dump(), sort_keys=True)
    assert result.execution_status == "READY"
    assert "private-locked-message" not in serialized
    assert "public message" not in serialized
    assert "oracle" not in serialized
    for tickets in LOCKED_CASES.values():
        for ticket_id in tickets:
            assert ticket_id not in serialized
    for tickets in VALIDATION_CASES.values():
        for ticket_id in tickets:
            assert ticket_id not in serialized
