from __future__ import annotations

from threading import Lock
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
from .runtime import (
    ProductionRequest,
    ProductionRuntime,
    ProductionRuntimeConfig,
    RuntimeConfigurationIdentity,
)


class PreparedRealtimeRun:
    """One-shot prepared run whose `run_started` event is already safely persisted."""

    def __init__(
        self,
        *,
        controller: ObservableAgentController,
        user_request: str,
    ) -> None:
        self.controller = controller
        self.user_request = user_request
        self._lock = Lock()
        self._executed = False

    def execute(self) -> RunTrace:
        with self._lock:
            if self._executed:
                raise RuntimeError("prepared_realtime_run_already_executed")
            # Claim before execution: unexpected failures do not authorize blind replay.
            self._executed = True
        return self.controller.run(self.user_request)


class RealtimeProductionRuntime(ProductionRuntime):
    """Prospective observable adapter over the frozen ProductionRuntime v1 contract.

    The base runtime remains byte-exact for historical freezes when no external candidate identity
    is supplied. This adapter reuses its validated configuration, registry and action-safety
    ownership, while substituting only production-owned wrappers that publish safe trace projections
    after canonical E2 appends. Provider/tool/controller semantics are regression-tested for exact
    trace equivalence.
    """

    def __init__(
        self,
        *,
        decision_source: DecisionSource,
        transport: RequestTransport,
        observability_sink: SafeObservabilityEventSink,
        registry: Mapping[str, ToolSpec] | None = None,
        config: ProductionRuntimeConfig | None = None,
        configuration_identity: RuntimeConfigurationIdentity | None = None,
    ) -> None:
        super().__init__(
            decision_source=decision_source,
            transport=transport,
            registry=registry,
            config=config,
            configuration_identity=configuration_identity,
        )
        self.observability_publisher = FailIsolatedObservabilityPublisher(
            observability_sink
        )

    def prepare(self, request: ProductionRequest) -> PreparedRealtimeRun:
        """Create the real execution boundary and publish only genuine `run_started`.

        No model decision or tool call occurs before the returned one-shot object is executed.
        This lets the product API return a safe run id only after the live stream can already
        resolve the run, eliminating the POST→SSE race without fabricating progress events.
        """

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
        return PreparedRealtimeRun(
            controller=controller,
            user_request=request.user_request,
        )

    def run(self, request: ProductionRequest) -> RunTrace:
        return self.prepare(request).execute()
