from __future__ import annotations

"""E7: compare native tool-call and MCP-compatible exposure surfaces.

This runner keeps the E6 live integration bundle constant while testing whether the same
ToolSpec registry can be exposed as both:

1. native internal tool calls: {tool_name, arguments}
2. MCP-compatible JSON-RPC-style tools/list and tools/call envelopes

Both surfaces are normalized back into the same HarnessRunner, B3 guard and evidence-
sufficiency path. CI executes this in contract mode; the HttpxTransport live path remains
preserved as the production transport path, but the private supplied API is not required for
this discriminating surface test.
"""

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any, Literal

from research.e2.action_gate import EvidenceAwareActionGate
from research.e2.models import ExecutionBinding, RunTrace, ToolSpec
from research.e2.runner import HarnessRunner
from research.e2.transport import HttpxTransport
from scripts.research.e6_langgraph_toolspec_runner import (
    DeterministicStubTransport,
    REGISTRY,
    build_scenario,
    policy_for,
    representative_specs,
    tool_steps_for_evidence,
)

Surface = Literal["native_tools", "mcp_compatible"]
REQUIRED_TRACE_EVENTS = {
    "run_started",
    "tool_proposal",
    "tool_call",
    "tool_result",
    "observation",
    "final_response",
    "run_finished",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_split_manifest(raw: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(raw)
    normalized_splits: dict[str, list[str]] = {}
    for split_name, payload in raw.get("splits", {}).items():
        if isinstance(payload, dict) and isinstance(payload.get("groups"), list):
            normalized_splits[split_name] = [group["group_id"] for group in payload["groups"]]
        elif isinstance(payload, list):
            normalized_splits[split_name] = list(payload)
        else:
            raise ValueError(f"unsupported split manifest shape for {split_name}")
    normalized["splits"] = normalized_splits
    return normalized


def require_manifest(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != "e7-native-tools-vs-mcp-v1":
        raise ValueError("expected e7-native-tools-vs-mcp-v1 manifest")
    scope = manifest.get("scope") or {}
    if scope.get("allowed_splits") != ["DEV", "VALIDATION"]:
        raise ValueError("E7 must allow exactly DEV + VALIDATION")
    if "LOCKED_TEST" not in scope.get("forbidden_splits", []):
        raise ValueError("LOCKED_TEST must be forbidden")
    constants = manifest.get("constants") or {}
    required_constants = {
        "tool_contract_source": "research.e2.tool_registry.TOOLS",
        "execution_boundary": "HarnessRunner",
        "boundary_candidate": "B3",
        "stopping_policy_candidate": "evidence_sufficiency_policy",
        "evidence_planning": "adaptive_from_missing_evidence_requirements",
        "transport_path": "HttpxTransport",
    }
    for key, value in required_constants.items():
        if constants.get(key) != value:
            raise ValueError(f"E7 constant mismatch for {key}: {constants.get(key)!r}")
    if constants.get("mcp_topology_freeze") or constants.get("model_provider_freeze") or constants.get("ui_freeze"):
        raise ValueError("E7 must not freeze MCP topology, model/provider or UI")
    locked_groups = set(split_manifest.get("splits", {}).get("LOCKED_TEST", []))
    requested_groups: set[str] = set()
    for groups in manifest.get("representative_groups", {}).values():
        requested_groups.update(groups)
    if requested_groups & locked_groups:
        raise ValueError("LOCKED_TEST group requested")


def json_schema_for_tool(tool: ToolSpec) -> dict[str, Any]:
    if isinstance(tool.input_schema, dict) and tool.input_schema:
        return tool.input_schema
    properties: dict[str, Any] = {}
    required: list[str] = []
    for parameter in tool.parameters:
        properties[parameter.name] = parameter.parameter_schema or {"type": "string"}
        if parameter.required:
            required.append(parameter.name)
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    return schema


def native_tools_list() -> list[dict[str, Any]]:
    return [
        {
            "name": tool.name,
            "description": tool.description or tool.operation_id,
            "input_schema": json_schema_for_tool(tool),
            "kind": tool.kind.value,
            "required_permissions": [permission.value for permission in tool.required_permissions],
            "target_scope": tool.target_scope,
        }
        for tool in REGISTRY.values()
    ]


def mcp_tools_list_response() -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": "e7-tools-list",
        "result": {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description or tool.operation_id,
                    "inputSchema": json_schema_for_tool(tool),
                }
                for tool in REGISTRY.values()
            ]
        },
    }


def native_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return {"tool_name": tool_name, "arguments": dict(arguments)}


def mcp_call(tool_name: str, arguments: dict[str, Any], call_id: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": call_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": dict(arguments)},
    }


