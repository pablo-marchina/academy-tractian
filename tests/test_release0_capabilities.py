from __future__ import annotations

import json

from academy_tractian.release0_capabilities import (
    READ_SEMANTICS,
    build_release0_capability_manifest,
)
from academy_tractian.runtime import canonical_tool_registry


def _manifest() -> dict[str, object]:
    return build_release0_capability_manifest(
        release_git_sha="a" * 40,
        provider_calls_enabled=True,
        provider_selection_state="PROVISIONAL_RELEASE_PROVIDER",
        provider_id="cloudflare",
        provider_model_id="@cf/zai-org/glm-4.7-flash",
        tractian_transport_enabled=True,
        tractian_transport_state="CONFIGURED_UNVERIFIED",
        cost_policy="USD0_HARD_GATE",
        paid_fallback_enabled=False,
        local_serving_enabled=False,
    )


def test_release0_manifest_is_derived_from_all_18_canonical_tools() -> None:
    manifest = _manifest()
    tools = manifest["tools"]
    assert isinstance(tools, list)
    assert len(tools) == 18
    assert {item["name"] for item in tools} == set(canonical_tool_registry())

    reads = [item for item in tools if item["kind"] == "read"]
    actions = [item for item in tools if item["kind"] == "action"]
    assert len(reads) == 13
    assert len(actions) == 5
    assert all(item["availability"] == "LIVE_READ" for item in reads)
    assert all(item["availability"] == "PROPOSAL_ONLY" for item in actions)


def test_release0_manifest_exposes_expected_outputs_and_semantics_without_secrets() -> None:
    manifest = _manifest()
    assert manifest["read_semantics"] == list(READ_SEMANTICS)
    assert manifest["release"]["read_only_user_path_enabled"] is True
    assert manifest["action_execution"]["enabled"] is False
    assert manifest["action_execution"]["external_side_effects_allowed"] is False
    assert len(manifest["guided_intents"]) == 3
    assert len(manifest["expected_outputs"]) >= 10

    serialized = json.dumps(manifest, sort_keys=True).lower()
    for forbidden in (
        "api_token",
        "provider_account_id",
        "authorization: bearer",
        "tractian_server_headers",
        "postgres_internal_dsn",
        "postgres_scoped_dsn",
    ):
        assert forbidden not in serialized
    assert manifest["raw_secrets_exposed"] is False
    assert manifest["raw_api_payloads_exposed"] is False
    assert manifest["chain_of_thought_exposed"] is False


def test_release0_manifest_fails_closed_when_live_dependencies_are_disabled() -> None:
    manifest = build_release0_capability_manifest(
        release_git_sha="b" * 40,
        provider_calls_enabled=False,
        provider_selection_state="NO_SELECTION",
        provider_id=None,
        provider_model_id=None,
        tractian_transport_enabled=False,
        tractian_transport_state="UNCONFIGURED",
        cost_policy="USD0_HARD_GATE",
        paid_fallback_enabled=False,
        local_serving_enabled=False,
    )
    assert manifest["release"]["read_only_user_path_enabled"] is False
    assert all(item["availability"] == "UNAVAILABLE" for item in manifest["tools"])
