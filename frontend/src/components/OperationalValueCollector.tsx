import { FormEvent, useState } from "react";

import {
  completeOperationalValueTask,
  fetchOperationalValueTask,
  terminateOperationalValueTask,
} from "../api/client";
import type {
  HumanPilotTerminationStatus,
  OperationalPilotAssignment,
  OperationalPilotCompletionAccepted,
  OperationalPilotDecision,
} from "../api/operationalValueTypes";

const DECISIONS: OperationalPilotDecision[] = [
  "ORIENT",
  "INVESTIGATE",
  "ACT_REPROCESS",
  "ACT_REQUEST_SPECIALIST",
  "ACT_UPDATE_CONFIG",
  "ACT_REQUEST_RETRAINING",
  "ESCALATE_HUMAN",
  "ASK_CLARIFICATION",
  "ABSTAIN",
];

function publicError(error: unknown): string {
  const message = error instanceof Error && error.message
    ? error.message
    : "operational_pilot_request_failed";
  if (message === "operational_pilot_no_task_available") {
    return "No eligible measured task is available for this operator right now.";
  }
  if (message === "operational_pilot_timer_session_lost") {
    return "The authoritative server timer was lost, so this trial was invalidated instead of receiving a fabricated duration. Start another task to continue.";
  }
  if (message === "operational_pilot_assignment_not_found") {
    return "This measured assignment is no longer active. Start another task to continue.";
  }
  if (message === "operational_pilot_recovery_unavailable") {
    return "The measured-task service cannot safely reconcile its timing state right now.";
  }
  return message;
}

