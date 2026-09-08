from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
from typing import Any

from scripts.research.e0_contract_pipeline import (
    MergeDuplicateLoader,
    build_runtime_openapi,
    operations,
    request_schema,
)


ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "services" / "tractian-supplied-api"
EXPECTED_PART_COUNT = 7
ACTION_REQUEST_REF = {"$ref": "#/components/schemas/ActionRequest"}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _verified_runtime_bundle() -> tuple[bytes, dict[str, Any]]:
    manifest = json.loads((SERVICE / "manifest.json").read_text(encoding="utf-8"))
    parts = sorted(SERVICE.glob("runtime.bundle.b64.part*"))
    assert len(parts) == EXPECTED_PART_COUNT
    assert manifest["runtime_bundle_parts"] == EXPECTED_PART_COUNT
    encoded = b"".join(part.read_bytes().strip() for part in parts)
    bundle = base64.b64decode(encoded, validate=True)
    actual_sha = hashlib.sha256(bundle).hexdigest()
    assert actual_sha == manifest["runtime_bundle_sha256"]
    return bundle, manifest


def _safe_extract(bundle: bytes, destination: Path) -> Path:
    destination = destination.resolve()
    with tarfile.open(fileobj=io.BytesIO(bundle), mode="r:gz") as archive:
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            assert target == destination or destination in target.parents
        archive.extractall(destination)

    contracts = list(destination.rglob("docs/api-contract.openapi.yaml"))
    assert len(contracts) == 1
    return contracts[0].parent.parent


def _parse_partner_openapi(package_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw_path = package_root / "docs" / "api-contract.openapi.yaml"
    loader = MergeDuplicateLoader(raw_path.read_text(encoding="utf-8"))
    try:
        normalized = loader.get_single_data()
        duplicates = list(loader.duplicates)
    finally:
        loader.dispose()
    assert isinstance(normalized, dict)
    return normalized, duplicates


def test_action_request_is_extracted_from_verified_runtime_contract(tmp_path: Path) -> None:
    bundle, manifest = _verified_runtime_bundle()
    package_root = _safe_extract(bundle, tmp_path / "runtime")

    normalized, duplicates = _parse_partner_openapi(package_root)
    runtime = build_runtime_openapi(package_root)

    normalized_ops = operations(normalized)
    runtime_ops = operations(runtime)
    assert set(normalized_ops) == set(runtime_ops)

    request_body_differences: list[str] = []
    for key in sorted(normalized_ops):
        if request_schema(normalized_ops[key]) != request_schema(runtime_ops[key]):
            request_body_differences.append(key)
    assert request_body_differences == []

    normalized_action_request = normalized["components"]["schemas"]["ActionRequest"]
    runtime_action_request = runtime["components"]["schemas"]["ActionRequest"]
    assert normalized_action_request == runtime_action_request

    normalized_action_ops = sorted(
        key
        for key, operation in normalized_ops.items()
        if request_schema(operation) == ACTION_REQUEST_REF
    )
    runtime_action_ops = sorted(
        key
        for key, operation in runtime_ops.items()
        if request_schema(operation) == ACTION_REQUEST_REF
    )
    assert normalized_action_ops == runtime_action_ops
    assert len(runtime_action_ops) == 5

    proof = {
        "schema_version": "provider-v5-action-request-contract-proof-v1",
        "runtime_bundle_parts": EXPECTED_PART_COUNT,
        "runtime_bundle_sha256": manifest["runtime_bundle_sha256"],
        "normalized_operation_count": len(normalized_ops),
        "runtime_operation_count": len(runtime_ops),
        "normalized_unique_path_count": len(normalized.get("paths") or {}),
        "runtime_unique_path_count": len(runtime.get("paths") or {}),
        "duplicate_keys": duplicates,
        "request_body_schema_match": True,
        "action_request_structural_match": True,
        "action_request_sha256": hashlib.sha256(
            _canonical_json(normalized_action_request)
        ).hexdigest(),
        "action_operations": runtime_action_ops,
    }
    print("PROVIDER_V5_ACTION_REQUEST_PROOF=" + json.dumps(proof, sort_keys=True))
