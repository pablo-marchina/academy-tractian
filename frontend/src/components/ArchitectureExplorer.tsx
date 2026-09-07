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

function friendlyLayer(layer: ArchitectureComponent["layer"]): string {
  const labels: Record<ArchitectureComponent["layer"], string> = {
    browser: "Browser",
    api: "Application API",
    runtime: "Agent runtime",
    safety: "Safety controls",
    external: "External services",
    evaluator: "Evaluation",
    observability: "Observability",
  };
  return labels[layer];
}

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

  const activeIds = useMemo(
    () => new Set(manifest.components.filter((component) => isActive(component, events, hasRun, hasEvaluation)).map((component) => component.component_id)),
    [events, hasEvaluation, hasRun, manifest.components],
  );

  const { nodes, edges } = useMemo(() => {
    const layerCounts = new Map<string, number>();
    const graphNodes: Node[] = manifest.components.map((component) => {
      const x = layerOrder.indexOf(component.layer) * 235;
      const row = layerCounts.get(component.layer) ?? 0;
      layerCounts.set(component.layer, row + 1);
      const active = activeIds.has(component.component_id);
      return {
        id: component.component_id,
        position: { x, y: row * 150 },
        data: {
          label: (
            <div className="architecture-node-label">
              <span>{friendlyLayer(component.layer)}</span>
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
      animated: activeIds.has(edge.source) && activeIds.has(edge.target),
    }));
    return { nodes: graphNodes, edges: graphEdges };
  }, [activeIds, manifest]);

  return (
    <div className="architecture-layout refined-architecture-layout">
      <div className="architecture-main-column">
        <div className="architecture-guide" role="note">
          <strong>How to read this view</strong>
          <p>The diagram shows how product components connect. A highlighted component participated in the selected analysis. Choose a component below or in the diagram to inspect its responsibility and trust boundary.</p>
        </div>

        <div className="architecture-component-list" aria-label="Architecture components">
          {manifest.components.map((component) => {
            const active = activeIds.has(component.component_id);
            const selectedComponent = component.component_id === selectedId;
            return (
              <button
                type="button"
                key={component.component_id}
                className={`architecture-component-button ${active ? "is-active" : ""} ${selectedComponent ? "is-selected" : ""}`}
                aria-pressed={selectedComponent}
                onClick={() => setSelectedId(component.component_id)}
              >
                <span>{friendlyLayer(component.layer)}</span>
                <strong>{component.label}</strong>
                <small>{active ? "Used in this analysis" : "Not observed in this analysis"}</small>
              </button>
            );
          })}
        </div>

        <div className="architecture-graph graph-canvas" aria-label="Interactive architecture diagram">
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
            <MiniMap pannable zoomable ariaLabel="Architecture overview map" />
            <Controls showInteractive={false} />
          </ReactFlow>
        </div>
      </div>

      <aside className="architecture-detail" aria-live="polite">
        <div className="architecture-manifest-meta">
          <span>Architecture version</span>
          <strong>{manifest.architecture_version}</strong>
          <details className="technical-disclosure compact-disclosure">
            <summary>Manifest fingerprint</summary>
            <code>{manifest.manifest_sha256}</code>
          </details>
        </div>
        <div className="architecture-manifest-meta">
          <span>Provider selection</span>
          <strong>{manifest.provider_selection_state.replaceAll("_", " ").toLowerCase()}</strong>
        </div>

        {selected ? (
          <div className="architecture-selected">
            <p className="eyebrow">SELECTED COMPONENT</p>
            <h3>{selected.label}</h3>
            <p>{selected.responsibility}</p>
            <dl>
              <div><dt>Trust boundary</dt><dd>{selected.trust_boundary}</dd></div>
              <div><dt>Role</dt><dd>{selected.execution_role.replaceAll("_", " ")}</dd></div>
              <div><dt>Inputs</dt><dd>{selected.input_contracts.join(", ") || "None listed"}</dd></div>
              <div><dt>Outputs</dt><dd>{selected.output_contracts.join(", ") || "None listed"}</dd></div>
              <div><dt>Observed when</dt><dd>{selected.activates_on_event_types.join(", ") || "Post-run or interface state"}</dd></div>
            </dl>
          </div>
        ) : (
          <div className="empty-state small">
            <strong>Choose a component</strong>
            <p>You can use the accessible component list above or select a node in the diagram.</p>
          </div>
        )}
      </aside>
    </div>
  );
}
