from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from academy_tractian.deployment_feasibility import (
    DeploymentFeasibilityEvidence,
    DeploymentFeasibilityPolicy,
    decide_deployment_feasibility_set,
)


def _load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected_json_object:{path.name}")
    return payload


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("evaluated_at_requires_timezone")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Apply fail-closed hosted backend pilot-admission gates. PILOT_ADMISSIBLE authorizes "
            "only a controlled deployment experiment; it is not a production-host promotion."
        )
    )
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, action="append", required=True)
    parser.add_argument("--evaluated-at", type=_parse_datetime, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-candidate",
        help="Return exit code 2 unless this exact candidate is PILOT_ADMISSIBLE.",
    )
    args = parser.parse_args()

    policy = DeploymentFeasibilityPolicy.model_validate(_load_object(args.policy))
    evidence = tuple(
        DeploymentFeasibilityEvidence.model_validate(_load_object(path))
        for path in args.evidence
    )
    decisions = decide_deployment_feasibility_set(
        evidence=evidence,
        policy=policy,
        evaluated_at=args.evaluated_at,
    )
    admissible = tuple(
        item.candidate_id for item in decisions if item.outcome == "PILOT_ADMISSIBLE"
    )
    payload = {
        "schema_version": "deployment-feasibility-decision-set-v1",
        "evaluated_at": args.evaluated_at.isoformat(),
        "pilot_admissible_candidate_ids": list(admissible),
        "decisions": [item.model_dump(mode="json") for item in decisions],
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.require_candidate and args.require_candidate not in admissible:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
