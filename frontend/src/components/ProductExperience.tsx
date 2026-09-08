import type { ExecutionStatus, SafeEvent, SafeRun } from "../api/types";

interface Props {
  selectedRun: SafeRun | undefined;
  events: SafeEvent[];
  executionStatus: ExecutionStatus | undefined;
  connection: string;
  hasLiveRun: boolean;
  viewingHistorical: boolean;
  onOpenEvidence: () => void;
  onOpenTechnical: () => void;
  onStartNew: () => void;
}

function currentStage(
  run: SafeRun | undefined,
  events: SafeEvent[],
  executionStatus: ExecutionStatus | undefined,
  hasLiveRun: boolean,
): number {
  if (run?.completed || executionStatus === "completed") return 2;
  if (events.some((event) => event.event_type === "observation" || event.event_type === "tool_result" || event.event_type === "final_response")) return 1;
  if (hasLiveRun || executionStatus === "accepted" || executionStatus === "running") return 0;
  return -1;
}

function decisionTitle(decision: string | null | undefined, responseMode: string | null | undefined): string {
  if (decision === "ORIENT") {
    switch (responseMode) {
      case "complete": return "Analysis complete";
      case "partial": return "Part of the answer is supported";
      case "inconclusive": return "There is not enough data to conclude";
      case "conflict": return "The evidence points in different directions";
      case "unavailable": return "Required data is unavailable";
      default: return "Analysis result";
    }
  }
  switch (decision) {
    case "ASK_CLARIFICATION": return "More information is needed";
    case "ABSTAIN": return "There is not enough evidence yet";
    case "ESCALATE_HUMAN": return "A specialist should review this";
    default: return "Analysis result";
  }
}

function resultStatus(decision: string | null | undefined, responseMode: string | null | undefined): string {
  if (decision === "ESCALATE_HUMAN" || responseMode === "conflict") return "Needs attention";
  if (decision === "ABSTAIN" || decision === "ASK_CLARIFICATION" || responseMode === "partial" || responseMode === "inconclusive" || responseMode === "unavailable") return "Check before deciding";
  return "Ready to review";
}

function decisionNextStep(decision: string | null | undefined, responseMode: string | null | undefined): string {
  if (decision === "ORIENT") {
    switch (responseMode) {
      case "complete": return "Review the conclusion and its evidence before making an operational decision.";
      case "partial": return "Use only the supported part of the answer and verify the missing information before acting.";
      case "inconclusive": return "Check the missing or insufficient data, then run a follow-up analysis.";
      case "conflict": return "Review the conflicting observations with a qualified specialist before acting.";
      case "unavailable": return "Restore or provide the missing data source before relying on this analysis.";
      default: return "Review the conclusion and supporting evidence before using it operationally.";
    }
  }
  switch (decision) {
    case "ASK_CLARIFICATION": return "Add the information requested in the answer and start a new analysis.";
    case "ABSTAIN": return "Add the missing equipment, telemetry, time range or other evidence identified in the answer.";
    case "ESCALATE_HUMAN": return "Share this result and its evidence with a qualified specialist. The assistant intentionally did not guess.";
    default: return "Review the answer and its evidence before deciding what to do next.";
  }
}

export function ProductExperience({
  selectedRun,
  events,
  executionStatus,
  connection,
  hasLiveRun,
  viewingHistorical,
  onOpenEvidence,
  onOpenTechnical,
  onStartNew,
}: Props) {
  const hasRunContext = hasLiveRun || Boolean(selectedRun);
  const completed = Boolean(selectedRun?.completed);
  const stage = currentStage(selectedRun, events, executionStatus, hasLiveRun);

  if (!hasRunContext) return null;

  if (!completed) {
    const stages = ["Preparing the analysis", "Checking the available data", "Reviewing the result"];
    return (
      <section className="experience-shell task-experience-shell" aria-live="polite">
        <article className="task-progress">
          <h2>{viewingHistorical ? "Loading saved analysis" : "Analysing the available information"}</h2>
          <p>{viewingHistorical ? "The saved result will appear here when it is ready." : "You can stay on this page. The result will appear here automatically."}</p>
          <ol className="task-progress-list" aria-label="Analysis progress">
            {stages.map((label, index) => (
              <li key={label} className={index < stage ? "is-done" : index === stage ? "is-active" : ""}>
                <span className="task-progress-marker" aria-hidden="true">{index < stage ? "✓" : index + 1}</span>
                <strong>{label}</strong>
              </li>
            ))}
          </ol>
          {!viewingHistorical && connection && <span className="visually-hidden">Connection status: {connection}</span>}
        </article>
      </section>
    );
  }

  return (
    <section className="experience-shell task-experience-shell">
      <article className="task-outcome" data-testid="customer-outcome-summary">
        <span className="task-outcome-status">{resultStatus(selectedRun?.terminal_decision, selectedRun?.terminal_response_mode)}</span>
        <h1>{decisionTitle(selectedRun?.terminal_decision, selectedRun?.terminal_response_mode)}</h1>
        <p className="task-outcome-message">{selectedRun?.terminal_message || "No user-facing answer was saved for this analysis."}</p>

        <section className="task-next-step" aria-labelledby="next-step-heading">
          <h2 id="next-step-heading">What to do next</h2>
          <p>{decisionNextStep(selectedRun?.terminal_decision, selectedRun?.terminal_response_mode)}</p>
        </section>

        <div className="task-outcome-actions">
          <button type="button" className="task-primary-action" onClick={onOpenEvidence}>View evidence</button>
          <button type="button" className="task-secondary-action" onClick={onStartNew}>New analysis</button>
          <button type="button" className="task-tertiary-action" onClick={onOpenTechnical}>Technical details</button>
        </div>
      </article>
    </section>
  );
}
