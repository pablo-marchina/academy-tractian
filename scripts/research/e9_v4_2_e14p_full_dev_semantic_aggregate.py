#!/usr/bin/env python3
"""Aggregate E14p full-DEV E9 v4.2 semantic judge rows without row disclosure."""
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path
from typing import Any
HERE=Path(__file__).parent
BASE_PATH=HERE/"e9_v4_2_real_dev_semantic_aggregate.py"
RUNNER_PATH=HERE/"e9_v4_2_qwen36_27b_e14p_full_dev_semantic_judge_runner.py"
bs=importlib.util.spec_from_file_location("e9_v42_base_full",BASE_PATH); rs=importlib.util.spec_from_file_location("e9_v42_runner_full",RUNNER_PATH)
if bs is None or bs.loader is None or rs is None or rs.loader is None: raise RuntimeError("failed to load dependencies")
base=importlib.util.module_from_spec(bs); bs.loader.exec_module(base)
runner=importlib.util.module_from_spec(rs); rs.loader.exec_module(runner)
REPORT_VERSION="e9-v4.2-e14p-full-dev-semantic-aggregate-v1"
PASS_STATUS="E9_V4_2_E14P_FULL_DEV_SEMANTIC_GROUNDEDNESS_PASS"
FAIL_STATUS="E9_V4_2_E14P_FULL_DEV_SEMANTIC_GROUNDEDNESS_FAIL"
def run(args: argparse.Namespace)->dict[str,Any]:
    sr=base.runner; sv=base.EXPECTED_RESULT_VERSION
    base.runner=runner; base.EXPECTED_RESULT_VERSION=runner.RESULT_VERSION
    try: summary=base.run(args)
    finally: base.runner=sr; base.EXPECTED_RESULT_VERSION=sv
    if int(summary.get("factual_claims_total") or 0)==0:
        summary["factual_groundedness_rate"]=1.0; summary["factual_groundedness_rate_definition"]="1.0_when_zero_factual_assertions_else_supported_over_total"
    else: summary["factual_groundedness_rate_definition"]="supported_factual_assertions_over_total_factual_assertions"
    summary["report_version"]=REPORT_VERSION
    summary["status"]=PASS_STATUS if summary.get("semantic_groundedness_gate_pass") is True else FAIL_STATUS
    summary["candidate"]=runner.CANDIDATE
    summary["full_dev_v4_1_gate_already_failed"]=True
    summary["semantic_pass_can_rescue_candidate"]=False
    summary["validation_gate_authorized"]=False
    return summary
def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--claim-packet",type=Path,required=True); p.add_argument("--judge-results",type=Path,required=True); a=p.parse_args(); s=run(a); print(json.dumps(s,indent=2)); return 0 if s["semantic_groundedness_gate_pass"] else 1
if __name__=="__main__": raise SystemExit(main())
