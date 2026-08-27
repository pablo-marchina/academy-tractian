from __future__ import annotations
from .models import ActionImpact, Permission, ToolKind, ToolParameter, ToolSpec

# Source provenance for the delivered agent-facing contract. The OpenAPI YAML
# repeats /assets/{assetId} as two mapping keys (GET and PATCH). Duplicate-aware
# normalization plus executable implementation/tests confirm both operations.
SOURCE_OPENAPI_SHA256 = "8b3fdc5da50a8fa2923928a2f5aebcfe5034c622dba222df84f56abcd0b4aabf"
SOURCE_IMPLEMENTATION_SHA256 = "a9bdfb8a5fc85e8f169438984f787ad5fd0db95cdd2dc41a15e05ca363a3ca78"
SOURCE_TESTS_SHA256 = "b50fbabe2f497290a01984ba0663bb0b787184f0bc1b367e90871d0912326443"
NORMALIZED_OPERATION_COUNT = 18
UNIQUE_PATH_TEMPLATE_COUNT = 17

def p(name: str, location: str, required: bool = False, schema: dict | None = None) -> ToolParameter:
    return ToolParameter(name=name, location=location, required=required, schema=schema or {})  # type: ignore[arg-type]

def read(name: str, op: str, path: str, params: list[ToolParameter], *, scope: str = "resource", identity: bool = False, seed_supported: bool = True) -> ToolSpec:
    return ToolSpec(name=name, operation_id=op, method="GET", path_template=path, kind=ToolKind.READ, parameters=params, target_scope=scope, identity_required=identity, seed_supported=seed_supported)  # type: ignore[arg-type]

def action(name: str, op: str, method: str, path: str, params: list[ToolParameter], permission: Permission, impact: ActionImpact) -> ToolSpec:
    return ToolSpec(name=name, operation_id=op, method=method, path_template=path, kind=ToolKind.ACTION, impact=impact, parameters=params, required_permissions=[permission], target_scope="resource", justification_required=True, minimum_justification_length=20, identity_required=True, action_persistence="accepted_event_non_persistent", seed_supported=False)  # type: ignore[arg-type]

TOOLS: tuple[ToolSpec, ...] = (
    read("get_company", "getCompany", "/companies/{companyId}", [p("company_id", "path", True)], scope="company_resource"),
    read("list_assets_by_company", "listAssetsByCompany", "/companies/{companyId}/assets", [p("company_id", "path", True)], scope="company_resource"),
    read("get_current_user", "getCurrentUser", "/users/me", [], scope="none", identity=True, seed_supported=False),
    read("get_asset", "getAsset", "/assets/{assetId}", [p("asset_id", "path", True)]),
    action("update_asset_config", "updateAssetConfig", "PATCH", "/assets/{assetId}", [p("asset_id", "path", True), p("body", "body", True, {"$ref": "#/components/schemas/ActionRequest"})], Permission.ACTION_HIGH, ActionImpact.HIGH),
    read("list_analyses", "listAnalyses", "/assets/{assetId}/analyses", [p("asset_id", "path", True), p("status", "query", False, {"type": "string", "enum": ["current", "stale", "pending", "inconclusive"]})]),
    read("get_analysis", "getAnalysis", "/analyses/{analysisId}", [p("analysis_id", "path", True)]),
    action("reprocess_analysis", "reprocessAnalysis", "POST", "/analyses/{analysisId}/reprocess", [p("analysis_id", "path", True), p("body", "body", True, {"$ref": "#/components/schemas/ActionRequest"})], Permission.ACTION_LOW, ActionImpact.LOW),
    action("request_specialist_analysis", "requestSpecialistAnalysis", "POST", "/analyses/{analysisId}/request-specialist", [p("analysis_id", "path", True), p("body", "body", True, {"$ref": "#/components/schemas/ActionRequest"})], Permission.ACTION_LOW, ActionImpact.LOW),
    read("get_baseline", "getBaseline", "/assets/{assetId}/baseline", [p("asset_id", "path", True), p("point_id", "query")]),
    read("get_rms", "getRmsSeries", "/assets/{assetId}/rms", [p("asset_id", "path", True), p("point_id", "query")]),
    read("get_spectrum", "getSpectrum", "/assets/{assetId}/spectrum", [p("asset_id", "path", True), p("point_id", "query")]),
    read("get_data_quality", "getDataQuality", "/assets/{assetId}/data-quality", [p("asset_id", "path", True)]),
    read("get_model", "getModel", "/models/{modelId}", [p("model_id", "path", True)]),
    action("request_retraining", "requestRetraining", "POST", "/models/{modelId}/request-retraining", [p("model_id", "path", True), p("body", "body", True, {"$ref": "#/components/schemas/ActionRequest"})], Permission.ACTION_HIGH, ActionImpact.HIGH),
    read("search_knowledge", "searchKnowledge", "/knowledge/search", [p("q", "query", True, {"type": "string"}), p("type", "query", False, {"type": "string", "enum": ["procedure", "glossary", "guidance"]})], scope="none"),
    read("get_knowledge_doc", "getKnowledgeDoc", "/knowledge/{docId}", [p("doc_id", "path", True)], scope="none"),
    action("escalate_case", "escalateCase", "POST", "/cases/{caseId}/escalate", [p("case_id", "path", True), p("body", "body", True, {"$ref": "#/components/schemas/ActionRequest"})], Permission.ESCALATE, ActionImpact.WORKFLOW),
)

def get_tool(name: str) -> ToolSpec:
    for tool in TOOLS:
        if tool.name == name:
            return tool
    raise KeyError(name)

def validate_registry() -> None:
    assert len(TOOLS) == NORMALIZED_OPERATION_COUNT
    assert len({t.path_template for t in TOOLS}) == UNIQUE_PATH_TEMPLATE_COUNT
    assert len({(t.method, t.path_template) for t in TOOLS}) == NORMALIZED_OPERATION_COUNT
    assert len({t.operation_id for t in TOOLS}) == NORMALIZED_OPERATION_COUNT
    assert len({t.name for t in TOOLS}) == NORMALIZED_OPERATION_COUNT

    # Guard the duplicate-path normalization explicitly: the source YAML authors
    # both operations under repeated /assets/{assetId} keys.
    get_asset = get_tool("get_asset")
    update_asset = get_tool("update_asset_config")
    assert (get_asset.method, get_asset.path_template, get_asset.operation_id) == (
        "GET", "/assets/{assetId}", "getAsset"
    )
    assert (update_asset.method, update_asset.path_template, update_asset.operation_id) == (
        "PATCH", "/assets/{assetId}", "updateAssetConfig"
    )

    actions = [t for t in TOOLS if t.kind is ToolKind.ACTION]
    assert len(actions) == 5
    assert all(t.justification_required and t.minimum_justification_length == 20 for t in actions)
    assert all(t.identity_binding == "runner" for t in actions)
    assert all(t.target_scope == "resource" for t in actions)
    assert sum(t.seed_supported for t in TOOLS) == 12
