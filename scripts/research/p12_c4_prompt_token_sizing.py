#!/usr/bin/env python3
"""Provider-free prompt sizing and conservative Cerebras pacing evidence for P12-C4.

This script reconstructs only the public EXPOSED_POOL common-parent request inputs.
It never imports a provider SDK, reads credentials, reads private expected paths, or
contacts a network service. Token counts use GPT-OSS's o200k_harmony encoding.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

import tiktoken

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "research"
ACTIVATION = ROOT / "research" / "experiments" / "p12-c2-exposed-pool-activation-eligibility-v1.json"
CASES = ROOT / "research" / "fixtures" / "p12-c1-exposed-agent-input-cases-v1.json"
SEEDS = ROOT / "research" / "frozen" / "p12-c4-fresh-seed-map-v1.json"
E10B = SCRIPTS / "e10b_dev_only_action_escalation_capture.py"
E14O = SCRIPTS / "e14o_dev_only_public_factual_grounding_prompt.py"
E14J = SCRIPTS / "e14j_strict_output_schema.py"

MODEL = "gpt-oss-120b"
ENCODING = "o200k_harmony"
MAX_COMPLETION_TOKENS = 4096
MIN_RPM = 5
MIN_TPM = 30000
MIN_TPH = 1000000
MIN_TPD = 1000000
PACING_SECONDS = 75
SERIALIZATION_SAFETY_MULTIPLIER = 1.25
FIXED_TEMPLATE_MARGIN_TOKENS = 512
EXPECTED_CASES = 12
EXPECTED_PARENTS = 36


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def extract_e14o_suffix(path: Path) -> tuple[str, str]:
    """Evaluate only the two public prompt constants from E14o's AST."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    marker: str | None = None
    suffix_expr: ast.AST | None = None
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        name = node.targets[0].id
        if name == "PROMPT_MARKER" and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            marker = node.value.value
        elif name == "FACTUAL_GROUNDING_SUFFIX":
            suffix_expr = node.value
    if marker is None or suffix_expr is None:
        raise AssertionError("E14o public prompt constants not found")

    expr = suffix_expr
    strip = False
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "rstrip" and not expr.args and not expr.keywords:
        expr = expr.func.value
        strip = True
    if not isinstance(expr, ast.JoinedStr):
        raise AssertionError("E14o suffix expression shape changed")
    parts: list[str] = []
    for value in expr.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            parts.append(value.value)
        elif isinstance(value, ast.FormattedValue) and isinstance(value.value, ast.Name) and value.value.id == "PROMPT_MARKER":
            parts.append(marker)
        else:
            raise AssertionError("E14o suffix contains an unapproved dynamic expression")
    suffix = "".join(parts)
    if strip:
        suffix = suffix.rstrip()
    return marker, suffix


