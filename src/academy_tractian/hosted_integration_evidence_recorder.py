from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from threading import Lock
from uuid import uuid4

from research.e2.models import BoundRequest
from research.e2.tool_registry import TOOLS
from research.e2.transport import RequestTransport, TransportResponse

from .tractian_integration_evidence import (
    IntegrationEvidenceLedger,
    OperationEvidence,
)


def _compile_path_template(template: str) -> re.Pattern[str]:
    parts = re.split(r"(\{[^{}]+\})", template)
    pattern = "".join(r"[^/]+" if part.startswith("{") else re.escape(part) for part in parts)
    return re.compile(rf"^{pattern}$")


_CANONICAL_ROUTES = tuple(
    (tool, _compile_path_template(tool.path_template))
    for tool in TOOLS
)


def _resolve_canonical_tool(request: BoundRequest):
    matches = [
        tool
        for tool, pattern in _CANONICAL_ROUTES
        if request.method.upper() == tool.method and pattern.fullmatch(request.path)
    ]
    return matches[0] if len(matches) == 1 else None


class HostedIntegrationEvidenceRecorder:
    """Thread-safe, bounded, safe live-evidence accumulator.

    Only canonical operation metadata is retained. Request arguments, query values,
    headers, bodies and response bodies are intentionally never stored. Records are
    coalesced by operation/outcome, so multi-user traffic cannot grow memory without
    bound. The accumulator is process-local live telemetry, not persistent proof.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._records: dict[tuple[str, str], OperationEvidence] = {}
        self._invalid = False
        self._validation_errors: set[str] = set()

    def _mark_invalid(self, reason: str) -> None:
        with self._lock:
            self._invalid = True
            self._validation_errors.add(reason)

    def record(
        self,
        request: BoundRequest,
        *,
        outcome: str,
        http_status: int | None = None,
    ) -> None:
        tool = _resolve_canonical_tool(request)
        if tool is None:
            self._mark_invalid("runtime:canonical_route_resolution_failed")
            return

        observed_at = datetime.now(timezone.utc)
        probe_id = f"runtime-{uuid4().hex}"
        safe_fingerprint_input = json.dumps(
            {
                "operation": tool.name,
                "method": tool.method,
                "path_template": tool.path_template,
                "outcome": outcome,
                "http_status": http_status,
                "observed_at": observed_at.isoformat(),
                "probe_id": probe_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = "sha256:" + sha256(safe_fingerprint_input.encode("utf-8")).hexdigest()
        try:
            evidence = OperationEvidence(
                operation=tool.name,
                environment="hosted_live",
                outcome=outcome,
                method=tool.method,
                path_template=tool.path_template,
                observed_at=observed_at,
                probe_id=probe_id,
                evidence_ref="hosted-runtime-transport-observation",
                fingerprint=fingerprint,
                http_status=http_status,
            )
        except Exception:
            self._mark_invalid("runtime:evidence_record_validation_failed")
            return

        with self._lock:
            self._records[(tool.name, evidence.outcome)] = evidence

    def ledger(self) -> IntegrationEvidenceLedger:
        with self._lock:
            if self._invalid:
                return IntegrationEvidenceLedger(
                    source_label="hosted_live:runtime_transport",
                    state="INVALID",
                    validation_errors=tuple(sorted(self._validation_errors)),
                )
            records = tuple(
                self._records[key]
                for key in sorted(self._records)
            )
        return IntegrationEvidenceLedger(
            source_label="hosted_live:runtime_transport",
            state="VALID",
            records=records,
        )


class EvidenceRecordingTractianTransport:
    """RequestTransport decorator that records only safe canonical route evidence."""

    def __init__(
        self,
        delegate: RequestTransport,
        recorder: HostedIntegrationEvidenceRecorder,
    ) -> None:
        self._delegate = delegate
        self._recorder = recorder

    def request(self, request: BoundRequest) -> TransportResponse:
        try:
            response = self._delegate.request(request)
        except Exception:
            self._recorder.record(request, outcome="transport_failure")
            raise

        if 200 <= response.status_code < 400:
            self._recorder.record(
                request,
                outcome="success",
                http_status=response.status_code,
            )
        elif 400 <= response.status_code <= 599:
            self._recorder.record(
                request,
                outcome="http_error_observed",
                http_status=response.status_code,
            )
        else:
            self._recorder._mark_invalid("runtime:invalid_http_status")
        return response
