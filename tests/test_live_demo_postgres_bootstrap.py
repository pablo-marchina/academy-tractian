from __future__ import annotations

import os
from urllib import parse as urllib_parse
from uuid import uuid4

import pytest

from academy_tractian.live_demo_postgres_bootstrap import (
    LiveDemoScopedRoleBootstrapError,
    ensure_live_demo_scoped_role,
)


def _postgres_test_dsn() -> str:
    return os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN", "").strip()


def _scoped_dsn(admin_dsn: str, *, role_name: str, password: str) -> str:
    parsed = urllib_parse.urlsplit(admin_dsn)
    host = parsed.hostname or "127.0.0.1"
    port = "" if parsed.port is None else f":{parsed.port}"
    user = urllib_parse.quote(role_name, safe="")
    secret = urllib_parse.quote(password, safe="")
    return urllib_parse.urlunsplit(
        (parsed.scheme, f"{user}:{secret}@{host}{port}", parsed.path, parsed.query, parsed.fragment)
    )


def test_scoped_role_bootstrap_creates_least_privilege_login_and_is_idempotent() -> None:
    admin_dsn = _postgres_test_dsn()
    if not admin_dsn:
        pytest.skip("POSTGRES_OPERATIONAL_TEST_DSN is required")

    import psycopg
    from psycopg import sql

    role_name = f"academy_bootstrap_{uuid4().hex[:16]}"
    password = "live-demo-test-secret-0123456789"
    scoped_dsn = _scoped_dsn(admin_dsn, role_name=role_name, password=password)
    try:
        assert (
            ensure_live_demo_scoped_role(internal_dsn=admin_dsn, scoped_dsn=scoped_dsn)
            == role_name
        )
        # A second bootstrap updates the password in-place without widening privileges.
        assert (
            ensure_live_demo_scoped_role(internal_dsn=admin_dsn, scoped_dsn=scoped_dsn)
            == role_name
        )
        with psycopg.connect(admin_dsn) as connection:
            row = connection.execute(
                """
                SELECT rolcanlogin, rolsuper, rolbypassrls, rolcreatedb, rolcreaterole,
                       rolreplication
                FROM pg_roles WHERE rolname = %s
                """,
                (role_name,),
            ).fetchone()
            assert row == (True, False, False, False, False, False)
        with psycopg.connect(scoped_dsn) as scoped:
            assert scoped.execute("SELECT current_user").fetchone() == (role_name,)
    finally:
        with psycopg.connect(admin_dsn, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role_name)))


def test_scoped_role_bootstrap_rejects_existing_bypassrls_role() -> None:
    admin_dsn = _postgres_test_dsn()
    if not admin_dsn:
        pytest.skip("POSTGRES_OPERATIONAL_TEST_DSN is required")

    import psycopg
    from psycopg import sql

    role_name = f"academy_unsafe_{uuid4().hex[:16]}"
    password = "unsafe-test-secret-0123456789"
    scoped_dsn = _scoped_dsn(admin_dsn, role_name=role_name, password=password)
    try:
        with psycopg.connect(admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN BYPASSRLS PASSWORD {}").format(
                    sql.Identifier(role_name), sql.Literal(password)
                )
            )
        with pytest.raises(
            LiveDemoScopedRoleBootstrapError,
            match="existing_scoped_role_is_privileged",
        ):
            ensure_live_demo_scoped_role(internal_dsn=admin_dsn, scoped_dsn=scoped_dsn)
    finally:
        with psycopg.connect(admin_dsn, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role_name)))


def test_scoped_role_bootstrap_requires_password_and_safe_identifier() -> None:
    with pytest.raises(LiveDemoScopedRoleBootstrapError, match="scoped_role_password_required"):
        ensure_live_demo_scoped_role(
            internal_dsn="postgresql://owner:secret@db.example.com/academy",
            scoped_dsn="postgresql://scoped@db.example.com/academy",
        )
    with pytest.raises(LiveDemoScopedRoleBootstrapError, match="invalid_scoped_role_name"):
        ensure_live_demo_scoped_role(
            internal_dsn="postgresql://owner:secret@db.example.com/academy",
            scoped_dsn="postgresql://bad-role:secret@db.example.com/academy",
        )
