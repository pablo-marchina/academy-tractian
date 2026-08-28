from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "research" / "validate_provider_model_comparison_design.py"
MANIFEST_PATH = ROOT / "research" / "experiments" / "provider-model-comparison-design-manifest-v1.json"
POPULATION_PATH = ROOT / "research" / "experiments" / "provider-model-comparison-dev-population-v1.json"

SPEC = importlib.util.spec_from_file_location("provider_comparison_validator", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _clear_provider_envs(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in validator.FORBIDDEN_PROVIDER_ENVS:
        monkeypatch.delenv(name, raising=False)


def test_frozen_design_validates_provider_free(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_envs(monkeypatch)
    result = validator.run(MANIFEST_PATH, POPULATION_PATH)
    assert result["status"] == "PASS"
    assert result["provider_calls_executed"] == 0
    assert result["provider_calls_authorized"] == 0
    assert result["live_candidate_count"] == 2
    assert result["population_units"] == 8
    assert result["max_future_live_calls"] == 32
    assert result["metrics"] == [f"M{i}" for i in range(1, 11)]
    assert result["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"


def test_validator_rejects_provider_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_envs(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-used")
    with pytest.raises(AssertionError, match="provider credentials"):
        validator.run(MANIFEST_PATH, POPULATION_PATH)


def test_validator_rejects_population_tamper(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_envs(monkeypatch)
    population = _load(POPULATION_PATH)
    population["units"][0]["context"]["user_request"] = "tampered"
    tampered_population = tmp_path / "population.json"
    _write_json(tampered_population, population)

    manifest = _load(MANIFEST_PATH)
    manifest["population"]["path"] = str(tampered_population).replace("\\", "/")
    tampered_manifest = tmp_path / "manifest.json"
    _write_json(tampered_manifest, manifest)

    with pytest.raises(AssertionError):
        validator.run(tampered_manifest, tampered_population)


def test_validator_rejects_live_call_budget_change(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_envs(monkeypatch)
    manifest = _load(MANIFEST_PATH)
    manifest["execution"]["max_live_provider_calls_total"] = 33
    manifest["population"]["path"] = str(POPULATION_PATH).replace("\\", "/")
    path = tmp_path / "manifest.json"
    _write_json(path, manifest)
    with pytest.raises(AssertionError):
        validator.run(path, POPULATION_PATH)


def test_validator_requires_no_selection_outcome(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_envs(monkeypatch)
    manifest = _load(MANIFEST_PATH)
    manifest["selection_rule"]["allowed_outcomes"] = ["candidate_id"]
    manifest["selection_rule"]["step_2"] = "If no live candidate remains, stop."
    manifest["selection_rule"]["step_8"] = "If unresolved, stop."
    manifest["population"]["path"] = str(POPULATION_PATH).replace("\\", "/")
    path = tmp_path / "manifest.json"
    _write_json(path, manifest)
    with pytest.raises(AssertionError):
        validator.run(path, POPULATION_PATH)


def test_population_contains_only_public_synthetic_probe_identity() -> None:
    population = _load(POPULATION_PATH)
    serialized = json.dumps(population, sort_keys=True)
    assert "asset_dev_probe_" in serialized
    assert "expected-paths" not in serialized
    assert "LOCKED_TEST" not in serialized
    assert population["boundaries"]["uses_private_oracle"] is False
    assert population["boundaries"]["uses_historical_real_task_quality"] is False
