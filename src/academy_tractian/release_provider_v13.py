from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

from research.e2.tool_registry import TOOLS

from .cloudflare_provider_client import CLOUDFLARE_PROVIDER_ID
from .decision_source import ProviderCallIdentity, ProviderDecisionRequest, ProviderDecisionSource
from .production_config import RemoteProductionConfig
from .provider_budget_gate import production_provider_budget_gate_from_env
from .provider_budget_transport import BudgetGatedProviderJsonTransport
from .provider_clients import ProviderHttpRequest, UrllibProviderJsonTransport
from .release_provider import (
    RELEASE0_PROVIDER_DECISION_JSON_SCHEMA,
    _provider_audit_model_id,
    _successful_observation,
    _terminal_variants_for_request,
    _tool_variant,
    validate_release_provider_config,
)
from .release_provider_v12 import (
    RELEASE0_V12_GROUNDING_INSTRUCTION,
    Release0CloudflareDecisionClientV12,
    Release0ProviderDecisionSourceV12,
    _asset_investigation_request_v12,
    _asset_state_v12,
    _data_quality_request_v12,
    _explicit_asset_labels_v12,
    _mandatory_asset_continuation_v12,
    _requirement_missing_ids_v12,
)


RELEASE0_V13_GROUNDING_VERSION = "release0-initial-asset-grounding-v2"
RELEASE0_V13_GROUNDING_INSTRUCTION = """
Release 0 initial asset grounding:
- If the request contains a human-readable asset label such as R310 or R420 and the authenticated
  company context has not yet been observed, resolve identity with get_current_user first. Never ask
  the customer for company_id when that server-authorized discovery path is available.
- A successful single-asset get_data_quality read satisfies that requested quality check for the
  currently constrained asset. Do not repeat get_data_quality for the same single-asset question;
  advance to any still-required condition evidence or answer from the evidence already obtained.
- Repeating a successful direct measurement read is useful only when it can add distinct evidence.
  If the same measurement modality returns an observation identical to one already obtained for the
  single constrained asset, do not request that modality again. Switch to complementary evidence or
  produce the best bounded answer supported by the evidence already collected.
""".strip()


_DIRECT_MEASUREMENT_READS_V13 = ("get_rms", "get_spectrum")


def _has_repeated_identical_success(context, tool_name: str) -> bool:
    """Detect information-equivalent successful observations without inspecting private arguments.

    Provider observations contain the response body but not runtime-owned identity or credentials.
    Two equal successful bodies from the same direct measurement modality are therefore a useful
    adaptive non-progress signal: another identical read cannot add evidence. Distinct responses
    remain eligible, preserving legitimate multi-point or changing-state investigations.
    """

    prior_bodies: list[object] = []
    for observation in context.observations:
        if (
            observation.tool_name != tool_name
            or observation.status != "success"
            or not observation.executed
        ):
            continue
        if any(observation.body == prior for prior in prior_bodies):
            return True
        prior_bodies.append(observation.body)
    return False


def _mandatory_asset_continuation_v13(request: ProviderDecisionRequest) -> bool:
    """Extend V12's TOOL-only boundary to the very first explicit-asset grounding step."""

    if not _asset_investigation_request_v12(request.user_request) or not request.tools:
        return False
    current_user = _successful_observation(request, "get_current_user")
    assets = _successful_observation(request, "list_assets_by_company")
    names = {tool.name for tool in request.tools}
    if current_user is None and assets is None:
        return names == {"get_current_user"}
    return _mandatory_asset_continuation_v12(request)


def _schema_for_visible_tools_v13(request: ProviderDecisionRequest) -> dict[str, object]:
    template = deepcopy(RELEASE0_PROVIDER_DECISION_JSON_SCHEMA)
    variants = template.get("oneOf")
    if not isinstance(variants, list) or len(variants) != 3:
        raise RuntimeError("release0_v13_provider_schema_contract_drift")
    terminal_variants = (
        []
        if _mandatory_asset_continuation_v13(request)
        else _terminal_variants_for_request(
            variants[1:],
            user_request=request.user_request,
        )
    )
    template["oneOf"] = [*(_tool_variant(tool) for tool in request.tools), *terminal_variants]
    return template


