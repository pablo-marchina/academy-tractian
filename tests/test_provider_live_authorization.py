from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/research/validate_provider_live_authorization.py"
SPEC = importlib.util.spec_from_file_location("provider_live_authorization_validator", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def _payloads():
    return (
        validator.load_json(validator.AUTH_PATH),
        validator.load_json(validator.DESIGN_PATH),
        validator.load_json(validator.POPULATION_PATH),
    )


def test_live_authorization_packet_validates_provider_free() -> None:
    result = validator.run()
    assert result["status"] == "PASS_PROVIDER_FREE_LIVE_AUTHORIZATION_PACKET"
    assert result["max_future_live_calls"] == 32
    assert result["live_calls_executed"] == 0
    assert result["provider_model_selected"] is False
    assert result["scientific_gate_changed"] is False


def test_call_budget_tampering_fails_closed() -> None:
    authorization, design, population = _payloads()
    authorization = deepcopy(authorization)
    authorization["authorization"]["max_live_provider_calls_total"] = 33
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)


def test_retry_or_fallback_tampering_fails_closed() -> None:
    authorization, design, population = _payloads()
    authorization = deepcopy(authorization)
    authorization["authorization"]["automatic_retries"] = 1
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)

    authorization, design, population = _payloads()
    authorization = deepcopy(authorization)
    authorization["authorization"]["provider_fallbacks"] = 1
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)


def test_consumed_live_call_or_selection_claim_fails_closed() -> None:
    authorization, design, population = _payloads()
    authorization = deepcopy(authorization)
    authorization["production_live_calls_executed_by_issue_35"] = 1
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)

    authorization, design, population = _payloads()
    authorization = deepcopy(authorization)
    authorization["production_provider_model_selected"] = True
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)


def test_no_selection_removal_fails_closed() -> None:
    authorization, design, population = _payloads()
    design = deepcopy(design)
    design["selection_rule"]["allowed_outcomes"] = ["candidate_id"]
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)


def test_private_or_blind_population_tampering_fails_closed() -> None:
    authorization, design, population = _payloads()
    population = deepcopy(population)
    population["boundaries"]["uses_private_oracle"] = True
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)

    authorization, design, population = _payloads()
    population = deepcopy(population)
    population["boundaries"]["uses_fresh_blind"] = True
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)


def test_provider_client_blob_tampering_fails_closed() -> None:
    authorization, design, population = _payloads()
    authorization = deepcopy(authorization)
    authorization["validated_provider_client_implementation"]["provider_clients_git_blob"] = "0" * 40
    with pytest.raises(AssertionError):
        validator.validate_payload(authorization, design, population)


def test_authorization_stays_ineffective_before_adr_009() -> None:
    authorization, _, _ = _payloads()
    assert authorization["status"] == "AUTHORIZATION_PACKET_CANDIDATE_INEFFECTIVE_UNTIL_ADR_009"
    assert authorization["becomes_effective_only_when"]["adr_status"] == "ACCEPTED"
    assert authorization["production_live_calls_executed_by_issue_35"] == 0
