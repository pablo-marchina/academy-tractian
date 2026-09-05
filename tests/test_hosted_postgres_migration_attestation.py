from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.hosted_postgres_migration_attestation import (
    EXPECTED_META,
    REQUIRED_TABLES,
    RLS_TABLES,
    HostedPostgresMigrationObservation,
    HostedPostgresMigrationPolicy,
    MetaVersion,
    build_hosted_postgres_migration_evidence,
    decide_hosted_postgres_migration,
)
from academy_tractian.hosted_postgres_preflight import HostedPostgresPreflightDecision


CODE_SHA = "a" * 40
SQL_SHA = "b" * 64
SOURCE_SHA = "c" * 64
PREFLIGHT_SHA = "d" * 64


def _observation(**overrides):
    values = {
        "table_names": tuple(sorted(REQUIRED_TABLES)),
        "rls_enabled_tables": tuple(sorted(RLS_TABLES)),
        "tenant_select_policy_tables": tuple(sorted(RLS_TABLES)),
        "scoped_select_grant_tables": tuple(sorted(RLS_TABLES)),
        "meta_versions": tuple(
            MetaVersion(relation=relation, key=key, value=value)
            for relation, key, value in sorted(EXPECTED_META)
        ),
    }
    values.update(overrides)
    return HostedPostgresMigrationObservation(**values)


def _evidence(**overrides):
    values = {
        "code_sha": CODE_SHA,
        "migration_sql_sha256": SQL_SHA,
        "source_manifest_sha256": SOURCE_SHA,
        "preflight_artifact_sha256": PREFLIGHT_SHA,
        "observation": _observation(),
    }
    values.update(overrides)
    return build_hosted_postgres_migration_evidence(**values)


def _policy(**overrides):
    values = {
        "expected_code_sha": CODE_SHA,
        "expected_migration_sql_sha256": SQL_SHA,
        "expected_source_manifest_sha256": SOURCE_SHA,
        "expected_preflight_artifact_sha256": PREFLIGHT_SHA,
    }
    values.update(overrides)
    return HostedPostgresMigrationPolicy(**values)


def _preflight(outcome="PREFLIGHT_PASS"):
    return HostedPostgresPreflightDecision(outcome=outcome, reason_codes=())


def test_complete_migration_attestation_passes() -> None:
    decision = decide_hosted_postgres_migration(
        evidence=_evidence(), policy=_policy(), preflight_decision=_preflight()
    )
    assert decision.outcome == "MIGRATION_PASS"
    assert decision.reason_codes == ()


@pytest.mark.parametrize(
    ("evidence_overrides", "policy_overrides", "preflight", "reason"),
    [
        ({}, {}, "PREFLIGHT_FAIL", "POSTGRES_PREFLIGHT_NOT_PASSED"),
        ({"code_sha": "e" * 40}, {}, "PREFLIGHT_PASS", "CODE_SHA_MISMATCH"),
        ({"migration_sql_sha256": "e" * 64}, {}, "PREFLIGHT_PASS", "MIGRATION_SQL_SHA_MISMATCH"),
        ({"source_manifest_sha256": "e" * 64}, {}, "PREFLIGHT_PASS", "SOURCE_MANIFEST_SHA_MISMATCH"),
        ({"preflight_artifact_sha256": "e" * 64}, {}, "PREFLIGHT_PASS", "PREFLIGHT_ARTIFACT_SHA_MISMATCH"),
    ],
)
def test_provenance_and_preflight_gates_are_non_compensatory(
    evidence_overrides, policy_overrides, preflight, reason
) -> None:
    decision = decide_hosted_postgres_migration(
        evidence=_evidence(**evidence_overrides),
        policy=_policy(**policy_overrides),
        preflight_decision=_preflight(preflight),
    )
    assert decision.outcome == "MIGRATION_FAIL"
    assert reason in decision.reason_codes


@pytest.mark.parametrize(
    ("observation", "reason"),
    [
        (
            _observation(table_names=tuple(sorted(REQUIRED_TABLES[1:]))),
            "REQUIRED_TABLES_MISSING",
        ),
        (
            _observation(rls_enabled_tables=tuple(sorted(RLS_TABLES[1:]))),
            "RLS_NOT_ENABLED_ON_REQUIRED_TABLES",
        ),
        (
            _observation(tenant_select_policy_tables=tuple(sorted(RLS_TABLES[1:]))),
            "TENANT_SELECT_POLICY_MISSING",
        ),
        (
            _observation(scoped_select_grant_tables=tuple(sorted(RLS_TABLES[1:]))),
            "SCOPED_SELECT_GRANT_MISSING",
        ),
        (
            _observation(
                meta_versions=tuple(
                    MetaVersion(relation=relation, key=key, value=("wrong" if index == 0 else value))
                    for index, (relation, key, value) in enumerate(sorted(EXPECTED_META))
                )
            ),
            "SCHEMA_META_VERSION_MISMATCH",
        ),
    ],
)
def test_each_live_schema_surface_is_a_hard_gate(observation, reason) -> None:
    decision = decide_hosted_postgres_migration(
        evidence=_evidence(observation=observation),
        policy=_policy(),
        preflight_decision=_preflight(),
    )
    assert decision.outcome == "MIGRATION_FAIL"
    assert reason in decision.reason_codes


def test_attestation_hash_detects_tampering() -> None:
    evidence = _evidence()
    payload = evidence.model_dump(mode="json")
    payload["code_sha"] = "f" * 40
    with pytest.raises(ValidationError, match="hosted_postgres_migration_attestation_hash_mismatch"):
        type(evidence).model_validate(payload)


def test_observation_requires_canonical_unique_ordering() -> None:
    with pytest.raises(ValidationError, match="observation_set_not_canonical"):
        HostedPostgresMigrationObservation(
            table_names=("b", "a"),
            rls_enabled_tables=(),
            tenant_select_policy_tables=(),
            scoped_select_grant_tables=(),
            meta_versions=(),
        )
