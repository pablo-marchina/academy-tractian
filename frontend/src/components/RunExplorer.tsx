import type { SafeRun } from "../api/types";

function resultLabel(run: SafeRun): string {
  if (!run.completed) return "Analysis in progress";
  if (run.terminal_decision === "ASK_CLARIFICATION") return "More information needed";
  if (run.terminal_decision === "ABSTAIN") return "Not enough evidence";
  if (run.terminal_decision === "ESCALATE_HUMAN") return "Specialist review recommended";
  if (run.terminal_decision === "ORIENT") {
    if (run.terminal_response_mode === "complete") return "Answer ready";
    if (run.terminal_response_mode === "partial") return "Partial answer";
    if (run.terminal_response_mode === "conflict") return "Conflicting evidence";
    if (run.terminal_response_mode === "inconclusive") return "No reliable conclusion";
    if (run.terminal_response_mode === "unavailable") return "Data unavailable";
    return "Answer ready";
  }
  return "Analysis finished";
}

function preview(run: SafeRun): string {
  const message = run.terminal_message?.trim();
  if (!message) return run.completed ? "No saved answer text for this analysis." : "This analysis is still running.";
  return message.length > 150 ? `${message.slice(0, 147)}…` : message;
}

export function RunExplorer({
  runs,
  selectedRunId,
  liveRunId,
  loading,
  onSelect,
}: {
  runs: readonly SafeRun[];
  selectedRunId: string | null;
  liveRunId: string | null;
  loading: boolean;
  onSelect: (runId: string | null) => void;
}) {
  if (loading) {
    return <div className="task-empty" role="status">Loading saved analyses…</div>;
  }

  if (runs.length === 0) {
    return <div className="task-empty">No analyses yet. Start from Home and completed analyses will appear here.</div>;
  }

  return (
    <article className="run-explorer-panel task-run-explorer">
      {selectedRunId && liveRunId && (
        <button className="task-text-button" type="button" onClick={() => onSelect(null)}>
          Return to current analysis
        </button>
      )}
      <ol className="task-run-list" aria-label="Saved analyses">
        {runs.map((run, index) => {
          const selected = run.run_id === (selectedRunId ?? liveRunId);
          const analysisNumber = runs.length - index;
          return (
            <li className="task-run-item" key={run.run_id}>
              <button
                type="button"
                className="task-run-button"
                aria-current={selected ? "true" : undefined}
                aria-label={`Analysis ${analysisNumber}: ${resultLabel(run)}. Open analysis.`}
                onClick={() => onSelect(run.run_id === liveRunId ? null : run.run_id)}
              >
                <span className="task-run-main">
                  <strong>{resultLabel(run)}</strong>
                  <span>{preview(run)}</span>
                  <small>Analysis {analysisNumber} · {run.completed ? "Finished" : "In progress"}</small>
                  <span className="visually-hidden">Run ID {run.run_id}</span>
                </span>
                <span className="task-run-arrow" aria-hidden="true">›</span>
              </button>
            </li>
          );
        })}
      </ol>
    </article>
  );
}
