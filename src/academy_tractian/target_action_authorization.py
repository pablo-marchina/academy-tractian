from __future__ import annotations

from typing import Any, Callable, Mapping, Protocol
from uuid import uuid4

from research.e2.controller import ControllerLimits, DecisionSource
from research.e2.models import ExecutionBinding, ToolKind, ToolSpec
from research.e2.policy import PolicyDecision, ResourcePolicy
from research.e2.transport import RequestTransport

from .action_safety import (
    ActionIdempotencyBinding,
    ProductionActionAuthorizationContext,
    ProductionActionSafetyPolicy,
    action_fingerprint,
)
from .observability import safe_run_id
from .production_actions_v2 import (
    ACTION_EXECUTION_CONFIG_HASH,
    ClaimingProductionActionSafetyPolicy,
    PendingActionSafe,
    PreparedActionExecution,
    ProductionActionPrincipal,
)
from .realtime_observability import (
    FailIsolatedObservabilityPublisher,
    ObservableAgentController,
    ObservableHarnessRunner,
    SafeObservabilityEventSink,
)
from .realtime_runtime import PreparedRealtimeRun
from .runtime import ProductionRequest, ProductionRuntime, ProductionRuntimeConfig, canonical_tool_registry


class TargetActionAuthorizationResolver(Protocol):
    """Resolve server-owned authorization for the exact proposed action target."""

    def __call__(
        self,
        *,
        user_id: str,
        tool: ToolSpec,
        arguments: Mapping[str, Any],
    ) -> ProductionActionPrincipal: ...


class TargetAwarePendingActionCapturePolicy(ResourcePolicy):
    """Authorize an exact action proposal before creating private confirmation custody."""

    def __init__(
        self,
        *,
        user_id: str,
        target_authorization_resolver: TargetActionAuthorizationResolver,
        origin_raw_run_id: str,
        custody: Any,
        execution_guard: Callable[[], None] | None = None,
    ) -> None:
        self.user_id = user_id
        self.target_authorization_resolver = target_authorization_resolver
        self.origin_raw_run_id = origin_raw_run_id
        self.custody = custody
        self.execution_guard = execution_guard
        self.last_pending: PendingActionSafe | None = None

    def check(self, tool: ToolSpec, arguments: dict[str, object]) -> PolicyDecision:
        if self.execution_guard is not None:
            self.execution_guard()
        if tool.kind is not ToolKind.ACTION:
            return PolicyDecision(
                allowed=True,
                code="ALLOWED",
                reason="read tool outside action capture",
            )
        try:
            principal = self.target_authorization_resolver(
                user_id=self.user_id,
                tool=tool,
                arguments=dict(arguments),
            )
        except Exception:
            return PolicyDecision(
                allowed=False,
                code="RESOURCE_SCOPE_UNKNOWN",
                reason="prod-action-target-auth-v1: exact target authorization unavailable",
            )
        if principal.user_id != self.user_id:
            return PolicyDecision(
                allowed=False,
                code="PERMISSION_DENIED",
                reason="prod-action-target-auth-v1: principal user mismatch",
            )

        context = ProductionActionAuthorizationContext(
            execution_enabled=True,
            user_permissions=principal.permissions,
            user_company_id=principal.user_company_id,
            resource_company_bindings=principal.resource_company_bindings,
            confirmed_action_fingerprints=frozenset(),
            idempotency_bindings=(),
            consumed_idempotency_keys=frozenset(),
        )
        decision = ProductionActionSafetyPolicy(context=context).evaluate(tool, dict(arguments))
        blocking_failures = [
            code
            for code in decision.failed_codes
            if code not in {"CONFIRMATION_REQUIRED", "IDEMPOTENCY_KEY_REQUIRED"}
        ]
        if blocking_failures:
            return PolicyDecision(
                allowed=False,
                code=blocking_failures[0],
                reason=f"prod-action-target-auth-v1: {blocking_failures[0]}",
            )

        pending = self.custody.create_or_get(
            origin_raw_run_id=self.origin_raw_run_id,
            requester_user_id=principal.user_id,
            tool=tool,
            arguments=dict(arguments),
        )
        self.last_pending = pending
        return PolicyDecision(
            allowed=False,
            code="CONFIRMATION_REQUIRED",
            reason=(
                "prod-action-target-auth-v1: exact authorized action is privately custodied "
                "and requires operator confirmation"
            ),
        )


