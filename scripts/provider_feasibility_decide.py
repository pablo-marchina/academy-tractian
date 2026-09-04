from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from academy_tractian.provider_feasibility import (
    ProviderFeasibilityEvidence,
    ProviderFeasibilityPolicy,
    decide_provider_feasibility_set,
)


def _load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected_json_object:{path.name}")
    return payload


def _parse_datetime(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("evaluated_at_requires_timezone")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Apply non-compensatory hosted/zero-local/zero-cost/capacity gates before provider EDD. "
            "ELIGIBLE means only that a candidate may enter quality evaluation; it is not promotion."
        )
    )
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, action="append", required=True)
    parser.add_argument("--evaluated-at", type=_parse_datetime, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-all-eligible",
        action="store_true",
        help="Return exit code 2 when any supplied candidate is infeasible.",
    )
    args = parser.parse_args()

    policy = ProviderFeasibilityPolicy.model_validate(_load_object(args.policy))
    evidence = tuple(
        ProviderFeasibilityEvidence.model_validate(_load_object(path)) for path in args.evidence
    )
    decisions = decide_provider_feasibility_set(
        evidence=evidence,
        policy=policy,
        evaluated_at=args.evaluated_at,
    )
    payload = {
        "schema_version": "provider-feasibility-decision-set-v1",
        "evaluated_at": args.evaluated_at.isoformat(),
        "all_eligible": all(item.outcome == "ELIGIBLE" for item in decisions),
        "eligible_candidate_ids": [
            item.candidate_id for item in decisions if item.outcome == "ELIGIBLE"
        ],
        "ineligible_candidate_ids": [
            item.candidate_id for item in decisions if item.outcome == "INELIGIBLE"
        ],
        "decisions": [item.model_dump(mode="json") for item in decisions],
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.require_all_eligible and not payload["all_eligible"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
