import { FormEvent, useMemo, useState } from "react";

import {
  completeSemanticReview,
  fetchSemanticReviewTask,
  withdrawSemanticReview,
} from "../api/client";
import type {
  HumanLabelReason,
  SemanticReviewAccepted,
  SemanticReviewAssignment,
  SemanticReviewWithdrawn,
  SemanticScore,
} from "../api/semanticReviewTypes";

const DEFECT_REASONS: HumanLabelReason[] = [
  "UNSUPPORTED_CLAIM",
  "CONTRADICTED_CLAIM",
  "UNCERTAINTY_OVERSTATED",
  "WRONG_OPERATIONAL_CONCLUSION",
  "MISSING_NEXT_STEP",
  "WEAK_PRIORITIZATION",
  "AMBIGUOUS_COMMUNICATION",
  "UNNECESSARY_INTERNAL_DETAIL",
  "UNSAFE_DISCLOSURE",
  "ESCALATION_UNJUSTIFIED",
  "ESCALATION_CONTEXT_INCOMPLETE",
  "HUMAN_ACTION_UNCLEAR",
];

function publicError(error: unknown): string {
  const message = error instanceof Error && error.message
    ? error.message
    : "semantic_review_request_failed";
  if (message === "semantic_review_no_task_available") {
    return "No eligible blinded review task is available for this reviewer right now.";
  }
  if (message === "semantic_review_assignment_not_found") {
    return "This review assignment is no longer active. Request another task to continue.";
  }
  if (message === "insufficient_permission") {
    return "This authenticated account does not have semantic-review permission.";
  }
  return message;
}

function reasonLabel(reason: HumanLabelReason): string {
  return reason.toLowerCase().replaceAll("_", " ");
}

type TerminalState = SemanticReviewAccepted | SemanticReviewWithdrawn;

