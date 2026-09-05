from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.models import ExecutionBinding, ToolKind
from research.e2.tool_registry import TOOLS, get_tool
from research.e2.transport import RequestTransport, build_b0_request
from research.e2.validation import validate_arguments

from .hosted_integration_evidence_recorder import (
    EvidenceRecordingTractianTransport,
    HostedIntegrationEvidenceRecorder,
)
from .tractian_integration_evidence import IntegrationEvidenceLedger


ProbeOutcome = Literal[
    "success",
    "http_error_observed",
    "transport_failure",
    "blocked_by_safety",
    "not_configured",
]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class TransportProbeFixture(_StrictModel):
    operation: str = Field(min_length=1, max_length=96)
    valid_arguments: dict[str, Any]
    error_arguments: dict[str, Any] | None = None
    action_execution_approved: bool = False
    action_error_probe_approved: bool = False
    action_approval_ref: str | None = Field(default=None, min_length=8, max_length=256)

    @model_validator(mode="after")
    def validate_action_approval_shape(self) -> "TransportProbeFixture":
        try:
            tool = get_tool(self.operation)
        except KeyError as exc:
            raise ValueError("unknown_transport_probe_operation") from exc

        if tool.kind is ToolKind.READ:
            if (
                self.action_execution_approved
                or self.action_error_probe_approved
                or self.action_approval_ref is not None
            ):
                raise ValueError("read_fixture_cannot_carry_action_approval")
            return self

        if self.action_execution_approved and self.action_approval_ref is None:
            raise ValueError("approved_action_requires_approval_ref")
        if not self.action_execution_approved and self.action_approval_ref is not None:
            raise ValueError("action_approval_ref_requires_execution_approval")
        if self.action_error_probe_approved and not self.action_execution_approved:
            raise ValueError("action_error_probe_requires_execution_approval")
        if self.action_error_probe_approved and self.error_arguments is None:
            raise ValueError("action_error_probe_approval_requires_error_arguments")
        if self.error_arguments is not None and not self.action_error_probe_approved:
            raise ValueError("action_error_probe_requires_explicit_approval")
        return self


class TractianTransportCampaignManifest(_StrictModel):
    schema_version: Literal["tractian-transport-campaign-manifest-v1"] = (
        "tractian-transport-campaign-manifest-v1"
    )
    identity_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    seed: str | None = Field(default=None, min_length=1, max_length=128)
    fixtures: tuple[TransportProbeFixture, ...] = Field(min_length=1, max_length=18)

    @model_validator(mode="after")
    def validate_fixtures_against_contract(self) -> "TractianTransportCampaignManifest":
        operations = [fixture.operation for fixture in self.fixtures]
        if len(operations) != len(set(operations)):
            raise ValueError("duplicate_transport_probe_operation")

        known = {tool.name for tool in TOOLS}
        if any(operation not in known for operation in operations):
            raise ValueError("unknown_transport_probe_operation")

        binding = ExecutionBinding(
            identity_id=self.identity_id,
            user_id=self.user_id,
            seed=self.seed,
        )
        for fixture in self.fixtures:
            tool = get_tool(fixture.operation)
            valid_issues = validate_arguments(tool, fixture.valid_arguments)
            if valid_issues:
                raise ValueError(f"invalid_valid_probe_arguments:{fixture.operation}")
            try:
                build_b0_request(tool, fixture.valid_arguments, binding)
            except Exception as exc:
                raise ValueError(f"invalid_valid_probe_arguments:{fixture.operation}") from exc

            if fixture.error_arguments is not None:
                # Error probes must still be product-valid requests. They are expected to exercise a
                # real upstream HTTP error (for example a non-existent resource), not bypass B1 with
                # malformed client-side arguments.
                error_issues = validate_arguments(tool, fixture.error_arguments)
                if error_issues:
                    raise ValueError(f"invalid_error_probe_arguments:{fixture.operation}")
                try:
                    build_b0_request(tool, fixture.error_arguments, binding)
                except Exception as exc:
                    raise ValueError(f"invalid_error_probe_arguments:{fixture.operation}") from exc
        return self


class OperationTransportProbeResult(_StrictModel):
    operation: str
    kind: Literal["read", "action"]
    valid_probe: ProbeOutcome
    error_probe: ProbeOutcome
    action_live_execution_enabled: bool
    action_error_probe_enabled: bool


