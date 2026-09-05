from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from academy_tractian.deployment_feasibility import (
    DeploymentFeasibilityPolicy,
    build_deployment_feasibility_evidence,
    decide_deployment_feasibility,
    decide_deployment_feasibility_set,
)


NOW = datetime(2026, 9, 4, 20, 0, tzinfo=UTC)
SOURCE_HASH = "1" * 64
POLICY = DeploymentFeasibilityPolicy(
    max_evidence_age_days=7,
    require_hosted_service=True,
    max_required_local_components=0,
    require_zero_cost_guardrail=True,
    allowed_runtime_maturities=("ga",),
    require_dockerfile_compatibility=True,
    require_python_3_11_compatibility=True,
    require_outbound_https=True,
    require_managed_postgres_connectivity=True,
    require_streaming_http=True,
    forbid_persistent_local_disk_requirement=True,
    reject_provider_discouraged_production=True,
    allowed_migration_classes=("none", "minor"),
)


def _evidence(**overrides):
    payload = {
        "candidate_id": "test-host",
        "collected_at": NOW - timedelta(hours=1),
        "source_manifest_sha256": SOURCE_HASH,
        "hosted_service": True,
        "required_local_components": 0,
        "zero_cost_guardrail": "yes",
        "runtime_maturity": "ga",
        "dockerfile_compatible": "yes",
        "python_3_11_compatible": "yes",
        "outbound_https_supported": "yes",
        "managed_postgres_connectivity": "yes",
        "streaming_http_supported": "yes",
        "persistent_local_disk_required": False,
        "provider_explicitly_discourages_production": "no",
        "migration_class": "none",
        "published_compute_limit": None,
        "published_memory_limit": None,
    }
    payload.update(overrides)
    return build_deployment_feasibility_evidence(**payload)


def test_fully_compatible_host_is_only_pilot_admissible_not_promoted() -> None:
    decision = decide_deployment_feasibility(
        evidence=_evidence(), policy=POLICY, evaluated_at=NOW
    )
    assert decision.outcome == "PILOT_ADMISSIBLE"
    assert decision.reason_codes == ()


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"hosted_service": False}, "HOSTED_SERVICE_REQUIRED"),
        ({"required_local_components": 1}, "LOCAL_COMPONENT_LIMIT_EXCEEDED"),
        ({"zero_cost_guardrail": "no"}, "ZERO_COST_GUARDRAIL_REQUIRED"),
        ({"zero_cost_guardrail": "unknown"}, "ZERO_COST_GUARDRAIL_UNKNOWN"),
        ({"runtime_maturity": "beta"}, "RUNTIME_MATURITY_NOT_ALLOWED"),
        ({"dockerfile_compatible": "no"}, "DOCKERFILE_COMPATIBILITY_REQUIRED"),
        ({"python_3_11_compatible": "no"}, "PYTHON_3_11_COMPATIBILITY_REQUIRED"),
        ({"outbound_https_supported": "unknown"}, "OUTBOUND_HTTPS_UNKNOWN"),
        (
            {"managed_postgres_connectivity": "unknown"},
            "MANAGED_POSTGRES_CONNECTIVITY_UNKNOWN",
        ),
        ({"streaming_http_supported": "no"}, "STREAMING_HTTP_REQUIRED"),
        ({"persistent_local_disk_required": True}, "PERSISTENT_LOCAL_DISK_FORBIDDEN"),
        (
            {"provider_explicitly_discourages_production": "yes"},
            "PROVIDER_DISCOURAGES_PRODUCTION",
        ),
        (
            {"provider_explicitly_discourages_production": "unknown"},
            "PRODUCTION_SUITABILITY_UNKNOWN",
        ),
        ({"migration_class": "major"}, "MIGRATION_CLASS_NOT_ALLOWED"),
    ],
)
def test_each_hard_constraint_is_non_compensatory(overrides, reason: str) -> None:
    decision = decide_deployment_feasibility(
        evidence=_evidence(**overrides), policy=POLICY, evaluated_at=NOW
    )
    assert decision.outcome == "STATIC_REJECT"
    assert reason in decision.reason_codes


def test_stale_and_future_research_fail_closed() -> None:
    stale = decide_deployment_feasibility(
        evidence=_evidence(collected_at=NOW - timedelta(days=8)),
        policy=POLICY,
        evaluated_at=NOW,
    )
    future = decide_deployment_feasibility(
        evidence=_evidence(collected_at=NOW + timedelta(seconds=1)),
        policy=POLICY,
        evaluated_at=NOW,
    )
    assert stale.reason_codes == ("EVIDENCE_STALE",)
    assert future.reason_codes == ("EVIDENCE_FROM_FUTURE",)


def test_evidence_is_hash_bound() -> None:
    evidence = _evidence()
    payload = evidence.model_dump(mode="json")
    payload["zero_cost_guardrail"] = "no"
    with pytest.raises(ValidationError, match="deployment_feasibility_artifact_hash_mismatch"):
        type(evidence).model_validate(payload)


def test_duplicate_candidates_are_rejected() -> None:
    item = _evidence()
    with pytest.raises(ValueError, match="duplicate_candidate_evidence"):
        decide_deployment_feasibility_set(
            evidence=(item, item), policy=POLICY, evaluated_at=NOW
        )
