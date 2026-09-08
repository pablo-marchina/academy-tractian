from __future__ import annotations

from academy_tractian.cloudflare_provider_client import CLOUDFLARE_GLM_MODEL_ID
from academy_tractian.release_provider_v11 import RELEASE0_V11_RESPONSE_MODE_INSTRUCTION
from academy_tractian.release_provider_v12 import (
    RELEASE0_V12_GROUNDING_INSTRUCTION,
    RELEASE0_V12_GROUNDING_VERSION,
    Release0CloudflareDecisionClientV12,
    Release0ProviderDecisionSourceV12,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerObservation


class NeverCalledTransport:
    def post_json(self, request):  # pragma: no cover - construction-only regression
        raise AssertionError("provider transport must not be called")


def _client() -> Release0CloudflareDecisionClientV12:
    return Release0CloudflareDecisionClientV12(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )


def _source() -> Release0ProviderDecisionSourceV12:
    return Release0ProviderDecisionSourceV12(
        client=_client(),
        registry=canonical_tool_registry(),
    )


def _observation(tool_name: str, body) -> ControllerObservation:
    return ControllerObservation(
        tool_name=tool_name,
        status="success",
        executed=True,
        status_code=200,
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


def _parameter(request, tool_name: str, parameter_name: str):
    tool = next(tool for tool in request.tools if tool.name == tool_name)
    return next(parameter for parameter in tool.parameters if parameter.name == parameter_name)


def _schema_kinds(request) -> set[str]:
    schema = _client().build_http_request(request).body["response_format"]["json_schema"]
    return {
        kind
        for variant in schema["oneOf"]
        for kind in variant["properties"]["kind"]["enum"]
    }


def _identity() -> ControllerObservation:
    return _observation("get_current_user", {"data": {"company": {"id": "comp_papel_sul"}}})


def _assets(*asset_ids: str) -> ControllerObservation:
    return _observation(
        "list_assets_by_company",
        {"data": {"assets": [{"id": asset_id} for asset_id in asset_ids]}},
    )


def test_explicit_asset_comparison_discovers_company_assets_without_literal_asset_word() -> None:
    prompt = "Compare R310 e R420 e diga qual merece prioridade de manutenção, explicando a evidência."
    request = _source().build_request(_context(prompt, _identity()))

    assert _tool_names(request) == {"list_assets_by_company"}
    assert _parameter(request, "list_assets_by_company", "company_id").parameter_schema["enum"] == [
        "comp_papel_sul"
    ]
    assert _schema_kinds(request) == {"TOOL"}


def test_explicit_asset_comparison_requires_condition_evidence_for_both_assets() -> None:
    prompt = "Compare R310 e R420 e diga qual merece prioridade de manutenção, explicando a evidência."
    request = _source().build_request(
        _context(prompt, _identity(), _assets("asset_R310", "asset_R420"))
    )

    assert _tool_names(request) == {"get_rms", "get_spectrum"}
    for tool_name in _tool_names(request):
        assert _parameter(request, tool_name, "asset_id").parameter_schema["enum"] == [
            "asset_R310",
            "asset_R420",
        ]
    assert _schema_kinds(request) == {"TOOL"}

    after_r310 = _source().build_request(
        _context(
            prompt,
            _identity(),
            _assets("asset_R310", "asset_R420"),
            _observation("get_rms", {"asset_id": "asset_R310", "rms": 7.2}),
        )
    )
    assert _tool_names(after_r310) == {"get_rms", "get_spectrum", "list_analyses"}
    for tool_name in ("get_rms", "get_spectrum", "list_analyses"):
        assert _parameter(after_r310, tool_name, "asset_id").parameter_schema["enum"] == [
            "asset_R420"
        ]
    assert _schema_kinds(after_r310) == {"TOOL"}

    after_both = _source().build_request(
        _context(
            prompt,
            _identity(),
            _assets("asset_R310", "asset_R420"),
            _observation("get_rms", {"asset_id": "asset_R310", "rms": 7.2}),
            _observation("get_spectrum", {"asset_id": "asset_R420", "peaks": [3.0]}),
        )
    )
    assert "FINAL" in _schema_kinds(after_both)
    assert "get_asset" not in _tool_names(after_both)


def test_missing_explicit_asset_label_stops_without_requesting_internal_id() -> None:
    prompt = "Compare R310 e R420 e diga qual merece prioridade de manutenção, explicando a evidência."
    request = _source().build_request(
        _context(prompt, _identity(), _assets("asset_R310", "asset_V301"))
    )

    assert request.tools == ()
    assert "FINAL" in _schema_kinds(request)
    http_request = _client().build_http_request(request)
    instruction = http_request.body["messages"][0]["content"]
    assert "Do not ask for its internal asset_id" in instruction
    assert "Do not ask" in instruction


def test_causal_certainty_prompt_for_r310_cannot_ask_for_discoverable_asset_id() -> None:
    prompt = "Existe evidência suficiente para afirmar com certeza a causa da falha do R310?"
    request = _source().build_request(_context(prompt, _identity()))

    assert _tool_names(request) == {"list_assets_by_company"}
    assert _schema_kinds(request) == {"TOOL"}

    after_assets = _source().build_request(
        _context(prompt, _identity(), _assets("asset_R310", "asset_R420"))
    )
    assert {"get_rms", "get_spectrum", "list_analyses"} == _tool_names(after_assets)
    for tool_name in _tool_names(after_assets):
        assert _parameter(after_assets, tool_name, "asset_id").parameter_schema["enum"] == [
            "asset_R310"
        ]
    assert _schema_kinds(after_assets) == {"TOOL"}


def test_data_quality_trust_prompt_requires_quality_then_condition_evidence() -> None:
    prompt = "A qualidade dos dados do ativo R310 é suficiente para confiar no diagnóstico atual?"
    after_assets = _source().build_request(
        _context(prompt, _identity(), _assets("asset_R310", "asset_R420"))
    )

    assert _tool_names(after_assets) == {"get_data_quality"}
    assert _parameter(after_assets, "get_data_quality", "asset_id").parameter_schema["enum"] == [
        "asset_R310"
    ]
    assert _schema_kinds(after_assets) == {"TOOL"}

    after_quality = _source().build_request(
        _context(
            prompt,
            _identity(),
            _assets("asset_R310", "asset_R420"),
            _observation(
                "get_data_quality",
                {"asset_id": "asset_R310", "coverage": 0.98},
            ),
        )
    )
    assert _tool_names(after_quality) == {"get_rms", "get_spectrum", "list_analyses"}
    assert _schema_kinds(after_quality) == {"TOOL"}

    after_condition = _source().build_request(
        _context(
            prompt,
            _identity(),
            _assets("asset_R310", "asset_R420"),
            _observation(
                "get_data_quality",
                {"asset_id": "asset_R310", "coverage": 0.98},
            ),
            _observation("get_rms", {"asset_id": "asset_R310", "rms": 7.2}),
        )
    )
    assert "FINAL" in _schema_kinds(after_condition)
    assert "get_asset" not in _tool_names(after_condition)


def test_pure_data_quality_question_can_stop_after_quality_evidence() -> None:
    prompt = "Como está a qualidade dos dados do ativo R310?"
    after_quality = _source().build_request(
        _context(
            prompt,
            _identity(),
            _assets("asset_R310", "asset_R420"),
            _observation(
                "get_data_quality",
                {"asset_id": "asset_R310", "coverage": 0.98},
            ),
        )
    )

    assert "FINAL" in _schema_kinds(after_quality)
    assert "get_asset" not in _tool_names(after_quality)


def test_v12_preserves_v11_response_modes_and_adds_grounding_contract() -> None:
    request = _source().build_request(
        _context("Summarize the available evidence.")
    )
    instruction = _client().build_http_request(request).body["messages"][0]["content"]

    assert RELEASE0_V11_RESPONSE_MODE_INSTRUCTION in instruction
    assert RELEASE0_V12_GROUNDING_INSTRUCTION in instruction
    assert RELEASE0_V12_GROUNDING_VERSION == "release0-explicit-asset-grounding-v1"
