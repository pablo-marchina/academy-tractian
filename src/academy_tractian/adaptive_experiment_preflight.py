from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence


EXPERIMENT_ID = "ADAPT-A-001"
DEFAULT_SPLIT_MANIFEST = Path("research/frozen/benchmark-split-v1.json")
CANONICAL_AGENT_INPUT_SCHEMA = "tractian-agent-input-cases-v1"
CANONICAL_CASE_FIELDS = frozenset(
    {"id", "ticket_id", "company_id", "user_id", "asset_id", "message"}
)
EXPECTED_SPLIT_SCHEMA_VERSION = "benchmark-split-v1"
EXPECTED_SPLIT_STATUS = "FROZEN"
EXPECTED_ASSIGNMENT_UNIT = "asset_story_group"

ExecutionStatus = Literal["READY", "NOT_READY"]
Decision = Literal["INCONCLUSIVE"]
ReasonCode = Literal[
    "CANONICAL_DEV_CASE_SOURCE_NOT_MATERIALIZED",
    "CANONICAL_CASE_SOURCE_INCOMPLETE",
    "CANONICAL_AGENT_INPUT_SCHEMA_MISMATCH",
    "CANONICAL_SOURCE_MANIFEST_MISMATCH",
    "FORBIDDEN_SPLIT_CONTAMINATION",
    "DUPLICATE_CANONICAL_CASE",
    "MANIFEST_NOT_MATERIALIZED",
    "INVALID_STRUCTURAL_METADATA",
]


@dataclass(frozen=True)
class AdaptiveExperimentPreflightResult:
    """Safe structural readiness result for ADAPT-A-001.

    The result contains hashes and public structural identifiers only. It never returns case
    messages, prompts, evidence, model output, expected conclusions, oracle rows, rubrics or gold.
    """

    experiment_id: str
    execution_status: ExecutionStatus
    decision: Decision
    reason: ReasonCode | None
    source_materialized: bool
    source_contract_version: str | None
    source_sha256: str | None
    manifest_sha256: str | None
    dev_projection_sha256: str | None
    source_case_count: int
    selected_dev_case_count: int
    required_dev_groups: tuple[str, ...]
    observed_group_ids: tuple[str, ...]
    selected_dev_ticket_ids: tuple[str, ...]

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class _SplitContract:
    groups: tuple[str, ...]
    tickets: tuple[str, ...]
    ticket_to_group: Mapping[str, str]


@dataclass(frozen=True)
class _ManifestContract:
    dev: _SplitContract
    validation: _SplitContract
    locked_test: _SplitContract
    ticket_to_split: Mapping[str, str]
    ticket_to_group: Mapping[str, str]


@dataclass(frozen=True)
class _CanonicalCases:
    records_by_ticket: Mapping[str, Mapping[str, str]]
    source_case_count: int


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_payload_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _split_contract(payload: Mapping[str, Any], split_name: str) -> _SplitContract:
    try:
        groups = payload["splits"][split_name]["groups"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"missing split metadata: {split_name}") from exc
    if not isinstance(groups, list) or not groups:
        raise ValueError(f"split groups must be a non-empty list: {split_name}")

    group_ids: list[str] = []
    tickets: list[str] = []
    ticket_to_group: dict[str, str] = {}
    for group in groups:
        if not isinstance(group, Mapping):
            raise ValueError(f"invalid group metadata in split: {split_name}")
        group_id = group.get("group_id")
        group_tickets = group.get("tickets")
        if not isinstance(group_id, str) or not group_id:
            raise ValueError(f"missing group_id in split: {split_name}")
        if not isinstance(group_tickets, list) or not group_tickets:
            raise ValueError(f"missing ticket metadata in split: {split_name}/{group_id}")
        if group_id in group_ids:
            raise ValueError(f"duplicate group_id in split manifest: {split_name}")
        group_ids.append(group_id)
        for ticket_id in group_tickets:
            if not isinstance(ticket_id, str) or not ticket_id:
                raise ValueError(f"invalid ticket metadata in split: {split_name}/{group_id}")
            if ticket_id in ticket_to_group:
                raise ValueError(f"duplicate ticket_id in split manifest: {ticket_id}")
            tickets.append(ticket_id)
            ticket_to_group[ticket_id] = group_id

    return _SplitContract(
        groups=tuple(group_ids),
        tickets=tuple(tickets),
        ticket_to_group=ticket_to_group,
    )


