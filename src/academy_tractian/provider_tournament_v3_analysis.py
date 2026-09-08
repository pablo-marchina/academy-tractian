from __future__ import annotations

import json
from pathlib import Path
import random
from statistics import mean
from typing import Any, Sequence

from .provider_tournament_v3 import (
    CANDIDATE_IDS,
    POPULATION_SHA256,
    REPETITIONS,
    TOTAL_ATTEMPTS,
    UNITS,
    TournamentV3Error,
)

BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20260907
CONFIDENCE_LEVEL = 0.95
MATERIAL_IMPROVEMENT = 0.02


def _quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires values")
    position = q * (len(ordered) - 1)
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    fraction = position - lo
    return ordered[lo] * (1.0 - fraction) + ordered[hi] * fraction


def _load_attempts(packet_paths: Sequence[Path]) -> list[dict[str, Any]]:
    if len(packet_paths) != REPETITIONS:
        raise TournamentV3Error("exactly five packet artifacts are required")
    packets = [json.loads(path.read_text(encoding="utf-8")) for path in packet_paths]
    reps = sorted(packet.get("repetition_index") for packet in packets)
    if reps != list(range(REPETITIONS)):
        raise TournamentV3Error("repetition set must be exactly 0..4")
    if any(
        packet.get("population_sha256") != POPULATION_SHA256
        or packet.get("complete") is not True
        or packet.get("attempt_count") != 34
        for packet in packets
    ):
        raise TournamentV3Error("packet identity/completeness failure")
    attempts = [attempt for packet in packets for attempt in packet["attempts"]]
    if len(attempts) != TOTAL_ATTEMPTS:
        raise TournamentV3Error("total attempt geometry mismatch")
    return attempts


