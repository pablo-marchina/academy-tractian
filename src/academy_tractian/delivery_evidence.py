from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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

EXPECTED_DELIVERY_DEMO_REPORT_SHA256 = (
    "43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445"
)
EXPECTED_DELIVERY_DEMO_RESULT_SHA256: dict[str, str] = {
    "DEMO-01": "55a81f09d52fcb91caf22dcd452ac23dee143f405e4e3b90b1971d040b592cff",
    "DEMO-02": "a30033aed27b89a52602a0c794c15134ceec39c6a7935b39709698943e4854eb",
    "DEMO-03": "2e4dc13ef6edbae797299974e3031d893f11bd0fa4ddd7451a8a06525c6609cb",
    "DEMO-04": "1d72f3f40bf78bc63232c0dcc45496bd4ea5977cbdc6368565f654d313f37720",
    "DEMO-05": "80f11833ecfb1b425ea66f65d1fd709475ff856a240e747c37607fec74ce65ca",
}

DEMO_RESULT_MANIFEST_PATH = (
    "research/results/provider-free-final-delivery-demo-result-2026-08-28.json"
)
DELIVERY_VALIDATOR_PATH = "scripts/validate_delivery_reproduction.py"
DELIVERY_WORKFLOW_PATH = ".github/workflows/final-delivery-provider-free-reproduction.yml"
PROVIDER_COMPARISON_PLAN_PATH = (
    "research/frozen/provider-comparison-executor-freeze-v1.json"
)

FROZEN_RESULT_PATHS: dict[str, tuple[str, str, str]] = {
    "EV007": (
        "research/frozen/ev007-provider-free-failure-performance-freeze-v1.json",
        "research/results/ev007-provider-free-failure-campaign-result-2026-08-28.json",
        EXPECTED_EV007_REPORT_SHA256,
    ),
    "EV008": (
        "research/frozen/ev008-provider-free-repeated-run-stability-freeze-v1.json",
        "research/results/ev008-provider-free-stability-campaign-result-2026-08-28.json",
        EXPECTED_EV008_REPORT_SHA256,
    ),
    "EV011": (
        "research/frozen/ev011-provider-free-customer-safe-communication-freeze-v1.json",
        "research/results/ev011-provider-free-communication-campaign-result-2026-08-28.json",
        EXPECTED_EV011_REPORT_SHA256,
    ),
}

CANONICAL_REQUIRED_PATHS: dict[str, str] = {
    "EV007-FREEZE": FROZEN_RESULT_PATHS["EV007"][0],
    "EV007-RESULT": FROZEN_RESULT_PATHS["EV007"][1],
    "EV007-VALIDATOR": "scripts/validate_ev007_failure_campaign.py",
    "EV008-FREEZE": FROZEN_RESULT_PATHS["EV008"][0],
    "EV008-RESULT": FROZEN_RESULT_PATHS["EV008"][1],
    "EV008-VALIDATOR": "scripts/validate_ev008_stability_campaign.py",
    "EV011-FREEZE": FROZEN_RESULT_PATHS["EV011"][0],
    "EV011-RESULT": FROZEN_RESULT_PATHS["EV011"][1],
    "EV011-VALIDATOR": "scripts/validate_ev011_communication_campaign.py",
    "PROVIDER-COMPARISON-PLAN": PROVIDER_COMPARISON_PLAN_PATH,
    "DELIVERY-DEMO-CAMPAIGN": DEMO_RESULT_MANIFEST_PATH,
    "DELIVERY-VALIDATOR": DELIVERY_VALIDATOR_PATH,
    "DELIVERY-WORKFLOW": DELIVERY_WORKFLOW_PATH,
    **{scenario_id: DEMO_RESULT_MANIFEST_PATH for scenario_id in EXPECTED_DELIVERY_DEMO_RESULT_SHA256},
}


