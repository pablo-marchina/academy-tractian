from __future__ import annotations

from academy_tractian.cloudflare_provider_client import CLOUDFLARE_GLM_MODEL_ID
from academy_tractian.release_provider import Release0CloudflareDecisionClient
from academy_tractian.release_provider_v10 import Release0ProviderDecisionSourceV10
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerObservation


class NeverCalledTransport:
    def post_json(self, request):  # pragma: no cover - construction-only regression
        raise AssertionError("provider transport must not be called")


def _client() -> Release0CloudflareDecisionClient:
    return Release0CloudflareDecisionClient(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )


def _source() -> Release0ProviderDecisionSourceV10:
    return Release0ProviderDecisionSourceV10(
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


def _context(*observations: ControllerObservation) -> ControllerContext:
    return ControllerContext(
        user_request="Qual ativo tem maior criticidade e o que está acontecendo?",
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


def test_nested_asset_collection_advances_to_asset_scoped_reads() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"data": {"company": {"id": "comp_papel_sul"}}}),
            _observation(
                "list_assets_by_company",
                {
                    "response": {
                        "data": {
                            "assets": [
                                {"id": "asset_R310", "name": "R310"},
                                {"id": "asset_R420", "name": "R420"},
                            ]
                        }
                    }
                },
            ),
        )
    )

    expected = {
        "get_asset",
        "list_analyses",
        "get_baseline",
        "get_rms",
        "get_spectrum",
        "get_data_quality",
    }
    assert _tool_names(request) == expected
    assert "get_current_user" not in _tool_names(request)
    assert "list_assets_by_company" not in _tool_names(request)
    for tool_name in expected:
        assert _parameter(request, tool_name, "asset_id").parameter_schema["enum"] == [
            "asset_R310",
            "asset_R420",
        ]
    assert _schema_kinds(request) == {"TOOL"}


def test_generic_data_wrapper_accepts_only_resource_prefixed_generic_ids() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"company_id": "comp_papel_sul"}),
            _observation(
                "list_assets_by_company",
                {
                    "request": {"id": "request_123"},
                    "data": [
                        {"id": "asset_R310"},
                        {"id": "asset_R420"},
                        {"id": "metadata_ignored"},
                    ],
                },
            ),
        )
    )

    assert _parameter(request, "list_analyses", "asset_id").parameter_schema["enum"] == [
        "asset_R310",
        "asset_R420",
    ]


def test_nested_analysis_collection_advances_to_grounded_analysis_read() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"company_id": "comp_papel_sul"}),
            _observation(
                "list_assets_by_company",
                {"data": {"assets": [{"id": "asset_R310"}]}},
            ),
            _observation(
                "list_analyses",
                {"payload": {"results": {"analyses": [{"id": "analysis_123"}]}}},
            ),
        )
    )

    assert "list_analyses" not in _tool_names(request)
    assert "get_analysis" in _tool_names(request)
    assert _parameter(request, "get_analysis", "analysis_id").parameter_schema == {
        "enum": ["analysis_123"]
    }
    assert "get_current_user" not in _tool_names(request)
    assert _schema_kinds(request) == {"TOOL"}


def test_unparseable_asset_collection_fails_closed_instead_of_reoffering_identity() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"company_id": "comp_papel_sul"}),
            _observation(
                "list_assets_by_company",
                {"data": {"metadata": {"id": "request_123"}}},
            ),
        )
    )

    assert request.tools == ()
    assert "get_current_user" not in _tool_names(request)
    assert {"FINAL", "CLARIFY", "ESCALATE", "ABSTAIN"} <= _schema_kinds(request)


def test_successful_current_user_is_not_reoffered_on_non_asset_request() -> None:
    context = ControllerContext(
        user_request="Who am I?",
        turn_index=1,
        tool_call_count=1,
        observations=(
            _observation("get_current_user", {"company_id": "comp_papel_sul"}),
        ),
    )

    request = _source().build_request(context)
    assert "get_current_user" not in _tool_names(request)
    assert "FINAL" in _schema_kinds(request)
