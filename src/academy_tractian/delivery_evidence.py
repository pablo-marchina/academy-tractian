from __future__ import annotations

from pathlib import Path

from .delivery_reproduction import (
    EXPECTED_C4_ARTIFACT_BYTES,
    EXPECTED_C4_ARTIFACT_ROWS,
    EXPECTED_C4_ARTIFACT_SHA256,
    EXPECTED_EV007_REPORT_SHA256,
    EXPECTED_EV008_REPORT_SHA256,
    EXPECTED_EV011_REPORT_SHA256,
    EXPECTED_PROVIDER_PLAN_SHA256,
    EvidenceIndex,
    EvidenceIndexValidation,
    git_blob_sha1,
)


CANONICAL_ADR_PATHS: dict[int, str] = {
    4: "docs/adr/004-agent-controller-runtime-2026-08-27.md",
    5: "docs/adr/005-production-action-safety-policy-2026-08-27.md",
    6: "docs/adr/006-provider-neutral-decision-source-2026-08-27.md",
    7: "docs/adr/007-model-call-trace-provenance-2026-08-27.md",
    8: "docs/adr/008-provider-model-comparison-design-2026-08-28.md",
    9: "docs/adr/009-provider-http-clients-live-comparison-authorization-2026-08-28.md",
    10: "docs/adr/010-provider-comparison-executor-2026-08-28.md",
    11: "docs/adr/011-governed-live-provider-execution-wrapper-2026-08-28.md",
    12: "docs/adr/012-controlled-action-execution-profile-2026-08-28.md",
    13: "docs/adr/013-provider-free-failure-performance-campaign-2026-08-28.md",
    14: "docs/adr/014-provider-free-repeated-run-stability-2026-08-28.md",
    15: "docs/adr/015-provider-free-customer-safe-communication-2026-08-28.md",
}


def validate_delivery_evidence_index(
    index: EvidenceIndex,
    root: Path | str,
) -> EvidenceIndexValidation:
    root_path = Path(root).resolve()
    violations: list[str] = []
    resident_count = 0
    resolved_count = 0
    by_id = {entry.evidence_id: entry for entry in index.entries}

    for entry in index.entries:
        if entry.repository_path is None:
            continue
        resident_count += 1
        candidate = (root_path / entry.repository_path).resolve()
        try:
            candidate.relative_to(root_path)
        except ValueError:
            violations.append(f"{entry.evidence_id}: repository path escapes root")
            continue
        if not candidate.is_file():
            violations.append(f"{entry.evidence_id}: repository path missing")
            continue
        actual_blob = git_blob_sha1(candidate)
        if actual_blob != entry.git_blob_sha1:
            violations.append(f"{entry.evidence_id}: Git blob SHA-1 mismatch")
            continue
        resolved_count += 1

    for adr_number, expected_path in CANONICAL_ADR_PATHS.items():
        evidence_id = f"ADR-{adr_number:03d}"
        entry = by_id.get(evidence_id)
        if entry is None:
            violations.append(f"{evidence_id}: required ADR entry missing")
            continue
        if entry.category != "adr" or entry.adr_number != adr_number:
            violations.append(f"{evidence_id}: ADR metadata mismatch")
        if entry.repository_path != expected_path:
            violations.append(f"{evidence_id}: canonical ADR path mismatch")

    required_reports = {
        "EV007-RESULT": EXPECTED_EV007_REPORT_SHA256,
        "EV008-RESULT": EXPECTED_EV008_REPORT_SHA256,
        "EV011-RESULT": EXPECTED_EV011_REPORT_SHA256,
    }
    for evidence_id, expected_sha in required_reports.items():
        entry = by_id.get(evidence_id)
        if entry is None:
            violations.append(f"{evidence_id}: required frozen result missing")
        elif entry.canonical_sha256 != expected_sha:
            violations.append(f"{evidence_id}: canonical report SHA-256 mismatch")

    provider = by_id.get("PROVIDER-COMPARISON-PLAN")
    if provider is None:
        violations.append("PROVIDER-COMPARISON-PLAN: required entry missing")
    else:
        if provider.canonical_sha256 != EXPECTED_PROVIDER_PLAN_SHA256:
            violations.append("PROVIDER-COMPARISON-PLAN: canonical plan SHA-256 mismatch")
        if provider.reproduction_status != "UNEXECUTED_GATED":
            violations.append(
                "PROVIDER-COMPARISON-PLAN: live execution must remain UNEXECUTED_GATED"
            )

    c4 = by_id.get("C4-SCORE-ROW-ARTIFACT")
    if c4 is None:
        violations.append("C4-SCORE-ROW-ARTIFACT: required blocker entry missing")
    else:
        if c4.repository_path is not None or c4.git_blob_sha1 is not None:
            violations.append(
                "C4-SCORE-ROW-ARTIFACT: missing external artifact must not claim repository residency"
            )
        if c4.canonical_sha256 != EXPECTED_C4_ARTIFACT_SHA256:
            violations.append("C4-SCORE-ROW-ARTIFACT: expected SHA-256 mismatch")
        if c4.reproduction_status != "EXTERNALLY_BLOCKED":
            violations.append("C4-SCORE-ROW-ARTIFACT: must remain EXTERNALLY_BLOCKED")
        boundary = c4.authorization_boundary
        if (
            str(EXPECTED_C4_ARTIFACT_BYTES) not in boundary
            or str(EXPECTED_C4_ARTIFACT_ROWS) not in boundary
        ):
            violations.append(
                "C4-SCORE-ROW-ARTIFACT: blocker byte/row identity missing from boundary"
            )

    required_frozen_ids = {
        "EV007-FREEZE",
        "EV007-VALIDATOR",
        "EV008-FREEZE",
        "EV008-VALIDATOR",
        "EV011-FREEZE",
        "EV011-VALIDATOR",
    }
    for evidence_id in sorted(required_frozen_ids):
        if evidence_id not in by_id:
            violations.append(f"{evidence_id}: required evidence missing")

    required_demo_ids = {f"DEMO-0{i}" for i in range(1, 6)} | {
        "DELIVERY-DEMO-CAMPAIGN"
    }
    for evidence_id in sorted(required_demo_ids):
        if evidence_id not in by_id:
            violations.append(f"{evidence_id}: required demo evidence missing")

    return EvidenceIndexValidation(
        entry_count=len(index.entries),
        repository_resident_count=resident_count,
        resolved_repository_entries=resolved_count,
        violations=tuple(violations),
    )
