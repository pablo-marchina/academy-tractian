from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.apply_hosted_postgres_migration_plan import (
    assert_migration_authorized,
    execute_exact_migration_sql,
    validate_exact_migration_plan,
)
from scripts.generate_hosted_postgres_migration_sql import (
    build_migration_manifest,
    build_migration_sql,
)


def _write_plan(tmp_path: Path) -> tuple[Path, Path]:
    sql = build_migration_sql()
    manifest = build_migration_manifest(sql)
    sql_path = tmp_path / "migration.sql"
    manifest_path = tmp_path / "migration.json"
    sql_path.write_text(sql, encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    return sql_path, manifest_path


def test_exact_generated_plan_is_accepted_byte_for_byte(tmp_path: Path) -> None:
    sql_path, manifest_path = _write_plan(tmp_path)
    sql, manifest = validate_exact_migration_plan(sql_path=sql_path, manifest_path=manifest_path)
    assert sql == build_migration_sql()
    assert manifest == build_migration_manifest(sql)


def test_tampered_sql_is_rejected_before_any_database_execution(tmp_path: Path) -> None:
    sql_path, manifest_path = _write_plan(tmp_path)
    sql_path.write_text(sql_path.read_text(encoding="utf-8") + "\nSELECT 1;\n", encoding="utf-8")
    with pytest.raises(ValueError, match="migration_sql_not_canonical"):
        validate_exact_migration_plan(sql_path=sql_path, manifest_path=manifest_path)


def test_tampered_manifest_is_rejected(tmp_path: Path) -> None:
    sql_path, manifest_path = _write_plan(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["statement_count"] += 1
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="migration_manifest_not_canonical"):
        validate_exact_migration_plan(sql_path=sql_path, manifest_path=manifest_path)


def test_explicit_allow_flag_is_required_for_even_temporary_validation() -> None:
    with pytest.raises(PermissionError, match="migration_not_explicitly_allowed"):
        assert_migration_authorized(
            allow_migration=False,
            target_environment="temporary_validation",
            approval_ref=None,
        )
    assert_migration_authorized(
        allow_migration=True,
        target_environment="temporary_validation",
        approval_ref=None,
    )


def test_candidate_main_requires_approval_reference() -> None:
    with pytest.raises(PermissionError, match="candidate_main_migration_requires_approval_reference"):
        assert_migration_authorized(
            allow_migration=True,
            target_environment="candidate_main",
            approval_ref=None,
        )
    assert_migration_authorized(
        allow_migration=True,
        target_environment="candidate_main",
        approval_ref="approval-123",
    )


class _FakeConnection:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql: str) -> None:
        self.executed.append(sql)


def test_executor_sends_exact_artifact_once_with_autocommit() -> None:
    fake = _FakeConnection()
    calls = []

    def connect(dsn: str, **kwargs):
        calls.append((dsn, kwargs))
        return fake

    sql = "BEGIN;\nSELECT 1;\nCOMMIT;\n"
    execute_exact_migration_sql("postgresql://example.invalid/db", sql, connection_factory=connect)
    assert calls == [("postgresql://example.invalid/db", {"autocommit": True, "connect_timeout": 8})]
    assert fake.executed == [sql]
