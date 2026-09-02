from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import pytest

from academy_tractian.cloudflare_live_authorization_d02_v1 import (
    D01_MAXIMUM_IMPLIED_REMAINING,
    CloudflareD02OperatorAttestationEvidenceV1,
    d02_operator_attestation_to_pre_live_evidence,
    issue_d02_operator_attestation_receipt,
    validate_d02_operator_attestation_evidence,
    validate_d02_operator_attestation_receipt_for_execution,
    validate_frozen_d02_live_authorization,
)
from academy_tractian.cloudflare_live_authorization_v1 import CloudflareAuthorizationError
from academy_tractian.cloudflare_provider_comparison_v2 import load_frozen_cloudflare_comparison_bundle_v2
from academy_tractian.cloudflare_provider_d02 import (
    CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1,
    CloudflareD02PreLiveEvidence,
    build_cloudflare_d02_plan,
)
from academy_tractian.cloudflare_provider_d02_live import (
    D02_LEDGER_FILENAME,
    D02_RUN_DIRNAME,
    CloudflareD02ComparisonExecutorV1,
    CloudflareD02ExistingRunError,
    GovernedCloudflareD02LiveTaskV1,
    build_cloudflare_d02_live_clients,
)
from academy_tractian.cloudflare_provider_live_v2 import CloudflareLiveSecrets
from academy_tractian.provider_clients import ProviderHttpRequest, ProviderHttpResponse

SECRET = "d02-provider-free-secret-never-persist"
ACCOUNT_ID = "0123456789abcdef0123456789abcdef"
RESET = datetime(2026, 9, 3, 0, 0, 0, tzinfo=timezone.utc)
OBSERVED = RESET + timedelta(minutes=3)
RECEIPT_NOW = OBSERVED + timedelta(minutes=1)
EXECUTION_NOW = RECEIPT_NOW + timedelta(seconds=30)


def _decision(kind: str, **kwargs: Any) -> str:
    payload: dict[str, Any] = {"schema_version": "provider-decision-payload-v1", "kind": kind, "tool_name": None, "arguments": {}, "evidence_id": None, "final": None, "message": None, "reason_code": None}
    payload.update(kwargs)
    return json.dumps(payload, sort_keys=True)


def _good_response(text: str) -> str:
    if "asset_dev_probe_001" in text: return _decision("TOOL", tool_name="get_asset", arguments={"asset_id": "asset_dev_probe_001"})
    if "asset_dev_probe_002" in text: return _decision("TOOL", tool_name="list_analyses", arguments={"asset_id": "asset_dev_probe_002"})
    if "asset_dev_probe_003" in text: return _decision("TOOL", tool_name="get_data_quality", arguments={"asset_id": "asset_dev_probe_003"})
    if "BPFO" in text or "bpfo" in text: return _decision("TOOL", tool_name="search_knowledge", arguments={"q": "Explain BPFO", "type": "glossary"})
    if "asset I mentioned" in text: return _decision("CLARIFY", message="Which asset should I investigate?", reason_code="MISSING_ASSET")
    if "human specialist" in text: return _decision("ESCALATE", message="A human specialist should review the case.", reason_code="USER_REQUESTED_HUMAN")
    if "asset_dev_probe_007" in text: return _decision("ABSTAIN", message="The requested signal evidence is unavailable.", reason_code="UPSTREAM_UNAVAILABLE")
    if "analysis_dev_probe_008" in text: return _decision("FINAL", final={"decision": "ORIENT", "response_mode": "complete", "message": "The action remains blocked by policy."})
    raise AssertionError(text)