def _manifest_contract(payload: Mapping[str, Any]) -> _ManifestContract:
    if payload.get("schema_version") != EXPECTED_SPLIT_SCHEMA_VERSION:
        raise ValueError("unexpected split manifest schema_version")
    if payload.get("status") != EXPECTED_SPLIT_STATUS:
        raise ValueError("split manifest is not frozen")
    if payload.get("unit_of_assignment") != EXPECTED_ASSIGNMENT_UNIT:
        raise ValueError("unexpected split assignment unit")

    rules = payload.get("rules")
    if not isinstance(rules, Mapping):
        raise ValueError("missing split rules")
    required_rule_values = {
        "no_storyline_split": True,
        "locked_test_available_for_architecture_selection": False,
        "locked_test_available_for_prompt_or_model_selection": False,
        "gold_is_evaluator_only": True,
    }
    if any(rules.get(key) is not value for key, value in required_rule_values.items()):
        raise ValueError("frozen leakage rules do not match ADAPT-A-001 prerequisites")

    locked_policy = payload.get("locked_test_policy")
    if not isinstance(locked_policy, Mapping):
        raise ValueError("missing locked-test policy")
    forbidden_before_final = locked_policy.get("forbidden_before_final")
    if not isinstance(forbidden_before_final, list):
        raise ValueError("missing locked-test forbidden operations")
    forbidden = {str(item).strip().lower() for item in forbidden_before_final}
    if not {"runtime selection", "agent policy debugging"}.issubset(forbidden):
        raise ValueError("locked-test policy does not forbid adaptive selection/debugging")

    dev = _split_contract(payload, "DEV")
    validation = _split_contract(payload, "VALIDATION")
    locked_test = _split_contract(payload, "LOCKED_TEST")

    ticket_to_split: dict[str, str] = {}
    ticket_to_group: dict[str, str] = {}
    for split_name, contract in (
        ("DEV", dev),
        ("VALIDATION", validation),
        ("LOCKED_TEST", locked_test),
    ):
        for ticket_id, group_id in contract.ticket_to_group.items():
            if ticket_id in ticket_to_split:
                raise ValueError(f"ticket appears in more than one split: {ticket_id}")
            ticket_to_split[ticket_id] = split_name
            ticket_to_group[ticket_id] = group_id

    if set(dev.groups) & (set(validation.groups) | set(locked_test.groups)):
        raise ValueError("DEV group overlaps a protected split")
    if set(validation.groups) & set(locked_test.groups):
        raise ValueError("VALIDATION group overlaps LOCKED_TEST")

    source_group_count = payload.get("source_group_count")
    ticket_count = payload.get("ticket_count")
    all_groups = set(dev.groups) | set(validation.groups) | set(locked_test.groups)
    if source_group_count != len(all_groups) or ticket_count != len(ticket_to_split):
        raise ValueError("frozen split aggregate counts are inconsistent")

    aggregate_counts = payload.get("aggregate_counts")
    if not isinstance(aggregate_counts, Mapping):
        raise ValueError("missing aggregate split counts")
    for split_name, contract in (
        ("DEV", dev),
        ("VALIDATION", validation),
        ("LOCKED_TEST", locked_test),
    ):
        split_counts = aggregate_counts.get(split_name)
        if not isinstance(split_counts, Mapping) or split_counts.get("groups") != len(contract.groups):
            raise ValueError(f"group aggregate mismatch: {split_name}")

    return _ManifestContract(
        dev=dev,
        validation=validation,
        locked_test=locked_test,
        ticket_to_split=ticket_to_split,
        ticket_to_group=ticket_to_group,
    )


