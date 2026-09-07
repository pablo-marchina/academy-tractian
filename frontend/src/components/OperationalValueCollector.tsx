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

function decisionLabel(value: string): string {
  const labels: Partial<Record<OperationalPilotDecision, string>> = {
    ORIENT: "Provide guidance",
    INVESTIGATE: "Investigate further",
    ACT_REPROCESS: "Reprocess the data",
    ACT_REQUEST_SPECIALIST: "Ask a specialist to review",
    ACT_UPDATE_CONFIG: "Update the configuration",
    ACT_REQUEST_RETRAINING: "Request model retraining",
    ESCALATE_HUMAN: "Escalate for human review",
    ASK_CLARIFICATION: "Ask for more information",
    ABSTAIN: "Do not conclude from the available evidence",
  };
  const known = labels[value as OperationalPilotDecision];
  if (known) return known;
  const words = value.replaceAll("_", " ").toLowerCase();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function publicError(error: unknown): string {
  const message = error instanceof Error && error.message
    ? error.message
    : "operational_pilot_request_failed";
  if (message === "operational_pilot_no_task_available") {
    return "No eligible measured task is available for this operator right now.";
  }
  if (message === "operational_pilot_timer_session_lost") {
    return "The server timer was lost, so this trial was invalidated instead of receiving an estimated duration. Start another task to continue.";
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
      setError(publicError(terminationError));
    } finally {
      setSubmitting(false);
    }
  };

  const assistance = assignment?.task.assistance ?? null;

  return (
    <section className="panel pilot-panel" aria-labelledby="operational-value-heading" aria-busy={loading || submitting}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">CONTROLLED RESEARCH TASK</p>
          <h2 id="operational-value-heading">Engineer effort study</h2>
          <p className="section-supporting-copy">Complete one investigation at a time. Start only when you are ready: the server begins timing after you request a task.</p>
        </div>
        <span className="count-pill">server-timed</span>
      </div>

      <div className="pilot-study-steps" aria-label="Study steps">
        <span><b>1</b> Start a task</span>
        <span><b>2</b> Reach a decision</span>
        <span><b>3</b> Record the conclusion</span>
      </div>

      <p className="pilot-intro">
        This surface is only for study participants. Timing and assignment records are controlled by the server, and private experimental metadata is intentionally hidden so it cannot influence later tasks.
      </p>

      {!assignment && !completion && (
        <div className="pilot-empty">
          <strong>No study task is active.</strong>
          <p>Opening this page does not start the timer. The measured interval begins only after you choose “Start measured task”.</p>
          <button type="button" onClick={loadNext} disabled={loading || submitting} data-testid="pilot-start">
            {loading ? "Preparing task…" : "Start measured task"}
          </button>
        </div>
      )}

      {completion && !assignment && (
        <div className="pilot-completion" aria-live="polite" data-testid="pilot-completion">
          <span className={`pilot-status pilot-status-${completion.status.toLowerCase()}`}>{completion.status}</span>
          <div>
            <strong>Task state saved.</strong>
            <p>No score or elapsed-time feedback is shown between tasks, so later trials are not influenced by earlier measured performance.</p>
          </div>
          {completion.status !== "WITHDRAWN" && (
            <button type="button" className="ghost-button" onClick={loadNext} disabled={loading} data-testid="pilot-next">
              {loading ? "Preparing task…" : "Start another task"}
            </button>
          )}
        </div>
      )}

      {assignment && (
        <div className="pilot-task" data-testid="pilot-active-task">
          <article className="pilot-ticket">
            <p className="eyebrow">CUSTOMER REQUEST</p>
            <p>{assignment.task.ticket_request}</p>
          </article>

          {assistance ? (
            <article className="pilot-assistance" data-testid="pilot-assistance">
              <div className="pilot-assistance-heading">
                <p className="eyebrow">AGENT ASSISTANCE</p>
                <span>{decisionLabel(assistance.terminal_decision)}</span>
              </div>
              <p className="pilot-assistance-message">{assistance.terminal_message}</p>
              {assistance.safe_evidence_context.length > 0 && (
                <ul aria-label="Evidence available to the participant">
                  {assistance.safe_evidence_context.map((evidence, index) => <li key={`${index}:${evidence}`}>{evidence}</li>)}
                </ul>
              )}
            </article>
          ) : (
            <div className="pilot-manual-note" data-testid="pilot-manual">Complete this investigation without agent assistance.</div>
          )}

          <form className="pilot-form" onSubmit={submitValid}>
            <label htmlFor="pilot-decision">What decision did you reach?</label>
            <select
              id="pilot-decision"
              value={decision}
              onChange={(event) => setDecision(event.target.value as OperationalPilotDecision | "")}
              disabled={submitting}
              data-testid="pilot-decision"
            >
              <option value="">Choose the decision that best matches your conclusion</option>
              {DECISIONS.map((value) => <option key={value} value={value}>{decisionLabel(value)}</option>)}
            </select>

            <label htmlFor="pilot-summary">What should the engineer know or do next?</label>
            <textarea
              id="pilot-summary"
              value={summary}
              onChange={(event) => setSummary(event.target.value)}
              maxLength={10_000}
              rows={5}
              placeholder="Record the conclusion an engineer should act on, using only the evidence available in this task."
              disabled={submitting}
              data-testid="pilot-summary"
            />
            <div className="pilot-form-footer">
              <span>{summary.length.toLocaleString()} / 10,000 characters</span>
              <button type="submit" disabled={submitting || !decision || !summary.trim()} data-testid="pilot-submit">
                {submitting ? "Saving investigation…" : "Record completed investigation"}
              </button>
            </div>
          </form>

          <div className="pilot-invalid-actions">
            <div>
              <strong>Could you not complete the task normally?</strong>
              <p>Use “Mark interrupted” for an external disruption. Use “Withdraw trial” if you choose to stop participating in this task. These states are saved without a valid measured conclusion.</p>
            </div>
            <div className="pilot-invalid-buttons">
              <button className="ghost-button" type="button" disabled={submitting} onClick={() => terminate("INTERRUPTED")} data-testid="pilot-interrupt">Mark interrupted</button>
              <button className="ghost-button danger-button" type="button" disabled={submitting} onClick={() => terminate("WITHDRAWN")} data-testid="pilot-withdraw">Withdraw trial</button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="error-banner pilot-error friendly-error" role="alert" data-testid="pilot-error">
          <strong>The study task could not be updated.</strong>
          <span>{error}</span>
        </div>
      )}
    </section>
  );
}
