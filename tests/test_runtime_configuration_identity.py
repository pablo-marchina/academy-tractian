from __future__ import annotations

from hashlib import sha256
import json

import pytest
from pydantic import ValidationError

from academy_tractian.action_safety import ACTION_SAFETY_POLICY_VERSION
from academy_tractian.runtime import (
    ProductionRequest,
    ProductionRuntime,
    ProductionRuntimeConfig,
    canonical_tool_registry,
)
from academy_tractian.runtime_configuration_identity import (
    RuntimeConfigurationIdentity,
    bind_runtime_configuration_identity,
    production_runtime_config_hash,
)
from research.e2.controller import ControllerDecision, ControllerDecisionKind, ControllerContext
from research.e2.tool_registry import (
    SOURCE_IMPLEMENTATION_SHA256,
    SOURCE_OPENAPI_SHA256,
    SOURCE_TESTS_SHA256,
)
from research.e2.transport import TransportResponse


class _FinalSource:
    def decide(self, context: ControllerContext) -> ControllerDecision:
        del context
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Configuration provenance test.",
            },
        )


class _NoopTransport:
    def request(self, request):
        del request
        return TransportResponse(200, {}, {})


def _identity(
    *,
    candidate_id: str,
    provider_id: str,
    model_id: str,
    route_id: str,
) -> RuntimeConfigurationIdentity:
    return RuntimeConfigurationIdentity(
        candidate_id=candidate_id,
        provider_id=provider_id,
        model_id=model_id,
        route_id=route_id,
        adapter_version="provider-decision-adapter-v1",
        client_version="provider-http-clients-v1",
    )


def _historical_v1_hash(config: ProductionRuntimeConfig) -> str:
    registry = canonical_tool_registry()
    payload = {
        "runtime": config.model_dump(mode="json"),
        "action_safety_policy_version": ACTION_SAFETY_POLICY_VERSION,
        "tool_contract_sources": {
            "openapi_sha256": SOURCE_OPENAPI_SHA256,
            "implementation_sha256": SOURCE_IMPLEMENTATION_SHA256,
            "tests_sha256": SOURCE_TESTS_SHA256,
        },
        "registry": [
            registry[name].model_dump(mode="json")
            for name in sorted(registry)
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def test_omitted_identity_preserves_historical_v1_hash_payload_exactly() -> None:
    config = ProductionRuntimeConfig(max_turns=8, max_tool_calls=6)
    registry = canonical_tool_registry()

    assert production_runtime_config_hash(config, registry) == _historical_v1_hash(config)


def test_same_runtime_with_different_provider_identity_has_different_config_hash() -> None:
    config = ProductionRuntimeConfig()
    registry = canonical_tool_registry()
    openai = _identity(
        candidate_id="openai:gpt-5.6-sol",
        provider_id="openai",
        model_id="gpt-5.6-sol",
        route_id="openai.responses.v1.standard",
    )
    google = _identity(
        candidate_id="google:gemini-3.7-flash",
        provider_id="google",
        model_id="gemini-3.7-flash",
        route_id="google.interactions.v1beta.stateless",
    )

    openai_hash = production_runtime_config_hash(config, registry, openai)
    google_hash = production_runtime_config_hash(config, registry, google)

    assert openai_hash != google_hash
    assert openai_hash != production_runtime_config_hash(config, registry)
    assert google_hash != production_runtime_config_hash(config, registry)


def test_trace_carries_candidate_bound_runtime_hash_without_modifying_frozen_runtime() -> None:
    identity = _identity(
        candidate_id="openai:gpt-5.6-sol",
        provider_id="openai",
        model_id="gpt-5.6-sol",
        route_id="openai.responses.v1.standard",
    )
    runtime = ProductionRuntime(decision_source=_FinalSource(), transport=_NoopTransport())
    bind_runtime_configuration_identity(runtime, identity)
    trace = runtime.run(
        ProductionRequest(
            request_id="candidate-run-1",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Check provenance.",
        )
    )

    assert trace.config_hash == runtime.config_hash
    assert runtime.configuration_identity == identity


def test_factory_style_binding_is_one_shot_and_changes_hash_before_execution() -> None:
    runtime = ProductionRuntime(decision_source=_FinalSource(), transport=_NoopTransport())
    legacy_hash = runtime.config_hash
    identity = _identity(
        candidate_id="google:gemini-3.7-flash",
        provider_id="google",
        model_id="gemini-3.7-flash",
        route_id="google.interactions.v1beta.stateless",
    )

    bind_runtime_configuration_identity(runtime, identity)

    assert runtime.config_hash != legacy_hash
    assert runtime.configuration_identity == identity
    with pytest.raises(RuntimeError, match="already_bound"):
        bind_runtime_configuration_identity(runtime, identity)


@pytest.mark.parametrize(
    "field_value",
    [
        "Bearer secret-value",
        "api_key=secret-value",
        "Authorization: secret-value",
        "token=secret-value",
        "secret=secret-value",
    ],
)
def test_configuration_identity_rejects_secret_like_material(field_value: str) -> None:
    with pytest.raises(ValidationError, match="secret-like material"):
        RuntimeConfigurationIdentity(
            candidate_id="openai:gpt-5.6-sol",
            provider_id="openai",
            model_id="gpt-5.6-sol",
            route_id=field_value,
            adapter_version="provider-decision-adapter-v1",
            client_version="provider-http-clients-v1",
        )
