from __future__ import annotations

from academy_tractian.cloudflare_provider_client import CLOUDFLARE_GLM_MODEL_ID
from academy_tractian.release_provider_v14_knowledge import (
    RELEASE0_V14_KNOWLEDGE_INSTRUCTION,
    Release0CloudflareDecisionClientV14Knowledge,
    Release0ProviderDecisionSourceV14Knowledge,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerObservation


class NeverCalledTransport:
    def post_json(self, request):  # pragma: no cover - construction-only regression
        raise AssertionError("provider transport must not be called")


def _client() -> Release0CloudflareDecisionClientV14Knowledge:
    return Release0CloudflareDecisionClientV14Knowledge(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )


def _source() -> Release0ProviderDecisionSourceV14Knowledge:
    return Release0ProviderDecisionSourceV14Knowledge(
        client=_client(),
        registry=canonical_tool_registry(),
    )


def _observation(
    tool_name: str,
    body,
    *,
    status: str = "success",
    executed: bool = True,
    status_code: int = 200,
) -> ControllerObservation:
    return ControllerObservation(
        tool_name=tool_name,
        status=status,
        executed=executed,
        status_code=status_code,
        body=body,
    )


def _context(user_request: str, *observations: ControllerObservation) -> ControllerContext:
    return ControllerContext(
        user_request=user_request,
        turn_index=len(observations),
        tool_call_count=len(observations),
        observations=observations,
    )


def _tool_names(request) -> set[str]:
    return {tool.name for tool in request.tools}


def _schema_kinds(request) -> set[str]:
    schema = _client().build_http_request(request).body["response_format"]["json_schema"]
    return {
        kind
        for variant in schema["oneOf"]
        for kind in variant["properties"]["kind"]["enum"]
    }


def _parameter_enum(request, tool_name: str, parameter_name: str) -> list[str]:
    tool = next(tool for tool in request.tools if tool.name == tool_name)
    parameter = next(p for p in tool.parameters if p.name == parameter_name)
    return parameter.parameter_schema["enum"]


def test_explicit_knowledge_search_is_required_before_terminal() -> None:
    request = _source().build_request(
        _context(
            "Consulte a base de conhecimento e encontre orientação sobre vibração anormal."
        )
    )
    assert _tool_names(request) == {"search_knowledge"}
    assert _schema_kinds(request) == {"TOOL"}
    instruction = _client().build_http_request(request).body["messages"][0]["content"]
    assert RELEASE0_V14_KNOWLEDGE_INSTRUCTION in instruction


def test_knowledge_intent_takes_precedence_over_asset_grounding() -> None:
    request = _source().build_request(
        _context(
            "Consulte a base de conhecimento e explique como interpretar vibração anormal em um ativo como o M101."
        )
    )
    assert _tool_names(request) == {"search_knowledge"}
    assert "get_current_user" not in _tool_names(request)
    assert _schema_kinds(request) == {"TOOL"}


def test_search_only_request_can_terminal_immediately_after_successful_search() -> None:
    prompt = "Consulte a base de conhecimento sobre vibração anormal e responda com o que encontrou."
    request = _source().build_request(
        _context(
            prompt,
            _observation(
                "search_knowledge",
                {"items": [{"doc_id": "kb-vibration-1", "summary": "Bearing guidance"}]},
            ),
        )
    )
    assert request.tools == ()
    assert "FINAL" in _schema_kinds(request)


def test_document_depth_request_requires_grounded_document_before_terminal() -> None:
    prompt = "Pesquise a base de conhecimento e abra o documento mais relevante antes de responder."
    request = _source().build_request(
        _context(
            prompt,
            _observation(
                "search_knowledge",
                {
                    "items": [
                        {"doc_id": "kb-vibration-1", "title": "Vibration"},
                        {"doc_id": "kb-bearing-2", "title": "Bearings"},
                    ]
                },
            ),
        )
    )
    assert _tool_names(request) == {"get_knowledge_doc"}
    assert _parameter_enum(request, "get_knowledge_doc", "doc_id") == [
        "kb-vibration-1",
        "kb-bearing-2",
    ]
    assert _schema_kinds(request) == {"TOOL"}


def test_document_depth_request_stops_truthfully_when_no_structured_doc_id_exists() -> None:
    prompt = "Pesquise a base de conhecimento e abra o documento mais relevante antes de responder."
    request = _source().build_request(
        _context(
            prompt,
            _observation(
                "search_knowledge",
                {
                    "items": [
                        {"id": "generic-id-must-not-authorize", "text": "doc_id=kb-in-prose"}
                    ]
                },
            ),
        )
    )
    assert request.tools == ()
    assert "FINAL" in _schema_kinds(request)


def test_failed_search_does_not_trigger_document_or_retry_loop() -> None:
    prompt = "Search the knowledge base and open the most relevant document."
    request = _source().build_request(
        _context(
            prompt,
            _observation(
                "search_knowledge",
                {"error": "upstream unavailable"},
                status="error",
                status_code=503,
            ),
        )
    )
    assert request.tools == ()
    assert "FINAL" in _schema_kinds(request)


def test_document_depth_request_can_terminal_after_document_observation() -> None:
    prompt = "Search the knowledge base and open the most relevant document."
    request = _source().build_request(
        _context(
            prompt,
            _observation(
                "search_knowledge",
                {"items": [{"doc_id": "kb-bearing-2"}]},
            ),
            _observation(
                "get_knowledge_doc",
                {"doc_id": "kb-bearing-2", "content": "Inspect bearing defect frequencies."},
            ),
        )
    )
    assert request.tools == ()
    assert "FINAL" in _schema_kinds(request)


def test_non_knowledge_request_still_delegates_to_v14_grounding() -> None:
    identity = _observation(
        "get_current_user", {"data": {"company": {"id": "comp_forja_br"}}}
    )
    fleet = _observation(
        "list_assets_by_company",
        {"data": {"assets": [{"id": "asset_M101", "name": "Motor principal da forja"}]}},
    )
    request = _source().build_request(_context("Analise o RMS do M101.", identity, fleet))
    assert _tool_names(request) == {"get_rms"}
    assert _parameter_enum(request, "get_rms", "asset_id") == ["asset_M101"]
    assert _schema_kinds(request) == {"TOOL"}