class GovernedFixtureTransport:
    def __init__(self, custody_root: Path | None = None) -> None:
        self.calls: list[ProviderHttpRequest] = []
        self.custody_root = custody_root

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        if self.custody_root is not None:
            ledger = json.loads((self.custody_root / D02_RUN_DIRNAME / D02_LEDGER_FILENAME).read_text(encoding="utf-8"))
            assert ledger["entries"][len(self.calls)]["state"] == "claimed"
        self.calls.append(request)
        assert request.body["max_completion_tokens"] == 1024
        return ProviderHttpResponse(status_code=200, body={
            "id": f"d02-provider-free-{len(self.calls)}", "object": "chat.completion", "model": request.body["model"],
            "choices": [{"index": 0, "message": {"role": "assistant", "content": _good_response(request.body["messages"][1]["content"])}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        })


class LengthFailureTransport:
    def __init__(self) -> None:
        self.calls: list[ProviderHttpRequest] = []

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls.append(request)
        return ProviderHttpResponse(status_code=200, body={
            "id": "d02-length-provider-free", "object": "chat.completion", "model": request.body["model"],
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "{}"}, "finish_reason": "length"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 1024, "total_tokens": 1124},
        })


def _pre_live(free: float = 10000.0) -> CloudflareD02PreLiveEvidence:
    return CloudflareD02PreLiveEvidence(free_neurons_remaining=free, evidence_source="provider-free-d02-test")


def _evidence() -> CloudflareD02OperatorAttestationEvidenceV1:
    return CloudflareD02OperatorAttestationEvidenceV1(observed_at_utc=OBSERVED, utc_day="2026-09-03", reset_at_utc=RESET)


def test_d02_live_authorization_frozen_and_current_window_is_blocked() -> None:
    protocol = validate_frozen_d02_live_authorization(Path(__file__).resolve().parents[1])
    assert protocol["current_window"]["d02_live_eligible_in_this_window"] is False
    assert D01_MAXIMUM_IMPLIED_REMAINING == pytest.approx(7186.371536)
    with pytest.raises(ValueError, match="D01 already consumed"):
        CloudflareD02OperatorAttestationEvidenceV1(observed_at_utc=datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc), utc_day="2026-09-02", reset_at_utc=datetime(2026, 9, 2, 0, 0, tzinfo=timezone.utc))


def test_d02_start_gate_rejects_current_remaining_and_accepts_exact_bound() -> None:
    with pytest.raises(ValueError): _pre_live(7186.371536)
    with pytest.raises(ValueError): _pre_live(CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1 - 0.000001)
    assert _pre_live(CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1).free_neurons_remaining == pytest.approx(9352.805376)


def test_d02_receipt_is_short_lived_custody_bound_and_maps_to_exact_10000(tmp_path: Path) -> None:
    evidence = _evidence()
    receipt = issue_d02_operator_attestation_receipt(evidence, custody_root=tmp_path / "custody", now_utc=RECEIPT_NOW)
    assert (receipt.expires_at_utc - receipt.issued_at_utc).total_seconds() <= 300
    pre = d02_operator_attestation_to_pre_live_evidence(receipt, evidence, custody_root=tmp_path / "custody", now_utc=EXECUTION_NOW)
    assert pre.free_neurons_remaining == 10000.0
    assert pre.workers_paid_enabled is False
    with pytest.raises(CloudflareAuthorizationError, match="custody root mismatch"):
        validate_d02_operator_attestation_receipt_for_execution(receipt, evidence, custody_root=tmp_path / "other", now_utc=EXECUTION_NOW)
    with pytest.raises(CloudflareAuthorizationError, match="stale"):
        validate_d02_operator_attestation_evidence(evidence, now_utc=OBSERVED + timedelta(seconds=601))


