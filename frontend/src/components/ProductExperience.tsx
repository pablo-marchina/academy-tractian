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
}

const STAGES = [
  ["PREPARING", "Preparing"],
  ["DECIDING", "AI deciding"],
  ["READING", "Reading TRACTIAN"],
  ["REVIEWING", "Reviewing evidence"],
  ["EVALUATING", "Evaluating"],
  ["COMPLETE", "Complete"],
] as const;

const STARTER_EXAMPLES = [
  {
    intent_id: "STARTER_CONTEXT",
    label: "Understand the context",
    release0_behavior: "EDIT_BEFORE_RUNNING",
    prompt_template:
      "Help me understand this industrial situation using only evidence you can actually inspect. State what is known, what is uncertain, and what additional identifier or evidence would help if the context is incomplete.",
  },
  {
    intent_id: "STARTER_INVESTIGATE",
    label: "Investigate evidence",
    release0_behavior: "EDIT_BEFORE_RUNNING",
    prompt_template:
      "Investigate this industrial issue using the relevant read-only evidence available to you. Follow the evidence, do not guess unsupported facts, and return a concise customer-safe conclusion or stop safely if the evidence is insufficient.",
  },
  {
    intent_id: "STARTER_REVIEW",
    label: "Review a possible action",
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

function decisionTitle(decision: string | null | undefined): string {
  switch (decision) {
    case "ORIENT": return "Conclusion ready";
    case "ASK_CLARIFICATION": return "More context needed";
    case "ABSTAIN": return "Not enough evidence";
    case "ESCALATE_HUMAN": return "Human review recommended";
    default: return decision ? decision.replaceAll("_", " ").toLowerCase() : "Investigation result";
  }
}

function decisionNextStep(decision: string | null | undefined): string {
  switch (decision) {
    case "ORIENT":
      return "Review the conclusion and supporting evidence. Release 0 will not execute a consequential change for you.";
    case "ASK_CLARIFICATION":
      return "Provide the missing context requested in the message and start a new investigation with that information.";
    case "ABSTAIN":
      return "The agent stopped instead of guessing. Add the missing asset, analysis, telemetry, timestamp or other evidence identified in the message.";
    case "ESCALATE_HUMAN":
      return "Hand the conclusion, reason and evidence context to a qualified human reviewer. The system intentionally did not resolve the uncertainty itself.";
    default:
      return "Use the customer-safe message as the primary output and open deeper tabs only when you need supporting detail.";
  }
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
    <section className="experience-shell" aria-label="Release 0 user experience">
      {!hasRunContext && (
        <article className="experience-hero">
          <div className="experience-copy">
            <p className="eyebrow">RELEASE 0 · READ-ONLY PILOT</p>
            <h2>Investigate industrial evidence without guessing.</h2>
            <p>
              Describe what you need to understand. The agent can inspect the supplied TRACTIAN read
              APIs, ground its answer in evidence, and stop safely when the information is incomplete
              or conflicting. External consequential actions stay disabled in this release.
            </p>
            <div className="experience-guardrails" aria-label="Release 0 guarantees">
              <span>Live provider</span><span>Real TRACTIAN reads</span><span>Evidence-backed</span><span>No external actions</span>
            </div>
          </div>
          <div className="experience-start">
            <p className="eyebrow">QUICK START</p>
            <strong>Choose a starting posture</strong>
            <p className="muted">The preset fills the request. You can edit it before running.</p>
            {usingStarterExamples && (
              <p className="experience-source-note" role="status">
                Server-owned guided intents are unavailable in this environment, so these are starter examples only. Runtime capabilities remain authoritative.
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
                  <span>{intent.intent_id}</span>
                  <strong>{intent.label}</strong>
                  <small>{intent.release0_behavior.replaceAll("_", " ").toLowerCase()}</small>
                </button>
              ))}
              {capabilityQuery.isLoading && <span className="muted">Loading guided investigations…</span>}
            </div>
          </div>
        </article>
      )}

      {hasRunContext && !completed && (
        <article className="experience-progress" aria-live="polite">
          <div className="experience-progress-heading">
            <div>
              <p className="eyebrow">{viewingHistorical ? "PERSISTED INVESTIGATION" : "LIVE INVESTIGATION"}</p>
              <h2>Investigation in progress</h2>
            </div>
            <span className="experience-connection">{viewingHistorical ? "history" : connection.toLowerCase()}</span>
          </div>
          <ol className="experience-stage-list">
            {STAGES.map(([key, label], index) => (
              <li key={key} className={index < stage ? "done" : index === stage ? "active" : "pending"}>
                <span>{index < stage || stage === 5 ? "✓" : index + 1}</span>
                <small>{label}</small>
              </li>
            ))}
          </ol>
        </article>
      )}

      {completed && (
        <article className="experience-outcome" data-testid="customer-outcome-summary">
          <div className="experience-outcome-main">
            <p className="eyebrow">WHAT YOU NEED TO KNOW</p>
            <div className="experience-outcome-title">
              <h2>{decisionTitle(selectedRun?.terminal_decision)}</h2>
              {selectedRun?.terminal_response_mode && <span>{selectedRun.terminal_response_mode}</span>}
            </div>
            <p className="experience-message">{selectedRun?.terminal_message || "No customer-safe message was persisted."}</p>
            <div className="experience-next-step">
              <strong>What to do next</strong>
              <p>{decisionNextStep(selectedRun?.terminal_decision)}</p>
            </div>
          </div>
          <aside className="experience-evidence">
            <p className="eyebrow">SUPPORTING EVIDENCE</p>
            {evidence.length > 0 ? (
              <ul>
                {evidence.map((item) => (
                  <li key={item.id}>
                    <strong>{item.tool?.replaceAll("_", " ") ?? "Evidence"}</strong>
                    <span>{item.status ? `HTTP ${item.status}` : "persisted"}</span>
                    <small title={item.id}>{item.id}</small>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">No safe evidence reference was persisted for this terminal path.</p>
            )}
            <small className="experience-evidence-note">
              Open Evidence for the canonical trail, Investigation for runtime behavior, or Engineering for evaluator and architecture details.
            </small>
          </aside>
        </article>
      )}
    </section>
  );
}
