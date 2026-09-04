from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from hashlib import sha256
import json
from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .eval_driven import (
    EvalMetricBundle,
    EvalMetricRule,
    EvalScenarioRecord,
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


class ProviderBenchmarkObservation(_StrictModel):
    """One evaluated candidate/scenario/repeat observation with explicit independence unit."""

    group_id: str = Field(min_length=1, max_length=128)
    scenario_id: str = Field(min_length=1, max_length=128)
    repeat_index: int = Field(ge=1, le=1000)
    response_mode: str | None = Field(default=None, min_length=1, max_length=64)
    metrics: dict[str, float] = Field(default_factory=dict)
    hard_gate_failures: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_metrics(self) -> "ProviderBenchmarkObservation":
        if any(not key.strip() for key in self.metrics):
            raise ValueError("provider_benchmark_metric_name_blank")
        if len(set(self.hard_gate_failures)) != len(self.hard_gate_failures):
            raise ValueError("provider_benchmark_duplicate_hard_gate_failure")
        return self

    @property
    def case_id(self) -> str:
        return f"{self.scenario_id}::repeat-{self.repeat_index}"


class ProviderCandidateBenchmarkInput(_StrictModel):
    """One runtime-bound candidate before pairwise EDD comparison."""

    identity: RuntimeConfigurationIdentity
    runtime_config_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    observations: tuple[ProviderBenchmarkObservation, ...] = Field(min_length=1)
    human_calibration: ProviderHumanCalibrationEvidence | None = None

    @model_validator(mode="after")
    def validate_candidate_observations(self) -> "ProviderCandidateBenchmarkInput":
        keys = [(item.scenario_id, item.repeat_index) for item in self.observations]
        if len(keys) != len(set(keys)):
            raise ValueError("provider_benchmark_duplicate_scenario_repeat")

        groups_by_scenario: dict[str, set[str]] = defaultdict(set)
        for item in self.observations:
            groups_by_scenario[item.scenario_id].add(item.group_id)
        if any(len(groups) != 1 for groups in groups_by_scenario.values()):
            raise ValueError("provider_benchmark_scenario_crosses_independent_groups")

        if self.human_calibration is not None:
            if self.human_calibration.candidate_id != self.identity.candidate_id:
                raise ValueError("provider_benchmark_human_candidate_id_mismatch")
        return self

    def eval_bundle(self) -> EvalMetricBundle:
        return EvalMetricBundle(
            config_id=self.identity.candidate_id,
            records=tuple(
                EvalScenarioRecord(
                    group_id=item.group_id,
                    case_id=item.case_id,
                    response_mode=item.response_mode,
                    metrics=dict(item.metrics),
                    hard_gate_failures=item.hard_gate_failures,
                )
                for item in self.observations
            ),
            metadata={
                "runtime_config_hash": self.runtime_config_hash,
                "candidate_id": self.identity.candidate_id,
                "scenario_count": len({item.scenario_id for item in self.observations}),
                "independent_group_count": len({item.group_id for item in self.observations}),
            },
        )


class ProviderBenchmarkAssembly(_StrictModel):
    """Safe summary of one assembled benchmark; raw model outputs are deliberately absent."""

    evidence: ProviderBenchmarkEvidence
    runtime_config_hashes: dict[str, str]
    independent_group_counts: dict[str, int]
    rule_set_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


def _observation_maturity(
    observations: Sequence[ProviderBenchmarkObservation],
) -> tuple[int, int, int]:
    scenarios = {item.scenario_id for item in observations}
    groups = {item.group_id for item in observations}
    repeats_by_scenario = Counter(item.scenario_id for item in observations)
    if not scenarios or not groups:
        raise ValueError("provider_benchmark_observations_empty")
    return len(scenarios), min(repeats_by_scenario.values()), len(groups)


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
    """Build the promotion envelope from runtime-bound, paired candidate observations.

    ``group_id`` remains the independent asset/story unit used by the paired bootstrap. Scenario
    maturity and repeated-run stability are tracked separately through explicit ``scenario_id`` and
    ``repeat_index`` fields. This prevents pseudo-replication from inflating the number of independent
    experimental units while still making the amount of scenario/repeat coverage quantitative.

    Candidate/provider identity is code-owned and the expected runtime config hash is recomputed
    from the canonical 18-tool contract plus the exact candidate identity. Pairwise EDD reports are
    generated in both directions for every candidate pair so the promotion gate never accepts an
    incomplete comparison matrix.
    """

    if len(candidates) < 2:
        raise ValueError("provider_benchmark_requires_at_least_two_candidates")
    if len({candidate.identity.candidate_id for candidate in candidates}) != len(candidates):
        raise ValueError("provider_benchmark_duplicate_candidate")

    registry = canonical_tool_registry()
    runtime_hashes: dict[str, str] = {}
    independent_group_counts: dict[str, int] = {}
    provider_candidates: list[ProviderCandidateEvidence] = []
    bundles: dict[str, EvalMetricBundle] = {}

    canonical_coverage: set[tuple[str, int, str]] | None = None
    for candidate in candidates:
        candidate_id = candidate.identity.candidate_id
        expected_hash = production_runtime_config_hash(
            runtime_config,
            registry,
            candidate.identity,
        )
        if candidate.runtime_config_hash != expected_hash:
            raise ValueError("provider_benchmark_runtime_config_hash_mismatch")
        if candidate.human_calibration is not None:
            if candidate.human_calibration.config_hash != expected_hash:
                raise ValueError("provider_benchmark_human_config_hash_mismatch")
            if candidate.human_calibration.protocol_id != human_calibration_protocol.protocol_id:
                raise ValueError("provider_benchmark_human_protocol_id_mismatch")
            if candidate.human_calibration.protocol_hash != human_calibration_protocol.protocol_sha256:
                raise ValueError("provider_benchmark_human_protocol_hash_mismatch")

        coverage = {
            (item.scenario_id, item.repeat_index, item.group_id)
            for item in candidate.observations
        }
        if canonical_coverage is None:
            canonical_coverage = coverage
        elif coverage != canonical_coverage:
            raise ValueError("provider_benchmark_candidate_coverage_mismatch")

        scenario_count, repeat_count, independent_group_count = _observation_maturity(
            candidate.observations
        )
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
        independent_group_counts[candidate_id] = independent_group_count
        bundles[candidate_id] = candidate.eval_bundle()

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
        independent_group_counts=independent_group_counts,
        rule_set_hash=rule_hash,
    )
