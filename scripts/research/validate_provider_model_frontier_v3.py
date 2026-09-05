#!/usr/bin/env python3
"""Provider-free validation for the current hosted provider/model frontier v3."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from academy_tractian.hosted_candidate_registry import resolve_hosted_candidate
from academy_tractian.provider_frontier_v3 import (
    EXPECTED_PROVIDER_FRONTIER_V3_MANIFEST_SHA256,
    ProviderFrontierManifestV3,
)


DEFAULT_MANIFEST = Path("research/experiments/provider-model-frontier-preregistration-v3.json")
FORBIDDEN_PROVIDER_ENVS = (
    "OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_AUTH_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID",
)
EXPECTED_PROMOTABLE = (
    "google:gemini-3.8-flash",
    "groq:openai/gpt-oss-120b",
    "cloudflare:@cf/zai-org/glm-4.7-flash",
    "cloudflare:@cf/nvidia/nemotron-3-120b-a12b",
)
EXPECTED_REFERENCE_ONLY = ("openai:gpt-5.6-sol",)


def assert_provider_free_environment() -> None:
    present = tuple(sorted(name for name in FORBIDDEN_PROVIDER_ENVS if os.getenv(name)))
    if present:
        raise AssertionError(f"provider credentials forbidden during v3 preregistration validation: {present}")


def run(manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    assert_provider_free_environment()
    manifest = ProviderFrontierManifestV3.model_validate(
        json.loads(manifest_path.read_text(encoding="utf-8"))
    )
    assert manifest.canonical_sha256 == EXPECTED_PROVIDER_FRONTIER_V3_MANIFEST_SHA256
    assert manifest.provider_model_calls_authorized_now == 0
    assert manifest.credential_probes_authorized_now == 0
    assert manifest.production_provider_model_selected is False
    assert manifest.weighted_composite_score_forbidden is True
    assert manifest.reference_only_selection_forbidden is True

    promotable = tuple(item.candidate_id for item in manifest.candidate_set if item.role == "promotable")
    reference = tuple(item.candidate_id for item in manifest.candidate_set if item.role == "reference_only")
    assert promotable == EXPECTED_PROMOTABLE
    assert reference == EXPECTED_REFERENCE_ONLY

    for item in manifest.candidate_set:
        if item.hosted_registry_required:
            registered = resolve_hosted_candidate(item.provider_id, item.model_id)
            assert registered.candidate_id == item.candidate_id
        if item.role == "promotable":
            assert item.strict_usd0_required is True
            assert item.privacy_eligible_required is True
            assert item.live_evidence_required is True

    return {
        "status": "PASS",
        "schema_version": manifest.schema_version,
        "manifest_sha256": manifest.canonical_sha256,
        "provider_calls_executed": 0,
        "provider_calls_authorized": 0,
        "credential_probes_executed": 0,
        "promotable_candidate_count": len(promotable),
        "reference_only_candidate_count": len(reference),
        "production_provider_model_selected": False,
    }


def main() -> int:
    print(json.dumps(run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
