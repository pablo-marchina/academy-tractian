from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Literal, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field

from research.e2.controller import AgentController, ControllerLimits, DecisionSource
from research.e2.models import ExecutionBinding, RunTrace, ToolKind, ToolSpec
from research.e2.policy import PolicyDecision, ResourcePolicy
from research.e2.runner import HarnessRunner
from research.e2.tool_registry import (
    SOURCE_IMPLEMENTATION_SHA256,
    SOURCE_OPENAPI_SHA256,
    SOURCE_TESTS_SHA256,
)
from research.e2.transport import RequestTransport

from .action_safety import (
    ACTION_SAFETY_POLICY_VERSION,
    ProductionActionAuthorizationContext,
    ProductionActionSafetyPolicy,
    action_fingerprint,
)
from .runtime import ProductionRequest, canonical_tool_registry


CONTROLLED_ACTION_RUNTIME_VERSION = "controlled-action-runtime-v1"
ACTION_ATTEMPT_CLAIM_SCHEMA_VERSION = "controlled-action-attempt-claim-v1"


class ControlledActionInvariantError(RuntimeError):
    """Trusted action-control state is internally inconsistent."""


class ActionAuthorizationSource(Protocol):
    """Runtime-owned source of exact action authorization state.

    Implementations are control-plane inputs. They are never passed to ControllerContext or to a
    provider-visible tool schema.
    """

    def resolve(
        self,
        *,
        tool: ToolSpec,
        arguments: Mapping[str, Any],
    ) -> ProductionActionAuthorizationContext | None: ...


@dataclass(repr=False)
class StaticActionAuthorizationSource:
    """Exact-fingerprint authorization source for controlled/demo/test execution.

    This source is intentionally explicit rather than inferred from model text. A final external
    authorization integration may implement the same protocol with trusted identity/permission /
    scope systems, while ADR-005 remains the deterministic action policy.
    """

    _contexts_by_fingerprint: dict[str, ProductionActionAuthorizationContext]

    @classmethod
    def from_contexts(
        cls,
        contexts: Mapping[str, ProductionActionAuthorizationContext],
    ) -> "StaticActionAuthorizationSource":
        return cls(_contexts_by_fingerprint=dict(contexts))

    def __repr__(self) -> str:
        return f"StaticActionAuthorizationSource(grants={len(self._contexts_by_fingerprint)}, state=<redacted>)"

    def resolve(
        self,
        *,
        tool: ToolSpec,
        arguments: Mapping[str, Any],
    ) -> ProductionActionAuthorizationContext | None:
        fingerprint = action_fingerprint(tool, dict(arguments))
        return self._contexts_by_fingerprint.get(fingerprint)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ActionAttemptClaim(_FrozenModel):
    schema_version: Literal["controlled-action-attempt-claim-v1"] = (
        ACTION_ATTEMPT_CLAIM_SCHEMA_VERSION
    )
    runtime_version: Literal["controlled-action-runtime-v1"] = CONTROLLED_ACTION_RUNTIME_VERSION
    tool_name: str = Field(min_length=1)
    action_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    idempotency_key_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    state: Literal["claimed"] = "claimed"
    raw_idempotency_key_recorded: Literal[False] = False


