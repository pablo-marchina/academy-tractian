from __future__ import annotations

from pathlib import Path

import pytest

from academy_tractian.delivery_evidence import (
    CANONICAL_ADR_PATHS,
    validate_delivery_evidence_index,
)
from academy_tractian.delivery_reproduction import (
    EXPECTED_C4_ARTIFACT_BYTES,
    EXPECTED_C4_ARTIFACT_ROWS,
    EXPECTED_C4_ARTIFACT_SHA256,
    EXPECTED_EV007_REPORT_SHA256,
    EXPECTED_EV008_REPORT_SHA256,
    EXPECTED_EV011_REPORT_SHA256,
    EXPECTED_PROVIDER_PLAN_SHA256,
    EvidenceEntry,
    EvidenceIndex,
    canonical_sha256,
    demo_population,
    git_blob_sha1,
    run_provider_free_delivery_demo,
)


ROOT = Path(__file__).resolve().parents[1]
ADR_PATHS = CANONICAL_ADR_PATHS


def _resident(
    evidence_id: str,
    category: str,
    path: str,
    *,
    canonical: str | None = None,
    issue: int | None = None,
    pr: int | None = None,
    adr: int | None = None,
    status: str = "PROVIDER_FREE_REPRODUCIBLE",
    boundary: str = "Provider-free repository evidence only; no live provider authorization.",
) -> EvidenceEntry:
    return EvidenceEntry(
        evidence_id=evidence_id,
        category=category,
        title=evidence_id,
        repository_path=path,
        git_blob_sha1=git_blob_sha1(ROOT / path),
        canonical_sha256=canonical,
        issue_number=issue,
        pull_request_number=pr,
        adr_number=adr,
        reproduction_status=status,
        authorization_boundary=boundary,
    )


def _valid_index() -> EvidenceIndex:
    entries: list[EvidenceEntry] = []
    for adr, path in ADR_PATHS.items():
        entries.append(
            _resident(
                f"ADR-{adr:03d}",
                "adr",
                path,
                adr=adr,
                status="HISTORICAL_IMMUTABLE",
                boundary="Frozen ADR semantics only; no additional authorization inferred.",
            )
        )

    entries.extend(
        [
            _resident(
                "EV007-FREEZE",
                "freeze",
                "research/frozen/ev007-provider-free-failure-performance-freeze-v1.json",
                issue=48,
                pr=49,
            ),
            _resident(
                "EV007-RESULT",
                "result",
                "research/results/ev007-provider-free-failure-campaign-result-2026-08-28.json",
                canonical=EXPECTED_EV007_REPORT_SHA256,
                issue=48,
                pr=49,
            ),
            _resident(
                "EV007-VALIDATOR",
                "validator",
                "scripts/validate_ev007_failure_campaign.py",
                issue=48,
                pr=49,
            ),
            _resident(
                "EV008-FREEZE",
                "freeze",
                "research/frozen/ev008-provider-free-repeated-run-stability-freeze-v1.json",
                issue=51,
                pr=52,
            ),
            _resident(
                "EV008-RESULT",
                "result",
                "research/results/ev008-provider-free-stability-campaign-result-2026-08-28.json",
                canonical=EXPECTED_EV008_REPORT_SHA256,
                issue=51,
                pr=52,
            ),
            _resident(
                "EV008-VALIDATOR",
                "validator",
                "scripts/validate_ev008_stability_campaign.py",
                issue=51,
                pr=52,
            ),
            _resident(
                "EV011-FREEZE",
                "freeze",
                "research/frozen/ev011-provider-free-customer-safe-communication-freeze-v1.json",
                issue=54,
                pr=55,
            ),
            _resident(
                "EV011-RESULT",
                "result",
                "research/results/ev011-provider-free-communication-campaign-result-2026-08-28.json",
                canonical=EXPECTED_EV011_REPORT_SHA256,
                issue=54,
                pr=55,
            ),
            _resident(
                "EV011-VALIDATOR",
                "validator",
                "scripts/validate_ev011_communication_campaign.py",
                issue=54,
                pr=55,
            ),
            _resident(
                "PROVIDER-COMPARISON-PLAN",
                "provider_plan",
                "research/frozen/provider-comparison-executor-freeze-v1.json",
                canonical=EXPECTED_PROVIDER_PLAN_SHA256,
                issue=44,
                status="UNEXECUTED_GATED",
                boundary="Live comparison remains at 0/32 calls and requires both explicit secrets plus one canonical durable custody root.",
            ),
            EvidenceEntry(
                evidence_id="C4-SCORE-ROW-ARTIFACT",
                category="scientific_blocker",
                title="Missing evaluator-side deterministic score-row artifact",
                repository_path=None,
                git_blob_sha1=None,
                canonical_sha256=EXPECTED_C4_ARTIFACT_SHA256,
                reproduction_status="EXTERNALLY_BLOCKED",
                authorization_boundary=(
                    f"Exact external artifact only: {EXPECTED_C4_ARTIFACT_BYTES} bytes, "
                    f"{EXPECTED_C4_ARTIFACT_ROWS} rows; reconstruction/rescoring/substitution forbidden."
                ),
            ),
        ]
    )

    for scenario_id in [f"DEMO-0{i}" for i in range(1, 6)]:
        entries.append(
            _resident(
                scenario_id,
                "demo",
                "src/academy_tractian/delivery_reproduction.py",
                issue=57,
                boundary="Synthetic provider-free demo evidence only; no real customer mutation.",
            )
        )
    entries.append(
        _resident(
            "DELIVERY-DEMO-CAMPAIGN",
            "demo",
            "src/academy_tractian/delivery_reproduction.py",
            issue=57,
            boundary="Synthetic provider-free demo campaign only; no production-readiness claim.",
        )
    )
    return EvidenceIndex(entries=tuple(sorted(entries, key=lambda entry: entry.evidence_id)))


