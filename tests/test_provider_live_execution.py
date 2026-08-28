from __future__ import annotations

import json
from pathlib import Path

import pytest

import academy_tractian.provider_live_execution as live
from academy_tractian.provider_clients import (
    GoogleInteractionsDecisionClient,
    OpenAIResponsesDecisionClient,
)
from academy_tractian.provider_comparison import (
    ProviderComparisonAttempt,
    build_provider_comparison_plan,
)


OPENAI_ID = "openai_gpt_5_6_sol_responses_standard"
GOOGLE_ID = "google_gemini_3_7_flash_interactions_stateless"


def _secrets() -> live.LiveProviderSecrets:
    return live.LiveProviderSecrets(
        openai_api_key="openai-test-secret-never-serialize",
        google_api_key="google-test-secret-never-serialize",
    )


def _attempt(entry) -> ProviderComparisonAttempt:
    return ProviderComparisonAttempt(
        fixture_result=False,
        attempt_index=entry.attempt_index,
        candidate_id=entry.candidate_id,
        unit_id=entry.unit_id,
        repeat_index=entry.repeat_index,
        request_sha256="0" * 64,
        call_id="1" * 64,
        outcome="success",
        decision_kind="ABSTAIN",
        tool_name=None,
        failure_code=None,
        latency_ms=1,
        input_tokens=1,
        output_tokens=1,
        total_tokens=2,
        reasoning_tokens=None,
        structured_decision_adherent=True,
        known_tool_selection_valid=None,
        b1_valid=None,
        b1_issue_codes=(),
        identity_seed_attempt=False,
        private_key_attempt=False,
        rubric_pass=True,
        trace_integrity=True,
        trace_issue_codes=(),
        safe_failure_contained=None,
        raw_material_recorded=False,
    )


class _FakeProviderResult:
    selection = "NO_SELECTION"

    def model_dump(self, *, mode: str):
        assert mode == "json"
        return {
            "schema_version": "fake-provider-result-v1",
            "selection": self.selection,
        }


class _LedgerCheckingExecutor:
    def __init__(self, *, bundle, clients, fixture_result, ledger_path: Path):
        assert fixture_result is False
        self.plan = build_provider_comparison_plan(bundle)
        self.ledger_path = ledger_path
        self.index = 0
        self.stopped = False
        self.stop_reason = None

    def execute_next(self):
        entry = self.plan.entries[self.index]
        persisted = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        assert persisted["entries"][entry.attempt_index]["state"] == "claimed"
        self.index += 1
        return _attempt(entry)

    def finalize(self, *, fixed_failure_probe_passed):
        assert fixed_failure_probe_passed == {OPENAI_ID: True, GOOGLE_ID: True}
        return _FakeProviderResult()


class _ExplodingExecutor(_LedgerCheckingExecutor):
    def execute_next(self):
        entry = self.plan.entries[self.index]
        persisted = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        assert persisted["entries"][entry.attempt_index]["state"] == "claimed"
        raise RuntimeError("raw internal detail that must never be persisted")


def test_secret_presence_fails_before_run_directory_creation(tmp_path: Path) -> None:
    run_dir = tmp_path / "live-run"
    with pytest.raises(live.MissingProviderSecretsError, match="OPENAI_API_KEY"):
        live.GovernedLiveProviderComparison.prepare(
            run_dir=run_dir,
            secrets=live.LiveProviderSecrets(
                openai_api_key="",
                google_api_key="google-present",
            ),
        )
    assert not run_dir.exists()


def test_secret_repr_is_redacted() -> None:
    secrets = _secrets()
    rendered = repr(secrets)
    assert secrets.openai_api_key not in rendered
    assert secrets.google_api_key not in rendered
    assert "<redacted>" in rendered


def test_prepare_creates_exact_sanitized_ledger_without_network(tmp_path: Path) -> None:
    run_dir = tmp_path / "live-run"
    secrets = _secrets()
    prepared = live.GovernedLiveProviderComparison.prepare(
        run_dir=run_dir,
        secrets=secrets,
    )

    assert prepared.plan.plan_sha256 == live.EXPECTED_PLAN_SHA256
    payload = json.loads((run_dir / live.LEDGER_FILENAME).read_text(encoding="utf-8"))
    assert payload["state"] == "prepared"
    assert len(payload["entries"]) == 32
    assert [item["attempt_index"] for item in payload["entries"]] == list(range(32))
    serialized = json.dumps(payload, sort_keys=True)
    assert secrets.openai_api_key not in serialized
    assert secrets.google_api_key not in serialized
    assert not (run_dir / live.RESULT_FILENAME).exists()