export function SemanticReviewCollector() {
  const [assignment, setAssignment] = useState<SemanticReviewAssignment | null>(null);
  const [score, setScore] = useState<SemanticScore | null>(null);
  const [reasons, setReasons] = useState<HumanLabelReason[]>([]);
  const [terminal, setTerminal] = useState<TerminalState | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const effectiveReasons = useMemo<HumanLabelReason[]>(() => {
    if (score === 2) return ["NO_MATERIAL_DEFECT"];
    return reasons;
  }, [score, reasons]);

  const loadNext = async () => {
    if (loading || submitting) return;
    setLoading(true);
    setError(null);
    setTerminal(null);
    try {
      // Explicit reviewer intent is required before the server allocates/exposes a task. Mounting
      // the product UI therefore does not consume a blinded review assignment.
      const next = await fetchSemanticReviewTask();
      setAssignment(next);
      setScore(null);
      setReasons([]);
    } catch (loadError) {
      setAssignment(null);
      setError(publicError(loadError));
    } finally {
      setLoading(false);
    }
  };

  const chooseScore = (next: SemanticScore) => {
    setScore(next);
    setReasons([]);
  };

  const toggleReason = (reason: HumanLabelReason) => {
    setReasons((current) => current.includes(reason)
      ? current.filter((item) => item !== reason)
      : [...current, reason]);
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!assignment || score === null || submitting) return;
    if (score < 2 && effectiveReasons.length === 0) return;
    setSubmitting(true);
    setError(null);
    try {
      const accepted = await completeSemanticReview(assignment.assignment_id, {
        score,
        reason_codes: effectiveReasons,
      });
      setTerminal(accepted);
      setAssignment(null);
      setScore(null);
      setReasons([]);
    } catch (submitError) {
      // A label write is never auto-retried: the server remains authoritative for assignment state.
      setError(publicError(submitError));
    } finally {
      setSubmitting(false);
    }
  };

  const withdraw = async () => {
    if (!assignment || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const withdrawn = await withdrawSemanticReview(assignment.assignment_id);
      setTerminal(withdrawn);
      setAssignment(null);
      setScore(null);
      setReasons([]);
    } catch (withdrawError) {
      setError(publicError(withdrawError));
    } finally {
      setSubmitting(false);
    }
  };

  const task = assignment?.task ?? null;
  const submitDisabled = submitting
    || score === null
    || (score < 2 && effectiveReasons.length === 0);

  return (
    <section className="panel pilot-panel" aria-labelledby="semantic-review-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">HELD-OUT HUMAN CALIBRATION</p>
          <h2 id="semantic-review-heading">Blind semantic review</h2>
        </div>
        <span className="count-pill">reviewer-safe</span>
      </div>

      <p className="pilot-intro">
        Score only the sanitized operational output shown here. Scenario identity, split/group,
        reviewer slot, prior labels and whether a task needs adjudication are intentionally hidden.
      </p>

      {!assignment && !terminal && (
        <div className="pilot-empty">
          <strong>No active semantic review in this browser.</strong>
          <p>
            Requesting a task creates one authenticated blinded assignment. Opening this page does
            not allocate or expose calibration material.
          </p>
          <button
            type="button"
            onClick={loadNext}
            disabled={loading || submitting}
            data-testid="semantic-review-start"
          >
            {loading ? "Assigning…" : "Start blinded review"}
          </button>
        </div>
      )}

      {terminal && !assignment && (
        <div className="pilot-completion" aria-live="polite" data-testid="semantic-review-completion">
          <span className={`pilot-status ${terminal.state === "COMPLETED" ? "pilot-status-valid" : "pilot-status-withdrawn"}`}>
            {terminal.state}
          </span>
          <div>
            <strong>Review state persisted.</strong>
            <p>
              No agreement, adjudication status, gold label or evaluator score is shown between
              tasks, so later judgments remain blind.
            </p>
          </div>
          <button
            type="button"
            className="ghost-button"
            onClick={loadNext}
            disabled={loading}
            data-testid="semantic-review-next"
          >
            {loading ? "Assigning…" : "Request another review"}
          </button>
        </div>
      )}

      {task && assignment && (
        <div className="pilot-task" data-testid="semantic-review-active">
          <article className="pilot-ticket">
            <div className="pilot-assistance-heading">
              <div>
                <p className="eyebrow">DIMENSION</p>
                <strong data-testid="semantic-review-dimension">{task.dimension}</strong>
              </div>
              <span>{task.response_mode}</span>
            </div>
            <p>{task.criterion_description}</p>
          </article>

          <article className="pilot-assistance" data-testid="semantic-review-output">
            <div className="pilot-assistance-heading">
              <p className="eyebrow">SANITIZED OPERATIONAL OUTPUT</p>
              <span>{task.terminal_decision}</span>
            </div>
            <p className="pilot-assistance-message">{task.terminal_message}</p>
            {task.safe_evidence_context.length > 0 ? (
              <ul data-testid="semantic-review-evidence">
                {task.safe_evidence_context.map((item, index) => (
                  <li key={`${index}:${item}`}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="muted">No additional sanitized evidence references were available.</p>
            )}
          </article>

          <form className="pilot-form" onSubmit={submit}>
            <fieldset disabled={submitting}>
              <legend>Rubric score</legend>
              {([0, 1, 2] as SemanticScore[]).map((value) => {
                const anchor = value === 0
                  ? task.score_0_anchor
                  : value === 1
                    ? task.score_1_anchor
                    : task.score_2_anchor;
                return (
                  <label key={value} className="semantic-score-option">
                    <input
                      type="radio"
                      name="semantic-score"
                      value={value}
                      checked={score === value}
                      onChange={() => chooseScore(value)}
                      data-testid={`semantic-review-score-${value}`}
                    />
                    <span><strong>{value}</strong> — {anchor}</span>
                  </label>
                );
              })}
            </fieldset>

            {score !== null && score < 2 && (
              <fieldset disabled={submitting} data-testid="semantic-review-reasons">
                <legend>Material defect reason(s)</legend>
                {DEFECT_REASONS.map((reason) => (
                  <label key={reason} className="semantic-reason-option">
                    <input
                      type="checkbox"
                      checked={reasons.includes(reason)}
                      onChange={() => toggleReason(reason)}
                      value={reason}
                    />
                    <span>{reasonLabel(reason)}</span>
                  </label>
                ))}
              </fieldset>
            )}

            {score === 2 && (
              <p className="muted" data-testid="semantic-review-no-defect">
                Score 2 is recorded with the canonical NO_MATERIAL_DEFECT reason.
              </p>
            )}

            <div className="pilot-form-footer">
              <span>One blinded semantic judgment</span>
              <button
                type="submit"
                disabled={submitDisabled}
                data-testid="semantic-review-submit"
              >
                {submitting ? "Persisting…" : "Save blinded review"}
              </button>
            </div>
          </form>

          <div className="pilot-invalid-actions">
            <div>
              <strong>Do not want to score this assignment?</strong>
              <p>Withdraw it without creating a semantic label. The same task will not be shown to this reviewer again.</p>
            </div>
            <button
              className="ghost-button danger-button"
              type="button"
              disabled={submitting}
              onClick={withdraw}
              data-testid="semantic-review-withdraw"
            >
              Withdraw review
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="error-banner pilot-error" role="alert" data-testid="semantic-review-error">
          {error}
        </div>
      )}
    </section>
  );
}