#!/usr/bin/env python3
"""One-call V15 serving smoke composed through remote_server._decision_source_factory()."""
from __future__ import annotations

import json
import os
from types import SimpleNamespace

from pydantic import SecretStr

from academy_tractian.decision_source import ProviderDecisionPayload, ProviderDecisionRequest
from academy_tractian.remote_server import _decision_source_factory
from academy_tractian.release_provider import PROVISIONAL_RELEASE_PROVIDER_STATE
from academy_tractian.release_provider_v15 import (
    NVIDIA_ACCOUNT_SENTINEL,
    NVIDIA_MODEL_ID,
    NVIDIA_PROVIDER_ID,
    RELEASE0_V15_PROVIDER_VERSION,
    Release0NvidiaDecisionClientV15,
)


def main() -> int:
    key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not key:
        raise SystemExit("NVIDIA_API_KEY missing")

    config = SimpleNamespace(
        provider_calls_enabled=True,
        provider_selection_state=PROVISIONAL_RELEASE_PROVIDER_STATE,
        provider_id=NVIDIA_PROVIDER_ID,
        provider_model_id=NVIDIA_MODEL_ID,
        provider_account_id=NVIDIA_ACCOUNT_SENTINEL,
        provider_api_token=SecretStr(key),
        provider_timeout_seconds=90.0,
        cost_policy="usd0-hard-gate",
        paid_fallback_enabled=False,
        tractian_transport_enabled=True,
    )

    factory = _decision_source_factory(config)
    source = factory()
    client = source.client
    if not isinstance(client, Release0NvidiaDecisionClientV15):
        raise RuntimeError("V15 composition root did not produce the NVIDIA V15 client")

    request = ProviderDecisionRequest.model_construct(
        user_request="Synthetic V15 serving smoke. Do not use tools. Return a safe terminal decision only.",
        turn_index=0,
        tool_call_count=0,
        observations=(),
        tools=(),
        request_sha256="0" * 64,
    )
    raw = client.complete(request)
    decision = ProviderDecisionPayload.model_validate_json(raw)

    evidence = {
        "schema_version": "nvidia-v15-composition-serving-smoke-v1",
        "status": "PASS",
        "provider_version": RELEASE0_V15_PROVIDER_VERSION,
        "provider_id": client.provider_id,
        "model_id": client.model_id,
        "route_id": client.route_id,
        "decision_kind": decision.kind.value,
        "composition_root": "academy_tractian.remote_server._decision_source_factory",
        "provider_calls": 1,
        "official_cases_loaded": 0,
        "official_cases_consumed": 0,
        "raw_response_body_persisted": False,
        "credential_persisted": False,
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
