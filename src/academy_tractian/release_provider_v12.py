from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
import re
from typing import Any

from research.e2.tool_registry import TOOLS

from .cloudflare_provider_client import CLOUDFLARE_PROVIDER_ID
from .decision_source import ProviderCallIdentity, ProviderDecisionRequest, ProviderDecisionSource
from .production_config import RemoteProductionConfig
from .provider_clients import ProviderHttpRequest, UrllibProviderJsonTransport
from .release_provider import (
    RELEASE0_PROVIDER_DECISION_JSON_SCHEMA,
    _constrain_tool_parameter,
    _extract_company_ids,
    _normalized_request,
    _provider_audit_model_id,
    _successful_observation,
    _terminal_variants_for_request,
    _tool_variant,
    validate_release_provider_config,
)
from .release_provider_v10 import (
    Release0ProviderDecisionSourceV10,
    _extract_collection_ids_v10,
)
from .release_provider_v11 import Release0CloudflareDecisionClientV11


RELEASE0_V12_GROUNDING_VERSION = "release0-explicit-asset-grounding-v1"
_RELEASE0_V12_ASSET_LABEL_PATTERN = re.compile(
    r"(?<![a-z0-9])([a-z]{1,8}(?:[-_][a-z]{1,4})?[-_]?\d{1,8})(?![a-z0-9])",
    re.IGNORECASE,
)
_RELEASE0_V12_CONDITION_EVIDENCE_READS = frozenset(
    {"get_analysis", "get_rms", "get_spectrum"}
)
_RELEASE0_V12_MANDATORY_CONDITION_READS = ("get_rms", "get_spectrum")
_RELEASE0_V12_CONDITION_GOAL_MARKERS = (
    "critic",
    "maior",
    "highest",
    "most critical",
    "priorit",
    "attention",
    "atencao",
    "atenção",
    "acontecendo",
    "happening",
    "investig",
    "diagnos",
    "compar",
    "evid",
    "certeza",
    "certainty",
    "cause",
    "causa",
    "falha",
    "failure",
    "fault",
    "condicao",
    "condição",
    "condition",
)
_RELEASE0_V12_ASSET_GOAL_MARKERS = (
    *_RELEASE0_V12_CONDITION_GOAL_MARKERS,
    "qualidade dos dados",
    "qualidade de dados",
    "data quality",
)

RELEASE0_V12_GROUNDING_INSTRUCTION = """
Release 0 explicit-asset grounding:
- Human-readable asset labels in the request, such as R310, R420, V301, or PM-22, are not internal
  resource identifiers. Resolve them through the authenticated company and authorized fleet listing;
  never ask the customer to provide an asset_id when that authorized discovery path is available.
- When the customer compares two or more explicit asset labels, inspect condition evidence for every
  requested asset that is present in the authorized fleet before ranking them. Evidence for one asset
  does not authorize a comparative conclusion about another.
- If an explicit customer asset label is absent from the authorized fleet listing, state that it was
  not found in the accessible inventory and explain that the requested comparison cannot be completed
  from the available scope. Do not ask for its internal asset_id and do not speculate that it belongs
  to another company, plant, or tenant unless an authorized observation proves that.
- For a data-quality question, inspect get_data_quality before concluding. If the question also asks
  whether a diagnosis can be trusted, inspect condition evidence as well before answering.
- list_assets_by_company already grounds fleet identity and metadata. Once it succeeds, do not use
  get_asset as a follow-up metadata read; advance to the evidence needed by the user's question.
""".strip()


def _canonical_asset_label(value: str) -> str:
    return re.sub(r"[-_]", "", value.casefold().strip())


def _explicit_asset_labels_v12(user_request: str) -> tuple[str, ...]:
    normalized = _normalized_request(user_request)
    found: list[str] = []
    seen: set[str] = set()
    for match in _RELEASE0_V12_ASSET_LABEL_PATTERN.finditer(normalized):
        label = _canonical_asset_label(match.group(1))
        if label and label not in seen:
            seen.add(label)
            found.append(label)
    return tuple(found)


