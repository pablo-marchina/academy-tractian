from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import unquote, urlsplit

from psycopg import sql

from .postgres_operational import PostgresOperationalDatabase
from .postgres_product_api import initialize_postgres_operational_schema


_ROLE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,62}$")


@dataclass(frozen=True, repr=False)
class _RoleCredential:
    name: str
    password: str
    database: str

    def __repr__(self) -> str:
        return f"_RoleCredential(name={self.name!r}, password=<redacted>, database={self.database!r})"


def _psycopg():
    import psycopg

    return psycopg


def _role_from_dsn(dsn: str, *, label: str) -> _RoleCredential:
    parsed = urlsplit(dsn)
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname or not parsed.path:
        raise ValueError(f"invalid_{label}_dsn")
    if parsed.username is None or parsed.password is None:
        raise ValueError(f"{label}_dsn_requires_explicit_credentials")
    name = unquote(parsed.username)
    password = unquote(parsed.password)
    database = unquote(parsed.path.lstrip("/"))
    if not _ROLE.fullmatch(name):
        raise ValueError(f"invalid_{label}_role")
    if not password or not database:
        raise ValueError(f"invalid_{label}_dsn")
    return _RoleCredential(name=name, password=password, database=database)


def _assert_safe_role(connection, role_name: str, *, label: str) -> None:
    row = connection.execute(
        """
        SELECT rolsuper, rolbypassrls, rolcreatedb, rolcreaterole, rolreplication, rolcanlogin
        FROM pg_roles WHERE rolname = %s
        """,
        (role_name,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"{label}_role_missing")
    if bool(row[0]) or bool(row[1]) or bool(row[2]) or bool(row[3]) or bool(row[4]) or not bool(row[5]):
        raise RuntimeError(f"{label}_role_privileges_unsafe")


def _ensure_role(connection, credential: _RoleCredential, *, label: str) -> None:
    exists = connection.execute(
        "SELECT 1 FROM pg_roles WHERE rolname = %s",
        (credential.name,),
    ).fetchone()
    if exists is None:
        # psycopg.sql quotes both the identifier and password literal. The password never appears
        # in application logs/repr and this code is used only by the privileged migration process.
        connection.execute(
            sql.SQL(
                "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS "
                "NOCREATEDB NOCREATEROLE NOREPLICATION"
            ).format(sql.Identifier(credential.name), sql.Literal(credential.password))
        )
    _assert_safe_role(connection, credential.name, label=label)


def _verify_not_table_owner(connection, *, schema: str, roles: tuple[str, ...]) -> None:
    rows = connection.execute(
        """
        SELECT c.relname, pg_get_userbyid(c.relowner)
        FROM pg_class AS c
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = %s AND c.relkind IN ('r','p','S')
        """,
        (schema,),
    ).fetchall()
    for relation, owner in rows:
        if str(owner) in roles:
            raise RuntimeError(f"application_role_owns_relation:{relation}")


def provision_hosted_postgres(
    *,
    migration_owner_dsn: str,
    service_dsn: str,
    scoped_dsn: str,
    schema: str = "academy_operational",
) -> dict[str, object]:
    """Provision the hosted PostgreSQL boundary using a migration-only owner credential.

    This function is intentionally separate from serving. It creates application roles only when
    absent, initializes the canonical schema as the migration owner, grants the service role DML
    but no DDL, and leaves the scoped role limited to the existing RLS read channel. Existing role
    passwords are never changed implicitly.
    """

    service = _role_from_dsn(service_dsn, label="service")
    scoped = _role_from_dsn(scoped_dsn, label="scoped")
    if service.name == scoped.name:
        raise ValueError("service_and_scoped_roles_must_differ")
    if service.database != scoped.database:
        raise ValueError("service_and_scoped_databases_must_match")

    psycopg = _psycopg()
    with psycopg.connect(migration_owner_dsn, autocommit=True) as owner:
        current_user, current_database = owner.execute(
            "SELECT current_user, current_database()"
        ).fetchone()
        if str(current_database) != service.database:
            raise ValueError("migration_owner_database_mismatch")
        if str(current_user) in {service.name, scoped.name}:
            raise ValueError("migration_owner_must_be_distinct_from_application_roles")
        _ensure_role(owner, service, label="service")
        _ensure_role(owner, scoped, label="scoped")
        for role_name in (service.name, scoped.name):
            owner.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                    sql.Identifier(service.database), sql.Identifier(role_name)
                )
            )

    initialize_postgres_operational_schema(
        internal_dsn=migration_owner_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
    )

    with psycopg.connect(migration_owner_dsn, autocommit=True) as owner:
        _assert_safe_role(owner, service.name, label="service")
        _assert_safe_role(owner, scoped.name, label="scoped")
        owner.execute(
            sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(
                sql.Identifier(schema), sql.Identifier(service.name)
            )
        )
        owner.execute(
            sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {} TO {}").format(
                sql.Identifier(schema), sql.Identifier(service.name)
            )
        )
        owner.execute(
            sql.SQL("GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA {} TO {}").format(
                sql.Identifier(schema), sql.Identifier(service.name)
            )
        )
        owner.execute(
            sql.SQL("REVOKE CREATE ON SCHEMA {} FROM {}, {}").format(
                sql.Identifier(schema), sql.Identifier(service.name), sql.Identifier(scoped.name)
            )
        )
        # Scoped access is deliberately narrow even if a provider/database default is permissive.
        owner.execute(
            sql.SQL("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA {} FROM {}").format(
                sql.Identifier(schema), sql.Identifier(scoped.name)
            )
        )
        owner.execute(
            sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(
                sql.Identifier(schema), sql.Identifier(scoped.name)
            )
        )
        owner.execute(
            sql.SQL("GRANT SELECT ON {}.run_ownership TO {}").format(
                sql.Identifier(schema), sql.Identifier(scoped.name)
            )
        )
        _verify_not_table_owner(owner, schema=schema, roles=(service.name, scoped.name))

    # The same constructor used by serving must accept the least-privilege roles after migration.
    database = PostgresOperationalDatabase(
        internal_dsn=service_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
        initialize=False,
    )
    try:
        if not database.ready():
            raise RuntimeError("hosted_postgres_application_roles_not_ready")
    finally:
        database.close()

    return {
        "schema_version": "hosted-postgres-provisioning-v1",
        "schema": schema,
        "migration_owner_retained_by_serving": False,
        "service_role": service.name,
        "scoped_role": scoped.name,
        "service_role_ddl": False,
        "scoped_role_bypass_rls": False,
        "ready": True,
    }
