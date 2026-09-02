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
  if (event.event_type === "policy_check" && event.policy_allowed === false) {
    return "trace-node-warning";
  }
  if (event.event_type === "run_finished" || event.event_type === "final_response") {
    return "trace-node-success";
  }
  if (event.event_type === "model_call") return "trace-node-model";
  if (event.event_type.includes("tool") || event.event_type === "observation") {
    return "trace-node-tool";
  }
  return "trace-node-neutral";
}

export function TraceGraph({ events }: { events: readonly SafeEvent[] }) {
  const { nodes, edges } = useMemo(() => {
    const graphNodes: Node[] = events.map((event, index) => ({
      id: event.event_id,
      position: {
        x: (index % 4) * 245,
        y: Math.floor(index / 4) * 125,
      },
      data: {
        label: (
          <div className="trace-node-label">
            <span>{String(event.sequence).padStart(2, "0")} · {event.origin}</span>
            <strong>{eventDisplayLabel(event)}</strong>
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
        <strong>No trace to graph</strong>
        <p>The graph is derived only from persisted or live safe trace events.</p>
      </div>
    );
  }

  return (
    <div className="graph-canvas" aria-label="Canonical execution trace graph">
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
  );
}
