import type { SafeRun } from "../api/types";

function runTone(run: SafeRun): string {
  if (run.errors > 0) return "danger";
  if (run.policy_blocks > 0) return "warning";
  if (run.completed) return "success";
  return "live";
}

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

function statusDescription(run: SafeRun): string {
  if (run.errors > 0) return `${run.errors} recorded error${run.errors === 1 ? "" : "s"}`;
  if (run.policy_blocks > 0) return `${run.policy_blocks} safety block${run.policy_blocks === 1 ? "" : "s"}`;
  return run.completed ? "Finished normally" : "Still running";
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
  return (
    <article className="panel run-explorer-panel" aria-busy={loading}>
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">SAVED ANALYSES</p>
          <h2>Previous analyses</h2>
          <p className="section-supporting-copy">Choose an analysis by its order and result. Internal IDs stay hidden unless you open technical details.</p>
        </div>
        {selectedRunId && liveRunId && (
          <button className="ghost-button" type="button" onClick={() => onSelect(null)}>
            Return to current analysis
          </button>
        )}
      </div>

      {loading ? (
        <div className="empty-state small" role="status"><strong>Loading previous analyses…</strong><p>Saved results will appear here when they are ready.</p></div>
      ) : runs.length === 0 ? (
        <div className="empty-state small">
          <strong>No previous analyses yet</strong>
          <p>After you run an analysis, it will appear here so you can review it later.</p>
        </div>
      ) : (
        <div className="run-table-wrap">
          <table className="run-table friendly-run-table">
            <caption className="visually-hidden">Saved analyses, their status and result</caption>
            <thead>
              <tr>
                <th scope="col">Analysis</th>
                <th scope="col">Status</th>
                <th scope="col">Result</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run, index) => {
                const selected = run.run_id === (selectedRunId ?? liveRunId);
                const analysisNumber = runs.length - index;
                return (
                  <tr key={run.run_id} className={selected ? "run-row-selected" : undefined}>
                    <td>
                      <button
                        type="button"
                        className="run-select-button"
                        aria-current={selected ? "true" : undefined}
                        aria-label={`Analysis ${analysisNumber}: ${resultLabel(run)}. ${selected ? "Currently selected." : "Open analysis."}`}
                        onClick={() => onSelect(run.run_id === liveRunId ? null : run.run_id)}
                      >
                        <strong>Analysis {analysisNumber}</strong>
                        <small>{selected ? "Selected" : "Open analysis"}</small>
                        <span className="visually-hidden">{run.run_id.slice(0, 10)}</span>
                      </button>
                    </td>
                    <td>
                      <span className={`run-state-pill state-${runTone(run)}`}>{run.completed ? "Finished" : "In progress"}</span>
                      <small className="run-status-detail">{statusDescription(run)}</small>
                    </td>
                    <td>{resultLabel(run)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </article>
  );
}
