from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

from .models import ResponseMode, ToolKind, ToolSpec, TraceEvent
from .transport import TransportResponse


READ_SEMANTICS_VERSION = "read-semantics-v1"

ReadSemanticsSource = Literal["structured_mode", "http_status", "fail_closed"]
ReadSemanticsIssueCode = Literal[
    "NON_OBJECT_BODY",
    "MISSING_MODE",
    "INVALID_MODE",
    "INVALID_TRACE_RESULT",
    "INVALID_STATUS_CODE",
    "STATUS_CODE_MISMATCH",
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
    ``inconclusive`` while retaining an issue code for acceptance evaluation.
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
class ReadSemanticsTraceEntry:
    sequence: int
    tool_name: str
    response_mode: ResponseMode
    source: ReadSemanticsSource
    status_code: int | None
    issue_code: ReadSemanticsIssueCode | None = None


@dataclass(frozen=True)
class ReadSemanticsTraceReport:
    """Trace-only acceptance report over existing immutable tool-result evidence."""

    schema_version: str
    read_result_count: int
    assessed_result_count: int
    contract_issue_count: int
    mode_counts: dict[str, int]
    entries: tuple[ReadSemanticsTraceEntry, ...]

    @property
    def passed(self) -> bool:
        return (
            self.read_result_count == self.assessed_result_count
            and self.contract_issue_count == 0
        )


def _fail_closed_trace_entry(
    *,
    event: TraceEvent,
    issue_code: ReadSemanticsIssueCode,
    status_code: int | None = None,
) -> ReadSemanticsTraceEntry:
    return ReadSemanticsTraceEntry(
        sequence=event.sequence,
        tool_name=event.tool_name or "<unknown>",
        response_mode=ResponseMode.INCONCLUSIVE,
        source="fail_closed",
        status_code=status_code,
        issue_code=issue_code,
    )


class ReadSemanticsTraceEvaluator:
    """Classify read outcomes from raw canonical trace evidence without mutating the trace.

    Read membership comes from the trusted ToolSpec registry. The evaluator reconstructs only
    the minimal transport response needed for semantic classification from ``tool_result.result``.
    Historical/frozen HarnessRunner traces therefore remain byte-for-byte reproducible.
    """

    def __init__(self, registry: Mapping[str, ToolSpec]) -> None:
        self.registry = dict(registry)

    def _assess_event(self, event: TraceEvent) -> ReadSemanticsTraceEntry:
        result = event.result
        if not isinstance(result, dict):
            return _fail_closed_trace_entry(
                event=event,
                issue_code="INVALID_TRACE_RESULT",
            )

        raw_status = result.get("status_code")
        if isinstance(raw_status, bool) or not isinstance(raw_status, int):
            return _fail_closed_trace_entry(
                event=event,
                issue_code="INVALID_STATUS_CODE",
            )

        metadata_status = event.metadata.get("status_code")
        if (
            metadata_status is not None
            and (
                isinstance(metadata_status, bool)
                or not isinstance(metadata_status, int)
                or metadata_status != raw_status
            )
        ):
            return _fail_closed_trace_entry(
                event=event,
                issue_code="STATUS_CODE_MISMATCH",
                status_code=raw_status,
            )

        tool = self.registry[event.tool_name or ""]
        assessment = classify_read_response(
            tool=tool,
            response=TransportResponse(
                status_code=raw_status,
                headers={},
                body=result.get("body"),
            ),
        )
        return ReadSemanticsTraceEntry(
            sequence=event.sequence,
            tool_name=event.tool_name or "<unknown>",
            response_mode=assessment.response_mode,
            source=assessment.source,
            status_code=raw_status,
            issue_code=assessment.issue_code,
        )

    def evaluate(self, trace: list[TraceEvent]) -> ReadSemanticsTraceReport:
        read_results = [
            event
            for event in trace
            if event.event_type == "tool_result"
            and event.tool_name in self.registry
            and self.registry[event.tool_name].kind is ToolKind.READ
        ]
        entries = tuple(self._assess_event(event) for event in read_results)
        mode_counts = {mode.value: 0 for mode in ResponseMode}
        for entry in entries:
            mode_counts[entry.response_mode.value] += 1
        return ReadSemanticsTraceReport(
            schema_version=READ_SEMANTICS_VERSION,
            read_result_count=len(read_results),
            assessed_result_count=len(entries),
            contract_issue_count=sum(entry.issue_code is not None for entry in entries),
            mode_counts=mode_counts,
            entries=entries,
        )
