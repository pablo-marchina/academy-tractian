#!/usr/bin/env python3
"""No-provider local readiness preflight for the single E14m-R1 replacement.

This script makes no network/provider call and reads no private oracle values
beyond validating that required local JSON files exist and parse. It verifies
that the frozen candidate/transport environment is exactly the preregistered
E14m-R1 configuration and refuses to proceed if the requested replacement
capture path already exists.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
R1_PATH = HERE / "e14m_r1_operational_replacement.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r1 = load_module("e14m_r1_for_local_preflight", R1_PATH)

EXPECTED_ENV = {
    "E8_ENABLE_GROQ": "1",
    "E8_CONFIRM_ZERO_COST": "1",
    "E8_GROQ_MODEL": "openai/gpt-oss-120b",
    "E8_MODEL_TEMPERATURE": "0",
    "E14_REASONING_EFFORT": "medium",
    "E14_REASONING_FORMAT": "hidden",
    "E14_RESPONSE_FORMAT_MODE": "json_schema_strict",
    "E14_MAX_COMPLETION_TOKENS": "4096",
    "E8_PROVIDER_MAX_ATTEMPTS": "5",
    "E8_PROVIDER_RETRY_BASE_SECONDS": "5",
    "E14_PROVIDER_MAX_RETRY_SLEEP_SECONDS": "90",
    "E14_PROVIDER_MAX_DOCUMENTED_RETRY_SECONDS": "180",
    "E8_BETWEEN_CALL_DELAY_SECONDS": "25",
    "E14M_ADJUDICATION_DELAY_SECONDS": "25",
    "E14F_REPAIR_DELAY_SECONDS": "25",
    "E14_MAX_RETRIES": "2",
}

REQUIRED_REPO_FILES = (
    Path("research/experiments/e14m-dev-only-public-decision-adjudication-manifest.json"),
    Path("research/experiments/e14m-operational-replacement-r1-amendment.json"),
    Path("research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json"),
    Path("research/frozen/benchmark-split-v1.json"),
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_env() -> list[str]:
    errors: list[str] = []
    for name, expected in EXPECTED_ENV.items():
        actual = os.getenv(name)
        if actual != expected:
            errors.append(f"{name}:expected={expected}:actual={'unset' if actual is None else actual}")
    if not os.getenv("GROQ_API_KEY"):
        errors.append("GROQ_API_KEY:missing")
    return errors


def run(private_root: Path, capture_out: Path) -> dict[str, Any]:
    # Self-checks are structural only and make no provider call.
    r1.run_self_checks()

    env_errors = _validate_env()
    repo_files_valid = True
    for path in REQUIRED_REPO_FILES:
        try:
            _load_json(path)
        except Exception:
            repo_files_valid = False

    cases = private_root / "agent-input" / "cases.json"
    oracle = private_root / "eval" / "expected-paths.json"
    private_files_valid = True
    for path in (cases, oracle):
        try:
            _load_json(path)
        except Exception:
            private_files_valid = False

    capture_path_available = not capture_out.exists()
    amendment = _load_json(Path("research/experiments/e14m-operational-replacement-r1-amendment.json"))
    replacement_rule = amendment.get("replacement_rule", {}) if isinstance(amendment, dict) else {}
    replacement_rule_valid = (
        amendment.get("amendment_id") == "E14m-R1"
        and replacement_rule.get("replacement_captures_allowed") == 1
        and replacement_rule.get("same_candidate_required") is True
        and replacement_rule.get("if_replacement_is_incomplete") == "STOP_E14M_NO_THIRD_REAL_CAPTURE"
    )

    passed = (
        not env_errors
        and repo_files_valid
        and private_files_valid
        and capture_path_available
        and replacement_rule_valid
    )
    return {
        "status": "E14M_R1_LOCAL_PREFLIGHT_PASS" if passed else "E14M_R1_LOCAL_PREFLIGHT_NEEDS_REVIEW",
        "provider_call_made": False,
        "private_oracle_values_printed": False,
        "api_key_printed": False,
        "frozen_environment_pass": not env_errors,
        "environment_error_count": len(env_errors),
        "environment_errors": env_errors,
        "repo_json_files_valid": repo_files_valid,
        "private_required_json_files_valid": private_files_valid,
        "replacement_capture_path_available": capture_path_available,
        "replacement_rule_valid": replacement_rule_valid,
        "replacement_capture_index": 1,
        "replacement_captures_allowed": 1,
        "validation_used": False,
        "locked_test_used": False,
        "safe_to_run_only_after_operator_confirms_long_window_quota_restored": passed,
    }


def run_self_check() -> None:
    saved = {name: os.environ.get(name) for name in (*EXPECTED_ENV.keys(), "GROQ_API_KEY")}
    try:
        os.environ.update(EXPECTED_ENV)
        os.environ["GROQ_API_KEY"] = "self-check-placeholder-never-used"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "agent-input").mkdir(parents=True)
            (root / "eval").mkdir(parents=True)
            (root / "agent-input" / "cases.json").write_text("{}", encoding="utf-8")
            (root / "eval" / "expected-paths.json").write_text("[]", encoding="utf-8")
            result = run(root, root / "replacement.json")
            if result.get("status") != "E14M_R1_LOCAL_PREFLIGHT_PASS":
                raise AssertionError("E14m-R1 local preflight positive self-check failed")
            occupied = root / "occupied.json"
            occupied.write_text("{}", encoding="utf-8")
            blocked = run(root, occupied)
            if blocked.get("replacement_capture_path_available") is not False:
                raise AssertionError("preflight must refuse an existing replacement capture path")
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path)
    parser.add_argument("--capture-out", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        run_self_check()
        print("E14M_R1_LOCAL_PREFLIGHT_SELF_CHECK_PASS")
        return 0
    if args.private_root is None or args.capture_out is None:
        parser.error("--private-root and --capture-out are required unless --self-check is used")

    result = run(args.private_root, args.capture_out)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "E14M_R1_LOCAL_PREFLIGHT_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
