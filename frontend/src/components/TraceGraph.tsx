import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useMemo } from "react";

import type { SafeEvent } from "../api/types";
import { eventDisplayLabel } from "../state/runEvents";

function nodeClass(event: SafeEvent): string {
  if (event.failure_code || event.event_type === "error") return "trace-node-danger";
  if (event.event_type === "policy_check" && event.policy_allowed === false) return "trace-node-warning";
  if (event.event_type === "run_finished" || event.event_type === "final_response") return "trace-node-success";
  if (event.event_type === "model_call") return "trace-node-model";
  if (event.event_type.includes("tool") || event.event_type === "observation") return "trace-node-tool";
  return "trace-node-neutral";
}

function friendlyTraceLabel(event: SafeEvent): string {
  if (event.event_type === "model_call") return "Agent chose the next step";
  if (event.event_type === "tool_call") return event.tool_name ? `Requested ${event.tool_name.replaceAll("_", " ")}` : "Requested information";
  if (event.event_type === "tool_result") return "Received tool result";
  if (event.event_type === "observation") return "Saved evidence";
  if (event.event_type === "policy_check") return event.policy_allowed === false ? "Safety policy blocked a step" : "Safety policy allowed a step";
  if (event.event_type === "final_response") return "Prepared final answer";
  if (event.event_type === "run_finished") return "Analysis finished";
  if (event.event_type === "error") return "Recorded an error";
  return eventDisplayLabel(event);
}

export function TraceGraph({ events }: { events: readonly SafeEvent[] }) {
  const { nodes, edges } = useMemo(() => {
    const graphNodes: Node[] = events.map((event, index) => ({
      id: event.event_id,
      position: { x: (index % 4) * 245, y: Math.floor(index / 4) * 125 },
      data: {
        label: (
          <div className="trace-node-label">
            <span>Step {event.sequence}</span>
            <strong>{friendlyTraceLabel(event)}</strong>
            {event.tool_name && <small>{event.tool_name}</small>}
          </div>
        ),
      },
      className: `trace-node ${nodeClass(event)}`,
    }));

    const graphEdges: Edge[] = events.slice(1).map((event, index) => ({
      id: `${events[index].event_id}->${event.event_id}`,
      source: events[index].event_id,
      target: event.event_id,
      animated: !events.some((item) => item.event_type === "run_finished"),
    }));

    return { nodes: graphNodes, edges: graphEdges };
  }, [events]);

  if (events.length === 0) {
    return (
      <div className="empty-state graph-empty">
        <strong>No process steps to show</strong>
        <p>The process graph appears only when a selected analysis has safe trace events.</p>
      </div>
    );
  }

  return (
    <div className="trace-graph-shell">
      <div className="trace-legend" aria-label="Process graph legend">
        <span><i className="trace-legend-dot trace-legend-model" aria-hidden="true" />Agent decision</span>
        <span><i className="trace-legend-dot trace-legend-tool" aria-hidden="true" />Data/tool step</span>
        <span><i className="trace-legend-dot trace-legend-warning" aria-hidden="true" />Safety block</span>
        <span><i className="trace-legend-dot trace-legend-success" aria-hidden="true" />Completed step</span>
      </div>
      <div className="graph-canvas" aria-label="Execution process graph">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          minZoom={0.25}
          maxZoom={1.8}
          nodesConnectable={false}
          nodesDraggable={false}
          elementsSelectable
        >
          <Background gap={22} size={1} />
          <MiniMap pannable zoomable />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
      <details className="technical-disclosure trace-text-alternative">
        <summary>Read the process as a list</summary>
        <ol>
          {events.map((event) => (
            <li key={event.event_id}>
              <strong>Step {event.sequence}: {friendlyTraceLabel(event)}</strong>
              <span>{event.message || "No additional public message was saved for this step."}</span>
              {(event.tool_name || event.failure_code) && (
                <small>{event.tool_name ? `Tool: ${event.tool_name}` : ""}{event.tool_name && event.failure_code ? " · " : ""}{event.failure_code ? `Failure: ${event.failure_code}` : ""}</small>
              )}
            </li>
          ))}
        </ol>
      </details>
    </div>
  );
}
