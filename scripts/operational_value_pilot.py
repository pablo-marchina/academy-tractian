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

from academy_tractian.operational_value_pilot import (  # noqa: E402
    OperationalPilotCompletion,
    OperationalPilotManifest,
    OperationalPilotPacket,
    OperationalPilotSource,
    build_operational_pilot_packet,
    resolve_operational_pilot,
)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_list(path: Path, model_type):
    payload = _load_json(path)
    if not isinstance(payload, list):
        raise SystemExit(f"{path} must contain a JSON array")
    return [model_type.model_validate(item) for item in payload]


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare or resolve the blinded DEV operational-value pilot. "
            "Gold/private truth is never consumed by this CLI."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--sources", required=True, type=Path)
    prepare.add_argument("--split-manifest", required=True, type=Path)
    prepare.add_argument("--protocol-id", required=True)
    prepare.add_argument("--shuffle-seed", type=int, default=20260903)
    prepare.add_argument("--minimum-distinct-groups", type=int, default=2)
    prepare.add_argument("--operator-packet", required=True, type=Path)
    prepare.add_argument("--evaluator-manifest", required=True, type=Path)

    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("--operator-packet", required=True, type=Path)
    resolve.add_argument("--evaluator-manifest", required=True, type=Path)
    resolve.add_argument("--completions", required=True, type=Path)
    resolve.add_argument("--effort-pairs", required=True, type=Path)
    resolve.add_argument("--resolution-report", required=True, type=Path)
    resolve.add_argument("--require-complete", action="store_true")
    return parser


def _prepare(args: argparse.Namespace) -> int:
    sources = _load_list(args.sources, OperationalPilotSource)
    split_manifest = _load_json(args.split_manifest)
    if not isinstance(split_manifest, dict):
        raise SystemExit("--split-manifest must contain a JSON object")

    packet, manifest = build_operational_pilot_packet(
        sources=sources,
        frozen_split_payload=split_manifest,
        protocol_id=args.protocol_id,
        deterministic_shuffle_seed=args.shuffle_seed,
        minimum_distinct_groups=args.minimum_distinct_groups,
    )
    _write_json(args.operator_packet, packet.model_dump(mode="json"))
    _write_json(args.evaluator_manifest, manifest.model_dump(mode="json"))
    print(
        json.dumps(
            {
                "packet_id": packet.packet_id,
                "protocol_id": packet.protocol_id,
                "measurement_design": packet.measurement_design,
                "source_count": packet.source_count,
                "task_count": packet.task_count,
                "group_count": len(manifest.group_ids),
                "pair_count": len(manifest.pair_ids),
                "frozen_split_sha256": manifest.frozen_split_sha256,
            },
            sort_keys=True,
        )
    )
    return 0


def _resolve(args: argparse.Namespace) -> int:
    packet = OperationalPilotPacket.model_validate(_load_json(args.operator_packet))
    manifest = OperationalPilotManifest.model_validate(_load_json(args.evaluator_manifest))
    completions = _load_list(args.completions, OperationalPilotCompletion)

    report = resolve_operational_pilot(
        packet=packet,
        manifest=manifest,
        completions=completions,
    )
    _write_json(
        args.effort_pairs,
        [pair.model_dump(mode="json") for pair in report.effort_pairs],
    )
    _write_json(args.resolution_report, report.model_dump(mode="json"))
    print(
        json.dumps(
            {
                "packet_id": report.packet_id,
                "protocol_id": report.protocol_id,
                "pair_count": report.pair_count,
                "resolved_pair_count": report.resolved_pair_count,
                "unresolved_pair_count": len(report.unresolved_pair_ids),
                "invalid_task_count": len(report.invalid_task_ids),
                "missing_task_count": len(report.missing_task_ids),
                "duplicate_task_count": len(report.duplicate_task_ids),
                "resolution_ready": report.resolution_ready,
            },
            sort_keys=True,
        )
    )
    if args.require_complete and not report.resolution_ready:
        return 2
    return 0


def main() -> int:
    args = _parser().parse_args()
    if args.command == "prepare":
        return _prepare(args)
    return _resolve(args)


if __name__ == "__main__":
    raise SystemExit(main())
