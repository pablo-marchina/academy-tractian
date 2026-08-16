"""Run a non-demo integrated B0 conformance probe against the supplied partner API.

The script executes the CEN-01 reference path only to verify transport, runner binding,
TraceSchema integration and replay capture. It does not evaluate or demonstrate agent policy.

Usage:
    python scripts/research/e2_b0_real_api_probe.py --partner-root /path/to/inteli-tractian-project

The partner package is never copied into this repository.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi.testclient import TestClient

from research.e2.models import ExecutionBinding
from research.e2.replay import ReplayStore
from research.e2.runner import HarnessRunner
from research.e2.tool_registry import TOOLS
from research.e2.transport import TransportResponse


def load_partner_api(partner_root: Path):
    api_root = partner_root / "api"
    sys.path.insert(0, str(api_root))
    from app import main, store  # type: ignore
    import seed_data  # type: ignore

    tables = {
        "companies": pd.DataFrame(seed_data.COMPANIES),
        "users": pd.DataFrame(seed_data.USERS),
        "assets": pd.DataFrame(seed_data.ASSETS),
        "points": pd.DataFrame(seed_data.POINTS),
        "analyses": pd.DataFrame(seed_data.ANALYSES),
        "baselines": pd.DataFrame(seed_data.BASELINES),
        "rms": pd.DataFrame(seed_data.RMS_ROWS),
        "spectra": pd.DataFrame(seed_data.SPECTRA),
        "data_quality": pd.DataFrame(seed_data.DATA_QUALITY),
        "models": pd.DataFrame(seed_data.MODELS),
        "knowledge": pd.DataFrame(seed_data.KNOWLEDGE),
        "cases": pd.DataFrame(seed_data.CASES),
    }
    store._tables.cache_clear()
    store._tables = lambda: tables
    store.seed_config.cache_clear()
    store.seed_config = lambda: seed_data.SEED_JSON
    return main.app


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def resolve_tool(method: str, path: str):
    for tool in TOOLS:
        if tool.method != method:
            continue
        pattern = re.escape(tool.path_template)
        for parameter in tool.parameters:
            if parameter.location == "path":
                pattern = pattern.replace(re.escape("{" + _snake_to_camel(parameter.name) + "}"), r"([^/]+)")
        match = re.fullmatch(pattern, path)
        if match:
            path_parameters = [p for p in tool.parameters if p.location == "path"]
            arguments = {p.name: value for p, value in zip(path_parameters, match.groups())}
            return tool, arguments
    raise KeyError(f"no canonical tool for {method} {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partner-root", type=Path, required=True)
    args = parser.parse_args()

    expected = json.loads((args.partner_root / "eval/expected-paths.json").read_text())
    case = next(item for item in expected if item["ticket_id"] == "TKT-INV-04")
    app = load_partner_api(args.partner_root)
    client = TestClient(app)

    class ClientTransport:
        def request(self, request):
            response = client.request(request.method, request.path, params=request.query, headers=request.headers, json=request.body)
            try:
                body = response.json()
            except ValueError:
                body = response.text
            return TransportResponse(response.status_code, dict(response.headers), body)

    registry = {tool.name: tool for tool in TOOLS}
    replay = ReplayStore()
    runner = HarnessRunner(
        run_id="probe-cen-01",
        scenario_id="CEN-01",
        config_hash="0" * 64,
        registry=registry,
        binding=ExecutionBinding(identity_id="probe-cen-01", user_id="usr_pedro", seed="CEN-01"),
        transport=ClientTransport(),
        replay=replay,
    )

    results: list[dict[str, Any]] = []
    for index, expected_step in enumerate(case["expected_path"]):
        method, path = expected_step["step"].split(" ", 1)
        tool, arguments = resolve_tool(method, path)
        if tool.kind.value == "action":
            arguments["body"] = {"justification": "probe-only: deterministic transport conformance for CEN-01 action execution"}
        result = runner.execute_tool(tool.name, arguments, evidence_id=f"probe-step-{index + 1}")
        assert result.response is not None
        body = result.response.body if isinstance(result.response.body, dict) else {}
        results.append({"step": index + 1, "tool": tool.name, "status": result.response.status_code, "mode": body.get("mode"), "accepted": body.get("accepted")})

    trace = runner.finish({"probe_only": True})
    report = {
        "scenario": "CEN-01",
        "purpose": "transport_trace_replay_conformance_only",
        "results": results,
        "trace_event_count": len(trace.events),
        "replay_observation_count": len(replay.export()),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not all(item["status"] == 200 for item in results):
        return 1
    if results[-1]["accepted"] is not True:
        return 1
    if report["replay_observation_count"] != len(results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
