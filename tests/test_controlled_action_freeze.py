from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research/frozen/controlled-action-execution-profile-freeze-v1.json"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def test_controlled_action_freeze_matches_exact_frozen_files() -> None:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))

    assert freeze["schema_version"] == "controlled-action-execution-profile-freeze-v1"
    assert freeze["status"] == "FROZEN_FOR_CONTROLLED_ACTION_EXECUTION_PROFILE"
    assert freeze["adr_009_live_calls_consumed"] == 0
    assert freeze["real_customer_mutations"] == 0
    assert freeze["authorization_boundary"]["blanket_real_customer_mutation_authorized"] is False
    assert freeze["execution_invariants"]["default_production_runtime_remains_action_disabled"] is True
    assert freeze["execution_invariants"]["durable_claim_before_action_transport"] is True
    assert freeze["execution_invariants"]["raw_idempotency_key_persisted"] is False
    assert freeze["execution_invariants"]["uncertain_post_claim_failure_replayed_automatically"] is False

    frozen_files = (
        freeze["implementation"]["controlled_actions"],
        freeze["implementation"]["controlled_action_evaluation"],
        freeze["tests"]["controlled_actions"],
        freeze["tests"]["controlled_action_evaluation"],
        freeze["preserved_dependencies"]["adr_005_action_safety"],
        freeze["preserved_dependencies"]["harness_runner"],
        freeze["preserved_dependencies"]["baseline_production_evaluator"],
        freeze["preserved_dependencies"]["read_only_production_runtime"],
    )

    for entry in frozen_files:
        path = ROOT / entry["path"]
        assert path.is_file(), entry["path"]
        assert _git_blob_sha(path) == entry["git_blob"], entry["path"]


def test_controlled_action_freeze_covers_all_canonical_mutating_actions() -> None:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    assert freeze["canonical_actions_covered"] == [
        "update_asset_config",
        "reprocess_analysis",
        "request_specialist_analysis",
        "request_retraining",
        "escalate_case",
    ]
