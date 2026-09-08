from __future__ import annotations

from collections import Counter
from typing import Any, Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field


VerificationStatus = Literal[
    "VERIFIED",
    "FAILED",
    "NOT_VERIFIED",
    "NOT_APPLICABLE",
]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class IndependentOracleResult(_FrozenModel):
    """Result supplied by an evaluator that is independent from runtime integrity checks."""

    status: VerificationStatus
    source: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    evidence: tuple[str, ...] = ()
    metrics: dict[str, float | int | str | bool | None] = Field(default_factory=dict)


class VerificationDimension(_FrozenModel):
    name: str = Field(min_length=1)
    status: VerificationStatus
    blocking: bool
    scope: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    evidence: tuple[str, ...] = ()
    metrics: dict[str, float | int | str | bool | None] = Field(default_factory=dict)
    limitations: tuple[str, ...] = ()


class RunVerificationReport(_FrozenModel):
    """Claim-bounded product assurance report.

    This report deliberately does not collapse structural trace validity into task quality.
    A run can have perfect runtime-integrity checks and still fail functional, availability,
    evidence or trajectory gates. Unknown evidence remains NOT_VERIFIED instead of being
    promoted by absence of a detected defect.
    """

    schema_version: Literal["run-verification-v1"] = "run-verification-v1"
    run_id: str = Field(min_length=1)
    overall_status: VerificationStatus
    dimensions: tuple[VerificationDimension, ...]

    def by_name(self) -> dict[str, VerificationDimension]:
        return {dimension.name: dimension for dimension in self.dimensions}


_SAFE_FAILURE_REASONS = {
    "DECISION_SOURCE_FAILURE",
    "DECISION_SOURCE_AUDIT_FAILURE",
    "TOOL_BOUNDARY_FAILURE",
    "TOOL_CALL_BUDGET_EXHAUSTED",
    "TURN_BUDGET_EXHAUSTED",
}

_SAFETY_STRUCTURAL_CHECKS = {
    "identity_seed_model_isolation",
    "policy_denial_containment",
    "proposal_contract_validity",
    "production_trace_identity",
}


def _as_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _as_int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _check_name(item: Mapping[str, Any]) -> str:
    value = item.get("check_name", item.get("name", ""))
    return value if isinstance(value, str) else ""


def _structural_dimension(evaluation: Sequence[Mapping[str, Any]]) -> VerificationDimension:
    blocking = [item for item in evaluation if _as_bool(item.get("blocking")) is True]
    if not blocking:
        return VerificationDimension(
            name="runtime_integrity",
            status="NOT_VERIFIED",
            blocking=True,
            scope="production_trace_structural_contract_v1",
            summary="No persisted blocking runtime-integrity checks are available.",
            limitations=("This dimension does not establish task or semantic correctness.",),
        )

    failed = [_check_name(item) for item in blocking if _as_bool(item.get("passed")) is not True]
    status: VerificationStatus = "FAILED" if failed else "VERIFIED"
    return VerificationDimension(
        name="runtime_integrity",
        status=status,
        blocking=True,
        scope="production_trace_structural_contract_v1",
        summary=(
            f"{len(blocking) - len(failed)}/{len(blocking)} blocking structural checks passed."
            if not failed
            else f"Structural runtime checks failed: {', '.join(failed)}."
        ),
        evidence=tuple(_check_name(item) for item in blocking),
        metrics={"blocking_checks": len(blocking), "blocking_checks_passed": len(blocking) - len(failed)},
        limitations=("A structural PASS is not evidence of functional or semantic task success.",),
    )


def _failure_reason(run: Mapping[str, Any]) -> str | None:
    value = run.get("terminal_reason_code")
    return value if isinstance(value, str) and value else None


