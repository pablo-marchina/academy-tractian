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
    FrozenSemanticCalibrationReport,
    SemanticCalibrationEvidenceManifest,
    SemanticCalibrationProtocol,
    calibrate_semantic_judge_frozen,
)
from academy_tractian.semantic_evaluation import (  # noqa: E402
    HumanSemanticReference,
    JudgeSemanticObservation,
    SemanticCalibrationAcceptancePolicy,
    SemanticCalibrationReport,
    calibrate_semantic_judge,
    semantic_rubric_v1,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Calibrate structured semantic-judge observations against adjudicated human references. "
            "Promotion authorization requires a frozen v2 protocol bound to held-out VALIDATION evidence."
        )
    )
    parser.add_argument("--human", required=True, type=Path)
    parser.add_argument("--judge", required=True, type=Path)
    gate = parser.add_mutually_exclusive_group()
    gate.add_argument(
        "--protocol",
        type=Path,
        help="Frozen semantic-calibration-protocol-v2 used by the promotion-authorizing path.",
    )
    gate.add_argument(
        "--policy",
        type=Path,
        help=(
            "Legacy semantic-calibration-policy-v1. It is evaluated for historical comparison "
            "but is forcibly DESCRIPTIVE_ONLY and cannot authorize promotion."
        ),
    )
    parser.add_argument(
        "--evidence-manifest",
        type=Path,
        help="Hash-bound HELD_OUT_CALIBRATION/VALIDATION evidence manifest required with --protocol.",
    )
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    parser.add_argument("--require-calibrated-gate", action="store_true")
    return parser


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_list(path: Path, model_type):
    payload = _load_json(path)
    if not isinstance(payload, list):
        raise SystemExit(f"{path} must contain a JSON array")
    return [model_type.model_validate(item) for item in payload]


def _fmt(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def _metrics_table(report: SemanticCalibrationReport) -> list[str]:
    lines = [
        "| Dimension | Expected | Valid | Exact | Adjacent | MAE | QWK | False pass | False fail | Invalid |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for metric in report.dimension_metrics:
        lines.append(
            "| "
            + " | ".join(
                [
                    metric.dimension,
                    str(metric.expected_observations),
                    str(metric.valid_pairs),
                    _fmt(metric.exact_agreement),
                    _fmt(metric.adjacent_agreement),
                    _fmt(metric.mean_absolute_error),
                    _fmt(metric.quadratic_weighted_kappa),
                    _fmt(metric.false_pass_rate),
                    _fmt(metric.false_fail_rate),
                    _fmt(metric.invalid_rate),
                ]
            )
            + " |"
        )
    return lines


def _markdown_legacy(report: SemanticCalibrationReport, *, legacy_policy_supplied: bool) -> str:
    lines = [
        "# Semantic evaluator calibration report",
        "",
        f"- state: **{report.state}**",
        f"- gate authorized: **{str(report.gate_authorized).lower()}**",
        "- gate path: `LEGACY_DESCRIPTIVE_ONLY`",
        f"- rubric: `{report.rubric_id}`",
        f"- rubric SHA-256: `{report.rubric_sha256}`",
        f"- dataset SHA-256: `{report.dataset_sha256}`",
        f"- judge ids: `{', '.join(report.judge_ids) if report.judge_ids else 'none'}`",
        f"- legacy policy evaluated: **{str(legacy_policy_supplied).lower()}**",
        "",
        *_metrics_table(report),
        "",
        "## Gate failures",
        "",
    ]
    if report.gate_failures:
        lines.extend(f"- `{failure}`" for failure in report.gate_failures)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Calibration integrity",
            "",
            f"- unresolved human keys: {len(report.unresolved_human_keys)}",
            f"- unmatched human keys: {len(report.unmatched_human_keys)}",
            f"- unmatched judge keys: {len(report.unmatched_judge_keys)}",
            "",
            "Legacy v1 policy results are descriptive only. Promotion authorization requires a "
            "`semantic-calibration-protocol-v2` frozen before held-out VALIDATION outcomes, plus "
            "its matching hash-bound evidence manifest.",
        ]
    )
    return "\n".join(lines) + "\n"