def _replace(index: EvidenceIndex, evidence_id: str, **changes: object) -> EvidenceIndex:
    entries = [
        entry.model_copy(update=changes) if entry.evidence_id == evidence_id else entry
        for entry in index.entries
    ]
    return EvidenceIndex(entries=tuple(entries))


def test_demo_population_is_exact_and_preregistered() -> None:
    population = demo_population()
    assert [spec.scenario_id for spec in population] == [f"DEMO-0{i}" for i in range(1, 6)]
    assert [spec.fixture_kind for spec in population] == [
        "read_investigate",
        "clarify",
        "abstain",
        "escalate",
        "controlled_action",
    ]
    assert [spec.expected_terminal_decision for spec in population] == [
        "ORIENT",
        "ASK_CLARIFICATION",
        "ABSTAIN",
        "ESCALATE_HUMAN",
        "ACT_REPROCESS",
    ]
    assert [spec.expected_transport_count for spec in population] == [1, 0, 0, 0, 1]
    assert [spec.expected_action_transport_count for spec in population] == [0, 0, 0, 0, 1]
    assert all(spec.expected_evaluator_pass for spec in population)
    assert len({spec.spec_sha256 for spec in population}) == 5


def test_delivery_demo_executes_exact_five_traces_and_controlled_action_once(tmp_path: Path) -> None:
    report = run_provider_free_delivery_demo(tmp_path / "demo")

    assert report.denominator == 5
    assert report.exact_traces_evaluated == 5
    assert report.contract_expectations_passed == 5
    assert report.provider_calls == 0
    assert report.credential_account_probes == 0
    assert report.real_customer_mutations == 0
    assert report.semantic_private_blind_access == 0
    assert report.automatic_retry_count == 0
    assert report.replay_count == 0
    assert [result.scenario_id for result in report.results] == [f"DEMO-0{i}" for i in range(1, 6)]
    assert all(result.evaluator_pass for result in report.results)
    assert all(result.trace_lifecycle_valid for result in report.results)

    controlled = report.results[-1]
    assert controlled.terminal_decision == "ACT_REPROCESS"
    assert controlled.transport_count == 1
    assert controlled.action_transport_count == 1
    assert controlled.durable_claim_count == 1
    assert list((tmp_path / "demo" / "DEMO-05" / "claims").glob("*.json"))


