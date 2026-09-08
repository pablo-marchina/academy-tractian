from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
import re
import unicodedata
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
    _provider_audit_model_id,
    _successful_observation,
    _terminal_variants_for_request,
    _tool_variant,
    validate_release_provider_config,
)
from .release_provider_v10 import _extract_collection_ids_v10
from .release_provider_v12 import (
    _data_quality_request_v12,
    _explicit_asset_labels_v12,
    _requirement_missing_ids_v12,
)
from .release_provider_v13 import (
    RELEASE0_V13_GROUNDING_INSTRUCTION,
    Release0CloudflareDecisionClientV13,
    Release0ProviderDecisionSourceV13,
)


RELEASE0_V14_GROUNDING_VERSION = "release0-canonical-asset-grounding-v1"
RELEASE0_V14_GROUNDING_INSTRUCTION = """
Release 0 canonical asset grounding:
- Treat the authorized list_assets_by_company result as the canonical source for asset identity.
  Resolve customer-facing codes and names to the exact canonical asset id from that result before
  any asset-bound read. Once resolved, never shorten, reconstruct, or otherwise rewrite that id.
- Asset aliases may come from the canonical id, its public suffix, or human-readable name/label
  fields actually returned by the authorized fleet. Do not invent aliases or infer tenant scope.
- If a customer-facing alias is absent or maps to more than one authorized asset, do not guess.
  Explain that the target could not be uniquely grounded from the accessible fleet. Never ask for
  an internal asset_id when the authorized discovery path has already been used.
- For multi-asset requests, keep every resolved target bound to its own canonical id and obtain the
  requested evidence for each target before making a comparative conclusion.
""".strip()

_ASSET_COLLECTION_KEYS_V14 = frozenset({"assets"})
_ASSET_WRAPPER_KEYS_V14 = frozenset(
    {"data", "items", "results", "records", "nodes", "entries", "values"}
)
_ASSET_NAME_KEYS_V14 = (
    "name",
    "label",
    "display_name",
    "displayName",
    "asset_name",
    "assetName",
    "title",
)
_ASSET_ID_KEYS_V14 = ("asset_id", "assetId", "id")
_MAX_ASSET_PARSE_DEPTH_V14 = 8
_STOPWORDS_V14 = frozenset(
    {
        "a",
        "as",
        "da",
        "das",
        "de",
        "do",
        "dos",
        "e",
        "o",
        "os",
        "of",
        "the",
        "and",
    }
)
_TASK_MARKERS_V14 = (
    "analis",
    "analyz",
    "analyse",
    "rms",
    "spectrum",
    "espectro",
    "vibr",
    "baseline",
    "linha de base",
    "status",
    "estado",
    "condition",
    "condicao",
    "health",
    "saude",
    "critic",
    "priorit",
    "attention",
    "atenc",
    "acontecendo",
    "happening",
    "como esta",
    "how is",
    "investig",
    "diagnos",
    "confi",
    "compar",
    "evid",
    "certeza",
    "certainty",
    "cause",
    "causa",
    "falha",
    "failure",
    "fault",
    "qualidade dos dados",
    "qualidade de dados",
    "data quality",
)
_EQUIPMENT_SCOPE_MARKERS_V14 = (
    "ativo",
    "ativos",
    "asset",
    "assets",
    "motor",
    "martelete",
    "hammer",
    "bomba",
    "pump",
    "compressor",
    "turbina",
    "turbine",
    "ventilador",
    "fan",
    "redutor",
    "gearbox",
    "rolamento",
    "bearing",
    "maquina",
    "machine",
    "equipamento",
    "equipment",
)
_GENERIC_CONDITION_MARKERS_V14 = (
    "analis",
    "analyz",
    "analyse",
    "status",
    "estado",
    "condition",
    "condicao",
    "health",
    "saude",
    "critic",
    "priorit",
    "attention",
    "atenc",
    "acontecendo",
    "happening",
    "como esta",
    "how is",
    "investig",
    "diagnos",
    "confi",
    "compar",
    "evid",
    "certeza",
    "certainty",
    "cause",
    "causa",
    "falha",
    "failure",
    "fault",
    "vibr",
)
_GENERIC_CONDITION_READS_V14 = frozenset(
    {"get_analysis", "get_rms", "get_spectrum"}
)
_DIRECT_EVIDENCE_MARKERS_V14 = (
    ("get_rms", ("rms",)),
    ("get_spectrum", ("spectrum", "espectro")),
    ("get_baseline", ("baseline", "linha de base")),
)


