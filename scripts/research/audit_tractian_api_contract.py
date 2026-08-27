#!/usr/bin/env python3
from __future__ import annotations

"""Duplicate-aware conformance audit for the delivered TRACTIAN API contract.

Consumes exact external agent-facing source files plus the repository Tool Registry.
It never reads evaluator/gold material and serializes only source identity,
operation signatures, duplicate-key evidence, and conformance mismatches.
"""

import argparse
import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_OPENAPI_SHA256 = "8b3fdc5da50a8fa2923928a2f5aebcfe5034c622dba222df84f56abcd0b4aabf"
EXPECTED_IMPLEMENTATION_SHA256 = "a9bdfb8a5fc85e8f169438984f787ad5fd0db95cdd2dc41a15e05ca363a3ca78"
EXPECTED_TESTS_SHA256 = "b50fbabe2f497290a01984ba0663bb0b787184f0bc1b367e90871d0912326443"
EXPECTED_OPERATION_COUNT = 18
EXPECTED_UNIQUE_PATH_COUNT = 17
EXPECTED_DUPLICATE_PATH = "/assets/{assetId}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def normalize_path_parameters(path: str) -> str:
    return re.sub(r"\{[^{}]+\}", "{}", path)


def parse_authored_openapi(text: str) -> dict[str, Any]:
    """Parse only paths/method/operationId structure while preserving duplicate keys."""
    in_paths = False
    current_path: str | None = None
    current_method: str | None = None
    path_occurrences: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []

    path_re = re.compile(r"^  (/[^:]+):\s*$")
    method_re = re.compile(r"^    (get|post|patch|put|delete):\s*$")
    operation_re = re.compile(r"^      operationId:\s*([A-Za-z0-9_.-]+)\s*$")

    for line_no, line in enumerate(text.splitlines(), start=1):
        if line == "paths:":
            in_paths = True
            current_path = None
            current_method = None
            continue
        if not in_paths:
            continue
        if line and not line.startswith(" "):
            break

        path_match = path_re.match(line)
        if path_match:
            current_path = path_match.group(1)
            current_method = None
            path_occurrences.append({"path": current_path, "line": line_no})
            continue

        method_match = method_re.match(line)
        if method_match and current_path is not None:
            current_method = method_match.group(1).upper()
            continue

        operation_match = operation_re.match(line)
        if operation_match and current_path is not None and current_method is not None:
            operations.append(
                {
                    "method": current_method,
                    "path": current_path,
                    "operation_id": operation_match.group(1),
                    "operation_id_line": line_no,
                }
            )

    counts = Counter(item["path"] for item in path_occurrences)
    duplicate_paths = sorted(path for path, count in counts.items() if count > 1)
    if not operations:
        raise AssertionError("no authored OpenAPI operations discovered")
    return {
        "path_occurrences": path_occurrences,
        "unique_paths": sorted(counts),
        "duplicate_paths": duplicate_paths,
        "operations": operations,
    }


def parse_fastapi_routes(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r'@app\.(get|post|patch|put|delete)\(\s*"([^"]+)"',
        flags=re.IGNORECASE,
    )
    routes = [
        {
            "method": match.group(1).upper(),
            "path": match.group(2),
            "normalized_path": normalize_path_parameters(match.group(2)),
        }
        for match in pattern.finditer(text)
    ]
    if not routes:
        raise AssertionError("no FastAPI routes discovered")
    return routes


def literal_str(node: ast.AST, label: str) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    raise AssertionError(f"registry {label} is not a literal string")


