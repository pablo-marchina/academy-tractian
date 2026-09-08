from __future__ import annotations

from typing import Mapping

from research.e2.controller import ControllerLimits, DecisionSource
from research.e2.models import ExecutionBinding, RunTrace, ToolSpec
from research.e2.runner import HarnessRunner
from research.e2.transport import RequestTransport

from .action_safety import ProductionActionAuthorizationContext, ProductionActionSafetyPolicy
from .production_controller import ProductionAgentController
from .runtime import (
    ProductionRequest,
    ProductionRuntime,
    ProductionRuntimeConfig,
    canonical_tool_registry,
)


class ProductionRuntimeV2(ProductionRuntime):
    """Prospective serving runtime that preserves the frozen baseline runtime blob.

    Historical campaigns pin ``runtime.py`` by Git blob. New production-only controller
    invariants therefore compose here instead of rewriting frozen evidence.
    """

    def __init__(
        self,
        *,
        decision_source: DecisionSource,
        transport: RequestTransport,
        registry: Mapping[str, ToolSpec] | None = None,
        config: ProductionRuntimeConfig | None = None,
    ) -> None:
        super().__init__(
            decision_source=decision_source,
            transport=transport,
            registry=registry or canonical_tool_registry(),
            config=config,
        )

    def run(self, request: ProductionRequest) -> RunTrace:
        binding = ExecutionBinding(
            identity_id=request.identity_id,
            user_id=request.user_id,
            seed=request.seed,
        )
        action_context = ProductionActionAuthorizationContext(
            execution_enabled=self.config.actions_enabled,
            user_permissions=frozenset(),
            user_company_id="__production_read_only__",
        )
        resource_policy = ProductionActionSafetyPolicy(context=action_context)
        runner = HarnessRunner(
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
        controller = ProductionAgentController(
            runner=runner,
            decision_source=self.decision_source,
            limits=ControllerLimits(
                max_turns=self.config.max_turns,
                max_tool_calls=self.config.max_tool_calls,
            ),
        )
        return controller.run(request.user_request)