def _canonical_cases(payload: Any) -> _CanonicalCases:
    if not isinstance(payload, list):
        raise TypeError("canonical agent-input/cases.json must be a top-level JSON list")
    if not payload:
        raise TypeError("canonical agent-input/cases.json must not be empty")

    records_by_ticket: dict[str, Mapping[str, str]] = {}
    case_ids: Counter[str] = Counter()
    ticket_ids: Counter[str] = Counter()

    for record in payload:
        if not isinstance(record, Mapping):
            raise TypeError("each canonical agent input case must be a JSON object")
        if set(record.keys()) != CANONICAL_CASE_FIELDS:
            raise TypeError("canonical agent input case fields do not match INPUT_FIELDS")

        normalized: dict[str, str] = {}
        for field in CANONICAL_CASE_FIELDS:
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                raise TypeError(f"canonical agent input field must be a non-empty string: {field}")
            normalized[field] = value

        case_ids[normalized["id"]] += 1
        ticket_ids[normalized["ticket_id"]] += 1
        records_by_ticket[normalized["ticket_id"]] = normalized

    if any(count != 1 for count in case_ids.values()) or any(count != 1 for count in ticket_ids.values()):
        raise RuntimeError("canonical case id or ticket id is duplicated")

    return _CanonicalCases(
        records_by_ticket=records_by_ticket,
        source_case_count=len(payload),
    )


def _not_ready(
    *,
    reason: ReasonCode,
    source_materialized: bool,
    source_sha256: str | None,
    manifest_sha256: str | None,
    source_case_count: int = 0,
    required_dev_groups: tuple[str, ...] = (),
    observed_group_ids: tuple[str, ...] = (),
    selected_dev_ticket_ids: tuple[str, ...] = (),
) -> AdaptiveExperimentPreflightResult:
    return AdaptiveExperimentPreflightResult(
        experiment_id=EXPERIMENT_ID,
        execution_status="NOT_READY",
        decision="INCONCLUSIVE",
        reason=reason,
        source_materialized=source_materialized,
        source_contract_version=CANONICAL_AGENT_INPUT_SCHEMA if source_materialized else None,
        source_sha256=source_sha256,
        manifest_sha256=manifest_sha256,
        dev_projection_sha256=None,
        source_case_count=source_case_count,
        selected_dev_case_count=0,
        required_dev_groups=required_dev_groups,
        observed_group_ids=tuple(sorted(observed_group_ids)),
        selected_dev_ticket_ids=tuple(sorted(selected_dev_ticket_ids)),
    )


