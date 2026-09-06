from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

from .models import ResponseMode, ToolKind, ToolSpec, TraceEvent
from .transport import TransportResponse


READ_SEMANTICS_VERSION = "read-semantics-v1"

ReadSemanticsSource = Literal["structured_mode", "http_status", "fail_closed"]
ReadSemanticsIssueCode = Literal[
    "NON_OBJECT_BODY",
    "MISSING_MODE",
    "INVALID_MODE",
]


@dataclass(frozen=True)
class ReadSemanticsAssessment:
    """Deterministic epistemic classification for one executed read response.

    The supplied TRACTIAN API exposes the semantic response state through the structured
    response-body field ``mode``. This classifier deliberately does not inspect prose, error
    messages, data values, or model output. A successful HTTP status without a valid structured
    mode is therefore inconclusive rather than implicitly complete.
    """

    response_mode: ResponseMode
    source: ReadSemanticsSource
    issue_code: ReadSemanticsIssueCode | None = None

    def trace_metadata(self) -> dict[str, str]:
        metadata = {
            "read_semantics_version": READ_SEMANTICS_VERSION,
            "response_mode": self.response_mode.value,
            "response_mode_source": self.source,
        }
        if self.issue_code is not None:
            metadata["response_mode_issue_code"] = self.issue_code
        return metadata


def classify_read_response(
    *,
    tool: ToolSpec,
    response: TransportResponse,
) -> ReadSemanticsAssessment:
    """Classify one read response without textual heuristics or inferred business meaning.

    Non-read tools are rejected to prevent action acknowledgements from being interpreted as
    epistemic read states. Non-2xx HTTP responses deterministically mean ``unavailable`` even if
    a body happens to claim otherwise. For 2xx reads, only an exact structured ``mode`` value
    from :class:`ResponseMode` is accepted. Missing or malformed structured state fails closed to
    ``inconclusive`` while retaining an issue code in the trace.
    """

    if tool.kind is not ToolKind.READ:
        raise ValueError("read semantics classification only accepts read tools")

    if not 200 <= response.status_code < 300:
        return ReadSemanticsAssessment(
            response_mode=ResponseMode.UNAVAILABLE,
            source="http_status",
        )

    if not isinstance(response.body, dict):
        return ReadSemanticsAssessment(
            response_mode=ResponseMode.INCONCLUSIVE,
            source="fail_closed",
            issue_code="NON_OBJECT_BODY",
        )

    if "mode" not in response.body:
        return ReadSemanticsAssessment(
            response_mode=ResponseMode.INCONCLUSIVE,
            source="fail_closed",
            issue_code="MISSING_MODE",
        )

    raw_mode = response.body["mode"]
    if not isinstance(raw_mode, str):
        return ReadSemanticsAssessment(
            response_mode=ResponseMode.INCONCLUSIVE,
            source="fail_closed",
            issue_code="INVALID_MODE",
        )

    try:
        mode = ResponseMode(raw_mode)
    except ValueError:
        return ReadSemanticsAssessment(
            response_mode=ResponseMode.INCONCLUSIVE,
            source="fail_closed",
            issue_code="INVALID_MODE",
        )

    return ReadSemanticsAssessment(
        response_mode=mode,
        source="structured_mode",
    )


@dataclass(frozen=True)
class ReadSemanticsTraceReport:
    """Trace-only evaluator output for deterministic read-semantics instrumentation."""

    read_result_count: int
    covered_result_count: int
    contract_issue_count: int
    mode_counts: dict[str, int]

    @property
    def passed(self) -> bool:
        return self.read_result_count == self.covered_result_count


class ReadSemanticsTraceEvaluator:
    """Evaluate semantic-state trace coverage from the canonical tool registry.

    Read membership is derived from trusted registry metadata instead of self-reported trace
    metadata. This makes pre-instrumentation or tampered read results visible as missing semantic
    coverage instead of allowing them to disappear from the evaluator denominator.
    """

    def __init__(self, registry: Mapping[str, ToolSpec]) -> None:
        self.registry = dict(registry)

    def evaluate(self, trace: list[TraceEvent]) -> ReadSemanticsTraceReport:
        read_results = [
            event
            for event in trace
            if event.event_type == "tool_result"
            and event.tool_name in self.registry
            and self.registry[event.tool_name].kind is ToolKind.READ
        ]
        covered = [
            event
            for event in read_results
            if event.metadata.get("kind") == "read"
            and event.metadata.get("read_semantics_version") == READ_SEMANTICS_VERSION
            and event.metadata.get("response_mode") in {mode.value for mode in ResponseMode}
            and event.metadata.get("response_mode_source")
            in {"structured_mode", "http_status", "fail_closed"}
        ]
        mode_counts = {mode.value: 0 for mode in ResponseMode}
        for event in covered:
            mode_counts[str(event.metadata["response_mode"])] += 1
        issues = [
            event
            for event in covered
            if event.metadata.get("response_mode_issue_code") is not None
        ]
        return ReadSemanticsTraceReport(
            read_result_count=len(read_results),
            covered_result_count=len(covered),
            contract_issue_count=len(issues),
            mode_counts=mode_counts,
        )
