from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from importlib import resources
import json
from pathlib import Path
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from research.e2.tool_registry import TOOLS


INTEGRATION_EVIDENCE_SCHEMA_VERSION = "tractian-integration-evidence-v1"
FROZEN_EVIDENCE_RESOURCE = "frozen_tool_integration_evidence.json"

EvidenceEnvironment = Literal["frozen", "hosted_live"]
EvidenceOutcome = Literal[
    "success",
    "http_error_observed",
    "transport_failure",
    "unavailable",
    "blocked_by_safety",
]
EvidenceState = Literal["VALID", "INVALID", "MISSING"]

_ROUTE_OBSERVED_OUTCOMES = frozenset({"success", "http_error_observed"})


class OperationEvidence(BaseModel):
    """Safe, bounded evidence that one canonical TRACTIAN operation was observed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    operation: str = Field(min_length=1, max_length=96)
    environment: EvidenceEnvironment
    outcome: EvidenceOutcome
    method: str = Field(min_length=3, max_length=8)
    path_template: str = Field(min_length=1, max_length=256)
    observed_at: datetime
    probe_id: str = Field(min_length=1, max_length=128)
    evidence_ref: str = Field(min_length=1, max_length=256)
    fingerprint: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    http_status: int | None = Field(default=None, ge=100, le=599)

    @model_validator(mode="after")
    def validate_observation_semantics(self) -> "OperationEvidence":
        if self.method != self.method.upper():
            raise ValueError("method_must_be_uppercase")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at_must_be_timezone_aware")
        if self.outcome == "http_error_observed":
            if self.http_status is None or self.http_status < 400:
                raise ValueError("http_error_requires_error_status")
        elif self.outcome in {"transport_failure", "unavailable", "blocked_by_safety"}:
            if self.http_status is not None:
                raise ValueError("non_http_observation_must_not_have_status")
        elif self.outcome == "success" and self.http_status is not None:
            if not 200 <= self.http_status < 400:
                raise ValueError("success_status_must_be_non_error")
        return self


class IntegrationEvidenceDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["tractian-integration-evidence-v1"]
    records: tuple[OperationEvidence, ...] = ()


@dataclass(frozen=True)
class IntegrationEvidenceLedger:
    source_label: str
    state: EvidenceState
    records: tuple[OperationEvidence, ...] = ()
    validation_errors: tuple[str, ...] = ()

    @property
    def valid(self) -> bool:
        return self.state == "VALID"

    def records_for(self, operation: str, environment: EvidenceEnvironment) -> tuple[OperationEvidence, ...]:
        if not self.valid:
            return ()
        return tuple(
            item
            for item in self.records
            if item.operation == operation and item.environment == environment
        )

    def unique_route_observed_operations(self, environment: EvidenceEnvironment) -> frozenset[str]:
        if not self.valid:
            return frozenset()
        return frozenset(
            item.operation
            for item in self.records
            if item.environment == environment and item.outcome in _ROUTE_OBSERVED_OUTCOMES
        )

    def unique_success_operations(self, environment: EvidenceEnvironment) -> frozenset[str]:
        if not self.valid:
            return frozenset()
        return frozenset(
            item.operation
            for item in self.records
            if item.environment == environment and item.outcome == "success"
        )

    def unique_outcome_operations(
        self,
        environment: EvidenceEnvironment,
        outcome: EvidenceOutcome,
    ) -> frozenset[str]:
        if not self.valid:
            return frozenset()
        return frozenset(
            item.operation
            for item in self.records
            if item.environment == environment and item.outcome == outcome
        )


_TOOL_BY_NAME = {tool.name: tool for tool in TOOLS}


def _schema_error_codes(exc: ValidationError) -> tuple[str, ...]:
    # Expose only bounded validator error types. Never echo input values, URLs,
    # response bodies, tokens, DSNs, or other attacker-controlled evidence data.
    codes = sorted({str(item.get("type", "validation_error")) for item in exc.errors()})
    return tuple(f"schema:{code}" for code in codes) or ("schema:validation_error",)


def parse_integration_evidence_document(
    payload: Mapping[str, Any],
    *,
    source_label: str,
    expected_environment: EvidenceEnvironment | None = None,
) -> IntegrationEvidenceLedger:
    """Validate an evidence document as one atomic trust unit.

    Any schema or contract mismatch invalidates the whole document and returns
    zero trusted records. This deliberately fails closed so malformed evidence
    can never increase an integration-coverage claim.
    """

    try:
        document = IntegrationEvidenceDocument.model_validate(payload)
    except ValidationError as exc:
        return IntegrationEvidenceLedger(
            source_label=source_label,
            state="INVALID",
            validation_errors=_schema_error_codes(exc),
        )

    errors: list[str] = []
    for item in document.records:
        tool = _TOOL_BY_NAME.get(item.operation)
        if tool is None:
            errors.append("contract:unknown_operation")
            continue
        if item.method != tool.method or item.path_template != tool.path_template:
            errors.append("contract:route_mismatch")
        if expected_environment is not None and item.environment != expected_environment:
            errors.append("contract:environment_mismatch")

    if errors:
        return IntegrationEvidenceLedger(
            source_label=source_label,
            state="INVALID",
            validation_errors=tuple(sorted(set(errors))),
        )

    return IntegrationEvidenceLedger(
        source_label=source_label,
        state="VALID",
        records=document.records,
    )


def empty_hosted_integration_evidence() -> IntegrationEvidenceLedger:
    """Trusted empty hosted ledger: no live claim until explicit evidence exists."""

    return IntegrationEvidenceLedger(source_label="hosted_live:not_supplied", state="VALID")


def load_integration_evidence_path(
    path: str | Path,
    *,
    expected_environment: EvidenceEnvironment,
) -> IntegrationEvidenceLedger:
    """Load a bounded experiment artifact without making it a runtime dependency."""

    source_label = f"artifact:{Path(path).name}"
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return IntegrationEvidenceLedger(
            source_label=source_label,
            state="MISSING",
            validation_errors=("artifact:missing",),
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        return IntegrationEvidenceLedger(
            source_label=source_label,
            state="INVALID",
            validation_errors=("artifact:unreadable_or_invalid_json",),
        )
    if not isinstance(payload, Mapping):
        return IntegrationEvidenceLedger(
            source_label=source_label,
            state="INVALID",
            validation_errors=("schema:document_not_object",),
        )
    return parse_integration_evidence_document(
        payload,
        source_label=source_label,
        expected_environment=expected_environment,
    )


@lru_cache(maxsize=1)
def load_frozen_integration_evidence() -> IntegrationEvidenceLedger:
    """Load the packaged historical conformance evidence, failing closed."""

    source_label = f"package:research.e2/{FROZEN_EVIDENCE_RESOURCE}"
    try:
        raw = resources.files("research.e2").joinpath(FROZEN_EVIDENCE_RESOURCE).read_text(
            encoding="utf-8"
        )
        payload = json.loads(raw)
    except (FileNotFoundError, ModuleNotFoundError, OSError, UnicodeError, json.JSONDecodeError):
        return IntegrationEvidenceLedger(
            source_label=source_label,
            state="INVALID",
            validation_errors=("package:frozen_evidence_unavailable",),
        )
    if not isinstance(payload, Mapping):
        return IntegrationEvidenceLedger(
            source_label=source_label,
            state="INVALID",
            validation_errors=("schema:document_not_object",),
        )
    return parse_integration_evidence_document(
        payload,
        source_label=source_label,
        expected_environment="frozen",
    )
