from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from research.e2.tool_registry import TOOLS


CAMPAIGN_EVIDENCE_SCHEMA_VERSION = "tractian-campaign-evidence-v1"
CampaignProofDimension = Literal[
    "invalid_parameters_rejected",
    "response_normalization_verified",
    "agent_evaluator_behavior_verified",
]
CampaignEvidenceState = Literal["VALID", "INVALID", "MISSING"]


class CampaignProofRecord(BaseModel):
    """Bounded evidence reference for one semantic integration requirement.

    Raw requests, raw TRACTIAN responses, prompts, provider outputs, tokens and
    evaluator-private truth are intentionally not part of this schema.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    operation: str = Field(min_length=1, max_length=96)
    dimension: CampaignProofDimension
    environment: Literal["hosted_live"] = "hosted_live"
    passed: bool
    observed_at: datetime
    probe_id: str = Field(min_length=1, max_length=128)
    evidence_ref: str = Field(min_length=1, max_length=256)
    fingerprint: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_timestamp(self) -> "CampaignProofRecord":
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at_must_be_timezone_aware")
        return self


class CampaignEvidenceDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["tractian-campaign-evidence-v1"]
    records: tuple[CampaignProofRecord, ...] = ()


@dataclass(frozen=True)
class CampaignEvidenceLedger:
    source_label: str
    state: CampaignEvidenceState
    records: tuple[CampaignProofRecord, ...] = ()
    validation_errors: tuple[str, ...] = ()

    @property
    def valid(self) -> bool:
        return self.state == "VALID"

    def records_for(
        self,
        operation: str,
        dimension: CampaignProofDimension,
    ) -> tuple[CampaignProofRecord, ...]:
        if not self.valid:
            return ()
        return tuple(
            record
            for record in self.records
            if record.operation == operation and record.dimension == dimension
        )


def _schema_error_codes(exc: ValidationError) -> tuple[str, ...]:
    codes = sorted({str(item.get("type", "validation_error")) for item in exc.errors()})
    return tuple(f"schema:{code}" for code in codes) or ("schema:validation_error",)


def parse_campaign_evidence_document(
    payload: Mapping[str, Any],
    *,
    source_label: str,
) -> CampaignEvidenceLedger:
    """Validate a semantic campaign evidence document as one atomic trust unit."""

    try:
        document = CampaignEvidenceDocument.model_validate(payload)
    except ValidationError as exc:
        return CampaignEvidenceLedger(
            source_label=source_label,
            state="INVALID",
            validation_errors=_schema_error_codes(exc),
        )

    known_operations = {tool.name for tool in TOOLS}
    if any(record.operation not in known_operations for record in document.records):
        return CampaignEvidenceLedger(
            source_label=source_label,
            state="INVALID",
            validation_errors=("contract:unknown_operation",),
        )

    return CampaignEvidenceLedger(
        source_label=source_label,
        state="VALID",
        records=document.records,
    )


def empty_campaign_evidence() -> CampaignEvidenceLedger:
    return CampaignEvidenceLedger(source_label="hosted_live:campaign_not_supplied", state="VALID")
