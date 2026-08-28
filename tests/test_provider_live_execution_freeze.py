from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path


FREEZE_PATH = Path("research/frozen/provider-live-execution-wrapper-freeze-v1.json")


def _git_blob(path: Path) -> str:
    data = path.read_bytes()
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return sha1(header + data).hexdigest()


def test_provider_live_execution_freeze_matches_exact_provider_free_implementation() -> None:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))

    assert freeze["schema_version"] == "provider-live-execution-wrapper-freeze-v1"
    assert freeze["status"] == "FROZEN_PROVIDER_FREE_NO_LIVE_CALLS"
    assert freeze["issue"] == 41
    assert freeze["pr"] == 42
    assert freeze["live_provider_calls_consumed_by_issue_41"] == 0
    assert freeze["production_provider_model_selected"] is False
    assert freeze["production_mutating_actions_enabled"] is False

    implementation = freeze["implementation"]
    tests = freeze["tests"]
    assert _git_blob(Path(implementation["path"])) == implementation["git_blob"]
    assert _git_blob(Path(tests["path"])) == tests["git_blob"]

    dependencies = freeze["frozen_dependencies"]
    assert _git_blob(Path(dependencies["provider_comparison_executor_path"])) == dependencies[
        "provider_comparison_executor_git_blob"
    ]
    assert _git_blob(Path(dependencies["provider_clients_path"])) == dependencies[
        "provider_clients_git_blob"
    ]
    assert _git_blob(Path(dependencies["authorization_path"])) == dependencies[
        "authorization_git_blob"
    ]
    assert _git_blob(Path(dependencies["adr_009_path"])) == dependencies["adr_009_git_blob"]
    assert dependencies["canonical_plan_sha256"] == (
        "69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f"
    )

    behavior = freeze["frozen_behavior"]
    assert behavior["required_secret_presence_check_only"] is True
    assert behavior["credential_or_account_probe"] is False
    assert behavior["write_ahead_claim_before_executor_invocation"] is True
    assert behavior["automatic_resume"] is False
    assert behavior["automatic_retry_after_claim"] is False
    assert behavior["claimed_exception_becomes_uncertain"] is True
    assert behavior["credentials_persisted"] is False
    assert behavior["raw_provider_request_persisted"] is False
    assert behavior["raw_provider_response_persisted"] is False
    assert behavior["raw_exception_text_persisted"] is False
    assert behavior["production_selection_claim"] is False

    boundary = freeze["authorization_boundary"]
    assert boundary["this_freeze_executes_live_calls"] is False
    assert boundary["actual_live_calls_consumed"] == 0
    assert boundary["actual_provider_selected"] is False
    assert boundary["actual_credentials_probed"] is False
    assert boundary["actual_tractian_tools_executed"] == 0
    assert boundary["semantic_evaluation"] is False
    assert boundary["fresh_blind"] is False
    assert boundary["legacy_locked_test"] is False
    assert boundary["c4_rescoring"] is False
