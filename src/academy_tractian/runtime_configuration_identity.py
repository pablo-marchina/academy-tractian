from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from research.e2.models import ToolSpec

from .runtime import ProductionRuntimeConfig, _config_hash


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RuntimeConfigurationIdentity(_FrozenModel):
    """Public, provider-neutral identity for one empirically comparable runtime candidate.

    The frozen production runtime remains byte-exact. Candidate identity is layered on top of its
    already-computed config hash so provider/model/route drift is observable without mutating the
    historical runtime implementation or its accepted freeze artifacts.
    """

    schema_version: Literal["runtime-configuration-identity-v1"] = (
        "runtime-configuration-identity-v1"
    )
    candidate_id: str = Field(min_length=1, max_length=128)
    provider_id: str = Field(min_length=1, max_length=64)
    model_id: str = Field(min_length=1, max_length=128)
    route_id: str = Field(min_length=1, max_length=192)
    adapter_version: str = Field(min_length=1, max_length=128)
    client_version: str = Field(min_length=1, max_length=128)

    @field_validator(
        "candidate_id",
        "provider_id",
        "model_id",
        "route_id",
        "adapter_version",
        "client_version",
    )
    @classmethod
    def reject_secret_like_or_control_characters(cls, value: str) -> str:
        normalized = value.strip()
        if normalized != value or not normalized:
            raise ValueError("runtime configuration identity fields must be trimmed and non-empty")
        lowered = normalized.lower()
        forbidden = (
            "bearer ",
            "api_key",
            "api-key",
            "authorization:",
            "password=",
            "token=",
            "secret=",
        )
        if any(marker in lowered for marker in forbidden):
            raise ValueError("runtime configuration identity contains secret-like material")
        if any(ord(character) < 32 for character in normalized):
            raise ValueError("runtime configuration identity contains control characters")
        return normalized


class _RuntimeWithConfigHash(Protocol):
    config_hash: str


def _validate_sha256(value: str, *, code: str) -> None:
    if len(value) != 64:
        raise ValueError(code)
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(code) from exc


def candidate_runtime_config_hash(
    base_runtime_config_hash: str,
    configuration_identity: RuntimeConfigurationIdentity,
) -> str:
    """Bind public candidate identity to a frozen runtime hash without changing that runtime."""

    _validate_sha256(base_runtime_config_hash, code="base_runtime_config_hash_invalid")
    payload = {
        "schema_version": "candidate-runtime-config-hash-v1",
        "base_runtime_config_hash": base_runtime_config_hash,
        "configuration_identity": configuration_identity.model_dump(mode="json"),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def production_runtime_config_hash(
    config: ProductionRuntimeConfig,
    registry: Mapping[str, ToolSpec],
    configuration_identity: RuntimeConfigurationIdentity | None = None,
) -> str:
    """Return the frozen runtime hash, optionally layered with candidate identity."""

    base_hash = _config_hash(config, registry)
    if configuration_identity is None:
        return base_hash
    return candidate_runtime_config_hash(base_hash, configuration_identity)


def bind_runtime_configuration_identity(
    runtime: _RuntimeWithConfigHash,
    configuration_identity: RuntimeConfigurationIdentity,
) -> None:
    """Bind one candidate identity to a newly built prospective runtime before execution.

    The binding is intentionally external to ``ProductionRuntime``. A second binding is rejected,
    preventing one runtime object from silently changing experimental identity between requests.
    """

    if getattr(runtime, "configuration_identity", None) is not None:
        raise RuntimeError("runtime_configuration_identity_already_bound")
    base_hash = runtime.config_hash
    runtime.config_hash = candidate_runtime_config_hash(base_hash, configuration_identity)
    setattr(runtime, "configuration_identity", configuration_identity)
