import type { SafeRun } from "../api/types";

function runTone(run: SafeRun): string {
  if (run.errors > 0) return "danger";
  if (run.policy_blocks > 0) return "warning";
  if (run.completed) return "success";
  return "live";
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
          <p className="eyebrow">PERSISTED SAFE TELEMETRY</p>
          <h2>Run Explorer</h2>
        </div>
        {selectedRunId && liveRunId && (
          <button className="ghost-button" type="button" onClick={() => onSelect(null)}>
            Follow live run
          </button>
        )}
      </div>

      {loading ? (
        <p className="muted">Loading persisted runs…</p>
      ) : runs.length === 0 ? (
        <div className="empty-state small">
          <strong>No persisted runs</strong>
          <p>Runs appear here only after the backend has persisted a safe run projection.</p>
        </div>
      ) : (
        <div className="run-table-wrap">
          <table className="run-table">
            <thead>
              <tr>
                <th>Run</th>
                <th>State</th>
                <th>Decision</th>
                <th>Events</th>
                <th>Tools</th>
                <th>Blocks</th>
                <th>Errors</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => {
                const selected = run.run_id === (selectedRunId ?? liveRunId);
                return (
                  <tr
                    key={run.run_id}
                    className={selected ? "run-row-selected" : undefined}
                    onClick={() => onSelect(run.run_id === liveRunId ? null : run.run_id)}
                  >
                    <td><code>{run.run_id.slice(0, 18)}</code></td>
                    <td><span className={`run-state-pill state-${runTone(run)}`}>{run.completed ? "complete" : "active"}</span></td>
                    <td>{run.terminal_decision ?? "—"}</td>
                    <td>{run.event_count}</td>
                    <td>{run.tool_calls}</td>
                    <td>{run.policy_blocks}</td>
                    <td>{run.errors}</td>
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
