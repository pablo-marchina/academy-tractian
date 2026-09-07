from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from research.e2.models import ToolKind

from .production_config import RemoteProductionConfig
from .release_identity import ArtifactReleaseIdentity
from .runtime import canonical_tool_registry


RELEASE0_CAPABILITIES_SCHEMA_VERSION = "release0-capabilities-v1"
READ_SEMANTICS = (
    "complete",
    "partial",
    "inconclusive",
    "conflict",
    "unavailable",
)

_GUIDED_INTENTS: tuple[dict[str, str], ...] = (
    {
        "intent_id": "CONTEXTUALIZE",
        "label": "Contextualize",
        "runtime_mapping": "ORIENT / CONTEXTUALIZE",
        "release0_behavior": "LIVE_READS_WHEN_NEEDED",
        "prompt_template": (
            "Contextualize this industrial request using the minimum relevant live TRACTIAN evidence. "
            "Explain the current context, cite the evidence you actually inspected, and state uncertainty "
            "when the available evidence is not complete. Do not propose or execute an operational action."
        ),
    },
    {
        "intent_id": "INVESTIGATE",
        "label": "Investigate",
        "runtime_mapping": "INVESTIGATE",
        "release0_behavior": "LIVE_READS_REQUIRED_BY_RUNTIME_GATE",
        "prompt_template": (
            "Investigate this industrial issue with the relevant live TRACTIAN read tools. Follow the evidence, "
            "check for partial, inconclusive, conflicting, or unavailable data, and return a customer-safe conclusion. "
            "Do not claim facts that are not supported by the retrieved evidence and do not execute actions."
        ),
    },
    {
        "intent_id": "EXECUTE",
        "label": "Execute (proposal only)",
        "runtime_mapping": "EXECUTION_DEFERRED",
        "release0_behavior": "ACTION_PROPOSAL_ONLY",
        "prompt_template": (
            "Evaluate whether the requested operational action is justified. Gather the required live evidence first. "
            "If an action is warranted, produce the appropriate action proposal with a clear justification; otherwise "
            "clarify, abstain, or escalate. Release 0 must not claim that any consequential action was executed."
        ),
    },
)

_EXPECTED_OUTPUTS: tuple[dict[str, str], ...] = (
    {"output_id": "terminal", "label": "Customer-safe terminal outcome", "description": "Decision, response mode, reason code, and final message."},
    {"output_id": "semantics", "label": "Read semantics", "description": "complete / partial / inconclusive / conflict / unavailable for canonical read results."},
    {"output_id": "timeline", "label": "Canonical event timeline", "description": "Persisted model, decision, tool, policy, evidence, and terminal events."},
    {"output_id": "tool_provenance", "label": "Tool provenance", "description": "Canonical tool name, method/path template, status, and safe latency metadata."},
    {"output_id": "model_provenance", "label": "Model provenance", "description": "Server-owned provider, model, route, live-call, outcome, and latency projection."},
    {"output_id": "evidence", "label": "Evidence references", "description": "Safe references derived from real tool results without raw secret-bearing payloads."},
    {"output_id": "policy", "label": "Policy decisions", "description": "Deterministic allow/block/containment decisions at the safety boundary."},
    {"output_id": "lineage", "label": "Output lineage", "description": "Traceable runtime and evaluation cards linking output back to observable evidence."},
    {"output_id": "evaluation", "label": "Post-runtime evaluation", "description": "Evaluator-isolated blocking and diagnostic checks after the terminal trace."},
    {"output_id": "action_proposal", "label": "Governed action proposal", "description": "Proposal and policy evidence remain observable while external execution is disabled in Release 0."},
    {"output_id": "realtime", "label": "Realtime + persisted history", "description": "SSE live progress with durable reconnect/catch-up and historical run retrieval."},
)


