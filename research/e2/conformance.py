from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import ToolSpec

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


@dataclass(frozen=True)
class ConformanceFinding:
    code: str
    operation_id: str
    detail: str


def _resolve_parameter(spec: dict[str, Any], parameter: dict[str, Any]) -> dict[str, Any]:
    if "$ref" not in parameter:
        return parameter
    name = parameter["$ref"].split("/")[-1]
    return spec.get("components", {}).get("parameters", {}).get(name, {})


def derive_contract_signatures(
    spec: dict[str, Any],
    *,
    parameter_transformations: dict[str, str],
    runner_bound_fields: set[str] | frozenset[str] = frozenset({"seed", "x-user-id"}),
) -> dict[str, dict[str, Any]]:
    signatures: dict[str, dict[str, Any]] = {}
    for path, path_item in (spec.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            if not operation_id:
                continue
            parameters: list[tuple[str, str, bool]] = []
            for raw_parameter in operation.get("parameters", []) or []:
                parameter = _resolve_parameter(spec, raw_parameter)
                raw_name = parameter.get("name")
                if not raw_name or raw_name in runner_bound_fields:
                    continue
                canonical_name = parameter_transformations.get(raw_name, raw_name)
                parameters.append((canonical_name, parameter.get("in"), bool(parameter.get("required", False))))
            if operation.get("requestBody"):
                parameters.append(("body", "body", True))
            signatures[operation_id] = {
                "method": method.upper(),
                "path": path,
                "parameters": tuple(parameters),
                "seed_supported": any(
                    _resolve_parameter(spec, p).get("name") == "seed"
                    for p in operation.get("parameters", []) or []
                ),
            }
    return signatures


def registry_signatures(registry: dict[str, ToolSpec]) -> dict[str, dict[str, Any]]:
    return {
        tool.operation_id: {
            "method": tool.method,
            "path": tool.path_template,
            "parameters": tuple((p.name, p.location, p.required) for p in tool.parameters),
        }
        for tool in registry.values()
    }


def compare_registry_to_contract(
    *,
    spec: dict[str, Any],
    registry: dict[str, ToolSpec],
    parameter_transformations: dict[str, str],
) -> tuple[ConformanceFinding, ...]:
    contract = derive_contract_signatures(
        spec,
        parameter_transformations=parameter_transformations,
    )
    actual = registry_signatures(registry)
    findings: list[ConformanceFinding] = []

    for operation_id in sorted(set(contract) | set(actual)):
        expected = contract.get(operation_id)
        observed = actual.get(operation_id)
        if expected is None:
            findings.append(ConformanceFinding("REGISTRY_EXTRA_OPERATION", operation_id, str(observed)))
            continue
        if observed is None:
            findings.append(ConformanceFinding("REGISTRY_MISSING_OPERATION", operation_id, str(expected)))
            continue
        for field in ("method", "path", "parameters"):
            if expected[field] != observed[field]:
                findings.append(
                    ConformanceFinding(
                        f"REGISTRY_{field.upper()}_MISMATCH",
                        operation_id,
                        f"contract={expected[field]!r}; registry={observed[field]!r}",
                    )
                )
    return tuple(findings)
