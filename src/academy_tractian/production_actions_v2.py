from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Literal, Mapping, Protocol
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from research.e2.controller import ControllerLimits, DecisionSource
from research.e2.models import ExecutionBinding, Permission, RunTrace, ToolKind, ToolSpec
from research.e2.policy import PolicyDecision, ResourcePolicy
from research.e2.transport import RequestTransport

from .action_safety import (
    ActionIdempotencyBinding,
    ProductionActionAuthorizationContext,
    ProductionActionSafetyPolicy,
    ResourceCompanyBinding,
    action_fingerprint,
)
from .observability import safe_run_id
from .realtime_observability import (
    FailIsolatedObservabilityPublisher,
    ObservableAgentController,
    ObservableHarnessRunner,
    SafeObservabilityEventSink,
)
from .realtime_runtime import PreparedRealtimeRun
from .runtime import ProductionRequest, ProductionRuntime, ProductionRuntimeConfig, canonical_tool_registry


ACTION_EXECUTION_CONFIG_HASH = sha256(b"prod-action-runtime-v2").hexdigest()


def _duckdb():
    """Load the legacy local adapter only when a test explicitly selects it."""

    try:
        import duckdb
    except ImportError as exc:  # pragma: no cover - packaging guard for test-only adapter
        raise RuntimeError("DuckDB action adapters require the dev/test DuckDB extra") from exc
    return duckdb


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProductionActionPrincipal(_FrozenModel):
    """Server-owned authorization facts; never model- or browser-controlled."""

    user_id: str = Field(min_length=1)
    user_company_id: str = Field(min_length=1)
    permissions: frozenset[Permission] = frozenset()
    resource_company_bindings: tuple[ResourceCompanyBinding, ...] = ()


class ActionAuthorizationResolver(Protocol):
    def __call__(self, *, user_id: str) -> ProductionActionPrincipal: ...


class PendingActionSafe(_FrozenModel):
    action_id: str
    origin_run_id: str
    tool_name: str
    action_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    impact: str
    required_permissions: tuple[str, ...]
    confirmation_required: Literal[True] = True
    state: Literal[
        "PENDING_CONFIRMATION",
        "CONFIRMED",
        "EXECUTING",
        "ACCEPTED",
        "BLOCKED",
        "NOT_ACCEPTED",
        "UNCERTAIN",
    ]
    execution_run_id: str | None = None


@dataclass(frozen=True)
class _PendingActionPrivate:
    safe: PendingActionSafe
    requester_user_sha256: str
    arguments: dict[str, Any]
    idempotency_key: str


def _user_hash(user_id: str) -> str:
    return sha256(user_id.encode("utf-8")).hexdigest()


def _safe_action_id(origin_raw_run_id: str, fingerprint: str) -> str:
    material = f"{origin_raw_run_id}:{fingerprint}".encode("utf-8")
    return "act_" + sha256(material).hexdigest()[:24]


