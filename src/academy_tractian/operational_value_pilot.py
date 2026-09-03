from __future__ import annotations

from hashlib import sha256
import json
import random
from typing import Any, Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator


PilotCondition = Literal["MANUAL", "ASSISTED"]
PilotTrialStatus = Literal["VALID", "INTERRUPTED", "TECHNICAL_FAILURE", "WITHDRAWN"]
BenchmarkSplit = Literal["DEV", "VALIDATION", "LOCKED_TEST"]

_FORBIDDEN_PUBLIC_MARKERS = (
    "authorization:",
    "bearer ",
    "api_key",
    "api-key",
    "identity_id",
    "chain_of_thought",
    "raw_prompt",
    "raw_response",
    "gold_answer",
    "private_truth",
    "expected_path",
    "expected-path",
    "oracle",
)


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


def _assert_public_safe_text(value: str, *, field_name: str) -> str:
    if not value.strip():
        raise ValueError(f"{field_name} must be non-empty")
    lowered = value.lower()
    hit = next((marker for marker in _FORBIDDEN_PUBLIC_MARKERS if marker in lowered), None)
    if hit is not None:
        raise ValueError(f"{field_name} contains forbidden evaluator/runtime material marker: {hit}")
    return value


def _ticket_sha256(ticket_request: str) -> str:
    return _canonical_sha256({"ticket_request": ticket_request})


def _assistance_sha256(
    *,
    terminal_decision: str,
    terminal_message: str,
    safe_evidence_context: Sequence[str],
) -> str:
    return _canonical_sha256(
        {
            "agent_terminal_decision": terminal_decision,
            "agent_terminal_message": terminal_message,
            "safe_evidence_context": list(safe_evidence_context),
        }
    )


class OperationalPilotSource(_FrozenModel):
    """Sanitized evaluator-time source for one matched manual/assisted DEV case."""

    schema_version: Literal["operational-pilot-source-v1"] = "operational-pilot-source-v1"
    scenario_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    ticket_request: str = Field(min_length=1)
    agent_terminal_decision: str = Field(min_length=1)
    agent_terminal_message: str = Field(min_length=1)
    safe_evidence_context: tuple[str, ...] = ()
    agent_runtime_seconds: float | None = Field(default=None, ge=0.0)

    @model_validator(mode="after")
    def validate_public_material(self) -> "OperationalPilotSource":
        _assert_public_safe_text(self.scenario_id, field_name="scenario_id")
        _assert_public_safe_text(self.case_id, field_name="case_id")
        _assert_public_safe_text(self.ticket_request, field_name="ticket_request")
        _assert_public_safe_text(
            self.agent_terminal_decision,
            field_name="agent_terminal_decision",
        )
        _assert_public_safe_text(
            self.agent_terminal_message,
            field_name="agent_terminal_message",
        )
        for index, item in enumerate(self.safe_evidence_context):
            _assert_public_safe_text(item, field_name=f"safe_evidence_context[{index}]")
        return self

    @property
    def ticket_sha256(self) -> str:
        return _ticket_sha256(self.ticket_request)

    @property
    def assistance_sha256(self) -> str:
        return _assistance_sha256(
            terminal_decision=self.agent_terminal_decision,
            terminal_message=self.agent_terminal_message,
            safe_evidence_context=self.safe_evidence_context,
        )


class OperationalPilotAssistance(_FrozenModel):
    terminal_decision: str = Field(min_length=1)
    terminal_message: str = Field(min_length=1)
    safe_evidence_context: tuple[str, ...]

    @model_validator(mode="after")
    def validate_public_material(self) -> "OperationalPilotAssistance":
        _assert_public_safe_text(self.terminal_decision, field_name="terminal_decision")
        _assert_public_safe_text(self.terminal_message, field_name="terminal_message")
        for index, item in enumerate(self.safe_evidence_context):
            _assert_public_safe_text(item, field_name=f"safe_evidence_context[{index}]")
        return self

    @property
    def assistance_sha256(self) -> str:
        return _assistance_sha256(
            terminal_decision=self.terminal_decision,
            terminal_message=self.terminal_message,
            safe_evidence_context=self.safe_evidence_context,
        )


