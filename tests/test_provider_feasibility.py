from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from academy_tractian.provider_feasibility import (
    ProviderFeasibilityPolicy,
    build_provider_feasibility_evidence,
    decide_provider_feasibility,
    decide_provider_feasibility_set,
)


NOW = datetime(2026, 9, 4, 19, 30, tzinfo=UTC)
SOURCE_HASH = "1" * 64
POLICY = ProviderFeasibilityPolicy(
    max_evidence_age_days=7,
    allowed_model_maturities=("ga",),
    allowed_api_maturities=("ga",),
    require_hosted_service=True,
    max_required_local_components=0,
    require_zero_cost_execution=True,
    require_structured_output=True,
    min_free_requests_per_day=100,
    min_free_tokens_per_day=100_000,
)


def _evidence(candidate_id: str = "groq:openai/gpt-oss-120b", **overrides):
    payload = {
        "candidate_id": candidate_id,
        "collected_at": NOW - timedelta(hours=1),
        "source_manifest_sha256": SOURCE_HASH,
        "hosted_service": True,
        "required_local_components": 0,
        "zero_cost_execution_status": "available",
        "metered_input_usd_per_million": 0.15,
        "metered_output_usd_per_million": 0.60,
        "structured_output_supported": True,
        "free_requests_per_day": 1000,
        "free_tokens_per_day": 200_000,
    }
    payload.update(overrides)
    return build_provider_feasibility_evidence(**payload)


def test_eligible_means_only_hard_constraints_passed_not_quality_promotion() -> None:
    decision = decide_provider_feasibility(
        evidence=_evidence(),
        policy=POLICY,
        evaluated_at=NOW,
    )
    assert decision.outcome == "ELIGIBLE"
    assert decision.reason_codes == ()
    assert decision.candidate_id == "groq:openai/gpt-oss-120b"
    assert decision.model_maturity == "ga"
    assert decision.api_maturity == "ga"


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"hosted_service": False}, "HOSTED_SERVICE_REQUIRED"),
        ({"required_local_components": 1}, "LOCAL_COMPONENT_LIMIT_EXCEEDED"),
        ({"zero_cost_execution_status": "unavailable"}, "ZERO_COST_EXECUTION_REQUIRED"),
        ({"zero_cost_execution_status": "unknown"}, "ZERO_COST_EXECUTION_UNKNOWN"),
        ({"structured_output_supported": False}, "STRUCTURED_OUTPUT_REQUIRED"),
        ({"free_requests_per_day": 99}, "FREE_REQUEST_CAPACITY_INSUFFICIENT"),
        ({"free_tokens_per_day": 99_999}, "FREE_TOKEN_CAPACITY_INSUFFICIENT"),
        ({"free_requests_per_day": None}, "FREE_REQUEST_CAPACITY_UNKNOWN"),
        ({"free_tokens_per_day": None}, "FREE_TOKEN_CAPACITY_UNKNOWN"),
    ],
)
def test_each_hard_constraint_is_non_compensatory(overrides, reason: str) -> None:
    decision = decide_provider_feasibility(
        evidence=_evidence(**overrides),
        policy=POLICY,
        evaluated_at=NOW,
    )
    assert decision.outcome == "INELIGIBLE"
    assert reason in decision.reason_codes


def test_metered_price_is_recorded_but_does_not_override_a_valid_free_path() -> None:
    decision = decide_provider_feasibility(
        evidence=_evidence(
            zero_cost_execution_status="available",
            metered_input_usd_per_million=999.0,
            metered_output_usd_per_million=999.0,
        ),
        policy=POLICY,
        evaluated_at=NOW,
    )
    assert decision.outcome == "ELIGIBLE"


def test_stale_and_future_evidence_fail_closed() -> None:
    stale = decide_provider_feasibility(
        evidence=_evidence(collected_at=NOW - timedelta(days=8)),
        policy=POLICY,
        evaluated_at=NOW,
    )
    future = decide_provider_feasibility(
        evidence=_evidence(collected_at=NOW + timedelta(seconds=1)),
        policy=POLICY,
        evaluated_at=NOW,
    )
    assert stale.outcome == "INELIGIBLE"
    assert stale.reason_codes == ("EVIDENCE_STALE",)
    assert future.outcome == "INELIGIBLE"
    assert future.reason_codes == ("EVIDENCE_FROM_FUTURE",)


def test_candidate_identity_is_recomputed_from_code_owned_registry() -> None:
    with pytest.raises(ValueError, match="unsupported_hosted_candidate"):
        decide_provider_feasibility(
            evidence=_evidence(candidate_id="local:ollama"),
            policy=POLICY,
            evaluated_at=NOW,
        )


def test_evidence_integrity_is_hash_bound() -> None:
    evidence = _evidence()
    payload = evidence.model_dump(mode="json")
    payload["zero_cost_execution_status"] = "unknown"
    with pytest.raises(ValidationError, match="provider_feasibility_artifact_hash_mismatch"):
        type(evidence).model_validate(payload)


def test_duplicate_candidate_evidence_is_rejected() -> None:
    item = _evidence()
    with pytest.raises(ValueError, match="duplicate_candidate_evidence"):
        decide_provider_feasibility_set(
            evidence=(item, item),
            policy=POLICY,
            evaluated_at=NOW,
        )


def test_zero_capacity_requirement_does_not_invent_unknown_quota_failure() -> None:
    policy = POLICY.model_copy(
        update={"min_free_requests_per_day": 0, "min_free_tokens_per_day": 0}
    )
    decision = decide_provider_feasibility(
        evidence=_evidence(free_requests_per_day=None, free_tokens_per_day=None),
        policy=policy,
        evaluated_at=NOW,
    )
    assert decision.outcome == "ELIGIBLE"
