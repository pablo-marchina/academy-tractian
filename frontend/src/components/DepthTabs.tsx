import type { KeyboardEvent } from "react";

export type WorkspaceTabId = "results" | "evidence" | "investigation" | "engineering";

interface TabDefinition {
  id: WorkspaceTabId;
  number: string;
  label: string;
  description: string;
}

const TABS: readonly TabDefinition[] = [
  { id: "results", number: "01", label: "Results", description: "Answer & next step" },
  { id: "evidence", number: "02", label: "Evidence", description: "Why this answer" },
  { id: "investigation", number: "03", label: "Investigation", description: "Runtime & operations" },
  { id: "engineering", number: "04", label: "Engineering", description: "Architecture & evals" },
];

interface Props {
  activeTab: WorkspaceTabId;
  onChange: (tab: WorkspaceTabId) => void;
  evidenceCount: number;
  eventCount: number;
  hasEvaluation: boolean;
}

function tabStatus(tab: WorkspaceTabId, evidenceCount: number, eventCount: number, hasEvaluation: boolean): string | null {
  if (tab === "evidence" && evidenceCount > 0) return `${evidenceCount} refs`;
  if (tab === "investigation" && eventCount > 0) return `${eventCount} events`;
  if (tab === "engineering" && hasEvaluation) return "evaluated";
  return null;
}

export function DepthTabs({ activeTab, onChange, evidenceCount, eventCount, hasEvaluation }: Props) {
  const activate = (index: number) => {
    const next = TABS[index];
    onChange(next.id);
    window.requestAnimationFrame(() => document.getElementById(`workspace-tab-${next.id}`)?.focus());
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    let nextIndex: number | null = null;
    if (event.key === "ArrowRight") nextIndex = (index + 1) % TABS.length;
    if (event.key === "ArrowLeft") nextIndex = (index - 1 + TABS.length) % TABS.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = TABS.length - 1;
    if (nextIndex === null) return;
    event.preventDefault();
    activate(nextIndex);
  };

  return (
    <nav className="depth-navigation" aria-label="Product depth">
      <div className="depth-navigation-copy">
        <p className="eyebrow">PROGRESSIVE DEPTH</p>
        <strong>Start with the answer. Go deeper only when you need to.</strong>
        <span>Every layer keeps the same persisted run and observability context.</span>
      </div>
      <div className="depth-tablist" role="tablist" aria-label="Product depth layers">
        {TABS.map((tab, index) => {
          const selected = activeTab === tab.id;
          const status = tabStatus(tab.id, evidenceCount, eventCount, hasEvaluation);
          return (
            <button
              type="button"
              role="tab"
              id={`workspace-tab-${tab.id}`}
              aria-selected={selected}
              aria-controls={`workspace-panel-${tab.id}`}
              tabIndex={selected ? 0 : -1}
              className={`depth-tab ${selected ? "active" : ""}`}
              key={tab.id}
              onClick={() => onChange(tab.id)}
              onKeyDown={(event) => handleKeyDown(event, index)}
            >
              <span className="depth-tab-number">{tab.number}</span>
              <span className="depth-tab-copy">
                <strong>{tab.label}</strong>
                <small>{tab.description}</small>
              </span>
              {status && <span className="depth-tab-status">{status}</span>}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
