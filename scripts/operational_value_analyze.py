from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (SRC_ROOT, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from academy_tractian.operational_value_analysis import (  # noqa: E402
    OperationalValueAnalysisProtocol,
    OperationalValueAnalysisResult,
    analyze_operational_value,
)
from academy_tractian.postgres_operational import PostgresOperationalDatabase  # noqa: E402
from academy_tractian.postgres_operational_value_analysis import (  # noqa: E402
    PostgresOperationalValueAnalysisStore,
)
from academy_tractian.postgres_operational_value_v5 import (  # noqa: E402
    PostgresOperationalPilotStoreV5,
)


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"required environment variable is missing: {name}")
    return value


def _load_protocol(path: Path) -> OperationalValueAnalysisProtocol:
    try:
        return OperationalValueAnalysisProtocol.model_validate_json(
            path.read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as exc:
        raise SystemExit(f"invalid frozen protocol: {path}: {exc}") from exc


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _aggregate_export(result: OperationalValueAnalysisResult) -> dict[str, object]:
    """Return the trusted aggregate artifact without participant-level timing rows."""

    payload = result.model_dump(mode="json", exclude={"paired_results"})
    payload["paired_result_count"] = len(result.paired_results)
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze/snapshot and analyze the blinded operational-value collection. "
            "PostgreSQL DSNs are read only from environment variables so credentials "
            "do not enter shell history. The output contains aggregate evidence only."
        )
    )
    parser.add_argument("--organization-id", required=True)
    parser.add_argument("--packet-id", required=True)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--schema", default="academy_operational")
    parser.add_argument(
        "--close",
        action="store_true",
        help=(
            "Irreversibly close collection for this packet before snapshotting. "
            "Fails if any assignment is ACTIVE."
        ),
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    protocol = _load_protocol(args.protocol)
    internal_dsn = _required_env("ACADEMY_POSTGRES_INTERNAL_DSN")
    scoped_dsn = _required_env("ACADEMY_POSTGRES_SCOPED_DSN")

    database = PostgresOperationalDatabase(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=args.schema,
        initialize=False,
    )
    try:
        pilot_store = PostgresOperationalPilotStoreV5(database, initialize=False)
        if not database.ready() or not pilot_store.ready():
            raise RuntimeError("postgres_operational_value_schema_not_ready")

        analysis_store = PostgresOperationalValueAnalysisStore(database)
        closed_task_count = 0
        if args.close:
            closed_task_count = analysis_store.close_packet(
                organization_id=args.organization_id,
                packet_id=args.packet_id,
            )
        snapshot = analysis_store.snapshot(
            organization_id=args.organization_id,
            packet_id=args.packet_id,
        )
        result = analyze_operational_value(snapshot=snapshot, protocol=protocol)
        export = _aggregate_export(result)
        export["closed_task_count_this_run"] = closed_task_count
        _write_json(args.output, export)
        print(
            json.dumps(
                {
                    "status": result.status,
                    "business_claim_ready": result.business_claim_ready,
                    "requires_operational_quality_gate": (
                        result.requires_operational_quality_gate
                    ),
                    "collection_closed": result.collection_closed,
                    "complete_pair_count": result.complete_pair_count,
                    "incomplete_pair_count": result.incomplete_pair_count,
                    "snapshot_sha256": result.snapshot_sha256,
                    "evidence_sha256": result.evidence_sha256,
                    "output": str(args.output),
                },
                sort_keys=True,
            )
        )
    finally:
        database.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
