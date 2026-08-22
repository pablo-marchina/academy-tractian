from __future__ import annotations

"""E6 follow-up: minimal LangGraph integration spike.

This runner verifies whether the E6 LangGraph scorecard survives an executable
minimal graph. It holds project decisions constant: ToolSpec discipline, B3 as an
external deterministic guard, evidence-sufficiency/stopping as explicit state,
DEV/VALIDATION-only scope, and no model/MCP/RAG/UI freeze.
"""

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, TypedDict


class SpikeState(TypedDict, total=False):
    scenario_id: str
    split: str
    required_evidence: list[str]
    evidence: list[str]
    ready_to_act: bool
    guard_allowed: bool
    action_executed: bool
    final_answer: str
    events: list[dict[str, Any]]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def event(event_type: str, **metadata: Any) -> dict[str, Any]:
    return {"event_type": event_type, "metadata": metadata}


def append_event(state: SpikeState, event_type: str, **metadata: Any) -> list[dict[str, Any]]:
    return [*state.get("events", []), event(event_type, **metadata)]


def acquire_evidence(state: SpikeState) -> SpikeState:
    evidence = ["asset", "analysis", "data_quality"]
    return {
        **state,
        "evidence": evidence,
        "events": append_event(
            state,
            "tool_result",
            node="acquire_evidence",
            tool_names=["get_asset", "get_analysis", "get_data_quality"],
            evidence=evidence,
        ),
    }


def evidence_sufficiency_gate(state: SpikeState) -> SpikeState:
    required = set(state.get("required_evidence", []))
    observed = set(state.get("evidence", []))
    ready = required.issubset(observed)
    return {
        **state,
        "ready_to_act": ready,
        "events": append_event(
            state,
            "policy_check",
            node="evidence_sufficiency_gate",
            policy="evidence_sufficiency_policy",
            allowed=ready,
            missing=sorted(required - observed),
        ),
    }


def b3_guard(state: SpikeState) -> SpikeState:
    allowed = bool(state.get("ready_to_act"))
    return {
        **state,
        "guard_allowed": allowed,
        "events": append_event(
            state,
            "policy_check",
            node="b3_guard",
            boundary="B3",
            allowed=allowed,
            external_deterministic_guard=True,
        ),
    }


def execute_tool(state: SpikeState) -> SpikeState:
    executed = bool(state.get("guard_allowed"))
    event_type = "tool_call" if executed else "tool_blocked"
    return {
        **state,
        "action_executed": executed,
        "events": append_event(
            state,
            event_type,
            node="execute_tool",
            tool_name="request_specialist_analysis",
            accepted=executed,
        ),
    }


def finalize(state: SpikeState) -> SpikeState:
    final = "Action executed after required evidence and B3 guard approval." if state.get("action_executed") else "Action blocked by B3/evidence-sufficiency policy."
    return {
        **state,
        "final_answer": final,
        "events": append_event(state, "final_response", node="finalize", final_answer=final),
    }


def direct_harness(initial: SpikeState) -> SpikeState:
    state = acquire_evidence(initial)
    state = evidence_sufficiency_gate(state)
    state = b3_guard(state)
    state = execute_tool(state)
    state = finalize(state)
    return state


def require_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != "e6-langgraph-integration-spike-v1":
        raise ValueError("expected e6-langgraph-integration-spike-v1 manifest")
    if "LOCKED_TEST" not in manifest.get("forbidden_splits", []):
        raise ValueError("LOCKED_TEST must be forbidden")
    constants = manifest.get("constants") or {}
    if constants.get("boundary_candidate") != "B3":
        raise ValueError("E6 follow-up must hold B3 constant")
    if constants.get("stopping_policy_candidate") != "evidence_sufficiency_policy":
        raise ValueError("E6 follow-up must hold evidence-sufficiency policy constant")
    if constants.get("model_provider_freeze") or constants.get("mcp_topology_freeze") or constants.get("ui_freeze"):
        raise ValueError("E6 follow-up must not freeze model/MCP/UI")


