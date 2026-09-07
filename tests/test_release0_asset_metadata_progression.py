from __future__ import annotations

from academy_tractian.cloudflare_provider_client import CLOUDFLARE_GLM_MODEL_ID
from academy_tractian.release_provider_v10 import (
    Release0CloudflareDecisionClientV10,
    Release0ProviderDecisionSourceV10,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerObservation


class NeverCalledTransport:
    def post_json(self, request):  # pragma: no cover - construction-only regression
        raise AssertionError("provider transport must not be called")


def _source() -> Release0ProviderDecisionSourceV10:
    client = Release0CloudflareDecisionClientV10(
        api_token="test-token",
        account_id="abc123",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        transport=NeverCalledTransport(),
    )
    return Release0ProviderDecisionSourceV10(
        client=client,
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


def test_asset_metadata_read_is_not_offered_after_asset_discovery() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"company_id": "comp_papel_sul"}),
            _observation(
                "list_assets_by_company",
                {"data": {"assets": [{"id": "asset_R310"}, {"id": "asset_R420"}]}},
            ),
        )
    )

    assert "get_asset" not in _tool_names(request)
    assert _tool_names(request) == {
        "list_analyses",
        "get_rms",
        "get_spectrum",
    }


def test_successful_asset_metadata_read_cannot_loop_on_get_asset() -> None:
    request = _source().build_request(
        _context(
            _observation("get_current_user", {"company_id": "comp_papel_sul"}),
            _observation(
                "list_assets_by_company",
                {"data": {"assets": [{"id": "asset_R310"}, {"id": "asset_R420"}]}},
            ),
            _observation("get_asset", {"data": {"id": "asset_R310"}}),
        )
    )

    names = _tool_names(request)
    assert "get_asset" not in names
    assert names == {"list_analyses", "get_rms", "get_spectrum"}
