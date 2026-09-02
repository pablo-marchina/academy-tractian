from __future__ import annotations

from hashlib import sha256
import json
from typing import TYPE_CHECKING, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field

from research.e2.controller import AgentController, ControllerLimits, DecisionSource
from research.e2.models import ExecutionBinding, RunTrace, ToolKind, ToolSpec
from research.e2.runner import HarnessRunner
from research.e2.tool_registry import (
    SOURCE_IMPLEMENTATION_SHA256,
    SOURCE_OPENAPI_SHA256,
    SOURCE_TESTS_SHA256,
    TOOLS,
    validate_registry,
)
from research.e2.transport import RequestTransport

from .action_safety import (
    ACTION_SAFETY_POLICY_VERSION,
    ProductionActionAuthorizationContext,
    ProductionActionSafetyPolicy,
)

if TYPE_CHECKING:
    from .realtime_observability import (
        FailIsolatedObservabilityPublisher,
        SafeObservabilityEventSink,
    )


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProductionRuntimeConfig(_FrozenModel):
    """Configuration frozen for the first production vertical slice."""

    runtime_version: Literal["prod-runtime-v1"] = "prod-runtime-v1"
    strict_arguments: Literal[True] = True
    actions_enabled: Literal[False] = False
    max_turns: int = Field(default=8, ge=1, le=64)
    max_tool_calls: int = Field(default=6, ge=0, le=64)


class ProductionRequest(_FrozenModel):
    """Runtime-owned request context.

    Identity and seed live here and are bound into the E2 execution boundary. They are
    intentionally absent from ControllerContext and therefore unavailable to DecisionSource.
    Production action authorization state is also intentionally absent from this model-facing
    context and is owned by the runtime/action-safety boundary.
    """

    request_id: str = Field(min_length=1)
    identity_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    user_request: str = Field(min_length=1)
    seed: str | None = None


def canonical_tool_registry() -> dict[str, ToolSpec]:
    """Return the validated canonical 18-operation agent-facing registry."""

    validate_registry()
    return {tool.name: tool for tool in TOOLS}


def _config_hash(
    config: ProductionRuntimeConfig,
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
        "registry": [
            registry[name].model_dump(mode="json")
            for name in sorted(registry)
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


class ProductionRuntime:
    """Production-path adapter over the accepted ADR-004 controller boundary.

    The canonical action tools stay present in the registry so attempted actions remain
    auditable. ProductionActionSafetyPolicy owns the B2 action-safety decision, but this runtime
    still constructs it with execution disabled and zero permissions. No mutating action can
    reach transport in this slice.

    Realtime observability is optional and fail-isolated. When a safe event sink is supplied,
    production-owned wrappers publish allow-listed projections immediately after canonical E2
    trace appends. The accepted `research/e2` controller/runner bytes and tool-execution
    ownership are not modified, and sink failure cannot change the returned RunTrace.
    """

    def __init__(
        self,
        *,
        decision_source: DecisionSource,
        transport: RequestTransport,
        registry: Mapping[str, ToolSpec] | None = None,
        config: ProductionRuntimeConfig | None = None,
        observability_sink: SafeObservabilityEventSink | None = None,
    ) -> None:
        self.decision_source = decision_source
        self.transport = transport
        self.registry = dict(registry or canonical_tool_registry())
        self.config = config or ProductionRuntimeConfig()
        self.observability_sink = observability_sink
        self.observability_publisher: FailIsolatedObservabilityPublisher | None = None
        if observability_sink is not None:
            # Lazy import avoids coupling the base runtime import path to FastAPI/DuckDB modules.
            from .realtime_observability import FailIsolatedObservabilityPublisher

            self.observability_publisher = FailIsolatedObservabilityPublisher(observability_sink)

        action_tools = [
            tool for tool in self.registry.values() if tool.kind is ToolKind.ACTION
        ]
        if any(not tool.required_permissions for tool in action_tools):
            raise ValueError(
                "read-only production slice requires every action tool to declare "
                "a deterministic permission"
            )

        self.config_hash = _config_hash(self.config, self.registry)

    def run(self, request: ProductionRequest) -> RunTrace:
        """Execute one production request through the validated provider-free controller."""

        binding = ExecutionBinding(
            identity_id=request.identity_id,
            user_id=request.user_id,
            seed=request.seed,
        )

        # This is deliberately runtime-owned state. DecisionSource receives none of it.
        # The global switch remains literal False and no production permissions are granted.
        action_context = ProductionActionAuthorizationContext(
            execution_enabled=self.config.actions_enabled,
            user_permissions=frozenset(),
            user_company_id="__production_read_only__",
        )
        resource_policy = ProductionActionSafetyPolicy(context=action_context)

        runner_kwargs = dict(
            run_id=request.request_id,
            scenario_id=f"prod:{request.request_id}",
            config_hash=self.config_hash,
            registry=self.registry,
            binding=binding,
            transport=self.transport,
            execution_mode="live",
            strict_arguments=True,
            resource_policy=resource_policy,
        )

        if self.observability_publisher is None:
            runner = HarnessRunner(**runner_kwargs)
            controller = AgentController(
                runner=runner,
                decision_source=self.decision_source,
                limits=ControllerLimits(
                    max_turns=self.config.max_turns,
                    max_tool_calls=self.config.max_tool_calls,
                ),
            )
        else:
            from .realtime_observability import (
                ObservableAgentController,
                ObservableHarnessRunner,
            )

            runner = ObservableHarnessRunner(
                observability_publisher=self.observability_publisher,
                **runner_kwargs,
            )
            controller = ObservableAgentController(
                runner=runner,
                decision_source=self.decision_source,
                limits=ControllerLimits(
                    max_turns=self.config.max_turns,
                    max_tool_calls=self.config.max_tool_calls,
                ),
                observability_publisher=self.observability_publisher,
            )

        return controller.run(request.user_request)
