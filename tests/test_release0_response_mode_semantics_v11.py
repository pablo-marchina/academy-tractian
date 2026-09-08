from __future__ import annotations

from academy_tractian.cloudflare_provider_client import CLOUDFLARE_GLM_MODEL_ID
from academy_tractian.release_provider_v10 import Release0ProviderDecisionSourceV10
from academy_tractian.release_provider_v11 import (
    RELEASE0_V11_RESPONSE_MODE_INSTRUCTION,
    RELEASE0_V11_RESPONSE_MODE_SEMANTICS_VERSION,
    Release0CloudflareDecisionClientV11,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext


class NeverCalledTransport:
    def post_json(self, request):  # pragma: no cover - construction-only regression
        raise AssertionError("provider transport must not be called")


def _client() -> Release0CloudflareDecisionClientV11:
    return Release0CloudflareDecisionClientV11(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )


def test_v11_appends_explicit_response_mode_semantics_to_system_instruction() -> None:
    client = _client()
    source = Release0ProviderDecisionSourceV10(
        client=client,
        registry=canonical_tool_registry(),
    )
    request = source.build_request(
        ControllerContext(
            user_request="Summarize the available evidence.",
            turn_index=0,
            tool_call_count=0,
            observations=(),
        )
    )

    http_request = client.build_http_request(request)
    messages = http_request.body["messages"]
    assert len(messages) == 2
    system_instruction = messages[0]["content"]

    assert "Release 0 decision contract:" in system_instruction
    assert RELEASE0_V11_RESPONSE_MODE_INSTRUCTION in system_instruction
    assert RELEASE0_V11_RESPONSE_MODE_SEMANTICS_VERSION == "release0-response-mode-semantics-v1"


def test_v11_distinguishes_partial_from_inconclusive_for_supported_directional_answers() -> None:
    instruction = RELEASE0_V11_RESPONSE_MODE_INSTRUCTION

    assert "A supported prioritization or ranking plus an" in instruction
    assert "evidence-backed likely fault mechanism is partial" in instruction
    assert "it does not support a reliable directional answer" in instruction
    assert "Do not use inconclusive merely because a supported conclusion" in instruction
    assert "Never label that kind of" in instruction
    assert "supported directional answer inconclusive" in instruction


def test_v11_defines_all_customer_visible_response_modes() -> None:
    instruction = RELEASE0_V11_RESPONSE_MODE_INSTRUCTION

    for mode in ("complete", "partial", "inconclusive", "conflict", "unavailable"):
        assert f"- {mode}:" in instruction