def test_existing_run_directory_refuses_resume_or_budget_reset(tmp_path: Path) -> None:
    run_dir = tmp_path / "live-run"
    live.GovernedLiveProviderComparison.prepare(run_dir=run_dir, secrets=_secrets())
    with pytest.raises(live.ExistingLiveRunError, match="refusing resume"):
        live.GovernedLiveProviderComparison.prepare(run_dir=run_dir, secrets=_secrets())


def test_fixed_failure_probes_are_provider_free_and_pass() -> None:
    bundle = live.load_frozen_provider_comparison_bundle(Path("."))
    assert live.run_provider_free_fixed_failure_probes(bundle) == {
        OPENAI_ID: True,
        GOOGLE_ID: True,
    }


def test_exact_live_client_construction_does_not_call_network_and_redacts_keys() -> None:
    secrets = _secrets()
    clients = live._build_exact_live_clients(secrets)
    assert type(clients[OPENAI_ID]) is OpenAIResponsesDecisionClient
    assert type(clients[GOOGLE_ID]) is GoogleInteractionsDecisionClient
    assert secrets.openai_api_key not in repr(clients[OPENAI_ID])
    assert secrets.google_api_key not in repr(clients[GOOGLE_ID])


def test_execute_all_claims_durably_before_every_invocation(monkeypatch, tmp_path: Path) -> None:
    run_dir = tmp_path / "live-run"
    prepared = live.GovernedLiveProviderComparison.prepare(
        run_dir=run_dir,
        secrets=_secrets(),
    )
    ledger_path = run_dir / live.LEDGER_FILENAME

    monkeypatch.setattr(
        live,
        "run_provider_free_fixed_failure_probes",
        lambda bundle: {OPENAI_ID: True, GOOGLE_ID: True},
    )
    monkeypatch.setattr(live, "_build_exact_live_clients", lambda secrets: {})
    monkeypatch.setattr(
        live,
        "ProviderComparisonExecutor",
        lambda **kwargs: _LedgerCheckingExecutor(
            **kwargs,
            ledger_path=ledger_path,
        ),
    )

    result = prepared.execute_all()
    assert result.state == "complete"
    assert result.completed_attempts == 32
    assert result.consumed_or_uncertain_attempts == 32
    assert result.selection == "NO_SELECTION"

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["state"] == "complete"
    assert all(item["state"] == "completed" for item in ledger["entries"])
    assert (run_dir / live.RESULT_FILENAME).exists()


def test_exception_after_claim_is_uncertain_sanitized_and_not_resumable(
    monkeypatch,
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "live-run"
    prepared = live.GovernedLiveProviderComparison.prepare(
        run_dir=run_dir,
        secrets=_secrets(),
    )
    ledger_path = run_dir / live.LEDGER_FILENAME

    monkeypatch.setattr(
        live,
        "run_provider_free_fixed_failure_probes",
        lambda bundle: {OPENAI_ID: True, GOOGLE_ID: True},
    )
    monkeypatch.setattr(live, "_build_exact_live_clients", lambda secrets: {})
    monkeypatch.setattr(
        live,
        "ProviderComparisonExecutor",
        lambda **kwargs: _ExplodingExecutor(
            **kwargs,
            ledger_path=ledger_path,
        ),
    )

    with pytest.raises(live.LiveExecutionStopped, match="EXECUTOR_INTERNAL_FAILURE"):
        prepared.execute_all()

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["state"] == "stopped"
    assert ledger["entries"][0]["state"] == "uncertain"
    assert ledger["entries"][0]["stop_code"] == "EXECUTOR_INTERNAL_FAILURE"
    serialized_ledger = json.dumps(ledger, sort_keys=True)
    assert "raw internal detail" not in serialized_ledger

    result = json.loads((run_dir / live.RESULT_FILENAME).read_text(encoding="utf-8"))
    assert result["selection"] == "NO_SELECTION"
    assert result["consumed_or_uncertain_attempts"] == 1
    serialized_result = json.dumps(result, sort_keys=True)
    assert "raw internal detail" not in serialized_result

    with pytest.raises(live.ExistingLiveRunError):
        live.GovernedLiveProviderComparison.prepare(run_dir=run_dir, secrets=_secrets())