def _markdown_frozen(report: FrozenSemanticCalibrationReport) -> str:
    calibration = report.calibration
    lines = [
        "# Frozen semantic evaluator calibration report",
        "",
        f"- state: **{report.state}**",
        f"- gate authorized: **{str(report.gate_authorized).lower()}**",
        "- gate path: `FROZEN_HELD_OUT_VALIDATION_V2`",
        f"- protocol id: `{report.protocol_id}`",
        f"- protocol SHA-256: `{report.protocol_sha256}`",
        f"- evidence manifest SHA-256: `{report.evidence_manifest_sha256}`",
        f"- source split: `{report.source_split}`",
        f"- frozen split SHA-256: `{report.frozen_split_sha256}`",
        f"- rubric SHA-256: `{report.rubric_sha256}`",
        f"- dataset SHA-256: `{report.dataset_sha256}`",
        f"- evidence SHA-256: `{report.evidence_sha256}`",
        f"- judge ids: `{', '.join(report.judge_ids) if report.judge_ids else 'none'}`",
        "",
        *_metrics_table(calibration),
        "",
        "## Gate failures",
        "",
    ]
    if report.gate_failures:
        lines.extend(f"- `{failure}`" for failure in report.gate_failures)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Calibration integrity",
            "",
            f"- unresolved human keys: {len(calibration.unresolved_human_keys)}",
            f"- unmatched human keys: {len(calibration.unmatched_human_keys)}",
            f"- unmatched judge keys: {len(calibration.unmatched_judge_keys)}",
            "",
            "`CALIBRATED_GATE` is possible only when the preregistered protocol, held-out "
            "VALIDATION evidence manifest, human-reference key set, rubric and judge observations "
            "all bind and every frozen threshold passes.",
        ]
    )
    return "\n".join(lines) + "\n"


def _force_legacy_descriptive(report: SemanticCalibrationReport) -> SemanticCalibrationReport:
    failures = tuple(sorted(set(report.gate_failures) | {"LEGACY_V1_POLICY_NOT_GATE_AUTHORIZED"}))
    state = "NOT_CALIBRATED" if report.state == "NOT_CALIBRATED" else "DESCRIPTIVE_ONLY"
    return SemanticCalibrationReport.model_validate(
        {
            **report.model_dump(mode="json"),
            "state": state,
            "gate_authorized": False,
            "gate_failures": failures,
        }
    )


def main() -> None:
    args = _parser().parse_args()
    if (args.protocol is None) != (args.evidence_manifest is None):
        raise SystemExit("--protocol and --evidence-manifest must be supplied together")

    human = _load_list(args.human, HumanSemanticReference)
    judge = _load_list(args.judge, JudgeSemanticObservation)

    if args.protocol is not None:
        protocol = SemanticCalibrationProtocol.model_validate(_load_json(args.protocol))
        evidence_manifest = SemanticCalibrationEvidenceManifest.model_validate(
            _load_json(args.evidence_manifest)
        )
        frozen_report = calibrate_semantic_judge_frozen(
            human_references=human,
            judge_observations=judge,
            protocol=protocol,
            evidence_manifest=evidence_manifest,
        )
        output_payload = frozen_report.model_dump(mode="json")
        markdown = _markdown_frozen(frozen_report)
        state = frozen_report.state
        gate_authorized = frozen_report.gate_authorized
        summary = {
            "state": state,
            "gate_authorized": gate_authorized,
            "gate_path": "FROZEN_HELD_OUT_VALIDATION_V2",
            "protocol_id": frozen_report.protocol_id,
            "protocol_sha256": frozen_report.protocol_sha256,
            "evidence_manifest_sha256": frozen_report.evidence_manifest_sha256,
            "rubric_sha256": frozen_report.rubric_sha256,
            "dataset_sha256": frozen_report.dataset_sha256,
            "valid_pairs": frozen_report.valid_pairs,
            "gate_failures": list(frozen_report.gate_failures),
        }
    else:
        legacy_policy = None
        if args.policy is not None:
            legacy_policy = SemanticCalibrationAcceptancePolicy.model_validate(
                _load_json(args.policy)
            )
        legacy_report = calibrate_semantic_judge(
            human_references=human,
            judge_observations=judge,
            acceptance_policy=legacy_policy,
            rubric=semantic_rubric_v1(),
        )
        if legacy_policy is not None:
            legacy_report = _force_legacy_descriptive(legacy_report)
        output_payload = legacy_report.model_dump(mode="json")
        markdown = _markdown_legacy(
            legacy_report,
            legacy_policy_supplied=legacy_policy is not None,
        )
        state = legacy_report.state
        gate_authorized = False
        summary = {
            "state": state,
            "gate_authorized": False,
            "gate_path": "LEGACY_DESCRIPTIVE_ONLY",
            "rubric_sha256": legacy_report.rubric_sha256,
            "dataset_sha256": legacy_report.dataset_sha256,
            "valid_pairs": legacy_report.valid_pairs,
            "gate_failures": list(legacy_report.gate_failures),
        }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(
            output_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown, encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    if args.require_calibrated_gate and not gate_authorized:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