def run_adaptive_experiment_preflight(
    *,
    agent_input_cases_path: str | Path,
    split_manifest_path: str | Path = DEFAULT_SPLIT_MANIFEST,
) -> AdaptiveExperimentPreflightResult:
    """Verify the canonical source and derive the frozen DEV-only structural projection.

    The canonical TRACTIAN package contains cases from all benchmark splits. This preflight may
    inspect their public structural identifiers only to prove source completeness and leakage
    boundaries. Decision-bearing selection is then derived exclusively from the frozen DEV ticket
    mapping; VALIDATION and LOCKED_TEST case contents are never returned or emitted.
    """

    source_path = Path(agent_input_cases_path)
    manifest_path = Path(split_manifest_path)

    if not manifest_path.is_file():
        return _not_ready(
            reason="MANIFEST_NOT_MATERIALIZED",
            source_materialized=source_path.is_file(),
            source_sha256=_sha256_file(source_path) if source_path.is_file() else None,
            manifest_sha256=None,
        )

    manifest_sha256 = _sha256_file(manifest_path)
    try:
        manifest_payload = _load_json(manifest_path)
        if not isinstance(manifest_payload, Mapping):
            raise ValueError("split manifest must be a JSON object")
        manifest = _manifest_contract(manifest_payload)
    except (OSError, json.JSONDecodeError, ValueError):
        return _not_ready(
            reason="INVALID_STRUCTURAL_METADATA",
            source_materialized=source_path.is_file(),
            source_sha256=_sha256_file(source_path) if source_path.is_file() else None,
            manifest_sha256=manifest_sha256,
        )

    if not source_path.is_file():
        return _not_ready(
            reason="CANONICAL_DEV_CASE_SOURCE_NOT_MATERIALIZED",
            source_materialized=False,
            source_sha256=None,
            manifest_sha256=manifest_sha256,
            required_dev_groups=manifest.dev.groups,
        )

    source_sha256 = _sha256_file(source_path)
    try:
        source_payload = _load_json(source_path)
        canonical = _canonical_cases(source_payload)
    except RuntimeError:
        return _not_ready(
            reason="DUPLICATE_CANONICAL_CASE",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            required_dev_groups=manifest.dev.groups,
        )
    except (OSError, json.JSONDecodeError, TypeError):
        return _not_ready(
            reason="CANONICAL_AGENT_INPUT_SCHEMA_MISMATCH",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            required_dev_groups=manifest.dev.groups,
        )

    expected_tickets = set(manifest.ticket_to_split)
    observed_tickets = set(canonical.records_by_ticket)
    missing_tickets = expected_tickets - observed_tickets
    if missing_tickets:
        return _not_ready(
            reason="CANONICAL_CASE_SOURCE_INCOMPLETE",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            source_case_count=canonical.source_case_count,
            required_dev_groups=manifest.dev.groups,
            selected_dev_ticket_ids=tuple(ticket for ticket in manifest.dev.tickets if ticket in observed_tickets),
        )
    if observed_tickets != expected_tickets:
        return _not_ready(
            reason="CANONICAL_SOURCE_MANIFEST_MISMATCH",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            source_case_count=canonical.source_case_count,
            required_dev_groups=manifest.dev.groups,
        )

    protected_groups = set(manifest.validation.groups) | set(manifest.locked_test.groups)
    for ticket_id, expected_group in manifest.ticket_to_group.items():
        actual_group = canonical.records_by_ticket[ticket_id]["asset_id"]
        if actual_group != expected_group:
            if manifest.ticket_to_split[ticket_id] == "DEV" and actual_group in protected_groups:
                return _not_ready(
                    reason="FORBIDDEN_SPLIT_CONTAMINATION",
                    source_materialized=True,
                    source_sha256=source_sha256,
                    manifest_sha256=manifest_sha256,
                    source_case_count=canonical.source_case_count,
                    required_dev_groups=manifest.dev.groups,
                )
            return _not_ready(
                reason="CANONICAL_SOURCE_MANIFEST_MISMATCH",
                source_materialized=True,
                source_sha256=source_sha256,
                manifest_sha256=manifest_sha256,
                source_case_count=canonical.source_case_count,
                required_dev_groups=manifest.dev.groups,
            )

    selected_records = [canonical.records_by_ticket[ticket_id] for ticket_id in manifest.dev.tickets]
    selected_groups = tuple(sorted({record["asset_id"] for record in selected_records}))
    selected_tickets = tuple(sorted(record["ticket_id"] for record in selected_records))
    if set(selected_groups) != set(manifest.dev.groups):
        return _not_ready(
            reason="CANONICAL_CASE_SOURCE_INCOMPLETE",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            source_case_count=canonical.source_case_count,
            required_dev_groups=manifest.dev.groups,
            observed_group_ids=selected_groups,
            selected_dev_ticket_ids=selected_tickets,
        )
    if set(selected_groups) & protected_groups:
        return _not_ready(
            reason="FORBIDDEN_SPLIT_CONTAMINATION",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            source_case_count=canonical.source_case_count,
            required_dev_groups=manifest.dev.groups,
            observed_group_ids=selected_groups,
            selected_dev_ticket_ids=selected_tickets,
        )

    dev_projection = [
        canonical.records_by_ticket[ticket_id]
        for ticket_id in sorted(manifest.dev.tickets)
    ]
    return AdaptiveExperimentPreflightResult(
        experiment_id=EXPERIMENT_ID,
        execution_status="READY",
        decision="INCONCLUSIVE",
        reason=None,
        source_materialized=True,
        source_contract_version=CANONICAL_AGENT_INPUT_SCHEMA,
        source_sha256=source_sha256,
        manifest_sha256=manifest_sha256,
        dev_projection_sha256=_stable_payload_sha256(dev_projection),
        source_case_count=canonical.source_case_count,
        selected_dev_case_count=len(selected_records),
        required_dev_groups=manifest.dev.groups,
        observed_group_ids=selected_groups,
        selected_dev_ticket_ids=selected_tickets,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed canonical DEV preflight for ADAPT-A-001")
    parser.add_argument("--agent-input-cases", required=True, type=Path)
    parser.add_argument("--split-manifest", type=Path, default=DEFAULT_SPLIT_MANIFEST)
    args = parser.parse_args(argv)

    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=args.agent_input_cases,
        split_manifest_path=args.split_manifest,
    )
    print(json.dumps(result.model_dump(), sort_keys=True, separators=(",", ":")))
    return 0 if result.execution_status == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
