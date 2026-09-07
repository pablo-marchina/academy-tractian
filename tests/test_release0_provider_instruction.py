import json

import pytest

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


class StaticDecisionClient:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def complete(self, request):
        del request
        return json.dumps(self.payload)


def _context(user_request: str = "Investigate a vibration alert using read-only evidence.") -> ControllerContext:
    return ControllerContext(
        user_request=user_request,
        turn_index=0,
        tool_call_count=0,
    )


def _request():
    return build_provider_decision_request(
        context=_context(),
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


def _release_source(client=None):
    return Release0ProviderDecisionSource(
        client=client or _release_client(),
        registry=canonical_tool_registry(),
    )


def _search_context(body, *, status="success", executed=True) -> ControllerContext:
    return ControllerContext(
        user_request="Investigate vibration guidance.",
        turn_index=1,
        tool_call_count=1,
        observations=(
            ControllerObservation(
                tool_name="search_knowledge",
                status=status,
                executed=executed,
                status_code=200 if status == "success" else 503,
                body=body,
            ),
        ),
    )


def _successful_search_context() -> ControllerContext:
    return _search_context({"results": [{"title": "Vibration diagnostic procedure"}]})


def _grounded_search_context() -> ControllerContext:
    return _search_context(
        {
            "results": [
                {"doc_id": "doc-vibration-1", "title": "Vibration diagnostic procedure"},
                {"doc_id": "doc-vibration-2", "title": "Bearing diagnostic guidance"},
                {"doc_id": "doc-vibration-1", "title": "duplicate id is deduplicated"},
            ]
        }
    )


def _after_doc_context() -> ControllerContext:
    search = _grounded_search_context().observations[0]
    return ControllerContext(
        user_request="Investigate vibration guidance.",
        turn_index=2,
        tool_call_count=2,
        observations=(
            search,
            ControllerObservation(
                tool_name="get_knowledge_doc",
                status="success",
                executed=True,
                status_code=200,
                body={"doc_id": "doc-vibration-1", "content": "Grounded guidance."},
            ),
        ),
    )


def _tool_variant(schema: dict[str, object], tool_name: str) -> dict[str, object]:
    variants = schema["oneOf"]
    return next(
        variant
        for variant in variants
        if variant["properties"]["kind"]["enum"] == ["TOOL"]
        and variant["properties"]["tool_name"]["enum"] == [tool_name]
    )


def _tool_names(schema: dict[str, object]) -> set[str]:
    return {
        variant["properties"]["tool_name"]["enum"][0]
        for variant in schema["oneOf"]
        if variant["properties"]["kind"]["enum"] == ["TOOL"]
    }


def test_frozen_cloudflare_client_keeps_historical_request_contract() -> None:
    http_request = _base_client().build_http_request(_request())
    assert http_request.body["messages"][0] == {
        "role": "system",
        "content": PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    }
    assert http_request.body["max_completion_tokens"] == CLOUDFLARE_MAX_COMPLETION_TOKENS == 512
    assert "reasoning_effort" not in http_request.body
    assert "chat_template_kwargs" not in http_request.body


def test_release0_request_policy_is_read_only_and_tool_arguments_are_exact() -> None:
    assert RELEASE0_PROVIDER_SYSTEM_INSTRUCTION != PROVIDER_DECISION_SYSTEM_INSTRUCTION
    for required_fragment in (
        "all eight top-level fields",
        "Release 0 is read-only",
        "one TOOL variant per tool",
        "only tools[].parameters[].name keys are allowed",
        "kind=FINAL",
        'decision="ORIENT"',
        "complete, partial, inconclusive, conflict, or unavailable",
        "arguments={}",
        "search_knowledge accepts only q and optional type",
        "use it at most once in a run",
        "exact doc_id values",
        "no further read tool is supplied",
        "explicit user prohibition",
    ):
        assert required_fragment in RELEASE0_PROVIDER_SYSTEM_INSTRUCTION

    source = _release_source()
    request = source.build_request(_context())
    visible_names = {tool.name for tool in request.tools}
    assert len(request.tools) == 13
    assert "search_knowledge" in visible_names
    assert "get_knowledge_doc" in visible_names
    for action_name in (
        "update_asset_config",
        "reprocess_analysis",
        "request_specialist_analysis",
        "request_retraining",
        "escalate_case",
    ):
        assert action_name not in visible_names

    http_request = _release_client().build_http_request(request)
    assert http_request.body["messages"][0]["content"] == RELEASE0_PROVIDER_SYSTEM_INSTRUCTION
    assert http_request.body["max_completion_tokens"] == RELEASE0_MAX_COMPLETION_TOKENS == 1024
    assert http_request.body["reasoning_effort"] is None
    assert http_request.body["chat_template_kwargs"] == {"enable_thinking": False}

    response_schema = http_request.body["response_format"]["json_schema"]
    variants = response_schema["oneOf"]
    assert len(variants) == len(request.tools) + 2

    search_variant = _tool_variant(response_schema, "search_knowledge")
    search_arguments = search_variant["properties"]["arguments"]
    assert search_arguments["additionalProperties"] is False
    assert set(search_arguments["properties"]) == {"q", "type"}
    assert search_arguments["required"] == ["q"]
    assert search_arguments["properties"]["q"] == {"type": "string"}
    assert search_arguments["properties"]["type"] == {
        "type": "string",
        "enum": ["procedure", "glossary", "guidance"],
    }

    doc_variant = _tool_variant(response_schema, "get_knowledge_doc")
    doc_arguments = doc_variant["properties"]["arguments"]
    assert doc_arguments["additionalProperties"] is False
    assert set(doc_arguments["properties"]) == {"doc_id"}
    assert doc_arguments["required"] == ["doc_id"]

    final_variant = next(
        variant
        for variant in variants
        if variant["properties"]["kind"]["enum"] == ["FINAL"]
    )
    assert final_variant["properties"]["arguments"]["maxProperties"] == 0
    assert final_variant["properties"]["final"]["required"] == [
        "decision",
        "response_mode",
        "message",
    ]
    assert final_variant["properties"]["final"]["properties"]["decision"]["enum"] == [
        "ORIENT"
    ]

    serialized = str(http_request.body["messages"][0]).lower()
    assert "test-token" not in serialized
    assert "abc123" not in serialized


@pytest.mark.parametrize(
    ("prompt", "expected_kind"),
    (
        (
            "Do not use any tool. Ask me one question for the missing context required to continue.",
            "CLARIFY",
        ),
        (
            "I prohibit tool use. This diagnosis cannot be made from the available evidence; stop safely.",
            "ABSTAIN",
        ),
        (
            "I prohibit tool use. The claims are contradictory and unresolved; hand this to a human specialist.",
            "ESCALATE",
        ),
    ),
)
def test_release0_explicit_safe_terminal_request_hides_tools_and_narrows_schema(
    prompt: str,
    expected_kind: str,
) -> None:
    source = _release_source()
    request = source.build_request(_context(prompt))
    assert request.tools == ()

    schema = _release_client().build_http_request(request).body["response_format"]["json_schema"]
    assert len(schema["oneOf"]) == 1
    assert _tool_names(schema) == set()
    assert schema["oneOf"][0]["properties"]["kind"]["enum"] == [expected_kind]


def test_release0_no_tool_request_without_unambiguous_terminal_keeps_terminal_choices() -> None:
    source = _release_source()
    request = source.build_request(_context("Do not use any tool; answer as safely as possible."))
    assert request.tools == ()
    schema = _release_client().build_http_request(request).body["response_format"]["json_schema"]
    assert len(schema["oneOf"]) == 2
    assert _tool_names(schema) == set()


def test_release0_search_without_structured_doc_id_becomes_terminal_only() -> None:
    source = _release_source()
    after_search = source.build_request(_successful_search_context())
    assert after_search.tools == ()

    http_request = _release_client().build_http_request(after_search)
    schema = http_request.body["response_format"]["json_schema"]
    assert _tool_names(schema) == set()
    assert len(schema["oneOf"]) == 2


def test_release0_search_failure_or_block_becomes_terminal_only() -> None:
    source = _release_source()
    failed = source.build_request(_search_context({"error": "unavailable"}, status="failure"))
    blocked = source.build_request(
        _search_context({"text": "not executed"}, status="blocked", executed=False)
    )
    assert failed.tools == ()
    assert blocked.tools == ()


def test_release0_grounded_doc_ids_are_the_only_allowed_continuation() -> None:
    source = _release_source()
    after_search = source.build_request(_grounded_search_context())
    assert [tool.name for tool in after_search.tools] == ["get_knowledge_doc"]

    doc_parameter = after_search.tools[0].parameters[0]
    assert doc_parameter.name == "doc_id"
    assert doc_parameter.parameter_schema == {
        "enum": ["doc-vibration-1", "doc-vibration-2"],
    }

    schema = _release_client().build_http_request(after_search).body["response_format"][
        "json_schema"
    ]
    assert _tool_names(schema) == {"get_knowledge_doc"}
    doc_variant = _tool_variant(schema, "get_knowledge_doc")
    assert doc_variant["properties"]["arguments"]["properties"]["doc_id"] == {
        "enum": ["doc-vibration-1", "doc-vibration-2"],
    }


def test_release0_grounding_ignores_free_text_generic_ids_and_invalid_doc_ids() -> None:
    source = _release_source()
    context = _search_context(
        {
            "results": [
                {"id": "generic-id", "text": "doc_id: text-only-id"},
                {"doc_id": "   "},
                {"doc_id": 123},
            ]
        }
    )
    assert source.build_request(context).tools == ()


def test_release0_after_document_observation_becomes_terminal_only() -> None:
    source = _release_source()
    request = source.build_request(_after_doc_context())
    assert request.tools == ()
    schema = _release_client().build_http_request(request).body["response_format"]["json_schema"]
    assert _tool_names(schema) == set()


def test_release0_adapter_rejects_search_after_terminal_only_transition() -> None:
    source = _release_source(
        StaticDecisionClient(
            {
                "schema_version": "provider-decision-payload-v1",
                "kind": "TOOL",
                "tool_name": "search_knowledge",
                "arguments": {"q": "vibration"},
                "evidence_id": "ev-search",
                "final": None,
                "message": None,
                "reason_code": None,
            }
        )
    )

    with pytest.raises(ValueError, match="unknown tool: search_knowledge"):
        source.decide(_successful_search_context())


def test_release0_adapter_rejects_lateral_read_after_grounded_search() -> None:
    source = _release_source(
        StaticDecisionClient(
            {
                "schema_version": "provider-decision-payload-v1",
                "kind": "TOOL",
                "tool_name": "get_asset",
                "arguments": {"asset_id": "asset-1"},
                "evidence_id": "ev-lateral",
                "final": None,
                "message": None,
                "reason_code": None,
            }
        )
    )

    with pytest.raises(ValueError, match="unknown tool: get_asset"):
        source.decide(_grounded_search_context())


def test_release0_adapter_rejects_action_tool_even_on_first_turn() -> None:
    source = _release_source(
        StaticDecisionClient(
            {
                "schema_version": "provider-decision-payload-v1",
                "kind": "TOOL",
                "tool_name": "escalate_case",
                "arguments": {"case_id": "case-1", "body": {}},
                "evidence_id": "ev-action",
                "final": None,
                "message": None,
                "reason_code": None,
            }
        )
    )

    with pytest.raises(ValueError, match="unknown tool: escalate_case"):
        source.decide(_context())
