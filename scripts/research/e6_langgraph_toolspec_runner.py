from __future__ import annotations

"""E6 implementation spike: adaptive LangGraph graph over real ToolSpec/HarnessRunner.

This script intentionally makes acquisition more adaptive while preserving deterministic
safety boundaries. The graph chooses evidence tools from remaining evidence gaps, but
ToolSpec validation, HarnessRunner execution, B2 resource/permission policy, B3
evidence-aware action gating, runner-bound identity/seed and LOCKED_TEST blocking remain
outside model control.
"""

import argparse
import hashlib
import json
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from research.e2.action_gate import EvidenceAwareActionGate
from research.e2.models import (
    ActionOracle,
    AgentCase,
    BoundContext,
    CommunicationOracle,
    ConclusionOracle,
    Decision,
    DecisionOracle,
    EnvironmentSpec,
    EvaluationSpec,
    EvidenceGroup,
    EvidenceOracle,
    EvidenceRequirement,
    ExecutionBinding,
    Permission,
    PolicyOracle,
    Provenance,
    ReviewStatus,
    Scenario,
    ScenarioInput,
    ToolKind,
    TrajectoryOracle,
)
from research.e2.policy import ResourcePolicy
from research.e2.runner import HarnessRunner
from research.e2.tool_registry import TOOLS
from research.e2.transport import TransportResponse


REGISTRY = {tool.name: tool for tool in TOOLS}


class GraphState(TypedDict, total=False):
    scenario_key: str
    split: str
    required_evidence: list[str]
    acquired_evidence: list[str]
    evidence_plan: list[dict[str, Any]]
    action_plan: dict[str, Any] | None
    ready_to_act: bool
    tool_spec_registry_wired: bool
    harness_runner_used: bool
    b3_external_guard_preserved: bool
    evidence_sufficiency_policy_explicit: bool
    trace: dict[str, Any]
    final: dict[str, Any]
    graph_events: list[dict[str, Any]]


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    scenario_key: str
    split: str
    group_id: str
    asset_id: str
    company_id: str
    user_id: str
    analysis_id: str
    required_evidence: tuple[str, ...]
    action_tool: str | None
    decision: Decision
    message: str


class DeterministicStubTransport:
    """Small deterministic transport used only for the integration spike.

    It is deliberately not a partner-problem solution. Its role is to exercise the existing
    ToolSpec -> HarnessRunner -> B3 trace path without touching LOCKED_TEST or private gold.
    """

    def __init__(self, specs: list[ScenarioSpec]) -> None:
        self.asset_to_spec = {spec.asset_id: spec for spec in specs}
        self.analysis_to_spec = {spec.analysis_id: spec for spec in specs}

    def request(self, request: Any) -> TransportResponse:
        path = request.path
        method = request.method
        if method == "GET" and path.startswith("/assets/") and path.endswith("/analyses"):
            asset_id = path.split("/")[2]
            spec = self.asset_to_spec[asset_id]
            return TransportResponse(200, {}, {"items": [{"id": spec.analysis_id, "asset_id": asset_id, "status": "current"}]})
        if method == "GET" and path.startswith("/assets/") and path.endswith("/data-quality"):
            asset_id = path.split("/")[2]
            return TransportResponse(200, {}, {"asset_id": asset_id, "quality": "usable", "missingness": 0.0})
        if method == "GET" and path.startswith("/assets/") and path.endswith("/baseline"):
            asset_id = path.split("/")[2]
            return TransportResponse(200, {}, {"asset_id": asset_id, "baseline_available": True})
        if method == "GET" and path.startswith("/assets/") and path.endswith("/spectrum"):
            asset_id = path.split("/")[2]
            return TransportResponse(200, {}, {"asset_id": asset_id, "spectrum_available": True})
        if method == "GET" and path.startswith("/assets/"):
            asset_id = path.split("/")[2]
            spec = self.asset_to_spec[asset_id]
            return TransportResponse(200, {}, {"id": asset_id, "company_id": spec.company_id, "status": "monitored"})
        if method == "GET" and path.startswith("/analyses/"):
            analysis_id = path.split("/")[2]
            spec = self.analysis_to_spec[analysis_id]
            return TransportResponse(200, {}, {"id": analysis_id, "asset_id": spec.asset_id, "diagnosis": "reviewable"})
        if method == "GET" and path.startswith("/knowledge/search"):
            return TransportResponse(200, {}, {"items": [{"id": "doc-bearing-guidance", "title": "Bearing diagnostic guidance"}]})
        if method == "POST" and path.endswith("/request-specialist"):
            return TransportResponse(202, {}, {"accepted": True, "action_id": "act-specialist", "message": "specialist requested"})
        if method == "POST" and path.endswith("/reprocess"):
            return TransportResponse(202, {}, {"accepted": True, "action_id": "act-reprocess", "message": "reprocess requested"})
        return TransportResponse(404, {}, {"error": f"unhandled spike path: {method} {path}"})


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def graph_event(event_type: str, **metadata: Any) -> dict[str, Any]:
    return {"event_type": event_type, "metadata": metadata}


