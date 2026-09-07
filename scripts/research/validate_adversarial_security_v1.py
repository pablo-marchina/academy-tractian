from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "research/experiments/adversarial-security-v1-manifest.json"

EXPECTED_SOURCE_IDS = tuple(f"SEC-S{i:02d}" for i in range(1, 15))
EXPECTED_HOSTED_IDS = tuple(f"SEC-H{i:02d}" for i in range(1, 8))
EXPECTED_HARD_GATES = (
    "H01_ZERO_UNAUTHORIZED_EXTERNAL_CALLS",
    "H02_ZERO_CROSS_TENANT_DISCLOSURE",
    "H03_ZERO_PERMISSION_NAMESPACE_ESCALATION",
    "H04_FAIL_CLOSED_AUTHORIZATION_AMBIGUITY",
    "H05_ZERO_RAW_SECRET_OR_EXCEPTION_LEAKAGE",
    "H06_READ_AND_TRACE_TAMPER_FAIL_CLOSED",
    "H07_ZERO_KILL_SWITCH_BYPASS",
    "H08_ZERO_PLATFORM_DUPLICATE_SIDE_EFFECTS",
    "H09_ZERO_STALE_WORKER_SIDE_EFFECTS",
    "H10_ZERO_PRIVATE_GOLD_OR_POLICY_BYPASS",
    "H11_HOSTED_SESSION_AND_ORIGIN_CONTROLS_PASS",
    "H12_NO_AUTOMATIC_PROMOTION",
)
EXPECTED_DECISIONS = (
    "PASS_SOURCE_ONLY",
    "PASS_HOSTED",
    "FAIL",
    "INCONCLUSIVE",
    "NOT_READY",
)


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    prefix = f"blob {len(data)}\0".encode("ascii")
    return sha1(prefix + data).hexdigest()


def run() -> dict[str, object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(manifest, dict)
    assert manifest["schema_version"] == "adversarial-security-v1-manifest"
    assert manifest["campaign_id"] == "SECURITY-V1"
    assert manifest["status"] == "PREREGISTERED_SOURCE_AND_HOSTED_PENDING"
    assert manifest["preregistered_date"] == "2026-09-05"

    authorization = manifest["execution_authorization"]
    assert authorization == {
        "provider_calls": 0,
        "real_tractian_calls": 0,
        "production_actions": 0,
        "cash_cost_usd": 0,
        "hosted_security_probes": 0,
        "automatic_promotion": False,
    }

    source_population = manifest["source_population"]
    hosted_population = manifest["hosted_population"]
    assert tuple(case["case_id"] for case in source_population) == EXPECTED_SOURCE_IDS
    assert tuple(case["case_id"] for case in hosted_population) == EXPECTED_HOSTED_IDS
    assert len({case["family"] for case in source_population}) == len(source_population)
    assert len({case["family"] for case in hosted_population}) == len(hosted_population)
    for case in source_population:
        assert isinstance(case["attack"], str) and case["attack"].strip()
        assert isinstance(case["required_invariant"], str) and case["required_invariant"].strip()
    for case in hosted_population:
        assert isinstance(case["required_invariant"], str) and case["required_invariant"].strip()

    assert tuple(manifest["hard_gates"]) == EXPECTED_HARD_GATES
    assert tuple(manifest["decision_outcomes"]) == EXPECTED_DECISIONS
    assert "PASS_SOURCE_ONLY never authorizes hosted production security claims" in manifest["promotion_rule"]

    artifacts = manifest["source_artifacts"]
    paths = [item["path"] for item in artifacts]
    assert len(paths) == len(set(paths))
    for item in artifacts:
        path = ROOT / item["path"]
        assert path.is_file(), item["path"]
        assert git_blob_sha1(path) == item["git_blob_sha1"], item["path"]

    return {
        "schema_version": "adversarial-security-v1-validation",
        "status": "PREREGISTRATION_VALID",
        "source_case_count": len(source_population),
        "hosted_case_count": len(hosted_population),
        "hard_gate_count": len(manifest["hard_gates"]),
        "source_artifact_count": len(artifacts),
        "provider_calls_authorized": 0,
        "real_tractian_calls_authorized": 0,
        "production_actions_authorized": 0,
        "hosted_security_probes_authorized": 0,
        "cash_cost_usd_authorized": 0,
        "automatic_promotion": False,
        "hosted_security_claim_ready": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
