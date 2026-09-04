from __future__ import annotations

from typing import Any, Protocol

from research.e2.models import RunTrace

from .evaluation import ProductionEvaluationReport
from .observability import SafeEvaluation, SafeEvidenceRef, SafeEvent, SafeRun


class ObservabilityStoreBackend(Protocol):
    """Backend-neutral persistence contract for browser-safe observability projections.

    Implementations may use DuckDB for isolated tests/baselines or managed PostgreSQL for the
    hosted product. Only allow-listed safe projections cross this boundary.
    """

    def ready(self) -> bool: ...

    def persist_trace(
        self,
        trace: RunTrace,
        *,
        evaluation: ProductionEvaluationReport | None = None,
    ) -> str: ...

    def persist_projection(
        self,
        run: SafeRun,
        events: tuple[SafeEvent, ...],
        evidence: tuple[SafeEvidenceRef, ...],
        *,
        evaluation: SafeEvaluation | None = None,
    ) -> str: ...

    def persist_live_update(
        self,
        *,
        run: SafeRun,
        event: SafeEvent,
        evidence: SafeEvidenceRef | None = None,
    ) -> bool: ...

    def overview(self) -> dict[str, Any]: ...

    def list_runs(self, *, limit: int = 100) -> list[dict[str, Any]]: ...

    def get_run(self, run_id: str) -> dict[str, Any] | None: ...

    def get_events(self, run_id: str) -> list[dict[str, Any]]: ...

    def get_events_after(
        self,
        run_id: str,
        *,
        after_sequence: int = -1,
        limit: int = 1000,
    ) -> list[dict[str, Any]]: ...

    def get_evidence(self, run_id: str) -> list[dict[str, Any]]: ...

    def get_evaluation(self, run_id: str) -> list[dict[str, Any]]: ...
