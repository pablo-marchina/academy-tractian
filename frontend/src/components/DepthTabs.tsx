import type { KeyboardEvent } from "react";

export type WorkspaceTabId = "results" | "evidence" | "investigation" | "engineering";

interface TabDefinition {
  id: WorkspaceTabId;
  number: string;
  label: string;
  description: string;
}

const TABS: readonly TabDefinition[] = [
  { id: "results", number: "1", label: "Overview", description: "Answer and next step" },
  { id: "evidence", number: "2", label: "Why this answer?", description: "Evidence used" },
  { id: "investigation", number: "3", label: "History", description: "Saved analyses" },
  { id: "engineering", number: "4", label: "Technical details", description: "For specialists" },
];

interface Props {
  activeTab: WorkspaceTabId;
  onChange: (tab: WorkspaceTabId) => void;
  evidenceCount: number;
  eventCount: number;
  hasEvaluation: boolean;
}

function tabStatus(tab: WorkspaceTabId, evidenceCount: number, hasEvaluation: boolean): string | null {
  if (tab === "evidence" && evidenceCount > 0) return `${evidenceCount} source${evidenceCount === 1 ? "" : "s"}`;
  if (tab === "engineering" && hasEvaluation) return "evaluation ready";
  return null;
}

export function DepthTabs({ activeTab, onChange, evidenceCount, hasEvaluation }: Props) {
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
    <nav className="depth-navigation" aria-label="Analysis sections">
      <div className="depth-navigation-copy">
        <strong>Start with the answer.</strong>
        <span>Open more detail only when it helps your decision.</span>
      </div>
      <div className="depth-tablist" role="tablist" aria-label="Analysis sections">
        {TABS.map((tab, index) => {
          const selected = activeTab === tab.id;
          const status = tabStatus(tab.id, evidenceCount, hasEvaluation);
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
              <span className="depth-tab-number" aria-hidden="true">{tab.number}</span>
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
