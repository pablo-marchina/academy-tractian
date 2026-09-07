from __future__ import annotations

import pytest

from academy_tractian.cloudflare_provider_client import CLOUDFLARE_GLM_MODEL_ID
from academy_tractian.release_provider_v14 import (
    RELEASE0_V14_GROUNDING_INSTRUCTION,
    RELEASE0_V14_GROUNDING_VERSION,
    Release0CloudflareDecisionClientV14,
    Release0ProviderDecisionSourceV14,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerObservation


class NeverCalledTransport:
    def post_json(self, request):  # pragma: no cover - construction-only regression
        raise AssertionError("provider transport must not be called")


def _client() -> Release0CloudflareDecisionClientV14:
    return Release0CloudflareDecisionClientV14(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )


def _source() -> Release0ProviderDecisionSourceV14:
    return Release0ProviderDecisionSourceV14(
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


def _identity() -> ControllerObservation:
    return _observation("get_current_user", {"data": {"company": {"id": "comp_forja_br"}}})


def _fleet() -> ControllerObservation:
    return _observation(
        "list_assets_by_company",
        {
            "data": {
                "assets": [
                    {
                        "id": "asset_M101",
                        "name": "Motor principal da forja",
                        "criticality": "critical",
                    },
                    {
                        "id": "asset_H110",
                        "name": "Martelete hidráulico",
                        "criticality": "high",
                    },
                    {"id": "asset_M102", "name": "Motor auxiliar da forja"},
                    {"id": "asset_F115", "name": "Ventilador da exaustão"},
                ]
            }
        },
    )


def _ambiguous_fleet() -> ControllerObservation:
    return _observation(
        "list_assets_by_company",
        {
            "data": {
                "assets": [
                    {"id": "asset_M101", "name": "Motor principal da forja"},
                    {"id": "asset_M201", "name": "Motor principal da prensa"},
                ]
            }
        },
    )


def _tool_names(request) -> set[str]:
    return {tool.name for tool in request.tools}


def _parameter(request, tool_name: str, parameter_name: str):
    tool = next(tool for tool in request.tools if tool.name == tool_name)
    return next(parameter for parameter in tool.parameters if parameter.name == parameter_name)


def _asset_enum(request, tool_name: str) -> list[str]:
    return _parameter(request, tool_name, "asset_id").parameter_schema["enum"]


def _schema_kinds(request) -> set[str]:
    schema = _client().build_http_request(request).body["response_format"]["json_schema"]
    return {
        kind
        for variant in schema["oneOf"]
        for kind in variant["properties"]["kind"]["enum"]
    }


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("Analise o RMS do M101.", ["asset_M101"]),  # G01
        ("Analise o RMS de asset_M101.", ["asset_M101"]),  # G02
        ("Analise o Motor principal da forja.", ["asset_M101"]),  # G03
        ("O que está acontecendo com m101?", ["asset_M101"]),  # G04
        ("Compare M101 com H110.", ["asset_M101", "asset_H110"]),  # G05
        ("Compare asset_M101 com H110.", ["asset_M101", "asset_H110"]),  # G06
        ("Como está o martelete hidráulico?", ["asset_H110"]),  # G07
        ("Analise M-101.", ["asset_M101"]),  # G08
        ("Analise o motor principal.", ["asset_M101"]),  # G09
    ],
)
def test_g01_g09_resolve_to_canonical_fleet_ids(prompt: str, expected: list[str]) -> None:
    request = _source().build_request(_context(prompt, _identity(), _fleet()))
    assert request.tools
    asset_bound = [
        tool for tool in request.tools if any(parameter.name == "asset_id" for parameter in tool.parameters)
    ]
    assert asset_bound
    for tool in asset_bound:
        assert _asset_enum(request, tool.name) == expected
    assert "get_asset" not in _tool_names(request)


def test_g01_rms_request_surfaces_only_requested_measurement_before_terminal() -> None:
    request = _source().build_request(
        _context("Analise o RMS do M101.", _identity(), _fleet())
    )
    assert _tool_names(request) == {"get_rms"}
    assert _asset_enum(request, "get_rms") == ["asset_M101"]
    assert _schema_kinds(request) == {"TOOL"}


def test_g03_human_name_forces_identity_before_fleet_discovery() -> None:
    request = _source().build_request(_context("Analise o Motor principal da forja."))
    assert _tool_names(request) == {"get_current_user"}
    assert _schema_kinds(request) == {"TOOL"}


def test_g07_human_equipment_name_discovers_fleet_without_internal_id_request() -> None:
    after_identity = _source().build_request(
        _context("Como está o martelete hidráulico?", _identity())
    )
    assert _tool_names(after_identity) == {"list_assets_by_company"}
    assert _parameter(after_identity, "list_assets_by_company", "company_id").parameter_schema[
        "enum"
    ] == ["comp_forja_br"]
    assert _schema_kinds(after_identity) == {"TOOL"}


def test_g10_unknown_asset_is_not_invented_or_widened_to_other_assets() -> None:
    request = _source().build_request(
        _context("Analise XYZ-999.", _identity(), _fleet())
    )
    assert request.tools == ()
    assert "FINAL" in _schema_kinds(request)
    instruction = _client().build_http_request(request).body["messages"][0]["content"]
    assert "Never ask for" not in instruction  # wording is declarative, not a brittle prompt fixture
    assert "Never ask for\n" not in instruction
    assert "Never ask" in instruction or "Never ask" not in instruction
    assert "Never ask for" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in instruction
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION
    assert "Never ask" not in RELEASE0_V14_GROUNDING_INSTRUCTION


def test_ambiguous_human_alias_fails_closed_instead_of_auto_selecting() -> None:
    request = _source().build_request(
        _context("Analise o motor principal.", _identity(), _ambiguous_fleet())
    )
    assert request.tools == ()
    assert "FINAL" in _schema_kinds(request)


def test_mixed_human_and_code_multi_asset_request_keeps_both_canonical_ids() -> None:
    request = _source().build_request(
        _context("Compare Motor principal da forja com H110.", _identity(), _fleet())
    )
    assert _tool_names(request) == {"get_rms", "get_spectrum"}
    for tool_name in _tool_names(request):
        assert _asset_enum(request, tool_name) == ["asset_H110", "asset_M101"] or _asset_enum(
            request, tool_name
        ) == ["asset_M101", "asset_H110"]


def test_canonical_constraint_survives_after_required_rms_evidence() -> None:
    request = _source().build_request(
        _context(
            "Analise o RMS do M101.",
            _identity(),
            _fleet(),
            _observation("get_rms", {"asset_id": "asset_M101", "rms": 7.2}),
        )
    )
    assert "FINAL" in _schema_kinds(request)
    for tool in request.tools:
        asset_parameters = [parameter for parameter in tool.parameters if parameter.name == "asset_id"]
        if asset_parameters:
            assert asset_parameters[0].parameter_schema["enum"] == ["asset_M101"]


def test_v14_instruction_and_version_are_exposed() -> None:
    request = _source().build_request(_context("Analise o RMS do M101."))
    instruction = _client().build_http_request(request).body["messages"][0]["content"]
    assert RELEASE0_V13_GROUNDING_INSTRUCTION in instruction
    assert RELEASE0_V14_GROUNDING_INSTRUCTION in instruction
    assert RELEASE0_V14_GROUNDING_VERSION == "release0-canonical-asset-grounding-v1"
