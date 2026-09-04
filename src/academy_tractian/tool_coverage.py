from __future__ import annotations

from typing import Any

from research.e2.models import ToolKind
from research.e2.tool_registry import NORMALIZED_OPERATION_COUNT, TOOLS


TOOL_COVERAGE_SCHEMA_VERSION = "tractian-tool-coverage-v1"

# Evidence from the frozen 2026-08-27 conformance artifact. Do not expand this set merely because
# a route exists in the implementation: explicit integrated route execution evidence is a stronger
# claim than contract/implementation conformance.
_EXPLICIT_INTEGRATED_ROUTE_EVIDENCE = frozenset({"get_asset"})


def build_tractian_tool_coverage() -> dict[str, Any]:
    operations: list[dict[str, Any]] = []
    for tool in TOOLS:
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
                "integrated_route_execution_evidenced": tool.name
                in _EXPLICIT_INTEGRATED_ROUTE_EVIDENCE,
                "integration_evidence_scope": (
                    "frozen_route_test_evidence"
                    if tool.name in _EXPLICIT_INTEGRATED_ROUTE_EVIDENCE
                    else "not_yet_explicitly_evidenced"
                ),
            }
        )

    registered = len(operations)
    integrated = sum(item["integrated_route_execution_evidenced"] for item in operations)
    actions = sum(item["kind"] == ToolKind.ACTION.value for item in operations)
    return {
        "schema_version": TOOL_COVERAGE_SCHEMA_VERSION,
        "status": "PARTIAL_INTEGRATED_ROUTE_EVIDENCE",
        "claim_boundary": (
            "All 18 normalized operations are contract-registered and present in the executable "
            "implementation; only explicitly recorded route execution is counted as integrated "
            "route evidence."
        ),
        "summary": {
            "normalized_operations": NORMALIZED_OPERATION_COUNT,
            "contract_registered": registered,
            "implementation_routes_present": registered,
            "integrated_route_execution_evidenced": integrated,
            "integrated_route_execution_not_yet_evidenced": registered - integrated,
            "actions": actions,
            "reads": registered - actions,
        },
        "operations": operations,
    }
