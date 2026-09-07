from __future__ import annotations

from research.e2.tool_registry import TOOLS

from .cloudflare_provider_client import CLOUDFLARE_PROVIDER_ID
from .decision_source import ProviderCallIdentity, ProviderDecisionRequest, ProviderDecisionSource
from .production_config import RemoteProductionConfig
from .provider_clients import ProviderHttpRequest, UrllibProviderJsonTransport
from .release_provider import _provider_audit_model_id, validate_release_provider_config
from .release_provider_v10 import (
    Release0CloudflareDecisionClientV10,
    Release0ProviderDecisionSourceV10,
)


RELEASE0_V11_RESPONSE_MODE_SEMANTICS_VERSION = "release0-response-mode-semantics-v1"
RELEASE0_V11_RESPONSE_MODE_INSTRUCTION = """
Release 0 response-mode semantics:
The response_mode is a customer-visible epistemic status, not a generic confidence label. Choose the
single mode whose definition matches both the evidence and the wording of the final message.

- complete: every material part of the user's request is answered by the inspected evidence, with no
  material unresolved gap needed to use the conclusion as stated.
- partial: at least one material requested conclusion is supported, while another material part remains
  uncertain, probabilistic, or not fully evidenced. A supported prioritization or ranking plus an
  evidence-backed likely fault mechanism is partial when the mechanism is not fully confirmed.
- inconclusive: evidence was inspected, but it does not support a reliable directional answer to the
  core question. Do not use inconclusive merely because a supported conclusion still contains normal
  diagnostic uncertainty.
- conflict: inspected observations materially contradict one another and that contradiction prevents a
  single reliable conclusion.
- unavailable: evidence required to answer the request could not be obtained from the authorized read
  surface, for example because the source/tool/data was unavailable or failed.

The mode and message must agree. In particular, if the message identifies a specific highest-criticality
asset and gives an evidence-backed probable explanation of what is happening, use partial unless every
material causal claim is directly supported strongly enough for complete. Never label that kind of
supported directional answer inconclusive solely because the causal explanation remains probabilistic.
""".strip()


class Release0CloudflareDecisionClientV11(Release0CloudflareDecisionClientV10):
    """Release 0 V11 client with explicit customer-visible response-mode semantics."""

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        base = super().build_http_request(request)
        body = dict(base.body)
        messages = list(body.get("messages") or [])
        if len(messages) != 2 or not isinstance(messages[0], dict):
            raise RuntimeError("release0_v11_cloudflare_message_contract_drift")
        system_content = messages[0].get("content")
        if not isinstance(system_content, str) or not system_content.strip():
            raise RuntimeError("release0_v11_system_instruction_contract_drift")
        messages[0] = {
            **messages[0],
            "content": f"{system_content}\n\n{RELEASE0_V11_RESPONSE_MODE_INSTRUCTION}",
        }
        body["messages"] = messages
        return ProviderHttpRequest(
            method=base.method,
            url=base.url,
            headers=dict(base.headers),
            body=body,
            timeout_seconds=base.timeout_seconds,
        )


def build_release_provider_decision_source_v11(
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

    client = Release0CloudflareDecisionClientV11(
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


def build_release_provider_decision_source_factory_v11(config: RemoteProductionConfig):
    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source_v11(config=config)