class OperationalPilotTask(_FrozenModel):
    """Single task safe to render to one operator; carries no split/group/pair/gold metadata."""

    task_id: str = Field(pattern=r"^ovt_[0-9a-f]{24}$")
    condition: PilotCondition
    ticket_request: str = Field(min_length=1)
    assistance: OperationalPilotAssistance | None = None

    @model_validator(mode="after")
    def validate_condition_projection(self) -> "OperationalPilotTask":
        _assert_public_safe_text(self.ticket_request, field_name="ticket_request")
        if self.condition == "MANUAL" and self.assistance is not None:
            raise ValueError("MANUAL task must not contain agent assistance")
        if self.condition == "ASSISTED" and self.assistance is None:
            raise ValueError("ASSISTED task requires the safe agent projection")
        return self


class OperationalPilotPacket(_FrozenModel):
    """Host-side task collection. The collection itself is not handed wholesale to an operator."""

    schema_version: Literal["operational-pilot-packet-v1"] = "operational-pilot-packet-v1"
    packet_id: str = Field(pattern=r"^ovpkt_[0-9a-f]{24}$")
    protocol_id: str = Field(min_length=1)
    measurement_design: Literal["INDEPENDENT_MATCHED"] = "INDEPENDENT_MATCHED"
    deterministic_shuffle_seed: int
    source_count: int = Field(ge=1)
    task_count: int = Field(ge=2)
    tasks: tuple[OperationalPilotTask, ...]

    @model_validator(mode="after")
    def validate_packet(self) -> "OperationalPilotPacket":
        if self.task_count != len(self.tasks):
            raise ValueError("task_count does not match tasks")
        if self.task_count != self.source_count * 2:
            raise ValueError("INDEPENDENT_MATCHED packet requires exactly two tasks per source")
        if len({task.task_id for task in self.tasks}) != len(self.tasks):
            raise ValueError("packet contains duplicate task ids")
        if sum(task.condition == "MANUAL" for task in self.tasks) != self.source_count:
            raise ValueError("packet manual-task count does not match source_count")
        if sum(task.condition == "ASSISTED" for task in self.tasks) != self.source_count:
            raise ValueError("packet assisted-task count does not match source_count")
        return self


class OperationalPilotManifestEntry(_FrozenModel):
    task_id: str = Field(pattern=r"^ovt_[0-9a-f]{24}$")
    pair_id: str = Field(pattern=r"^ovpair_[0-9a-f]{24}$")
    scenario_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    source_split: Literal["DEV"] = "DEV"
    condition: PilotCondition
    ticket_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    assistance_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    agent_runtime_seconds: float | None = Field(default=None, ge=0.0)


class OperationalPilotManifest(_FrozenModel):
    """Evaluator-only mapping kept separate from the host/operator task collection."""

    schema_version: Literal["operational-pilot-manifest-v1"] = "operational-pilot-manifest-v1"
    packet_id: str = Field(pattern=r"^ovpkt_[0-9a-f]{24}$")
    protocol_id: str = Field(min_length=1)
    measurement_design: Literal["INDEPENDENT_MATCHED"] = "INDEPENDENT_MATCHED"
    frozen_split_schema_version: str = Field(min_length=1)
    frozen_split_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    group_ids: tuple[str, ...]
    pair_ids: tuple[str, ...]
    entries: tuple[OperationalPilotManifestEntry, ...]

    @model_validator(mode="after")
    def validate_manifest(self) -> "OperationalPilotManifest":
        if not self.entries:
            raise ValueError("manifest requires entries")
        if len({entry.task_id for entry in self.entries}) != len(self.entries):
            raise ValueError("manifest contains duplicate task ids")
        if tuple(sorted(set(entry.group_id for entry in self.entries))) != self.group_ids:
            raise ValueError("group_ids do not match entries")
        if tuple(sorted(set(entry.pair_id for entry in self.entries))) != self.pair_ids:
            raise ValueError("pair_ids do not match entries")

        by_pair: dict[str, list[OperationalPilotManifestEntry]] = {}
        for entry in self.entries:
            by_pair.setdefault(entry.pair_id, []).append(entry)
        for pair_id, pair_entries in by_pair.items():
            if len(pair_entries) != 2:
                raise ValueError(f"pair {pair_id} must contain exactly two tasks")
            if {entry.condition for entry in pair_entries} != {"MANUAL", "ASSISTED"}:
                raise ValueError(f"pair {pair_id} must contain MANUAL and ASSISTED tasks")
            for field_name in (
                "scenario_id",
                "case_id",
                "group_id",
                "ticket_sha256",
                "assistance_sha256",
                "agent_runtime_seconds",
            ):
                if len({getattr(entry, field_name) for entry in pair_entries}) != 1:
                    raise ValueError(f"pair {pair_id} mixes {field_name}")
        return self


