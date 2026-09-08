from __future__ import annotations

import json
from pathlib import Path

import pytest

from academy_tractian.cloudflare_workers_plan_probe import probe_workers_plan
from academy_tractian.provider_budget_transport import BudgetGatedProviderJsonTransport
from academy_tractian.provider_clients import ProviderHttpRequest, ProviderHttpResponse
from academy_tractian.provider_tournament_v3 import CANDIDATE_IDS, POPULATION_SHA256
from academy_tractian.provider_tournament_v3_analysis import analyze_tournament


class _Gate:
    def __init__(self, *, blocked: bool = False) -> None:
        self.blocked = blocked
        self.calls = 0

    def assert_provider_available(self) -> None:
        self.calls += 1
        if self.blocked:
            raise RuntimeError("blocked")


class _Transport:
    def __init__(self) -> None:
        self.calls = 0

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls += 1
        return ProviderHttpResponse(status_code=200, headers={}, body={"ok": True})


def test_budget_transport_checks_gate_before_network() -> None:
    gate = _Gate(blocked=True)
    inner = _Transport()
    transport = BudgetGatedProviderJsonTransport(gate=gate, inner=inner)  # type: ignore[arg-type]
    request = ProviderHttpRequest(method="POST", url="https://example.test", headers={}, body={})
    with pytest.raises(RuntimeError, match="blocked"):
        transport.post_json(request)
    assert gate.calls == 1
    assert inner.calls == 0


def test_workers_plan_probe_requires_readable_free_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = iter([
        {"success": True, "result": {"default_usage_model": "bundled"}},
        {"success": True, "result": []},
    ])
    monkeypatch.setattr(
        "academy_tractian.cloudflare_workers_plan_probe._get_json",
        lambda **_kwargs: next(responses),
    )
    evidence = probe_workers_plan(api_token="token", account_id="account")
    assert evidence.state == "WORKERS_FREE"
    assert evidence.workers_paid_detected is False
    assert evidence.raw_response_recorded is False
    assert evidence.provider_inference_used is False


def test_workers_plan_probe_detects_paid_signal(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = iter([
        {"success": True, "result": {"default_usage_model": "standard"}},
        {"success": True, "result": [{"name": "Workers Paid"}]},
    ])
    monkeypatch.setattr(
        "academy_tractian.cloudflare_workers_plan_probe._get_json",
        lambda **_kwargs: next(responses),
    )
    evidence = probe_workers_plan(api_token="token", account_id="account")
    assert evidence.state == "WORKERS_PAID"
    assert evidence.workers_paid_detected is True


def _attempt(candidate: str, repetition: int, unit_index: int, quality: bool) -> dict:
    model = (
        "@cf/zai-org/glm-4.7-flash"
        if candidate == CANDIDATE_IDS[0]
        else "@cf/nvidia/nemotron-3-120b-a12b"
    )
    return {
        "candidate_id": candidate,
        "model_id": model,
        "unit_id": f"U-{unit_index}",
        "unit_index": unit_index,
        "repetition_index": repetition,
        "outcome": "success",
        "decision_kind": "FINAL",
        "tool_name": None,
        "trace_integrity": True,
        "raw_provider_material_recorded": False,
        "identity_seed_attempt": False,
        "private_key_attempt": False,
        "rubric_pass": quality,
        "neurons": 1.0,
    }


def _packets(tmp_path: Path, *, a_quality, b_quality) -> list[Path]:
    paths: list[Path] = []
    for repetition in range(5):
        attempts = []
        for unit in range(17):
            attempts.append(_attempt(CANDIDATE_IDS[0], repetition, unit, a_quality(unit, repetition)))
            attempts.append(_attempt(CANDIDATE_IDS[1], repetition, unit, b_quality(unit, repetition)))
        packet = {
            "schema_version": "provider-tournament-v3-packet-v1",
            "repetition_index": repetition,
            "population_sha256": POPULATION_SHA256,
            "attempt_count": 34,
            "attempts": attempts,
            "packet_observed_neurons": 34.0,
            "available_free_neurons_at_start": 10000.0,
            "actual_cash_cost_usd": 0.0,
            "complete": True,
            "raw_provider_material_recorded": False,
        }
        path = tmp_path / f"packet-{repetition}.json"
        path.write_text(json.dumps(packet), encoding="utf-8")
        paths.append(path)
    return paths


def test_hierarchical_analysis_promotes_clear_quality_winner(tmp_path: Path) -> None:
    paths = _packets(
        tmp_path,
        a_quality=lambda _u, _r: True,
        b_quality=lambda u, _r: u >= 4,
    )
    result = analyze_tournament(paths)
    assert result["selection"] == f"PROMOTE:{CANDIDATE_IDS[0]}"
    assert result["selection_reason"] == "CONFIDENT_MATERIAL_PRIMARY_QUALITY_ADVANTAGE"
    assert result["bootstrap"]["ci_low"] > 0


def test_hierarchical_analysis_is_inconclusive_on_primary_tie(tmp_path: Path) -> None:
    paths = _packets(
        tmp_path,
        a_quality=lambda u, r: (u + r) % 2 == 0,
        b_quality=lambda u, r: (u + r) % 2 == 0,
    )
    result = analyze_tournament(paths)
    assert result["selection"] == "INCONCLUSIVE"
    assert result["selection_reason"] == "PRIMARY_NOT_CONFIDENTLY_MATERIAL_AND_M06_NOT_INDEPENDENTLY_SCOREABLE"