@dataclass(frozen=True)
class AssetGroundingStateV14:
    asset_ids: tuple[str, ...]
    selected_asset_ids: tuple[str, ...]
    unresolved_aliases: tuple[str, ...]
    ambiguous_aliases: tuple[str, ...]


def _normalize_text_v14(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    ascii_like = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_like).split())


def _compact_alias_v14(value: str) -> str:
    return _normalize_text_v14(value).replace(" ", "")


def _asset_investigation_request_v14(user_request: str) -> bool:
    normalized = _normalize_text_v14(user_request)
    has_task = any(marker in normalized for marker in _TASK_MARKERS_V14)
    has_code = bool(_explicit_asset_labels_v12(user_request))
    has_equipment_scope = any(marker in normalized for marker in _EQUIPMENT_SCOPE_MARKERS_V14)
    return has_task and (has_code or has_equipment_scope)


def _condition_evidence_groups_v14(user_request: str) -> tuple[frozenset[str], ...]:
    normalized = _normalize_text_v14(user_request)
    direct: list[frozenset[str]] = []
    for tool_name, markers in _DIRECT_EVIDENCE_MARKERS_V14:
        if any(marker in normalized for marker in markers):
            direct.append(frozenset({tool_name}))
    if direct:
        return tuple(direct)
    if any(marker in normalized for marker in _GENERIC_CONDITION_MARKERS_V14):
        return (_GENERIC_CONDITION_READS_V14,)
    return ()