def _asset_investigation_request_v12(user_request: str) -> bool:
    normalized = _normalized_request(user_request)
    has_literal_asset_scope = any(
        marker in normalized for marker in ("asset", "assets", "ativo", "ativos")
    )
    has_explicit_asset_scope = bool(_explicit_asset_labels_v12(user_request))
    has_goal = any(marker in normalized for marker in _RELEASE0_V12_ASSET_GOAL_MARKERS)
    return (has_literal_asset_scope or has_explicit_asset_scope) and has_goal


def _data_quality_request_v12(user_request: str) -> bool:
    normalized = _normalized_request(user_request)
    return any(
        marker in normalized
        for marker in ("data quality", "qualidade dos dados", "qualidade de dados")
    )


def _requires_condition_evidence_v12(user_request: str) -> bool:
    normalized = _normalized_request(user_request)
    return any(marker in normalized for marker in _RELEASE0_V12_CONDITION_GOAL_MARKERS)


def _asset_id_aliases(asset_id: str) -> frozenset[str]:
    raw = asset_id.casefold().strip()
    aliases = {_canonical_asset_label(raw)}
    for prefix in ("asset_", "asset-"):
        if raw.startswith(prefix):
            aliases.add(_canonical_asset_label(raw[len(prefix) :]))
    return frozenset(alias for alias in aliases if alias)


