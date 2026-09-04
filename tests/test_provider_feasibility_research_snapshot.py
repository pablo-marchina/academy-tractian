from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path

from academy_tractian.provider_feasibility import (
    ProviderFeasibilityEvidence,
    ProviderFeasibilityPolicy,
    decide_provider_feasibility_set,
)


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
SNAPSHOT = RESEARCH / "provider-feasibility"
MANIFEST = RESEARCH / "provider-feasibility-source-manifest-2026-09-04.json"
EXPECTED_MANIFEST_SHA256 = "50b52da24e5dc87025f4aeb07d059b9f71f61883bbea3c0eb44c7ae454462d0a"


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


def test_frozen_source_manifest_hash_matches_every_feasibility_artifact() -> None:
    manifest = _load(MANIFEST)
    assert _canonical_sha256(manifest) == EXPECTED_MANIFEST_SHA256

    for path in sorted(SNAPSHOT.glob("*-2026-09-04.json")):
        if path.name.startswith("pilot-admission-policy"):
            continue
        evidence = ProviderFeasibilityEvidence.model_validate(_load(path))
        assert evidence.source_manifest_sha256 == EXPECTED_MANIFEST_SHA256


def test_pilot_admission_snapshot_is_fail_closed_and_not_a_promotion_decision() -> None:
    policy = ProviderFeasibilityPolicy.model_validate(
        _load(SNAPSHOT / "pilot-admission-policy-2026-09-04.json")
    )
    evidence = tuple(
        ProviderFeasibilityEvidence.model_validate(_load(path))
        for path in (
            SNAPSHOT / "openai-gpt-5.6-sol-2026-09-04.json",
            SNAPSHOT / "google-gemini-3.7-flash-2026-09-04.json",
            SNAPSHOT / "google-gemini-3.8-flash-2026-09-04.json",
            SNAPSHOT / "groq-gpt-oss-120b-2026-09-04.json",
        )
    )
    decisions = decide_provider_feasibility_set(
        evidence=evidence,
        policy=policy,
        evaluated_at=datetime(2026, 9, 4, 19, 40, tzinfo=UTC),
    )
    by_id = {decision.candidate_id: decision for decision in decisions}

    assert by_id["openai:gpt-5.6-sol"].outcome == "INELIGIBLE"
    assert by_id["openai:gpt-5.6-sol"].reason_codes == ("ZERO_COST_EXECUTION_UNKNOWN",)
    assert by_id["google:gemini-3.7-flash"].outcome == "ELIGIBLE"
    assert by_id["google:gemini-3.8-flash"].outcome == "ELIGIBLE"
    assert by_id["groq:openai/gpt-oss-120b"].outcome == "ELIGIBLE"

    # Pilot admission has no capacity threshold by design. It only authorizes controlled comparison;
    # ProviderPromotionDecision remains the separate and stricter quality-selection boundary.
    assert policy.min_free_requests_per_day == 0
    assert policy.min_free_tokens_per_day == 0
