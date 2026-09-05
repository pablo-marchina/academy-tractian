from __future__ import annotations

import os

import psycopg
import pytest

from academy_tractian.hosted_postgres_provisioning import provision_hosted_postgres


MIGRATION_DSN = os.environ.get("HOSTED_TEST_MIGRATION_DSN")
SERVICE_DSN = os.environ.get("HOSTED_TEST_SERVICE_DSN")
SCOPED_DSN = os.environ.get("HOSTED_TEST_SCOPED_DSN")

pytestmark = pytest.mark.skipif(
    not (MIGRATION_DSN and SERVICE_DSN and SCOPED_DSN),
    reason="hosted PostgreSQL provisioning DSNs not configured",
)


def test_provisioning_creates_least_privilege_roles_and_is_idempotent() -> None:
    assert MIGRATION_DSN and SERVICE_DSN and SCOPED_DSN
    first = provision_hosted_postgres(
        migration_owner_dsn=MIGRATION_DSN,
        service_dsn=SERVICE_DSN,
        scoped_dsn=SCOPED_DSN,
        schema="academy_hosted_ci",
    )
    second = provision_hosted_postgres(
        migration_owner_dsn=MIGRATION_DSN,
        service_dsn=SERVICE_DSN,
        scoped_dsn=SCOPED_DSN,
        schema="academy_hosted_ci",
    )
    assert first == second
    assert first["migration_owner_retained_by_serving"] is False
    assert first["service_role_ddl"] is False
    assert first["scoped_role_bypass_rls"] is False
    assert first["ready"] is True

    with psycopg.connect(MIGRATION_DSN) as connection:
        rows = connection.execute(
            """
            SELECT rolname, rolsuper, rolbypassrls, rolcreatedb, rolcreaterole, rolreplication
            FROM pg_roles
            WHERE rolname IN ('academy_hosted_service', 'academy_hosted_scoped')
            ORDER BY rolname
            """
        ).fetchall()
        assert rows == [
            ("academy_hosted_scoped", False, False, False, False, False),
            ("academy_hosted_service", False, False, False, False, False),
        ]
        owner = connection.execute(
            """
            SELECT pg_get_userbyid(c.relowner)
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'academy_hosted_ci' AND c.relname = 'run_ownership'
            """
        ).fetchone()
        assert owner is not None
        assert owner[0] not in {"academy_hosted_service", "academy_hosted_scoped"}

    with psycopg.connect(SERVICE_DSN) as connection:
        privileges = connection.execute(
            """
            SELECT
                has_schema_privilege(current_user, 'academy_hosted_ci', 'USAGE'),
                has_schema_privilege(current_user, 'academy_hosted_ci', 'CREATE'),
                has_table_privilege(current_user, 'academy_hosted_ci.run_ownership', 'SELECT'),
                has_table_privilege(current_user, 'academy_hosted_ci.run_ownership', 'INSERT')
            """
        ).fetchone()
        assert privileges == (True, False, True, True)

    with psycopg.connect(SCOPED_DSN) as connection:
        privileges = connection.execute(
            """
            SELECT
                has_schema_privilege(current_user, 'academy_hosted_ci', 'USAGE'),
                has_schema_privilege(current_user, 'academy_hosted_ci', 'CREATE'),
                has_table_privilege(current_user, 'academy_hosted_ci.run_ownership', 'SELECT'),
                has_table_privilege(current_user, 'academy_hosted_ci.run_ownership', 'INSERT'),
                has_table_privilege(current_user, 'academy_hosted_ci.run_executions', 'SELECT')
            """
        ).fetchone()
        assert privileges == (True, False, True, False, False)
