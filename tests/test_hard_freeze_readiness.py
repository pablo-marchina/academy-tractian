from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from academy_tractian.hard_freeze_readiness import (
    HARD_FREEZE_NOT_BEFORE_UTC,
    HardFreezeReadinessObservation,
    HardFreezeReadinessReport,
    evaluate_hard_freeze_readiness,
    extract_classic_required_status_contexts,
    extract_ruleset_required_status_contexts,
    ruleset_targets_main,
)


CANDIDATE = "3c0eb98054d9d67c52ba821b0e7329b4544f30e7"
MANIFEST = "bd3d4df0cb74b88f602b371873c89ff22db49c355a472568783b41a37af5a793"


def _observation(**overrides) -> HardFreezeReadinessObservation:
    values = {
        "candidate_sha": CANDIDATE,
        "observed_main_sha": CANDIDATE,
        "observed_at_utc": datetime(2026, 9, 6, 3, 5, tzinfo=timezone.utc),
        "branch_protected": True,
        "required_status_contexts": ("required-gate",),
        "final_ci_run_id": 33835290807,
        "final_ci_head_sha": CANDIDATE,
        "final_ci_conclusion": "success",
        "required_gate_conclusion": "success",
        "bundle_manifest_sha256": MANIFEST,
        "bundle_validation_failures": (),
    }
    values.update(overrides)
    return HardFreezeReadinessObservation(**values)


def _ruleset(*, includes=None, excludes=None, enforcement="active", checks=None):
    return {
        "id": 42,
        "target": "branch",
        "enforcement": enforcement,
        "conditions": {
            "ref_name": {
                "include": includes or ["~DEFAULT_BRANCH"],
                "exclude": excludes or [],
            }
        },
        "rules": [
            {
                "type": "required_status_checks",
                "parameters": {
                    "required_status_checks": checks
                    or [{"context": "required-gate", "integration_id": 1}],
                    "strict_required_status_checks_policy": True,
                },
            }
        ],
    }


def test_ready_attestation_is_hash_bound_and_never_activates_freeze() -> None:
    report = evaluate_hard_freeze_readiness(_observation())

    assert report.status == "READY_FOR_ACTIVATION"
    assert report.hard_freeze_effective is False
    assert report.production_readiness_claim_ready is False
    assert report.blockers == ()
    assert report.freeze_not_before_utc == HARD_FREEZE_NOT_BEFORE_UTC
    assert len(report.evidence_sha256) == 64

    exported = report.model_dump(mode="json")
    for forbidden_key in (
        "token",
        "authorization",
        "identity",
        "user_id",
        "organization_id",
        "raw_trace",
        "arguments",
    ):
        assert forbidden_key not in exported


def test_readiness_fails_closed_before_window_or_without_protection() -> None:
    report = evaluate_hard_freeze_readiness(
        _observation(
            observed_at_utc=datetime(2026, 9, 5, 23, 59, tzinfo=timezone.utc),
            branch_protected=False,
            required_status_contexts=(),
        )
    )

    assert report.status == "BLOCKED"
    assert report.hard_freeze_effective is False
    assert "freeze_window_not_open" in report.blockers
    assert "branch_protection_not_enforced" in report.blockers
    assert "required_gate_not_required" in report.blockers


def test_readiness_blocks_sha_or_final_ci_mismatch() -> None:
    other_sha = "1" * 40
    report = evaluate_hard_freeze_readiness(
        _observation(
            observed_main_sha=other_sha,
            final_ci_head_sha=other_sha,
            final_ci_conclusion="failure",
            required_gate_conclusion="failure",
        )
    )

    assert report.status == "BLOCKED"
    assert "main_sha_mismatch" in report.blockers
    assert "final_ci_not_success_on_candidate" in report.blockers
    assert "required_gate_not_success" in report.blockers


def test_readiness_blocks_bundle_validation_failure() -> None:
    report = evaluate_hard_freeze_readiness(
        _observation(bundle_validation_failures=("artifact_2_blob_mismatch",))
    )

    assert report.status == "BLOCKED"
    assert report.bundle_validation_failure_count == 1
    assert "final_bundle_validation_failed" in report.blockers


def test_report_rejects_hash_tampering() -> None:
    report = evaluate_hard_freeze_readiness(_observation())
    payload = report.model_dump(mode="json")
    payload["branch_protected"] = False

    with pytest.raises(ValidationError, match="hard freeze readiness hash mismatch"):
        HardFreezeReadinessReport.model_validate(payload)


def test_naive_observation_time_is_rejected() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        _observation(observed_at_utc=datetime(2026, 9, 6, 3, 5))


def test_classic_branch_protection_contexts_are_extracted() -> None:
    branch = {
        "protection": {
            "required_status_checks": {
                "contexts": ["required-gate", "lint"],
                "checks": [{"context": "required-gate"}, {"context": "unit"}],
            }
        }
    }
    assert extract_classic_required_status_contexts(branch) == (
        "lint",
        "required-gate",
        "unit",
    )


def test_active_default_branch_ruleset_exposes_required_gate() -> None:
    ruleset = _ruleset()
    assert ruleset_targets_main(ruleset) is True
    assert extract_ruleset_required_status_contexts((ruleset,)) == ("required-gate",)


def test_ruleset_exact_and_glob_main_patterns_are_supported() -> None:
    exact = _ruleset(includes=["refs/heads/main"])
    globbed = _ruleset(includes=["refs/heads/m*"])
    assert ruleset_targets_main(exact) is True
    assert ruleset_targets_main(globbed) is True


def test_ruleset_exclusion_or_nonactive_enforcement_fails_closed() -> None:
    excluded = _ruleset(includes=["~ALL"], excludes=["refs/heads/main"])
    evaluate_only = _ruleset(enforcement="evaluate")
    assert ruleset_targets_main(excluded) is False
    assert ruleset_targets_main(evaluate_only) is False
    assert extract_ruleset_required_status_contexts((excluded, evaluate_only)) == ()


def test_non_status_rules_do_not_manufacture_required_contexts() -> None:
    ruleset = _ruleset()
    ruleset["rules"] = [{"type": "non_fast_forward"}, {"type": "pull_request"}]
    assert ruleset_targets_main(ruleset) is True
    assert extract_ruleset_required_status_contexts((ruleset,)) == ()
