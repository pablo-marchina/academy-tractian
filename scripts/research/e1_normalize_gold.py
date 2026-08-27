from __future__ import annotations

"""E1: normalize supplied machine + narrative gold into a review-ready private draft.

The output contains evaluator-only material and MUST remain private until artifact-publication
policy is clarified. The script performs mechanical extraction and diagnostics; it does not turn
machine extraction into benchmark authority. Every scenario remains human-review-required.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

SCENARIO_RE = re.compile(r"^##\s+(CEN-\d+)\s+—\s+(.+?)\s+\(([^)]+)\)\s*$")
FIELD_RE = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
HTTP_RE = re.compile(r"`((?:GET|POST|PATCH|PUT|DELETE)\s+[^`]+)`", re.I)
HTTP_METHODS = {"get", "post", "patch", "put", "delete"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_sections(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line_number, line in enumerate(lines, start=1):
        match = SCENARIO_RE.match(line)
        if match:
            if current:
                sections.append(current)
            current = {
                "scenario_id": match.group(1),
                "title": match.group(2).strip(),
                "ticket_ref": match.group(3).strip(),
                "start_line": line_number,
                "lines": [],
            }
        elif current:
            if line.startswith("## "):
                sections.append(current)
                current = None
            else:
                current["lines"].append((line_number, line))
    if current:
        sections.append(current)
    return sections


def parse_fields(lines: list[tuple[int, str]]) -> dict[str, dict[str, Any]]:
    fields: dict[str, dict[str, Any]] = {}
    current: str | None = None
    for line_number, line in lines:
        match = FIELD_RE.match(line)
        if match:
            current = match.group(1).strip()
            fields[current] = {"start_line": line_number, "parts": [match.group(2).rstrip()]}
        elif current is not None:
            fields[current]["parts"].append(line.rstrip())
    for value in fields.values():
        parts = value["parts"]
        while parts and not parts[-1].strip():
            parts.pop()
        value["text"] = "\n".join(parts).strip()
    return fields


def ticket_ids(reference: str) -> list[str]:
    return re.findall(r"TKT-[A-Z]+-\d+b?", reference)


def bullet_items(text: str) -> list[str]:
    items: list[str] = []
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            if current:
                items.append(current.strip())
            current = stripped[2:]
        elif current and stripped:
            current += " " + stripped
    if current:
        items.append(current.strip())
    return items


def numbered_items(text: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if match:
            if current:
                items.append(current)
            current = {"n": int(match.group(1)), "text": match.group(2)}
        elif current and stripped:
            current["text"] += " " + stripped
    if current:
        items.append(current)
    for item in items:
        match = HTTP_RE.search(item["text"])
        item["call"] = match.group(1).strip() if match else None
        item["inspect"] = item["text"].split("?", 1)[1].strip() if "?" in item["text"] else None
    return items


def resolution_label(text: str) -> str | None:
    match = re.match(r"^\*\*(.+?)\*\*", text.strip(), re.S)
    return match.group(1).strip() if match else None


def source_clauses(text: str) -> list[str]:
    normalized = " ".join(line.strip() for line in text.splitlines())
    return [part.strip() for part in re.split(r";\s*", normalized) if part.strip()]


def load_contract_routes(path: Path):
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    routes = []
    for route, path_item in (spec.get("paths") or {}).items():
        for method in path_item:
            if method.lower() not in HTTP_METHODS:
                continue
            pattern = "^" + re.sub(r"\\\{[^{}]+\\\}", r"[^/?]+", re.escape(route)) + "$"
            routes.append((method.upper(), route, re.compile(pattern)))
    return routes


def call_signature(call: str | None, routes) -> str | None:
    if not call:
        return None
    method, rest = call.split(None, 1)
    path = rest.split("?", 1)[0]
    for candidate_method, route, pattern in routes:
        if candidate_method != method.upper():
            continue
        concrete_candidate = re.sub(r"\{[^{}]+\}", "X", path)
        if pattern.match(concrete_candidate) or pattern.match(path):
            return f"{candidate_method} {re.sub(r'{[^{}]+}', '{}', route)}"
    return f"{method.upper()} {re.sub(r'{[^{}]+}', '{}', path)}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--contract", required=True, help="E0 normalized contract candidate")
    parser.add_argument("--out", required=True, help="PRIVATE review-ready draft")
    parser.add_argument("--summary", required=True, help="Safe aggregate summary")
    args = parser.parse_args()

    cases_path = Path(args.cases)
    expected_path = Path(args.expected)
    scenarios_path = Path(args.scenarios)
    contract_path = Path(args.contract)

    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    case_by_ticket = {item["ticket_id"]: item for item in cases}
    expected_by_ticket = {item["ticket_id"]: item for item in expected}
    routes = load_contract_routes(contract_path)

    required_fields = [
        "Objetivo",
        "Contexto inicial",
        "Política",
        "Trajetória esperada",
        "Resolução esperada",
        "Variações a testar",
        "Critério de sucesso (P1)",
        "Métricas (P2)",
    ]

    records: list[dict[str, Any]] = []
    parser_issues: list[dict[str, Any]] = []

    for section in split_sections(scenarios_path.read_text(encoding="utf-8")):
        fields = parse_fields(section["lines"])
        tickets = ticket_ids(section["ticket_ref"])
        missing_fields = [field for field in required_fields if field not in fields]
        if missing_fields:
            parser_issues.append({"scenario_id": section["scenario_id"], "type": "missing_fields", "fields": missing_fields})

        matched_cases = [case_by_ticket[ticket] for ticket in tickets if ticket in case_by_ticket]
        matched_expected = [expected_by_ticket[ticket] for ticket in tickets if ticket in expected_by_ticket]
        if len(matched_cases) != len(tickets):
            parser_issues.append({"scenario_id": section["scenario_id"], "type": "missing_agent_case", "ticket_ids": tickets})
        if len(matched_expected) != len(tickets):
            parser_issues.append({"scenario_id": section["scenario_id"], "type": "missing_machine_gold", "ticket_ids": tickets})

        narrative_steps = numbered_items(fields.get("Trajetória esperada", {}).get("text", ""))
        narrative_signatures = [call_signature(step["call"], routes) for step in narrative_steps if step["call"]]
        machine_steps = []
        for item in matched_expected:
            for step in item.get("expected_path", []):
                machine_steps.append({
                    "ticket_id": item["ticket_id"],
                    **step,
                    "signature": call_signature(step.get("step"), routes),
                })
        machine_signatures = [step["signature"] for step in machine_steps if step["signature"]]

        asset_ids = sorted({item.get("asset_id") for item in matched_cases if item.get("asset_id")})
        company_ids = sorted({item.get("company_id") for item in matched_cases if item.get("company_id")})
        user_ids = sorted({item.get("user_id") for item in matched_cases if item.get("user_id")})

        record = {
            "schema_version": "scenario-v1-draft-source-normalized",
            "scenario_id": section["scenario_id"],
            "title": section["title"],
            "ticket_ids": tickets,
            "split_group_id": asset_ids[0] if len(asset_ids) == 1 else "+".join(asset_ids),
            "provenance": {
                "scenario_markdown_line": section["start_line"],
                "source_hashes": {
                    "cases_json": sha256(cases_path),
                    "expected_paths_json": sha256(expected_path),
                    "test_scenarios_md": sha256(scenarios_path),
                    "normalized_contract": sha256(contract_path),
                },
                "human_review_required": True,
                "review_status": "UNREVIEWED",
            },
            "bound_context": {"asset_ids": asset_ids, "company_ids": company_ids, "user_ids": user_ids},
            "agent_inputs": matched_cases,
            "machine_reference": matched_expected,
            "narrative": {
                "objective": fields.get("Objetivo", {}).get("text"),
                "initial_context": fields.get("Contexto inicial", {}).get("text"),
                "policy_items": bullet_items(fields.get("Política", {}).get("text", "")),
                "reference_trajectory": narrative_steps,
                "expected_resolution_text": fields.get("Resolução esperada", {}).get("text"),
                "expected_resolution_label": resolution_label(fields.get("Resolução esperada", {}).get("text", "")),
                "variations_text": fields.get("Variações a testar", {}).get("text"),
                "p1_success_text": fields.get("Critério de sucesso (P1)", {}).get("text"),
                "p1_success_clauses": source_clauses(fields.get("Critério de sucesso (P1)", {}).get("text", "")),
                "p2_metrics_text": fields.get("Métricas (P2)", {}).get("text"),
                "p2_metric_clauses": source_clauses(fields.get("Métricas (P2)", {}).get("text", "")),
            },
            "trajectory_diagnostic": {
                "narrative_signatures": narrative_signatures,
                "machine_signatures": machine_signatures,
                "narrative_not_in_machine": sorted(set(narrative_signatures) - set(machine_signatures)),
                "machine_not_in_narrative": sorted(set(machine_signatures) - set(narrative_signatures)),
                "exact_signature_sequence_equal": narrative_signatures == machine_signatures,
            },
            "oracle_draft": {
                "decision_label_source_text": resolution_label(fields.get("Resolução esperada", {}).get("text", "")),
                "policy_source_items": bullet_items(fields.get("Política", {}).get("text", "")),
                "p1_requirement_source_clauses": source_clauses(fields.get("Critério de sucesso (P1)", {}).get("text", "")),
                "structured_oracle_status": "REQUIRES_HUMAN_REVIEW_BEFORE_BENCHMARK_USE",
            },
        }
        records.append(record)

    private_output = {"schema_version": "gold-normalization-v1-draft", "records": records}
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(private_output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    divergent = sum(
        bool(record["trajectory_diagnostic"]["narrative_not_in_machine"] or record["trajectory_diagnostic"]["machine_not_in_narrative"])
        for record in records
    )
    summary = {
        "schema_version": "gold-normalization-summary-v0",
        "source_hashes": {
            "cases_json": sha256(cases_path),
            "expected_paths_json": sha256(expected_path),
            "test_scenarios_md": sha256(scenarios_path),
            "normalized_contract": sha256(contract_path),
        },
        "scenario_count": len(records),
        "unique_ticket_count": len({ticket for record in records for ticket in record["ticket_ids"]}),
        "unique_split_groups": len({record["split_group_id"] for record in records}),
        "scenarios_with_machine_vs_narrative_endpoint_divergence": divergent,
        "parser_issues": parser_issues,
        "human_review_required_for_all": True,
        "benchmark_authoritative": False,
        "private_output_sha256": sha256(output_path),
        "scenario_status": [
            {
                "scenario_id": record["scenario_id"],
                "ticket_ids": record["ticket_ids"],
                "split_group_id": record["split_group_id"],
                "narrative_steps": len(record["narrative"]["reference_trajectory"]),
                "machine_steps": len(record["trajectory_diagnostic"]["machine_signatures"]),
                "endpoint_divergence": bool(record["trajectory_diagnostic"]["narrative_not_in_machine"] or record["trajectory_diagnostic"]["machine_not_in_narrative"]),
                "review_status": "UNREVIEWED",
            }
            for record in records
        ],
    }
    Path(args.summary).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
