from __future__ import annotations

import argparse
import json
from pathlib import Path

from academy_tractian.eval_driven import (
    EvalMetricBundle,
    EvalMetricRule,
    compare_eval_bundles,
)


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_rules(path: Path) -> tuple[EvalMetricRule, ...]:
    payload = _load_json(path)
    if not isinstance(payload, list):
        raise ValueError("rules file must contain a JSON array")
    rules = tuple(EvalMetricRule.model_validate(item) for item in payload)
    if not rules:
        raise ValueError("rules file must contain at least one rule")
    return rules


def _markdown(report) -> str:
    lines = [
        "# Eval-Driven Comparison",
        "",
        f"- Baseline: `{report.baseline_config_id}`",
        f"- Candidate: `{report.candidate_config_id}`",
        f"- Decision: **{report.decision}**",
        f"- Comparison ID: `{report.comparison_id}`",
        "",
        "## Overall metrics",
        "",
        "| Metric | Baseline | Candidate | Directional delta | 95% bootstrap CI (raw delta) | Regression | Material |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for delta in report.metric_deltas:
        lines.append(
            f"| {delta.name} | {delta.baseline_mean:.6f} | {delta.candidate_mean:.6f} | "
            f"{delta.directional_improvement:.6f} | [{delta.ci_low:.6f}, {delta.ci_high:.6f}] | "
            f"{'yes' if delta.regression else 'no'} | {'yes' if delta.materially_improved else 'no'} |"
        )
    lines.extend(["", "## Decision reasons", ""])
    lines.extend(f"- `{reason}`" for reason in report.decision_reasons)

    if report.candidate_hard_gate_failures:
        lines.extend(["", "## Candidate hard-gate failures", ""])
        lines.extend(f"- `{failure}`" for failure in report.candidate_hard_gate_failures)

    if report.response_mode_slices:
        lines.extend(["", "## Response-mode slices", ""])
        for slice_delta in report.response_mode_slices:
            lines.append(f"### `{slice_delta.value}`")
            if slice_delta.issues:
                lines.extend(f"- issue: `{issue}`" for issue in slice_delta.issues)
            for delta in slice_delta.metric_deltas:
                lines.append(
                    f"- `{delta.name}`: baseline={delta.baseline_mean:.6f}, "
                    f"candidate={delta.candidate_mean:.6f}, "
                    f"directional_delta={delta.directional_improvement:.6f}, "
                    f"regression={str(delta.regression).lower()}"
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare provider-free eval bundles using preregistered group-aware EDD rules."
    )
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--rules",
        type=Path,
        required=True,
        help="Preregistered JSON metric rules. No implicit promotion thresholds are used.",
    )
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--bootstrap-samples", type=int, default=4000)
    parser.add_argument("--require-promote", action="store_true")
    args = parser.parse_args()

    baseline = EvalMetricBundle.model_validate(_load_json(args.baseline))
    candidate = EvalMetricBundle.model_validate(_load_json(args.candidate))
    rules = _load_rules(args.rules)
    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=rules,
        bootstrap_samples=args.bootstrap_samples,
    )

    json_text = json.dumps(
        report.model_dump(mode="json"), indent=2, sort_keys=True
    ) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json_text, encoding="utf-8")
    else:
        print(json_text, end="")

    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(_markdown(report), encoding="utf-8")

    if args.require_promote and report.decision != "PROMOTE":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
