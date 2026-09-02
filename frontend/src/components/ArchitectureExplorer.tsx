import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import { useMemo, useState } from "react";

import type {
  ArchitectureComponent,
  ArchitectureManifest,
  SafeEvent,
} from "../api/types";

const layerOrder: ArchitectureComponent["layer"][] = [
  "browser",
  "api",
  "runtime",
  "safety",
  "external",
  "evaluator",
  "observability",
];

function isActive(
  component: ArchitectureComponent,
  events: readonly SafeEvent[],
  hasRun: boolean,
  hasEvaluation: boolean,
): boolean {
  if (!hasRun) return false;
  if (component.component_id === "operator_frontend") return true;
  if (component.component_id === "production_evaluator") return hasEvaluation;
  if (component.activates_on_event_types.length === 0) return false;
  const eventTypes = new Set(events.map((event) => event.event_type));
  return component.activates_on_event_types.some((eventType) => eventTypes.has(eventType));
}

export function ArchitectureExplorer({
  manifest,
  events,
  hasRun,
  hasEvaluation,
}: {
  manifest: ArchitectureManifest;
  events: readonly SafeEvent[];
  hasRun: boolean;
  hasEvaluation: boolean;
}) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = manifest.components.find((component) => component.component_id === selectedId) ?? null;

  const { nodes, edges } = useMemo(() => {
    const layerCounts = new Map<string, number>();
    const graphNodes: Node[] = manifest.components.map((component) => {
      const x = layerOrder.indexOf(component.layer) * 235;
      const row = layerCounts.get(component.layer) ?? 0;
      layerCounts.set(component.layer, row + 1);
      const active = isActive(component, events, hasRun, hasEvaluation);
      return {
        id: component.component_id,
        position: { x, y: row * 150 },
        data: {
          label: (
            <div className="architecture-node-label">
              <span>{component.layer}</span>
              <strong>{component.label}</strong>
              <small>{component.execution_role.replaceAll("_", " ")}</small>
            </div>
          ),
        },
        className: `architecture-node ${active ? "architecture-node-active" : "architecture-node-idle"}`,
      };
    });

    const graphEdges: Edge[] = manifest.edges.map((edge, index) => ({
      id: `architecture-edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      animated:
        isActive(
          manifest.components.find((component) => component.component_id === edge.source)!,
          events,
          hasRun,
          hasEvaluation,
        ) &&
        isActive(
          manifest.components.find((component) => component.component_id === edge.target)!,
          events,
          hasRun,
          hasEvaluation,
        ),
    }));
    return { nodes: graphNodes, edges: graphEdges };
  }, [events, hasEvaluation, hasRun, manifest]);

  return (
    <div className="architecture-layout">
      <div className="architecture-graph graph-canvas">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          minZoom={0.2}
          maxZoom={1.6}
          nodesConnectable={false}
          nodesDraggable={false}
          onNodeClick={(_, node) => setSelectedId(node.id)}
        >
          <Background gap={22} size={1} />
          <MiniMap pannable zoomable />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>

      <aside className="architecture-detail">
        <div className="architecture-manifest-meta">
          <span>Manifest</span>
          <strong>{manifest.architecture_version}</strong>
          <code>{manifest.manifest_sha256.slice(0, 14)}</code>
        </div>
        <div className="architecture-manifest-meta">
          <span>Provider selection</span>
          <strong>{manifest.provider_selection_state}</strong>
        </div>

        {selected ? (
          <div className="architecture-selected">
            <p className="eyebrow">SELECTED COMPONENT</p>
            <h3>{selected.label}</h3>
            <p>{selected.responsibility}</p>
            <dl>
              <div><dt>Trust boundary</dt><dd>{selected.trust_boundary}</dd></div>
              <div><dt>Role</dt><dd>{selected.execution_role.replaceAll("_", " ")}</dd></div>
              <div><dt>Inputs</dt><dd>{selected.input_contracts.join(", ") || "—"}</dd></div>
              <div><dt>Outputs</dt><dd>{selected.output_contracts.join(", ") || "—"}</dd></div>
              <div><dt>Run evidence</dt><dd>{selected.activates_on_event_types.join(", ") || "post-runtime / UI state"}</dd></div>
            </dl>
          </div>
        ) : (
          <div className="empty-state small">
            <strong>Select an architecture node</strong>
            <p>Responsibilities and boundaries come from the backend manifest, not frontend copy.</p>
          </div>
        )}
      </aside>
    </div>
  );
}