def test_delivery_demo_hashes_are_deterministic_across_fresh_custody_roots(tmp_path: Path) -> None:
    first = run_provider_free_delivery_demo(tmp_path / "first")
    second = run_provider_free_delivery_demo(tmp_path / "second")

    assert first.report_sha256 == second.report_sha256
    assert [result.spec_sha256 for result in first.results] == [result.spec_sha256 for result in second.results]
    assert [result.result_sha256 for result in first.results] == [result.result_sha256 for result in second.results]
    assert [result.behavioral_trace_sha256 for result in first.results] == [result.behavioral_trace_sha256 for result in second.results]
    assert [result.trace_sha256 for result in first.results] == [result.trace_sha256 for result in second.results]


def test_empty_action_fingerprint_signature_is_canonical_for_non_action_scenarios(tmp_path: Path) -> None:
    report = run_provider_free_delivery_demo(tmp_path / "demo")
    empty = canonical_sha256([])
    assert all(result.action_fingerprint_sha256 == empty for result in report.results[:4])
    assert report.results[-1].action_fingerprint_sha256 != empty


def test_valid_evidence_index_resolves_repository_items_and_preserves_blockers() -> None:
    validation = validate_delivery_evidence_index(_valid_index(), ROOT)
    assert validation.passed, validation.violations
    assert validation.repository_resident_count == validation.resolved_repository_entries
    assert validation.repository_resident_count == validation.entry_count - 1


def test_wrong_repository_blob_is_rejected() -> None:
    index = _replace(_valid_index(), "EV007-RESULT", git_blob_sha1="0" * 40)
    validation = validate_delivery_evidence_index(index, ROOT)
    assert not validation.passed
    assert "EV007-RESULT: Git blob SHA-1 mismatch" in validation.violations


def test_missing_repository_path_is_rejected() -> None:
    index = _replace(
        _valid_index(),
        "EV008-VALIDATOR",
        repository_path="scripts/definitely-missing-delivery-validator.py",
        git_blob_sha1="0" * 40,
    )
    validation = validate_delivery_evidence_index(index, ROOT)
    assert not validation.passed
    assert "EV008-VALIDATOR: repository path missing" in validation.violations


def test_wrong_frozen_report_sha_is_rejected() -> None:
    index = _replace(_valid_index(), "EV011-RESULT", canonical_sha256="0" * 64)
    validation = validate_delivery_evidence_index(index, ROOT)
    assert not validation.passed
    assert "EV011-RESULT: canonical report SHA-256 mismatch" in validation.violations


def test_c4_cannot_be_relabelled_as_provider_free_reproducible() -> None:
    index = _replace(
        _valid_index(),
        "C4-SCORE-ROW-ARTIFACT",
        reproduction_status="PROVIDER_FREE_REPRODUCIBLE",
    )
    validation = validate_delivery_evidence_index(index, ROOT)
    assert not validation.passed
    assert "C4-SCORE-ROW-ARTIFACT: must remain EXTERNALLY_BLOCKED" in validation.violations


def test_live_provider_plan_cannot_be_relabelled_as_reproduced() -> None:
    index = _replace(
        _valid_index(),
        "PROVIDER-COMPARISON-PLAN",
        reproduction_status="PROVIDER_FREE_REPRODUCIBLE",
    )
    validation = validate_delivery_evidence_index(index, ROOT)
    assert not validation.passed
    assert "PROVIDER-COMPARISON-PLAN: live execution must remain UNEXECUTED_GATED" in validation.violations


def test_wrong_adr_path_is_rejected() -> None:
    index = _replace(
        _valid_index(),
        "ADR-015",
        repository_path=ADR_PATHS[14],
        git_blob_sha1=git_blob_sha1(ROOT / ADR_PATHS[14]),
    )
    validation = validate_delivery_evidence_index(index, ROOT)
    assert not validation.passed
    assert "ADR-015: canonical ADR path mismatch" in validation.violations


def test_duplicate_evidence_ids_are_rejected_by_schema() -> None:
    valid = _valid_index()
    with pytest.raises(ValueError, match="unique"):
        EvidenceIndex(entries=valid.entries + (valid.entries[0],))
