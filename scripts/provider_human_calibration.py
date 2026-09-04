from __future__ import annotations

import argparse
import json
from pathlib import Path

from academy_tractian.provider_human_calibration import (
    ProviderHumanCalibrationProtocol,
    build_provider_human_calibration_protocol,
    derive_provider_human_calibration_evidence,
)
from academy_tractian.semantic_annotation_sources import SemanticAnnotationSourceManifest
from academy_tractian.semantic_human_calibration import (
    SemanticAnnotationManifest,
    SemanticHumanResolutionReport,
)


def _read_object(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return payload


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze the provider-human OCA computation protocol or derive candidate-specific "
            "hash-bound OCA evidence from completed held-out human calibration. Metrics are never "
            "accepted as CLI inputs."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    freeze = sub.add_parser(
        "freeze-protocol",
        help="Freeze the Wilson-95 operational-usefulness computation contract before outcomes.",
    )
    freeze.add_argument("--protocol-id", required=True)
    freeze.add_argument("--output", required=True, type=Path)

    derive = sub.add_parser(
        "derive",
        help="Derive candidate OCA from source/annotation/resolution artifacts.",
    )
    derive.add_argument("--candidate-id", required=True)
    derive.add_argument("--protocol", required=True, type=Path)
    derive.add_argument("--source-manifest", required=True, type=Path)
    derive.add_argument("--annotation-manifest", required=True, type=Path)
    derive.add_argument("--resolution-report", required=True, type=Path)
    derive.add_argument("--output", required=True, type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()

    if args.command == "freeze-protocol":
        protocol = build_provider_human_calibration_protocol(protocol_id=args.protocol_id)
        _write(args.output, protocol.model_dump(mode="json"))
        print(
            json.dumps(
                {
                    "status": "FROZEN",
                    "protocol_id": protocol.protocol_id,
                    "protocol_sha256": protocol.protocol_sha256,
                    "dimension": protocol.dimension,
                    "passing_score": protocol.passing_score,
                    "confidence_level": protocol.confidence_level,
                    "interval_method": protocol.interval_method,
                },
                sort_keys=True,
            )
        )
        return 0

    protocol = ProviderHumanCalibrationProtocol.model_validate(_read_object(args.protocol))
    source_manifest = SemanticAnnotationSourceManifest.model_validate(
        _read_object(args.source_manifest)
    )
    annotation_manifest = SemanticAnnotationManifest.model_validate(
        _read_object(args.annotation_manifest)
    )
    resolution_report = SemanticHumanResolutionReport.model_validate(
        _read_object(args.resolution_report)
    )
    artifact = derive_provider_human_calibration_evidence(
        candidate_id=args.candidate_id,
        protocol=protocol,
        source_manifest=source_manifest,
        annotation_manifest=annotation_manifest,
        resolution_report=resolution_report,
    )
    _write(args.output, artifact.model_dump(mode="json"))
    print(
        json.dumps(
            {
                "status": "DERIVED",
                "candidate_id": artifact.candidate_id,
                "config_hash": artifact.config_hash,
                "protocol_id": artifact.protocol_id,
                "protocol_hash": artifact.protocol_hash,
                "case_count": artifact.case_count,
                "human_agreement_rate": artifact.human_agreement_rate,
                "operational_conclusion_accuracy": artifact.operational_conclusion_accuracy,
                "operational_conclusion_accuracy_ci_low": artifact.operational_conclusion_accuracy_ci_low,
                "artifact_sha256": artifact.artifact_sha256,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
