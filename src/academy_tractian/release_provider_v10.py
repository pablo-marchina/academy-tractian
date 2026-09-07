from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from research.e2.tool_registry import TOOLS

from .cloudflare_provider_client import (
    CLOUDFLARE_PROVIDER_ID,
)
from .decision_source import ProviderCallIdentity, ProviderDecisionSource
from .production_config import RemoteProductionConfig
from .provider_clients import UrllibProviderJsonTransport
from .release_provider import (
    Release0CloudflareDecisionClient,
    Release0ProviderDecisionSource,
    _ASSET_DIAGNOSTIC_TOOL_NAMES,
    _append_bounded_identifier,
    _asset_investigation_request,
    _constrain_tool_parameter,
    _extract_company_ids,
    _provider_audit_model_id,
    _successful_observation,
    validate_release_provider_config,
)

_RELEASE0_V10_MAX_DEPTH = 8
_RELEASE0_V10_COLLECTION_WRAPPERS = frozenset(
    {"items", "data", "results", "records", "nodes", "entries", "values"}
)
_RELEASE0_V10_NON_REPEATABLE_CONTEXT_READS = frozenset(
    {"get_current_user", "list_assets_by_company"}
)


def _resource_prefixes(explicit_keys: tuple[str, ...]) -> tuple[str, ...]:
    if any(key in {"asset_id", "assetId"} for key in explicit_keys):
        return ("asset_", "asset-")
    if any(key in {"analysis_id", "analysisId"} for key in explicit_keys):
        return ("analysis_", "analysis-")
    return ()


def _extract_collection_ids_v10(
    value: Any,
    *,
    explicit_keys: tuple[str, ...],
    collection_keys: tuple[str, ...],
) -> tuple[str, ...]:
    """Extract exact ids from bounded structured collections, including nested wrappers.

    Explicit resource-id fields are authoritative wherever they occur in structured output.
    Generic ``id`` fields are accepted only inside a recognized collection and either under a
    semantic collection key (for example ``assets``/``analyses``) or when the value carries the
    expected public resource prefix. Free text is never inspected.
    """

    found: list[str] = []
    seen: set[str] = set()
    semantic_keys = frozenset(
        key for key in collection_keys if key not in _RELEASE0_V10_COLLECTION_WRAPPERS
    )
    wrapper_keys = frozenset(collection_keys) | _RELEASE0_V10_COLLECTION_WRAPPERS
    prefixes = _resource_prefixes(explicit_keys)

    def prefixed(value: Any) -> bool:
        return isinstance(value, str) and any(value.startswith(prefix) for prefix in prefixes)

    def add_explicit(record: Mapping[str, Any]) -> None:
        for key in explicit_keys:
            _append_bounded_identifier(found, seen, record.get(key))

    def add_record(record: Mapping[str, Any], *, semantic: bool) -> None:
        add_explicit(record)
        raw_id = record.get("id")
        if semantic or prefixed(raw_id):
            _append_bounded_identifier(found, seen, raw_id)

    def inspect_collection(node: Any, *, semantic: bool, depth: int) -> None:
        if depth > _RELEASE0_V10_MAX_DEPTH:
            return
        if isinstance(node, (list, tuple)):
            for item in node:
                if isinstance(item, Mapping):
                    add_record(item, semantic=semantic)
                    for key, child in item.items():
                        if key in semantic_keys:
                            inspect_collection(child, semantic=True, depth=depth + 1)
                        elif key in wrapper_keys:
                            inspect_collection(child, semantic=semantic, depth=depth + 1)
                elif isinstance(item, (list, tuple)):
                    inspect_collection(item, semantic=semantic, depth=depth + 1)
            return
        if not isinstance(node, Mapping):
            return

        add_record(node, semantic=semantic)
        for key, child in node.items():
            if semantic and prefixed(key):
                _append_bounded_identifier(found, seen, key)
            if key in semantic_keys:
                inspect_collection(child, semantic=True, depth=depth + 1)
            elif key in wrapper_keys:
                inspect_collection(child, semantic=semantic, depth=depth + 1)

    def scan(node: Any, *, depth: int) -> None:
        if depth > _RELEASE0_V10_MAX_DEPTH:
            return
        if isinstance(node, Mapping):
            add_explicit(node)
            for key, child in node.items():
                if key in semantic_keys:
                    inspect_collection(child, semantic=True, depth=depth + 1)
                elif key in wrapper_keys:
                    inspect_collection(child, semantic=False, depth=depth + 1)
                elif isinstance(child, (Mapping, list, tuple)):
                    scan(child, depth=depth + 1)
        elif isinstance(node, (list, tuple)):
            inspect_collection(node, semantic=False, depth=depth)

    scan(value, depth=0)
    return tuple(found)


class Release0ProviderDecisionSourceV10(Release0ProviderDecisionSource):
    """Release 0 grounding hotfix for nested collections and redundant context reads."""

    @staticmethod
    def _asset_discovery_registry(context, visible: Mapping[str, Any]):
        if not _asset_investigation_request(context.user_request):
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
            # A successful identity read must never fall back to re-offering the same context read.
            return {}

        if assets is None:
            return None

        if any(
            _successful_observation(context, name) is not None
            for name in _ASSET_DIAGNOSTIC_TOOL_NAMES
        ):
            return None

        asset_ids = _extract_collection_ids_v10(
            assets.body,
            explicit_keys=("asset_id", "assetId"),
            collection_keys=("assets", "items", "data", "results"),
        )
        if not asset_ids:
            # Fail closed instead of widening back to every read tool and looping on identity.
            return {}

        restricted: dict[str, Any] = {}
        analyses = _successful_observation(context, "list_analyses")
        # list_assets_by_company already grounds asset identity and fleet metadata. get_asset is a
        # metadata read rather than diagnostic evidence, so re-offering it here can consume the
        # entire bounded tool budget without making progress toward "what is happening".
        for name in (
            "get_data_quality",
            "get_baseline",
            "get_rms",
            "get_spectrum",
        ):
            tool = visible.get(name)
            if tool is not None:
                restricted[name] = _constrain_tool_parameter(tool, "asset_id", asset_ids)

        if analyses is None:
            tool = visible.get("list_analyses")
            if tool is not None:
                restricted["list_analyses"] = _constrain_tool_parameter(
                    tool,
                    "asset_id",
                    asset_ids,
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
        successful = {
            observation.tool_name
            for observation in context.observations
            if observation.executed and observation.status == "success"
        }
        for tool_name in _RELEASE0_V10_NON_REPEATABLE_CONTEXT_READS & successful:
            visible.pop(tool_name, None)
        return visible


def build_release_provider_decision_source_v10(
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

    client = Release0CloudflareDecisionClient(
        api_token=config.provider_api_token.get_secret_value(),
        account_id=config.provider_account_id,
        model_id=config.provider_model_id,
        transport=UrllibProviderJsonTransport(),
        timeout_seconds=config.provider_timeout_seconds,
    )
    registry = {tool.name: tool for tool in TOOLS}
    return Release0ProviderDecisionSourceV10(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=_provider_audit_model_id(client.model_id),
            route_id=client.route_id,
            live_call=True,
        ),
    )


def build_release_provider_decision_source_factory_v10(config: RemoteProductionConfig):
    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source_v10(config=config)