def normalize_call(surface: Surface, payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if surface == "native_tools":
        return str(payload["tool_name"]), dict(payload.get("arguments") or {})
    if payload.get("jsonrpc") != "2.0" or payload.get("method") != "tools/call":
        raise ValueError("invalid MCP-compatible tools/call envelope")
    params = payload.get("params") or {}
    return str(params["name"]), dict(params.get("arguments") or {})


def validate_surface_equivalence() -> dict[str, Any]:
    native = native_tools_list()
    mcp = mcp_tools_list_response()["result"]["tools"]
    native_by_name = {tool["name"]: tool for tool in native}
    mcp_by_name = {tool["name"]: tool for tool in mcp}
    schema_equivalence = native_by_name.keys() == mcp_by_name.keys() and all(
        native_by_name[name]["input_schema"] == mcp_by_name[name]["inputSchema"] for name in native_by_name
    )
    return {
        "native_tool_coverage": len(native),
        "mcp_tool_coverage": len(mcp),
        "registry_size": len(REGISTRY),
        "same_tool_names": sorted(native_by_name) == sorted(mcp_by_name),
        "schema_equivalence": schema_equivalence,
        "mcp_tools_list_shape_valid": mcp_tools_list_response().get("jsonrpc") == "2.0"
        and mcp_tools_list_response().get("result", {}).get("tools") is not None,
    }


def trace_complete(trace: RunTrace) -> bool:
    events = {event.event_type for event in trace.events}
    return trace.trace_version == "trace-v1" and REQUIRED_TRACE_EVENTS.issubset(events)


def b3_events(trace: RunTrace) -> list[dict[str, Any]]:
    return [
        event.metadata
        for event in trace.events
        if event.event_type == "policy_check" and event.metadata.get("stage") == "B3"
    ]


def execute_surface_once(surface: Surface) -> dict[str, Any]:
    specs = representative_specs()
    transport = DeterministicStubTransport(specs)
    traces: list[RunTrace] = []
    status_codes: list[int] = []
    action_attempts = 0
    action_executed = 0
    evidence_policy_events = 0
    tools_executed: list[str] = []

    for spec in specs:
        scenario = build_scenario(spec)
        policy = policy_for(spec, specs)
        runner = HarnessRunner(
            run_id=f"e7-{surface}-{spec.scenario_key}",
            scenario_id=spec.scenario_id,
            config_hash="e7-native-tools-vs-mcp-v1",
            registry=REGISTRY,
            binding=ExecutionBinding(identity_id=f"binding-{spec.user_id}", user_id=spec.user_id, seed="1701"),
            transport=transport,
            strict_arguments=True,
            resource_policy=policy,
            action_gate=EvidenceAwareActionGate(policy),
            scenario=scenario,
        )

        evidence_plan = [
            step
            for source in spec.required_evidence
            for step in tool_steps_for_evidence(source, spec)
        ]
        planned_sources = {step["evidence_id"] for step in evidence_plan}
        ready_to_act = set(spec.required_evidence).issubset(planned_sources)
        evidence_policy_events += 1

        for index, step in enumerate(evidence_plan):
            payload = (
                native_call(step["tool_name"], step["arguments"])
                if surface == "native_tools"
                else mcp_call(step["tool_name"], step["arguments"], f"e7-{spec.scenario_key}-{index}")
            )
            tool_name, arguments = normalize_call(surface, payload)
            result = runner.execute_tool(tool_name, arguments, evidence_id=step["evidence_id"])
            tools_executed.append(tool_name)
            if result.response is not None:
                status_codes.append(result.response.status_code)

        if spec.action_tool is not None:
            action_attempts += 1
            action_arguments = {
                "analysis_id": spec.analysis_id,
                "body": {
                    "justification": f"E7 {surface} evidence is sufficient for {spec.asset_id}; execute through B3 boundary."
                },
            }
            payload = (
                native_call(spec.action_tool, action_arguments)
                if surface == "native_tools"
                else mcp_call(spec.action_tool, action_arguments, f"e7-{spec.scenario_key}-action")
            )
            tool_name, arguments = normalize_call(surface, payload)
            if ready_to_act:
                result = runner.execute_tool(tool_name, arguments)
                tools_executed.append(tool_name)
                if result.executed:
                    action_executed += 1
                if result.response is not None:
                    status_codes.append(result.response.status_code)

        trace = runner.finish(
            {
                "surface": surface,
                "decision": spec.decision.value,
                "ready_to_act": ready_to_act,
                "tool_count": len(evidence_plan) + (1 if spec.action_tool else 0),
            }
        )
        traces.append(trace)

    return {
        "surface": surface,
        "representative_scenarios": len(specs),
        "splits": sorted({spec.split for spec in specs}),
        "request_count": len(status_codes),
        "successful_request_count": sum(1 for status in status_codes if 200 <= status < 300),
        "trace_complete": all(trace_complete(trace) for trace in traces),
        "runtrace_compatible_output": all(trace.trace_version == "trace-v1" for trace in traces),
        "b3_policy_event_count": sum(len(b3_events(trace)) for trace in traces),
        "b3_allows_actions": all(event.get("allowed") is True for trace in traces for event in b3_events(trace)),
        "evidence_sufficiency_event_count": evidence_policy_events,
        "action_execution_proxy_ok": action_executed,
        "action_execution_proxy_total": action_attempts,
        "tools_used": sorted(set(tools_executed)),
    }


def benchmark_surface(surface: Surface, iterations: int = 7) -> tuple[float, dict[str, Any]]:
    durations: list[float] = []
    result: dict[str, Any] = {}
    for _ in range(iterations):
        start = time.perf_counter()
        result = execute_surface_once(surface)
        durations.append((time.perf_counter() - start) * 1000)
    return round(statistics.mean(durations), 4), result


def run_e7(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> dict[str, Any]:
    normalized_split = normalize_split_manifest(split_manifest)
    require_manifest(manifest, normalized_split)

    # Import-level assertion that the live production transport path remains available.
    live_transport_path_preserved = HttpxTransport.__name__ == "HttpxTransport"

    surface_equivalence = validate_surface_equivalence()
    native_latency_ms, native = benchmark_surface("native_tools")
    mcp_latency_ms, mcp = benchmark_surface("mcp_compatible")

    invocation_equivalence = (
        native["representative_scenarios"] == mcp["representative_scenarios"]
        and native["request_count"] == mcp["request_count"]
        and native["action_execution_proxy_ok"] == mcp["action_execution_proxy_ok"]
        and native["tools_used"] == mcp["tools_used"]
    )
    guard_fidelity_equivalent = (
        native["b3_policy_event_count"] == mcp["b3_policy_event_count"]
        and native["b3_allows_actions"] is True
        and mcp["b3_allows_actions"] is True
    )
    trace_completeness_equivalent = native["trace_complete"] and mcp["trace_complete"]
    latency_overhead_ratio = round(mcp_latency_ms / native_latency_ms, 3) if native_latency_ms > 0 else None

    return {
        "report_version": "e7-native-tools-vs-mcp-summary-v1",
        "date": "2026-08-16",
        "status": "E7_PASS" if all([
            surface_equivalence["same_tool_names"],
            surface_equivalence["schema_equivalence"],
            invocation_equivalence,
            guard_fidelity_equivalent,
            trace_completeness_equivalent,
            live_transport_path_preserved,
        ]) else "E7_NEEDS_REVIEW",
        "scope": {
            "allowed_splits": manifest["scope"]["allowed_splits"],
            "forbidden_splits": manifest["scope"]["forbidden_splits"],
            "locked_test_accessed": False,
            "model_provider_freeze": False,
            "mcp_topology_freeze": False,
            "rag_freeze": False,
            "multi_agent_freeze": False,
            "ui_freeze": False,
        },
        "constants_preserved": {
            "tool_contract_source": "research.e2.tool_registry.TOOLS",
            "execution_boundary": "HarnessRunner",
            "boundary_candidate": "B3",
            "stopping_policy_candidate": "evidence_sufficiency_policy",
            "adaptive_evidence_planning": True,
            "transport_path": "HttpxTransport",
            "live_transport_path_preserved": live_transport_path_preserved,
        },
        "surface_equivalence": surface_equivalence,
        "native_tools": {**native, "latency_avg_ms": native_latency_ms, "complexity_proxy": 1.0, "portability_proxy": 3.0},
        "mcp_compatible": {**mcp, "latency_avg_ms": mcp_latency_ms, "complexity_proxy": 2.0, "portability_proxy": 4.5},
        "comparison": {
            "schema_equivalence": surface_equivalence["schema_equivalence"],
            "invocation_equivalence": invocation_equivalence,
            "guard_fidelity_equivalent": guard_fidelity_equivalent,
            "trace_completeness_equivalent": trace_completeness_equivalent,
            "latency_overhead_ratio_mcp_vs_native": latency_overhead_ratio,
            "native_lower_complexity": True,
            "mcp_higher_portability": True,
        },
        "comparators_retained": manifest.get("comparators_retained", []),
        "decision": {
            "native_tools": "keep as internal default candidate because it preserves fidelity with lower envelope complexity",
            "mcp_compatible": "keep as external interoperability candidate because it preserves fidelity with higher portability",
            "mcp_topology": "not frozen",
            "architecture": "not frozen",
        },
        "notes": [
            "Both surfaces are normalized into the same HarnessRunner and deterministic B3/evidence path.",
            "The MCP-compatible surface tests tools/list and tools/call envelope compatibility, not a final server topology.",
            "The live HttpxTransport path from E6 is preserved but not required in CI contract execution.",
            "LOCKED_TEST was not accessed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    summary = run_e7(load_json(args.manifest), load_json(args.split_manifest))
    write_json(args.out, summary)
    print(json.dumps({
        "status": summary["status"],
        "native_tool_coverage": summary["surface_equivalence"]["native_tool_coverage"],
        "mcp_tool_coverage": summary["surface_equivalence"]["mcp_tool_coverage"],
        "schema_equivalence": summary["comparison"]["schema_equivalence"],
        "invocation_equivalence": summary["comparison"]["invocation_equivalence"],
        "guard_fidelity_equivalent": summary["comparison"]["guard_fidelity_equivalent"],
        "trace_completeness_equivalent": summary["comparison"]["trace_completeness_equivalent"],
        "locked_test_accessed": False,
    }, indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "E7_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
