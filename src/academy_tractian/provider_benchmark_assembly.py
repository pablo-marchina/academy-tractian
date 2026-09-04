from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .eval_driven import (
    EvalMetricBundle,
    EvalMetricRule,
    compare_eval_bundles,
)
from .provider_human_calibration import ProviderHumanCalibrationProtocol
from .provider_promotion import (
    ProviderBenchmarkEvidence,
    ProviderCandidateEvidence,
    ProviderHumanCalibrationEvidence,
)
from .runtime import (
    ProductionRuntimeConfig,
    RuntimeConfigurationIdentity,
    canonical_tool_registry,
    production_runtime_config_hash,
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def eval_rule_set_sha256(rules: Sequence[EvalMetricRule]) -> str:
    if not rules:
        raise ValueError("provider_benchmark_requires_rules")
    return _canonical_sha256([rule.model_dump(mode="json") for rule in rules])


class ProviderCandidateBenchmarkInput(_StrictModel):
    """One runtime-bound candidate bundle before pairwise EDD comparison."""

    identity: RuntimeConfigurationIdentity
    bundle: EvalMetricBundle
    human_calibration: ProviderHumanCalibrationEvidence | None = None

    @model_validator(mode="after")
    def validate_candidate_identity(self) -> "ProviderCandidateBenchmarkInput":
        if self.bundle.config_id != self.identity.candidate_id:
            raise ValueError("provider_benchmark_bundle_candidate_id_mismatch")
        if self.human_calibration is not None:
            if self.human_calibration.candidate_id != self.identity.candidate_id:
                raise ValueError("provider_benchmark_human_candidate_id_mismatch")
        return self


class ProviderBenchmarkAssembly(_StrictModel):
    """Safe summary of one assembled benchmark; raw model outputs are deliberately absent."""

    evidence: ProviderBenchmarkEvidence
    runtime_config_hashes: dict[str, str]
    rule_set_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


def _bundle_maturity(bundle: EvalMetricBundle) -> tuple[int, int]:
    counts = Counter(record.group_id for record in bundle.records)
    if not counts:
        raise ValueError("provider_benchmark_bundle_has_no_groups")
    return len(counts), min(counts.values())


def _declared_runtime_hash(bundle: EvalMetricBundle) -> str:
    value = bundle.metadata.get("runtime_config_hash")
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("provider_benchmark_bundle_runtime_config_hash_missing")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("provider_benchmark_bundle_runtime_config_hash_invalid") from exc
    return value


def assemble_provider_benchmark_evidence(
    *,
    candidates: Sequence[ProviderCandidateBenchmarkInput],
    runtime_config: ProductionRuntimeConfig,
    rules: Sequence[EvalMetricRule],
    corpus_id: str,
    corpus_hash: str,
    evaluator_version: str,
    rule_set_id: str,
    code_sha: str,
    human_calibration_protocol: ProviderHumanCalibrationProtocol,
    generated_at: datetime,
    bootstrap_samples: int = 4000,
) -> ProviderBenchmarkAssembly:
    """Build the promotion envelope from runtime-bound, paired candidate bundles.

    Candidate/provider identity is code-owned and the expected runtime config hash is recomputed
    from the canonical 18-tool contract plus the exact candidate identity. The bundle must carry
    that same safe hash in metadata; a model name or deployment setting alone is never enough to
    associate results with a candidate. Scenario/repeat maturity is derived from records rather
    than caller-supplied counts. Pairwise EDD reports are generated in both directions for every
    candidate pair so the promotion gate never accepts an incomplete comparison matrix.
    """

    if len(candidates) < 2:
        raise ValueError("provider_benchmark_requires_at_least_two_candidates")
    if len({candidate.identity.candidate_id for candidate in candidates}) != len(candidates):
        raise ValueError("provider_benchmark_duplicate_candidate")

    registry = canonical_tool_registry()
    runtime_hashes: dict[str, str] = {}
    provider_candidates: list[ProviderCandidateEvidence] = []
    bundles: dict[str, EvalMetricBundle] = {}

    for candidate in candidates:
        candidate_id = candidate.identity.candidate_id
        expected_hash = production_runtime_config_hash(
            runtime_config,
            registry,
            candidate.identity,
        )
        declared_hash = _declared_runtime_hash(candidate.bundle)
        if declared_hash != expected_hash:
            raise ValueError("provider_benchmark_runtime_config_hash_mismatch")
        if candidate.human_calibration is not None:
            if candidate.human_calibration.config_hash != expected_hash:
                raise ValueError("provider_benchmark_human_config_hash_mismatch")
            if candidate.human_calibration.protocol_id != human_calibration_protocol.protocol_id:
                raise ValueError("provider_benchmark_human_protocol_id_mismatch")
            if candidate.human_calibration.protocol_hash != human_calibration_protocol.protocol_sha256:
                raise ValueError("provider_benchmark_human_protocol_hash_mismatch")

        scenario_count, repeat_count = _bundle_maturity(candidate.bundle)
        provider_candidates.append(
            ProviderCandidateEvidence(
                candidate_id=candidate_id,
                provider_id=candidate.identity.provider_id,
                model_id=candidate.identity.model_id,
                config_hash=expected_hash,
                scenario_count=scenario_count,
                repeat_count=repeat_count,
                human_calibration=candidate.human_calibration,
            )
        )
        runtime_hashes[candidate_id] = expected_hash
        bundles[candidate_id] = candidate.bundle

    reports = []
    ordered_ids = tuple(candidate.identity.candidate_id for candidate in candidates)
    for baseline_id in ordered_ids:
        for candidate_id in ordered_ids:
            if baseline_id == candidate_id:
                continue
            reports.append(
                compare_eval_bundles(
                    bundles[baseline_id],
                    bundles[candidate_id],
                    rules=rules,
                    bootstrap_samples=bootstrap_samples,
                )
            )

    rule_hash = eval_rule_set_sha256(rules)
    evidence = ProviderBenchmarkEvidence(
        corpus_id=corpus_id,
        corpus_hash=corpus_hash,
        evaluator_version=evaluator_version,
        rule_set_id=rule_set_id,
        rule_set_hash=rule_hash,
        human_calibration_protocol_id=human_calibration_protocol.protocol_id,
        human_calibration_protocol_hash=human_calibration_protocol.protocol_sha256,
        code_sha=code_sha,
        generated_at=generated_at,
        candidates=tuple(provider_candidates),
        pairwise_reports=tuple(reports),
    )
    return ProviderBenchmarkAssembly(
        evidence=evidence,
        runtime_config_hashes=runtime_hashes,
        rule_set_hash=rule_hash,
    )
