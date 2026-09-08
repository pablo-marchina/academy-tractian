from __future__ import annotations

from academy_tractian.cloudflare_provider_client import CLOUDFLARE_GLM_MODEL_ID
from academy_tractian.release_provider_v12 import RELEASE0_V12_GROUNDING_INSTRUCTION
from academy_tractian.release_provider_v13 import (
    RELEASE0_V13_GROUNDING_INSTRUCTION,
    RELEASE0_V13_GROUNDING_VERSION,
    Release0CloudflareDecisionClientV13,
    Release0ProviderDecisionSourceV13,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerObservation


class NeverCalledTransport:
    def post_json(self, request):  # pragma: no cover - construction-only regression
        raise AssertionError("provider transport must not be called")


def _client() -> Release0CloudflareDecisionClientV13:
    return Release0CloudflareDecisionClientV13(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )


def _source() -> Release0ProviderDecisionSourceV13:
    return Release0ProviderDecisionSourceV13(
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


def test_live_causal_prompt_forces_identity_before_any_terminal() -> None:
    prompt = "Qual é a causa mais provável do problema do R310 e qual o grau de certeza dessa conclusão?"

    initial = _source().build_request(_context(prompt))
    assert _tool_names(initial) == {"get_current_user"}
    assert _schema_kinds(initial) == {"TOOL"}

    after_identity = _source().build_request(_context(prompt, _identity()))
    assert _tool_names(after_identity) == {"list_assets_by_company"}
    assert _schema_kinds(after_identity) == {"TOOL"}


def test_comparison_prompt_also_forces_identity_from_zero_observations() -> None:
    prompt = "Compare R310 e R420 e diga qual está mais crítico, explicando a evidência usada para chegar à conclusão."

    initial = _source().build_request(_context(prompt))
    assert _tool_names(initial) == {"get_current_user"}
    assert _schema_kinds(initial) == {"TOOL"}


def test_completed_single_asset_data_quality_read_is_not_reoffered_after_condition() -> None:
    prompt = "A qualidade dos dados do ativo R310 é suficiente para confiar no diagnóstico atual?"
    context = _context(
        prompt,
        _identity(),
        _assets("asset_R310", "asset_R420"),
        _observation("get_data_quality", {"quality": "available"}),
        _observation("get_spectrum", {"asset_id": "asset_R310", "peaks": [3.0]}),
    )

    request = _source().build_request(context)
    assert "get_data_quality" not in _tool_names(request)
    assert "get_asset" not in _tool_names(request)
    assert "FINAL" in _schema_kinds(request)


def test_pure_quality_read_is_not_reoffered_after_success() -> None:
    prompt = "Como está a qualidade dos dados do ativo R310?"
    request = _source().build_request(
        _context(
            prompt,
            _identity(),
            _assets("asset_R310"),
            _observation("get_data_quality", {"coverage": 0.98}),
        )
    )

    assert "get_data_quality" not in _tool_names(request)
    assert "FINAL" in _schema_kinds(request)


def test_repeated_identical_single_asset_rms_is_removed_from_next_surface() -> None:
    prompt = "Why is R310 vibrating more than usual? Identify the most likely mechanism only if the evidence supports it."
    repeated = {"asset_id": "asset_R310", "point_id": "ftf", "rms": [1.2, 1.3, 1.4]}
    request = _source().build_request(
        _context(
            prompt,
            _identity(),
            _assets("asset_R310"),
            _observation("get_rms", repeated),
            _observation("get_rms", repeated),
        )
    )

    names = _tool_names(request)
    assert "get_rms" not in names
    assert "get_spectrum" in names
    assert "FINAL" in _schema_kinds(request)


def test_distinct_single_asset_rms_observations_remain_eligible() -> None:
    prompt = "Why is R310 vibrating more than usual? Identify the most likely mechanism only if the evidence supports it."
    request = _source().build_request(
        _context(
            prompt,
            _identity(),
            _assets("asset_R310"),
            _observation(
                "get_rms",
                {"asset_id": "asset_R310", "point_id": "de", "rms": [1.2, 1.3]},
            ),
            _observation(
                "get_rms",
                {"asset_id": "asset_R310", "point_id": "nde", "rms": [1.5, 1.7]},
            ),
        )
    )

    assert "get_rms" in _tool_names(request)


def test_v13_preserves_v12_grounding_instruction() -> None:
    request = _source().build_request(_context("Summarize the available evidence."))
    instruction = _client().build_http_request(request).body["messages"][0]["content"]

    assert RELEASE0_V12_GROUNDING_INSTRUCTION in instruction
    assert RELEASE0_V13_GROUNDING_INSTRUCTION in instruction
    assert RELEASE0_V13_GROUNDING_VERSION == "release0-initial-asset-grounding-v2"
