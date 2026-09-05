from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256
import ipaddress
import json
import re
from typing import Any
from urllib.parse import parse_qs, urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator


_LOCAL_HOST_ALIASES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "host.docker.internal",
        "gateway.docker.internal",
        "kubernetes.docker.internal",
    }
)


def _fingerprint(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _hostname_is_local(hostname: str | None) -> bool:
    if hostname is None:
        return True
    normalized = hostname.rstrip(".").lower()
    if normalized in _LOCAL_HOST_ALIASES or normalized.endswith(".localhost"):
        return True
    address_literal = normalized.split("%", 1)[0]
    try:
        address = ipaddress.ip_address(address_literal)
    except ValueError:
        return False
    return address.is_loopback or address.is_unspecified


def _dsn_metadata(dsn: str) -> tuple[str, bool, bool]:
    parsed = urlsplit(dsn)
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname or not parsed.path:
        raise ValueError("invalid_hosted_postgres_dsn")
    if _hostname_is_local(parsed.hostname):
        raise ValueError("local_hosted_postgres_endpoint_forbidden")
    query = parse_qs(parsed.query, keep_blank_values=True)
    sslmode = tuple(query.get("sslmode", ()))
    tls_required = any(value in {"require", "verify-ca", "verify-full"} for value in sslmode)
    channel_binding = tuple(query.get("channel_binding", ()))
    channel_binding_required = "require" in channel_binding
    return _fingerprint(parsed.hostname.lower()), tls_required, channel_binding_required


@dataclass(frozen=True)
class ObservedPostgresSession:
    database_name: str
    role_name: str
    server_version: str
    role_superuser: bool
    role_bypass_rls: bool
    role_create_role: bool
    role_create_db: bool
    role_inherit: bool
    role_can_login: bool
    tls_active: bool


class HostedPostgresSessionEvidence(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    endpoint_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    role_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    database_name: str = Field(min_length=1, max_length=128)
    server_version: str = Field(min_length=1, max_length=128)
    server_major: int = Field(ge=1, le=99)
    tls_active: bool
    dsn_tls_required: bool
    channel_binding_required: bool
    role_superuser: bool
    role_bypass_rls: bool
    role_create_role: bool
    role_create_db: bool
    role_inherit: bool
    role_can_login: bool


class HostedPostgresPreflightEvidence(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "hosted-postgres-preflight-v1"
    internal: HostedPostgresSessionEvidence
    scoped: HostedPostgresSessionEvidence
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _verify_hash(self) -> "HostedPostgresPreflightEvidence":
        payload = self.model_dump(mode="json", exclude={"artifact_sha256"})
        expected = _fingerprint(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        if self.artifact_sha256 != expected:
            raise ValueError("hosted_postgres_preflight_artifact_hash_mismatch")
        return self


class HostedPostgresPreflightDecision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "hosted-postgres-preflight-decision-v1"
    outcome: str
    reason_codes: tuple[str, ...]


def _server_major(server_version: str) -> int:
    raw = server_version.strip().split(".", 1)[0]
    try:
        major = int(raw)
    except ValueError as exc:
        raise ValueError("invalid_postgres_server_version") from exc
    if major <= 0:
        raise ValueError("invalid_postgres_server_version")
    return major


def _session_evidence(
    metadata: tuple[str, bool, bool], observed: ObservedPostgresSession
) -> HostedPostgresSessionEvidence:
    endpoint_sha256, tls_required, channel_binding_required = metadata
    if not observed.database_name or not observed.role_name or not observed.server_version:
        raise ValueError("incomplete_postgres_session_observation")
    return HostedPostgresSessionEvidence(
        endpoint_sha256=endpoint_sha256,
        role_sha256=_fingerprint(observed.role_name),
        database_name=observed.database_name,
        server_version=observed.server_version,
        server_major=_server_major(observed.server_version),
        tls_active=observed.tls_active,
        dsn_tls_required=tls_required,
        channel_binding_required=channel_binding_required,
        role_superuser=observed.role_superuser,
        role_bypass_rls=observed.role_bypass_rls,
        role_create_role=observed.role_create_role,
        role_create_db=observed.role_create_db,
        role_inherit=observed.role_inherit,
        role_can_login=observed.role_can_login,
    )


def inspect_postgres_session(dsn: str) -> ObservedPostgresSession:
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - packaging guard
        raise RuntimeError("hosted Postgres preflight requires psycopg") from exc

    with psycopg.connect(dsn, connect_timeout=8) as connection:
        role_row = connection.execute(
            """
            SELECT
                current_database(),
                current_user,
                current_setting('server_version'),
                r.rolsuper,
                r.rolbypassrls,
                r.rolcreaterole,
                r.rolcreatedb,
                r.rolinherit,
                r.rolcanlogin
            FROM pg_roles AS r
            WHERE r.rolname = current_user
            """
        ).fetchone()
        if role_row is None:
            raise RuntimeError("hosted_postgres_current_role_unknown")
        ssl_row = connection.execute(
            "SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()"
        ).fetchone()
        if ssl_row is None:
            raise RuntimeError("hosted_postgres_ssl_state_unavailable")

    return ObservedPostgresSession(
        database_name=str(role_row[0]),
        role_name=str(role_row[1]),
        server_version=str(role_row[2]),
        role_superuser=bool(role_row[3]),
        role_bypass_rls=bool(role_row[4]),
        role_create_role=bool(role_row[5]),
        role_create_db=bool(role_row[6]),
        role_inherit=bool(role_row[7]),
        role_can_login=bool(role_row[8]),
        tls_active=bool(ssl_row[0]),
    )


def build_hosted_postgres_preflight_evidence(
    *,
    internal_dsn: str,
    scoped_dsn: str,
    inspector: Callable[[str], ObservedPostgresSession] = inspect_postgres_session,
) -> HostedPostgresPreflightEvidence:
    # Validate both targets before any connection is attempted. A local or malformed DSN must fail
    # closed without causing network I/O.
    internal_metadata = _dsn_metadata(internal_dsn)
    scoped_metadata = _dsn_metadata(scoped_dsn)

    internal = _session_evidence(internal_metadata, inspector(internal_dsn))
    scoped = _session_evidence(scoped_metadata, inspector(scoped_dsn))
    payload: dict[str, Any] = {
        "schema_version": "hosted-postgres-preflight-v1",
        "internal": internal.model_dump(mode="json"),
        "scoped": scoped.model_dump(mode="json"),
    }
    artifact_sha256 = _fingerprint(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return HostedPostgresPreflightEvidence(
        internal=internal,
        scoped=scoped,
        artifact_sha256=artifact_sha256,
    )


def decide_hosted_postgres_preflight(
    evidence: HostedPostgresPreflightEvidence,
    *,
    required_server_major: int = 18,
) -> HostedPostgresPreflightDecision:
    reasons: list[str] = []
    internal = evidence.internal
    scoped = evidence.scoped

    if internal.role_sha256 == scoped.role_sha256:
        reasons.append("INTERNAL_AND_SCOPED_ROLE_NOT_DISTINCT")
    if internal.database_name != scoped.database_name:
        reasons.append("DATABASE_MISMATCH")
    if internal.server_major != required_server_major or scoped.server_major != required_server_major:
        reasons.append("POSTGRES_MAJOR_MISMATCH")
    if not internal.dsn_tls_required or not scoped.dsn_tls_required:
        reasons.append("DSN_TLS_NOT_REQUIRED")
    if not internal.tls_active or not scoped.tls_active:
        reasons.append("LIVE_TLS_NOT_ACTIVE")
    if scoped.role_superuser:
        reasons.append("SCOPED_ROLE_SUPERUSER")
    if scoped.role_bypass_rls:
        reasons.append("SCOPED_ROLE_BYPASSES_RLS")
    if scoped.role_create_role:
        reasons.append("SCOPED_ROLE_CAN_CREATE_ROLE")
    if scoped.role_create_db:
        reasons.append("SCOPED_ROLE_CAN_CREATE_DB")
    if scoped.role_inherit:
        reasons.append("SCOPED_ROLE_INHERITS_PRIVILEGES")
    if not scoped.role_can_login:
        reasons.append("SCOPED_ROLE_CANNOT_LOGIN")

    deduped = tuple(dict.fromkeys(reasons))
    return HostedPostgresPreflightDecision(
        outcome="PREFLIGHT_PASS" if not deduped else "PREFLIGHT_FAIL",
        reason_codes=deduped,
    )