def parse_registry(path: Path) -> list[dict[str, Any]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    tools_assignment: ast.AST | None = None
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets: list[ast.expr] = []
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
                value = node.value
            else:
                targets = [node.target]
                value = node.value
            if any(isinstance(t, ast.Name) and t.id == "TOOLS" for t in targets):
                tools_assignment = value
                break

    if not isinstance(tools_assignment, (ast.Tuple, ast.List)):
        raise AssertionError("TOOLS tuple/list not found in registry")

    tools: list[dict[str, Any]] = []
    for item in tools_assignment.elts:
        if not isinstance(item, ast.Call) or not isinstance(item.func, ast.Name):
            raise AssertionError("unexpected TOOLS entry")
        kind = item.func.id
        if kind == "read":
            if len(item.args) < 3:
                raise AssertionError("read registry entry missing positional arguments")
            name = literal_str(item.args[0], "tool name")
            operation_id = literal_str(item.args[1], "operation_id")
            method = "GET"
            path_template = literal_str(item.args[2], "path")
        elif kind == "action":
            if len(item.args) < 4:
                raise AssertionError("action registry entry missing positional arguments")
            name = literal_str(item.args[0], "tool name")
            operation_id = literal_str(item.args[1], "operation_id")
            method = literal_str(item.args[2], "method").upper()
            path_template = literal_str(item.args[3], "path")
        else:
            raise AssertionError(f"unexpected registry constructor: {kind}")

        tools.append(
            {
                "name": name,
                "operation_id": operation_id,
                "method": method,
                "path": path_template,
                "normalized_path": normalize_path_parameters(path_template),
            }
        )
    return tools


def signature_set(
    rows: list[dict[str, Any]], *, include_operation_id: bool
) -> set[tuple[str, ...]]:
    result: set[tuple[str, ...]] = set()
    for row in rows:
        base = (str(row["method"]).upper(), str(row["path"]))
        if include_operation_id:
            result.add((*base, str(row["operation_id"])))
        else:
            result.add(base)
    return result


def normalized_route_set(rows: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {
        (
            str(row["method"]).upper(),
            normalize_path_parameters(str(row["path"])),
        )
        for row in rows
    }


def sorted_signatures(values: set[tuple[str, ...]]) -> list[str]:
    return [" | ".join(parts) for parts in sorted(values)]


def run(args: argparse.Namespace) -> int:
    if sha256(args.openapi) != EXPECTED_OPENAPI_SHA256:
        raise AssertionError("OpenAPI source SHA-256 mismatch")
    if sha256(args.implementation) != EXPECTED_IMPLEMENTATION_SHA256:
        raise AssertionError("implementation source SHA-256 mismatch")
    if sha256(args.tests) != EXPECTED_TESTS_SHA256:
        raise AssertionError("tests source SHA-256 mismatch")
    registry_blob = git_blob_sha(args.registry)

    openapi = parse_authored_openapi(args.openapi.read_text(encoding="utf-8"))
    implementation = parse_fastapi_routes(
        args.implementation.read_text(encoding="utf-8")
    )
    registry = parse_registry(args.registry)
    tests_text = args.tests.read_text(encoding="utf-8")

    openapi_ops = openapi["operations"]
    if len(openapi_ops) != EXPECTED_OPERATION_COUNT:
        raise AssertionError(
            f"authored OpenAPI operation count mismatch: {len(openapi_ops)}"
        )
    if len(openapi["unique_paths"]) != EXPECTED_UNIQUE_PATH_COUNT:
        raise AssertionError("authored OpenAPI unique path count mismatch")
    if openapi["duplicate_paths"] != [EXPECTED_DUPLICATE_PATH]:
        raise AssertionError(
            f"unexpected duplicate OpenAPI path keys: {openapi['duplicate_paths']}"
        )

    duplicate_ops = [
        row for row in openapi_ops if row["path"] == EXPECTED_DUPLICATE_PATH
    ]
    expected_duplicate_ops = {
        ("GET", EXPECTED_DUPLICATE_PATH, "getAsset"),
        ("PATCH", EXPECTED_DUPLICATE_PATH, "updateAssetConfig"),
    }
    actual_duplicate_ops = {
        (row["method"], row["path"], row["operation_id"]) for row in duplicate_ops
    }
    if actual_duplicate_ops != expected_duplicate_ops:
        raise AssertionError("duplicate-path operation semantics mismatch")

    openapi_exact = signature_set(openapi_ops, include_operation_id=True)
    registry_exact = signature_set(registry, include_operation_id=True)

    openapi_normalized_routes = normalized_route_set(openapi_ops)
    implementation_normalized_routes = normalized_route_set(implementation)
    registry_normalized_routes = normalized_route_set(registry)

    mismatches = {
        "openapi_missing_from_registry": sorted_signatures(openapi_exact - registry_exact),
        "registry_missing_from_openapi": sorted_signatures(registry_exact - openapi_exact),
        "openapi_routes_missing_from_implementation": sorted_signatures(
            openapi_normalized_routes - implementation_normalized_routes
        ),
        "implementation_routes_missing_from_openapi": sorted_signatures(
            implementation_normalized_routes - openapi_normalized_routes
        ),
        "registry_routes_missing_from_implementation": sorted_signatures(
            registry_normalized_routes - implementation_normalized_routes
        ),
        "implementation_routes_missing_from_registry": sorted_signatures(
            implementation_normalized_routes - registry_normalized_routes
        ),
    }

    get_asset_tested = (
        "def test_get_asset_with_points" in tests_text
        and 'client.get("/assets/asset_M101")' in tests_text
        and "def test_get_asset_404" in tests_text
    )
    if not get_asset_tested:
        raise AssertionError("delivered tests do not confirm GET /assets/{assetId}")

    if len(implementation) != EXPECTED_OPERATION_COUNT:
        raise AssertionError("FastAPI route count mismatch")
    if len(registry) != EXPECTED_OPERATION_COUNT:
        raise AssertionError("Tool Registry count mismatch")
    if any(mismatches.values()):
        raise AssertionError(f"contract conformance mismatch: {mismatches}")

    duplicate_occurrences = [
        item for item in openapi["path_occurrences"]
        if item["path"] == EXPECTED_DUPLICATE_PATH
    ]

    result = {
        "schema_version": "tractian-api-contract-conformance-v1",
        "status": "PASS_NORMALIZED_18_OPERATIONS_17_UNIQUE_PATHS",
        "task_issue": 11,
        "source_identity": {
            "openapi_sha256": EXPECTED_OPENAPI_SHA256,
            "implementation_sha256": EXPECTED_IMPLEMENTATION_SHA256,
            "tests_sha256": EXPECTED_TESTS_SHA256,
            "tool_registry_git_blob": registry_blob,
        },
        "authored_openapi": {
            "operation_count": len(openapi_ops),
            "path_key_occurrence_count": len(openapi["path_occurrences"]),
            "unique_path_count": len(openapi["unique_paths"]),
            "duplicate_path_keys": openapi["duplicate_paths"],
            "duplicate_path_occurrences": duplicate_occurrences,
            "duplicate_path_operations": sorted(
                [
                    {
                        "method": row["method"],
                        "path": row["path"],
                        "operation_id": row["operation_id"],
                        "operation_id_line": row["operation_id_line"],
                    }
                    for row in duplicate_ops
                ],
                key=lambda row: (row["method"], row["operation_id"]),
            ),
            "lossy_mapping_parser_risk": True,
        },
        "executable_implementation": {
            "route_count": len(implementation),
            "unique_normalized_method_path_count": len(implementation_normalized_routes),
            "get_asset_route_present": (
                "GET", normalize_path_parameters(EXPECTED_DUPLICATE_PATH)
            ) in implementation_normalized_routes,
        },
        "tool_registry": {
            "tool_count": len(registry),
            "unique_path_count": len({row["path"] for row in registry}),
            "unique_method_path_count": len(
                {(row["method"], row["path"]) for row in registry}
            ),
            "get_asset_present": any(
                row["operation_id"] == "getAsset"
                and row["method"] == "GET"
                and row["path"] == EXPECTED_DUPLICATE_PATH
                for row in registry
            ),
            "update_asset_config_present": any(
                row["operation_id"] == "updateAssetConfig"
                and row["method"] == "PATCH"
                and row["path"] == EXPECTED_DUPLICATE_PATH
                for row in registry
            ),
        },
        "delivered_tests": {
            "get_asset_route_tested": get_asset_tested,
        },
        "conformance": {
            "authored_openapi_equals_tool_registry": openapi_exact == registry_exact,
            "authored_openapi_routes_equal_implementation_routes": (
                openapi_normalized_routes == implementation_normalized_routes
            ),
            "tool_registry_routes_equal_implementation_routes": (
                registry_normalized_routes == implementation_normalized_routes
            ),
            "mismatches": mismatches,
        },
        "interpretation": {
            "intended_operation_count": 18,
            "unique_path_template_count": 17,
            "root_cause_of_prior_17_operation_parse": (
                "duplicate YAML mapping key /assets/{assetId}; ordinary mapping loaders "
                "may retain only one of GET getAsset or PATCH updateAssetConfig"
            ),
            "normalization_rule": (
                "merge duplicate path-key method blocks into one normalized path item; "
                "preserve both operations and validate against executable implementation/tests"
            ),
        },
        "custody_boundaries": {
            "raw_partner_source_committed": False,
            "evaluation_or_gold_material_accessed": False,
            "provider_calls": 0,
            "model_calls": 0,
            "scientific_gate_state_changed": False,
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--openapi", type=Path, required=True)
    ap.add_argument("--implementation", type=Path, required=True)
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument(
        "--registry",
        type=Path,
        default=Path("research/e2/tool_registry.py"),
    )
    ap.add_argument("--out", type=Path, required=True)
    return ap.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
