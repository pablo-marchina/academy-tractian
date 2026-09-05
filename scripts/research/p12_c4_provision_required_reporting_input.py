#!/usr/bin/env python3
from __future__ import annotations

"""Fail-closed evaluator-side provisioner for frozen P12-C4 score rows.

This utility NEVER reconstructs, rescores, mutates, or publishes evaluator data.
It accepts only the exact already-existing deterministic score-row artifact bound
by the frozen required-reporting execution contract, verifies its immutable
identity and geometry, and atomically copies it to a destination outside the
repository. Only a sanitized receipt is printed/written.
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

EXPECTED_SHA256 = "b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c"
EXPECTED_BYTES = 177350
EXPECTED_SCHEMA = "p12-c4-deterministic-private-scoring-rows-v1"
EXPECTED_STATUS = "PASS_144_OF_144_DETERMINISTIC_SCORES"
EXPECTED_EXPERIMENT_ID = "P12-C4-PROSPECTIVE-EXPOSED-POOL"
EXPECTED_PARTITION = "EXPOSED_POOL"
EXPECTED_ROWS = 144
EXPECTED_PARENTS = 36
EXPECTED_ARMS = ["A00", "A10", "A01", "A11"]
EXPECTED_GROUPS = [
    "asset_B204",
    "asset_C710",
    "asset_G501",
    "asset_M101",
    "asset_M102",
    "asset_M208",
    "asset_S420",
]
EXPECTED_MODALITIES = ["investigate", "execute", "contextualize"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_and_validate(source: Path) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    if not source.is_file():
        raise AssertionError("source artifact does not exist or is not a regular file")

    data = source.read_bytes()
    actual_sha = sha256_bytes(data)
    if actual_sha != EXPECTED_SHA256:
        raise AssertionError(f"source SHA-256 mismatch: {actual_sha}")
    if len(data) != EXPECTED_BYTES:
        raise AssertionError(f"source size mismatch: {len(data)} bytes")

    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssertionError("source is not the expected UTF-8 JSON artifact") from exc

    if payload.get("schema_version") != EXPECTED_SCHEMA:
        raise AssertionError("score artifact schema mismatch")
    if payload.get("status") != EXPECTED_STATUS:
        raise AssertionError("score artifact status mismatch")
    if payload.get("experiment_id") != EXPECTED_EXPERIMENT_ID:
        raise AssertionError("score artifact experiment_id mismatch")
    if payload.get("partition") != EXPECTED_PARTITION:
        raise AssertionError("score artifact partition mismatch")
    if payload.get("participating_arms") != EXPECTED_ARMS:
        raise AssertionError("score artifact arm order/set mismatch")
    if int(payload.get("common_parent_count") or 0) != EXPECTED_PARENTS:
        raise AssertionError("score artifact common-parent count mismatch")

    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ROWS:
        raise AssertionError("score artifact must contain exactly 144 rows")
    if any((row.get("score") or {}).get("scoreable") is not True for row in rows):
        raise AssertionError("all deterministic score rows must remain scoreable")

    parents: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        parent_id = str(row.get("parent_id"))
        parents.setdefault(parent_id, []).append(row)

    expected_parent_ids = {f"P{i:02d}" for i in range(1, EXPECTED_PARENTS + 1)}
    if set(parents) != expected_parent_ids:
        raise AssertionError("parent IDs are not exactly P01..P36")
    for parent_id, parent_rows in parents.items():
        if len(parent_rows) != len(EXPECTED_ARMS):
            raise AssertionError(f"{parent_id}: expected exactly four arm rows")
        if {str(row.get("arm")) for row in parent_rows} != set(EXPECTED_ARMS):
            raise AssertionError(f"{parent_id}: paired arm set mismatch")

    groups = sorted({str(row.get("group_id")) for row in rows})
    if groups != sorted(EXPECTED_GROUPS):
        raise AssertionError("asset_story_group set mismatch")
    modalities = sorted({str(row.get("modality")) for row in rows})
    if modalities != sorted(EXPECTED_MODALITIES):
        raise AssertionError("modality set mismatch")

    receipt = {
        "schema_version": "p12-c4-required-reporting-input-provisioning-receipt-v1",
        "status": "PASS_EXACT_EVALUATOR_SIDE_INPUT_PROVISIONED",
        "artifact_sha256": EXPECTED_SHA256,
        "artifact_bytes": EXPECTED_BYTES,
        "score_schema_version": EXPECTED_SCHEMA,
        "score_status": EXPECTED_STATUS,
        "experiment_id": EXPECTED_EXPERIMENT_ID,
        "partition": EXPECTED_PARTITION,
        "rows": EXPECTED_ROWS,
        "common_parents": EXPECTED_PARENTS,
        "arms": EXPECTED_ARMS,
        "group_ids": EXPECTED_GROUPS,
        "modalities": EXPECTED_MODALITIES,
        "scores_recomputed": False,
        "scores_mutated": False,
        "private_oracle_loaded": False,
        "provider_calls": 0,
        "model_calls": 0,
        "source_path_serialized": False,
        "destination_path_serialized": False,
    }
    return data, payload, receipt


def provision(data: bytes, destination: Path, root: Path) -> str:
    destination = destination.expanduser().resolve()
    if inside(destination, root):
        raise AssertionError("destination must be outside the Git repository")

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.parent.chmod(0o700)
    except OSError:
        pass

    if destination.exists():
        if not destination.is_file():
            raise AssertionError("destination exists and is not a regular file")
        existing = destination.read_bytes()
        if sha256_bytes(existing) != EXPECTED_SHA256 or len(existing) != EXPECTED_BYTES:
            raise AssertionError("destination exists with different bytes")
        return "ALREADY_PROVISIONED_EXACT_BYTES"

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=str(destination.parent),
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            temp_path.chmod(0o600)
        except OSError:
            pass

        if sha256_bytes(temp_path.read_bytes()) != EXPECTED_SHA256:
            raise AssertionError("atomic-copy verification failed before replace")

        os.replace(temp_path, destination)
        try:
            destination.chmod(0o600)
        except OSError:
            pass
    finally:
        if temp_path.exists():
            temp_path.unlink()

    copied = destination.read_bytes()
    if len(copied) != EXPECTED_BYTES or sha256_bytes(copied) != EXPECTED_SHA256:
        raise AssertionError("post-provisioning destination verification failed")
    return "PROVISIONED_EXACT_BYTES"


def write_receipt(receipt: dict[str, Any], receipt_out: Path | None) -> None:
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if receipt_out is None:
        sys.stdout.write(rendered)
        return

    target = receipt_out.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp")
    tmp.write_text(rendered, encoding="utf-8")
    os.replace(tmp, target)
    sys.stdout.write(rendered)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Provision only the exact frozen P12-C4 deterministic score artifact."
    )
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--destination", type=Path, required=True)
    ap.add_argument(
        "--receipt-out",
        type=Path,
        default=None,
        help="optional sanitized JSON receipt path; never contains evaluator row data",
    )
    args = ap.parse_args()

    root = repo_root()
    source = args.source.expanduser().resolve()
    if inside(source, root):
        raise AssertionError("source artifact must remain outside the Git repository")

    data, _payload, receipt = load_and_validate(source)
    disposition = provision(data, args.destination, root)
    receipt["disposition"] = disposition
    receipt["destination_outside_repository"] = True
    write_receipt(receipt, args.receipt_out)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"PROVISIONING_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(2)
