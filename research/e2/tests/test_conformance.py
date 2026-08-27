from research.e2.conformance import compare_registry_to_contract, derive_contract_signatures
from research.e2.models import ToolKind, ToolParameter, ToolSpec


def test_contract_derivation_removes_runner_seed_and_adds_body():
    spec = {
        "paths": {
            "/assets/{assetId}": {
                "patch": {
                    "operationId": "updateAssetConfig",
                    "parameters": [{"name": "assetId", "in": "path", "required": True}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}},
                }
            },
            "/assets/{assetId}/rms": {
                "get": {
                    "operationId": "getRmsSeries",
                    "parameters": [
                        {"name": "seed", "in": "query", "required": False},
                        {"name": "assetId", "in": "path", "required": True},
                    ],
                }
            },
        }
    }
    signatures = derive_contract_signatures(spec, parameter_transformations={"assetId": "asset_id"})
    assert signatures["updateAssetConfig"]["parameters"] == (("asset_id", "path", True), ("body", "body", True))
    assert signatures["getRmsSeries"]["parameters"] == (("asset_id", "path", True),)
    assert signatures["getRmsSeries"]["seed_supported"] is True


def test_registry_conformance_detects_and_clears_mismatch():
    spec = {"paths": {"/x/{assetId}": {"get": {"operationId": "getX", "parameters": [{"name": "assetId", "in": "path", "required": True}]}}}}
    good = ToolSpec(name="get_x", operation_id="getX", method="GET", path_template="/x/{assetId}", kind=ToolKind.READ, parameters=[ToolParameter(name="asset_id", location="path", required=True)])
    bad = good.model_copy(update={"method": "POST"})
    assert compare_registry_to_contract(spec=spec, registry={"get_x": good}, parameter_transformations={"assetId": "asset_id"}) == ()
    findings = compare_registry_to_contract(spec=spec, registry={"get_x": bad}, parameter_transformations={"assetId": "asset_id"})
    assert any(f.code == "REGISTRY_METHOD_MISMATCH" for f in findings)