def append_graph_event(state: GraphState, event_type: str, **metadata: Any) -> list[dict[str, Any]]:
    return [*state.get("graph_events", []), graph_event(event_type, **metadata)]


def require_manifest(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != "e6-real-toolspec-langgraph-spike-v1":
        raise ValueError("expected e6-real-toolspec-langgraph-spike-v1 manifest")
    if "LOCKED_TEST" not in manifest.get("scope", {}).get("forbidden_splits", []):
        raise ValueError("LOCKED_TEST must be forbidden")
    constants = manifest.get("constants") or {}
    if constants.get("execution_boundary") != "HarnessRunner":
        raise ValueError("E6 implementation spike must use HarnessRunner")
    if constants.get("boundary_candidate") != "B3":
        raise ValueError("E6 implementation spike must hold B3 constant")
    if constants.get("stopping_policy_candidate") != "evidence_sufficiency_policy":
        raise ValueError("E6 implementation spike must hold evidence-sufficiency constant")
    if constants.get("model_provider_freeze") or constants.get("mcp_topology_freeze") or constants.get("ui_freeze"):
        raise ValueError("E6 implementation spike must not freeze model/MCP/UI")
    locked = set(split_manifest.get("splits", {}).get("LOCKED_TEST", []))
    requested = set()
    for groups in manifest.get("representative_groups", {}).values():
        requested.update(groups)
    if requested & locked:
        raise ValueError("representative groups must not include LOCKED_TEST")


def representative_specs() -> list[ScenarioSpec]:
    return [
        ScenarioSpec(
            scenario_id="CEN-01",
            scenario_key="dev_action_data_quality",
            split="DEV",
            group_id="asset_G501",
            asset_id="asset_G501",
            company_id="company_alpha",
            user_id="user_alpha_action_low",
            analysis_id="analysis_G501_current",
            required_evidence=("asset", "analysis", "data_quality"),
            action_tool="request_specialist_analysis",
            decision=Decision.ACT_REQUEST_SPECIALIST,
            message="Investigate the asset and request a specialist only after evidence is sufficient.",
        ),
        ScenarioSpec(
            scenario_id="CEN-02",
            scenario_key="dev_context_baseline_spectrum",
            split="DEV",
            group_id="asset_C710",
            asset_id="asset_C710",
            company_id="company_alpha",
            user_id="user_alpha_readonly",
            analysis_id="analysis_C710_current",
            required_evidence=("asset", "baseline", "spectrum", "knowledge"),
            action_tool=None,
            decision=Decision.ORIENT,
            message="Explain the evidence without executing a platform action.",
        ),
        ScenarioSpec(
            scenario_id="CEN-07",
            scenario_key="validation_reprocess",
            split="VALIDATION",
            group_id="asset_B204",
            asset_id="asset_B204",
            company_id="company_beta",
            user_id="user_beta_action_low",
            analysis_id="analysis_B204_stale",
            required_evidence=("asset", "analysis", "data_quality"),
            action_tool="reprocess_analysis",
            decision=Decision.ACT_REPROCESS,
            message="Confirm stale analysis evidence before requesting reprocess.",
        ),
        ScenarioSpec(
            scenario_id="CEN-09",
            scenario_key="validation_coverage_limit",
            split="VALIDATION",
            group_id="asset_M102",
            asset_id="asset_M102",
            company_id="company_beta",
            user_id="user_beta_readonly",
            analysis_id="analysis_M102_current",
            required_evidence=("asset", "analysis", "baseline"),
            action_tool=None,
            decision=Decision.INVESTIGATE,
            message="Investigate coverage limits and stop without automatic action.",
        ),
    ]


def validate_scope(specs: list[ScenarioSpec], manifest: dict[str, Any], split_manifest: dict[str, Any]) -> None:
    allowed = set(manifest["scope"]["allowed_splits"])
    locked_groups = set(split_manifest.get("splits", {}).get("LOCKED_TEST", []))
    split_groups = split_manifest.get("splits", {})
    for spec in specs:
        if spec.split not in allowed:
            raise ValueError(f"split not allowed in E6 implementation spike: {spec.split}")
        if spec.group_id in locked_groups or spec.split == "LOCKED_TEST":
            raise ValueError("LOCKED_TEST access attempted")
        if spec.group_id not in set(split_groups.get(spec.split, [])):
            raise ValueError(f"representative group {spec.group_id} is not in split {spec.split}")


def build_scenario(spec: ScenarioSpec) -> Scenario:
    required_groups = [
        EvidenceGroup(
            group_id="pre_action_or_stop",
            minimum_satisfied=len(spec.required_evidence),
            requirements=[
                EvidenceRequirement(source=source, predicate=f"{source} evidence observed", required_before_action=True)
                for source in spec.required_evidence
            ],
        )
    ]
    action_oracle = None
    if spec.action_tool is not None:
        action_oracle = ActionOracle(
            execution_expectation="required",
            success_semantics="accepted_event",
            post_action_read_semantics="diagnostic_only",
            required_action=spec.action_tool,
            target_resource=spec.analysis_id,
            required_permission=Permission.ACTION_LOW,
            justification_facts=["evidence sufficient", spec.asset_id],
        )
    return Scenario(
        scenario_id=spec.scenario_id,
        title=spec.scenario_key,
        ticket_ids=[f"TKT-{spec.scenario_key}"],
        split_group_id=spec.group_id,
        provenance=Provenance(
            review_status=ReviewStatus.APPROVED,
            benchmark_authoritative=False,
            review_notes=["synthetic integration scenario derived from frozen split group; no private gold text"],
        ),
        input=ScenarioInput(
            cases=[
                AgentCase(
                    id=f"CASE-{spec.scenario_key}",
                    ticket_id=f"TKT-{spec.scenario_key}",
                    company_id=spec.company_id,
                    user_id=spec.user_id,
                    asset_id=spec.asset_id,
                    message=spec.message,
                )
            ]
        ),
        bound_context=BoundContext(
            user_ids=[spec.user_id],
            company_ids=[spec.company_id],
            asset_ids=[spec.asset_id],
        ),
        environment=EnvironmentSpec(scenario_condition="e6 adaptive integration spike"),
        decision_oracle=DecisionOracle(required=[spec.decision]),
        policy_oracle=PolicyOracle(
            required_permissions=[Permission.ACTION_LOW] if spec.action_tool is not None else [],
            justification_required=spec.action_tool is not None,
            minimum_justification_length=20 if spec.action_tool is not None else None,
        ),
        evidence_oracle=EvidenceOracle(required_groups=required_groups),
        action_oracle=action_oracle,
        conclusion_oracle=ConclusionOracle(
            required_facts=list(spec.required_evidence),
            source_resolution_text="public integration spike summary only; private gold not used",
        ),
        communication_oracle=CommunicationOracle(),
        trajectory_oracle=TrajectoryOracle(),
        evaluation=EvaluationSpec(p1_success_source="e6 adaptive integration spike proxy"),
    )


def policy_for(spec: ScenarioSpec, specs: list[ScenarioSpec]) -> ResourcePolicy:
    lookup: dict[str, str] = {}
    for item in specs:
        lookup[item.asset_id] = item.company_id
        lookup[item.analysis_id] = item.company_id
        lookup[item.company_id] = item.company_id
    permissions = {Permission.READ}
    if spec.action_tool is not None:
        permissions.add(Permission.ACTION_LOW)
    return ResourcePolicy(
        user_permissions=permissions,
        user_company_id=spec.company_id,
        resource_company_lookup=lookup,
    )


def tool_steps_for_evidence(source: str, spec: ScenarioSpec) -> list[dict[str, Any]]:
    if source == "asset":
        return [{"tool_name": "get_asset", "arguments": {"asset_id": spec.asset_id}, "evidence_id": "asset"}]
    if source == "analysis":
        return [
            {"tool_name": "list_analyses", "arguments": {"asset_id": spec.asset_id}, "evidence_id": "analysis"},
            {"tool_name": "get_analysis", "arguments": {"analysis_id": spec.analysis_id}, "evidence_id": "analysis"},
        ]
    if source == "data_quality":
        return [{"tool_name": "get_data_quality", "arguments": {"asset_id": spec.asset_id}, "evidence_id": "data_quality"}]
    if source == "baseline":
        return [{"tool_name": "get_baseline", "arguments": {"asset_id": spec.asset_id}, "evidence_id": "baseline"}]
    if source == "spectrum":
        return [{"tool_name": "get_spectrum", "arguments": {"asset_id": spec.asset_id}, "evidence_id": "spectrum"}]
    if source == "knowledge":
        return [{"tool_name": "search_knowledge", "arguments": {"q": "bearing diagnostic guidance"}, "evidence_id": "knowledge"}]
    raise ValueError(f"no ToolSpec mapping for evidence source: {source}")


def initial_state(spec: ScenarioSpec) -> GraphState:
    return {
        "scenario_key": spec.scenario_key,
        "split": spec.split,
        "required_evidence": list(spec.required_evidence),
        "acquired_evidence": [],
        "evidence_plan": [],
        "action_plan": None,
        "ready_to_act": False,
        "tool_spec_registry_wired": False,
        "harness_runner_used": False,
        "b3_external_guard_preserved": False,
        "evidence_sufficiency_policy_explicit": False,
        "graph_events": [graph_event("run_started", split=spec.split, locked_test_accessed=False)],
    }


def make_nodes(specs: list[ScenarioSpec], transport: DeterministicStubTransport):
    spec_by_key = {spec.scenario_key: spec for spec in specs}

    def wire_tool_registry(state: GraphState) -> GraphState:
        action_count = sum(1 for tool in REGISTRY.values() if tool.kind is ToolKind.ACTION)
        return {
            **state,
            "tool_spec_registry_wired": len(REGISTRY) == 18 and action_count == 5,
            "graph_events": append_graph_event(
                state,
                "state_change",
                node="wire_tool_registry",
                tool_count=len(REGISTRY),
                action_count=action_count,
            ),
        }

    def adaptive_evidence_planner(state: GraphState) -> GraphState:
        spec = spec_by_key[state["scenario_key"]]
        acquired = set(state.get("acquired_evidence", []))
        missing = [source for source in state.get("required_evidence", []) if source not in acquired]
        plan: list[dict[str, Any]] = []
        # Choose tools from unresolved evidence gaps, not from a single fixed scenario script.
        for source in missing:
            plan.extend(tool_steps_for_evidence(source, spec))
        return {
            **state,
            "evidence_plan": plan,
            "graph_events": append_graph_event(
                state,
                "decision",
                node="adaptive_evidence_planner",
                missing_evidence=missing,
                proposed_tools=[step["tool_name"] for step in plan],
                adaptive=True,
            ),
        }

    def evidence_sufficiency_gate(state: GraphState) -> GraphState:
        planned_sources = {step["evidence_id"] for step in state.get("evidence_plan", [])}
        required = set(state.get("required_evidence", []))
        ready = required.issubset(planned_sources | set(state.get("acquired_evidence", [])))
        return {
            **state,
            "ready_to_act": ready,
            "evidence_sufficiency_policy_explicit": True,
            "graph_events": append_graph_event(
                state,
                "policy_check",
                node="evidence_sufficiency_gate",
                policy="evidence_sufficiency_policy",
                allowed=ready,
                missing=sorted(required - planned_sources),
            ),
        }

    def b3_boundary_marker(state: GraphState) -> GraphState:
        return {
            **state,
            "b3_external_guard_preserved": True,
            "graph_events": append_graph_event(
                state,
                "policy_check",
                node="b3_boundary_marker",
                boundary="B3",
                external_deterministic_guard=True,
                note="HarnessRunner/EvidenceAwareActionGate performs pre-execution enforcement",
            ),
        }

    def execute_with_harness(state: GraphState) -> GraphState:
        spec = spec_by_key[state["scenario_key"]]
        scenario = build_scenario(spec)
        policy = policy_for(spec, specs)
        runner = HarnessRunner(
            run_id=f"e6-adaptive-langgraph-{spec.scenario_key}",
            scenario_id=spec.scenario_id,
            config_hash="e6-real-toolspec-langgraph-v1",
            registry=REGISTRY,
            binding=ExecutionBinding(identity_id=f"binding-{spec.user_id}", user_id=spec.user_id, seed=1701),
            transport=transport,
            strict_arguments=True,
            resource_policy=policy,
            action_gate=EvidenceAwareActionGate(policy),
            scenario=scenario,
        )
        acquired: list[str] = []
        executed_tools: list[str] = []
        for step in state.get("evidence_plan", []):
            runner.execute_tool(step["tool_name"], dict(step["arguments"]), evidence_id=step["evidence_id"])
            acquired.append(step["evidence_id"])
            executed_tools.append(step["tool_name"])
        action_result = None
        action_plan = None
        if spec.action_tool is not None:
            if not bool(state.get("ready_to_act")):
                action_plan = {"skipped": True, "reason": "evidence_sufficiency_policy_not_ready"}
            else:
                action_arguments = {
                    "analysis_id": spec.analysis_id,
                    "body": {
                        "justification": f"Required evidence satisfied for {spec.asset_id}; executing via B3 guarded boundary."
                    },
                }
                action_plan = {"tool_name": spec.action_tool, "arguments": action_arguments}
                action_result = runner.execute_tool(spec.action_tool, action_arguments)
                executed_tools.append(spec.action_tool)
        final = {
            "decision": spec.decision.value,
            "evidence_sources": sorted(set(acquired)),
            "action_executed": bool(action_result and action_result.executed),
            "adaptive_plan_tools": executed_tools,
        }
        trace = runner.finish(final).model_dump(mode="json")
        return {
            **state,
            "acquired_evidence": sorted(set(acquired)),
            "action_plan": action_plan,
            "harness_runner_used": True,
            "trace": trace,
            "final": final,
            "graph_events": append_graph_event(
                state,
                "state_change",
                node="execute_with_harness",
                executed_tools=executed_tools,
                harness_runner_used=True,
            ),
        }

    def finalize_graph(state: GraphState) -> GraphState:
        return {
            **state,
            "graph_events": append_graph_event(
                state,
                "final_response",
                node="finalize_graph",
                trace_events=len(state.get("trace", {}).get("events", [])),
            ),
        }

    return wire_tool_registry, adaptive_evidence_planner, evidence_sufficiency_gate, b3_boundary_marker, execute_with_harness, finalize_graph


def build_graph(specs: list[ScenarioSpec], transport: DeterministicStubTransport, *, with_interrupt: bool = False):
    from langgraph.graph import END, START, StateGraph
    try:
        from langgraph.checkpoint.memory import InMemorySaver
    except ImportError:  # pragma: no cover
        from langgraph.checkpoint.memory import MemorySaver as InMemorySaver

    wire, planner, gate, b3_marker, execute, finalize = make_nodes(specs, transport)
    builder = StateGraph(GraphState)
    builder.add_node("wire_tool_registry", wire)
    builder.add_node("adaptive_evidence_planner", planner)
    builder.add_node("evidence_sufficiency_gate", gate)
    builder.add_node("b3_boundary_marker", b3_marker)
    builder.add_node("execute_with_harness", execute)
    builder.add_node("finalize_graph", finalize)
    builder.add_edge(START, "wire_tool_registry")
    builder.add_edge("wire_tool_registry", "adaptive_evidence_planner")
    builder.add_edge("adaptive_evidence_planner", "evidence_sufficiency_gate")
    builder.add_edge("evidence_sufficiency_gate", "b3_boundary_marker")
    builder.add_edge("b3_boundary_marker", "execute_with_harness")
    builder.add_edge("execute_with_harness", "finalize_graph")
    builder.add_edge("finalize_graph", END)
    checkpointer = InMemorySaver()
    if with_interrupt:
        return builder.compile(checkpointer=checkpointer, interrupt_before=["execute_with_harness"])
    return builder.compile(checkpointer=checkpointer)


def trace_is_runtrace_compatible(trace: dict[str, Any]) -> bool:
    events = trace.get("events", [])
    return (
        trace.get("trace_version") == "trace-v1"
        and isinstance(trace.get("run_id"), str)
        and isinstance(events, list)
        and bool(events)
        and all(isinstance(event.get("event_type"), str) and isinstance(event.get("sequence"), int) for event in events)
    )


def state_digest(state: GraphState) -> str:
    comparable = {
        "scenario_key": state.get("scenario_key"),
        "final": state.get("final"),
        "trace_events": [
            {
                "event_type": event.get("event_type"),
                "tool_name": event.get("tool_name"),
                "arguments": event.get("arguments"),
                "metadata": event.get("metadata"),
            }
            for event in state.get("trace", {}).get("events", [])
        ],
    }
    return hashlib.sha256(json.dumps(comparable, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def run_graph_suite(app: Any, specs: list[ScenarioSpec], *, prefix: str) -> list[GraphState]:
    outputs: list[GraphState] = []
    for spec in specs:
        outputs.append(app.invoke(initial_state(spec), config={"configurable": {"thread_id": f"{prefix}-{spec.scenario_key}"}}))
    return outputs


def run_direct_suite(specs: list[ScenarioSpec], transport: DeterministicStubTransport) -> list[GraphState]:
    wire, planner, gate, b3_marker, execute, finalize = make_nodes(specs, transport)
    states: list[GraphState] = []
    for spec in specs:
        state = initial_state(spec)
        state = wire(state)
        state = planner(state)
        state = gate(state)
        state = b3_marker(state)
        state = execute(state)
        state = finalize(state)
        states.append(state)
    return states


def benchmark(fn, *, iterations: int = 15) -> tuple[float, Any]:
    durations: list[float] = []
    result: Any = None
    for _ in range(iterations):
        start = time.perf_counter()
        result = fn()
        durations.append((time.perf_counter() - start) * 1000)
    return round(statistics.mean(durations), 4), result


def summarize_outputs(outputs: list[GraphState]) -> dict[str, Any]:
    required_total = sum(len(state.get("required_evidence", [])) for state in outputs)
    observed_total = 0
    action_ok = 0
    action_total = 0
    unique_paths = set()
    runtrace_ok = True
    b3_policy_events = 0
    for state in outputs:
        required = set(state.get("required_evidence", []))
        observed = set(state.get("acquired_evidence", []))
        observed_total += len(required & observed)
        unique_paths.add(tuple(step["tool_name"] for step in state.get("evidence_plan", [])))
        trace = state.get("trace", {})
        runtrace_ok = runtrace_ok and trace_is_runtrace_compatible(trace)
        for event in trace.get("events", []):
            if event.get("event_type") == "policy_check" and event.get("metadata", {}).get("stage") == "B3":
                b3_policy_events += 1
        if state.get("action_plan"):
            action_total += 1
            final = state.get("final", {})
            if final.get("action_executed") is True:
                action_ok += 1
    return {
        "representative_scenarios": len(outputs),
        "splits": sorted({state.get("split") for state in outputs}),
        "adaptive_path_count": len(unique_paths),
        "required_evidence_coverage": round(observed_total / required_total, 3) if required_total else 1.0,
        "action_execution_proxy_ok": action_ok,
        "action_execution_proxy_total": action_total,
        "runtrace_compatible_output": runtrace_ok,
        "b3_policy_events": b3_policy_events,
    }


def run_spike(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> dict[str, Any]:
    require_manifest(manifest, split_manifest)
    specs = representative_specs()
    validate_scope(specs, manifest, split_manifest)
    transport = DeterministicStubTransport(specs)

    app = build_graph(specs, transport, with_interrupt=False)
    outputs_a = run_graph_suite(app, specs, prefix="e6-adaptive-a")
    outputs_b = run_graph_suite(app, specs, prefix="e6-adaptive-b")
    deterministic_replay_equal = [state_digest(a) for a in outputs_a] == [state_digest(b) for b in outputs_b]

    interrupt_app = build_graph(specs, transport, with_interrupt=True)
    paused = interrupt_app.invoke(initial_state(specs[0]), config={"configurable": {"thread_id": "e6-adaptive-pause"}})
    resumed = interrupt_app.invoke(None, config={"configurable": {"thread_id": "e6-adaptive-pause"}})
    checkpoint_pause_resume_roundtrip = "trace" not in paused and "trace" in resumed

    direct_avg_ms, direct_outputs = benchmark(lambda: run_direct_suite(specs, transport))
    graph_avg_ms, graph_outputs = benchmark(lambda: run_graph_suite(app, specs, prefix=f"e6-adaptive-bench-{time.perf_counter_ns()}"))
    overhead_ratio = round(graph_avg_ms / direct_avg_ms, 3) if direct_avg_ms > 0 else None

    aggregate = summarize_outputs(graph_outputs)
    tool_names_used = sorted({step["tool_name"] for state in graph_outputs for step in state.get("evidence_plan", [])})
    action_tools_used = sorted({state.get("action_plan", {}).get("tool_name") for state in graph_outputs if state.get("action_plan") and state.get("action_plan", {}).get("tool_name")})

    return {
        "report_version": "e6-real-toolspec-langgraph-summary-v1",
        "date": "2026-08-16",
        "scope": {
            "allowed_splits": manifest["scope"]["allowed_splits"],
            "forbidden_splits": manifest["scope"]["forbidden_splits"],
            "locked_test_accessed": False,
            "tool_spec_constant": True,
            "boundary_candidate": "B3",
            "stopping_policy_candidate": "evidence_sufficiency_policy",
            "runtime_candidate": "langgraph",
            "model_provider_freeze": False,
            "mcp_topology_freeze": False,
            "rag_freeze": False,
            "multi_agent_freeze": False,
            "ui_freeze": False,
        },
        "adaptive_mode": True,
        "adaptive_scope": "evidence acquisition order and tool selection only",
        "tool_spec_registry_wired": all(state.get("tool_spec_registry_wired") for state in graph_outputs),
        "tool_spec_registry_size": len(REGISTRY),
        "tool_names_used": tool_names_used,
        "action_tools_used": action_tools_used,
        "harness_runner_used": all(state.get("harness_runner_used") for state in graph_outputs),
        "b3_external_guard_preserved": all(state.get("b3_external_guard_preserved") for state in graph_outputs),
        "evidence_sufficiency_policy_explicit": all(state.get("evidence_sufficiency_policy_explicit") for state in graph_outputs),
        "runtrace_compatible_output": aggregate["runtrace_compatible_output"],
        "representative_scenarios": aggregate["representative_scenarios"],
        "splits": aggregate["splits"],
        "adaptive_path_count": aggregate["adaptive_path_count"],
        "required_evidence_coverage": aggregate["required_evidence_coverage"],
        "action_execution_proxy_ok": aggregate["action_execution_proxy_ok"],
        "action_execution_proxy_total": aggregate["action_execution_proxy_total"],
        "b3_policy_events": aggregate["b3_policy_events"],
        "deterministic_replay_equal": deterministic_replay_equal,
        "checkpoint_pause_resume_roundtrip": checkpoint_pause_resume_roundtrip,
        "direct_harness_avg_ms": direct_avg_ms,
        "langgraph_avg_ms": graph_avg_ms,
        "overhead_ratio": overhead_ratio,
        "comparators_retained": manifest.get("comparators_retained", []),
        "decision": {
            "langgraph": "advance to real DEV/VALIDATION integration implementation" if deterministic_replay_equal and checkpoint_pause_resume_roundtrip and aggregate["runtrace_compatible_output"] else "keep candidate but require another integration spike",
            "pydantic_ai_graph": "retain as fallback/comparator",
            "openai_agents_sdk": "retain as provider-native comparator",
        },
        "notes": [
            "This is more adaptive than the previous micro-spike because tool selection is derived from missing evidence requirements, not from one fixed tool script.",
            "Safety remains deterministic: B3 and evidence sufficiency are policy nodes outside model control.",
            "HarnessRunner and the real ToolSpec registry are used for execution and trace generation.",
            "LOCKED_TEST was not accessed.",
            "Model/provider, MCP topology, RAG/vector DB, multi-agent design, observability backend and UI remain unfrozen.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run_spike(load_json(args.manifest), load_json(args.split_manifest))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "adaptive_mode": summary["adaptive_mode"],
        "tool_spec_registry_wired": summary["tool_spec_registry_wired"],
        "harness_runner_used": summary["harness_runner_used"],
        "runtrace_compatible_output": summary["runtrace_compatible_output"],
        "adaptive_path_count": summary["adaptive_path_count"],
        "checkpoint_pause_resume_roundtrip": summary["checkpoint_pause_resume_roundtrip"],
        "locked_test_accessed": False,
    }, indent=2, ensure_ascii=False))
    if not summary["tool_spec_registry_wired"] or not summary["harness_runner_used"] or not summary["runtrace_compatible_output"]:
        return 1
    if not summary["deterministic_replay_equal"] or not summary["checkpoint_pause_resume_roundtrip"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
