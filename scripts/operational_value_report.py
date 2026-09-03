from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (SRC_ROOT, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from academy_tractian.operational_value import (  # noqa: E402
    OperationalValueObservation,
    build_operational_value_report,
    operational_value_metric_bundle,
)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate evaluator-side operational correctness and measured engineer-effort "
            "observations. This command never imputes missing effort and does not accept LOCKED_TEST."
        )
    )
    parser.add_argument("--observations", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--config-id")
    parser.add_argument("--metadata", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    raw = _load_json(args.observations)
    if not isinstance(raw, list):
        raise SystemExit("--observations must contain a JSON array")

    observations = [OperationalValueObservation.model_validate(item) for item in raw]
    report = build_operational_value_report(observations)
    _write_json(args.report, report.model_dump(mode="json"))

    if args.bundle is not None:
        if not args.config_id:
            raise SystemExit("--config-id is required when --bundle is supplied")
        metadata: dict[str, object] | None = None
        if args.metadata is not None:
            loaded_metadata = _load_json(args.metadata)
            if not isinstance(loaded_metadata, dict):
                raise SystemExit("--metadata must contain a JSON object")
            metadata = loaded_metadata
        bundle = operational_value_metric_bundle(
            config_id=args.config_id,
            observations=observations,
            metadata=metadata,
        )
        _write_json(args.bundle, bundle.model_dump(mode="json"))

    print(
        json.dumps(
            {
                "ticket_count": report.ticket_count,
                "source_splits": report.source_splits,
                "operational_conclusion_accuracy": report.operational_conclusion_accuracy,
                "escalation_correctness_rate": report.escalation_correctness_rate,
                "paired_effort_sample_count": report.paired_effort_sample_count,
                "effort_sample_coverage_rate": report.effort_sample_coverage_rate,
                "engineer_minutes_saved_per_ticket": report.engineer_minutes_saved_per_ticket,
                "hard_failure_counts": report.hard_failure_counts,
                "dataset_sha256": report.dataset_sha256,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
