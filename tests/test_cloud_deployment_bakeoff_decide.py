from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import subprocess
import sys

from scripts.cloud_deployment_bakeoff_decide import build_provider_free_no_live_decision


ROOT = Path(__file__).resolve().parents[1]
EVALUATED_AT = datetime(2026, 9, 4, 20, 0, tzinfo=UTC)


def test_provider_free_offline_decision_recomputes_static_frontier_and_refuses_promotion() -> None:
    payload = build_provider_free_no_live_decision(evaluated_at=EVALUATED_AT)

    assert payload["provider_free"] is True
    assert payload["network_calls_performed"] == 0
    assert payload["cloud_resources_created"] == 0
    assert payload["live_evidence_supplied"] is False
    assert payload["static_compute_admissible_candidate_ids"] == ["oracle-oci-always-free-a1"]
    assert payload["static_database_admissible_candidate_ids"] == ["neon-free"]
    assert payload["static_identity_admissible_candidate_ids"] == ["auth0-free"]
    assert payload["required_state_identity_bundle"]["bundle_id"] == "neon-plus-auth0"
    assert payload["required_state_identity_bundle"]["outcome"] == "PILOT_ADMISSIBLE"

    decision = payload["bakeoff_decision"]
    assert decision["outcome"] == "NO_SELECTION"
    assert decision["selected_topology_id"] is None
    assert decision["qualified_topology_ids"] == []
    assert decision["reason_codes"] == ["NO_LIVE_QUALIFIED_TOPOLOGY"]

    assessments = {item["compute_candidate_id"]: item for item in decision["assessments"]}
    assert assessments["google-cloud-run-request-free-tier"]["reason_codes"] == [
        "STATIC_FEASIBILITY_REJECTED"
    ]
    oracle_reasons = set(assessments["oracle-oci-always-free-a1"]["reason_codes"])
    assert {
        "STATE_IDENTITY_PILOT_MISSING",
        "STATE_IDENTITY_EVIDENCE_MISSING",
        "LIVE_ATTESTATION_MISSING",
        "LIVE_ATTESTATION_EVIDENCE_MISSING",
        "RUNTIME_EVIDENCE_MISSING",
    } <= oracle_reasons


def test_cli_require_promotion_fails_closed_without_live_evidence(tmp_path: Path) -> None:
    output = tmp_path / "decision.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "cloud_deployment_bakeoff_decide.py"),
            "--evaluated-at",
            "2026-09-04T20:00:00Z",
            "--output",
            str(output),
            "--require-promotion",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["bakeoff_decision"]["outcome"] == "NO_SELECTION"
    assert payload["network_calls_performed"] == 0
    assert payload["cloud_resources_created"] == 0
