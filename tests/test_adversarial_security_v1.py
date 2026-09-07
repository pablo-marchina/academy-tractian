from __future__ import annotations

from scripts.research.validate_adversarial_security_v1 import run


def test_adversarial_security_v1_preregistration_is_provider_free_and_fail_closed() -> None:
    result = run()

    assert result == {
        "schema_version": "adversarial-security-v1-validation",
        "status": "PREREGISTRATION_VALID",
        "source_case_count": 14,
        "hosted_case_count": 7,
        "hard_gate_count": 12,
        "source_artifact_count": 7,
        "provider_calls_authorized": 0,
        "real_tractian_calls_authorized": 0,
        "production_actions_authorized": 0,
        "hosted_security_probes_authorized": 0,
        "cash_cost_usd_authorized": 0,
        "automatic_promotion": False,
        "hosted_security_claim_ready": False,
    }
