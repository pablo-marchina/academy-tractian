from __future__ import annotations

from collections import Counter
from hashlib import sha1
import json
from pathlib import Path
from typing import Any

AUDIT_PATH = "research/results/final-handoff-acceptance-audit-2026-08-28.json"
ALLOWED_STATUSES = {
    "PASS_EVIDENCED",
    "PASS_BOUNDED",
    "EXTERNALLY_BLOCKED",
    "UNEXECUTED_GATED",
    "GAP_ACTION_REQUIRED",
}
EXPECTED_GROUP_COUNTS = {"A": 5, "B": 13, "C": 13, "D": 7, "E": 14, "F": 10, "G": 13, "H": 8}
EXPECTED_STATUS_COUNTS = {
    "PASS_EVIDENCED": 41,
    "PASS_BOUNDED": 40,
    "EXTERNALLY_BLOCKED": 1,
    "UNEXECUTED_GATED": 1,
}
EXPECTED_REPORTS = {
    "ev007_report_sha256": "7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9",
    "ev008_report_sha256": "1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8",
    "ev011_report_sha256": "cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e",
    "delivery_demo_report_sha256": "43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445",
    "provider_comparison_plan_sha256": "69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f",
    "c4_required_artifact_sha256": "b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c",
}
EXPECTED_HANDOFF_BLOBS = {
    "README.md": "7298d2b4d7546b4ea93b64021faf95fb24958b0f",
    "docs/FINAL-HANDOFF-RUNBOOK.md": "c7df131f555e3b07161fd1d518965958d245555c",
    "docs/RUBRIC-TO-EVIDENCE.md": "a6e540147557991547c2b3b511c727384089506d",
}
REQUIRED_ROW_FIELDS = {
    "audit_id",
    "group",
    "requirement_ids",
    "title",
    "status",
    "evidence",
    "evidence_scope",
    "limitation_or_blocker",
    "gap_action",
    "claim_boundary",
}


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_audit(root: Path) -> dict[str, Any]:
    payload = json.loads((root / AUDIT_PATH).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("audit root must be an object")
    return payload


def validate_handoff_audit(payload: dict[str, Any], root: Path) -> list[str]:
    failures: list[str] = []

    if payload.get("schema_version") != "final-handoff-acceptance-audit-v1":
        failures.append("schema_version")
    if payload.get("issue") != 60:
        failures.append("issue")

    population = payload.get("population")
    if not isinstance(population, dict):
        failures.append("population")
        population = {}
    if population.get("total_rows") != 83:
        failures.append("population_total")
    if population.get("group_counts") != EXPECTED_GROUP_COUNTS:
        failures.append("population_group_counts")
    if population.get("preregistration_correction_comment_id") != 5450823946:
        failures.append("preregistration_correction")

    boundaries = payload.get("frozen_boundaries")
    if not isinstance(boundaries, dict):
        failures.append("frozen_boundaries")
        boundaries = {}
    for field, expected in EXPECTED_REPORTS.items():
        if boundaries.get(field) != expected:
            failures.append(f"boundary_{field}")
    expected_scalars = {
        "provider_calls_consumed": 0,
        "provider_calls_max": 32,
        "credential_account_probes": 0,
        "real_customer_mutations": 0,
        "scientific_gate": "REQUIRED_PER_GROUP_AND_SLICE_REPORTING",
        "provider_selected": False,
        "global_architecture_frozen": False,
        "production_readiness_authorized": False,
    }
    for field, expected in expected_scalars.items():
        if boundaries.get(field) != expected:
            failures.append(f"boundary_{field}")

    rows = payload.get("rows")
    if not isinstance(rows, list):
        return failures + ["rows"]
    if len(rows) != 83:
        failures.append("row_count")

    ids: list[str] = []
    groups: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    by_id: dict[str, dict[str, Any]] = {}

    for index, raw in enumerate(rows):
        prefix = f"row_{index:02d}"
        if not isinstance(raw, dict):
            failures.append(f"{prefix}_object")
            continue
        missing = REQUIRED_ROW_FIELDS - set(raw)
        if missing:
            failures.append(f"{prefix}_fields")
            continue

        audit_id = raw.get("audit_id")
        group = raw.get("group")
        status = raw.get("status")
        evidence = raw.get("evidence")

        if not _nonempty(audit_id):
            failures.append(f"{prefix}_audit_id")
        else:
            ids.append(audit_id)
            by_id[audit_id] = raw
        if group not in EXPECTED_GROUP_COUNTS:
            failures.append(f"{prefix}_group")
        else:
            groups[group] += 1
        if status not in ALLOWED_STATUSES:
            failures.append(f"{prefix}_status")
        else:
            statuses[status] += 1
        if not isinstance(raw.get("requirement_ids"), list) or not raw["requirement_ids"]:
            failures.append(f"{prefix}_requirement_ids")
        if not _nonempty(raw.get("title")):
            failures.append(f"{prefix}_title")
        if not _nonempty(raw.get("evidence_scope")):
            failures.append(f"{prefix}_evidence_scope")
        if not _nonempty(raw.get("claim_boundary")):
            failures.append(f"{prefix}_claim_boundary")

        if not isinstance(evidence, list):
            failures.append(f"{prefix}_evidence_list")
            evidence = []
        if status in {"PASS_EVIDENCED", "PASS_BOUNDED"} and not evidence:
            failures.append(f"{prefix}_pass_without_evidence")
        if status in {"PASS_BOUNDED", "EXTERNALLY_BLOCKED", "UNEXECUTED_GATED"} and not _nonempty(raw.get("limitation_or_blocker")):
            failures.append(f"{prefix}_missing_limitation")
        if status == "GAP_ACTION_REQUIRED" and not _nonempty(raw.get("gap_action")):
            failures.append(f"{prefix}_gap_without_action")

        for evidence_index, item in enumerate(evidence):
            eprefix = f"{prefix}_evidence_{evidence_index}"
            if not isinstance(item, dict) or not _nonempty(item.get("path")):
                failures.append(f"{eprefix}_path")
                continue
            relative = Path(item["path"])
            if relative.is_absolute() or ".." in relative.parts:
                failures.append(f"{eprefix}_unsafe_path")
                continue
            target = root / relative
            if not target.is_file():
                failures.append(f"{eprefix}_missing")
                continue
            data = target.read_bytes()
            declared_blob = item.get("git_blob_sha1")
            if declared_blob is not None and git_blob_sha1(data) != declared_blob:
                failures.append(f"{eprefix}_blob")
            canonical = item.get("canonical_sha256")
            if canonical is not None and canonical.encode("ascii") not in data:
                failures.append(f"{eprefix}_canonical_identity")

    if len(ids) != len(set(ids)):
        failures.append("duplicate_audit_id")
    if dict(groups) != EXPECTED_GROUP_COUNTS:
        failures.append("observed_group_counts")
    if dict(statuses) != EXPECTED_STATUS_COUNTS:
        failures.append("observed_status_counts")
    if payload.get("status_counts") != EXPECTED_STATUS_COUNTS:
        failures.append("declared_status_counts")
    if statuses.get("GAP_ACTION_REQUIRED", 0) != 0:
        failures.append("unclosed_gap")

    c13 = by_id.get("C-13", {})
    if c13.get("status") != "EXTERNALLY_BLOCKED" or EXPECTED_REPORTS["c4_required_artifact_sha256"] not in str(c13.get("limitation_or_blocker")):
        failures.append("c4_blocker_disposition")
    e11 = by_id.get("E-11", {})
    if e11.get("status") != "UNEXECUTED_GATED" or "0/32" not in str(e11.get("limitation_or_blocker")):
        failures.append("provider_disposition")

    closures = payload.get("initial_unblocked_gaps_closed")
    if not isinstance(closures, list) or len(closures) != 3:
        failures.append("gap_closures")
    else:
        for closure in closures:
            if not isinstance(closure, dict) or not _nonempty(closure.get("closure_path")):
                failures.append("gap_closure_entry")
                continue
            if not (root / closure["closure_path"]).is_file():
                failures.append("gap_closure_missing")

    for path, expected_blob in EXPECTED_HANDOFF_BLOBS.items():
        target = root / path
        if not target.is_file() or git_blob_sha1(target.read_bytes()) != expected_blob:
            failures.append(f"handoff_blob_{path}")

    if not _nonempty(payload.get("interpretation")):
        failures.append("interpretation")

    return failures
