#!/usr/bin/env python3
"""Provider-free validator for the bounded production live-comparison authorization packet."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AUTH_PATH = ROOT / "research/frozen/provider-model-live-comparison-authorization-v1.json"
DESIGN_PATH = ROOT / "research/experiments/provider-model-comparison-design-manifest-v1.json"
POPULATION_PATH = ROOT / "research/experiments/provider-model-comparison-dev-population-v1.json"
PROVIDER_CLIENTS_PATH = ROOT / "src/academy_tractian/provider_clients.py"
PROVIDER_CLIENT_TESTS_PATH = ROOT / "tests/test_provider_clients.py"
PACKAGE_EXPORTS_PATH = ROOT / "src/academy_tractian/__init__.py"
DECISION_SOURCE_PATH = ROOT / "src/academy_tractian/decision_source.py"

EXPECTED_AUTH_BLOB = "5690414564ccddb07184c333fdf79f4ee2fb7788"
EXPECTED_DESIGN_BLOB = "9c3d0901414445bd4de557d5ef1d2f68a15c883b"
EXPECTED_POPULATION_BLOB = "abd6a7d973a8779f425c3607d963e29f15db09e5"
EXPECTED_POPULATION_SHA256 = "561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251"
EXPECTED_PROVIDER_CLIENTS_BLOB = "e78807bdfd4fd0ca9840fa2d9e6c62474237ee45"
EXPECTED_PROVIDER_CLIENT_TESTS_BLOB = "16d4165b966ae47f1117fa72f87e35b0522a64ac"
EXPECTED_PACKAGE_EXPORTS_BLOB = "2868fe2bf73bd89d6cc0a6f49a9a096cf5d5bcd1"
EXPECTED_DECISION_SOURCE_BLOB = "5579cf6f4c6bfe25d50220fa8b9ddf75c95d100a"
EXPECTED_VALIDATED_IMPLEMENTATION_HEAD = "3b823c498811a138de60acd65b280cef5dfd2bb1"

EXPECTED_CANDIDATES = {
    (
        "openai_gpt_5_6_sol_responses_standard",
        "openai",
        "gpt-5.6-sol",
        "openai.responses.v1.standard",
        "https://api.openai.com/v1/responses",
        "OpenAIResponsesDecisionClient",
    ),
    (
        "google_gemini_3_7_flash_interactions_stateless",
        "google",
        "gemini-3.7-flash",
        "google.interactions.v1beta.stateless",
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        "GoogleInteractionsDecisionClient",
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return payload


def git_blob(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "hash-object", relative],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _method(tree: ast.AST, class_name: str, method_name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == method_name:
                    return child
    raise AssertionError(f"missing method {class_name}.{method_name}")


def validate_client_source(source: str) -> None:
    forbidden_fragments = (
        "import os",
        "from os",
        "os.getenv",
        "os.environ",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "import openai",
        "from openai",
        "from google",
        "import google",
        "langgraph",
        "pydantic_ai",
        "FRESH_BLIND",
        "LEGACY_LOCKED_TEST",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source, f"forbidden provider-client source fragment: {fragment}"

    tree = ast.parse(source)
    for class_name in ("OpenAIResponsesDecisionClient", "GoogleInteractionsDecisionClient"):
        complete = _method(tree, class_name, "complete")
        invoke_calls = [
            node
            for node in ast.walk(complete)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_invoke_once"
        ]
        assert len(invoke_calls) == 1, f"{class_name}.complete must invoke transport boundary exactly once"
        assert not any(isinstance(node, (ast.For, ast.While, ast.AsyncFor)) for node in ast.walk(complete))

    invoke_once = _method(tree, "_BaseProviderDecisionClient", "_invoke_once")
    transport_calls = [
        node
        for node in ast.walk(invoke_once)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "post_json"
    ]
    assert len(transport_calls) == 1
    assert not any(isinstance(node, (ast.For, ast.While, ast.AsyncFor)) for node in ast.walk(invoke_once))

    urllib_transport = _method(tree, "UrllibProviderJsonTransport", "post_json")
    assert not any(isinstance(node, (ast.For, ast.While, ast.AsyncFor)) for node in ast.walk(urllib_transport))

    required_literals = (
        'OPENAI_MODEL_ID = "gpt-5.6-sol"',
        'OPENAI_ROUTE_ID = "openai.responses.v1.standard"',
        'OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"',
        'GOOGLE_MODEL_ID = "gemini-3.7-flash"',
        'GOOGLE_ROUTE_ID = "google.interactions.v1beta.stateless"',
        'GOOGLE_INTERACTIONS_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"',
        '"store": False',
        '"thinking_level": "medium"',
        '"thinking_summaries": "none"',
        '"tool_choice": "none"',
    )
    for literal in required_literals:
        assert literal in source, f"missing frozen provider-client literal: {literal}"


def validate_payload(
    authorization: dict[str, Any],
    design: dict[str, Any],
    population: dict[str, Any],
) -> None:
    assert authorization["schema_version"] == "provider-model-live-comparison-authorization-v1"
    assert authorization["status"] == "AUTHORIZATION_PACKET_CANDIDATE_INEFFECTIVE_UNTIL_ADR_009"
    assert authorization["issue"] == 35
    assert authorization["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"
    assert authorization["scientific_state_changed"] is False
    assert authorization["scientific_provider_calls_authorized_now"] == 0
    assert authorization["production_live_calls_executed_by_issue_35"] == 0
    assert authorization["production_provider_model_selected"] is False
    assert authorization["production_mutating_actions_enabled"] is False

    effect = authorization["becomes_effective_only_when"]
    assert effect["adr_path"] == "docs/adr/009-provider-http-clients-live-comparison-authorization-2026-08-28.md"
    assert effect["adr_status"] == "ACCEPTED"
    assert effect["exact_final_head_provider_free_revalidated"] is True

    frozen = authorization["frozen_design"]
    assert frozen["manifest_git_blob"] == EXPECTED_DESIGN_BLOB
    assert frozen["population_git_blob"] == EXPECTED_POPULATION_BLOB
    assert frozen["population_sha256"] == EXPECTED_POPULATION_SHA256
    assert frozen["unit_count"] == 8
    assert frozen["repetitions_per_live_candidate"] == 2
    assert frozen["selection_rule_includes_no_selection"] is True

    impl = authorization["validated_provider_client_implementation"]
    assert impl["head"] == EXPECTED_VALIDATED_IMPLEMENTATION_HEAD
    assert impl["provider_clients_git_blob"] == EXPECTED_PROVIDER_CLIENTS_BLOB
    assert impl["provider_client_tests_git_blob"] == EXPECTED_PROVIDER_CLIENT_TESTS_BLOB
    assert impl["package_exports_git_blob"] == EXPECTED_PACKAGE_EXPORTS_BLOB
    assert impl["provider_neutral_adapter_git_blob"] == EXPECTED_DECISION_SOURCE_BLOB
    assert impl["production_runtime_ci"]["run_id"] == 33140957622
    assert impl["production_runtime_ci"]["run_number"] == 23
    assert impl["production_runtime_ci"]["conclusion"] == "success"
    assert impl["triggered_workflows"] == {"total": 11, "success": 11}
    assert impl["preserved_failed_attempt"]["head"] == "b0a5bc8c2dbea0041ac0324e6471b09b9e68b644"
    assert impl["preserved_failed_attempt"]["production_runtime_run_id"] == 33140883236

    candidates = {
        (
            item["candidate_id"],
            item["provider_id"],
            item["model_id"],
            item["route_id"],
            item["endpoint"],
            item["client_class"],
        )
        for item in authorization["live_candidates"]
    }
    assert candidates == EXPECTED_CANDIDATES
    assert all(item["automatic_retries"] == 0 for item in authorization["live_candidates"])
    assert all(item["fallbacks"] == 0 for item in authorization["live_candidates"])
    assert all(item["store"] is False for item in authorization["live_candidates"])

    execution = authorization["authorization"]
    assert execution["scope"] == "SEPARATE_GOVERNED_EXECUTION_TASK_ONLY"
    assert execution["live_candidates"] == 2
    assert execution["units"] == 8
    assert execution["repetitions_per_unit_per_candidate"] == 2
    assert execution["max_live_provider_calls_total"] == 32
    assert execution["max_live_provider_calls_total"] == (
        execution["live_candidates"] * execution["units"] * execution["repetitions_per_unit_per_candidate"]
    )
    assert execution["warmup_calls"] == 0
    assert execution["automatic_retries"] == 0
    assert execution["provider_fallbacks"] == 0
    assert execution["parallel_live_calls"] is False
    assert execution["provider_seed_forwarded"] is False
    assert execution["provider_side_conversation_state"] is False
    assert execution["provider_native_tractian_tool_execution"] is False
    assert execution["production_actions_enabled"] is False
    assert execution["semantic_judge_authorized"] is False
    assert execution["fresh_blind_authorized"] is False
    assert execution["legacy_locked_test_authorized"] is False
    assert execution["candidate_or_threshold_changes_after_first_call"] is False

    hard = authorization["hard_gates"]
    assert hard["private_or_binding_leakage_violations_required"] == 0
    assert hard["unauthorized_action_transport_required"] == 0
    assert hard["hidden_retry_fallback_warmup_required"] == 0
    assert hard["model_call_provenance_valid_rate_required"] == 1.0
    assert hard["controller_harnessrunner_b1_b2_ownership_preserved"] is True
    assert hard["raw_request_response_exception_recording_required"] is False
    assert hard["route_or_model_change_allowed"] is False

    metrics = authorization["metrics"]
    assert metrics["source"] == "ADR-008 M1-M10 unchanged"
    assert metrics["operational_failures_remain_in_denominators"] is True
    assert metrics["post_result_threshold_changes_forbidden"] is True

    stopping = authorization["stopping_rules"]
    assert stopping["stop_on_custody_or_provenance_violation"] is True
    assert stopping["stop_on_route_or_model_change"] is True
    assert stopping["stop_if_hidden_repair_retry_or_fallback_would_be_required"] is True
    assert stopping["stop_at_call_budget"] == 32
    assert stopping["incomplete_packet_selection"] == "NO_SELECTION"

    non_auth = authorization["non_authorizations"]
    assert all(value is False for value in non_auth.values())

    assert design["schema_version"] == "provider-model-comparison-design-v1"
    assert design["scientific_gate"] == authorization["scientific_gate"]
    assert design["execution"]["max_live_provider_calls_total"] == 32
    assert design["execution"]["warmup_calls"] == 0
    assert design["execution"]["automatic_retries"] == 0
    assert design["execution"]["provider_fallbacks"] == 0
    assert design["execution"]["parallel_live_calls"] is False
    assert design["execution"]["provider_seed_forwarded"] is False
    assert "NO_SELECTION" in design["selection_rule"]["allowed_outcomes"]
    assert design["selection_rule"]["post_result_threshold_changes_forbidden"] is True
    assert set(design["metrics"]) == {f"M{i}" for i in range(1, 11)}

    assert population["schema_version"] == "provider-model-comparison-dev-population-v1"
    assert population["status"] == "PROSPECTIVE_PUBLIC_DEV_ONLY"
    assert population["unit_count"] == 8
    assert population["repetitions_per_live_candidate"] == 2
    boundaries = population["boundaries"]
    assert boundaries["uses_private_oracle"] is False
    assert boundaries["uses_expected_paths"] is False
    assert boundaries["uses_validation"] is False
    assert boundaries["uses_locked_test"] is False
    assert boundaries["uses_fresh_blind"] is False
    assert boundaries["uses_historical_real_task_quality"] is False


def validate_files() -> None:
    expected = {
        AUTH_PATH: EXPECTED_AUTH_BLOB,
        DESIGN_PATH: EXPECTED_DESIGN_BLOB,
        POPULATION_PATH: EXPECTED_POPULATION_BLOB,
        PROVIDER_CLIENTS_PATH: EXPECTED_PROVIDER_CLIENTS_BLOB,
        PROVIDER_CLIENT_TESTS_PATH: EXPECTED_PROVIDER_CLIENT_TESTS_BLOB,
        PACKAGE_EXPORTS_PATH: EXPECTED_PACKAGE_EXPORTS_BLOB,
        DECISION_SOURCE_PATH: EXPECTED_DECISION_SOURCE_BLOB,
    }
    for path, expected_blob in expected.items():
        actual = git_blob(path)
        assert actual == expected_blob, f"git blob mismatch for {path.relative_to(ROOT)}: {actual}"
    assert sha256_file(POPULATION_PATH) == EXPECTED_POPULATION_SHA256
    validate_client_source(PROVIDER_CLIENTS_PATH.read_text(encoding="utf-8"))


def run() -> dict[str, Any]:
    authorization = load_json(AUTH_PATH)
    design = load_json(DESIGN_PATH)
    population = load_json(POPULATION_PATH)
    validate_payload(authorization, design, population)
    validate_files()
    return {
        "status": "PASS_PROVIDER_FREE_LIVE_AUTHORIZATION_PACKET",
        "authorization_packet_git_blob": EXPECTED_AUTH_BLOB,
        "validated_provider_client_head": EXPECTED_VALIDATED_IMPLEMENTATION_HEAD,
        "max_future_live_calls": 32,
        "live_calls_executed": 0,
        "provider_model_selected": False,
        "scientific_gate_changed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
