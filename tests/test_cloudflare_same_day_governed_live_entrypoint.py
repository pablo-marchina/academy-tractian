from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

from academy_tractian.cloudflare_live_authorization_same_day_v3 import (
    CloudflareSameDayZeroUseEvidenceV1,
    issue_same_day_zero_use_receipt,
)
from academy_tractian.provider_clients import ProviderHttpRequest, ProviderHttpResponse


RESET = datetime(2026, 9, 2, 0, 0, 0, tzinfo=timezone.utc)
OBSERVED = RESET + timedelta(minutes=39)
RECEIPT_NOW = OBSERVED + timedelta(minutes=1)
EXECUTION_NOW = RECEIPT_NOW + timedelta(seconds=30)
SECRET = "same-day-provider-free-secret-never-persist"
ACCOUNT_ID = "abcdef0123456789abcdef0123456789"


def _decision(kind: str, **kwargs: Any) -> str:
    payload: dict[str, Any] = {
        "schema_version": "provider-decision-payload-v1",
        "kind": kind,
        "tool_name": None,
        "arguments": {},
        "evidence_id": None,
        "final": None,
        "message": None,
        "reason_code": None,
    }
    payload.update(kwargs)
    return json.dumps(payload, sort_keys=True)


def _good_response(text: str) -> str:
    if "asset_dev_probe_001" in text:
        return _decision("TOOL", tool_name="get_asset", arguments={"asset_id": "asset_dev_probe_001"})
    if "asset_dev_probe_002" in text:
        return _decision("TOOL", tool_name="list_analyses", arguments={"asset_id": "asset_dev_probe_002"})
    if "asset_dev_probe_003" in text:
        return _decision("TOOL", tool_name="get_data_quality", arguments={"asset_id": "asset_dev_probe_003"})
    if "BPFO" in text or "bpfo" in text:
        return _decision("TOOL", tool_name="search_knowledge", arguments={"q": "Explain BPFO", "type": "glossary"})
    if "asset I mentioned" in text:
        return _decision("CLARIFY", message="Which asset should I investigate?", reason_code="MISSING_ASSET")
    if "human specialist" in text:
        return _decision("ESCALATE", message="A human specialist should review the case.", reason_code="USER_REQUESTED_HUMAN")
    if "asset_dev_probe_007" in text:
        return _decision("ABSTAIN", message="The requested signal evidence is unavailable.", reason_code="UPSTREAM_UNAVAILABLE")
    if "analysis_dev_probe_008" in text:
        return _decision(
            "FINAL",
            final={"decision": "ORIENT", "response_mode": "complete", "message": "The action remains blocked by policy."},
        )
    raise AssertionError(text)


class ProviderFreeCloudflareTransport:
    def __init__(self) -> None:
        self.calls: list[ProviderHttpRequest] = []

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls.append(request)
        model = request.body["model"]
        user_text = request.body["messages"][1]["content"]
        return ProviderHttpResponse(
            status_code=200,
            body={
                "id": f"provider-free-same-day-{len(self.calls)}",
                "object": "chat.completion",
                "model": model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": _good_response(user_text)}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
            },
        )


def _load_launcher(repo_root: Path):
    path = repo_root / "scripts" / "research" / "execute_cloudflare_live_comparison_same_day_v1.py"
    spec = importlib.util.spec_from_file_location("cloudflare_same_day_entrypoint", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_same_day_entrypoint_composes_into_existing_governed_task_provider_free(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    launcher = _load_launcher(repo_root)
    custody_root = tmp_path / "custody"
    evidence_path = tmp_path / "evidence.json"
    receipt_path = tmp_path / "receipt.json"

    evidence = CloudflareSameDayZeroUseEvidenceV1(
        observed_at_utc=OBSERVED,
        utc_day="2026-09-02",
        reset_at_utc=RESET,
        workers_plan="Workers Free",
        workers_paid_enabled=False,
        free_allocation_neurons=10000.0,
        derived_free_neurons_remaining=10000.0,
        no_workers_ai_calls_since_reset_attested=True,
        no_automated_workers_ai_consumers_since_reset_attested=True,
        exclusive_workers_ai_account_window_until_packet_completion_attested=True,
        direct_workers_ai_route=True,
        ai_gateway_route_used=False,
        prepaid_unified_billing_route_used=False,
        gateway_header_present=False,
        comparison_attempts_consumed=0,
        inference_used_to_obtain_evidence=False,
        credential_account_probe_used=False,
        account_identifier_recorded=False,
        secret_recorded=False,
        workers_free_source_artifact_sha256="6" * 64,
        source_artifact_retained_outside_repo=True,
    )
    receipt = issue_same_day_zero_use_receipt(evidence, custody_root=custody_root, now_utc=RECEIPT_NOW)
    evidence_path.write_text(json.dumps(evidence.model_dump(mode="json"), sort_keys=True), encoding="utf-8")
    receipt_path.write_text(json.dumps(receipt.model_dump(mode="json"), sort_keys=True), encoding="utf-8")

    transport = ProviderFreeCloudflareTransport()
    monkeypatch.setattr(launcher, "_current_utc", lambda: EXECUTION_NOW)
    monkeypatch.setattr(launcher, "build_cloudflare_one_shot_transport_v2", lambda: transport)
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", SECRET)
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", ACCOUNT_ID)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(repo_root / "scripts" / "research" / "execute_cloudflare_live_comparison_same_day_v1.py"),
            "--evidence",
            str(evidence_path),
            "--receipt",
            str(receipt_path),
            "--custody-root",
            str(custody_root),
        ],
    )

    launcher.main()

    output = capsys.readouterr().out.strip()
    result = json.loads(output)
    assert result["state"] == "complete"
    assert result["completed_attempts"] == 32
    assert result["consumed_or_uncertain_attempts"] == 32
    assert result["raw_provider_material_recorded"] is False
    assert len(transport.calls) == 32

    marker = json.loads((custody_root / "cloudflare-adr018-live-comparison-custody-v2.json").read_text(encoding="utf-8"))
    ledger = json.loads((custody_root / "run" / "attempt-ledger-v2.json").read_text(encoding="utf-8"))
    assert marker["credentials_recorded"] is False
    assert marker["raw_provider_material_recorded"] is False
    assert ledger["state"] == "complete"
    assert len(ledger["entries"]) == 32
    assert all(entry["state"] == "completed" for entry in ledger["entries"])

    persisted = "\n".join(path.read_text(encoding="utf-8") for path in custody_root.rglob("*.json"))
    assert SECRET not in persisted
    assert ACCOUNT_ID not in persisted
    assert SECRET not in output
    assert ACCOUNT_ID not in output
