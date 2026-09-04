from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from academy_tractian.provider_promotion import (
    ProviderBenchmarkEvidence,
    ProviderPromotionPolicy,
    decide_provider_promotion,
)


def _load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected_json_object:{path.name}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Apply the fail-closed provider/model promotion gate to frozen EDD reports. "
            "NO_SELECTION is a valid scientific outcome."
        )
    )
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-promote",
        action="store_true",
        help="Return exit code 2 when the evidence does not justify a unique promotion.",
    )
    args = parser.parse_args()

    evidence = ProviderBenchmarkEvidence.model_validate(_load_object(args.evidence))
    policy = ProviderPromotionPolicy.model_validate(_load_object(args.policy))
    decision = decide_provider_promotion(evidence=evidence, policy=policy)
    rendered = json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.require_promote and decision.outcome != "PROMOTE":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
