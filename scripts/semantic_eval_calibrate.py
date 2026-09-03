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
            "No implicit acceptance thresholds are provided."
        )
    )
    parser.add_argument("--human", required=True, type=Path)
    parser.add_argument("--judge", required=True, type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    parser.add_argument("--require-calibrated-gate", action="store_true")
    return parser


def _load_list(path: Path, model_type):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit(f"{path} must contain a JSON array")
    return [model_type.model_validate(item) for item in payload]


def _fmt(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def _markdown(report: SemanticCalibrationReport) -> str:
    lines = [
        "# Semantic evaluator calibration report",
        "",
        f"- state: **{report.state}**",
        f"- gate authorized: **{str(report.gate_authorized).lower()}**",
        f"- rubric: `{report.rubric_id}`",
        f"- rubric SHA-256: `{report.rubric_sha256}`",
        f"- dataset SHA-256: `{report.dataset_sha256}`",
        f"- judge ids: `{', '.join(report.judge_ids) if report.judge_ids else 'none'}`",
        f"- acceptance policy: `{report.acceptance_policy_id or 'none'}`",
        "",
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
    lines.extend(["", "## Gate failures", ""])
    if report.gate_failures:
        lines.extend(f"- `{failure}`" for failure in report.gate_failures)
    else:
        lines.append("- none")
    lines.extend(["", "## Calibration integrity", ""])
    lines.append(f"- unresolved human keys: {len(report.unresolved_human_keys)}")
    lines.append(f"- unmatched human keys: {len(report.unmatched_human_keys)}")
    lines.append(f"- unmatched judge keys: {len(report.unmatched_judge_keys)}")
    lines.append("")
    lines.append(
        "`DESCRIPTIVE_ONLY` is intentionally non-gating. A semantic evaluator may affect promotion "
        "only when an explicit preregistered policy exists and the report reaches `CALIBRATED_GATE`."
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = _parser().parse_args()
    human = _load_list(args.human, HumanSemanticReference)
    judge = _load_list(args.judge, JudgeSemanticObservation)
    policy = None
    if args.policy is not None:
        policy = SemanticCalibrationAcceptancePolicy.model_validate(
            json.loads(args.policy.read_text(encoding="utf-8"))
        )

    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
        acceptance_policy=policy,
        rubric=semantic_rubric_v1(),
    )

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(
            report.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "state": report.state,
                "gate_authorized": report.gate_authorized,
                "rubric_sha256": report.rubric_sha256,
                "dataset_sha256": report.dataset_sha256,
                "valid_pairs": report.valid_pairs,
                "gate_failures": list(report.gate_failures),
            },
            sort_keys=True,
        )
    )
    if args.require_calibrated_gate and not report.gate_authorized:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