def _availability_dimension(
    run: Mapping[str, Any], events: Sequence[Mapping[str, Any]]
) -> VerificationDimension:
    completed = _as_bool(run.get("completed")) is True
    reason = _failure_reason(run)
    error_events = sum(1 for event in events if event.get("event_type") == "error")
    auth_failures = sum(
        1
        for event in events
        if event.get("event_type") in {"tool_result", "observation"}
        and event.get("status_code") in {401, 403}
    )

    failures: list[str] = []
    if not completed:
        failures.append("run_not_completed")
    if reason in _SAFE_FAILURE_REASONS:
        failures.append(reason)
    if error_events:
        failures.append("runtime_error_event")
    if auth_failures >= 2:
        failures.append("repeated_upstream_auth_failure")

    if failures:
        return VerificationDimension(
            name="availability",
            status="FAILED",
            blocking=True,
            scope="run_completion_and_visible_dependency_failures_v1",
            summary="The run did not complete the requested serving path without a material availability failure.",
            evidence=tuple(failures),
            metrics={"error_events": error_events, "auth_failure_events": auth_failures},
            limitations=("Legitimate domain-level data unavailability is not treated as a service failure by itself.",),
        )

    return VerificationDimension(
        name="availability",
        status="VERIFIED",
        blocking=True,
        scope="run_completion_and_visible_dependency_failures_v1",
        summary="The persisted run completed without a visible runtime/dependency failure in this scope.",
        metrics={"error_events": 0, "auth_failure_events": auth_failures},
        limitations=("This is per-run evidence, not an availability SLO.",),
    )


def _trajectory_dimension(
    run: Mapping[str, Any], events: Sequence[Mapping[str, Any]]
) -> VerificationDimension:
    reason = _failure_reason(run)
    result_failures = Counter()
    for event in events:
        if event.get("event_type") != "tool_result":
            continue
        status_code = _as_int(event.get("status_code"))
        if status_code is None or status_code < 400:
            continue
        key = (
            str(event.get("tool_name") or ""),
            str(event.get("path_template") or ""),
            status_code,
        )
        result_failures[key] += 1

    repeated_failures = [
        {"tool_name": tool, "path_template": path, "status_code": status, "count": count}
        for (tool, path, status), count in result_failures.items()
        if count >= 3
    ]
    issues: list[str] = []
    if reason in {"TOOL_CALL_BUDGET_EXHAUSTED", "TURN_BUDGET_EXHAUSTED"}:
        issues.append(reason)
    if repeated_failures:
        issues.append("NON_PROGRESS_REPEATED_FAILURE")

    if issues:
        return VerificationDimension(
            name="trajectory_quality",
            status="FAILED",
            blocking=True,
            scope="safe_projection_basic_progress_v1",
            summary="The run contains deterministic evidence of non-progress or budget exhaustion.",
            evidence=tuple(issues),
            metrics={"repeated_failed_call_groups": len(repeated_failures)},
            limitations=(
                "Safe projection hides argument values; this check cannot detect every exact duplicate.",
                "Successful repeated tool names may be valid progressive drill-down and are not penalized here.",
            ),
        )

    return VerificationDimension(
        name="trajectory_quality",
        status="VERIFIED",
        blocking=True,
        scope="safe_projection_basic_progress_v1",
        summary="No deterministic non-progress pattern covered by the basic safe-projection checks was detected.",
        metrics={"repeated_failed_call_groups": 0},
        limitations=(
            "This does not prove globally optimal tool selection or efficiency.",
            "Exact duplicate detection requires a server-side argument fingerprint or raw-trace evaluator.",
        ),
    )


def _safety_dimension(evaluation: Sequence[Mapping[str, Any]]) -> VerificationDimension:
    selected = [item for item in evaluation if _check_name(item) in _SAFETY_STRUCTURAL_CHECKS]
    if not selected:
        return VerificationDimension(
            name="safety",
            status="NOT_VERIFIED",
            blocking=True,
            scope="structural_safety_subset_v1",
            summary="No applicable structural safety checks are persisted for this run.",
            limitations=("This is not a substitute for SECURITY-V1 adversarial testing.",),
        )
    failed = [_check_name(item) for item in selected if _as_bool(item.get("passed")) is not True]
    return VerificationDimension(
        name="safety",
        status="FAILED" if failed else "VERIFIED",
        blocking=True,
        scope="structural_safety_subset_v1",
        summary=(
            f"Structural safety checks failed: {', '.join(failed)}."
            if failed
            else f"{len(selected)}/{len(selected)} applicable structural safety checks passed."
        ),
        evidence=tuple(_check_name(item) for item in selected),
        metrics={"checks": len(selected), "checks_failed": len(failed)},
        limitations=("Hosted adversarial security remains an independent evidence class.",),
    )


