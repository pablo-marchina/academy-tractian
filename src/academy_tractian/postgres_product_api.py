from __future__ import annotations

from typing import Callable

from fastapi import FastAPI

from research.e2.controller import DecisionSource
from research.e2.transport import RequestTransport

from .action_product_api import create_action_capable_product_app
from .operational_value_collection import attach_operational_value_collection_api
from .operational_value_pilot import OperationalPilotManifest, OperationalPilotPacket
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
from .postgres_semantic_review import PostgresSemanticReviewStore
from .product_api import RuntimeContextProvider
from .production_actions_v2 import ActionAuthorizationResolver
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
        "pending_actions",
        "action_claims",
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
        pilot_store = PostgresOperationalPilotStoreV5(database, initialize=True)
        semantic_store = PostgresSemanticReviewStore(database, initialize=True)
        observability_store = PostgresObservabilityStore(database, initialize=True)
        if (
            not database.ready()
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
        if (
            not database.ready()
            or not store.ready()
            or not observability_store.ready()
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
        if (
            not database.ready()
            or not store.ready()
            or not observability_store.ready()
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
) -> FastAPI:
    """Create the promoted no-local PostgreSQL production topology.

    All mutable operational state and the sanitized observability/evaluation read model share
    the qualified PostgreSQL substrate. The production entrypoint intentionally exposes no file
    path parameter: serving cannot select a local persistence backend by configuration accident.
    With ``initialize_schema=False`` it remains fail-closed until the explicit migration step has
    established every required table and policy.
    """

    database = PostgresOperationalDatabase(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
        max_size=max(8, max_workers * 4),
        initialize=initialize_schema,
    )
    try:
        custody = PostgresPendingActionCustody(database, initialize=initialize_schema)
        ledger = PostgresActionIdempotencyLedger(database, initialize=initialize_schema)
        pilot_store = PostgresOperationalPilotStoreV5(database, initialize=initialize_schema)
        semantic_store = PostgresSemanticReviewStore(database, initialize=initialize_schema)
        observability_store = PostgresObservabilityStore(database, initialize=initialize_schema)
        if (
            not database.ready()
            or not pilot_store.ready()
            or not semantic_store.ready()
            or not observability_store.ready()
            or not _required_tables_ready(database)
        ):
            raise RuntimeError("postgres_operational_schema_not_ready")
        app = create_action_capable_product_app(
            # The generic composition seam still calls this argument ``db_path``. Passing the
            # shared database object selects PostgresObservabilityStore; it never becomes a path.
            db_path=database,  # type: ignore[arg-type]
            decision_source_factory=decision_source_factory,
            transport_factory=transport_factory,
            context_provider=context_provider,
            authorization_resolver=authorization_resolver,
            custody_store=custody,
            action_ledger=ledger,
            run_access_store=PostgresRunAccessStore(database),
            execution_store=PostgresRunExecutionStore(database),
            operational_close=database.close,
            max_workers=max_workers,
            provider_calls_enabled=provider_calls_enabled,
            actions_enabled=actions_enabled,
            heartbeat_interval_ms=heartbeat_interval_ms,
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
        database.close()
        raise

    app.state.postgres_operational_database = database
    app.state.operational_value_collection_store = pilot_store
    app.state.semantic_review_collection_store = semantic_store
    app.state.observability_backend = "postgresql"
    app.state.operational_backend = "postgresql"
    app.state.local_test_storage_enabled = False
    return app