def exact_cases(payload: Any) -> dict[str, dict[str, Any]]:
    rows = payload.get("cases") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise AssertionError("public cases payload must be a list or object with cases")
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict) and row.get("ticket_id"):
            ticket = str(row["ticket_id"])
            if ticket in out:
                raise AssertionError(f"duplicate ticket {ticket}")
            out[ticket] = row
    return out


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    activation = load_json(ACTIVATION)
    mapping = activation.get("exposed_pool_mapping")
    if not isinstance(mapping, list) or len(mapping) != EXPECTED_CASES:
        raise AssertionError("public C4 geometry lineage must contain 12 mapped tickets")
    cases = exact_cases(load_json(CASES))
    seed_payload = load_json(SEEDS)
    seed_rows = seed_payload.get("common_parents")
    if not isinstance(seed_rows, list) or len(seed_rows) != EXPECTED_PARENTS:
        raise AssertionError("C4 must have exactly 36 fresh seed bindings")
    c4_seeds = [int(row["seed"]) for row in seed_rows]
    if len(set(c4_seeds)) != EXPECTED_PARENTS:
        raise AssertionError("C4 seeds must be unique")

    e10b = load_module("p12_c4_sizing_e10b", E10B)
    e14j = load_module("p12_c4_sizing_e14j", E14J)
    marker, suffix = extract_e14o_suffix(E14O)
    system_prompt = e10b.STRICT_E10B_SYSTEM_PROMPT.rstrip() + suffix
    if marker not in system_prompt:
        raise AssertionError("E14o marker missing from effective system prompt")
    response_format = e14j.strict_response_format()
    e14j.run_self_checks()

    encoding = tiktoken.get_encoding(ENCODING)
    rows: list[dict[str, Any]] = []
    ordinal = 0
    for mapped in mapping:
        ticket = str(mapped["ticket_id"])
        case = cases.get(ticket)
        if case is None:
            raise AssertionError(f"public mapped ticket missing: {ticket}")
        if str(case.get("asset_id")) != str(mapped.get("group_id")):
            raise AssertionError(f"ticket/group mismatch: {ticket}")
        for repeat_index in range(3):
            ordinal += 1
            packet = e10b.e10b_observation_packet(
                "EXPOSED_POOL",
                str(mapped["group_id"]),
                {str(mapped["group_id"]): case},
            )
            user_prompt = e10b.e10b_build_prompt(packet, repeat_index)
            request = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0,
                "reasoning_effort": "medium",
                "reasoning_format": "hidden",
                "max_completion_tokens": MAX_COMPLETION_TOKENS,
                "seed": c4_seeds[ordinal - 1],
                "stream": False,
                "response_format": response_format,
            }
            serialized = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            serialized_tokens = len(encoding.encode(serialized))
            content_tokens = len(encoding.encode(system_prompt)) + len(encoding.encode(user_prompt))
            conservative_prompt_upper_bound = math.ceil(serialized_tokens * SERIALIZATION_SAFETY_MULTIPLIER) + FIXED_TEMPLATE_MARGIN_TOKENS
            reserved_admission_tokens = conservative_prompt_upper_bound + MAX_COMPLETION_TOKENS
            rows.append({
                "ordinal": ordinal,
                "parent_id": f"P{ordinal:02d}",
                "ticket_id": ticket,
                "group_id": str(mapped["group_id"]),
                "repeat_index": repeat_index,
                "seed": c4_seeds[ordinal - 1],
                "packet_sha256": sha256_text(json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
                "system_prompt_sha256": sha256_text(system_prompt),
                "user_prompt_sha256": sha256_text(user_prompt),
                "request_sha256": sha256_text(serialized),
                "system_plus_user_content_tokens": content_tokens,
                "serialized_request_tokens": serialized_tokens,
                "conservative_prompt_upper_bound_tokens": conservative_prompt_upper_bound,
                "reserved_admission_tokens": reserved_admission_tokens,
            })
    if len(rows) != EXPECTED_PARENTS:
        raise AssertionError("sizing did not materialize exactly 36 parents")
    meta = {
        "system_prompt_sha256": sha256_text(system_prompt),
        "response_format_sha256": sha256_text(json.dumps(response_format, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
        "e14o_prompt_marker": marker,
    }
    return rows, meta


def main() -> int:
    rows, meta = build_rows()
    worst = max(rows, key=lambda x: int(x["reserved_admission_tokens"]))
    max_reserved = int(worst["reserved_admission_tokens"])
    max_prompt = int(worst["conservative_prompt_upper_bound_tokens"])
    tpm_headroom = MIN_TPM - max_reserved
    tpm_headroom_fraction = tpm_headroom / MIN_TPM
    max_requests_in_any_60s = 1 if PACING_SECONDS >= 60 else math.ceil(60 / PACING_SECONDS)
    packet_reserved_upper_bound = sum(int(x["reserved_admission_tokens"]) for x in rows)
    elapsed_seconds_lower_bound = (EXPECTED_PARENTS - 1) * PACING_SECONDS

    if max_reserved >= MIN_TPM:
        raise AssertionError("one conservatively bounded C4 request would exceed minimum TPM")
    if tpm_headroom_fraction < 0.20:
        raise AssertionError("frozen pacing requires at least 20% minimum-TPM headroom per request")
    if max_requests_in_any_60s > MIN_RPM:
        raise AssertionError("frozen pacing exceeds minimum RPM")
    if packet_reserved_upper_bound >= MIN_TPD:
        raise AssertionError("full packet conservative reservation exceeds minimum TPD")
    if packet_reserved_upper_bound >= MIN_TPH:
        raise AssertionError("full packet conservative reservation exceeds minimum TPH")

    evidence = {
        "schema_version": "p12-c4-prompt-token-sizing-v1",
        "status": "PASS_CONDITIONAL_ON_ACCOUNT_LIMIT_ATTESTATION",
        "provider_calls": 0,
        "credentials_read": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "tokenizer": {"library": "tiktoken", "encoding": ENCODING},
        "request_contract": {
            "model": MODEL,
            "temperature": 0,
            "reasoning_effort": "medium",
            "reasoning_format": "hidden",
            "max_completion_tokens": MAX_COMPLETION_TOKENS,
            "strict_json_schema": True,
            "fresh_c4_seed_binding": True,
        },
        "sizing_method": {
            "serialized_request_is_provider_free_conservative_proxy": True,
            "serialization_safety_multiplier": SERIALIZATION_SAFETY_MULTIPLIER,
            "fixed_template_margin_tokens": FIXED_TEMPLATE_MARGIN_TOKENS,
            "provider_exact_prompt_token_count_claimed": False,
        },
        "published_minimum_capacity_boundary": {
            "rpm": MIN_RPM,
            "tpm": MIN_TPM,
            "tph": MIN_TPH,
            "tpd": MIN_TPD,
        },
        "frozen_pacing_candidate": {
            "minimum_seconds_between_provider_requests": PACING_SECONDS,
            "maximum_requests_in_any_60_second_window": max_requests_in_any_60s,
            "implicit_retries": 0,
            "implicit_warming_requests": 0,
            "automatic_failover": False,
            "requires_exact_account_limits_at_or_above_published_boundary": True,
        },
        "summary": {
            "parents": EXPECTED_PARENTS,
            "max_conservative_prompt_upper_bound_tokens": max_prompt,
            "max_reserved_admission_tokens": max_reserved,
            "minimum_tpm_headroom_tokens": tpm_headroom,
            "minimum_tpm_headroom_fraction": round(tpm_headroom_fraction, 6),
            "full_packet_reserved_admission_upper_bound_tokens": packet_reserved_upper_bound,
            "minimum_elapsed_seconds_for_36_requests_at_frozen_spacing": elapsed_seconds_lower_bound,
            "worst_case_parent_id": worst["parent_id"],
            "worst_case_ticket_id": worst["ticket_id"],
        },
        "hashes": meta,
        "parents": rows,
        "authorization": {
            "synthetic_live_probe": False,
            "exposed_pool_live_generation": False,
            "private_scoring": False,
        },
        "next_gate": "VERIFY_EXACT_CEREBRAS_ACCOUNT_LIMITS_AND_ACTIVE_API_ACCESS_BEFORE_ANY_PROVIDER_CALL",
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