def _grounded_asset_selection_v12(
    *,
    user_request: str,
    asset_ids: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    labels = _explicit_asset_labels_v12(user_request)
    if not labels:
        return asset_ids, ()

    selected: list[str] = []
    missing: list[str] = []
    for label in labels:
        matches = [asset_id for asset_id in asset_ids if label in _asset_id_aliases(asset_id)]
        if not matches:
            missing.append(label)
            continue
        for asset_id in matches:
            if asset_id not in selected:
                selected.append(asset_id)
    return tuple(selected), tuple(missing)


def _successful_resource_ids_v12(
    observations: Iterable[Any],
    *,
    tool_names: frozenset[str],
) -> tuple[str, ...]:
    found: list[str] = []
    seen: set[str] = set()
    for observation in observations:
        if (
            observation.tool_name not in tool_names
            or not observation.executed
            or observation.status != "success"
        ):
            continue
        ids = _extract_collection_ids_v10(
            observation.body,
            explicit_keys=("asset_id", "assetId"),
            collection_keys=("assets", "items", "data", "results", "records"),
        )
        for asset_id in ids:
            if asset_id not in seen:
                seen.add(asset_id)
                found.append(asset_id)
    return tuple(found)


def _requirement_missing_ids_v12(
    *,
    observations: Iterable[Any],
    selected_asset_ids: tuple[str, ...],
    tool_names: frozenset[str],
    require_every_selected_asset: bool,
) -> tuple[str, ...]:
    successful = tuple(
        observation
        for observation in observations
        if observation.tool_name in tool_names
        and observation.executed
        and observation.status == "success"
    )
    if not successful:
        return selected_asset_ids

    if not require_every_selected_asset:
        return ()

    observed_ids = set(
        _successful_resource_ids_v12(successful, tool_names=tool_names)
    )
    # A single selected asset is deterministically bound by the prior constrained tool surface, so
    # a successful result without an echoed asset_id is sufficient for that one resource. Multiple
    # assets remain fail-closed unless the structured result identifies which asset was observed.
    if len(selected_asset_ids) == 1 and successful:
        return ()
    return tuple(asset_id for asset_id in selected_asset_ids if asset_id not in observed_ids)


def _asset_state_v12(request_or_context: Any):
    assets = _successful_observation(request_or_context, "list_assets_by_company")
    if assets is None:
        return None
    asset_ids = _extract_collection_ids_v10(
        assets.body,
        explicit_keys=("asset_id", "assetId"),
        collection_keys=("assets", "items", "data", "results"),
    )
    if not asset_ids:
        return ((), (), ())
    selected, missing_labels = _grounded_asset_selection_v12(
        user_request=request_or_context.user_request,
        asset_ids=asset_ids,
    )
    return (asset_ids, selected, missing_labels)


def _mandatory_asset_continuation_v12(request: ProviderDecisionRequest) -> bool:
    if not _asset_investigation_request_v12(request.user_request) or not request.tools:
        return False

    names = {tool.name for tool in request.tools}
    current_user = _successful_observation(request, "get_current_user")
    assets = _successful_observation(request, "list_assets_by_company")
    if current_user is not None and assets is None:
        return names == {"list_assets_by_company"}
    if assets is None:
        return False

    state = _asset_state_v12(request)
    if state is None:
        return False
    _asset_ids, selected_asset_ids, missing_labels = state
    if not selected_asset_ids or missing_labels:
        return False

    explicit_labels = _explicit_asset_labels_v12(request.user_request)
    require_every = len(explicit_labels) >= 2

    if _data_quality_request_v12(request.user_request):
        missing_quality = _requirement_missing_ids_v12(
            observations=request.observations,
            selected_asset_ids=selected_asset_ids,
            tool_names=frozenset({"get_data_quality"}),
            require_every_selected_asset=require_every,
        )
        if missing_quality:
            return names == {"get_data_quality"}

    if _requires_condition_evidence_v12(request.user_request):
        missing_condition = _requirement_missing_ids_v12(
            observations=request.observations,
            selected_asset_ids=selected_asset_ids,
            tool_names=_RELEASE0_V12_CONDITION_EVIDENCE_READS,
            require_every_selected_asset=require_every,
        )
        if missing_condition:
            return bool(names) and names <= {
                "list_analyses",
                "get_analysis",
                "get_rms",
                "get_spectrum",
            }
    return False


def _schema_for_visible_tools_v12(request: ProviderDecisionRequest) -> dict[str, object]:
    template = deepcopy(RELEASE0_PROVIDER_DECISION_JSON_SCHEMA)
    variants = template.get("oneOf")
    if not isinstance(variants, list) or len(variants) != 3:
        raise RuntimeError("release0_v12_provider_schema_contract_drift")
    terminal_variants = (
        []
        if _mandatory_asset_continuation_v12(request)
        else _terminal_variants_for_request(
            variants[1:],
            user_request=request.user_request,
        )
    )
    template["oneOf"] = [*(_tool_variant(tool) for tool in request.tools), *terminal_variants]
    return template


class Release0CloudflareDecisionClientV12(Release0CloudflareDecisionClientV11):
    """V11 response semantics plus V12 explicit-asset grounding/stopping schema."""

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        base = super().build_http_request(request)
        body = dict(base.body)
        messages = list(body.get("messages") or [])
        if len(messages) != 2 or not isinstance(messages[0], dict):
            raise RuntimeError("release0_v12_cloudflare_message_contract_drift")
        system_content = messages[0].get("content")
        if not isinstance(system_content, str) or not system_content.strip():
            raise RuntimeError("release0_v12_system_instruction_contract_drift")
        messages[0] = {
            **messages[0],
            "content": f"{system_content}\n\n{RELEASE0_V12_GROUNDING_INSTRUCTION}",
        }
        body["messages"] = messages
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": _schema_for_visible_tools_v12(request),
        }
        return ProviderHttpRequest(
            method=base.method,
            url=base.url,
            headers=dict(base.headers),
            body=body,
            timeout_seconds=base.timeout_seconds,
        )


