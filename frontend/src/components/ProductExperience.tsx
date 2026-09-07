import { useQuery } from "@tanstack/react-query";

import { fetchRelease0Capabilities } from "../api/release0Client";
import type { ExecutionStatus, SafeEvent, SafeRun } from "../api/types";

interface Props {
  selectedRun: SafeRun | undefined;
  events: SafeEvent[];
  executionStatus: ExecutionStatus | undefined;
  connection: string;
  hasLiveRun: boolean;
  viewingHistorical: boolean;
  onUsePrompt: (prompt: string) => void;
  onOpenEvidence: () => void;
  onOpenTechnical: () => void;
}

const STAGES = [
  ["PREPARING", "Getting ready"],
  ["DECIDING", "Understanding your question"],
  ["READING", "Checking available data"],
  ["REVIEWING", "Comparing what we found"],
  ["EVALUATING", "Running safety checks"],
  ["COMPLETE", "Ready"],
] as const;

const STARTER_EXAMPLES = [
  {
    intent_id: "STARTER_CONTEXT",
    label: "Help me understand what is happening",
    release0_behavior: "EDIT_BEFORE_RUNNING",
    prompt_template:
      "Help me understand this industrial situation using only evidence you can actually inspect. State what is known, what is uncertain, and what additional identifier or evidence would help if the context is incomplete.",
  },
  {
    intent_id: "STARTER_INVESTIGATE",
    label: "Investigate which evidence matters most",
    release0_behavior: "EDIT_BEFORE_RUNNING",
    prompt_template:
      "Investigate this industrial issue using the relevant read-only evidence available to you. Follow the evidence, do not guess unsupported facts, and return a concise customer-safe conclusion or stop safely if the evidence is insufficient.",
  },
  {
    intent_id: "STARTER_REVIEW",
    label: "Check whether a maintenance action is supported",
    release0_behavior: "NO_EXTERNAL_ACTIONS",
    prompt_template:
      "Review whether the operational action I am considering is supported by the available evidence. Do not execute anything. Explain what evidence supports or contradicts the action and what a human operator should verify next.",
  },
] as const;

function currentStage(
  run: SafeRun | undefined,
  events: SafeEvent[],
  executionStatus: ExecutionStatus | undefined,
  hasLiveRun: boolean,
): number {
  if (run?.completed || executionStatus === "completed") return 5;
  if (events.some((event) => event.event_type === "final_response" || event.event_type === "run_finished")) return 4;
  if (events.some((event) => event.event_type === "observation" || event.event_type === "tool_result")) return 3;
  if (events.some((event) => event.event_type === "tool_call")) return 2;
  if (events.some((event) => event.event_type === "model_call")) return 1;
  if (hasLiveRun || executionStatus === "accepted" || executionStatus === "running") return 0;
  return -1;
}

function decisionTitle(
  decision: string | null | undefined,
  responseMode: string | null | undefined,
): string {
  if (decision === "ORIENT") {
    switch (responseMode) {
      case "complete": return "Analysis complete";
      case "partial": return "We found part of the answer";
      case "inconclusive": return "The data is not enough to conclude";
      case "conflict": return "The data points in different directions";
      case "unavailable": return "Some required data is unavailable";
      default: return "Analysis result";
    }
  }
  switch (decision) {
    case "ASK_CLARIFICATION": return "More information needed";
    case "ABSTAIN": return "There is not enough evidence yet";
    case "ESCALATE_HUMAN": return "A specialist should review this";
    default: return "Analysis result";
  }
}

function decisionTone(decision: string | null | undefined, responseMode: string | null | undefined): string {
  if (decision === "ESCALATE_HUMAN" || responseMode === "conflict") return "attention";
  if (decision === "ABSTAIN" || decision === "ASK_CLARIFICATION" || responseMode === "partial" || responseMode === "inconclusive" || responseMode === "unavailable") return "caution";
  return "ready";
}

