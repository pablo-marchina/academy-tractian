from __future__ import annotations

from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field

from research.e2.models import RunTrace, ToolSpec
from research.e2.read_semantics import ReadSemanticsTraceEvaluator

from .runtime import canonical_tool_registry


PRODUCTION_READ_SEMANTICS_GATE_VERSION = "production-read-semantics-gate-v1"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProductionReadSemanticsEntry(_FrozenModel):
    sequence: int = Field(ge=0)
    tool_name: str = Field(min_length=1)
    response_mode: Literal[
        "complete",
        "partial",
        "inconclusive",
        "conflict",
        "unavailable",
    ]
    source: Literal["structured_mode", "http_status", "fail_closed"]
    status_code: int | None = None
    issue_code: str | None = None


class ProductionReadSemanticsReport(_FrozenModel):
    """Sanitized source-gate report; raw API response bodies are deliberately excluded."""

    schema_version: Literal["production-read-semantics-gate-v1"] = (
        PRODUCTION_READ_SEMANTICS_GATE_VERSION
    )
    run_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    passed: bool
    read_result_count: int = Field(ge=0)
    assessed_result_count: int = Field(ge=0)
    contract_issue_count: int = Field(ge=0)
    mode_counts: dict[str, int]
    entries: tuple[ProductionReadSemanticsEntry, ...]
    raw_response_recorded: Literal[False] = False
    trace_mutated: Literal[False] = False


class ProductionReadSemanticsGateError(RuntimeError):
    def __init__(self, report: ProductionReadSemanticsReport) -> None:
        super().__init__(
            "production read-semantics gate failed: "
            f"reads={report.read_result_count} "
            f"assessed={report.assessed_result_count} "
            f"contract_issues={report.contract_issue_count}"
        )
        self.report = report


class ProductionReadSemanticsGate:
    """Evaluate raw production RunTrace read results without changing frozen runtime semantics.

    This gate is intentionally separate from the frozen ProductionEvaluator/HarnessRunner
    foundation. It consumes the same canonical trace after execution, exposes only sanitized
    outcome/provenance fields, and can be promoted independently without rewriting historical
    EV-* evidence.
    """

    def __init__(self, *, registry: Mapping[str, ToolSpec] | None = None) -> None:
        self.registry = dict(registry or canonical_tool_registry())
        self._evaluator = ReadSemanticsTraceEvaluator(self.registry)

    def evaluate(self, trace: RunTrace) -> ProductionReadSemanticsReport:
        result = self._evaluator.evaluate(list(trace.events))
        entries = tuple(
            ProductionReadSemanticsEntry(
                sequence=entry.sequence,
                tool_name=entry.tool_name,
                response_mode=entry.response_mode.value,
                source=entry.source,
                status_code=entry.status_code,
                issue_code=entry.issue_code,
            )
            for entry in result.entries
        )
        return ProductionReadSemanticsReport(
            run_id=trace.run_id,
            scenario_id=trace.scenario_id,
            passed=result.passed,
            read_result_count=result.read_result_count,
            assessed_result_count=result.assessed_result_count,
            contract_issue_count=result.contract_issue_count,
            mode_counts=dict(result.mode_counts),
            entries=entries,
        )

    def require(self, trace: RunTrace) -> ProductionReadSemanticsReport:
        report = self.evaluate(trace)
        if not report.passed:
            raise ProductionReadSemanticsGateError(report)
        return report