class Release0ProviderDecisionSourceV12(Release0ProviderDecisionSourceV10):
    """Ground explicit asset labels and require per-asset evidence for comparisons."""

    @staticmethod
    def _asset_discovery_registry(context, visible: Mapping[str, Any]):
        if not _asset_investigation_request_v12(context.user_request):
            return None

        current_user = _successful_observation(context, "get_current_user")
        assets = _successful_observation(context, "list_assets_by_company")

        if current_user is not None and assets is None:
            company_ids = _extract_company_ids(current_user.body)
            tool = visible.get("list_assets_by_company")
            if len(company_ids) == 1 and tool is not None:
                return {
                    "list_assets_by_company": _constrain_tool_parameter(
                        tool,
                        "company_id",
                        company_ids,
                    )
                }
            return {}

        if assets is None:
            return None

        state = _asset_state_v12(context)
        if state is None:
            return None
        _asset_ids, selected_asset_ids, missing_labels = state
        if not selected_asset_ids or missing_labels:
            # Authorized fleet discovery is complete. Missing explicit labels cannot be repaired by
            # asking the user for internal IDs, and no other tenant/company scope is authorized.
            return {}

        explicit_labels = _explicit_asset_labels_v12(context.user_request)
        require_every = len(explicit_labels) >= 2

        if _data_quality_request_v12(context.user_request):
            missing_quality = _requirement_missing_ids_v12(
                observations=context.observations,
                selected_asset_ids=selected_asset_ids,
                tool_names=frozenset({"get_data_quality"}),
                require_every_selected_asset=require_every,
            )
            if missing_quality:
                tool = visible.get("get_data_quality")
                if tool is None:
                    return {}
                return {
                    "get_data_quality": _constrain_tool_parameter(
                        tool,
                        "asset_id",
                        missing_quality,
                    )
                }

        if not _requires_condition_evidence_v12(context.user_request):
            return None

        missing_condition = _requirement_missing_ids_v12(
            observations=context.observations,
            selected_asset_ids=selected_asset_ids,
            tool_names=_RELEASE0_V12_CONDITION_EVIDENCE_READS,
            require_every_selected_asset=require_every,
        )
        if not missing_condition:
            return None

        restricted: dict[str, Any] = {}
        for name in _RELEASE0_V12_MANDATORY_CONDITION_READS:
            tool = visible.get(name)
            if tool is not None:
                restricted[name] = _constrain_tool_parameter(
                    tool,
                    "asset_id",
                    missing_condition,
                )

        # Analysis discovery remains useful for a single selected asset. For multi-asset comparisons
        # direct condition reads avoid losing argument lineage between separate list_analyses calls.
        if len(missing_condition) == 1:
            analyses = _successful_observation(context, "list_analyses")
            if analyses is None:
                tool = visible.get("list_analyses")
                if tool is not None:
                    restricted["list_analyses"] = _constrain_tool_parameter(
                        tool,
                        "asset_id",
                        missing_condition,
                    )
            else:
                analysis_ids = _extract_collection_ids_v10(
                    analyses.body,
                    explicit_keys=("analysis_id", "analysisId"),
                    collection_keys=("analyses", "items", "data", "results"),
                )
                tool = visible.get("get_analysis")
                if analysis_ids and tool is not None:
                    restricted["get_analysis"] = _constrain_tool_parameter(
                        tool,
                        "analysis_id",
                        analysis_ids,
                    )

        return restricted or {}

    def _visible_registry(self, context):
        visible = dict(super()._visible_registry(context))
        if (
            _asset_investigation_request_v12(context.user_request)
            and _successful_observation(context, "list_assets_by_company") is not None
        ):
            visible.pop("get_asset", None)
        return visible


def build_release_provider_decision_source_v12(
    *,
    config: RemoteProductionConfig,
) -> ProviderDecisionSource:
    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    assert config.provider_id is not None
    assert config.provider_model_id is not None
    assert config.provider_account_id is not None
    assert config.provider_api_token is not None
    if config.provider_id != CLOUDFLARE_PROVIDER_ID:
        raise RuntimeError("release_provider_not_supported")

    client = Release0CloudflareDecisionClientV12(
        api_token=config.provider_api_token.get_secret_value(),
        account_id=config.provider_account_id,
        model_id=config.provider_model_id,
        transport=UrllibProviderJsonTransport(),
        timeout_seconds=config.provider_timeout_seconds,
    )
    registry = {tool.name: tool for tool in TOOLS}
    return Release0ProviderDecisionSourceV12(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=_provider_audit_model_id(client.model_id),
            route_id=client.route_id,
            live_call=True,
        ),
    )


def build_release_provider_decision_source_factory_v12(config: RemoteProductionConfig):
    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source_v12(config=config)