def build_release0_capability_manifest(
    *,
    release_git_sha: str,
    provider_calls_enabled: bool,
    provider_selection_state: str,
    provider_id: str | None,
    provider_model_id: str | None,
    tractian_transport_enabled: bool,
    tractian_transport_state: str,
    cost_policy: str,
    paid_fallback_enabled: bool,
    local_serving_enabled: bool,
) -> dict[str, Any]:
    """Build the browser-safe Release 0 contract from the canonical runtime registry.

    The manifest deliberately excludes provider credentials, TRACTIAN endpoint/headers, raw
    responses, tenant identifiers, and action authorization material. It describes capability,
    availability, and output contracts only; observed per-run use remains sourced from persisted
    safe events.
    """

    registry = canonical_tool_registry()
    tools: list[dict[str, Any]] = []
    read_count = 0
    action_count = 0
    read_path_enabled = provider_calls_enabled and tractian_transport_enabled

    for tool in registry.values():
        if tool.kind is ToolKind.READ:
            read_count += 1
            availability = "LIVE_READ" if read_path_enabled else "UNAVAILABLE"
        else:
            action_count += 1
            availability = "PROPOSAL_ONLY" if provider_calls_enabled else "UNAVAILABLE"

        tools.append(
            {
                "name": tool.name,
                "operation_id": tool.operation_id,
                "method": tool.method,
                "path_template": tool.path_template,
                "kind": tool.kind.value,
                "impact": tool.impact.value,
                "availability": availability,
                "parameters": [
                    {
                        "name": parameter.name,
                        "location": parameter.location,
                        "required": parameter.required,
                    }
                    for parameter in tool.parameters
                ],
                "required_permissions": sorted(permission.value for permission in tool.required_permissions),
                "justification_required": tool.justification_required,
                "minimum_justification_length": tool.minimum_justification_length,
                "identity_required": tool.identity_required,
                "seed_supported": tool.seed_supported,
            }
        )

    if len(tools) != 18 or read_count != 13 or action_count != 5:
        raise RuntimeError("release0_capability_registry_count_drift")

    safe_release_ready = (
        read_path_enabled
        and not paid_fallback_enabled
        and not local_serving_enabled
        and provider_selection_state == "PROVISIONAL_RELEASE_PROVIDER"
    )

    return {
        "schema_version": RELEASE0_CAPABILITIES_SCHEMA_VERSION,
        "release": {
            "git_sha": release_git_sha,
            "read_only_user_path_enabled": safe_release_ready,
            "cost_policy": cost_policy,
            "paid_fallback_enabled": paid_fallback_enabled,
            "local_serving_enabled": local_serving_enabled,
        },
        "provider": {
            "calls_enabled": provider_calls_enabled,
            "selection_state": provider_selection_state,
            "provider_id": provider_id,
            "model_id": provider_model_id,
            "provisional": provider_selection_state == "PROVISIONAL_RELEASE_PROVIDER",
        },
        "tractian": {
            "transport_enabled": tractian_transport_enabled,
            "transport_state": tractian_transport_state,
            "read_path_enabled": read_path_enabled,
        },
        "action_execution": {
            "enabled": False,
            "mode": "PROPOSAL_ONLY",
            "external_side_effects_allowed": False,
            "explanation": "Release 0 exposes action proposals and deterministic policy evidence, but never executes consequential external actions.",
        },
        "tool_summary": {
            "total": len(tools),
            "reads": read_count,
            "actions": action_count,
            "live_reads": sum(item["availability"] == "LIVE_READ" for item in tools),
            "proposal_only_actions": sum(item["availability"] == "PROPOSAL_ONLY" for item in tools),
        },
        "read_semantics": list(READ_SEMANTICS),
        "guided_intents": [dict(item) for item in _GUIDED_INTENTS],
        "expected_outputs": [dict(item) for item in _EXPECTED_OUTPUTS],
        "tools": tools,
        "server_owned": True,
        "raw_secrets_exposed": False,
        "raw_api_payloads_exposed": False,
        "chain_of_thought_exposed": False,
    }


def install_release0_capabilities(
    app: FastAPI,
    *,
    config: RemoteProductionConfig,
    artifact_release_identity: ArtifactReleaseIdentity,
    provider_selection_state: str,
    tractian_transport_state: str,
) -> None:
    """Install one immutable, browser-safe capability/readiness endpoint at serving boot."""

    manifest = build_release0_capability_manifest(
        release_git_sha=artifact_release_identity.git_sha,
        provider_calls_enabled=config.provider_calls_enabled,
        provider_selection_state=provider_selection_state,
        provider_id=config.provider_id,
        provider_model_id=config.provider_model_id,
        tractian_transport_enabled=config.tractian_transport_enabled,
        tractian_transport_state=tractian_transport_state,
        cost_policy=config.cost_policy,
        paid_fallback_enabled=config.paid_fallback_enabled,
        local_serving_enabled=config.local_serving_enabled,
    )
    app.state.release0_capability_manifest = manifest

    @app.get("/api/release0/capabilities")
    def release0_capabilities() -> dict[str, Any]:
        return manifest