class OperationalPilotCompletion(_FrozenModel):
    """Host-timed operator result. Correctness remains evaluator-side and is not scored here."""

    schema_version: Literal["operational-pilot-completion-v1"] = "operational-pilot-completion-v1"
    packet_id: str = Field(pattern=r"^ovpkt_[0-9a-f]{24}$")
    task_id: str = Field(pattern=r"^ovt_[0-9a-f]{24}$")
    operator_ref_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    measurement_source: Literal["HOST_MONOTONIC_TIMER"] = "HOST_MONOTONIC_TIMER"
    status: PilotTrialStatus
    elapsed_seconds: float | None = Field(default=None, gt=0.0)
    terminal_decision: str | None = None
    conclusion_summary: str | None = None
    invalid_reason: str | None = None

    @model_validator(mode="after")
    def validate_completion(self) -> "OperationalPilotCompletion":
        if self.status == "VALID":
            if self.elapsed_seconds is None:
                raise ValueError("VALID completion requires elapsed_seconds")
            if self.terminal_decision is None or self.conclusion_summary is None:
                raise ValueError("VALID completion requires terminal decision and conclusion summary")
            _assert_public_safe_text(self.terminal_decision, field_name="terminal_decision")
            _assert_public_safe_text(self.conclusion_summary, field_name="conclusion_summary")
            if self.invalid_reason is not None:
                raise ValueError("VALID completion must not carry invalid_reason")
        else:
            if self.invalid_reason is None:
                raise ValueError("invalid completion requires invalid_reason")
            _assert_public_safe_text(self.invalid_reason, field_name="invalid_reason")
        return self

    @property
    def public_output_sha256(self) -> str | None:
        if self.status != "VALID":
            return None
        return _canonical_sha256(
            {
                "terminal_decision": self.terminal_decision,
                "conclusion_summary": self.conclusion_summary,
            }
        )


class OperationalEffortPair(_FrozenModel):
    """Resolved evaluator-side pair. Operator identities and raw conclusion text are omitted."""

    schema_version: Literal["operational-effort-pair-v1"] = "operational-effort-pair-v1"
    pair_id: str = Field(pattern=r"^ovpair_[0-9a-f]{24}$")
    protocol_id: str = Field(min_length=1)
    measurement_design: Literal["INDEPENDENT_MATCHED"] = "INDEPENDENT_MATCHED"
    scenario_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    split: Literal["DEV"] = "DEV"
    manual_task_id: str = Field(pattern=r"^ovt_[0-9a-f]{24}$")
    assisted_task_id: str = Field(pattern=r"^ovt_[0-9a-f]{24}$")
    ticket_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    assistance_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    manual_seconds: float = Field(gt=0.0)
    assisted_seconds: float = Field(gt=0.0)
    agent_runtime_seconds: float | None = Field(default=None, ge=0.0)
    manual_output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    assisted_output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @property
    def engineer_seconds_saved(self) -> float:
        return self.manual_seconds - self.assisted_seconds