class TargetAwareActionProposalRealtimeProductionRuntime(ProductionRuntime):
    """Read runtime with lazy exact-target authorization for consequential proposals."""

    def __init__(
        self,
        *,
        decision_source: DecisionSource,
        transport: RequestTransport,
        observability_sink: SafeObservabilityEventSink,
        target_authorization_resolver: TargetActionAuthorizationResolver,
        custody: Any,
        registry: Mapping[str, ToolSpec] | None = None,
        config: ProductionRuntimeConfig | None = None,
    ) -> None:
        super().__init__(
            decision_source=decision_source,
            transport=transport,
            registry=registry,
            config=config,
        )
        self.observability_publisher = FailIsolatedObservabilityPublisher(observability_sink)
        self.target_authorization_resolver = target_authorization_resolver
        self.custody = custody

    def prepare(self, request: ProductionRequest) -> PreparedRealtimeRun:
        binding = ExecutionBinding(
            identity_id=request.identity_id,
            user_id=request.user_id,
            seed=request.seed,
        )
        execution_guard = getattr(self.observability_publisher.sink, "assert_active", None)
        policy = TargetAwarePendingActionCapturePolicy(
            user_id=request.user_id,
            target_authorization_resolver=self.target_authorization_resolver,
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
        controller = ObservableAgentController(
            runner=runner,
            decision_source=self.decision_source,
            limits=ControllerLimits(
                max_turns=self.config.max_turns,
                max_tool_calls=self.config.max_tool_calls,
            ),
            observability_publisher=self.observability_publisher,
        )
        return PreparedRealtimeRun(controller=controller, user_request=request.user_request)


class TargetAwareProductionActionExecutor:
    """Confirmation executor that re-resolves the exact target before accepting work."""

    def __init__(
        self,
        *,
        custody: Any,
        ledger: Any,
        target_authorization_resolver: TargetActionAuthorizationResolver,
        transport_factory: Callable[[], RequestTransport],
        observability_sink: SafeObservabilityEventSink,
        registry: Mapping[str, ToolSpec] | None = None,
        actions_enabled: bool = False,
    ) -> None:
        self.custody = custody
        self.ledger = ledger
        self.target_authorization_resolver = target_authorization_resolver
        self.transport_factory = transport_factory
        self.observability_publisher = FailIsolatedObservabilityPublisher(observability_sink)
        self.registry = dict(registry or canonical_tool_registry())
        self.actions_enabled = bool(actions_enabled)

    def set_actions_enabled(self, enabled: bool) -> None:
        self.actions_enabled = bool(enabled)

    def prepare_confirmed(
        self,
        *,
        action_id: str,
        identity_id: str,
        requester_user_id: str,
    ) -> tuple[str, PreparedActionExecution]:
        if not self.actions_enabled:
            raise RuntimeError("action_kill_switch_engaged")
        item = self.custody.get_private_for_requester(
            action_id=action_id,
            requester_user_id=requester_user_id,
        )
        if item.safe.state not in {"PENDING_CONFIRMATION", "CONFIRMED"}:
            raise RuntimeError(f"action_not_confirmable:{item.safe.state}")
        tool = self.registry[item.safe.tool_name]
        fingerprint = action_fingerprint(tool, item.arguments)
        if fingerprint != item.safe.action_fingerprint:
            raise RuntimeError("pending_action_fingerprint_drift")

        try:
            principal = self.target_authorization_resolver(
                user_id=requester_user_id,
                tool=tool,
                arguments=item.arguments,
            )
        except Exception as exc:
            raise RuntimeError("action_authorization_unavailable") from exc
        if principal.user_id != requester_user_id:
            raise RuntimeError("action_principal_user_mismatch")

        context = ProductionActionAuthorizationContext(
            execution_enabled=True,
            user_permissions=principal.permissions,
            user_company_id=principal.user_company_id,
            resource_company_bindings=principal.resource_company_bindings,
            confirmed_action_fingerprints=frozenset({fingerprint}),
            idempotency_bindings=(
                ActionIdempotencyBinding(
                    action_fingerprint=fingerprint,
                    idempotency_key=item.idempotency_key,
                ),
            ),
            consumed_idempotency_keys=frozenset(),
        )
        preflight = ProductionActionSafetyPolicy(context=context).evaluate(tool, item.arguments)
        if not preflight.allowed:
            raise RuntimeError(f"action_authorization_denied:{preflight.code}")

        policy = ClaimingProductionActionSafetyPolicy(
            context=context,
            ledger=self.ledger,
            action_id=action_id,
        )
        raw_execution_id = "action-run-" + uuid4().hex
        execution_run_id = safe_run_id(raw_execution_id)
        transitioned = self.custody.transition(
            action_id=action_id,
            expected_states=frozenset({"PENDING_CONFIRMATION", "CONFIRMED"}),
            new_state="EXECUTING",
            execution_run_id=execution_run_id,
        )
        if not transitioned:
            raise RuntimeError("action_confirmation_race_lost")

        binding = ExecutionBinding(
            identity_id=identity_id,
            user_id=requester_user_id,
            seed=None,
        )
        runner = ObservableHarnessRunner(
            observability_publisher=self.observability_publisher,
            run_id=raw_execution_id,
            scenario_id=f"prod:action:{action_id}",
            config_hash=ACTION_EXECUTION_CONFIG_HASH,
            registry=self.registry,
            binding=binding,
            transport=self.transport_factory(),
            execution_mode="live",
            strict_arguments=True,
            resource_policy=policy,
        )
        prepared = PreparedActionExecution(
            action_id=action_id,
            runner=runner,
            tool=tool,
            arguments=item.arguments,
            policy=policy,
            custody=self.custody,
            ledger=self.ledger,
        )
        return execution_run_id, prepared


def target_resolver_from_legacy(
    authorization_resolver: Any,
) -> TargetActionAuthorizationResolver | None:
    """Discover an explicit target method without changing the public composition signature."""

    candidate = getattr(authorization_resolver, "resolve_target", None)
    return candidate if callable(candidate) else None
