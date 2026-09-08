from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Any, Mapping

from .binding import validate_model_arguments
from .models import ToolSpec


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    field: str | None = None


def _issue(code: str, message: str, field: str) -> ValidationIssue:
    return ValidationIssue(code=code, message=message, field=field)


def _json_type_matches(expected: str, value: Any) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, (list, tuple))
    if expected == "object":
        return isinstance(value, Mapping)
    return True


def _validate_schema(value: Any, schema: Mapping[str, Any], field: str) -> list[ValidationIssue]:
    """Validate the executable JSON-Schema subset carried by ToolParameter.

    ToolSpec schemas are the canonical provider/runtime argument contract. Local ``$ref`` values
    remain intentionally unresolved here because the frozen ToolSpec does not carry the referenced
    component graph. Existing action-specific rules therefore remain defense in depth until the
    source registry exposes a self-contained resolved schema.
    """

    issues: list[ValidationIssue] = []

    expected = schema.get("type")
    if isinstance(expected, str):
        expected_types = (expected,)
    elif isinstance(expected, list) and all(isinstance(item, str) for item in expected):
        expected_types = tuple(expected)
    else:
        expected_types = ()
    if expected_types and not any(_json_type_matches(item, value) for item in expected_types):
        return [
            _issue(
                "INVALID_TYPE",
                f"'{field}' must match JSON type {expected_types}",
                field,
            )
        ]

    if "const" in schema and value != schema["const"]:
        issues.append(_issue("INVALID_CONST", f"'{field}' does not match the required constant", field))
    enum = schema.get("enum")
    if isinstance(enum, list) and value not in enum:
        issues.append(_issue("INVALID_ENUM", f"'{field}' is not one of the allowed values", field))

    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        exclusive_minimum = schema.get("exclusiveMinimum")
        exclusive_maximum = schema.get("exclusiveMaximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            issues.append(_issue("VALUE_TOO_SMALL", f"'{field}' is below minimum {minimum}", field))
        if isinstance(maximum, (int, float)) and value > maximum:
            issues.append(_issue("VALUE_TOO_LARGE", f"'{field}' is above maximum {maximum}", field))
        if isinstance(exclusive_minimum, (int, float)) and value <= exclusive_minimum:
            issues.append(_issue("VALUE_TOO_SMALL", f"'{field}' must be greater than {exclusive_minimum}", field))
        if isinstance(exclusive_maximum, (int, float)) and value >= exclusive_maximum:
            issues.append(_issue("VALUE_TOO_LARGE", f"'{field}' must be less than {exclusive_maximum}", field))

    if isinstance(value, str):
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        pattern = schema.get("pattern")
        if isinstance(min_length, int) and len(value) < min_length:
            issues.append(_issue("STRING_TOO_SHORT", f"'{field}' is shorter than {min_length}", field))
        if isinstance(max_length, int) and len(value) > max_length:
            issues.append(_issue("STRING_TOO_LONG", f"'{field}' is longer than {max_length}", field))
        if isinstance(pattern, str):
            try:
                matched = re.search(pattern, value) is not None
            except re.error:
                matched = True
            if not matched:
                issues.append(_issue("PATTERN_MISMATCH", f"'{field}' does not match the declared pattern", field))

    if isinstance(value, (list, tuple)):
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if isinstance(min_items, int) and len(value) < min_items:
            issues.append(_issue("ARRAY_TOO_SHORT", f"'{field}' has fewer than {min_items} items", field))
        if isinstance(max_items, int) and len(value) > max_items:
            issues.append(_issue("ARRAY_TOO_LONG", f"'{field}' has more than {max_items} items", field))
        if schema.get("uniqueItems") is True:
            normalized = [repr(item) for item in value]
            if len(normalized) != len(set(normalized)):
                issues.append(_issue("DUPLICATE_ARRAY_ITEM", f"'{field}' requires unique items", field))
        item_schema = schema.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(value):
                issues.extend(_validate_schema(item, item_schema, f"{field}[{index}]"))

    if isinstance(value, Mapping):
        required = schema.get("required")
        if isinstance(required, list):
            for name in required:
                if isinstance(name, str) and name not in value:
                    issues.append(_issue("MISSING_REQUIRED_FIELD", f"missing required field '{name}'", f"{field}.{name}"))
        properties = schema.get("properties")
        if isinstance(properties, Mapping):
            for name, property_schema in properties.items():
                if isinstance(name, str) and name in value and isinstance(property_schema, Mapping):
                    issues.extend(_validate_schema(value[name], property_schema, f"{field}.{name}"))
            if schema.get("additionalProperties") is False:
                for name in sorted(set(value) - set(properties)):
                    issues.append(_issue("UNKNOWN_OBJECT_FIELD", f"field '{name}' is not allowed", f"{field}.{name}"))

    return issues


def validate_arguments(tool: ToolSpec, arguments: dict[str, Any]) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    try:
        validate_model_arguments(arguments)
    except ValueError as exc:
        issues.append(ValidationIssue("MODEL_CONTROLLED_FIELD", str(exc)))
        return tuple(issues)

    allowed = {parameter.name for parameter in tool.parameters}
    for field in sorted(set(arguments) - allowed):
        issues.append(
            ValidationIssue(
                "UNKNOWN_ARGUMENT",
                f"argument '{field}' is not declared by the ToolSpec",
                field,
            )
        )

    for parameter in tool.parameters:
        if parameter.required and parameter.name not in arguments:
            issues.append(
                ValidationIssue(
                    "MISSING_REQUIRED_ARGUMENT",
                    f"missing required argument '{parameter.name}'",
                    parameter.name,
                )
            )
            continue
        if parameter.name in arguments and parameter.parameter_schema:
            issues.extend(
                _validate_schema(
                    arguments[parameter.name],
                    parameter.parameter_schema,
                    parameter.name,
                )
            )

    if tool.justification_required:
        body = arguments.get("body")
        if not isinstance(body, dict):
            issues.append(ValidationIssue("INVALID_BODY", "action body must be an object", "body"))
        else:
            justification = body.get("justification")
            if not isinstance(justification, str) or len(justification.strip()) < (
                tool.minimum_justification_length or 0
            ):
                issues.append(
                    ValidationIssue(
                        "INVALID_JUSTIFICATION",
                        "action justification does not satisfy the frozen minimum",
                        "body.justification",
                    )
                )

    if tool.name == "update_asset_config" and isinstance(arguments.get("body"), dict):
        changes = arguments["body"].get("changes", {})
        if (
            isinstance(changes, dict)
            and "criticality" in changes
            and changes["criticality"] not in {"low", "medium", "high", "critical"}
        ):
            issues.append(
                ValidationIssue(
                    "INVALID_ENUM",
                    "criticality must be one of low/medium/high/critical",
                    "body.changes.criticality",
                )
            )
    return tuple(issues)


def assert_valid_arguments(tool: ToolSpec, arguments: dict[str, Any]) -> None:
    issues = validate_arguments(tool, arguments)
    if issues:
        raise ValueError("; ".join(f"{issue.code}: {issue.message}" for issue in issues))
