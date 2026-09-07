import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { confirmAction, fetchProductionHealth, fetchRunActions } from "../api/client";
import type { ActionExecutionAccepted, PendingActionSafe } from "../api/actionTypes";
import type { RunAccepted } from "../api/types";

function actionTone(state: PendingActionSafe["state"]): string {
  if (state === "ACCEPTED") return "health-good";
  if (state === "UNCERTAIN" || state === "BLOCKED" || state === "NOT_ACCEPTED") return "health-bad";
  return "health-unknown";
}

function actionStateLabel(state: PendingActionSafe["state"]): string {
  switch (state) {
    case "PENDING_CONFIRMATION": return "Waiting for your confirmation";
    case "CONFIRMED": return "Confirmed";
    case "EXECUTING": return "Running";
    case "ACCEPTED": return "Accepted by the external service";
    case "BLOCKED": return "Blocked for safety";
    case "NOT_ACCEPTED": return "Not accepted";
    case "UNCERTAIN": return "Outcome needs verification";
  }
}

function impactLabel(impact: string): string {
  const normalized = impact.toLowerCase();
  if (normalized === "high") return "High impact";
  if (normalized === "medium") return "Medium impact";
  if (normalized === "low") return "Low impact";
  return `${impact.replaceAll("_", " ")} impact`;
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

  const heading = (
    <div className="section-heading compact">
      <div>
        <p className="eyebrow">GOVERNED EXTERNAL ACTIONS</p>
        <h2>Action Control</h2>
        <p className="section-supporting-copy">Review what an action would do before anything is confirmed. The browser cannot change the protected payload.</p>
      </div>
      {actionSwitch && (
        <span className={`health-status ${actionSwitch.engaged ? "health-unknown" : "health-good"}`}>
          {actionSwitch.engaged ? "External actions paused" : "Confirmation path available"}
        </span>
      )}
    </div>
  );

  if (!selectedRunId) {
    return (
      <article className="panel operations-panel action-control-panel">
        {heading}
        <div className="empty-state small"><strong>No analysis selected</strong><p>Select an analysis to see whether it proposed an external action.</p></div>
      </article>
    );
  }

  if (actionsQuery.isLoading) {
    return (
      <article className="panel operations-panel action-control-panel" aria-busy="true">
        {heading}
        <div className="empty-state small"><strong>Checking action state…</strong><p>Confirmation stays unavailable until the protected action record is loaded.</p></div>
      </article>
    );
  }

  if (actionsQuery.error) {
    return (
      <article className="panel operations-panel action-control-panel">
        {heading}
        <div className="error-banner friendly-error" role="alert">
          <strong>Action information is unavailable.</strong>
          <span>Nothing can be confirmed from this screen until the safe action record loads.</span>
          <button className="ghost-button" type="button" onClick={() => void actionsQuery.refetch()}>Try again</button>
        </div>
      </article>
    );
  }

  return (
    <article className="panel operations-panel action-control-panel">
      {heading}
      <div className="action-safety-summary" role="note">
        <strong>Confirmation is a separate safety step.</strong>
        <p>The agent may propose an action, but authorization, target, exact payload and idempotency remain server-controlled. A confirmation approves only the exact fingerprint shown here.</p>
      </div>
      {!actionsQuery.data?.items.length ? (
        <div className="empty-state small"><strong>No consequential action for this run</strong><p>This analysis did not create an external action that needs operator confirmation.</p></div>
      ) : (
        <div className="action-card-list">
          {actionsQuery.data.items.map((action) => {
            const canConfirm = action.state === "PENDING_CONFIRMATION" && actionSwitch?.engaged === false;
            const pendingThis = confirmMutation.isPending && confirmMutation.variables === action.action_id;
            return (
              <section className="action-card" key={action.action_id} aria-label={`${action.tool_name} action`}>
                <div className="action-card-heading">
                  <div>
                    <span className="origin-badge">{impactLabel(action.impact)}</span>
                    <strong>{action.tool_name.replaceAll("_", " ")}</strong>
                  </div>
                  <span className={`health-status ${actionTone(action.state)}`}>{actionStateLabel(action.state)}</span>
                </div>

                {action.state === "PENDING_CONFIRMATION" && (
                  <div className="action-confirmation-note">
                    <strong>Before you confirm</strong>
                    <p>Confirm only if this is the intended action for the intended target. If anything is unclear, do not continue.</p>
                  </div>
                )}

                <dl className="action-summary-list">
                  <div><dt>Impact</dt><dd>{impactLabel(action.impact)}</dd></div>
                  <div><dt>Required permission</dt><dd>{action.required_permissions.join(", ") || "No additional permission listed"}</dd></div>
                  <div><dt>Confirmation</dt><dd>{action.confirmation_required ? "Required before execution" : "Not required by this action"}</dd></div>
                  <div><dt>Execution</dt><dd>{action.execution_run_id ? "Execution record available" : "Not executed"}</dd></div>
                </dl>

                <details className="technical-disclosure compact-disclosure">
                  <summary>Technical identifiers</summary>
                  <dl className="detail-list">
                    <div><dt>Action ID</dt><dd title={action.action_id}>{action.action_id}</dd></div>
                    <div><dt>Fingerprint</dt><dd title={action.action_fingerprint}>{action.action_fingerprint}</dd></div>
                    <div><dt>Internal state</dt><dd>{action.state}</dd></div>
                    <div><dt>Execution run</dt><dd>{action.execution_run_id ?? "—"}</dd></div>
                  </dl>
                </details>

                {action.state === "PENDING_CONFIRMATION" && (
                  <button
                    type="button"
                    className="action-confirm-button"
                    disabled={!canConfirm || pendingThis}
                    aria-describedby={`action-confirm-help-${action.action_id}`}
                    onClick={() => confirmMutation.mutate(action.action_id)}
                  >
                    {pendingThis ? "Confirming exact action…" : actionSwitch?.engaged ? "Action kill switch engaged" : "Confirm exact action"}
                  </button>
                )}
                {action.state === "PENDING_CONFIRMATION" && (
                  <small id={`action-confirm-help-${action.action_id}`} className="action-confirm-help">
                    {actionSwitch?.engaged ? "External actions are currently paused by the system." : "This confirms only the server-held action that matches this fingerprint."}
                  </small>
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
                  >Open execution details</button>
                )}
              </section>
            );
          })}
        </div>
      )}
      {confirmMutation.error && (
        <div className="error-banner friendly-error" role="alert">
          <strong>The action was not confirmed.</strong>
          <span>No success is assumed. Review the current action state before trying anything else.</span>
          <details><summary>Technical detail</summary><code>{confirmMutation.error.message}</code></details>
        </div>
      )}
    </article>
  );
}