def _asset_record_id_v14(record: Mapping[str, Any], *, semantic: bool) -> str | None:
    for key in ("asset_id", "assetId"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    value = record.get("id")
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    if semantic or value.startswith(("asset_", "asset-")):
        return value
    return None


def _extract_asset_records_v14(body: Any) -> tuple[Mapping[str, Any], ...]:
    found: dict[str, Mapping[str, Any]] = {}

    def visit(node: Any, *, semantic: bool, depth: int) -> None:
        if depth > _MAX_ASSET_PARSE_DEPTH_V14:
            return
        if isinstance(node, (list, tuple)):
            for item in node:
                visit(item, semantic=semantic, depth=depth + 1)
            return
        if not isinstance(node, Mapping):
            return

        asset_id = _asset_record_id_v14(node, semantic=semantic)
        if asset_id is not None and asset_id not in found:
            found[asset_id] = node

        for key, child in node.items():
            if key in _ASSET_COLLECTION_KEYS_V14:
                visit(child, semantic=True, depth=depth + 1)
            elif key in _ASSET_WRAPPER_KEYS_V14:
                visit(child, semantic=semantic, depth=depth + 1)

    visit(body, semantic=False, depth=0)
    if found:
        return tuple(found.values())

    # Preserve V10's bounded id extraction as a metadata-free fallback for older response shapes.
    ids = _extract_collection_ids_v10(
        body,
        explicit_keys=("asset_id", "assetId"),
        collection_keys=("assets", "items", "data", "results"),
    )
    return tuple({"id": asset_id} for asset_id in ids)


def _asset_names_v14(record: Mapping[str, Any]) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()
    for key in _ASSET_NAME_KEYS_V14:
        value = record.get(key)
        if not isinstance(value, str):
            continue
        value = value.strip()
        if value and value not in seen:
            seen.add(value)
            names.append(value)
    return tuple(names)


def _human_aliases_v14(value: str) -> frozenset[str]:
    normalized = _normalize_text_v14(value)
    if not normalized:
        return frozenset()
    aliases = {normalized}
    tokens = normalized.split()
    # Partial human aliases are deterministic contiguous phrases, never edit-distance/fuzzy matches.
    # Require at least two substantive words so generic single words from a long asset name do not
    # silently select a resource. Ambiguity is resolved fleet-wide later.
    for start in range(len(tokens)):
        for end in range(start + 2, min(len(tokens), start + 4) + 1):
            span = tokens[start:end]
            if sum(token not in _STOPWORDS_V14 for token in span) >= 2:
                aliases.add(" ".join(span))
    return frozenset(aliases)


def _asset_alias_maps_v14(
    records: tuple[Mapping[str, Any], ...],
) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    asset_ids: list[str] = []
    code_index: dict[str, list[str]] = {}
    human_index: dict[str, list[str]] = {}

    def add(index: dict[str, list[str]], alias: str, asset_id: str) -> None:
        if not alias:
            return
        values = index.setdefault(alias, [])
        if asset_id not in values:
            values.append(asset_id)

    for record in records:
        asset_id = _asset_record_id_v14(record, semantic=True)
        if asset_id is None:
            continue
        if asset_id not in asset_ids:
            asset_ids.append(asset_id)
        add(code_index, _compact_alias_v14(asset_id), asset_id)
        raw = asset_id.casefold().strip()
        for prefix in ("asset_", "asset-"):
            if raw.startswith(prefix):
                add(code_index, _compact_alias_v14(asset_id[len(prefix) :]), asset_id)
        for name in _asset_names_v14(record):
            for alias in _human_aliases_v14(name):
                add(human_index, alias, asset_id)

    return (
        tuple(asset_ids),
        {alias: tuple(ids) for alias, ids in code_index.items()},
        {alias: tuple(ids) for alias, ids in human_index.items()},
    )


def _human_matches_v14(
    user_request: str,
    human_index: Mapping[str, tuple[str, ...]],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    normalized = _normalize_text_v14(user_request)
    candidates: list[tuple[int, int, str, tuple[str, ...]]] = []
    for alias, asset_ids in human_index.items():
        if not alias:
            continue
        # Single-token aliases are accepted only when they are complete fleet-provided names.
        # Partial aliases generated above always contain at least two substantive words.
        pattern = re.compile(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])")
        for match in pattern.finditer(normalized):
            candidates.append((match.start(), match.end(), alias, asset_ids))

    # Most-specific phrase wins within an overlapping span. This prevents a unique full name from
    # being invalidated by a shorter overlapping phrase that happens to be ambiguous fleet-wide.
    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2]))
    accepted: list[tuple[int, int, str, tuple[str, ...]]] = []
    for candidate in candidates:
        start, end, _alias, _ids = candidate
        if any(start < existing_end and end > existing_start for existing_start, existing_end, *_ in accepted):
            continue
        accepted.append(candidate)
    return tuple((alias, ids) for _start, _end, alias, ids in accepted)


def _grounded_asset_selection_v14(
    *,
    user_request: str,
    records: tuple[Mapping[str, Any], ...],
) -> AssetGroundingStateV14:
    asset_ids, code_index, human_index = _asset_alias_maps_v14(records)
    selected: list[str] = []
    unresolved: list[str] = []
    ambiguous: list[str] = []

    def consume(alias: str, matches: tuple[str, ...]) -> None:
        if not matches:
            if alias not in unresolved:
                unresolved.append(alias)
            return
        if len(matches) != 1:
            if alias not in ambiguous:
                ambiguous.append(alias)
            return
        asset_id = matches[0]
        if asset_id not in selected:
            selected.append(asset_id)

    for label in _explicit_asset_labels_v12(user_request):
        consume(label, code_index.get(label, ()))

    for alias, matches in _human_matches_v14(user_request, human_index):
        consume(alias, matches)

    return AssetGroundingStateV14(
        asset_ids=asset_ids,
        selected_asset_ids=tuple(selected),
        unresolved_aliases=tuple(unresolved),
        ambiguous_aliases=tuple(ambiguous),
    )