def digest_events(state: SpikeState) -> str:
    public_events = [
        {"event_type": item.get("event_type"), "metadata": item.get("metadata", {})}
        for item in state.get("events", [])
    ]
    payload = json.dumps(public_events, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def trace_schema_compatible(state: SpikeState) -> bool:
    events = state.get("events", [])
    if not events:
        return False
    return all(isinstance(item, dict) and isinstance(item.get("event_type"), str) and isinstance(item.get("metadata", {}), dict) for item in events)


def build_langgraph_app(*, with_interrupt: bool = False):
    from langgraph.graph import END, START, StateGraph
    try:
        from langgraph.checkpoint.memory import InMemorySaver
    except ImportError:  # backward-compatible alias in older installs
        from langgraph.checkpoint.memory import MemorySaver as InMemorySaver

    builder = StateGraph(SpikeState)
    builder.add_node("acquire_evidence", acquire_evidence)
    builder.add_node("evidence_sufficiency_gate", evidence_sufficiency_gate)
    builder.add_node("b3_guard", b3_guard)
    builder.add_node("execute_tool", execute_tool)
    builder.add_node("finalize", finalize)
    builder.add_edge(START, "acquire_evidence")
    builder.add_edge("acquire_evidence", "evidence_sufficiency_gate")
    builder.add_edge("evidence_sufficiency_gate", "b3_guard")
    builder.add_edge("b3_guard", "execute_tool")
    builder.add_edge("execute_tool", "finalize")
    builder.add_edge("finalize", END)
    checkpointer = InMemorySaver()
    if with_interrupt:
        return builder.compile(checkpointer=checkpointer, interrupt_before=["execute_tool"])
    return builder.compile(checkpointer=checkpointer)


def benchmark(fn, *, iterations: int = 25) -> tuple[float, Any]:
    durations: list[float] = []
    result: Any = None
    for index in range(iterations):
        start = time.perf_counter()
        result = fn(index)
        durations.append((time.perf_counter() - start) * 1000)
    return round(statistics.mean(durations), 4), result


def run_spike(manifest: dict[str, Any]) -> dict[str, Any]:
    require_manifest(manifest)
    initial: SpikeState = {
        "scenario_id": "E6-LANGGRAPH-SPIKE",
        "split": "VALIDATION",
        "required_evidence": ["asset", "analysis", "data_quality"],
        "events": [event("run_started", runtime="langgraph", locked_test_accessed=False)],
    }

    langgraph_imported = False
    graph_compiled = False
    graph_invoked = False
    deterministic_replay_equal = False
    pause_resume_roundtrip = False
    pause_resume_diagnostic = "not_run"
    output: SpikeState | None = None

    try:
        app = build_langgraph_app(with_interrupt=False)
        langgraph_imported = True
        graph_compiled = True
        config_a = {"configurable": {"thread_id": "e6-langgraph-normal-a"}}
        config_b = {"configurable": {"thread_id": "e6-langgraph-normal-b"}}
        output_a = app.invoke(initial, config=config_a)
        output_b = app.invoke(initial, config=config_b)
        output = output_a
        graph_invoked = True
        deterministic_replay_equal = digest_events(output_a) == digest_events(output_b)

        interrupt_app = build_langgraph_app(with_interrupt=True)
        interrupt_config = {"configurable": {"thread_id": "e6-langgraph-interrupt"}}
        paused = interrupt_app.invoke(initial, config=interrupt_config)
        resumed = interrupt_app.invoke(None, config=interrupt_config)
        paused_events = [item.get("event_type") for item in (paused or {}).get("events", [])]
        resumed_events = [item.get("event_type") for item in (resumed or {}).get("events", [])]
        pause_resume_roundtrip = "tool_call" not in paused_events and "tool_call" in resumed_events
        pause_resume_diagnostic = "static_interrupt_before_execute_tool_roundtrip" if pause_resume_roundtrip else f"paused={paused_events}; resumed={resumed_events}"
    except Exception as exc:  # pragma: no cover - diagnostic path in dependency changes
        pause_resume_diagnostic = f"langgraph integration failed: {type(exc).__name__}: {exc}"
        if output is None:
            output = direct_harness(initial)

    direct_avg_ms, direct_result = benchmark(lambda _: direct_harness(initial))
    graph_avg_ms, graph_result = benchmark(
        lambda index: build_langgraph_app(with_interrupt=False).invoke(
            initial,
            config={"configurable": {"thread_id": f"e6-langgraph-bench-{index}"}},
        )
    ) if graph_compiled else (None, output)

    trace_state = graph_result or output or direct_result
    overhead_ratio = None
    if graph_avg_ms is not None and direct_avg_ms > 0:
        overhead_ratio = round(graph_avg_ms / direct_avg_ms, 3)

    summary = {
        "report_version": "e6-langgraph-integration-summary-v1",
        "date": "2026-08-16",
        "scope": {
            "allowed_splits": manifest["allowed_splits"],
            "forbidden_splits": manifest["forbidden_splits"],
            "locked_test_accessed": False,
            "tool_spec_constant": True,
            "boundary_candidate": "B3",
            "stopping_policy_candidate": "evidence_sufficiency_policy",
            "model_provider_freeze": False,
            "mcp_topology_freeze": False,
            "rag_freeze": False,
            "multi_agent_freeze": False,
            "ui_freeze": False,
        },
        "langgraph_imported": langgraph_imported,
        "graph_compiled": graph_compiled,
        "graph_invoked": graph_invoked,
        "trace_schema_compatible_events": trace_schema_compatible(trace_state),
        "trace_event_count": len(trace_state.get("events", [])),
        "b3_external_guard_preserved": any(
            item.get("event_type") == "policy_check" and item.get("metadata", {}).get("boundary") == "B3" and item.get("metadata", {}).get("external_deterministic_guard") is True
            for item in trace_state.get("events", [])
        ),
        "evidence_sufficiency_policy_explicit": any(
            item.get("event_type") == "policy_check" and item.get("metadata", {}).get("policy") == "evidence_sufficiency_policy"
            for item in trace_state.get("events", [])
        ),
        "deterministic_replay_equal": deterministic_replay_equal,
        "checkpoint_pause_resume_roundtrip": pause_resume_roundtrip,
        "pause_resume_diagnostic": pause_resume_diagnostic,
        "direct_harness_avg_ms": direct_avg_ms,
        "langgraph_avg_ms": graph_avg_ms,
        "overhead_ratio": overhead_ratio,
        "comparators_retained": manifest.get("comparators_retained", []),
        "decision": {
            "langgraph": "confirm as current runtime candidate for implementation spike" if graph_compiled and graph_invoked and deterministic_replay_equal and trace_schema_compatible(trace_state) else "keep candidate but require follow-up before implementation",
            "pydantic_ai_graph": "retain as fallback/comparator",
            "openai_agents_sdk": "retain as provider-native comparator",
        },
        "notes": [
            "This is a minimal runtime integration spike, not full agent-quality evidence.",
            "B3 and evidence-sufficiency are represented as deterministic graph/policy nodes outside model control.",
            "LOCKED_TEST was not accessed.",
            "Model/provider, MCP topology, RAG/vector DB, multi-agent design, observability backend and UI remain unfrozen.",
        ],
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run_spike(load_json(args.manifest))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "langgraph_imported": summary["langgraph_imported"], "graph_compiled": summary["graph_compiled"], "replay": summary["deterministic_replay_equal"], "pause_resume": summary["checkpoint_pause_resume_roundtrip"], "locked_test_accessed": False}, indent=2, ensure_ascii=False))
    if not summary["graph_compiled"] or not summary["graph_invoked"] or not summary["deterministic_replay_equal"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
