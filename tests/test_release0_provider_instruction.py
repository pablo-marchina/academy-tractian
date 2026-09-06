from academy_tractian.cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_MAX_COMPLETION_TOKENS,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from academy_tractian.decision_source import build_provider_decision_request
from academy_tractian.provider_clients import PROVIDER_DECISION_SYSTEM_INSTRUCTION
from academy_tractian.release_provider import (
    RELEASE0_MAX_COMPLETION_TOKENS,
    RELEASE0_PROVIDER_SYSTEM_INSTRUCTION,
    Release0CloudflareDecisionClient,
    Release0ProviderDecisionSource,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerObservation


class NeverCalledTransport:
    def post_json(self, request):  # pragma: no cover - construction-only regression
        raise AssertionError("provider transport must not be called")


def _request():
    return build_provider_decision_request(
        context=ControllerContext(
            user_request="Investigate a vibration alert using read-only evidence.",
            turn_index=0,
            tool_call_count=0,
        ),
        registry=canonical_tool_registry(),
    )


def _base_client():
    return CloudflareWorkersAIChatCompletionsDecisionClient(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )


def _release_client():
    return Release0CloudflareDecisionClient(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )


def test_frozen_cloudflare_client_keeps_historical_request_contract() -> None:
    http_request = _base_client().build_http_request(_request())
    assert http_request.body["messages"][0] == {
        "role": "system",
        "content": PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    }
    assert http_request.body["max_completion_tokens"] == CLOUDFLARE_MAX_COMPLETION_TOKENS == 512
    assert "reasoning_effort" not in http_request.body
    assert "chat_template_kwargs" not in http_request.body


def test_release0_request_policy_is_isolated_and_encodes_relational_contract() -> None:
    assert RELEASE0_PROVIDER_SYSTEM_INSTRUCTION != PROVIDER_DECISION_SYSTEM_INSTRUCTION
    for required_fragment in (
        "all eight top-level fields",
        "tools[].parameters[].name",
        "Never wrap tool arguments",
        "kind=FINAL",
        'decision="ORIENT"',
        "complete, partial, inconclusive, conflict, or unavailable",
        "arguments={}",
        "search_knowledge accepts only q and optional type",
        "use it at most once in a run",
        "absent from the current supplied tools list",
        "read-only and no-action requests",
    ):
        assert required_fragment in RELEASE0_PROVIDER_SYSTEM_INSTRUCTION

    http_request = _release_client().build_http_request(_request())
    assert http_request.body["messages"][0]["content"] == RELEASE0_PROVIDER_SYSTEM_INSTRUCTION
    assert http_request.body["max_completion_tokens"] == RELEASE0_MAX_COMPLETION_TOKENS == 1024
    assert http_request.body["reasoning_effort"] is None
    assert http_request.body["chat_template_kwargs"] == {"enable_thinking": False}
    serialized = str(http_request.body["messages"][0]).lower()
    assert "test-token" not in serialized
    assert "abc123" not in serialized


def test_release0_provider_surface_removes_search_after_successful_search_observation() -> None:
    source = Release0ProviderDecisionSource(
        client=_release_client(),
        registry=canonical_tool_registry(),
    )
    initial = source.build_request(
        ControllerContext(
            user_request="Investigate vibration guidance.",
            turn_index=0,
            tool_call_count=0,
        )
    )
    assert len(initial.tools) == 18
    assert "search_knowledge" in {tool.name for tool in initial.tools}

    after_search = source.build_request(
        ControllerContext(
            user_request="Investigate vibration guidance.",
            turn_index=1,
            tool_call_count=1,
            observations=(
                ControllerObservation(
                    tool_name="search_knowledge",
                    status="success",
                    executed=True,
                    status_code=200,
                    body={"results": [{"title": "Vibration diagnostic procedure"}]},
                ),
            ),
        )
    )
    visible_names = {tool.name for tool in after_search.tools}
    assert len(after_search.tools) == 17
    assert "search_knowledge" not in visible_names
    assert "get_knowledge_doc" in visible_names
