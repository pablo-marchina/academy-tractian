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

ExecutionStatus = Literal["READY", "NOT_READY"]
Decision = Literal["INCONCLUSIVE"]
ReasonCode = Literal[
    "CANONICAL_DEV_CASE_SOURCE_NOT_MATERIALIZED",
    "CANONICAL_DEV_CASE_SOURCE_INCOMPLETE",
    "FORBIDDEN_SPLIT_CONTAMINATION",
    "DUPLICATE_DEV_GROUP",
    "MANIFEST_NOT_MATERIALIZED",
    "INVALID_STRUCTURAL_METADATA",
]

_GROUP_FIELDS = ("asset_group", "group_id", "asset_story_group")
_CONTAINER_FIELDS = ("cases", "groups", "agent_input_cases", "items")


@dataclass(frozen=True)
class AdaptiveExperimentPreflightResult:
    """Safe structural readiness result for ADAPT-A-001.

    This object deliberately contains no prompt, evidence, model output, expected conclusion,
    oracle, rubric or gold payload. It is safe to persist as experiment provenance.
    """

    experiment_id: str
    execution_status: ExecutionStatus
    decision: Decision
    reason: ReasonCode | None
    source_materialized: bool
    source_sha256: str | None
    manifest_sha256: str | None
    required_dev_groups: tuple[str, ...]
    observed_group_ids: tuple[str, ...]

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _split_groups(payload: Mapping[str, Any], split_name: str) -> tuple[str, ...]:
    try:
        groups = payload["splits"][split_name]["groups"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"missing split metadata: {split_name}") from exc
    if not isinstance(groups, list):
        raise ValueError(f"split groups must be a list: {split_name}")

    result: list[str] = []
    for group in groups:
        if not isinstance(group, Mapping):
            raise ValueError(f"invalid group metadata in split: {split_name}")
        group_id = group.get("group_id")
        if not isinstance(group_id, str) or not group_id:
            raise ValueError(f"missing group_id in split: {split_name}")
        result.append(group_id)
    if len(result) != len(set(result)):
        raise ValueError(f"duplicate group_id in split manifest: {split_name}")
    return tuple(result)


def _candidate_records(payload: Any, known_groups: set[str]) -> Sequence[Any] | Mapping[str, Any]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, Mapping):
        raise ValueError("agent input cases must be a JSON object or list")

    for field in _CONTAINER_FIELDS:
        value = payload.get(field)
        if isinstance(value, list):
            return value

    known_mapping_keys = [key for key in payload if isinstance(key, str) and key in known_groups]
    if known_mapping_keys:
        return {key: payload[key] for key in known_mapping_keys}
    raise ValueError("agent input cases expose no supported structural group metadata")


def _group_ids_from_cases(payload: Any, known_groups: set[str]) -> tuple[str, ...]:
    records = _candidate_records(payload, known_groups)
    if isinstance(records, Mapping):
        return tuple(str(group_id) for group_id in records.keys())

    group_ids: list[str] = []
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("each agent input case must be a JSON object")
        group_id: str | None = None
        for field in _GROUP_FIELDS:
            value = record.get(field)
            if isinstance(value, str) and value:
                group_id = value
                break
        if group_id is None:
            raise ValueError("agent input case has no structural group identifier")
        group_ids.append(group_id)
    return tuple(group_ids)


def _not_ready(
    *,
    reason: ReasonCode,
    source_materialized: bool,
    source_sha256: str | None,
    manifest_sha256: str | None,
    required_dev_groups: tuple[str, ...] = (),
    observed_group_ids: tuple[str, ...] = (),
) -> AdaptiveExperimentPreflightResult:
    return AdaptiveExperimentPreflightResult(
        experiment_id=EXPERIMENT_ID,
        execution_status="NOT_READY",
        decision="INCONCLUSIVE",
        reason=reason,
        source_materialized=source_materialized,
        source_sha256=source_sha256,
        manifest_sha256=manifest_sha256,
        required_dev_groups=required_dev_groups,
        observed_group_ids=tuple(sorted(observed_group_ids)),
    )


def run_adaptive_experiment_preflight(
    *,
    agent_input_cases_path: str | Path,
    split_manifest_path: str | Path = DEFAULT_SPLIT_MANIFEST,
) -> AdaptiveExperimentPreflightResult:
    """Verify that ADAPT-A-001 can use the frozen canonical DEV boundary.

    The preflight is intentionally fail-closed. It inspects only structural grouping metadata;
    payload contents are never returned or logged by this module.
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
        dev_groups = _split_groups(manifest_payload, "DEV")
        validation_groups = _split_groups(manifest_payload, "VALIDATION")
        locked_groups = _split_groups(manifest_payload, "LOCKED_TEST")
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
            required_dev_groups=dev_groups,
        )

    source_sha256 = _sha256_file(source_path)
    known_groups = set(dev_groups) | set(validation_groups) | set(locked_groups)
    try:
        source_payload = _load_json(source_path)
        observed_group_ids = _group_ids_from_cases(source_payload, known_groups)
    except (OSError, json.JSONDecodeError, ValueError):
        return _not_ready(
            reason="INVALID_STRUCTURAL_METADATA",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            required_dev_groups=dev_groups,
        )

    forbidden_groups = set(validation_groups) | set(locked_groups)
    if forbidden_groups.intersection(observed_group_ids):
        return _not_ready(
            reason="FORBIDDEN_SPLIT_CONTAMINATION",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            required_dev_groups=dev_groups,
            observed_group_ids=observed_group_ids,
        )

    counts = Counter(observed_group_ids)
    if any(counts[group_id] > 1 for group_id in dev_groups):
        return _not_ready(
            reason="DUPLICATE_DEV_GROUP",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            required_dev_groups=dev_groups,
            observed_group_ids=observed_group_ids,
        )

    if set(observed_group_ids) != set(dev_groups) or len(observed_group_ids) != len(dev_groups):
        return _not_ready(
            reason="CANONICAL_DEV_CASE_SOURCE_INCOMPLETE",
            source_materialized=True,
            source_sha256=source_sha256,
            manifest_sha256=manifest_sha256,
            required_dev_groups=dev_groups,
            observed_group_ids=observed_group_ids,
        )

    return AdaptiveExperimentPreflightResult(
        experiment_id=EXPERIMENT_ID,
        execution_status="READY",
        decision="INCONCLUSIVE",
        reason=None,
        source_materialized=True,
        source_sha256=source_sha256,
        manifest_sha256=manifest_sha256,
        required_dev_groups=dev_groups,
        observed_group_ids=tuple(sorted(observed_group_ids)),
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
