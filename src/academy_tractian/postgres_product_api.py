from __future__ import annotations

from pathlib import Path
from typing import Callable

from fastapi import FastAPI

from research.e2.controller import DecisionSource
from research.e2.transport import RequestTransport

from .action_product_api import create_action_capable_product_app
from .postgres_action_operational import (
    PostgresActionIdempotencyLedger,
    PostgresPendingActionCustody,
)
from .postgres_operational import (
    PostgresOperationalDatabase,
    PostgresRunAccessStore,
    PostgresRunExecutionStore,
)
from .product_api import RuntimeContextProvider
from .production_actions_v2 import ActionAuthorizationResolver


def _required_tables_ready(database: PostgresOperationalDatabase) -> bool:
    names = ("run_ownership", "run_executions", "pending_actions", "action_claims")
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
    """Explicit migration/bootstrap entrypoint for mutable operational state."""

    database = PostgresOperationalDatabase(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
        initialize=True,
    )
    try:
        PostgresPendingActionCustody(database, initialize=True)
        PostgresActionIdempotencyLedger(database, initialize=True)
        if not database.ready() or not _required_tables_ready(database):
            raise RuntimeError("postgres_operational_schema_not_ready_after_initialize")
    finally:
        database.close()


def create_postgres_action_capable_product_app(
    *,
    db_path: str | Path,
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
    """Create the promoted production topology.

    PostgreSQL owns mutable multi-user operational state. DuckDB still owns the sanitized
    observability/evaluation read model at ``db_path``. Serving with ``initialize_schema=False``
    is the recommended production path after an explicit migration step.
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
        if not database.ready() or not _required_tables_ready(database):
            raise RuntimeError("postgres_operational_schema_not_ready")
        app = create_action_capable_product_app(
            db_path=db_path,
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
    except Exception:
        database.close()
        raise

    app.state.postgres_operational_database = database
    app.state.operational_backend = "postgresql"
    return app
