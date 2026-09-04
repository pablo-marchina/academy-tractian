from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .binding import validate_model_arguments
from .models import ToolSpec

@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    field: str | None = None


def validate_arguments(tool: ToolSpec, arguments: dict[str, Any]) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    try:
        validate_model_arguments(arguments)
    except ValueError as exc:
        issues.append(ValidationIssue("MODEL_CONTROLLED_FIELD", str(exc)))
        return tuple(issues)
    allowed = {p.name for p in tool.parameters}
    for field in sorted(set(arguments) - allowed):
        issues.append(ValidationIssue("UNKNOWN_ARGUMENT", f"argument '{field}' is not declared by the ToolSpec", field))
    for parameter in tool.parameters:
        if parameter.required and parameter.name not in arguments:
            issues.append(ValidationIssue("MISSING_REQUIRED_ARGUMENT", f"missing required argument '{parameter.name}'", parameter.name))
            continue
        if parameter.name not in arguments:
            continue
        declared_enum = parameter.parameter_schema.get("enum")
        if isinstance(declared_enum, list) and arguments[parameter.name] not in declared_enum:
            issues.append(
                ValidationIssue(
                    "INVALID_ENUM",
                    f"argument '{parameter.name}' is outside the declared enum",
                    parameter.name,
                )
            )
    if tool.justification_required:
        body = arguments.get("body")
        if not isinstance(body, dict):
            issues.append(ValidationIssue("INVALID_BODY", "action body must be an object", "body"))
        else:
            justification = body.get("justification")
            if not isinstance(justification, str) or len(justification.strip()) < (tool.minimum_justification_length or 0):
                issues.append(ValidationIssue("INVALID_JUSTIFICATION", "action justification does not satisfy the frozen minimum", "body.justification"))
    if tool.name == "update_asset_config" and isinstance(arguments.get("body"), dict):
        changes = arguments["body"].get("changes", {})
        if isinstance(changes, dict) and "criticality" in changes and changes["criticality"] not in {"low", "medium", "high", "critical"}:
            issues.append(ValidationIssue("INVALID_ENUM", "criticality must be one of low/medium/high/critical", "body.changes.criticality"))
    return tuple(issues)


def assert_valid_arguments(tool: ToolSpec, arguments: dict[str, Any]) -> None:
    issues = validate_arguments(tool, arguments)
    if issues:
        raise ValueError("; ".join(f"{i.code}: {i.message}" for i in issues))
