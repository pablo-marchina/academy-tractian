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
    <article className="panel run-explorer-panel">
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">SAVED ANALYSES</p>
          <h2>Previous analyses</h2>
          <p className="section-supporting-copy">Open an earlier analysis to review its answer and evidence.</p>
        </div>
        {selectedRunId && liveRunId && (
          <button className="ghost-button" type="button" onClick={() => onSelect(null)}>
            Return to current analysis
          </button>
        )}
      </div>

      {loading ? (
        <p className="muted">Loading previous analyses…</p>
      ) : runs.length === 0 ? (
        <div className="empty-state small">
          <strong>No previous analyses yet</strong>
          <p>After you run an analysis, it will appear here so you can review it later.</p>
        </div>
      ) : (
        <div className="run-table-wrap">
          <table className="run-table friendly-run-table">
            <thead>
              <tr>
                <th>Analysis</th>
                <th>Status</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run, index) => {
                const selected = run.run_id === (selectedRunId ?? liveRunId);
                return (
                  <tr key={run.run_id} className={selected ? "run-row-selected" : undefined}>
                    <td>
                      <button
                        type="button"
                        className="run-select-button"
                        aria-current={selected ? "true" : undefined}
                        onClick={() => onSelect(run.run_id === liveRunId ? null : run.run_id)}
                      >
                        <strong>Analysis {runs.length - index}</strong>
                        <small title={run.run_id}>{run.run_id.slice(0, 10)}…</small>
                      </button>
                    </td>
                    <td><span className={`run-state-pill state-${runTone(run)}`}>{run.completed ? "Finished" : "In progress"}</span></td>
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
