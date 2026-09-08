from __future__ import annotations

from research.e2.models import ToolKind, ToolParameter, ToolSpec
from research.e2.tool_registry import get_tool
from research.e2.validation import validate_arguments


def _tool(schema: dict) -> ToolSpec:
    return ToolSpec(
        name="schema_fixture",
        operation_id="schema_fixture",
        method="GET",
        path_template="/fixture",
        kind=ToolKind.READ,
        parameters=(
            ToolParameter(
                name="value",
                location="query",
                required=True,
                parameter_schema=schema,
            ),
        ),
    )


def _codes(tool: ToolSpec, value) -> set[str]:
    return {issue.code for issue in validate_arguments(tool, {"value": value})}


def test_real_registry_enum_is_enforced_deterministically() -> None:
    issues = validate_arguments(get_tool("list_analyses"), {"status": "banana"})
    assert any(issue.code == "INVALID_ENUM" and issue.field == "status" for issue in issues)


def test_real_registry_integer_bounds_and_bool_rejection_are_enforced() -> None:
    tool = get_tool("search_knowledge")
    assert "VALUE_TOO_SMALL" in {issue.code for issue in validate_arguments(tool, {"query": "bearing", "top_k": 0})}
    assert "VALUE_TOO_LARGE" in {issue.code for issue in validate_arguments(tool, {"query": "bearing", "top_k": 26})}
    assert "INVALID_TYPE" in {issue.code for issue in validate_arguments(tool, {"query": "bearing", "top_k": True})}
    assert validate_arguments(tool, {"query": "bearing", "top_k": 5}) == ()


def test_string_constraints_are_enforced() -> None:
    tool = _tool({"type": "string", "minLength": 3, "maxLength": 5, "pattern": "^[A-Z]+$"})
    assert "STRING_TOO_SHORT" in _codes(tool, "A")
    assert "STRING_TOO_LONG" in _codes(tool, "ABCDEF")
    assert "PATTERN_MISMATCH" in _codes(tool, "abc")
    assert _codes(tool, "ABCD") == set()


def test_array_and_nested_object_constraints_are_enforced() -> None:
    tool = _tool(
        {
            "type": "array",
            "minItems": 1,
            "maxItems": 2,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "required": ["score"],
                "additionalProperties": False,
                "properties": {"score": {"type": "number", "minimum": 0, "maximum": 1}},
            },
        }
    )
    issues = validate_arguments(tool, {"value": [{"score": 2, "extra": True}]})
    by_field = {(issue.code, issue.field) for issue in issues}
    assert ("VALUE_TOO_LARGE", "value[0].score") in by_field
    assert ("UNKNOWN_OBJECT_FIELD", "value[0].extra") in by_field
    assert "DUPLICATE_ARRAY_ITEM" in _codes(tool, [{"score": 0.5}, {"score": 0.5}])
    assert _codes(tool, [{"score": 0.5}]) == set()


def test_unknown_ref_is_not_misrepresented_as_resolved_validation() -> None:
    tool = _tool({"$ref": "#/components/schemas/Unavailable"})
    assert validate_arguments(tool, {"value": {"opaque": "still validated by special rules if any"}}) == ()
