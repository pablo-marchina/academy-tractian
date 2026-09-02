from __future__ import annotations

from typing import Mapping

from research.e2.controller import ControllerLimits, DecisionSource
from research.e2.models import ExecutionBinding, RunTrace, ToolSpec
from research.e2.transport import RequestTransport

from .action_safety import (
    ProductionActionAuthorizationContext,
    ProductionActionSafetyPolicy,
)
from .realtime_observability import (
    FailIsolatedObservabilityPublisher,
    ObservableAgentController,
    ObservableHarnessRunner,
    SafeObservabilityEventSink,
)
from .runtime import ProductionRequest, ProductionRuntime, ProductionRuntimeConfig


class RealtimeProductionRuntime(ProductionRuntime):
    """Prospective observable adapter over the frozen ProductionRuntime v1 contract.

    The base runtime remains byte-exact for historical freezes. This adapter reuses its
    validated configuration, registry and action-safety ownership, while substituting only
    production-owned wrappers that publish safe trace projections after canonical E2 appends.
    Provider/tool/controller semantics are regression-tested for exact trace equivalence.
    """

    def __init__(
        self,
        *,
        decision_source: DecisionSource,
        transport: RequestTransport,
        observability_sink: SafeObservabilityEventSink,
        registry: Mapping[str, ToolSpec] | None = None,
        config: ProductionRuntimeConfig | None = None,
    ) -> None:
        super().__init__(
            decision_source=decision_source,
            transport=transport,
            registry=registry,
            config=config,
        )
        self.observability_publisher = FailIsolatedObservabilityPublisher(
            observability_sink
        )

    def run(self, request: ProductionRequest) -> RunTrace:
        binding = ExecutionBinding(
            identity_id=request.identity_id,
            user_id=request.user_id,
            seed=request.seed,
        )

        # Keep the exact read-only action authorization state owned by ProductionRuntime v1.
        action_context = ProductionActionAuthorizationContext(
            execution_enabled=self.config.actions_enabled,
            user_permissions=frozenset(),
            user_company_id="__production_read_only__",
        )
        resource_policy = ProductionActionSafetyPolicy(context=action_context)

        runner = ObservableHarnessRunner(
            observability_publisher=self.observability_publisher,
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
