from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.final_freeze_bundle import (  # noqa: E402
    load_final_freeze_manifest,
    validate_final_freeze_manifest,
)
from academy_tractian.hard_freeze_readiness import (  # noqa: E402
    REQUIRED_STATUS_CONTEXT,
    HardFreezeReadinessObservation,
    evaluate_hard_freeze_readiness,
    extract_classic_required_status_contexts,
    extract_ruleset_required_status_contexts,
)


API_ROOT = "https://api.github.com"
FINAL_CI_WORKFLOW = "final-ci-required.yml"


def _request_payload(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "academy-tractian-hard-freeze-readiness",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310 - fixed GitHub API root
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"github_readiness_query_http_{exc.code}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("github_readiness_query_failed") from exc


def _request_json(url: str, token: str | None) -> dict[str, Any]:
    payload = _request_payload(url, token)
    if not isinstance(payload, dict):
        raise RuntimeError("github_readiness_query_non_object")
    return payload


def _request_list(url: str, token: str | None) -> list[dict[str, Any]]:
    payload = _request_payload(url, token)
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise RuntimeError("github_readiness_query_non_list")
    return payload


def _ruleset_details(encoded_repo: str, token: str) -> tuple[dict[str, Any], ...]:
    url = f"{API_ROOT}/repos/{encoded_repo}/rulesets?includes_parents=true"
    try:
        summaries = _request_list(url, token)
        effective_token: str | None = token
    except RuntimeError as exc:
        if str(exc) != "github_readiness_query_http_403":
            raise
        # Public repository ruleset metadata may be readable without auth even when
        # GITHUB_TOKEN lacks Administration(read). A second read-only attempt is safe.
        summaries = _request_list(url, None)
        effective_token = None

    details: list[dict[str, Any]] = []
    for summary in summaries:
        ruleset_id = summary.get("id")
        if not isinstance(ruleset_id, int) or ruleset_id <= 0:
            raise RuntimeError("github_ruleset_id_invalid")
        details.append(
            _request_json(
                f"{API_ROOT}/repos/{encoded_repo}/rulesets/{ruleset_id}?includes_parents=true",
                effective_token,
            )
        )
    return tuple(details)


def _select_final_ci_run(
    runs_payload: dict[str, Any], candidate_sha: str
) -> dict[str, Any] | None:
    runs = runs_payload.get("workflow_runs")
    if not isinstance(runs, list):
        return None
    matching = [
        item
        for item in runs
        if isinstance(item, dict) and item.get("head_sha") == candidate_sha
    ]
    if not matching:
        return None
    matching.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    return matching[0]


def _required_gate_conclusion(jobs_payload: dict[str, Any]) -> str | None:
    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list):
        return None
    for job in jobs:
        if isinstance(job, dict) and job.get("name") == REQUIRED_STATUS_CONTEXT:
            conclusion = job.get("conclusion")
            return conclusion if isinstance(conclusion, str) else None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed hard-freeze readiness check using sanitized GitHub metadata."
    )
    parser.add_argument("--repository", required=True, help="GitHub owner/repository")
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("HARD_FREEZE_READINESS=BLOCKED reason=github_token_missing")
        return 2

    repository = args.repository.strip()
    if repository.count("/") != 1:
        print("HARD_FREEZE_READINESS=BLOCKED reason=invalid_repository")
        return 2
    owner, repo = repository.split("/", 1)
    encoded_repo = f"{quote(owner, safe='')}/{quote(repo, safe='')}"

    try:
        branch_payload = _request_json(
            f"{API_ROOT}/repos/{encoded_repo}/branches/main",
            token,
        )
        workflow_runs = _request_json(
            f"{API_ROOT}/repos/{encoded_repo}/actions/workflows/"
            f"{FINAL_CI_WORKFLOW}/runs?branch=main&status=completed&per_page=30",
            token,
        )
    except RuntimeError as exc:
        print(f"HARD_FREEZE_READINESS=BLOCKED reason={exc}")
        return 2

    commit = branch_payload.get("commit")
    observed_main_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(observed_main_sha, str):
        print("HARD_FREEZE_READINESS=BLOCKED reason=main_sha_unavailable")
        return 2

    required_contexts = set(extract_classic_required_status_contexts(branch_payload))
    if branch_payload.get("protected") is True and REQUIRED_STATUS_CONTEXT not in required_contexts:
        try:
            required_contexts.update(
                extract_ruleset_required_status_contexts(
                    _ruleset_details(encoded_repo, token)
                )
            )
        except RuntimeError as exc:
            print(f"HARD_FREEZE_READINESS=BLOCKED reason={exc}")
            return 2

    selected_run = _select_final_ci_run(workflow_runs, args.candidate_sha)
    final_ci_run_id: int | None = None
    final_ci_head_sha: str | None = None
    final_ci_conclusion: str | None = None
    required_gate_conclusion: str | None = None

    if selected_run is not None:
        raw_run_id = selected_run.get("id")
        if isinstance(raw_run_id, int) and raw_run_id > 0:
            final_ci_run_id = raw_run_id
            final_ci_head_sha = (
                selected_run.get("head_sha")
                if isinstance(selected_run.get("head_sha"), str)
                else None
            )
            final_ci_conclusion = (
                selected_run.get("conclusion")
                if isinstance(selected_run.get("conclusion"), str)
                else None
            )
            try:
                jobs_payload = _request_json(
                    f"{API_ROOT}/repos/{encoded_repo}/actions/runs/{final_ci_run_id}/jobs",
                    token,
                )
            except RuntimeError as exc:
                print(f"HARD_FREEZE_READINESS=BLOCKED reason={exc}")
                return 2
            required_gate_conclusion = _required_gate_conclusion(jobs_payload)

    manifest = load_final_freeze_manifest(ROOT)
    bundle_failures = tuple(validate_final_freeze_manifest(manifest, ROOT))

    observation = HardFreezeReadinessObservation(
        candidate_sha=args.candidate_sha,
        observed_main_sha=observed_main_sha,
        observed_at_utc=datetime.now(timezone.utc),
        branch_protected=branch_payload.get("protected") is True,
        required_status_contexts=tuple(sorted(required_contexts)),
        final_ci_run_id=final_ci_run_id,
        final_ci_head_sha=final_ci_head_sha,
        final_ci_conclusion=final_ci_conclusion,
        required_gate_conclusion=required_gate_conclusion,
        bundle_manifest_sha256=manifest.manifest_sha256,
        bundle_validation_failures=bundle_failures,
    )
    report = evaluate_hard_freeze_readiness(observation)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    print(f"HARD_FREEZE_READINESS={report.status}")
    print(f"HARD_FREEZE_CANDIDATE_SHA={report.candidate_sha}")
    print(f"HARD_FREEZE_MAIN_SHA={report.observed_main_sha}")
    print(f"HARD_FREEZE_BRANCH_PROTECTED={str(report.branch_protected).lower()}")
    print(f"HARD_FREEZE_REQUIRED_GATE_REQUIRED={str(report.required_gate_required).lower()}")
    print(f"HARD_FREEZE_FINAL_CI_SUCCESS={str(report.final_ci_success).lower()}")
    print(f"HARD_FREEZE_REQUIRED_GATE_SUCCESS={str(report.required_gate_success).lower()}")
    print(f"HARD_FREEZE_BUNDLE_FAILURES={report.bundle_validation_failure_count}")
    print(f"HARD_FREEZE_BLOCKERS={','.join(report.blockers) if report.blockers else 'none'}")
    print(f"HARD_FREEZE_EVIDENCE_SHA256={report.evidence_sha256}")

    return 0 if report.status == "READY_FOR_ACTIVATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
