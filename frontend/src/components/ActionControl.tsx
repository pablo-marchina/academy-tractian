import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { confirmAction, fetchProductionHealth, fetchRunActions } from "../api/client";
import type { ActionExecutionAccepted, PendingActionSafe } from "../api/actionTypes";
import type { RunAccepted } from "../api/types";

function actionTone(state: PendingActionSafe["state"]): string {
  if (state === "ACCEPTED") return "health-good";
  if (state === "UNCERTAIN" || state === "BLOCKED" || state === "NOT_ACCEPTED") return "health-bad";
  return "health-unknown";
}

function asRunAccepted(action: ActionExecutionAccepted): RunAccepted {
  return {
    run_id: action.execution_run_id,
    status: "accepted",
    stream_path: action.stream_path,
    run_path: action.run_path,
    execution_path: action.execution_path,
  };
}

export function ActionControl({
  selectedRunId,
  onFollowExecution,
}: {
  selectedRunId: string | null;
  onFollowExecution: (run: RunAccepted) => void;
}) {
  const queryClient = useQueryClient();
  const actionsQuery = useQuery({
    queryKey: ["run-actions", selectedRunId],
    queryFn: () => fetchRunActions(selectedRunId!),
    enabled: Boolean(selectedRunId),
    refetchInterval: selectedRunId ? 1_000 : false,
    retry: false,
  });
  const healthQuery = useQuery({
    queryKey: ["production-health"],
    queryFn: fetchProductionHealth,
    refetchInterval: 3_000,
  });
  const actionSwitch = healthQuery.data?.measured.controls?.action_kill_switch;
  const confirmMutation = useMutation({
    mutationFn: confirmAction,
    onSuccess: async (accepted) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["run-actions", selectedRunId] }),
        queryClient.invalidateQueries({ queryKey: ["runs"] }),
        queryClient.invalidateQueries({ queryKey: ["production-health"] }),
      ]);
      onFollowExecution(asRunAccepted(accepted));
    },
  });

  if (!selectedRunId) {
    return (
      <article className="panel operations-panel action-control-panel">
        <div className="section-heading compact"><div><p className="eyebrow">CONSEQUENTIAL ACTIONS</p><h2>Action Control</h2></div></div>
        <div className="empty-state small"><strong>No run selected</strong><p>Select a run to inspect pending or executed action custody projections.</p></div>
      </article>
    );
  }

  if (actionsQuery.error) {
    return (
      <article className="panel operations-panel action-control-panel">
        <div className="section-heading compact"><div><p className="eyebrow">CONSEQUENTIAL ACTIONS</p><h2>Action Control</h2></div></div>
        <div className="empty-state small"><strong>Action surface unavailable</strong><p>The selected product API did not return a safe action projection for this run.</p></div>
      </article>
    );
  }

  return (
    <article className="panel operations-panel action-control-panel">
      <div className="section-heading compact">
        <div><p className="eyebrow">TWO-PHASE EXECUTION</p><h2>Action Control</h2></div>
        <span className={`health-status ${actionSwitch?.engaged ? "health-unknown" : "health-good"}`}>
          {actionSwitch?.engaged ? "kill switch engaged" : "confirmed execution enabled"}
        </span>
      </div>
      <p className="panel-copy">The agent may propose an action, but the exact payload remains in private custody. This UI receives only an opaque action id, fingerprint, risk and state. Confirmation cannot change tool arguments or authorization.</p>
      {!actionsQuery.data?.items.length ? (
        <div className="empty-state small"><strong>No consequential action for this run</strong><p>No eligible action proposal has entered private confirmation custody.</p></div>
      ) : (
        <div className="action-card-list">
          {actionsQuery.data.items.map((action) => {
            const canConfirm = action.state === "PENDING_CONFIRMATION" && actionSwitch?.engaged === false;
            const pendingThis = confirmMutation.isPending && confirmMutation.variables === action.action_id;
            return (
              <div className="action-card" key={action.action_id}>
                <div className="action-card-heading">
                  <div><span className="origin-badge">{action.impact}</span><strong>{action.tool_name}</strong></div>
                  <span className={`health-status ${actionTone(action.state)}`}>{action.state}</span>
                </div>
                <dl>
                  <div><dt>action id</dt><dd title={action.action_id}>{action.action_id}</dd></div>
                  <div><dt>fingerprint</dt><dd title={action.action_fingerprint}>{action.action_fingerprint.slice(0, 16)}…</dd></div>
                  <div><dt>permissions</dt><dd>{action.required_permissions.join(", ") || "none"}</dd></div>
                  <div><dt>confirmation</dt><dd>{action.confirmation_required ? "exact operator confirmation required" : "not required"}</dd></div>
                  <div><dt>execution run</dt><dd>{action.execution_run_id ?? "not executed"}</dd></div>
                </dl>
                {action.state === "PENDING_CONFIRMATION" && (
                  <button
                    type="button"
                    className="action-confirm-button"
                    disabled={!canConfirm || pendingThis}
                    onClick={() => confirmMutation.mutate(action.action_id)}
                  >
                    {pendingThis ? "Confirming exact action…" : actionSwitch?.engaged ? "Action kill switch engaged" : "Confirm exact action"}
                  </button>
                )}
                {action.execution_run_id && (
                  <button
                    type="button"
                    className="ghost-button action-follow-button"
                    onClick={() => onFollowExecution({
                      run_id: action.execution_run_id!,
                      status: "accepted",
                      stream_path: `/api/stream?run_id=${encodeURIComponent(action.execution_run_id!)}`,
                      run_path: `/api/runs/${encodeURIComponent(action.execution_run_id!)}`,
                      execution_path: `/api/runs/${encodeURIComponent(action.execution_run_id!)}/execution`,
                    })}
                  >Follow execution run</button>
                )}
              </div>
            );
          })}
        </div>
      )}
      {confirmMutation.error && <div className="error-banner">{confirmMutation.error.message}</div>}
    </article>
  );
}