def test_d02_governed_task_runs_32_provider_free_calls_with_write_ahead_claim(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    custody_root = tmp_path / "custody"
    transport = GovernedFixtureTransport(custody_root)
    task = GovernedCloudflareD02LiveTaskV1.prepare(custody_root=custody_root, secrets=CloudflareLiveSecrets(api_token=SECRET, account_id=ACCOUNT_ID), pre_live_evidence=_pre_live(), transport=transport, fixture_result=True, repo_root=repo_root)
    result = task.execute_all()
    assert result.state == "complete"
    assert result.completed_attempts == 32
    assert result.consumed_or_uncertain_attempts == 32
    assert result.actual_cash_cost_usd == 0.0
    assert result.raw_provider_material_recorded is False
    assert result.provider_result is not None
    assert result.provider_result.complete is True
    assert result.provider_result.resource_accounting_complete is True
    assert result.provider_result.completion_token_cap == 1024
    assert len(transport.calls) == 32
    ledger = json.loads((custody_root / D02_RUN_DIRNAME / D02_LEDGER_FILENAME).read_text(encoding="utf-8"))
    assert ledger["state"] == "complete"
    assert all(item["state"] == "completed" for item in ledger["entries"])
    persisted = "\n".join(path.read_text(encoding="utf-8") for path in custody_root.rglob("*.json"))
    assert SECRET not in persisted
    assert ACCOUNT_ID not in persisted
    assert "raw_response" not in persisted
    assert all(call.body["max_completion_tokens"] == 1024 for call in transport.calls)


def test_d02_length_failure_is_persistable_as_sanitized_subtype_without_raw_output() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    bundle = load_frozen_cloudflare_comparison_bundle_v2(repo_root)
    plan = build_cloudflare_d02_plan(repo_root)
    transport = LengthFailureTransport()
    clients = build_cloudflare_d02_live_clients(secrets=CloudflareLiveSecrets(api_token=SECRET, account_id=ACCOUNT_ID), transport=transport)
    executor = CloudflareD02ComparisonExecutorV1(bundle=bundle, plan=plan, clients=clients, fixture_result=True, available_free_neurons=10000.0, zero_cash_cost_route_proven=True)
    attempt = executor.execute_next()
    assert attempt.outcome == "failure"
    assert attempt.failure_code == "CLIENT_FAILURE"
    assert attempt.failure_subtype == "CLOUDFLARE_FINISH_REASON_INVALID"
    assert attempt.output_tokens == 1024
    assert attempt.raw_material_recorded is False
    serialized = json.dumps(attempt.model_dump(mode="json"), sort_keys=True)
    assert SECRET not in serialized
    assert ACCOUNT_ID not in serialized


def test_d02_duplicate_custody_refuses_replay_before_any_provider_call(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    custody_root = tmp_path / "custody"
    transport = GovernedFixtureTransport(custody_root)
    kwargs = dict(custody_root=custody_root, secrets=CloudflareLiveSecrets(api_token=SECRET, account_id=ACCOUNT_ID), pre_live_evidence=_pre_live(), transport=transport, fixture_result=True, repo_root=repo_root)
    GovernedCloudflareD02LiveTaskV1.prepare(**kwargs)
    with pytest.raises(CloudflareD02ExistingRunError): GovernedCloudflareD02LiveTaskV1.prepare(**kwargs)
    assert transport.calls == []


def _load_launcher(repo_root: Path):
    path = repo_root / "scripts" / "research" / "execute_cloudflare_d02_live_comparison_operator_attestation_v1.py"
    spec = importlib.util.spec_from_file_location("d02_live_launcher", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_d02_launcher_authorization_fails_before_provider_environment_read(monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    launcher = _load_launcher(repo_root)
    reads: list[str] = []

    class GuardedEnvironment(dict[str, str]):
        def get(self, key: str, default: str = "") -> str:
            if key in {"CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"}:
                reads.append(key)
                raise AssertionError("provider environment read before authorization")
            return super().get(key, default)

    monkeypatch.setattr(launcher.os, "environ", GuardedEnvironment())
    monkeypatch.setattr(launcher, "validate_frozen_d02_live_authorization", lambda _root: (_ for _ in ()).throw(CloudflareAuthorizationError("blocked-before-secrets")))
    monkeypatch.setattr(sys, "argv", [str(repo_root / "scripts/research/execute_cloudflare_d02_live_comparison_operator_attestation_v1.py"), "--evidence", "not-read.json", "--receipt", "not-read.json", "--custody-root", "not-used"])
    with pytest.raises(CloudflareAuthorizationError, match="blocked-before-secrets"):
        launcher.main()
    assert reads == []
