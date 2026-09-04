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

from academy_tractian.semantic_calibration_freeze import (  # noqa: E402
    build_semantic_calibration_evidence_manifest,
)
from academy_tractian.semantic_human_calibration import (  # noqa: E402
    SemanticAnnotationManifest,
    SemanticAnnotationSource,
    SemanticHumanAdjudication,
    SemanticReviewerLabel,
    SemanticReviewerPacket,
    build_semantic_reviewer_packet,
    resolve_human_semantic_labels,
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
            "Prepare blind human semantic-review packets or resolve two-pass labels into "
            "adjudicated HumanSemanticReference records. No judge, threshold or human label is fabricated."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Build reviewer packet + evaluator-only manifest")
    prepare.add_argument("--sources", required=True, type=Path)
    prepare.add_argument("--split-manifest", required=True, type=Path)
    prepare.add_argument(
        "--purpose",
        required=True,
        choices=("PILOT", "HELD_OUT_CALIBRATION"),
    )
    prepare.add_argument("--shuffle-seed", type=int, default=20260903)
    prepare.add_argument("--minimum-distinct-groups", type=int, default=2)
    prepare.add_argument("--reviewer-packet", required=True, type=Path)
    prepare.add_argument("--annotation-manifest", required=True, type=Path)

    resolve = subparsers.add_parser("resolve", help="Resolve two independent review passes + adjudication")
    resolve.add_argument("--reviewer-packet", required=True, type=Path)
    resolve.add_argument("--annotation-manifest", required=True, type=Path)
    resolve.add_argument("--labels", required=True, type=Path)
    resolve.add_argument("--adjudications", type=Path)
    resolve.add_argument("--human-references", required=True, type=Path)
    resolve.add_argument("--resolution-report", required=True, type=Path)
    resolve.add_argument(
        "--calibration-evidence-manifest",
        type=Path,
        help=(
            "For a complete HELD_OUT_CALIBRATION packet, write the hash-bound VALIDATION "
            "evidence manifest required by the frozen v2 calibration gate."
        ),
    )
    resolve.add_argument("--require-complete", action="store_true")
    return parser


def _prepare(args: argparse.Namespace) -> None:
    sources = _load_list(args.sources, SemanticAnnotationSource)
    split_payload = _load_json(args.split_manifest)
    if not isinstance(split_payload, dict):
        raise SystemExit("split manifest must contain a JSON object")

    packet, manifest = build_semantic_reviewer_packet(
        sources=sources,
        frozen_split_payload=split_payload,
        purpose=args.purpose,
        deterministic_shuffle_seed=args.shuffle_seed,
        minimum_distinct_groups=args.minimum_distinct_groups,
    )
    _write_json(args.reviewer_packet, packet.model_dump(mode="json"))
    _write_json(args.annotation_manifest, manifest.model_dump(mode="json"))
    print(
        json.dumps(
            {
                "packet_id": packet.packet_id,
                "purpose": packet.purpose,
                "source_count": packet.source_count,
                "task_count": packet.task_count,
                "group_count": len(manifest.group_ids),
                "source_split": manifest.source_split,
                "rubric_sha256": packet.rubric_sha256,
            },
            sort_keys=True,
        )
    )


def _resolve(args: argparse.Namespace) -> None:
    packet = SemanticReviewerPacket.model_validate(_load_json(args.reviewer_packet))
    manifest = SemanticAnnotationManifest.model_validate(_load_json(args.annotation_manifest))
    labels = _load_list(args.labels, SemanticReviewerLabel)
    adjudications = []
    if args.adjudications is not None:
        adjudications = _load_list(args.adjudications, SemanticHumanAdjudication)

    report = resolve_human_semantic_labels(
        packet=packet,
        manifest=manifest,
        labels=labels,
        adjudications=adjudications,
    )
    _write_json(
        args.human_references,
        [reference.model_dump(mode="json") for reference in report.human_references],
    )
    _write_json(args.resolution_report, report.model_dump(mode="json"))

    evidence_manifest_sha256 = None
    if args.calibration_evidence_manifest is not None:
        evidence_manifest = build_semantic_calibration_evidence_manifest(
            packet=packet,
            annotation_manifest=manifest,
            resolution_report=report,
        )
        _write_json(
            args.calibration_evidence_manifest,
            evidence_manifest.model_dump(mode="json"),
        )
        evidence_manifest_sha256 = evidence_manifest.evidence_manifest_sha256

    print(
        json.dumps(
            {
                "packet_id": report.packet_id,
                "task_count": report.task_count,
                "resolved_count": report.resolved_count,
                "unresolved_count": len(report.unresolved_task_ids),
                "agreed_count": report.agreed_count,
                "adjudicated_count": report.adjudicated_count,
                "calibration_ready": report.calibration_ready,
                "calibration_evidence_manifest_sha256": evidence_manifest_sha256,
            },
            sort_keys=True,
        )
    )
    if args.require_complete and not report.calibration_ready:
        raise SystemExit(2)


def main() -> None:
    args = _parser().parse_args()
    if args.command == "prepare":
        _prepare(args)
    elif args.command == "resolve":
        _resolve(args)
    else:  # pragma: no cover - argparse enforces this
        raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    main()
