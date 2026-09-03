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

const DECISIONS: OperationalPilotDecision[] = ["FINAL", "CLARIFY", "ESCALATE", "ABSTAIN"];

function publicError(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  return "operational_pilot_request_failed";
}

export function OperationalValueCollector() {
  const [assignment, setAssignment] = useState<OperationalPilotAssignment | null>(null);
  const [decision, setDecision] = useState<OperationalPilotDecision>("FINAL");
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
      const next = await fetchOperationalValueTask();
      setAssignment(next);
      setDecision("FINAL");
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
    const normalized = summary.trim();
    if (!assignment || !normalized || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const accepted = await completeOperationalValueTask(assignment.assignment_id, {
        terminal_decision: decision,
        conclusion_summary: normalized,
      });
      setCompletion(accepted);
      setAssignment(null);
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
      setSummary("");
    } catch (terminationError) {
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
          <p>Loading a task starts the authoritative server-side measurement interval.</p>
          <button type="button" onClick={loadNext} disabled={loading || submitting}>
            {loading ? "Assigning…" : "Load next assigned task"}
          </button>
        </div>
      )}

      {completion && !assignment && (
        <div className="pilot-completion" aria-live="polite">
          <span className={`pilot-status pilot-status-${completion.status.toLowerCase()}`}>
            {completion.status}
          </span>
          <div>
            <strong>Trial state persisted.</strong>
            <p>No study score or elapsed-time feedback is shown between tasks.</p>
          </div>
          <button type="button" className="ghost-button" onClick={loadNext} disabled={loading}>
            {loading ? "Assigning…" : "Load another task"}
          </button>
        </div>
      )}

      {assignment && (
        <div className="pilot-task" data-testid="operational-value-task">
          <article className="pilot-ticket">
            <p className="eyebrow">CUSTOMER TICKET</p>
            <p>{assignment.task.ticket_request}</p>
          </article>

          {assistance ? (
            <article className="pilot-assistance" data-testid="operational-value-assistance">
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
            <div className="pilot-manual-note" data-testid="operational-value-manual">
              Complete this investigation without agent assistance.
            </div>
          )}

          <form className="pilot-form" onSubmit={submitValid}>
            <label htmlFor="pilot-decision">Operational decision</label>
            <select
              id="pilot-decision"
              value={decision}
              onChange={(event) => setDecision(event.target.value as OperationalPilotDecision)}
              disabled={submitting}
            >
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
            />
            <div className="pilot-form-footer">
              <span>{summary.length.toLocaleString()} / 10,000</span>
              <button type="submit" disabled={submitting || !summary.trim()}>
                {submitting ? "Persisting…" : "Record completed investigation"}
              </button>
            </div>
          </form>

          <div className="pilot-invalid-actions">
            <div>
              <strong>Trial became invalid?</strong>
              <p>Use interruption for an external disruption; withdraw if you want to stop this trial.</p>
            </div>
            <div className="pilot-invalid-buttons">
              <button
                className="ghost-button"
                type="button"
                disabled={submitting}
                onClick={() => terminate("INTERRUPTED")}
              >
                Mark interrupted
              </button>
              <button
                className="ghost-button danger-button"
                type="button"
                disabled={submitting}
                onClick={() => terminate("WITHDRAWN")}
              >
                Withdraw trial
              </button>
            </div>
          </div>
        </div>
      )}

      {error && <div className="error-banner pilot-error" role="alert">{error}</div>}
    </section>
  );
}