class Release0CloudflareDecisionClientV13(Release0CloudflareDecisionClientV12):
    """V12 semantics plus schema-enforced grounding and adaptive non-progress guidance."""

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        base = super().build_http_request(request)
        body = dict(base.body)
        messages = list(body.get("messages") or [])
        if len(messages) != 2 or not isinstance(messages[0], dict):
            raise RuntimeError("release0_v13_cloudflare_message_contract_drift")
        system_content = messages[0].get("content")
        if not isinstance(system_content, str) or not system_content.strip():
            raise RuntimeError("release0_v13_system_instruction_contract_drift")
        messages[0] = {
            **messages[0],
            "content": f"{system_content}\n\n{RELEASE0_V13_GROUNDING_INSTRUCTION}",
        }
        body["messages"] = messages
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": _schema_for_visible_tools_v13(request),
        }
        return ProviderHttpRequest(
            method=base.method,
            url=base.url,
            headers=dict(base.headers),
            body=body,
            timeout_seconds=base.timeout_seconds,
        )


class Release0ProviderDecisionSourceV13(Release0ProviderDecisionSourceV12):
    """Close initial-grounding and repeated-evidence gaps on explicit asset investigations."""

    @staticmethod
    def _asset_discovery_registry(context, visible: Mapping[str, object]):
        if not _asset_investigation_request_v12(context.user_request):
            return None

        current_user = _successful_observation(context, "get_current_user")
        assets = _successful_observation(context, "list_assets_by_company")
        if current_user is None and assets is None:
            tool = visible.get("get_current_user")
            return {"get_current_user": tool} if tool is not None else {}

        return Release0ProviderDecisionSourceV12._asset_discovery_registry(context, visible)

    def _visible_registry(self, context):
        visible = dict(super()._visible_registry(context))
        if not _asset_investigation_request_v12(context.user_request):
            return visible

        state = _asset_state_v12(context)
        if state is None:
            return visible
        _asset_ids, selected_asset_ids, missing_labels = state
        if not selected_asset_ids or missing_labels:
            return visible

        explicit_labels = _explicit_asset_labels_v12(context.user_request)
        require_every = len(explicit_labels) >= 2

        if _data_quality_request_v12(context.user_request):
            missing_quality = _requirement_missing_ids_v12(
                observations=context.observations,
                selected_asset_ids=selected_asset_ids,
                tool_names=frozenset({"get_data_quality"}),
                require_every_selected_asset=require_every,
            )
            if not missing_quality:
                visible.pop("get_data_quality", None)

        # Single-asset investigations may legitimately query one modality at different points.
        # Keep the modality available while observations differ; once a successful body repeats,
        # another same-modality call is information-equivalent and is removed from the next model
        # surface. Multi-asset comparisons retain V12's per-asset constrained progression.
        if len(explicit_labels) == 1 and len(selected_asset_ids) == 1:
            for tool_name in _DIRECT_MEASUREMENT_READS_V13:
                if _has_repeated_identical_success(context, tool_name):
                    visible.pop(tool_name, None)

        return visible


def build_release_provider_decision_source_v13(
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

    gate = production_provider_budget_gate_from_env()
    gate.ensure_schema()
    client = Release0CloudflareDecisionClientV13(
        api_token=config.provider_api_token.get_secret_value(),
        account_id=config.provider_account_id,
        model_id=config.provider_model_id,
        transport=BudgetGatedProviderJsonTransport(
            gate=gate,
            inner=UrllibProviderJsonTransport(),
        ),
        timeout_seconds=config.provider_timeout_seconds,
    )
    registry = {tool.name: tool for tool in TOOLS}
    return Release0ProviderDecisionSourceV13(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=_provider_audit_model_id(client.model_id),
            route_id=client.route_id,
            live_call=True,
        ),
    )


def build_release_provider_decision_source_factory_v13(config: RemoteProductionConfig):
    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source_v13(config=config)