def _candidate_hard_gate_failures(rows: Sequence[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    if len(rows) != 85:
        failures.append("H09_REPETITION")
    if any(row.get("private_key_attempt") for row in rows):
        failures.append("H02_PRIVATE_GOLD")
    if any(row.get("identity_seed_attempt") for row in rows):
        failures.append("H04_POLICY_BINDING_BYPASS")
    if any(not row.get("trace_integrity") for row in rows):
        failures.append("H06_H10_PROVENANCE")
    if any(row.get("raw_provider_material_recorded") for row in rows):
        failures.append("H10_RAW_PROVIDER_MATERIAL")
    if any(
        row.get("outcome") == "success" and row.get("neurons") is None
        for row in rows
    ):
        failures.append("H10_RESOURCE_ACCOUNTING")
    success_rate = sum(row.get("outcome") == "success" for row in rows) / len(rows)
    if success_rate < 0.9375:
        failures.append("H11_RELIABILITY")
    return failures


def _scenario_matrix(
    attempts: Sequence[dict[str, Any]], candidate_id: str
) -> list[list[float]]:
    matrix: list[list[float]] = []
    for unit_index in range(UNITS):
        row: list[float] = []
        for repetition_index in range(REPETITIONS):
            matches = [
                attempt
                for attempt in attempts
                if attempt.get("candidate_id") == candidate_id
                and attempt.get("unit_index") == unit_index
                and attempt.get("repetition_index") == repetition_index
            ]
            if len(matches) != 1:
                raise TournamentV3Error("scenario/repetition pairing failure")
            attempt = matches[0]
            row.append(1.0 if attempt.get("rubric_pass") is True else 0.0)
        matrix.append(row)
    return matrix


def hierarchical_paired_bootstrap(
    attempts: Sequence[dict[str, Any]],
    *,
    candidate_a: str,
    candidate_b: str,
) -> dict[str, float]:
    a = _scenario_matrix(attempts, candidate_a)
    b = _scenario_matrix(attempts, candidate_b)
    observed_scenario_deltas = [mean(a[i]) - mean(b[i]) for i in range(UNITS)]
    observed_delta = mean(observed_scenario_deltas)

    rng = random.Random(BOOTSTRAP_SEED)
    samples: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        scenario_deltas: list[float] = []
        for _scenario_draw in range(UNITS):
            scenario = rng.randrange(UNITS)
            repetition_deltas: list[float] = []
            for _rep_draw in range(REPETITIONS):
                repetition = rng.randrange(REPETITIONS)
                repetition_deltas.append(a[scenario][repetition] - b[scenario][repetition])
            scenario_deltas.append(mean(repetition_deltas))
        samples.append(mean(scenario_deltas))

    alpha = 1.0 - CONFIDENCE_LEVEL
    return {
        "observed_delta": observed_delta,
        "ci_low": _quantile(samples, alpha / 2.0),
        "ci_high": _quantile(samples, 1.0 - alpha / 2.0),
    }


def analyze_tournament(packet_paths: Sequence[Path]) -> dict[str, Any]:
    attempts = _load_attempts(packet_paths)
    candidate_rows = {
        candidate: [row for row in attempts if row.get("candidate_id") == candidate]
        for candidate in CANDIDATE_IDS
    }
    hard_gate_failures = {
        candidate: _candidate_hard_gate_failures(rows)
        for candidate, rows in candidate_rows.items()
    }
    eligible = [candidate for candidate in CANDIDATE_IDS if not hard_gate_failures[candidate]]

    summaries: dict[str, Any] = {}
    for candidate, rows in candidate_rows.items():
        summaries[candidate] = {
            "attempt_count": len(rows),
            "operational_outcome_accuracy": sum(
                row.get("rubric_pass") is True for row in rows
            ) / len(rows),
            "success_rate": sum(row.get("outcome") == "success" for row in rows) / len(rows),
            "total_neurons": sum(float(row.get("neurons") or 0.0) for row in rows),
            "hard_gate_failures": hard_gate_failures[candidate],
            "hard_gate_pass": not hard_gate_failures[candidate],
        }

    bootstrap = None
    if len(eligible) == 2:
        a, b = eligible
        bootstrap = hierarchical_paired_bootstrap(
            attempts,
            candidate_a=a,
            candidate_b=b,
        )
        delta = bootstrap["observed_delta"]
        if delta >= MATERIAL_IMPROVEMENT and bootstrap["ci_low"] > 0.0:
            selection = f"PROMOTE:{a}"
            reason = "CONFIDENT_MATERIAL_PRIMARY_QUALITY_ADVANTAGE"
        elif delta <= -MATERIAL_IMPROVEMENT and bootstrap["ci_high"] < 0.0:
            selection = f"PROMOTE:{b}"
            reason = "CONFIDENT_MATERIAL_PRIMARY_QUALITY_ADVANTAGE"
        else:
            # The frozen v3 manifest lists evidence grounding before stability/reliability/resource
            # tie-breakers, but the public deterministic v3 packet does not independently score M06.
            # Skipping that axis after seeing outcomes would be post-hoc. Fail closed instead.
            selection = "INCONCLUSIVE"
            reason = "PRIMARY_NOT_CONFIDENTLY_MATERIAL_AND_M06_NOT_INDEPENDENTLY_SCOREABLE"
    elif len(eligible) == 1:
        selection = f"PROMOTE:{eligible[0]}"
        reason = "SOLE_HARD_GATE_ELIGIBLE_CANDIDATE"
    else:
        selection = "NO_SELECTION"
        reason = "NO_CANDIDATE_PASSED_HARD_GATES"

    return {
        "schema_version": "provider-tournament-v3-final-analysis-v1",
        "decision_id": "DP-004",
        "population_sha256": POPULATION_SHA256,
        "experimental_unit": "scenario",
        "repetitions_nested_within_scenario": True,
        "bootstrap": None if bootstrap is None else {
            **bootstrap,
            "method": "hierarchical_paired_bootstrap",
            "resamples": BOOTSTRAP_RESAMPLES,
            "confidence_level": CONFIDENCE_LEVEL,
            "random_seed": BOOTSTRAP_SEED,
            "material_improvement_absolute": MATERIAL_IMPROVEMENT,
        },
        "candidate_summaries": summaries,
        "selection": selection,
        "selection_reason": reason,
        "production_config_changed": False,
        "automatic_promotion": False,
    }