def _asset_state_v14(request_or_context: Any) -> AssetGroundingStateV14 | None:
    assets = _successful_observation(request_or_context, "list_assets_by_company")
    if assets is None:
        return None
    return _grounded_asset_selection_v14(
        user_request=request_or_context.user_request,
        records=_extract_asset_records_v14(assets.body),
    )


def _missing_evidence_v14(
    *,
    request_or_context: Any,
    selected_asset_ids: tuple[str, ...],
    tool_names: frozenset[str],
) -> tuple[str, ...]:
    return _requirement_missing_ids_v12(
        observations=request_or_context.observations,
        selected_asset_ids=selected_asset_ids,
        tool_names=tool_names,
        require_every_selected_asset=len(selected_asset_ids) >= 2,
    )


def _missing_evidence_groups_v14(
    request_or_context: Any,
    selected_asset_ids: tuple[str, ...],
) -> tuple[tuple[frozenset[str], tuple[str, ...]], ...]:
    missing: list[tuple[frozenset[str], tuple[str, ...]]] = []
    for group in _condition_evidence_groups_v14(request_or_context.user_request):
        asset_ids = _missing_evidence_v14(
            request_or_context=request_or_context,
            selected_asset_ids=selected_asset_ids,
            tool_names=group,
        )
        if asset_ids:
            missing.append((group, asset_ids))
    return tuple(missing)


def _mandatory_asset_continuation_v14(request: ProviderDecisionRequest) -> bool:
    if not _asset_investigation_request_v14(request.user_request) or not request.tools:
        return False

    names = {tool.name for tool in request.tools}
    current_user = _successful_observation(request, "get_current_user")
    assets = _successful_observation(request, "list_assets_by_company")
    if current_user is None and assets is None:
        return names == {"get_current_user"}
    if current_user is not None and assets is None:
        return names == {"list_assets_by_company"}
    if assets is None:
        return False

    state = _asset_state_v14(request)
    if (
        state is None
        or not state.selected_asset_ids
        or state.unresolved_aliases
        or state.ambiguous_aliases
    ):
        return False

    if _data_quality_request_v12(request.user_request):
        missing_quality = _missing_evidence_v14(
            request_or_context=request,
            selected_asset_ids=state.selected_asset_ids,
            tool_names=frozenset({"get_data_quality"}),
        )
        if missing_quality:
            return names == {"get_data_quality"}

    missing_groups = _missing_evidence_groups_v14(request, state.selected_asset_ids)
    if not missing_groups:
        return False
    allowed = set()
    for group, _missing_ids in missing_groups:
        allowed.update(group)
        if group == _GENERIC_CONDITION_READS_V14:
            allowed.add("list_analyses")
    return bool(names) and names <= allowed


def _schema_for_visible_tools_v14(request: ProviderDecisionRequest) -> dict[str, object]:
    template = deepcopy(RELEASE0_PROVIDER_DECISION_JSON_SCHEMA)
    variants = template.get("oneOf")
    if not isinstance(variants, list) or len(variants) != 3:
        raise RuntimeError("release0_v14_provider_schema_contract_drift")
    terminal_variants = (
        []
        if _mandatory_asset_continuation_v14(request)
        else _terminal_variants_for_request(
            variants[1:],
            user_request=request.user_request,
        )
    )
    template["oneOf"] = [*(_tool_variant(tool) for tool in request.tools), *terminal_variants]
    return template


def _constrain_asset_bound_reads_v14(
    visible: Mapping[str, Any],
    asset_ids: tuple[str, ...],
) -> dict[str, Any]:
    constrained: dict[str, Any] = {}
    for name, tool in visible.items():
        if name == "get_asset":
            # list_assets_by_company already supplied canonical identity and metadata.
            continue
        if any(parameter.name == "asset_id" for parameter in tool.parameters):
            constrained[name] = _constrain_tool_parameter(tool, "asset_id", asset_ids)
        else:
            constrained[name] = tool
    return constrained


