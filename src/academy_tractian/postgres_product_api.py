from __future__ import annotations

from typing import Callable

from fastapi import FastAPI

from research.e2.controller import DecisionSource
from research.e2.transport import RequestTransport

from .action_product_api import create_action_capable_product_app
from .operational_value_collection import attach_operational_value_collection_api
from .operational_value_pilot import OperationalPilotManifest, OperationalPilotPacket
from .postgres_action_execution_lease import PostgresActionExecutionLeaseStore
from .postgres_action_operational import (
    PostgresActionIdempotencyLedger,
    PostgresPendingActionCustody,
)
from .postgres_observability_store import PostgresObservabilityStore
from .postgres_operational import (
    PostgresOperationalDatabase,
    PostgresRunAccessStore,
    PostgresRunExecutionStore,
)
from .postgres_operational_value_v5 import PostgresOperationalPilotStoreV5
from .postgres_runtime_handoff import PostgresRuntimeHandoffStore
from .postgres_semantic_review import PostgresSemanticReviewStore
from .product_api import RuntimeContextProvider
from .production_actions_v2 import ActionAuthorizationResolver
from .realtime_wakeup import DEFAULT_POSTGRES_WAKEUP_CHANNEL, PostgresListenNotifyWakeup
from .semantic_human_calibration import SemanticAnnotationManifest, SemanticReviewerPacket
from .semantic_review_collection import attach_semantic_review_collection_api


_OBSERVABILITY_TABLES = (
    "observability_meta",
    "observability_runs",
    "observability_events",
    "observability_evidence",
    "observability_evaluations",
)


def _required_tables_ready(database: PostgresOperationalDatabase) -> bool:
    names = (
        "run_ownership",
        "run_executions",
        "runtime_work_items",
        "pending_actions",
        "action_claims",
        "action_execution_leases",
        "operational_pilot_tasks",
        "operational_pilot_assignments",
        "semantic_review_tasks",
        "semantic_review_assignments",
        *_OBSERVABILITY_TABLES,
    )
    with database.internal_pool.connection() as connection:
        rows = connection.execute(
            """
            SELECT c.relname
            FROM pg_class AS c
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname = %s AND c.relname = ANY(%s)
            """,
            (database.schema, list(names)),
        ).fetchall()
    return {str(row[0]) for row in rows} == set(names)


def initialize_postgres_operational_schema(
    *,
    internal_dsn: str,
    scoped_dsn: str,
    schema: str = "academy_operational",
) -> None:
    """Explicit migration/bootstrap entrypoint for all PostgreSQL production state."""

    database = PostgresOperationalDatabase(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
        initialize=True,
    )
    try:
        PostgresPendingActionCustody(database, initialize=True)
        PostgresActionIdempotencyLedger(database, initialize=True)
        action_lease_store = PostgresActionExecutionLeaseStore(database, initialize=True)
        runtime_handoff_store = PostgresRuntimeHandoffStore(database, initialize=True)
        pilot_store = PostgresOperationalPilotStoreV5(database, initialize=True)
        semantic_store = PostgresSemanticReviewStore(database, initialize=True)
        observability_store = PostgresObservabilityStore(database, initialize=True)
        if (
            not database.ready()
            or not action_lease_store.ready()
            or not runtime_handoff_store.ready()
            or not pilot_store.ready()
            or not semantic_store.ready()
            or not observability_store.ready()
            or not _required_tables_ready(database)
        ):
            raise RuntimeError("postgres_operational_schema_not_ready_after_initialize")
    finally:
        database.close()


def register_postgres_operational_pilot_packet(
    *,
    internal_dsn: str,
    scoped_dsn: str,
    organization_id: str,
    packet: OperationalPilotPacket,
    manifest: OperationalPilotManifest,
    schema: str = "academy_operational",
) -> None:
    """Trusted evaluator/admin bootstrap. The manifest is never attached to the serving API."""

    database = PostgresOperationalDatabase(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
        initialize=False,
    )
    try:
        store = PostgresOperationalPilotStoreV5(database, initialize=False)
        observability_store = PostgresObservabilityStore(database, initialize=False)
        runtime_handoff_store = PostgresRuntimeHandoffStore(database, initialize=False)
        action_lease_store = PostgresActionExecutionLeaseStore(database, initialize=False)
        if (
            not database.ready()
            or not store.ready()
            or not observability_store.ready()
            or not runtime_handoff_store.ready()
            or not action_lease_store.ready()
            or not _required_tables_ready(database)
        ):
            raise RuntimeError("postgres_operational_schema_not_ready")
        store.register_packet(
            organization_id=organization_id,
            packet=packet,
            manifest=manifest,
        )
    finally:
        database.close()


def register_postgres_semantic_review_packet(
    *,
    internal_dsn: str,
    scoped_dsn: str,
    organization_id: str,
    packet: SemanticReviewerPacket,
    manifest: SemanticAnnotationManifest,
    schema: str = "academy_operational",
) -> None:
    """Trusted held-out reviewer bootstrap; private manifest never enters serving responses."""

    database = PostgresOperationalDatabase(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
        initialize=False,
    )
    try:
        store = PostgresSemanticReviewStore(database, initialize=False)
        observability_store = PostgresObservabilityStore(database, initialize=False)
        runtime_handoff_store = PostgresRuntimeHandoffStore(database, initialize=False)
        action_lease_store = PostgresActionExecutionLeaseStore(database, initialize=False)
        if (
            not database.ready()
            or not store.ready()
            or not observability_store.ready()
            or not runtime_handoff_store.ready()
            or not action_lease_store.ready()
            or not _required_tables_ready(database)
        ):
            raise RuntimeError("postgres_operational_schema_not_ready")
        store.register_packet(
            organization_id=organization_id,
            packet=packet,
            manifest=manifest,
        )
    finally:
        database.close()