class TractianTransportCampaignRun(_StrictModel):
    schema_version: Literal["tractian-transport-campaign-run-v1"] = (
        "tractian-transport-campaign-run-v1"
    )
    configured_operations: int
    executed_operations: int
    safety_blocked_actions: int
    successful_valid_probes: int
    observed_http_error_probes: int
    results: tuple[OperationTransportProbeResult, ...]


def _outcome_from_response(status_code: int) -> ProbeOutcome:
    if 200 <= status_code < 400:
        return "success"
    if 400 <= status_code <= 599:
        return "http_error_observed"
    return "transport_failure"


def _request_probe(
    *,
    transport: EvidenceRecordingTractianTransport,
    tool,
    arguments: dict[str, Any],
    binding: ExecutionBinding,
) -> ProbeOutcome:
    request = build_b0_request(tool, arguments, binding)
    try:
        response = transport.request(request)
    except Exception:
        return "transport_failure"
    return _outcome_from_response(response.status_code)


def run_tractian_transport_campaign(
    *,
    manifest: TractianTransportCampaignManifest,
    transport: RequestTransport,
    allow_actions: bool = False,
    recorder: HostedIntegrationEvidenceRecorder | None = None,
) -> tuple[TractianTransportCampaignRun, IntegrationEvidenceLedger]:
    """Execute bounded B1-valid live transport probes without manufacturing semantic proof.

    Every manifest request must pass both the frozen product argument validator and B0 request
    binding before execution. Consequential valid probes require two independent gates: per-fixture
    action approval and the invocation-level ``allow_actions=True`` switch. A consequential error
    probe is an additional mutation attempt and therefore requires a third, explicit
    ``action_error_probe_approved`` gate. Without the valid-action gates, no action request reaches
    the delegate transport and the attempted campaign step is recorded only as a real safety block.
    Raw arguments and response bodies never enter the campaign result.
    """

    active_recorder = recorder or HostedIntegrationEvidenceRecorder()
    recording_transport = EvidenceRecordingTractianTransport(transport, active_recorder)
    binding = ExecutionBinding(
        identity_id=manifest.identity_id,
        user_id=manifest.user_id,
        seed=manifest.seed,
    )

    results: list[OperationTransportProbeResult] = []
    for fixture in manifest.fixtures:
        tool = get_tool(fixture.operation)
        action_enabled = (
            tool.kind is ToolKind.ACTION
            and fixture.action_execution_approved
            and fixture.action_approval_ref is not None
            and allow_actions
        )
        action_error_enabled = (
            action_enabled
            and fixture.action_error_probe_approved
            and fixture.error_arguments is not None
        )
        if tool.kind is ToolKind.ACTION and not action_enabled:
            blocked_request = build_b0_request(tool, fixture.valid_arguments, binding)
            active_recorder.record(blocked_request, outcome="blocked_by_safety")
            results.append(
                OperationTransportProbeResult(
                    operation=tool.name,
                    kind=tool.kind.value,
                    valid_probe="blocked_by_safety",
                    error_probe="not_configured",
                    action_live_execution_enabled=False,
                    action_error_probe_enabled=False,
                )
            )
            continue

        valid_outcome = _request_probe(
            transport=recording_transport,
            tool=tool,
            arguments=fixture.valid_arguments,
            binding=binding,
        )
        error_outcome: ProbeOutcome = "not_configured"
        if fixture.error_arguments is not None and (
            tool.kind is ToolKind.READ or action_error_enabled
        ):
            error_outcome = _request_probe(
                transport=recording_transport,
                tool=tool,
                arguments=fixture.error_arguments,
                binding=binding,
            )
        results.append(
            OperationTransportProbeResult(
                operation=tool.name,
                kind=tool.kind.value,
                valid_probe=valid_outcome,
                error_probe=error_outcome,
                action_live_execution_enabled=action_enabled,
                action_error_probe_enabled=action_error_enabled,
            )
        )

    return (
        TractianTransportCampaignRun(
            configured_operations=len(results),
            executed_operations=sum(result.valid_probe != "blocked_by_safety" for result in results),
            safety_blocked_actions=sum(result.valid_probe == "blocked_by_safety" for result in results),
            successful_valid_probes=sum(result.valid_probe == "success" for result in results),
            observed_http_error_probes=sum(
                result.error_probe == "http_error_observed" for result in results
            ),
            results=tuple(results),
        ),
        active_recorder.ledger(),
    )
