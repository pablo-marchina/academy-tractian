from __future__ import annotations

from typing import Mapping

from research.e2.controller import ControllerLimits, DecisionSource
from research.e2.models import ExecutionBinding, ToolSpec
from research.e2.transport import RequestTransport

from .production_actions_v2 import (
    ActionAuthorizationResolver,
    ActionProposalRealtimeProductionRuntime,
    PendingActionCapturePolicy,
    PendingActionCustody,
)
from .production_observable_controller import ProductionObservableAgentController
from .realtime_observability import ObservableHarnessRunner, SafeObservabilityEventSink
from .realtime_runtime import PreparedRealtimeRun
from .runtime import ProductionRequest, ProductionRuntimeConfig


class ActionProposalRealtimeProductionRuntimeV3(ActionProposalRealtimeProductionRuntime):
    """Production-serving action runtime with duplicate-read containment.

    V2 remains unchanged for historical evidence. V3 changes only the controller used for the
    realtime read/proposal loop; action custody, authorization, observability and transport
    boundaries are inherited unchanged.
    """

    def __init__(
        self,
        *,
        decision_source: DecisionSource,
        transport: RequestTransport,
        observability_sink: SafeObservabilityEventSink,
        authorization_resolver: ActionAuthorizationResolver,
        custody: PendingActionCustody,
        registry: Mapping[str, ToolSpec] | None = None,
        config: ProductionRuntimeConfig | None = None,
    ) -> None:
        super().__init__(
            decision_source=decision_source,
            transport=transport,
            observability_sink=observability_sink,
            authorization_resolver=authorization_resolver,
            custody=custody,
            registry=registry,
            config=config,
        )

    def prepare(self, request: ProductionRequest) -> PreparedRealtimeRun:
        principal = self.authorization_resolver(user_id=request.user_id)
        if principal.user_id != request.user_id:
            raise RuntimeError("action_principal_user_mismatch")
        binding = ExecutionBinding(
            identity_id=request.identity_id,
            user_id=request.user_id,
            seed=request.seed,
        )
        execution_guard = getattr(self.observability_publisher.sink, "assert_active", None)
        policy = PendingActionCapturePolicy(
            principal=principal,
            origin_raw_run_id=request.request_id,
            custody=self.custody,
            execution_guard=execution_guard if callable(execution_guard) else None,
        )
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
            resource_policy=policy,
        )
        controller = ProductionObservableAgentController(
            runner=runner,
            decision_source=self.decision_source,
            limits=ControllerLimits(
                max_turns=self.config.max_turns,
                max_tool_calls=self.config.max_tool_calls,
            ),
            observability_publisher=self.observability_publisher,
        )
        return PreparedRealtimeRun(controller=controller, user_request=request.user_request)
