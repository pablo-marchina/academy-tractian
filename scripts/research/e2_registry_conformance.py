"""Verify Canonical ToolSpec metadata against the supplied TRACTIAN OpenAPI.

This is an infrastructure/conformance check, not an agent-quality experiment.
The partner artifact remains external to the repository.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from research.e2.conformance import compare_registry_to_contract, derive_contract_signatures
from research.e2.tool_registry import TOOLS
from scripts.research.e0_contract_pipeline import MergeDuplicateLoader

PARAMETER_TRANSFORMATIONS = {
    "companyId": "company_id",
    "assetId": "asset_id",
    "analysisId": "analysis_id",
    "modelId": "model_id",
    "docId": "doc_id",
    "caseId": "case_id",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partner-root", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    contract_path = args.partner_root / "docs" / "api-contract.openapi.yaml"
    loader = MergeDuplicateLoader(contract_path.read_text(encoding="utf-8"))
    try:
        spec = loader.get_single_data()
    finally:
        loader.dispose()

    registry = {tool.name: tool for tool in TOOLS}
    findings = compare_registry_to_contract(
        spec=spec,
        registry=registry,
        parameter_transformations=PARAMETER_TRANSFORMATIONS,
    )
    contract = derive_contract_signatures(
        spec,
        parameter_transformations=PARAMETER_TRANSFORMATIONS,
    )
    seed_expected = {operation_id for operation_id, item in contract.items() if item["seed_supported"]}
    seed_actual = {tool.operation_id for tool in TOOLS if tool.seed_supported}
    if seed_expected != seed_actual:
        from research.e2.conformance import ConformanceFinding
        findings = (*findings, ConformanceFinding("REGISTRY_SEED_SUPPORT_MISMATCH", "*", f"contract={sorted(seed_expected)!r}; registry={sorted(seed_actual)!r}"))

    report = {
        "report_version": "e2-registry-conformance-v1",
        "operation_count": len(contract),
        "registry_count": len(TOOLS),
        "seed_supported_count": len(seed_expected),
        "duplicate_keys": loader.duplicates,
        "findings": [finding.__dict__ for finding in findings],
        "passed": not findings,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