class DurableActionAttemptClaimStore:
    """Durable at-most-once claim store using exclusive-create semantics.

    A claim is persisted before HarnessRunner is allowed to reach action transport. If the
    process or transport fails afterwards, the claim remains and a later runtime instance treats
    the same idempotency key as consumed/uncertain rather than replaying a potentially mutating
    request. Raw idempotency keys are never written to disk.
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    @staticmethod
    def _key_sha256(idempotency_key: str) -> str:
        return sha256(idempotency_key.encode("utf-8")).hexdigest()

    def claim_path(self, idempotency_key: str) -> Path:
        return self.root / f"{self._key_sha256(idempotency_key)}.json"

    def claim(
        self,
        *,
        tool_name: str,
        action_fingerprint_sha256: str,
        idempotency_key: str,
    ) -> bool:
        if not isinstance(idempotency_key, str) or not idempotency_key:
            raise ControlledActionInvariantError("durable action claim requires non-empty idempotency key")
        self.root.mkdir(parents=True, exist_ok=True)
        key_sha = self._key_sha256(idempotency_key)
        path = self.root / f"{key_sha}.json"
        record = ActionAttemptClaim(
            tool_name=tool_name,
            action_fingerprint=action_fingerprint_sha256,
            idempotency_key_sha256=key_sha,
        )
        data = json.dumps(
            record.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ) + "\n"
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return False

        # Fail closed after exclusive creation: an incomplete claim file still prevents replay.
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            _fsync_directory(self.root)
        except Exception:
            raise
        return True


class DurableProductionActionPolicy(ResourcePolicy):
    """ADR-005 composition with durable pre-transport idempotency claiming."""

    def __init__(
        self,
        *,
        authorization_source: ActionAuthorizationSource,
        claim_store: DurableActionAttemptClaimStore,
    ) -> None:
        self.authorization_source = authorization_source
        self.claim_store = claim_store

    def check(self, tool: ToolSpec, arguments: dict[str, object]) -> PolicyDecision:
        if tool.kind is not ToolKind.ACTION:
            raise ValueError("DurableProductionActionPolicy only evaluates action ToolSpecs")

        context = self.authorization_source.resolve(tool=tool, arguments=arguments)
        if context is None:
            return PolicyDecision(
                allowed=False,
                code="AUTHORIZATION_NOT_PROVISIONED",
                reason=(
                    f"{CONTROLLED_ACTION_RUNTIME_VERSION}: no trusted authorization grant exists "
                    "for the exact action fingerprint"
                ),
            )

        adr005 = ProductionActionSafetyPolicy(context=context)
        decision = adr005.evaluate(tool, dict(arguments))
        if not decision.allowed:
            return PolicyDecision(
                allowed=False,
                code=decision.code,
                reason=f"{ACTION_SAFETY_POLICY_VERSION}: {decision.code}",
            )

        fingerprint = action_fingerprint(tool, dict(arguments))
        matching_keys = [
            binding.idempotency_key
            for binding in context.idempotency_bindings
            if binding.action_fingerprint == fingerprint
        ]
        if len(matching_keys) != 1:
            # ADR-005 ALLOWED should make this unreachable; fail closed if the contract drifts.
            raise ControlledActionInvariantError(
                "ADR-005 allowed an action without exactly one matching idempotency binding"
            )

        claimed = self.claim_store.claim(
            tool_name=tool.name,
            action_fingerprint_sha256=fingerprint,
            idempotency_key=matching_keys[0],
        )
        if not claimed:
            return PolicyDecision(
                allowed=False,
                code="DUPLICATE_ACTION",
                reason=(
                    f"{CONTROLLED_ACTION_RUNTIME_VERSION}: durable idempotency claim already exists"
                ),
            )

        return PolicyDecision(
            allowed=True,
            code="ALLOWED",
            reason=(
                f"{ACTION_SAFETY_POLICY_VERSION}: all checks passed; "
                f"{CONTROLLED_ACTION_RUNTIME_VERSION}: durable attempt claim persisted"
            ),
        )


class ControlledActionRuntimeConfig(_FrozenModel):
    runtime_version: Literal["controlled-action-runtime-v1"] = CONTROLLED_ACTION_RUNTIME_VERSION
    strict_arguments: Literal[True] = True
    authorization_mode: Literal["explicit_trusted_grants_only"] = "explicit_trusted_grants_only"
    durable_idempotency_required: Literal[True] = True
    max_turns: int = Field(default=8, ge=1, le=64)
    max_tool_calls: int = Field(default=6, ge=0, le=64)


def _controlled_config_hash(
    config: ControlledActionRuntimeConfig,
    registry: Mapping[str, ToolSpec],
) -> str:
    payload = {
        "runtime": config.model_dump(mode="json"),
        "action_safety_policy_version": ACTION_SAFETY_POLICY_VERSION,
        "tool_contract_sources": {
            "openapi_sha256": SOURCE_OPENAPI_SHA256,
            "implementation_sha256": SOURCE_IMPLEMENTATION_SHA256,
            "tests_sha256": SOURCE_TESTS_SHA256,
        },
        "registry": [registry[name].model_dump(mode="json") for name in sorted(registry)],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


class ControlledActionRuntime:
    """Explicit action-capable production-path profile for controlled supplied-API evidence.

    This does not replace or mutate the read-only ProductionRuntime. It preserves the same
    application-owned AgentController and HarnessRunner execution boundary, but its B2 policy is
    supplied with trusted runtime authorization plus a durable at-most-once claim store.
    """

    def __init__(
        self,
        *,
        decision_source: DecisionSource,
        transport: RequestTransport,
        authorization_source: ActionAuthorizationSource,
        claim_store: DurableActionAttemptClaimStore,
        registry: Mapping[str, ToolSpec] | None = None,
        config: ControlledActionRuntimeConfig | None = None,
    ) -> None:
        self.decision_source = decision_source
        self.transport = transport
        self.authorization_source = authorization_source
        self.claim_store = claim_store
        self.registry = dict(registry or canonical_tool_registry())
        self.config = config or ControlledActionRuntimeConfig()

        action_tools = [tool for tool in self.registry.values() if tool.kind is ToolKind.ACTION]
        if any(not tool.required_permissions for tool in action_tools):
            raise ValueError("controlled action runtime requires deterministic permissions for every action")

        self.config_hash = _controlled_config_hash(self.config, self.registry)

    def run(self, request: ProductionRequest) -> RunTrace:
        binding = ExecutionBinding(
            identity_id=request.identity_id,
            user_id=request.user_id,
            seed=request.seed,
        )
        resource_policy = DurableProductionActionPolicy(
            authorization_source=self.authorization_source,
            claim_store=self.claim_store,
        )
        runner = HarnessRunner(
            run_id=request.request_id,
            scenario_id=f"prod-action:{request.request_id}",
            config_hash=self.config_hash,
            registry=self.registry,
            binding=binding,
            transport=self.transport,
            execution_mode="live",
            strict_arguments=True,
            resource_policy=resource_policy,
        )
        controller = AgentController(
            runner=runner,
            decision_source=self.decision_source,
            limits=ControllerLimits(
                max_turns=self.config.max_turns,
                max_tool_calls=self.config.max_tool_calls,
            ),
        )
        return controller.run(request.user_request)


def _fsync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
