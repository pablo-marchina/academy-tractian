from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.delivery_evidence import (
    DEMO_RESULT_MANIFEST_PATH,
    EXPECTED_DELIVERY_DEMO_REPORT_SHA256,
    EXPECTED_DELIVERY_DEMO_RESULT_SHA256,
    validate_delivery_evidence_index,
)
from academy_tractian.delivery_reproduction import (
    EvidenceIndex,
    run_provider_free_delivery_demo,
)


EVIDENCE_INDEX_PATH = "research/results/final-delivery-evidence-index-2026-08-28.json"
SCENARIO_MANIFEST_FIELDS = (
    "scenario_id",
    "spec_sha256",
    "terminal_decision",
    "terminal_reason_code",
    "tool_selection_sha256",
    "canonical_arguments_sha256",
    "policy_outcomes_sha256",
    "action_fingerprint_sha256",
    "evaluator_pass",
    "behavioral_trace_sha256",
    "trace_sha256",
    "transport_count",
    "action_transport_count",
    "durable_claim_count",
    "result_sha256",
)


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _scenario_snapshot(result: object) -> dict[str, object]:
    payload = result.model_dump(mode="json")
    return {field: payload[field] for field in SCENARIO_MANIFEST_FIELDS}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="delivery-reproduction-") as tmp:
        report = run_provider_free_delivery_demo(Path(tmp) / "demo")

    failures: list[str] = []
    if report.report_sha256 != EXPECTED_DELIVERY_DEMO_REPORT_SHA256:
        failures.append("report_sha256")
    if report.denominator != 5:
        failures.append("denominator")
    if report.exact_traces_evaluated != 5:
        failures.append("exact_traces_evaluated")
    if report.contract_expectations_passed != 5:
        failures.append("contract_expectations_passed")
    if report.provider_calls != 0:
        failures.append("provider_calls")
    if report.credential_account_probes != 0:
        failures.append("credential_account_probes")
    if report.real_customer_mutations != 0:
        failures.append("real_customer_mutations")
    if report.semantic_private_blind_access != 0:
        failures.append("semantic_private_blind_access")
    if report.automatic_retry_count != 0:
        failures.append("automatic_retry_count")
    if report.replay_count != 0:
        failures.append("replay_count")
    if not all(result.trace_lifecycle_valid for result in report.results):
        failures.append("trace_lifecycle")
    if not all(result.evaluator_pass for result in report.results):
        failures.append("evaluator_classification")
    if not all(result.contract_expectations_met for result in report.results):
        failures.append("scenario_contracts")

    controlled = report.results[-1]
    if controlled.scenario_id != "DEMO-05":
        failures.append("controlled_scenario_order")
    if controlled.action_transport_count != 1:
        failures.append("controlled_action_transport_count")
    if controlled.durable_claim_count != 1:
        failures.append("controlled_durable_claim_count")

    try:
        manifest = _load_json(ROOT / DEMO_RESULT_MANIFEST_PATH)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        manifest = {}
        failures.append("demo_manifest_parse")

    manifest_expected_scalars = {
        "campaign_version": report.campaign_version,
        "report_sha256": report.report_sha256,
        "denominator": report.denominator,
        "exact_traces_evaluated": report.exact_traces_evaluated,
        "contract_expectations_passed": report.contract_expectations_passed,
        "provider_calls": report.provider_calls,
        "credential_account_probes": report.credential_account_probes,
        "real_customer_mutations": report.real_customer_mutations,
        "semantic_private_blind_access": report.semantic_private_blind_access,
        "automatic_retry_count": report.automatic_retry_count,
        "replay_count": report.replay_count,
    }
    for field, expected in manifest_expected_scalars.items():
        if manifest.get(field) != expected:
            failures.append(f"demo_manifest_{field}")

    expected_scenarios = [_scenario_snapshot(result) for result in report.results]
    if manifest.get("scenarios") != expected_scenarios:
        failures.append("demo_manifest_scenarios")
    if [result.result_sha256 for result in report.results] != list(
        EXPECTED_DELIVERY_DEMO_RESULT_SHA256.values()
    ):
        failures.append("scenario_result_identity")

    evidence_validation = None
    try:
        evidence_payload = _load_json(ROOT / EVIDENCE_INDEX_PATH)
        evidence_index = EvidenceIndex.model_validate(evidence_payload)
        evidence_validation = validate_delivery_evidence_index(evidence_index, ROOT)
        if not evidence_validation.passed:
            failures.append("evidence_index")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        failures.append("evidence_index_parse")

    status = "PASS" if not failures else "FAIL"
    print(f"DELIVERY_REPRODUCTION_VALIDATION={status}")
    print(f"DELIVERY_DEMO_REPORT_SHA256={report.report_sha256}")
    print(f"DELIVERY_DEMO_DENOMINATOR={report.denominator}")
    print(f"DELIVERY_DEMO_EXACT_TRACES_EVALUATED={report.exact_traces_evaluated}")
    print(f"DELIVERY_DEMO_CONTRACT_EXPECTATIONS_PASSED={report.contract_expectations_passed}")
    print(f"DELIVERY_DEMO_PROVIDER_CALLS={report.provider_calls}")
    print(f"DELIVERY_DEMO_CREDENTIAL_ACCOUNT_PROBES={report.credential_account_probes}")
    print(f"DELIVERY_DEMO_REAL_CUSTOMER_MUTATIONS={report.real_customer_mutations}")
    print(f"DELIVERY_DEMO_SEMANTIC_PRIVATE_BLIND_ACCESS={report.semantic_private_blind_access}")
    if evidence_validation is not None:
        print(f"DELIVERY_EVIDENCE_INDEX_ENTRIES={evidence_validation.entry_count}")
        print(
            "DELIVERY_EVIDENCE_INDEX_REPOSITORY_RESIDENT="
            f"{evidence_validation.repository_resident_count}"
        )
        print(
            "DELIVERY_EVIDENCE_INDEX_RESOLVED="
            f"{evidence_validation.resolved_repository_entries}"
        )
        print(f"DELIVERY_EVIDENCE_INDEX_VIOLATIONS={len(evidence_validation.violations)}")
    for result in report.results:
        key = result.scenario_id.replace("-", "_")
        print(f"DELIVERY_{key}_SPEC_SHA256={result.spec_sha256}")
        print(f"DELIVERY_{key}_RESULT_SHA256={result.result_sha256}")
        print(f"DELIVERY_{key}_TRACE_SHA256={result.trace_sha256}")
        print(f"DELIVERY_{key}_BEHAVIOR_SHA256={result.behavioral_trace_sha256}")
    if failures:
        print("DELIVERY_REPRODUCTION_FAILURES=" + ",".join(failures))
        if evidence_validation is not None and evidence_validation.violations:
            print(
                "DELIVERY_EVIDENCE_INDEX_VIOLATION_DETAILS="
                + json.dumps(list(evidence_validation.violations), separators=(",", ":"))
            )
    print(
        "DELIVERY_DEMO_REPORT_JSON="
        + json.dumps(
            report.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