export function OperationalValueCollector() {
  const [assignment, setAssignment] = useState<OperationalPilotAssignment | null>(null);
  const [decision, setDecision] = useState<OperationalPilotDecision | "">("");
  const [summary, setSummary] = useState("");
  const [completion, setCompletion] = useState<OperationalPilotCompletionAccepted | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadNext = async () => {
    if (loading || submitting) return;
    setLoading(true);
    setError(null);
    setCompletion(null);
    try {
      // This explicit operator action is the only browser path that starts a measurement. The
      // browser never keeps an authoritative timer and never auto-loads a study task on mount.
      const next = await fetchOperationalValueTask();
      setAssignment(next);
      setDecision("");
      setSummary("");
    } catch (loadError) {
      setAssignment(null);
      setError(publicError(loadError));
    } finally {
      setLoading(false);
    }
  };

  const submitValid = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalizedSummary = summary.trim();
    if (!assignment || !decision || !normalizedSummary || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const accepted = await completeOperationalValueTask(assignment.assignment_id, {
        terminal_decision: decision,
        conclusion_summary: normalizedSummary,
      });
      setCompletion(accepted);
      setAssignment(null);
      setDecision("");
      setSummary("");
    } catch (submitError) {
      // Never auto-retry a measurement completion. The server owns assignment/timer state and
      // decides whether the trial remains recoverable or becomes a technical failure.
      setError(publicError(submitError));
    } finally {
      setSubmitting(false);
    }
  };

  const terminate = async (status: HumanPilotTerminationStatus) => {
    if (!assignment || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const accepted = await terminateOperationalValueTask(assignment.assignment_id, { status });
      setCompletion(accepted);
      setAssignment(null);
      setDecision("");
      setSummary("");
    } catch (terminationError) {
      // Persist-first server semantics keep the authoritative timer alive if the database write
      // fails. The UI therefore surfaces the error and never guesses whether termination worked.
      setError(publicError(terminationError));
    } finally {
      setSubmitting(false);
    }
  };

  const assistance = assignment?.task.assistance ?? null;

  return (
    <section className="panel pilot-panel" aria-labelledby="operational-value-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">CONTROLLED DEV PILOT</p>
          <h2 id="operational-value-heading">Engineer effort study</h2>
        </div>
        <span className="count-pill">server-timed</span>
      </div>

      <p className="pilot-intro">
        Use this surface only as a study participant. Timing and assignment custody are controlled
        by the server; private experimental metadata is intentionally not rendered here.
      </p>

      {!assignment && !completion && (
        <div className="pilot-empty">
          <strong>No active study task in this browser.</strong>
          <p>
            Starting a task creates the authenticated assignment and begins the authoritative
            server-side measurement interval. Opening this page does not start a timer.
          </p>
          <button
            type="button"
            onClick={loadNext}
            disabled={loading || submitting}
            data-testid="pilot-start"
          >
            {loading ? "Assigning…" : "Start measured task"}
          </button>
        </div>
      )}

      {completion && !assignment && (
        <div className="pilot-completion" aria-live="polite" data-testid="pilot-completion">
          <span className={`pilot-status pilot-status-${completion.status.toLowerCase()}`}>
            {completion.status}
          </span>
          <div>
            <strong>Trial state persisted.</strong>
            <p>
              No study score or elapsed-time feedback is shown between tasks, so later trials are
              not influenced by knowledge of earlier measured performance.
            </p>
          </div>
          {completion.status !== "WITHDRAWN" && (
            <button
              type="button"
              className="ghost-button"
              onClick={loadNext}
              disabled={loading}
              data-testid="pilot-next"
            >
              {loading ? "Assigning…" : "Start another task"}
            </button>
          )}
        </div>
      )}

      {assignment && (
        <div className="pilot-task" data-testid="pilot-active-task">
          <article className="pilot-ticket">
            <p className="eyebrow">CUSTOMER TICKET</p>
            <p>{assignment.task.ticket_request}</p>
          </article>

          {assistance ? (
            <article className="pilot-assistance" data-testid="pilot-assistance">
              <div className="pilot-assistance-heading">
                <p className="eyebrow">SAFE AGENT ASSISTANCE</p>
                <span>{assistance.terminal_decision}</span>
              </div>
              <p className="pilot-assistance-message">{assistance.terminal_message}</p>
              {assistance.safe_evidence_context.length > 0 && (
                <ul>
                  {assistance.safe_evidence_context.map((evidence, index) => (
                    <li key={`${index}:${evidence}`}>{evidence}</li>
                  ))}
                </ul>
              )}
            </article>
          ) : (
            <div className="pilot-manual-note" data-testid="pilot-manual">
              Complete this investigation without agent assistance.
            </div>
          )}

          <form className="pilot-form" onSubmit={submitValid}>
            <label htmlFor="pilot-decision">Operational decision</label>
            <select
              id="pilot-decision"
              value={decision}
              onChange={(event) => setDecision(event.target.value as OperationalPilotDecision | "")}
              disabled={submitting}
              data-testid="pilot-decision"
            >
              <option value="">Select the decision reached</option>
              {DECISIONS.map((value) => (
                <option key={value} value={value}>{value}</option>
              ))}
            </select>

            <label htmlFor="pilot-summary">Operational conclusion</label>
            <textarea
              id="pilot-summary"
              value={summary}
              onChange={(event) => setSummary(event.target.value)}
              maxLength={10_000}
              rows={5}
              placeholder="Record the conclusion an engineer should act on, grounded only in the evidence available in this task."
              disabled={submitting}
              data-testid="pilot-summary"
            />
            <div className="pilot-form-footer">
              <span>{summary.length.toLocaleString()} / 10,000</span>
              <button
                type="submit"
                disabled={submitting || !decision || !summary.trim()}
                data-testid="pilot-submit"
              >
                {submitting ? "Persisting…" : "Record completed investigation"}
              </button>
            </div>
          </form>

          <div className="pilot-invalid-actions">
            <div>
              <strong>Trial became invalid?</strong>
              <p>
                Mark interruption for an external disruption. Withdraw if you want to stop this
                measured trial. Invalid trials are persisted without duration or conclusion.
              </p>
            </div>
            <div className="pilot-invalid-buttons">
              <button
                className="ghost-button"
                type="button"
                disabled={submitting}
                onClick={() => terminate("INTERRUPTED")}
                data-testid="pilot-interrupt"
              >
                Mark interrupted
              </button>
              <button
                className="ghost-button danger-button"
                type="button"
                disabled={submitting}
                onClick={() => terminate("WITHDRAWN")}
                data-testid="pilot-withdraw"
              >
                Withdraw trial
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="error-banner pilot-error" role="alert" data-testid="pilot-error">
          {error}
        </div>
      )}
    </section>
  );
}