function decisionNextStep(
  decision: string | null | undefined,
  responseMode: string | null | undefined,
): string {
  if (decision === "ORIENT") {
    switch (responseMode) {
      case "complete":
        return "Review the conclusion and the supporting evidence before making an operational decision.";
      case "partial":
        return "Use only the supported part of the answer and check the missing information before deciding what to do.";
      case "inconclusive":
        return "Check the missing or insufficient data before starting a follow-up analysis.";
      case "conflict":
        return "Review the conflicting observations with a specialist before taking action.";
      case "unavailable":
        return "Restore or provide the missing data source before relying on this analysis.";
      default:
        return "Review the answer and the supporting evidence before using it operationally.";
    }
  }
  switch (decision) {
    case "ASK_CLARIFICATION":
      return "Add the information requested in the answer and start a new analysis.";
    case "ABSTAIN":
      return "Add the missing equipment, analysis, telemetry, time range or other evidence identified in the answer.";
    case "ESCALATE_HUMAN":
      return "Share this result and its evidence with a qualified specialist. The assistant intentionally did not guess.";
    default:
      return "Review the answer first. Open the evidence only if you need to understand how the conclusion was reached.";
  }
}

function friendlyToolName(tool: string | null): string {
  if (!tool) return "Checked information";
  const known: Record<string, string> = {
    get_current_user: "Your workspace",
    list_assets_by_company: "Equipment list",
    get_asset: "Equipment details",
    list_analyses: "Analysis history",
    list_analyses_by_asset: "Analysis history",
    get_analysis: "Analysis details",
    get_rms: "Vibration level",
    get_spectrum: "Frequency spectrum",
    get_baseline: "Normal behavior baseline",
    get_data_quality: "Data quality",
  };
  if (known[tool]) return known[tool];
  const words = tool.replace(/^get_/, "").replace(/^list_/, "").replaceAll("_", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function evidenceSummary(events: SafeEvent[]) {
  const seen = new Set<string>();
  const evidence: Array<{ id: string; tool: string | null; status: number | null }> = [];
  for (const event of events) {
    if (!event.evidence_id || seen.has(event.evidence_id)) continue;
    seen.add(event.evidence_id);
    evidence.push({ id: event.evidence_id, tool: event.tool_name, status: event.status_code });
  }
  return evidence.slice(0, 4);
}

export function ProductExperience({
  selectedRun,
  events,
  executionStatus,
  connection,
  hasLiveRun,
  viewingHistorical,
  onUsePrompt,
  onOpenEvidence,
  onOpenTechnical,
}: Props) {
  const capabilityQuery = useQuery({
    queryKey: ["release0-capabilities"],
    queryFn: fetchRelease0Capabilities,
    staleTime: 60_000,
  });
  const stage = currentStage(selectedRun, events, executionStatus, hasLiveRun);
  const evidence = evidenceSummary(events);
  const serverIntents = capabilityQuery.data?.guided_intents ?? [];
  const usingStarterExamples = !capabilityQuery.isLoading && serverIntents.length === 0;
  const quickStartOptions = serverIntents.length > 0 ? serverIntents : usingStarterExamples ? STARTER_EXAMPLES : [];
  const hasRunContext = hasLiveRun || Boolean(selectedRun);
  const completed = Boolean(selectedRun?.completed);

  const usePrompt = (prompt: string) => {
    onUsePrompt(prompt);
    window.requestAnimationFrame(() => {
      document.getElementById("agent-request")?.focus();
      document.getElementById("agent-request")?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  };

  return (
    <section className="experience-shell" aria-label="Industrial analysis assistant">
      {!hasRunContext && (
        <article className="experience-hero">
          <div className="experience-copy">
            <p className="eyebrow">INDUSTRIAL ANALYSIS ASSISTANT</p>
            <h2>Ask about your equipment in your own words.</h2>
            <p>
              You do not need to know technical commands or internal IDs. Describe what you want to understand and the assistant will check the available TRACTIAN data, show what supports the answer, and stop safely when the information is not enough.
            </p>
            <ul className="experience-promises" aria-label="What the assistant does">
              <li><strong>Checks live data</strong><span>Uses the information available in TRACTIAN.</span></li>
              <li><strong>Shows its evidence</strong><span>You can see what information supports the answer.</span></li>
              <li><strong>Does not guess</strong><span>If the data is insufficient or conflicting, it tells you.</span></li>
              <li><strong>Does not change equipment</strong><span>This release is read-only unless an explicitly governed action is enabled.</span></li>
            </ul>
          </div>
          <div className="experience-start">
            <p className="eyebrow">NEED AN EXAMPLE?</p>
            <strong>Try one of these questions</strong>
            <p className="muted">Choose one to fill the question box. You can change the wording before starting.</p>
            {usingStarterExamples && (
              <p className="experience-source-note" role="status">
                These are safe starter examples. The live system remains the source of truth for available capabilities.
              </p>
            )}
            <div className="experience-intents">
              {quickStartOptions.map((intent) => (
                <button
                  type="button"
                  data-testid="quick-start-option"
                  key={intent.intent_id}
                  onClick={() => usePrompt(intent.prompt_template)}
                >
                  <strong>{intent.label}</strong>
                  <small>Use this example</small>
                </button>
              ))}
              {capabilityQuery.isLoading && <span className="muted">Loading examples…</span>}
            </div>
          </div>
        </article>
      )}

      {hasRunContext && !completed && (
        <article className="experience-progress" aria-live="polite">
          <div className="experience-progress-heading">
            <div>
              <p className="eyebrow">{viewingHistorical ? "SAVED ANALYSIS" : "ANALYSIS IN PROGRESS"}</p>
              <h2>We are checking the available information</h2>
              <p>You can stay on this page. The result will appear here when the analysis is ready.</p>
            </div>
            <span className="experience-connection">{viewingHistorical ? "saved" : connection.toLowerCase()}</span>
          </div>
          <ol className="experience-stage-list" aria-label="Analysis progress">
            {STAGES.map(([key, label], index) => (
              <li key={key} className={index < stage ? "done" : index === stage ? "active" : "pending"}>
                <span aria-hidden="true">{index < stage || stage === 5 ? "✓" : index + 1}</span>
                <small>{label}</small>
              </li>
            ))}
          </ol>
        </article>
      )}

      {completed && (
        <article className={`experience-outcome outcome-${decisionTone(selectedRun?.terminal_decision, selectedRun?.terminal_response_mode)}`} data-testid="customer-outcome-summary">
          <div className="experience-outcome-main">
            <p className="eyebrow">RESULT</p>
            <div className="experience-outcome-title">
              <h2>{decisionTitle(selectedRun?.terminal_decision, selectedRun?.terminal_response_mode)}</h2>
              <span className="plain-status-label">Analysis finished</span>
            </div>
            <p className="experience-message">{selectedRun?.terminal_message || "No user-facing answer was saved for this analysis."}</p>
            <div className="experience-next-step">
              <strong>What to do next</strong>
              <p>{decisionNextStep(selectedRun?.terminal_decision, selectedRun?.terminal_response_mode)}</p>
            </div>
            <div className="experience-outcome-actions">
              <button type="button" className="primary-secondary-button" onClick={onOpenEvidence}>See why this answer</button>
              <button type="button" className="quiet-link-button" onClick={onOpenTechnical}>Open technical details</button>
            </div>
          </div>
          <aside className="experience-evidence" aria-label="Evidence summary">
            <p className="eyebrow">INFORMATION CHECKED</p>
            <strong>{evidence.length > 0 ? `${evidence.length} supporting source${evidence.length === 1 ? "" : "s"} shown` : "No supporting source saved"}</strong>
            {evidence.length > 0 ? (
              <ul>
                {evidence.map((item, index) => (
                  <li key={item.id}>
                    <span className="evidence-number" aria-hidden="true">{index + 1}</span>
                    <div>
                      <strong>{friendlyToolName(item.tool)}</strong>
                      <small>{item.status && item.status >= 200 && item.status < 300 ? "Checked successfully" : "Saved for review"}</small>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">This result did not save a user-visible evidence reference.</p>
            )}
            <button type="button" className="evidence-link-button" onClick={onOpenEvidence}>View all evidence</button>
          </aside>
        </article>
      )}
    </section>
  );
}
