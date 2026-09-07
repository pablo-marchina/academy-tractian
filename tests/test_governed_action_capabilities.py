from __future__ import annotations

from academy_tractian.release0_capabilities import build_release0_capability_manifest


def _manifest(*, actions_enabled: bool):
    return build_release0_capability_manifest(
        release_git_sha="a" * 40,
        provider_calls_enabled=True,
        provider_selection_state="PROVISIONAL_RELEASE_PROVIDER",
        provider_id="provider",
        provider_model_id="model",
        tractian_transport_enabled=True,
        tractian_transport_state="CONFIGURED_UNVERIFIED",
        cost_policy="usd0-hard-gate",
        paid_fallback_enabled=False,
        local_serving_enabled=False,
        actions_enabled=actions_enabled,
    )


def test_governed_action_manifest_marks_all_five_actions_executable() -> None:
    manifest = _manifest(actions_enabled=True)

    actions = [tool for tool in manifest["tools"] if tool["kind"] == "action"]
    assert {tool["name"] for tool in actions} == {
        "update_asset_config",
        "reprocess_analysis",
        "request_specialist_analysis",
        "request_retraining",
        "escalate_case",
    }
    assert all(tool["availability"] == "EXECUTABLE_WITH_CONFIRMATION" for tool in actions)
    assert manifest["action_execution"] == {
        "enabled": True,
        "mode": "GOVERNED_CONFIRMATION",
        "external_side_effects_allowed": True,
        "explanation": manifest["action_execution"]["explanation"],
    }
    assert manifest["release"]["governed_action_path_enabled"] is True
    assert manifest["tool_summary"]["executable_actions"] == 5
    assert manifest["tool_summary"]["proposal_only_actions"] == 0


def test_action_manifest_remains_proposal_only_when_global_switch_is_off() -> None:
    manifest = _manifest(actions_enabled=False)

    actions = [tool for tool in manifest["tools"] if tool["kind"] == "action"]
    assert all(tool["availability"] == "PROPOSAL_ONLY" for tool in actions)
    assert manifest["action_execution"]["enabled"] is False
    assert manifest["action_execution"]["external_side_effects_allowed"] is False
    assert manifest["tool_summary"]["executable_actions"] == 0
    assert manifest["tool_summary"]["proposal_only_actions"] == 5