class OperationalPilotResolutionReport(_FrozenModel):
    schema_version: Literal["operational-pilot-resolution-v1"] = "operational-pilot-resolution-v1"
    packet_id: str = Field(pattern=r"^ovpkt_[0-9a-f]{24}$")
    protocol_id: str = Field(min_length=1)
    pair_count: int = Field(ge=1)
    resolved_pair_count: int = Field(ge=0)
    unresolved_pair_ids: tuple[str, ...]
    invalid_task_ids: tuple[str, ...]
    missing_task_ids: tuple[str, ...]
    duplicate_task_ids: tuple[str, ...]
    resolution_ready: bool
    effort_pairs: tuple[OperationalEffortPair, ...]


class _SplitAssignment(_FrozenModel):
    split: BenchmarkSplit
    group_id: str


def _split_index(
    split_payload: Mapping[str, Any],
) -> tuple[dict[str, _SplitAssignment], str, str]:
    schema_version = str(split_payload.get("schema_version") or "")
    if schema_version != "benchmark-split-v1":
        raise ValueError("unsupported split manifest schema")
    if split_payload.get("status") != "FROZEN":
        raise ValueError("split manifest must be FROZEN")
    splits = split_payload.get("splits")
    if not isinstance(splits, Mapping):
        raise ValueError("split manifest missing splits object")

    index: dict[str, _SplitAssignment] = {}
    for split_name in ("DEV", "VALIDATION", "LOCKED_TEST"):
        section = splits.get(split_name)
        if not isinstance(section, Mapping):
            raise ValueError(f"split manifest missing {split_name}")
        groups = section.get("groups")
        if not isinstance(groups, list):
            raise ValueError(f"split manifest {split_name} groups must be a list")
        for group in groups:
            if not isinstance(group, Mapping):
                raise ValueError("split group must be an object")
            group_id = str(group.get("group_id") or "")
            scenarios = group.get("scenarios")
            if not group_id or not isinstance(scenarios, list) or not scenarios:
                raise ValueError("split group missing group_id/scenarios")
            for scenario in scenarios:
                scenario_id = str(scenario)
                if scenario_id in index:
                    raise ValueError(f"scenario assigned more than once: {scenario_id}")
                index[scenario_id] = _SplitAssignment(
                    split=split_name,  # type: ignore[arg-type]
                    group_id=group_id,
                )
    return index, schema_version, _canonical_sha256(split_payload)


def _pair_id_from_material(
    *,
    protocol_id: str,
    scenario_id: str,
    case_id: str,
    ticket_sha256: str,
    assistance_sha256: str,
) -> str:
    return "ovpair_" + _canonical_sha256(
        {
            "protocol_id": protocol_id,
            "scenario_id": scenario_id,
            "case_id": case_id,
            "ticket_sha256": ticket_sha256,
            "assistance_sha256": assistance_sha256,
        }
    )[:24]


def _pair_id(source: OperationalPilotSource, *, protocol_id: str) -> str:
    return _pair_id_from_material(
        protocol_id=protocol_id,
        scenario_id=source.scenario_id,
        case_id=source.case_id,
        ticket_sha256=source.ticket_sha256,
        assistance_sha256=source.assistance_sha256,
    )


def _task_id_from_pair(*, pair_id: str, condition: PilotCondition) -> str:
    return "ovt_" + _canonical_sha256(
        {
            "pair_id": pair_id,
            "condition": condition,
        }
    )[:24]


def _task_id(
    source: OperationalPilotSource,
    *,
    protocol_id: str,
    condition: PilotCondition,
) -> str:
    return _task_id_from_pair(
        pair_id=_pair_id(source, protocol_id=protocol_id),
        condition=condition,
    )


def _packet_id_from_manifest_material(
    *,
    protocol_id: str,
    split_sha256: str,
    source_identities: Sequence[tuple[str, str, str, str]],
    shuffle_seed: int,
) -> str:
    return "ovpkt_" + _canonical_sha256(
        {
            "protocol_id": protocol_id,
            "measurement_design": "INDEPENDENT_MATCHED",
            "split_sha256": split_sha256,
            "source_identities": sorted(source_identities),
            "shuffle_seed": shuffle_seed,
        }
    )[:24]


