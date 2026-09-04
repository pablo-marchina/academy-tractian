from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from academy_tractian.adaptive_stopping import (
    AdaptiveStoppingReplayCase,
    AdaptiveStoppingSelection,
    analyze_adaptive_stopping_experiment,
)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Trusted/offline DEV-only evaluator for observed evidence-stopping headroom. "
            "The output is aggregate diagnostic evidence and never authorizes a runtime policy change."
        )
    )
    parser.add_argument(
        "--bundle",
        type=Path,
        required=True,
        help="Trusted JSON containing frozen selection and evaluator-private replay cases.",
    )
    parser.add_argument(
        "--split-manifest",
        type=Path,
        required=True,
        help="Frozen benchmark split manifest. Only DEV scenarios are accepted.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination for aggregate diagnostic JSON. Raw traces/judgments are never copied.",
    )
    args = parser.parse_args()

    bundle = _load_json(args.bundle)
    if not isinstance(bundle, dict):
        raise ValueError("adaptive stopping bundle must be a JSON object")
    selection = AdaptiveStoppingSelection.model_validate(bundle.get("selection"))
    raw_cases = bundle.get("replay_cases")
    if not isinstance(raw_cases, list):
        raise ValueError("adaptive stopping bundle replay_cases must be a list")
    replay_cases = tuple(AdaptiveStoppingReplayCase.model_validate(item) for item in raw_cases)
    split_manifest = _load_json(args.split_manifest)
    if not isinstance(split_manifest, dict):
        raise ValueError("split manifest must be a JSON object")

    result = analyze_adaptive_stopping_experiment(
        selection=selection,
        replay_cases=replay_cases,
        frozen_split_payload=split_manifest,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