class PendingActionCustody:
    """Private persistent custody for exact action payloads.

    This database is intentionally separate from the browser-safe observability database. Raw
    arguments and the raw idempotency key never enter the public read model or frontend.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("pending action custody requires a persistent path")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        connection = _duckdb().connect(self.path)
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_actions (
                    action_id VARCHAR PRIMARY KEY,
                    origin_run_id VARCHAR NOT NULL,
                    requester_user_sha256 VARCHAR NOT NULL,
                    tool_name VARCHAR NOT NULL,
                    action_fingerprint VARCHAR NOT NULL,
                    impact VARCHAR NOT NULL,
                    required_permissions_json VARCHAR NOT NULL,
                    arguments_json VARCHAR NOT NULL,
                    idempotency_key VARCHAR NOT NULL,
                    state VARCHAR NOT NULL,
                    execution_run_id VARCHAR,
                    UNIQUE(origin_run_id, action_fingerprint)
                )
                """
            )
        finally:
            connection.close()

    def create_or_get(
        self,
        *,
        origin_raw_run_id: str,
        requester_user_id: str,
        tool: ToolSpec,
        arguments: dict[str, Any],
    ) -> PendingActionSafe:
        fingerprint = action_fingerprint(tool, arguments)
        origin_run_id = safe_run_id(origin_raw_run_id)
        action_id = _safe_action_id(origin_raw_run_id, fingerprint)
        permissions = tuple(permission.value for permission in tool.required_permissions)
        with self._lock:
            connection = _duckdb().connect(self.path)
            try:
                existing = connection.execute(
                    "SELECT action_id FROM pending_actions WHERE origin_run_id = ? AND action_fingerprint = ?",
                    [origin_run_id, fingerprint],
                ).fetchone()
                if existing is None:
                    connection.execute(
                        """
                        INSERT INTO pending_actions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            action_id,
                            origin_run_id,
                            _user_hash(requester_user_id),
                            tool.name,
                            fingerprint,
                            tool.impact.value,
                            json.dumps(permissions, separators=(",", ":")),
                            json.dumps(arguments, sort_keys=True, separators=(",", ":")),
                            "idem-" + uuid4().hex,
                            "PENDING_CONFIRMATION",
                            None,
                        ],
                    )
                else:
                    action_id = str(existing[0])
            finally:
                connection.close()
        return self.get_safe(action_id)

    def _load_private(self, action_id: str) -> _PendingActionPrivate | None:
        connection = _duckdb().connect(self.path, read_only=True)
        try:
            row = connection.execute(
                """
                SELECT action_id, origin_run_id, requester_user_sha256, tool_name,
                       action_fingerprint, impact, required_permissions_json, arguments_json,
                       idempotency_key, state, execution_run_id
                FROM pending_actions WHERE action_id = ?
                """,
                [action_id],
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        safe = PendingActionSafe(
            action_id=str(row[0]),
            origin_run_id=str(row[1]),
            tool_name=str(row[3]),
            action_fingerprint=str(row[4]),
            impact=str(row[5]),
            required_permissions=tuple(json.loads(str(row[6]))),
            state=str(row[9]),  # type: ignore[arg-type]
            execution_run_id=None if row[10] is None else str(row[10]),
        )
        return _PendingActionPrivate(
            safe=safe,
            requester_user_sha256=str(row[2]),
            arguments=dict(json.loads(str(row[7]))),
            idempotency_key=str(row[8]),
        )

    def get_safe(self, action_id: str) -> PendingActionSafe:
        item = self._load_private(action_id)
        if item is None:
            raise KeyError(action_id)
        return item.safe

    def get_private_for_requester(
        self,
        *,
        action_id: str,
        requester_user_id: str,
    ) -> _PendingActionPrivate:
        item = self._load_private(action_id)
        if item is None:
            raise KeyError(action_id)
        if item.requester_user_sha256 != _user_hash(requester_user_id):
            raise PermissionError("action_requester_mismatch")
        return item

    def list_safe_for_origin(self, origin_run_id: str) -> list[PendingActionSafe]:
        connection = _duckdb().connect(self.path, read_only=True)
        try:
            rows = connection.execute(
                "SELECT action_id FROM pending_actions WHERE origin_run_id = ? ORDER BY action_id",
                [origin_run_id],
            ).fetchall()
        finally:
            connection.close()
        return [self.get_safe(str(row[0])) for row in rows]

    def transition(
        self,
        *,
        action_id: str,
        expected_states: frozenset[str],
        new_state: str,
        execution_run_id: str | None = None,
    ) -> bool:
        with self._lock:
            connection = _duckdb().connect(self.path)
            try:
                row = connection.execute(
                    "SELECT state FROM pending_actions WHERE action_id = ?",
                    [action_id],
                ).fetchone()
                if row is None or str(row[0]) not in expected_states:
                    return False
                connection.execute(
                    "UPDATE pending_actions SET state = ?, execution_run_id = COALESCE(?, execution_run_id) WHERE action_id = ?",
                    [new_state, execution_run_id, action_id],
                )
                return True
            finally:
                connection.close()


class DuckDBActionIdempotencyLedger:
    """Persistent one-shot claim ledger for consequential actions.

    The process lock plus database uniqueness guarantees exactly one claim in the supported
    single product process, including concurrent worker threads; persistence guarantees that a
    restart cannot silently forget a prior claim. Horizontal multi-process execution is not
    claimed by this adapter and remains a future external-ledger boundary.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("action idempotency ledger requires a persistent path")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        connection = _duckdb().connect(self.path)
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS action_claims (
                    idempotency_key_sha256 VARCHAR PRIMARY KEY,
                    action_fingerprint VARCHAR UNIQUE NOT NULL,
                    action_id VARCHAR NOT NULL,
                    state VARCHAR NOT NULL
                )
                """
            )
        finally:
            connection.close()

    def claim(self, *, key_sha256: str, action_fingerprint: str, action_id: str) -> bool:
        with self._lock:
            connection = _duckdb().connect(self.path)
            try:
                existing = connection.execute(
                    "SELECT idempotency_key_sha256 FROM action_claims WHERE idempotency_key_sha256 = ? OR action_fingerprint = ?",
                    [key_sha256, action_fingerprint],
                ).fetchone()
                if existing is not None:
                    return False
                connection.execute(
                    "INSERT INTO action_claims VALUES (?, ?, ?, 'CLAIMED')",
                    [key_sha256, action_fingerprint, action_id],
                )
                return True
            finally:
                connection.close()

    def mark(self, *, key_sha256: str, state: str) -> None:
        with self._lock:
            connection = _duckdb().connect(self.path)
            try:
                connection.execute(
                    "UPDATE action_claims SET state = ? WHERE idempotency_key_sha256 = ?",
                    [state, key_sha256],
                )
            finally:
                connection.close()

    def get(self, key_sha256: str) -> dict[str, str] | None:
        connection = _duckdb().connect(self.path, read_only=True)
        try:
            row = connection.execute(
                "SELECT action_fingerprint, action_id, state FROM action_claims WHERE idempotency_key_sha256 = ?",
                [key_sha256],
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return {
            "action_fingerprint": str(row[0]),
            "action_id": str(row[1]),
            "state": str(row[2]),
        }


class PendingActionCapturePolicy(ResourcePolicy):
    """Validate an agent proposal and create private custody instead of executing it."""

    def __init__(
        self,
        *,
        principal: ProductionActionPrincipal,
        origin_raw_run_id: str,
        custody: PendingActionCustody,
        execution_guard: Callable[[], None] | None = None,
    ) -> None:
        self.principal = principal
        self.origin_raw_run_id = origin_raw_run_id
        self.custody = custody
        self.execution_guard = execution_guard
        self.last_pending: PendingActionSafe | None = None

    def check(self, tool: ToolSpec, arguments: dict[str, object]) -> PolicyDecision:
        # Horizontal runtimes bind this to the current lease/generation. Checking before every
        # tool protects read calls and pending-action custody from a stale worker after takeover.
        if self.execution_guard is not None:
            self.execution_guard()
        if tool.kind is not ToolKind.ACTION:
            return PolicyDecision(
                allowed=True,
                code="ALLOWED",
                reason="read tool outside action capture",
            )
        context = ProductionActionAuthorizationContext(
            execution_enabled=True,
            user_permissions=self.principal.permissions,
            user_company_id=self.principal.user_company_id,
            resource_company_bindings=self.principal.resource_company_bindings,
            confirmed_action_fingerprints=frozenset(),
            idempotency_bindings=(),
            consumed_idempotency_keys=frozenset(),
        )
        decision = ProductionActionSafetyPolicy(context=context).evaluate(tool, dict(arguments))
        allowed_pending_failures = {"CONFIRMATION_REQUIRED", "IDEMPOTENCY_KEY_REQUIRED"}
        blocking_failures = [
            code for code in decision.failed_codes if code not in allowed_pending_failures
        ]
        if blocking_failures:
            return PolicyDecision(
                allowed=False,
                code=blocking_failures[0],
                reason=f"prod-action-proposal-v2: {blocking_failures[0]}",
            )
        pending = self.custody.create_or_get(
            origin_raw_run_id=self.origin_raw_run_id,
            requester_user_id=self.principal.user_id,
            tool=tool,
            arguments=dict(arguments),
        )
        self.last_pending = pending
        return PolicyDecision(
            allowed=False,
            code="CONFIRMATION_REQUIRED",
            reason="prod-action-proposal-v2: exact action is privately custodied and requires operator confirmation",
        )


class ClaimingProductionActionSafetyPolicy(ProductionActionSafetyPolicy):
    def __init__(
        self,
        *,
        context: ProductionActionAuthorizationContext,
        ledger: DuckDBActionIdempotencyLedger,
        action_id: str,
    ) -> None:
        super().__init__(context=context)
        self.ledger = ledger
        self.action_id = action_id
        self.claimed_key_sha256: str | None = None

    def check(self, tool: ToolSpec, arguments: dict[str, object]) -> PolicyDecision:
        decision = self.evaluate(tool, dict(arguments))
        if not decision.allowed:
            return super().check(tool, arguments)
        assert decision.idempotency_key_sha256 is not None
        claimed = self.ledger.claim(
            key_sha256=decision.idempotency_key_sha256,
            action_fingerprint=decision.action_fingerprint,
            action_id=self.action_id,
        )
        if not claimed:
            return PolicyDecision(
                allowed=False,
                code="DUPLICATE_ACTION",
                reason="prod-action-safety-v2: persistent idempotency claim already exists",
            )
        self.claimed_key_sha256 = decision.idempotency_key_sha256
        return PolicyDecision(
            allowed=True,
            code="ALLOWED",
            reason="prod-action-safety-v2: persistent claim acquired",
        )


class ActionProposalRealtimeProductionRuntime(ProductionRuntime):
    """Prospective runtime: consequential proposals become pending actions, never transport calls."""

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
            registry=registry,
            config=config,
        )
        self.observability_publisher = FailIsolatedObservabilityPublisher(observability_sink)
        self.authorization_resolver = authorization_resolver
        self.custody = custody

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

    def run(self, request: ProductionRequest) -> RunTrace:
        return self.prepare(request).execute()


class PreparedActionExecution:
    def __init__(
        self,
        *,
        action_id: str,
        runner: ObservableHarnessRunner,
        tool: ToolSpec,
        arguments: dict[str, Any],
        policy: ClaimingProductionActionSafetyPolicy,
        custody: PendingActionCustody,
        ledger: DuckDBActionIdempotencyLedger,
    ) -> None:
        self.action_id = action_id
        self.runner = runner
        self.tool = tool
        self.arguments = arguments
        self.policy = policy
        self.custody = custody
        self.ledger = ledger
        self._lock = Lock()
        self._executed = False

    def execute(self) -> RunTrace:
        with self._lock:
            if self._executed:
                raise RuntimeError("prepared_action_execution_already_executed")
            self._executed = True
        try:
            execution = self.runner.execute_tool(self.tool.name, self.arguments)
        except Exception:
            if self.policy.claimed_key_sha256 is not None:
                self.ledger.mark(
                    key_sha256=self.policy.claimed_key_sha256,
                    state="UNCERTAIN",
                )
            self.custody.transition(
                action_id=self.action_id,
                expected_states=frozenset({"EXECUTING"}),
                new_state="UNCERTAIN",
            )
            return self.runner.finish(
                {
                    "decision": "ABSTAIN",
                    "response_mode": "unavailable",
                    "reason_code": "ACTION_EXECUTION_UNCERTAIN",
                    "message": "The consequential action attempt is in an uncertain state and will not be retried automatically.",
                }
            )

        if not execution.executed:
            self.custody.transition(
                action_id=self.action_id,
                expected_states=frozenset({"EXECUTING"}),
                new_state="BLOCKED",
            )
            return self.runner.finish(
                {
                    "decision": "ABSTAIN",
                    "response_mode": "partial",
                    "reason_code": execution.blocked_code or "ACTION_BLOCKED",
                    "message": "The consequential action was blocked by the deterministic safety boundary.",
                }
            )

        body = execution.response.body if execution.response is not None else None
        accepted = isinstance(body, dict) and body.get("accepted") is True
        if self.policy.claimed_key_sha256 is not None:
            self.ledger.mark(
                key_sha256=self.policy.claimed_key_sha256,
                state="ACCEPTED" if accepted else "NOT_ACCEPTED",
            )
        self.custody.transition(
            action_id=self.action_id,
            expected_states=frozenset({"EXECUTING"}),
            new_state="ACCEPTED" if accepted else "NOT_ACCEPTED",
        )
        return self.runner.finish(
            {
                "decision": "ORIENT" if accepted else "ABSTAIN",
                "response_mode": "complete" if accepted else "partial",
                "reason_code": "ACTION_ACCEPTED" if accepted else "ACTION_NOT_ACCEPTED",
                "message": (
                    "The action was accepted by the TRACTIAN API."
                    if accepted
                    else "The API did not confirm accepted=true; no retry will be attempted automatically."
                ),
            }
        )


class ProductionActionExecutor:
    def __init__(
        self,
        *,
        custody: PendingActionCustody,
        ledger: DuckDBActionIdempotencyLedger,
        authorization_resolver: ActionAuthorizationResolver,
        transport_factory: Callable[[], RequestTransport],
        observability_sink: SafeObservabilityEventSink,
        registry: Mapping[str, ToolSpec] | None = None,
        actions_enabled: bool = False,
    ) -> None:
        self.custody = custody
        self.ledger = ledger
        self.authorization_resolver = authorization_resolver
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
        principal = self.authorization_resolver(user_id=requester_user_id)
        if principal.user_id != requester_user_id:
            raise RuntimeError("action_principal_user_mismatch")
        tool = self.registry[item.safe.tool_name]
        fingerprint = action_fingerprint(tool, item.arguments)
        if fingerprint != item.safe.action_fingerprint:
            raise RuntimeError("pending_action_fingerprint_drift")

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