def build_operational_pilot_packet(
    *,
    sources: Sequence[OperationalPilotSource],
    frozen_split_payload: Mapping[str, Any],
    protocol_id: str,
    deterministic_shuffle_seed: int = 20260903,
    minimum_distinct_groups: int = 2,
) -> tuple[OperationalPilotPacket, OperationalPilotManifest]:
    if not sources:
        raise ValueError("operational pilot requires at least one source")
    _assert_public_safe_text(protocol_id, field_name="protocol_id")
    if minimum_distinct_groups < 1:
        raise ValueError("minimum_distinct_groups must be >= 1")

    split_index, split_schema, split_sha = _split_index(frozen_split_payload)
    assignments: list[tuple[OperationalPilotSource, _SplitAssignment]] = []
    seen_case_identity: set[tuple[str, str]] = set()
    for source in sources:
        assignment = split_index.get(source.scenario_id)
        if assignment is None:
            raise ValueError(f"scenario absent from frozen split manifest: {source.scenario_id}")
        if assignment.split != "DEV":
            raise ValueError(
                f"operational-value pilot accepts DEV only; {source.scenario_id} belongs to {assignment.split}"
            )
        case_identity = (source.scenario_id, source.case_id)
        if case_identity in seen_case_identity:
            raise ValueError(
                f"duplicate operational pilot case identity: {source.scenario_id}/{source.case_id}"
            )
        seen_case_identity.add(case_identity)
        assignments.append((source, assignment))

    assignments.sort(
        key=lambda row: (
            row[0].scenario_id,
            row[0].case_id,
            row[0].ticket_sha256,
            row[0].assistance_sha256,
        )
    )
    group_ids = tuple(sorted({assignment.group_id for _, assignment in assignments}))
    if len(group_ids) < minimum_distinct_groups:
        raise ValueError(
            f"operational pilot requires at least {minimum_distinct_groups} distinct groups; got {len(group_ids)}"
        )

    tasks: list[OperationalPilotTask] = []
    entries: list[OperationalPilotManifestEntry] = []
    for source, assignment in assignments:
        pair_id = _pair_id(source, protocol_id=protocol_id)
        for condition in ("MANUAL", "ASSISTED"):
            task_id = _task_id_from_pair(pair_id=pair_id, condition=condition)
            assistance = None
            if condition == "ASSISTED":
                assistance = OperationalPilotAssistance(
                    terminal_decision=source.agent_terminal_decision,
                    terminal_message=source.agent_terminal_message,
                    safe_evidence_context=source.safe_evidence_context,
                )
            tasks.append(
                OperationalPilotTask(
                    task_id=task_id,
                    condition=condition,
                    ticket_request=source.ticket_request,
                    assistance=assistance,
                )
            )
            entries.append(
                OperationalPilotManifestEntry(
                    task_id=task_id,
                    pair_id=pair_id,
                    scenario_id=source.scenario_id,
                    case_id=source.case_id,
                    group_id=assignment.group_id,
                    condition=condition,
                    ticket_sha256=source.ticket_sha256,
                    assistance_sha256=source.assistance_sha256,
                    agent_runtime_seconds=source.agent_runtime_seconds,
                )
            )

    rng = random.Random(deterministic_shuffle_seed)
    rng.shuffle(tasks)
    canonical_entries = tuple(sorted(entries, key=lambda entry: entry.task_id))
    pair_ids = tuple(sorted({entry.pair_id for entry in canonical_entries}))
    source_identities = [
        (
            source.scenario_id,
            source.case_id,
            source.ticket_sha256,
            source.assistance_sha256,
        )
        for source, _ in assignments
    ]
    packet_id = _packet_id_from_manifest_material(
        protocol_id=protocol_id,
        split_sha256=split_sha,
        source_identities=source_identities,
        shuffle_seed=deterministic_shuffle_seed,
    )

    packet = OperationalPilotPacket(
        packet_id=packet_id,
        protocol_id=protocol_id,
        deterministic_shuffle_seed=deterministic_shuffle_seed,
        source_count=len(sources),
        task_count=len(tasks),
        tasks=tuple(tasks),
    )
    manifest = OperationalPilotManifest(
        packet_id=packet_id,
        protocol_id=protocol_id,
        frozen_split_schema_version=split_schema,
        frozen_split_sha256=split_sha,
        group_ids=group_ids,
        pair_ids=pair_ids,
        entries=canonical_entries,
    )
    return packet, manifest


