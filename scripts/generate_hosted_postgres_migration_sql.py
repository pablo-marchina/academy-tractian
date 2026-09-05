from __future__ import annotations

import argparse
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterator

from academy_tractian.postgres_action_operational import (
    PostgresActionIdempotencyLedger,
    PostgresPendingActionCustody,
)
from academy_tractian.postgres_campaign_evidence_store import PostgresCampaignEvidenceStore
from academy_tractian.postgres_integration_evidence_store import PostgresIntegrationEvidenceStore
from academy_tractian.postgres_observability_store import PostgresObservabilityStore
from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.postgres_operational_value_v5 import PostgresOperationalPilotStoreV5
from academy_tractian.postgres_semantic_review import PostgresSemanticReviewStore


ROOT = Path(__file__).resolve().parents[1]
SCOPED_ROLE = "academy_tractian_rls"
SCHEMA_VERSION = "hosted-postgres-migration-plan-v1"
SOURCE_PATHS = (
    "src/academy_tractian/postgres_operational.py",
    "src/academy_tractian/postgres_action_operational.py",
    "src/academy_tractian/postgres_operational_value.py",
    "src/academy_tractian/postgres_operational_value_v5.py",
    "src/academy_tractian/postgres_semantic_review.py",
    "src/academy_tractian/postgres_observability_store.py",
    "src/academy_tractian/postgres_integration_evidence_store.py",
    "src/academy_tractian/postgres_campaign_evidence_store.py",
)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
    ).hexdigest()


def source_manifest() -> dict[str, str]:
    return {
        path: sha256((ROOT / path).read_bytes()).hexdigest()
        for path in SOURCE_PATHS
    }


def source_manifest_sha256() -> str:
    return _canonical_sha256(source_manifest())


def _sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not (value == value and abs(value) != float("inf")):
            raise ValueError("non_finite_sql_literal_forbidden")
        return repr(value)
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    raise TypeError(f"unsupported_migration_sql_parameter:{type(value).__name__}")


def _render_query(query: object, params: object | None) -> str:
    text = str(query).strip()
    if params is None:
        rendered = text
    else:
        if not isinstance(params, (tuple, list)):
            raise TypeError("migration_sql_parameters_must_be_positional_sequence")
        pieces = text.split("%s")
        if len(pieces) - 1 != len(params):
            raise ValueError("migration_sql_parameter_count_mismatch")
        rendered_parts: list[str] = [pieces[0]]
        for value, tail in zip(params, pieces[1:], strict=True):
            rendered_parts.append(_sql_literal(value))
            rendered_parts.append(tail)
        rendered = "".join(rendered_parts)
    if "%s" in rendered:
        raise ValueError("unrendered_migration_parameter")
    return rendered.rstrip().rstrip(";") + ";"


class _RecordedResult:
    def __init__(self, row: tuple[object, ...] | None = None) -> None:
        self._row = row

    def fetchone(self) -> tuple[object, ...] | None:
        return self._row

    def fetchall(self) -> list[tuple[object, ...]]:
        return [] if self._row is None else [self._row]


class _RecordingConnection:
    def __init__(self, statements: list[str], *, scoped_role: str | None) -> None:
        self._statements = statements
        self._scoped_role = scoped_role

    @contextmanager
    def transaction(self) -> Iterator[None]:
        yield

    def execute(self, query: object, params: object | None = None) -> _RecordedResult:
        normalized = " ".join(str(query).split()).lower()
        if self._scoped_role is not None and normalized == "select current_user":
            return _RecordedResult((self._scoped_role,))
        if normalized.startswith("select"):
            raise RuntimeError(f"unexpected_select_during_migration_plan:{normalized[:120]}")
        self._statements.append(_render_query(query, params))
        return _RecordedResult()


class _RecordingPool:
    def __init__(self, statements: list[str], *, scoped_role: str | None = None) -> None:
        self._statements = statements
        self._scoped_role = scoped_role

    @contextmanager
    def connection(self) -> Iterator[_RecordingConnection]:
        yield _RecordingConnection(self._statements, scoped_role=self._scoped_role)


def _record_runtime_migration_statements() -> tuple[str, ...]:
    statements: list[str] = []
    database = object.__new__(PostgresOperationalDatabase)
    database.schema = "academy_operational"
    database.internal_pool = _RecordingPool(statements)
    database.scoped_pool = _RecordingPool(statements, scoped_role=SCOPED_ROLE)

    # This order is identical to scripts/migrate_hosted_postgres.py. No production DDL is copied
    # here: the canonical initialize_schema implementations emit every statement into the recorder.
    database.initialize_schema()
    PostgresPendingActionCustody(database).initialize_schema()
    PostgresActionIdempotencyLedger(database).initialize_schema()
    PostgresOperationalPilotStoreV5(database).initialize_schema()
    PostgresSemanticReviewStore(database).initialize_schema()
    PostgresObservabilityStore(database).initialize_schema()
    PostgresIntegrationEvidenceStore(database).initialize_schema()
    PostgresCampaignEvidenceStore(database).initialize_schema()
    return tuple(statements)


def build_migration_sql() -> str:
    statements = _record_runtime_migration_statements()
    manifest = source_manifest()
    header = (
        f"-- {SCHEMA_VERSION}\n"
        "-- provider_free_generation: true\n"
        "-- network_calls_performed: 0\n"
        f"-- scoped_role: {SCOPED_ROLE}\n"
        f"-- source_manifest_sha256: {_canonical_sha256(manifest)}\n"
        f"-- statement_count: {len(statements)}\n"
        "-- Generated by executing canonical initialize_schema methods against recording pools.\n"
        "-- Do not hand-edit this file; regenerate from the source schema implementations.\n"
    )
    return header + "\nBEGIN;\n\n" + "\n\n".join(statements) + "\n\nCOMMIT;\n"


def build_migration_manifest(sql: str) -> dict[str, object]:
    statements = _record_runtime_migration_statements()
    sources = source_manifest()
    return {
        "schema_version": SCHEMA_VERSION,
        "provider_free_generation": True,
        "network_calls_performed": 0,
        "scoped_role": SCOPED_ROLE,
        "source_files": sources,
        "source_manifest_sha256": _canonical_sha256(sources),
        "statement_count": len(statements),
        "sql_sha256": sha256(sql.encode("utf-8")).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic hosted PostgreSQL DDL")
    parser.add_argument("--sql-output", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, required=True)
    args = parser.parse_args()

    sql = build_migration_sql()
    manifest = build_migration_manifest(sql)
    args.sql_output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    args.sql_output.write_text(sql, encoding="utf-8")
    args.manifest_output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