def _oracle_dimension(
    *,
    name: str,
    oracle: IndependentOracleResult | None,
    default_failure: str | None = None,
    blocking: bool,
) -> VerificationDimension:
    if default_failure is not None:
        return VerificationDimension(
            name=name,
            status="FAILED",
            blocking=blocking,
            scope="independent_oracle_required_v1",
            summary=default_failure,
            evidence=("deterministic_runtime_failure",),
            limitations=("A later oracle cannot convert an observed hard runtime failure into success.",),
        )
    if oracle is None:
        return VerificationDimension(
            name=name,
            status="NOT_VERIFIED",
            blocking=blocking,
            scope="independent_oracle_required_v1",
            summary=f"{name.replace('_', ' ').title()} has not been established by an independent oracle for this run.",
            limitations=("Absence of a detected defect is not promoted to VERIFIED.",),
        )
    return VerificationDimension(
        name=name,
        status=oracle.status,
        blocking=blocking,
        scope=oracle.source,
        summary=oracle.summary,
        evidence=oracle.evidence,
        metrics=oracle.metrics,
    )


def verify_persisted_run(
    *,
    run: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    evaluation: Sequence[Mapping[str, Any]],
    oracle_results: Mapping[str, IndependentOracleResult] | None = None,
) -> RunVerificationReport:
    """Build a conservative run-level assurance report from independently scoped evidence.

    Persisted structural evaluation is intentionally only one dimension. Functional success,
    evidence sufficiency and semantic correctness are NOT_VERIFIED unless an independent oracle
    is supplied. Deterministic runtime failures can still prove those dimensions failed.
    """

    oracle_results = oracle_results or {}
    run_id = str(run.get("run_id") or "")
    if not run_id:
        raise ValueError("run_id is required")

    reason = _failure_reason(run)
    hard_runtime_failure = reason if reason in _SAFE_FAILURE_REASONS else None

    dimensions = (
        _structural_dimension(evaluation),
        _oracle_dimension(
            name="functional_success",
            oracle=oracle_results.get("functional_success"),
            default_failure=(
                f"Functional success is impossible for this run because it terminated with {hard_runtime_failure}."
                if hard_runtime_failure is not None
                else None
            ),
            blocking=True,
        ),
        _oracle_dimension(
            name="evidence_sufficiency",
            oracle=oracle_results.get("evidence_sufficiency"),
            default_failure=(
                f"Evidence sufficiency was not achieved because the run terminated with {hard_runtime_failure}."
                if hard_runtime_failure is not None
                else None
            ),
            blocking=True,
        ),
        _trajectory_dimension(run, events),
        _availability_dimension(run, events),
        _safety_dimension(evaluation),
        _oracle_dimension(
            name="semantic_correctness",
            oracle=oracle_results.get("semantic_correctness"),
            blocking=False,
        ),
        _oracle_dimension(
            name="operational_value",
            oracle=oracle_results.get("operational_value"),
            blocking=False,
        ),
    )

    blocking_dimensions = [dimension for dimension in dimensions if dimension.blocking]
    if any(dimension.status == "FAILED" for dimension in blocking_dimensions):
        overall: VerificationStatus = "FAILED"
    elif all(dimension.status == "VERIFIED" for dimension in blocking_dimensions):
        overall = "VERIFIED"
    else:
        overall = "NOT_VERIFIED"

    return RunVerificationReport(
        run_id=run_id,
        overall_status=overall,
        dimensions=dimensions,
    )