def _verify_packet_manifest_integrity(
    packet: OperationalPilotPacket,
    manifest: OperationalPilotManifest,
) -> None:
    if packet.packet_id != manifest.packet_id:
        raise ValueError("packet/manifest packet_id mismatch")
    if packet.protocol_id != manifest.protocol_id:
        raise ValueError("packet/manifest protocol_id mismatch")
    if packet.measurement_design != manifest.measurement_design:
        raise ValueError("packet/manifest measurement design mismatch")
    if packet.source_count != len(manifest.pair_ids):
        raise ValueError("packet source_count does not match manifest pairs")
    if packet.task_count != len(manifest.entries):
        raise ValueError("packet task_count does not match manifest entries")

    packet_tasks = {task.task_id: task for task in packet.tasks}
    manifest_entries = {entry.task_id: entry for entry in manifest.entries}
    if set(packet_tasks) != set(manifest_entries):
        raise ValueError("packet/manifest task sets differ")

    source_identities: set[tuple[str, str, str, str]] = set()
    for entry in manifest.entries:
        source_identities.add(
            (
                entry.scenario_id,
                entry.case_id,
                entry.ticket_sha256,
                entry.assistance_sha256,
            )
        )
        expected_pair_id = _pair_id_from_material(
            protocol_id=manifest.protocol_id,
            scenario_id=entry.scenario_id,
            case_id=entry.case_id,
            ticket_sha256=entry.ticket_sha256,
            assistance_sha256=entry.assistance_sha256,
        )
        if entry.pair_id != expected_pair_id:
            raise ValueError(f"manifest pair identity mismatch for {entry.task_id}")
        expected_task_id = _task_id_from_pair(
            pair_id=entry.pair_id,
            condition=entry.condition,
        )
        if entry.task_id != expected_task_id:
            raise ValueError(f"manifest task identity mismatch for {entry.task_id}")

        task = packet_tasks[entry.task_id]
        if task.condition != entry.condition:
            raise ValueError(f"packet/manifest condition mismatch for {entry.task_id}")
        if _ticket_sha256(task.ticket_request) != entry.ticket_sha256:
            raise ValueError(f"packet ticket content hash mismatch for {entry.task_id}")
        if entry.condition == "ASSISTED":
            if task.assistance is None:
                raise ValueError(f"assisted packet task missing assistance: {entry.task_id}")
            if task.assistance.assistance_sha256 != entry.assistance_sha256:
                raise ValueError(f"packet assistance content hash mismatch for {entry.task_id}")

    expected_packet_id = _packet_id_from_manifest_material(
        protocol_id=manifest.protocol_id,
        split_sha256=manifest.frozen_split_sha256,
        source_identities=tuple(source_identities),
        shuffle_seed=packet.deterministic_shuffle_seed,
    )
    if packet.packet_id != expected_packet_id:
        raise ValueError("packet identity does not match manifest content")