def _load_json(path: Path, evidence_id: str, violations: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        violations.append(f"{evidence_id}: repository JSON could not be parsed")
        return None
    if not isinstance(payload, dict):
        violations.append(f"{evidence_id}: repository JSON root must be an object")
        return None
    return payload


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
        if entry.reproduction_status != "HISTORICAL_IMMUTABLE":
            violations.append(f"{evidence_id}: frozen ADR must remain HISTORICAL_IMMUTABLE")

    for evidence_id, expected_path in CANONICAL_REQUIRED_PATHS.items():
        entry = by_id.get(evidence_id)
        if entry is None:
            violations.append(f"{evidence_id}: required evidence missing")
            continue
        if entry.repository_path != expected_path:
            violations.append(f"{evidence_id}: canonical repository path mismatch")

    for family, (freeze_path, result_path, expected_sha) in FROZEN_RESULT_PATHS.items():
        result_id = f"{family}-RESULT"
        result_entry = by_id.get(result_id)
        if result_entry is not None and result_entry.canonical_sha256 != expected_sha:
            violations.append(f"{result_id}: canonical report SHA-256 mismatch")

        result_file = root_path / result_path
        result_blob = git_blob_sha1(result_file) if result_file.is_file() else None
        if result_file.is_file():
            payload = _load_json(result_file, result_id, violations)
            if payload is not None and payload.get("report_sha256") != expected_sha:
                violations.append(f"{result_id}: repository result report SHA-256 mismatch")

        freeze_id = f"{family}-FREEZE"
        freeze_file = root_path / freeze_path
        if freeze_file.is_file():
            payload = _load_json(freeze_file, freeze_id, violations)
            if payload is not None:
                frozen_result = payload.get("result")
                if not isinstance(frozen_result, dict):
                    violations.append(f"{freeze_id}: frozen result declaration missing")
                elif frozen_result.get("report_sha256") != expected_sha:
                    violations.append(f"{freeze_id}: frozen report SHA-256 mismatch")
                if isinstance(frozen_result, dict) and "path" in frozen_result:
                    if frozen_result.get("path") != result_path:
                        violations.append(f"{freeze_id}: frozen result path mismatch")
                else:
                    direct_blobs = payload.get("direct_blobs")
                    if not isinstance(direct_blobs, dict):
                        violations.append(f"{freeze_id}: frozen direct_blobs declaration missing")
                    elif result_blob is None or direct_blobs.get(result_path) != result_blob:
                        violations.append(f"{freeze_id}: frozen result blob/path mismatch")

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
        provider_file = root_path / PROVIDER_COMPARISON_PLAN_PATH
        if provider_file.is_file():
            payload = _load_json(provider_file, "PROVIDER-COMPARISON-PLAN", violations)
            if payload is not None:
                if payload.get("plan_sha256") != EXPECTED_PROVIDER_PLAN_SHA256:
                    violations.append(
                        "PROVIDER-COMPARISON-PLAN: repository plan SHA-256 mismatch"
                    )
                if payload.get("production_live_calls_consumed") != 0:
                    violations.append(
                        "PROVIDER-COMPARISON-PLAN: repository freeze no longer records 0 live calls"
                    )
                if payload.get("production_provider_model_selected") is not False:
                    violations.append(
                        "PROVIDER-COMPARISON-PLAN: repository freeze unexpectedly selects provider"
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

    demo_manifest = root_path / DEMO_RESULT_MANIFEST_PATH
    if demo_manifest.is_file():
        payload = _load_json(demo_manifest, "DELIVERY-DEMO-CAMPAIGN", violations)
        if payload is not None:
            if payload.get("report_sha256") != EXPECTED_DELIVERY_DEMO_REPORT_SHA256:
                violations.append("DELIVERY-DEMO-CAMPAIGN: report SHA-256 mismatch")
            if payload.get("denominator") != 5 or payload.get("exact_traces_evaluated") != 5:
                violations.append("DELIVERY-DEMO-CAMPAIGN: exact denominator/trace count mismatch")
            if payload.get("contract_expectations_passed") != 5:
                violations.append("DELIVERY-DEMO-CAMPAIGN: contract pass count mismatch")
            for zero_field in (
                "provider_calls",
                "credential_account_probes",
                "real_customer_mutations",
                "semantic_private_blind_access",
                "automatic_retry_count",
                "replay_count",
            ):
                if payload.get(zero_field) != 0:
                    violations.append(
                        f"DELIVERY-DEMO-CAMPAIGN: {zero_field} must remain zero"
                    )

            scenarios = payload.get("scenarios")
            if not isinstance(scenarios, list):
                violations.append("DELIVERY-DEMO-CAMPAIGN: scenarios missing")
                scenarios = []
            scenario_by_id = {
                item.get("scenario_id"): item
                for item in scenarios
                if isinstance(item, dict) and isinstance(item.get("scenario_id"), str)
            }
            if list(scenario_by_id) != list(EXPECTED_DELIVERY_DEMO_RESULT_SHA256):
                violations.append("DELIVERY-DEMO-CAMPAIGN: scenario population/order mismatch")

            campaign_entry = by_id.get("DELIVERY-DEMO-CAMPAIGN")
            if (
                campaign_entry is not None
                and campaign_entry.canonical_sha256 != EXPECTED_DELIVERY_DEMO_REPORT_SHA256
            ):
                violations.append(
                    "DELIVERY-DEMO-CAMPAIGN: indexed canonical report SHA-256 mismatch"
                )
            if (
                campaign_entry is not None
                and campaign_entry.reproduction_status != "PROVIDER_FREE_REPRODUCIBLE"
            ):
                violations.append(
                    "DELIVERY-DEMO-CAMPAIGN: must be PROVIDER_FREE_REPRODUCIBLE"
                )

            for scenario_id, expected_result_sha in EXPECTED_DELIVERY_DEMO_RESULT_SHA256.items():
                entry = by_id.get(scenario_id)
                if entry is None:
                    violations.append(f"{scenario_id}: required demo evidence missing")
                    continue
                if entry.canonical_sha256 != expected_result_sha:
                    violations.append(f"{scenario_id}: indexed result SHA-256 mismatch")
                if entry.reproduction_status != "PROVIDER_FREE_REPRODUCIBLE":
                    violations.append(f"{scenario_id}: must be PROVIDER_FREE_REPRODUCIBLE")
                record = scenario_by_id.get(scenario_id)
                if not isinstance(record, dict):
                    violations.append(f"{scenario_id}: scenario record missing from manifest")
                elif record.get("result_sha256") != expected_result_sha:
                    violations.append(f"{scenario_id}: manifest result SHA-256 mismatch")

    delivery_validator = by_id.get("DELIVERY-VALIDATOR")
    if delivery_validator is not None and delivery_validator.category != "validator":
        violations.append("DELIVERY-VALIDATOR: category mismatch")
    delivery_workflow = by_id.get("DELIVERY-WORKFLOW")
    if delivery_workflow is not None and delivery_workflow.category != "workflow":
        violations.append("DELIVERY-WORKFLOW: category mismatch")

    return EvidenceIndexValidation(
        entry_count=len(index.entries),
        repository_resident_count=resident_count,
        resolved_repository_entries=resolved_count,
        violations=tuple(violations),
    )
