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

from academy_tractian.postgres_operational import PostgresOperationalDatabase  # noqa: E402
from academy_tractian.postgres_semantic_review import PostgresSemanticReviewStore  # noqa: E402
from academy_tractian.semantic_human_calibration import (  # noqa: E402
    SemanticAnnotationManifest,
    SemanticReviewerPacket,
    resolve_human_semantic_labels,
)


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"required environment variable is missing: {name}")
    return value


def _load(path: Path, model_type):
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"invalid {path}: {exc}") from exc


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Trusted semantic-review collection administration. PostgreSQL credentials are read "
            "only from ACADEMY_POSTGRES_INTERNAL_DSN and ACADEMY_POSTGRES_SCOPED_DSN."
        )
    )
    parser.add_argument("--schema", default="academy_operational")
    sub = parser.add_subparsers(dest="command", required=True)

    register = sub.add_parser("register", help="Register a held-out VALIDATION reviewer packet")
    register.add_argument("--organization-id", required=True)
    register.add_argument("--reviewer-packet", required=True, type=Path)
    register.add_argument("--annotation-manifest", required=True, type=Path)

    export = sub.add_parser("export", help="Export evaluator-private completed labels/adjudications")
    export.add_argument("--organization-id", required=True)
    export.add_argument("--packet-id", required=True)
    export.add_argument("--labels-output", required=True, type=Path)
    export.add_argument("--adjudications-output", required=True, type=Path)
    export.add_argument("--reviewer-packet", type=Path)
    export.add_argument("--annotation-manifest", type=Path)
    export.add_argument("--resolution-output", type=Path)
    export.add_argument("--require-complete", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    internal_dsn = _required_env("ACADEMY_POSTGRES_INTERNAL_DSN")
    scoped_dsn = _required_env("ACADEMY_POSTGRES_SCOPED_DSN")
    database = PostgresOperationalDatabase(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=args.schema,
        initialize=False,
    )
    try:
        store = PostgresSemanticReviewStore(database, initialize=False)
        if not database.ready() or not store.ready():
            raise RuntimeError("postgres_semantic_review_schema_not_ready")

        if args.command == "register":
            packet = _load(args.reviewer_packet, SemanticReviewerPacket)
            manifest = _load(args.annotation_manifest, SemanticAnnotationManifest)
            store.register_packet(
                organization_id=args.organization_id,
                packet=packet,
                manifest=manifest,
            )
            print(
                json.dumps(
                    {
                        "status": "REGISTERED",
                        "organization_id": args.organization_id,
                        "packet_id": packet.packet_id,
                        "task_count": packet.task_count,
                        "purpose": packet.purpose,
                        "source_split": manifest.source_split,
                        "rubric_sha256": packet.rubric_sha256,
                        "frozen_split_sha256": manifest.frozen_split_sha256,
                    },
                    sort_keys=True,
                )
            )
            return 0

        labels, adjudications = store.export_resolution_inputs(
            organization_id=args.organization_id,
            packet_id=args.packet_id,
        )
        _write(args.labels_output, [item.model_dump(mode="json") for item in labels])
        _write(
            args.adjudications_output,
            [item.model_dump(mode="json") for item in adjudications],
        )

        calibration_ready = None
        unresolved_count = None
        if any(
            value is not None
            for value in (args.reviewer_packet, args.annotation_manifest, args.resolution_output)
        ):
            if not all(
                value is not None
                for value in (args.reviewer_packet, args.annotation_manifest, args.resolution_output)
            ):
                raise SystemExit(
                    "--reviewer-packet, --annotation-manifest and --resolution-output must be supplied together"
                )
            packet = _load(args.reviewer_packet, SemanticReviewerPacket)
            manifest = _load(args.annotation_manifest, SemanticAnnotationManifest)
            if packet.packet_id != args.packet_id:
                raise SystemExit("export packet id does not match reviewer packet")
            resolution = resolve_human_semantic_labels(
                packet=packet,
                manifest=manifest,
                labels=labels,
                adjudications=adjudications,
            )
            _write(args.resolution_output, resolution.model_dump(mode="json"))
            calibration_ready = resolution.calibration_ready
            unresolved_count = len(resolution.unresolved_task_ids)
            if args.require_complete and not resolution.calibration_ready:
                print(
                    json.dumps(
                        {
                            "status": "INCOMPLETE",
                            "packet_id": args.packet_id,
                            "label_count": len(labels),
                            "adjudication_count": len(adjudications),
                            "unresolved_count": unresolved_count,
                            "calibration_ready": False,
                        },
                        sort_keys=True,
                    )
                )
                return 2
        elif args.require_complete:
            raise SystemExit(
                "--require-complete requires reviewer packet, annotation manifest and resolution output"
            )

        print(
            json.dumps(
                {
                    "status": "EXPORTED",
                    "packet_id": args.packet_id,
                    "label_count": len(labels),
                    "adjudication_count": len(adjudications),
                    "unresolved_count": unresolved_count,
                    "calibration_ready": calibration_ready,
                },
                sort_keys=True,
            )
        )
        return 0
    finally:
        database.close()


if __name__ == "__main__":
    raise SystemExit(main())