def resolve_operational_pilot(
    *,
    packet: OperationalPilotPacket,
    manifest: OperationalPilotManifest,
    completions: Sequence[OperationalPilotCompletion],
) -> OperationalPilotResolutionReport:
    # Revalidate serialized shapes in case callers created Pydantic objects using non-validating
    # model_copy/construct paths before invoking the resolver.
    packet = OperationalPilotPacket.model_validate(packet.model_dump(mode="json"))
    manifest = OperationalPilotManifest.model_validate(manifest.model_dump(mode="json"))
    validated_completions = [
        OperationalPilotCompletion.model_validate(row.model_dump(mode="json"))
        for row in completions
    ]
    _verify_packet_manifest_integrity(packet, manifest)

    packet_tasks = {task.task_id: task for task in packet.tasks}
    manifest_entries = {entry.task_id: entry for entry in manifest.entries}
    completion_rows: dict[str, list[OperationalPilotCompletion]] = {}
    for completion in validated_completions:
        if completion.packet_id != packet.packet_id:
            raise ValueError("completion packet_id mismatch")
        if completion.task_id not in packet_tasks:
            raise ValueError(f"completion references unknown task: {completion.task_id}")
        completion_rows.setdefault(completion.task_id, []).append(completion)

    duplicate_task_ids = tuple(
        sorted(task_id for task_id, rows in completion_rows.items() if len(rows) > 1)
    )
    missing_task_ids = tuple(sorted(set(packet_tasks) - set(completion_rows)))
    invalid_task_ids = tuple(
        sorted(
            task_id
            for task_id, rows in completion_rows.items()
            if len(rows) == 1 and rows[0].status != "VALID"
        )
    )

    entries_by_pair: dict[str, dict[PilotCondition, OperationalPilotManifestEntry]] = {}
    for entry in manifest.entries:
        entries_by_pair.setdefault(entry.pair_id, {})[entry.condition] = entry

    effort_pairs: list[OperationalEffortPair] = []
    unresolved: list[str] = []
    for pair_id in manifest.pair_ids:
        pair_entries = entries_by_pair[pair_id]
        manual_entry = pair_entries["MANUAL"]
        assisted_entry = pair_entries["ASSISTED"]
        manual_rows = completion_rows.get(manual_entry.task_id, [])
        assisted_rows = completion_rows.get(assisted_entry.task_id, [])

        if len(manual_rows) != 1 or len(assisted_rows) != 1:
            unresolved.append(pair_id)
            continue
        manual = manual_rows[0]
        assisted = assisted_rows[0]
        if manual.status != "VALID" or assisted.status != "VALID":
            unresolved.append(pair_id)
            continue
        if manual.operator_ref_sha256 == assisted.operator_ref_sha256:
            raise ValueError(
                f"INDEPENDENT_MATCHED pair {pair_id} reuses the same operator across conditions"
            )
        if manual.elapsed_seconds is None or assisted.elapsed_seconds is None:
            raise AssertionError("validated completion unexpectedly missing elapsed time")
        if manual.public_output_sha256 is None or assisted.public_output_sha256 is None:
            raise AssertionError("validated completion unexpectedly missing output hash")

        effort_pairs.append(
            OperationalEffortPair(
                pair_id=pair_id,
                protocol_id=manifest.protocol_id,
                scenario_id=manual_entry.scenario_id,
                case_id=manual_entry.case_id,
                group_id=manual_entry.group_id,
                manual_task_id=manual_entry.task_id,
                assisted_task_id=assisted_entry.task_id,
                ticket_sha256=manual_entry.ticket_sha256,
                assistance_sha256=assisted_entry.assistance_sha256,
                manual_seconds=manual.elapsed_seconds,
                assisted_seconds=assisted.elapsed_seconds,
                agent_runtime_seconds=assisted_entry.agent_runtime_seconds,
                manual_output_sha256=manual.public_output_sha256,
                assisted_output_sha256=assisted.public_output_sha256,
            )
        )

    effort_pairs.sort(key=lambda pair: pair.pair_id)
    unresolved_ids = tuple(sorted(unresolved))
    return OperationalPilotResolutionReport(
        packet_id=packet.packet_id,
        protocol_id=packet.protocol_id,
        pair_count=len(manifest.pair_ids),
        resolved_pair_count=len(effort_pairs),
        unresolved_pair_ids=unresolved_ids,
        invalid_task_ids=invalid_task_ids,
        missing_task_ids=missing_task_ids,
        duplicate_task_ids=duplicate_task_ids,
        resolution_ready=(
            len(effort_pairs) == len(manifest.pair_ids)
            and not unresolved_ids
            and not invalid_task_ids
            and not missing_task_ids
            and not duplicate_task_ids
        ),
        effort_pairs=tuple(effort_pairs),
    )
