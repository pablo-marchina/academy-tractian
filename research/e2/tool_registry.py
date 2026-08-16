from __future__ import annotations
from .models import ActionImpact, Permission, ToolKind, ToolParameter, ToolSpec

def p(name: str, location: str, required: bool = False, schema: dict | None = None) -> ToolParameter:
    return ToolParameter(name=name, location=location, required=required, schema=schema or {})  # type: ignore[arg-type]

def read(name: str, op: str, path: str, params: list[ToolParameter], *, scope: str = "resource", identity: bool = False) -> ToolSpec:
    return ToolSpec(name=name, operation_id=op, method="GET", path_template=path, kind=ToolKind.READ, parameters=params, target_scope=scope, identity_required=identity)  # type: ignore[arg-type]

def action(name: str, op: str, method: str, path: str, params: list[ToolParameter], permission: Permission, impact: ActionImpact) -> ToolSpec:
    return ToolSpec(name=name, operation_id=op, method=method, path_template=path, kind=ToolKind.ACTION, impact=impact, parameters=params, required_permissions=[permission], justification_required=True, minimum_justification_length=20, identity_required=True, action_persistence="accepted_event_non_persistent")  # type: ignore[arg-type]

TOOLS: tuple[ToolSpec, ...] = (
    read("get_company", "getCompany", "/companies/{companyId}", [p("company_id", "path", True)], scope="company_resource"),
    read("list_assets_by_company", "listAssetsByCompany", "/companies/{companyId}/assets", [p("company_id", "path", True)], scope="company_resource"),
    read("get_current_user", "getCurrentUser", "/users/me", [], scope="none", identity=True),
    read("get_asset", "getAsset", "/assets/{assetId}", [p("asset_id", "path", True)]),
    action("update_asset_config", "updateAssetConfig", "PATCH", "/assets/{assetId}", [p("asset_id", "path", True), p("body", "body", True, {"$ref": "#/components/schemas/ActionRequest"})], Permission.ACTION_HIGH, ActionImpact.HIGH),
    read("list_analyses", "listAnalyses", "/assets/{assetId}/analyses", [p("asset_id", "path", True), p("status", "query", False, {"type": "string", "enum": ["current", "stale", "pending", "inconclusive"]})]),
    read("get_analysis", "getAnalysis", "/analyses/{analysisId}", [p("analysis_id", "path", True)]),
    action("reprocess_analysis", "reprocessAnalysis", "POST", "/analyses/{analysisId}/reprocess", [p("analysis_id", "path", True), p("body", "body", True, {"$ref": "#/components/schemas/ActionRequest"})], Permission.ACTION_LOW, ActionImpact.LOW),
    action("request_specialist_analysis", "requestSpecialistAnalysis", "POST", "/analyses/{analysisId}/request-specialist", [p("analysis_id", "path", True), p("body", "body", True, {"$ref": "#/components/schemas/ActionRequest"})], Permission.ACTION_LOW, ActionImpact.LOW),
    read("get_baseline", "getBaseline", "/assets/{assetId}/baseline", [p("asset_id", "path", True), p("point_id", "query")]),
    read("get_rms", "getRmsSeries", "/assets/{assetId}/rms", [p("asset_id", "path", True), p("point_id", "query")]),
    read("get_spectrum", "getSpectrum", "/assets/{assetId}/spectrum", [p("asset_id", "path", True), p("point_id", "query")]),
    read("get_data_quality", "getDataQuality", "/assets/{assetId}/data-quality", [p("asset_id", "path", True), p("point_id", "query")]),
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
    assert len(TOOLS) == 18
    assert len({t.path_template for t in TOOLS}) == 17
    assert len({t.name for t in TOOLS}) == 18
    actions = [t for t in TOOLS if t.kind is ToolKind.ACTION]
    assert len(actions) == 5
    assert all(t.justification_required and t.minimum_justification_length == 20 for t in actions)
    assert all(t.identity_binding == "runner" for t in actions)
