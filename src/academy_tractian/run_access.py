from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

import duckdb


RUN_ACCESS_SCHEMA_VERSION = "run-access-v1"


@dataclass(frozen=True, slots=True)
class RunOwnership:
    run_id: str
    organization_id: str
    user_id: str


class RunAccessStore(Protocol):
    """Operational ownership contract used by product authorization."""

    def ready(self) -> bool: ...

    def claim(self, *, run_id: str, organization_id: str, user_id: str) -> bool: ...

    def get(self, run_id: str) -> RunOwnership | None: ...

    def get_many(self, run_ids: Iterable[str]) -> dict[str, RunOwnership]: ...

    def get_scoped(self, *, run_id: str, organization_id: str) -> RunOwnership | None: ...

    def get_many_scoped(
        self,
        *,
        run_ids: Iterable[str],
        organization_id: str,
    ) -> dict[str, RunOwnership]: ...


class DuckDBRunAccessStore:
    """Persistent ownership index for product authorization.

    This remains the test/bounded baseline implementation. The product authorization layer
    consumes ``RunAccessStore`` so a production backend can provide DB-native tenant scoping
    without changing route semantics.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("DuckDBRunAccessStore requires a persistent path")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.path)

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS run_access_meta (
                    key VARCHAR PRIMARY KEY,
                    value VARCHAR NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS run_ownership (
                    run_id VARCHAR PRIMARY KEY,
                    organization_id VARCHAR NOT NULL,
                    user_id VARCHAR NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                INSERT OR REPLACE INTO run_access_meta(key, value)
                VALUES ('schema_version', ?)
                """,
                [RUN_ACCESS_SCHEMA_VERSION],
            )
        finally:
            connection.close()

    def ready(self) -> bool:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT value FROM run_access_meta WHERE key = 'schema_version'"
            ).fetchone()
            return bool(row and row[0] == RUN_ACCESS_SCHEMA_VERSION)
        finally:
            connection.close()

    def claim(self, *, run_id: str, organization_id: str, user_id: str) -> bool:
        """Atomically establish immutable ownership.

        Returns True for a new claim and False for an idempotent repeated claim. A
        conflicting claim fails closed instead of silently changing ownership.
        """

        if not run_id or not organization_id or not user_id:
            raise ValueError("run ownership fields must be non-empty")

        connection = self._connect()
        try:
            connection.execute("BEGIN TRANSACTION")
            existing = connection.execute(
                "SELECT organization_id, user_id FROM run_ownership WHERE run_id = ?",
                [run_id],
            ).fetchone()
            if existing is not None:
                if existing != (organization_id, user_id):
                    connection.execute("ROLLBACK")
                    raise RuntimeError("run_ownership_conflict")
                connection.execute("COMMIT")
                return False

            connection.execute(
                """
                INSERT INTO run_ownership(run_id, organization_id, user_id)
                VALUES (?, ?, ?)
                """,
                [run_id, organization_id, user_id],
            )
            connection.execute("COMMIT")
            return True
        except Exception:
            try:
                connection.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            connection.close()

    def get(self, run_id: str) -> RunOwnership | None:
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT run_id, organization_id, user_id
                FROM run_ownership
                WHERE run_id = ?
                """,
                [run_id],
            ).fetchone()
            if row is None:
                return None
            return RunOwnership(
                run_id=str(row[0]),
                organization_id=str(row[1]),
                user_id=str(row[2]),
            )
        finally:
            connection.close()

    def get_many(self, run_ids: Iterable[str]) -> dict[str, RunOwnership]:
        unique = tuple(dict.fromkeys(run_id for run_id in run_ids if run_id))
        if not unique:
            return {}
        if len(unique) > 1000:
            raise ValueError("get_many supports at most 1000 run ids")

        placeholders = ",".join("?" for _ in unique)
        connection = self._connect()
        try:
            rows = connection.execute(
                f"""
                SELECT run_id, organization_id, user_id
                FROM run_ownership
                WHERE run_id IN ({placeholders})
                """,
                list(unique),
            ).fetchall()
            return {
                str(row[0]): RunOwnership(
                    run_id=str(row[0]),
                    organization_id=str(row[1]),
                    user_id=str(row[2]),
                )
                for row in rows
            }
        finally:
            connection.close()

    def get_scoped(self, *, run_id: str, organization_id: str) -> RunOwnership | None:
        item = self.get(run_id)
        if item is None or item.organization_id != organization_id:
            return None
        return item

    def get_many_scoped(
        self,
        *,
        run_ids: Iterable[str],
        organization_id: str,
    ) -> dict[str, RunOwnership]:
        return {
            run_id: item
            for run_id, item in self.get_many(run_ids).items()
            if item.organization_id == organization_id
        }
