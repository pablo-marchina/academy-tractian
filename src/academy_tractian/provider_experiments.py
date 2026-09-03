from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProviderCandidateSummary(_FrozenModel):
    candidate_id: str
    attempts: int
    hard_gate_pass: bool
    hard_gate_failures: tuple[str, ...]
    structured_decision_adherence: float
    public_task_quality: float
    safe_failure_behavior: float
    trace_integrity: float
    success_rate: float
    signature_stability: float
    median_latency_ms: float
    p95_latency_ms: float
    observed_neurons: float
    cash_cost_usd: float
    usage_complete: bool


class ProviderDiagnosticSummary(_FrozenModel):
    client_failures: int
    client_failures_at_completion_cap: int
    completion_cap_tokens: int
    response_payload_invalid: int
    clean_public_rubric_passes: int
    interpretation: str


class ProviderExperimentSummary(_FrozenModel):
    experiment_id: Literal["D01", "D02"]
    status: Literal["COMPLETE", "NOT_EXECUTED"]
    selection: str | None
    production_selection_claim: bool
    attempted_calls: int
    expected_calls: int
    cash_cost_usd: float | None
    packet_observed_neurons: float | None
    packet_max_neurons: float
    completion_cap_tokens: int
    raw_provider_material_recorded: bool
    resource_accounting_complete: bool
    attempt_matrix_available: bool
    candidates: tuple[ProviderCandidateSummary, ...]
    diagnostic: ProviderDiagnosticSummary | None = None
    note: str


class ProviderExperimentRegistry(_FrozenModel):
    schema_version: Literal["safe-provider-experiments-v1"] = "safe-provider-experiments-v1"
    registry_sha256: str
    experiments: tuple[ProviderExperimentSummary, ...]


def _payload() -> tuple[ProviderExperimentSummary, ...]:
    d01 = ProviderExperimentSummary(
        experiment_id="D01",
        status="COMPLETE",
        selection="NO_SELECTION",
        production_selection_claim=False,
        attempted_calls=32,
        expected_calls=32,
        cash_cost_usd=0.0,
        packet_observed_neurons=2813.6284639999994,
        packet_max_neurons=7937.522688,
        completion_cap_tokens=512,
        raw_provider_material_recorded=False,
        resource_accounting_complete=True,
        attempt_matrix_available=False,
        candidates=(
            ProviderCandidateSummary(
                candidate_id="cloudflare_glm_4_7_flash_workers_free",
                attempts=16,
                hard_gate_pass=False,
                hard_gate_failures=("M1_BELOW_MINIMUM", "M4_BELOW_MINIMUM", "M7_BELOW_MINIMUM"),
                structured_decision_adherence=0.0,
                public_task_quality=0.0,
                safe_failure_behavior=1.0,
                trace_integrity=1.0,
                success_rate=0.0,
                signature_stability=0.0,
                median_latency_ms=8959.5,
                p95_latency_ms=27395.0,
                observed_neurons=450.3848,
                cash_cost_usd=0.0,
                usage_complete=True,
            ),
            ProviderCandidateSummary(
                candidate_id="cloudflare_nemotron_3_120b_a12b_workers_free",
                attempts=16,
                hard_gate_pass=False,
                hard_gate_failures=("M1_BELOW_MINIMUM", "M4_BELOW_MINIMUM", "M7_BELOW_MINIMUM"),
                structured_decision_adherence=0.4375,
                public_task_quality=0.375,
                safe_failure_behavior=1.0,
                trace_integrity=1.0,
                success_rate=0.4375,
                signature_stability=0.375,
                median_latency_ms=6214.0,
                p95_latency_ms=8857.0,
                observed_neurons=2363.243664,
                cash_cost_usd=0.0,
                usage_complete=True,
            ),
        ),
        diagnostic=ProviderDiagnosticSummary(
            client_failures=24,
            client_failures_at_completion_cap=24,
            completion_cap_tokens=512,
            response_payload_invalid=1,
            clean_public_rubric_passes=6,
            interpretation=(
                "D01 remains NO_SELECTION. The accepted post-run diagnostic is completion-budget-censored: "
                "24/24 sanitized CLIENT_FAILURE attempts reached the exact 512-token completion cap."
            ),
        ),
        note=(
            "Accepted aggregate live result only. Raw provider material was not recorded and this registry "
            "does not invent the unavailable 32-row attempt matrix."
        ),
    )
    d02 = ProviderExperimentSummary(
        experiment_id="D02",
        status="COMPLETE",
        selection="NO_SELECTION",
        production_selection_claim=False,
        attempted_calls=32,
        expected_calls=32,
        cash_cost_usd=0.0,
        packet_observed_neurons=3344.1308560000007,
        packet_max_neurons=9352.805376,
        completion_cap_tokens=1024,
        raw_provider_material_recorded=False,
        resource_accounting_complete=True,
        attempt_matrix_available=False,
        candidates=(
            ProviderCandidateSummary(
                candidate_id="cloudflare_glm_4_7_flash_workers_free",
                attempts=16,
                hard_gate_pass=False,
                hard_gate_failures=("M1_BELOW_MINIMUM", "M4_BELOW_MINIMUM", "M7_BELOW_MINIMUM"),
                structured_decision_adherence=0.4375,
                public_task_quality=0.375,
                safe_failure_behavior=1.0,
                trace_integrity=1.0,
                success_rate=0.4375,
                signature_stability=0.25,
                median_latency_ms=15329.0,
                p95_latency_ms=38270.0,
                observed_neurons=642.9772000000002,
                cash_cost_usd=0.0,
                usage_complete=True,
            ),
            ProviderCandidateSummary(
                candidate_id="cloudflare_nemotron_3_120b_a12b_workers_free",
                attempts=16,
                hard_gate_pass=False,
                hard_gate_failures=("M1_BELOW_MINIMUM", "M4_BELOW_MINIMUM", "M7_BELOW_MINIMUM"),
                structured_decision_adherence=0.5625,
                public_task_quality=0.5625,
                safe_failure_behavior=1.0,
                trace_integrity=1.0,
                success_rate=0.5625,
                signature_stability=0.5,
                median_latency_ms=4218.5,
                p95_latency_ms=9168.0,
                observed_neurons=2701.153656,
                cash_cost_usd=0.0,
                usage_complete=True,
            ),
        ),
        diagnostic=None,
        note=(
            "Accepted governed D02 aggregate live result from plan "
            "e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958. "
            "The one-shot packet completed 32/32 attempts at USD 0 with a 1024-token completion cap. "
            "Both candidates still failed M1/M4/M7 hard gates, so selection remains NO_SELECTION. "
            "Raw provider material was not recorded and this registry does not invent the unavailable "
            "32-row attempt matrix or failure-subtype distribution."
        ),
    )
    return (d01, d02)


def provider_experiment_registry() -> ProviderExperimentRegistry:
    experiments = _payload()
    canonical = json.dumps(
        [item.model_dump(mode="json") for item in experiments],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return ProviderExperimentRegistry(
        registry_sha256=sha256(canonical).hexdigest(),
        experiments=experiments,
    )
