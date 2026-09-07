from __future__ import annotations

from academy_tractian.cloudflare_provider_client import CLOUDFLARE_GLM_MODEL_ID
from academy_tractian.release_provider import (
    RELEASE0_PROVIDER_SYSTEM_INSTRUCTION,
    Release0CloudflareDecisionClient,
    Release0ProviderDecisionSource,
)
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


def _source() -> Release0ProviderDecisionSource:
    return Release0ProviderDecisionSource(
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


def _schema(request):
    return _client().build_http_request(request).body["response_format"]["json_schema"]


def _tool_names(request) -> set[str]:
    return {tool.name for tool in request.tools}


def _parameter(request, tool_name: str, parameter_name: str):
    tool = next(tool for tool in request.tools if tool.name == tool_name)
    return next(parameter for parameter in tool.parameters if parameter.name == parameter_name)


def _schema_kinds(schema) -> set[str]:
    return {
        kind
        for variant in schema["oneOf"]
        for kind in variant["properties"]["kind"]["enum"]
    }


def test_release0_instruction_forbids_requesting_discoverable_resource_ids() -> None:
    for fragment in (
        "Never ask the customer to supply company_id, asset_id, analysis_id",
        "list that company's assets",
        "Missing an identifier is not a reason to clarify when a safe read can discover it",
        "Comparative claims require asset evidence",
        "diagnostic claims require analysis or technical evidence",
    ):
        assert fragment in RELEASE0_PROVIDER_SYSTEM_INSTRUCTION


def test_asset_investigation_uses_company_id_from_current_user_before_terminal() -> None:
    request = _source().build_request(
        _context(
            _observation(
                "get_current_user",
                {"user_id": "user-1", "company_id": "company-1"},
            )
        )
    )

    assert _tool_names(request) == {"list_assets_by_company"}
    assert _parameter(request, "list_assets_by_company", "company_id").parameter_schema == {
        "enum": ["company-1"]
    }
    assert _schema_kinds(_schema(request)) == {"TOOL"}


def test_asset_investigation_uses_asset_ids_from_list_before_terminal() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"company": {"id": "company-1"}}),
            _observation(
                "list_assets_by_company",
                {"items": [{"id": "asset-1"}, {"asset_id": "asset-2"}]},
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
    for tool_name in expected:
        assert _parameter(request, tool_name, "asset_id").parameter_schema["enum"] == [
            "asset-1",
            "asset-2",
        ]
    assert _schema_kinds(_schema(request)) == {"TOOL"}


def test_asset_investigation_can_follow_observed_analysis_id_without_repeating_list() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"company_id": "company-1"}),
            _observation("list_assets_by_company", {"assets": [{"id": "asset-1"}]}),
            _observation("list_analyses", {"analyses": [{"id": "analysis-1"}]}),
        )
    )

    assert "list_analyses" not in _tool_names(request)
    assert "get_analysis" in _tool_names(request)
    assert _parameter(request, "get_analysis", "analysis_id").parameter_schema == {
        "enum": ["analysis-1"]
    }
    assert _schema_kinds(_schema(request)) == {"TOOL"}


def test_terminal_choices_return_after_real_diagnostic_evidence() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"company_id": "company-1"}),
            _observation("list_assets_by_company", {"assets": [{"id": "asset-1"}]}),
            _observation("list_analyses", {"analyses": [{"id": "analysis-1"}]}),
            _observation(
                "get_analysis",
                {"id": "analysis-1", "status": "current", "diagnosis": "bearing wear"},
            ),
        )
    )

    assert len(request.tools) == 13
    assert {"FINAL", "CLARIFY", "ESCALATE", "ABSTAIN"} <= _schema_kinds(_schema(request))


def test_non_asset_request_is_not_forced_into_asset_discovery() -> None:
    context = ControllerContext(
        user_request="Who am I?",
        turn_index=1,
        tool_call_count=1,
        observations=(
            _observation("get_current_user", {"company_id": "company-1"}),
        ),
    )
    request = _source().build_request(context)

    assert len(request.tools) == 13
    assert "FINAL" in _schema_kinds(_schema(request))
