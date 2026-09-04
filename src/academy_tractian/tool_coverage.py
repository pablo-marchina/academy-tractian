from __future__ import annotations

from typing import Any

from research.e2.models import ToolKind
from research.e2.tool_registry import NORMALIZED_OPERATION_COUNT, TOOLS

from .tractian_integration_evidence import (
    IntegrationEvidenceLedger,
    empty_hosted_integration_evidence,
    load_frozen_integration_evidence,
)


TOOL_COVERAGE_SCHEMA_VERSION = "tractian-tool-coverage-v2"


def _coverage_status(
    *,
    frozen: IntegrationEvidenceLedger,
    hosted: IntegrationEvidenceLedger,
    hosted_exercised: int,
    integrated: int,
) -> str:
    if not frozen.valid or not hosted.valid:
        return "EVIDENCE_INVALID_FAIL_CLOSED"
    if hosted_exercised == NORMALIZED_OPERATION_COUNT:
        return "HOSTED_LIVE_FULLY_EXERCISED"
    if hosted_exercised > 0:
        return "PARTIAL_HOSTED_LIVE_EVIDENCE"
    if integrated > 0:
        return "PARTIAL_INTEGRATED_ROUTE_EVIDENCE"
    return "NO_INTEGRATION_EVIDENCE"


def build_tractian_tool_coverage(
    *,
    frozen_evidence: IntegrationEvidenceLedger | None = None,
    hosted_evidence: IntegrationEvidenceLedger | None = None,
) -> dict[str, Any]:
    """Build the canonical 18-operation coverage matrix from trusted evidence.

    Contract registration and implementation-route presence come from the frozen
    canonical registry. Integration execution is a stronger claim and is derived
    only from validated evidence ledgers; route existence, mocks and synthetic
    fixtures cannot silently promote hosted-live coverage.
    """

    frozen = frozen_evidence or load_frozen_integration_evidence()
    hosted = hosted_evidence or empty_hosted_integration_evidence()

    frozen_observed = frozen.unique_route_observed_operations("frozen")
    hosted_observed = hosted.unique_route_observed_operations("hosted_live")
    hosted_success = hosted.unique_success_operations("hosted_live")
    hosted_http_error = hosted.unique_outcome_operations("hosted_live", "http_error_observed")
    hosted_transport_failure = hosted.unique_outcome_operations("hosted_live", "transport_failure")
    hosted_unavailable = hosted.unique_outcome_operations("hosted_live", "unavailable")
    hosted_blocked = hosted.unique_outcome_operations("hosted_live", "blocked_by_safety")
    integrated_observed = frozen_observed | hosted_observed

    operations: list[dict[str, Any]] = []
    for tool in TOOLS:
        hosted_records = hosted.records_for(tool.name, "hosted_live")
        hosted_outcomes = sorted({item.outcome for item in hosted_records})
        integrated_evidenced = tool.name in integrated_observed
        operations.append(
            {
                "tool_name": tool.name,
                "operation_id": tool.operation_id,
                "method": tool.method,
                "path_template": tool.path_template,
                "kind": tool.kind.value,
                "impact": None if tool.impact is None else tool.impact.value,
                "required_permissions": sorted(item.value for item in tool.required_permissions),
                "parameter_count": len(tool.parameters),
                "required_parameter_count": sum(item.required for item in tool.parameters),
                "identity_required": tool.identity_required,
                "justification_required": tool.justification_required,
                "seed_supported": tool.seed_supported,
                "contract_registered": True,
                "implementation_route_present": True,
                # Backward-compatible aggregate claim: historical frozen evidence
                # and hosted-live route observations may satisfy this field.
                "integrated_route_execution_evidenced": integrated_evidenced,
                "integration_evidence_scope": (
                    "hosted_live_route_evidence"
                    if tool.name in hosted_observed
                    else (
                        "frozen_route_test_evidence"
                        if tool.name in frozen_observed
                        else "not_yet_explicitly_evidenced"
                    )
                ),
                "frozen_route_execution_evidenced": tool.name in frozen_observed,
                "hosted_live_exercised": tool.name in hosted_observed,
                "hosted_live_success": tool.name in hosted_success,
                "hosted_live_blocked_by_safety": tool.name in hosted_blocked,
                "hosted_live_outcomes": hosted_outcomes,
            }
        )

    registered = len(operations)
    integrated = len(integrated_observed)
    hosted_exercised = len(hosted_observed)
    actions = sum(item["kind"] == ToolKind.ACTION.value for item in operations)
    return {
        "schema_version": TOOL_COVERAGE_SCHEMA_VERSION,
        "status": _coverage_status(
            frozen=frozen,
            hosted=hosted,
            hosted_exercised=hosted_exercised,
            integrated=integrated,
        ),
        "claim_boundary": (
            "All 18 normalized operations are contract-registered and present in the executable "
            "implementation. Hosted-live coverage increases only when a validated hosted_live "
            "evidence record observes the canonical route; implementation presence, mocks, "
            "synthetic fixtures and safety-blocked actions do not count as hosted-live execution."
        ),
        "evidence": {
            "frozen": {
                "state": frozen.state,
                "source": frozen.source_label,
                "validation_errors": list(frozen.validation_errors),
            },
            "hosted_live": {
                "state": hosted.state,
                "source": hosted.source_label,
                "validation_errors": list(hosted.validation_errors),
            },
        },
        "summary": {
            "normalized_operations": NORMALIZED_OPERATION_COUNT,
            "contract_registered": registered,
            "implementation_routes_present": registered,
            "integrated_route_execution_evidenced": integrated,
            "integrated_route_execution_not_yet_evidenced": registered - integrated,
            "frozen_route_execution_evidenced": len(frozen_observed),
            "hosted_live_exercised": hosted_exercised,
            "hosted_live_success": len(hosted_success),
            "hosted_live_http_error_observed": len(hosted_http_error),
            "hosted_live_transport_failure": len(hosted_transport_failure),
            "hosted_live_unavailable": len(hosted_unavailable),
            "hosted_live_blocked_by_safety": len(hosted_blocked),
            "hosted_live_not_exercised": registered - hosted_exercised,
            "actions": actions,
            "reads": registered - actions,
        },
        "operations": operations,
    }