class Release0CloudflareDecisionClientV14(Release0CloudflareDecisionClientV13):
    """V13 semantics plus canonical fleet-derived alias grounding and stopping."""

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        base = super().build_http_request(request)
        body = dict(base.body)
        messages = list(body.get("messages") or [])
        if len(messages) != 2 or not isinstance(messages[0], dict):
            raise RuntimeError("release0_v14_cloudflare_message_contract_drift")
        system_content = messages[0].get("content")
        if not isinstance(system_content, str) or not system_content.strip():
            raise RuntimeError("release0_v14_system_instruction_contract_drift")
        messages[0] = {
            **messages[0],
            "content": f"{system_content}\n\n{RELEASE0_V14_GROUNDING_INSTRUCTION}",
        }
        body["messages"] = messages
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": _schema_for_visible_tools_v14(request),
        }
        return ProviderHttpRequest(
            method=base.method,
            url=base.url,
            headers=dict(base.headers),
            body=body,
            timeout_seconds=base.timeout_seconds,
        )


class Release0ProviderDecisionSourceV14(Release0ProviderDecisionSourceV13):
    """Resolve asset codes/names to canonical authorized fleet ids and keep them constrained."""

    @staticmethod
    def _asset_discovery_registry(context, visible: Mapping[str, Any]):
        if not _asset_investigation_request_v14(context.user_request):
            return Release0ProviderDecisionSourceV13._asset_discovery_registry(context, visible)

        current_user = _successful_observation(context, "get_current_user")
        assets = _successful_observation(context, "list_assets_by_company")
        if current_user is None and assets is None:
            tool = visible.get("get_current_user")
            return {"get_current_user": tool} if tool is not None else {}

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
            return {}

        state = _asset_state_v14(context)
        if (
            state is None
            or not state.selected_asset_ids
            or state.unresolved_aliases
            or state.ambiguous_aliases
        ):
            return {}

        if _data_quality_request_v12(context.user_request):
            missing_quality = _missing_evidence_v14(
                request_or_context=context,
                selected_asset_ids=state.selected_asset_ids,
                tool_names=frozenset({"get_data_quality"}),
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

        missing_groups = _missing_evidence_groups_v14(context, state.selected_asset_ids)
        if missing_groups:
            restricted: dict[str, Any] = {}
            for group, missing_ids in missing_groups:
                for name in group:
                    # get_analysis is exposed only after a grounded analysis id is available.
                    if name == "get_analysis":
                        continue
                    tool = visible.get(name)
                    if tool is not None:
                        restricted[name] = _constrain_tool_parameter(
                            tool,
                            "asset_id",
                            missing_ids,
                        )

                if group == _GENERIC_CONDITION_READS_V14 and len(missing_ids) == 1:
                    analyses = _successful_observation(context, "list_analyses")
                    if analyses is None:
                        tool = visible.get("list_analyses")
                        if tool is not None:
                            restricted["list_analyses"] = _constrain_tool_parameter(
                                tool,
                                "asset_id",
                                missing_ids,
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

        # Grounding remains active after the minimum evidence is satisfied so later optional reads
        # cannot regress from asset_M101 back to M101 (or another model-invented identifier).
        return _constrain_asset_bound_reads_v14(visible, state.selected_asset_ids)

    def _visible_registry(self, context):
        visible = dict(super()._visible_registry(context))
        if (
            _asset_investigation_request_v14(context.user_request)
            and _successful_observation(context, "list_assets_by_company") is not None
        ):
            visible.pop("get_asset", None)
        return visible


def build_release_provider_decision_source_v14(
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

    client = Release0CloudflareDecisionClientV14(
        api_token=config.provider_api_token.get_secret_value(),
        account_id=config.provider_account_id,
        model_id=config.provider_model_id,
        transport=UrllibProviderJsonTransport(),
        timeout_seconds=config.provider_timeout_seconds,
    )
    registry = {tool.name: tool for tool in TOOLS}
    return Release0ProviderDecisionSourceV14(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=_provider_audit_model_id(client.model_id),
            route_id=client.route_id,
            live_call=True,
        ),
    )


def build_release_provider_decision_source_factory_v14(config: RemoteProductionConfig):
    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source_v14(config=config)
