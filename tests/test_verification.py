from __future__ import annotations

from academy_tractian.verification import IndependentOracleResult, verify_persisted_run


STRUCTURAL_CHECKS = (
    "trace_lifecycle",
    "production_trace_identity",
    "proposal_contract_validity",
    "identity_seed_model_isolation",
    "execution_chain_integrity",
    "policy_denial_containment",
    "provider_free_trace",
    "model_call_provenance",
    "read_only_action_safety",
    "terminal_consistency",
)


def _evaluation(*, failed: set[str] | None = None) -> list[dict[str, object]]:
    failed = failed or set()
    return [
        {"check_name": name, "passed": name not in failed, "blocking": True}
        for name in STRUCTURAL_CHECKS
    ]


def _run(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "run_id": "run_test",
        "completed": True,
        "terminal_reason_code": None,
        "terminal_response_mode": "complete",
        "tool_calls": 2,
    }
    payload.update(overrides)
    return payload


def _clean_events() -> list[dict[str, object]]:
    return [
        {"event_type": "run_started"},
        {"event_type": "tool_result", "tool_name": "get_current_user", "status_code": 200},
        {"event_type": "observation", "tool_name": "get_current_user", "status_code": 200},
        {"event_type": "run_finished"},
    ]


def test_structural_green_is_not_promoted_to_overall_quality() -> None:
    report = verify_persisted_run(
        run=_run(),
        events=_clean_events(),
        evaluation=_evaluation(),
    )

    dimensions = report.by_name()
    assert dimensions["runtime_integrity"].status == "VERIFIED"
    assert dimensions["functional_success"].status == "NOT_VERIFIED"
    assert dimensions["evidence_sufficiency"].status == "NOT_VERIFIED"
    assert dimensions["semantic_correctness"].status == "NOT_VERIFIED"
    assert report.overall_status == "NOT_VERIFIED"


def test_safe_failure_cannot_receive_overall_green_when_structural_checks_pass() -> None:
    report = verify_persisted_run(
        run=_run(
            terminal_reason_code="DECISION_SOURCE_FAILURE",
            terminal_response_mode="unavailable",
        ),
        events=_clean_events(),
        evaluation=_evaluation(),
    )

    dimensions = report.by_name()
    assert dimensions["runtime_integrity"].status == "VERIFIED"
    assert dimensions["functional_success"].status == "FAILED"
    assert dimensions["evidence_sufficiency"].status == "FAILED"
    assert dimensions["availability"].status == "FAILED"
    assert report.overall_status == "FAILED"


def test_repeated_401_loop_is_detected_as_non_progress() -> None:
    events: list[dict[str, object]] = [{"event_type": "run_started"}]
    for _ in range(6):
        events.extend(
            [
                {"event_type": "tool_result", "tool_name": "get_current_user", "status_code": 401},
                {"event_type": "observation", "tool_name": "get_current_user", "status_code": 401},
            ]
        )
    events.append({"event_type": "run_finished"})

    report = verify_persisted_run(
        run=_run(
            terminal_reason_code="TOOL_CALL_BUDGET_EXHAUSTED",
            terminal_response_mode="unavailable",
            tool_calls=6,
        ),
        events=events,
        evaluation=_evaluation(),
    )

    dimensions = report.by_name()
    assert dimensions["trajectory_quality"].status == "FAILED"
    assert "NON_PROGRESS_REPEATED_FAILURE" in dimensions["trajectory_quality"].evidence
    assert dimensions["availability"].status == "FAILED"
    assert report.overall_status == "FAILED"


def test_structural_failure_remains_a_hard_failure() -> None:
    report = verify_persisted_run(
        run=_run(),
        events=_clean_events(),
        evaluation=_evaluation(failed={"execution_chain_integrity"}),
    )

    assert report.by_name()["runtime_integrity"].status == "FAILED"
    assert report.overall_status == "FAILED"


def test_independent_oracles_can_verify_functional_and_evidence_dimensions() -> None:
    report = verify_persisted_run(
        run=_run(),
        events=_clean_events(),
        evaluation=_evaluation(),
        oracle_results={
            "functional_success": IndependentOracleResult(
                status="VERIFIED",
                source="golden-functional-oracle-v1",
                summary="All mandatory functional requirements were observed.",
                evidence=("case:G01",),
            ),
            "evidence_sufficiency": IndependentOracleResult(
                status="VERIFIED",
                source="evidence-requirement-oracle-v1",
                summary="All required evidence classes were observed before terminal.",
                evidence=("condition_evidence",),
            ),
        },
    )

    assert report.by_name()["functional_success"].status == "VERIFIED"
    assert report.by_name()["evidence_sufficiency"].status == "VERIFIED"
    assert report.overall_status == "VERIFIED"
    assert report.by_name()["semantic_correctness"].status == "NOT_VERIFIED"


def test_nonblocking_semantic_unknown_does_not_falsely_fail_verified_hard_gates() -> None:
    report = verify_persisted_run(
        run=_run(),
        events=_clean_events(),
        evaluation=_evaluation(),
        oracle_results={
            "functional_success": IndependentOracleResult(
                status="VERIFIED",
                source="functional-oracle-v1",
                summary="Functional rubric passed.",
            ),
            "evidence_sufficiency": IndependentOracleResult(
                status="VERIFIED",
                source="evidence-oracle-v1",
                summary="Evidence rubric passed.",
            ),
        },
    )

    assert report.overall_status == "VERIFIED"
    assert report.by_name()["semantic_correctness"].blocking is False
