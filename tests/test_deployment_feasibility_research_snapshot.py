from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path

from academy_tractian.deployment_feasibility import (
    DeploymentFeasibilityEvidence,
    DeploymentFeasibilityPolicy,
    decide_deployment_feasibility_set,
)


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
SNAPSHOT = RESEARCH / "deployment-feasibility"
MANIFEST = RESEARCH / "deployment-feasibility-source-manifest-2026-09-04.json"
EXPECTED_MANIFEST_SHA256 = "305b98b8ba65d3f495199fb58953603d063b6fa45eb09315fe253fdbc2dd0c4b"


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_deployment_source_manifest_and_artifacts_are_hash_bound() -> None:
    manifest = _load(MANIFEST)
    assert _canonical_sha256(manifest) == EXPECTED_MANIFEST_SHA256

    for path in sorted(SNAPSHOT.glob("*-2026-09-04.json")):
        if path.name.startswith("backend-pilot-admission-policy"):
            continue
        evidence = DeploymentFeasibilityEvidence.model_validate(_load(path))
        assert evidence.source_manifest_sha256 == EXPECTED_MANIFEST_SHA256


def test_static_backend_screen_admits_only_oracle_always_free_for_live_pilot() -> None:
    policy = DeploymentFeasibilityPolicy.model_validate(
        _load(SNAPSHOT / "backend-pilot-admission-policy-2026-09-04.json")
    )
    evidence = tuple(
        DeploymentFeasibilityEvidence.model_validate(_load(path))
        for path in (
            SNAPSHOT / "vercel-hobby-python-2026-09-04.json",
            SNAPSHOT / "google-cloud-run-request-free-tier-2026-09-04.json",
            SNAPSHOT / "cloudflare-python-workers-free-2026-09-04.json",
            SNAPSHOT / "oracle-oci-always-free-a1-2026-09-04.json",
            SNAPSHOT / "railway-free-docker-2026-09-04.json",
        )
    )
    decisions = decide_deployment_feasibility_set(
        evidence=evidence,
        policy=policy,
        evaluated_at=datetime(2026, 9, 4, 20, 0, tzinfo=UTC),
    )
    by_id = {decision.candidate_id: decision for decision in decisions}

    assert by_id["oracle-oci-always-free-a1"].outcome == "PILOT_ADMISSIBLE"
    assert by_id["oracle-oci-always-free-a1"].reason_codes == ()

    assert by_id["google-cloud-run-request-free-tier"].outcome == "STATIC_REJECT"
    assert "ZERO_COST_GUARDRAIL_REQUIRED" in by_id[
        "google-cloud-run-request-free-tier"
    ].reason_codes

    assert by_id["vercel-hobby-python"].outcome == "STATIC_REJECT"
    assert "RUNTIME_MATURITY_NOT_ALLOWED" in by_id["vercel-hobby-python"].reason_codes
    assert "DOCKERFILE_COMPATIBILITY_REQUIRED" in by_id["vercel-hobby-python"].reason_codes

    assert by_id["cloudflare-python-workers-free"].outcome == "STATIC_REJECT"
    assert "PYTHON_3_11_COMPATIBILITY_REQUIRED" in by_id[
        "cloudflare-python-workers-free"
    ].reason_codes
    assert "MIGRATION_CLASS_NOT_ALLOWED" in by_id[
        "cloudflare-python-workers-free"
    ].reason_codes

    assert by_id["railway-free-docker"].outcome == "STATIC_REJECT"
    assert "PROVIDER_DISCOURAGES_PRODUCTION" in by_id["railway-free-docker"].reason_codes
