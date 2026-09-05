from __future__ import annotations

import re
from urllib import parse as urllib_parse


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class LiveDemoScopedRoleBootstrapError(RuntimeError):
    """Sanitized scoped-role bootstrap failure for the hosted demo."""


def _scoped_credentials(scoped_dsn: str) -> tuple[str, str]:
    parsed = urllib_parse.urlparse(scoped_dsn)
    role_name = urllib_parse.unquote(parsed.username or "")
    password = urllib_parse.unquote(parsed.password or "")
    if not _IDENTIFIER.fullmatch(role_name):
        raise LiveDemoScopedRoleBootstrapError("invalid_scoped_role_name")
    if not password:
        raise LiveDemoScopedRoleBootstrapError("scoped_role_password_required")
    return role_name, password


def ensure_live_demo_scoped_role(*, internal_dsn: str, scoped_dsn: str) -> str:
    """Create or password-bootstrap one least-privilege login role before app composition.

    This is an opt-in deployment bootstrap for a fresh hosted database. It never grants table
    privileges; the accepted PostgresOperationalDatabase initializer remains the sole owner of
    schema/RLS grants. Existing unsafe roles fail closed instead of being modified implicitly.
    """

    role_name, password = _scoped_credentials(scoped_dsn)
    try:
        import psycopg
        from psycopg import sql
    except ImportError as exc:  # pragma: no cover - production dependency guard
        raise LiveDemoScopedRoleBootstrapError("psycopg_required") from exc

    try:
        with psycopg.connect(internal_dsn, autocommit=True) as connection:
            row = connection.execute(
                """
                SELECT rolcanlogin, rolsuper, rolbypassrls, rolcreatedb, rolcreaterole,
                       rolreplication
                FROM pg_roles
                WHERE rolname = %s
                """,
                (role_name,),
            ).fetchone()
            if row is None:
                connection.execute(
                    sql.SQL(
                        "CREATE ROLE {} LOGIN NOSUPERUSER NOBYPASSRLS "
                        "NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD {}"
                    ).format(sql.Identifier(role_name), sql.Literal(password))
                )
            else:
                flags = tuple(bool(value) for value in row)
                expected = (True, False, False, False, False, False)
                if flags != expected:
                    raise LiveDemoScopedRoleBootstrapError("existing_scoped_role_is_privileged")
                connection.execute(
                    sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                        sql.Identifier(role_name), sql.Literal(password)
                    )
                )

            verified = connection.execute(
                """
                SELECT rolcanlogin, rolsuper, rolbypassrls, rolcreatedb, rolcreaterole,
                       rolreplication
                FROM pg_roles
                WHERE rolname = %s
                """,
                (role_name,),
            ).fetchone()
            if verified is None:
                raise LiveDemoScopedRoleBootstrapError("scoped_role_missing_after_bootstrap")
            if tuple(bool(value) for value in verified) != (
                True,
                False,
                False,
                False,
                False,
                False,
            ):
                raise LiveDemoScopedRoleBootstrapError("scoped_role_privilege_verification_failed")
    except LiveDemoScopedRoleBootstrapError:
        raise
    except Exception:
        raise LiveDemoScopedRoleBootstrapError("scoped_role_bootstrap_failed") from None

    return role_name