def create_postgres_action_capable_product_app(
    *,
    internal_dsn: str,
    scoped_dsn: str,
    decision_source_factory: Callable[[], DecisionSource],
    transport_factory: Callable[[], RequestTransport],
    context_provider: RuntimeContextProvider,
    authorization_resolver: ActionAuthorizationResolver,
    schema: str = "academy_operational",
    initialize_schema: bool = False,
    max_workers: int = 4,
    provider_calls_enabled: bool = True,
    actions_enabled: bool = False,
    heartbeat_interval_ms: int = 1000,
    realtime_fallback_poll_ms: int = 1000,
    runtime_handoff_lease_seconds: float = 15.0,
    runtime_handoff_scan_ms: int = 500,
    action_execution_lease_seconds: float = 15.0,
    action_execution_lease_scan_ms: int = 500,
    action_execution_orphan_grace_seconds: float = 5.0,
) -> FastAPI:
    """Create the promoted no-local PostgreSQL production topology.

    All mutable operational state and the sanitized observability/evaluation read model share
    the qualified PostgreSQL substrate. The production entrypoint intentionally exposes no file
    path parameter: serving cannot select a local persistence backend by configuration accident.
    With ``initialize_schema=False`` it remains fail-closed until the explicit migration step has
    established every required table and policy.

    Realtime coordination uses one LISTEN/NOTIFY listener per application replica. PostgreSQL
    rows remain authoritative; NOTIFY is only a wakeup and a bounded fallback cursor read
    preserves eventual delivery if a notification is missed.

    Read-only runtime execution uses a PostgreSQL SKIP LOCKED lease queue and may move to another
    replica after expiry. Consequential action execution deliberately uses a different,
    non-transferable lease: a healthy owner renews it, while expiry means UNCERTAIN and never
    authorizes another transport attempt.
    """

    database = PostgresOperationalDatabase(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
        max_size=max(8, max_workers * 4),
        initialize=initialize_schema,
    )
    wakeup = PostgresListenNotifyWakeup(
        dsn=internal_dsn,
        channel=DEFAULT_POSTGRES_WAKEUP_CHANNEL,
    )
    try:
        custody = PostgresPendingActionCustody(database, initialize=initialize_schema)
        ledger = PostgresActionIdempotencyLedger(database, initialize=initialize_schema)
        action_lease_store = PostgresActionExecutionLeaseStore(
            database,
            initialize=initialize_schema,
            orphan_grace_seconds=action_execution_orphan_grace_seconds,
        )
        runtime_handoff_store = PostgresRuntimeHandoffStore(
            database,
            initialize=initialize_schema,
        )
        pilot_store = PostgresOperationalPilotStoreV5(database, initialize=initialize_schema)
        semantic_store = PostgresSemanticReviewStore(database, initialize=initialize_schema)
        observability_store = PostgresObservabilityStore(
            database,
            initialize=initialize_schema,
            notify_channel=DEFAULT_POSTGRES_WAKEUP_CHANNEL,
        )
        if (
            not database.ready()
            or not action_lease_store.ready()
            or not runtime_handoff_store.ready()
            or not pilot_store.ready()
            or not semantic_store.ready()
            or not observability_store.ready()
            or not _required_tables_ready(database)
        ):
            raise RuntimeError("postgres_operational_schema_not_ready")
        app = create_action_capable_product_app(
            observability_store=observability_store,
            decision_source_factory=decision_source_factory,
            transport_factory=transport_factory,
            context_provider=context_provider,
            authorization_resolver=authorization_resolver,
            custody_store=custody,
            action_ledger=ledger,
            action_execution_lease_store=action_lease_store,
            run_access_store=PostgresRunAccessStore(database),
            execution_store=PostgresRunExecutionStore(database),
            runtime_handoff_store=runtime_handoff_store,
            operational_close=database.close,
            max_workers=max_workers,
            provider_calls_enabled=provider_calls_enabled,
            actions_enabled=actions_enabled,
            heartbeat_interval_ms=heartbeat_interval_ms,
            realtime_wakeup=wakeup,
            realtime_fallback_poll_ms=realtime_fallback_poll_ms,
            runtime_handoff_lease_seconds=runtime_handoff_lease_seconds,
            runtime_handoff_scan_ms=runtime_handoff_scan_ms,
            action_execution_lease_seconds=action_execution_lease_seconds,
            action_execution_lease_scan_ms=action_execution_lease_scan_ms,
        )
        attach_operational_value_collection_api(
            app,
            context_provider=context_provider,
            store=pilot_store,
        )
        attach_semantic_review_collection_api(
            app,
            context_provider=context_provider,
            store=semantic_store,
        )
    except Exception:
        wakeup.close()
        database.close()
        raise

    app.state.postgres_operational_database = database
    app.state.operational_value_collection_store = pilot_store
    app.state.semantic_review_collection_store = semantic_store
    app.state.observability_backend = "postgresql"
    app.state.operational_backend = "postgresql"
    app.state.realtime_backend = "postgresql_listen_notify"
    app.state.runtime_handoff_backend = "postgresql_skip_locked_lease"
    app.state.action_execution_lease_backend = "postgresql_non_transferable_lease"
    app.state.local_test_storage_enabled = False
    return app
