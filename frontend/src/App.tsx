import { useQuery } from "@tanstack/react-query";
import { FormEvent, useMemo, useState } from "react";

import {
  fetchArchitecture,
  fetchEvaluation,
  fetchExecution,
  fetchHealth,
  fetchRun,
  fetchRunById,
  fetchRunEvents,
  fetchRuns,
} from "./api/client";
import type { RunAccepted, SafeEvent } from "./api/types";
import { ActionControl } from "./components/ActionControl";
import { ArchitectureExplorer } from "./components/ArchitectureExplorer";
import { DepthTabs, type WorkspaceTabId } from "./components/DepthTabs";
import { OperationalValueCollector } from "./components/OperationalValueCollector";
import { OperationsWorkspace } from "./components/OperationsWorkspace";
import { ProductExperience } from "./components/ProductExperience";
import { Release0CapabilitySurface } from "./components/Release0CapabilitySurface";
import { RunExplorer } from "./components/RunExplorer";
import { SemanticReviewCollector } from "./components/SemanticReviewCollector";
import { TraceGraph } from "./components/TraceGraph";
import { useLiveRun } from "./hooks/useLiveRun";
import { deriveRunEventMetrics, eventDisplayLabel } from "./state/runEvents";

function valueOrDash(value: string | number | boolean | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "yes" : "no";
  return String(value);
}

function eventTone(event: SafeEvent): string {
  if (event.failure_code || event.event_type === "error") return "danger";
  if (event.event_type === "policy_check" && event.policy_allowed === false) return "warning";
  if (event.event_type === "final_response" || event.event_type === "run_finished") return "success";
  if (event.event_type === "model_call") return "model";
  if (event.event_type.includes("tool") || event.event_type === "observation") return "tool";
  return "neutral";
}

function friendlyEventLabel(event: SafeEvent): string {
  switch (event.event_type) {
    case "model_call": return "Understanding the next step";
    case "tool_call": return "Checking information";
    case "tool_result": return "Information received";
    case "observation": return "Evidence saved";
    case "policy_check": return event.policy_allowed === false ? "Safety check stopped a step" : "Safety check passed";
    case "final_response": return "Answer prepared";
    case "run_finished": return "Analysis finished";
    case "error": return "A problem was detected";
    default: return eventDisplayLabel(event);
  }
}

function friendlyDecisionLabel(decision: string | null | undefined, responseMode: string | null | undefined): string {
  if (decision === "ASK_CLARIFICATION") return "More information needed";
  if (decision === "ABSTAIN") return "Not enough evidence";
  if (decision === "ESCALATE_HUMAN") return "Specialist review recommended";
  if (decision === "ORIENT") {
    if (responseMode === "complete") return "Answer ready";
    if (responseMode === "partial") return "Partial answer";
    if (responseMode === "conflict") return "Conflicting evidence";
    if (responseMode === "inconclusive") return "No reliable conclusion";
    if (responseMode === "unavailable") return "Required data unavailable";
    return "Analysis result";
  }
  return decision ? "Analysis result" : "No result yet";
}

function EventMeta({ event }: { event: SafeEvent }) {
  const items = [
    event.tool_name && ["tool", event.tool_name],
    event.provider_id && ["provider", event.provider_id],
    event.model_id && ["model", event.model_id],
    event.policy_stage && ["policy", event.policy_stage],
    event.policy_violation && ["violation", event.policy_violation],
    event.evidence_id && ["evidence", event.evidence_id],
    event.response_mode && ["semantics", event.response_mode],
    event.status_code !== null && ["status", String(event.status_code)],
    event.latency_ms !== null && ["latency", `${event.latency_ms} ms`],
    event.reason_code && ["reason", event.reason_code],
  ].filter(Boolean) as [string, string][];
  if (items.length === 0) return null;
  return <div className="event-meta">{items.map(([label, value]) => <span key={`${label}:${value}`}><b>{label}</b> {value}</span>)}</div>;
}

function LayerIntro({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <div className="layer-intro friendly-layer-intro">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function App() {
  const [requestText, setRequestText] = useState("");
  const [historicalRunId, setHistoricalRunId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<WorkspaceTabId>("results");
  const live = useLiveRun();

  const healthQuery = useQuery({ queryKey: ["health"], queryFn: fetchHealth, refetchInterval: 5_000 });
  const architectureQuery = useQuery({ queryKey: ["architecture"], queryFn: fetchArchitecture, staleTime: 60_000 });
  const runsQuery = useQuery({ queryKey: ["runs"], queryFn: () => fetchRuns(100), refetchInterval: live.accepted && live.connection !== "completed" ? 2_000 : 5_000 });
  const liveRunQuery = useQuery({ queryKey: ["run", live.accepted?.run_id], queryFn: () => fetchRun(live.accepted!.run_path), enabled: Boolean(live.accepted), refetchInterval: (query) => (query.state.data?.completed ? false : 1_000) });
  const executionQuery = useQuery({
    queryKey: ["execution", live.accepted?.run_id],
    queryFn: () => fetchExecution(live.accepted!.execution_path),
    enabled: Boolean(live.accepted),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 500;
    },
  });
  const liveEvaluationReady = executionQuery.data?.status === "completed";
  const liveEvaluationQuery = useQuery({ queryKey: ["evaluation", live.accepted?.run_id], queryFn: () => fetchEvaluation(live.accepted!.run_id), enabled: Boolean(live.accepted && liveEvaluationReady) });
  const historicalRunQuery = useQuery({ queryKey: ["historical-run", historicalRunId], queryFn: () => fetchRunById(historicalRunId!), enabled: Boolean(historicalRunId) });
  const historicalEventsQuery = useQuery({ queryKey: ["historical-events", historicalRunId], queryFn: () => fetchRunEvents(historicalRunId!), enabled: Boolean(historicalRunId) });
  const historicalEvaluationQuery = useQuery({ queryKey: ["historical-evaluation", historicalRunId], queryFn: () => fetchEvaluation(historicalRunId!), enabled: Boolean(historicalRunId) });

  const selectedRun = historicalRunId ? historicalRunQuery.data : liveRunQuery.data;
  const selectedEvents = historicalRunId ? historicalEventsQuery.data?.items ?? [] : live.events;
  const selectedEvaluation = historicalRunId ? historicalEvaluationQuery.data : liveEvaluationQuery.data;
  const selectedEvaluationReady = historicalRunId ? Boolean(historicalRunQuery.data?.completed) : liveEvaluationReady;
  const selectedRunId = historicalRunId ?? live.accepted?.run_id ?? null;
  const metrics = useMemo(() => deriveRunEventMetrics(selectedEvents), [selectedEvents]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalized = requestText.trim();
    if (!normalized || live.submitting) return;
    setHistoricalRunId(null);
    setActiveTab("results");
    try { await live.submit(normalized); } catch { /* Hook exposes sanitized submission error state. */ }
  };

  const followActionRun = (run: RunAccepted) => {
    setHistoricalRunId(null);
    setActiveTab("results");
    live.follow(run);
  };

  const selectHistoricalRun = (runId: string | null) => {
    setHistoricalRunId(runId);
    if (runId) setActiveTab("results");
  };

  const blockingChecks = selectedEvaluation?.items.filter((check) => check.blocking) ?? [];
  const passedChecks = blockingChecks.filter((check) => check.passed).length;
  const viewingHistorical = historicalRunId !== null;
  const serviceOnline = healthQuery.data?.status === "ok";
  const hasAnyRun = Boolean(selectedRun || live.accepted);

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <header className="topbar friendly-topbar">
        <div className="product-brand">
          <p className="eyebrow">ACADEMY × TRACTIAN</p>
          <h1>Equipment analysis assistant</h1>
          <p>Understand what the data is telling you and what to check next.</p>
        </div>
        <div className={`service-state friendly-service-state ${serviceOnline ? "is-online" : "is-offline"}`} aria-live="polite">
          <span className={`status-dot ${serviceOnline ? "online" : "offline"}`} aria-hidden="true" />
          <div>
            <b>{serviceOnline ? "System online" : "System temporarily unavailable"}</b>
            <small>{serviceOnline ? "Ready for a new analysis" : "Please try again shortly"}</small>
          </div>
        </div>
      </header>

      <main id="main-content">
        <DepthTabs
          activeTab={activeTab}
          onChange={setActiveTab}
          evidenceCount={metrics.evidenceRefs}
          eventCount={metrics.events}
          hasEvaluation={Boolean(selectedEvaluation?.count)}
        />

        <section className="workspace-layer" id="workspace-panel-results" role="tabpanel" aria-labelledby="workspace-tab-results" tabIndex={0} hidden={activeTab !== "results"}>
          <LayerIntro
            eyebrow={hasAnyRun ? "CURRENT ANALYSIS" : "GET STARTED"}
            title={hasAnyRun ? "Your answer, first" : "What would you like to understand?"}
            description={hasAnyRun
              ? "Start with the result and the recommended next step. Open the other sections only if you want more detail."
              : "Describe the equipment issue in your own words. You do not need technical commands or internal identifiers."}
          />

          <ProductExperience
            selectedRun={selectedRun}
            events={selectedEvents}
            executionStatus={viewingHistorical ? undefined : executionQuery.data?.status}
            connection={live.connection}
            hasLiveRun={Boolean(live.accepted)}
            viewingHistorical={viewingHistorical}
            onUsePrompt={setRequestText}
            onOpenEvidence={() => setActiveTab("evidence")}
            onOpenTechnical={() => setActiveTab("engineering")}
          />

          <section className="control-panel primary-request-panel">
            <div className="section-heading request-heading">
              <div>
                <p className="eyebrow">{hasAnyRun ? "ASK ANOTHER QUESTION" : "YOUR QUESTION"}</p>
                <h2>{hasAnyRun ? "Start a new analysis" : "Tell us what you want to know"}</h2>
                <p className="section-supporting-copy">Write naturally, as if you were asking a colleague. The assistant will find identifiers it can safely discover.</p>
              </div>
              {live.accepted && <button className="ghost-button" type="button" onClick={live.clear}>Clear current analysis</button>}
            </div>
            <form className="request-form" onSubmit={submit}>
              <label htmlFor="agent-request">What would you like to understand?</label>
              <textarea
                id="agent-request"
                value={requestText}
                onChange={(event) => setRequestText(event.target.value)}
                placeholder="For example: Which equipment needs attention today, and why?"
                maxLength={20_000}
                rows={5}
              />
              <div className="request-actions">
                <span className="request-help">No special format is required.</span>
                <button type="submit" disabled={!requestText.trim() || live.submitting || !serviceOnline}>
                  {live.submitting ? "Starting analysis…" : "Start analysis"}
                </button>
              </div>
            </form>
            {live.error && (
              <div className="error-banner friendly-error" role="alert">
                <strong>We could not start the analysis.</strong>
                <span>Please try again. If the problem continues, open the technical detail below.</span>
                <details><summary>Technical detail</summary><code>{live.error}</code></details>
              </div>
            )}
          </section>
        </section>

        <section className="workspace-layer" id="workspace-panel-evidence" role="tabpanel" aria-labelledby="workspace-tab-evidence" tabIndex={0} hidden={activeTab !== "evidence"}>
          <LayerIntro
            eyebrow="WHY THIS ANSWER"
            title="See what the assistant checked"
            description="Review the information that supports the answer. Technical IDs and system metadata stay folded away unless you choose to open them."
          />

          <section className="workspace-grid friendly-evidence-grid">
            <article className="panel timeline-panel friendly-timeline-panel">
              <div className="section-heading compact">
                <div>
                  <p className="eyebrow">CHECKED INFORMATION</p>
                  <h2>What happened during the analysis</h2>
                  <p className="section-supporting-copy">The most important steps are shown in plain language.</p>
                </div>
                <span className="count-pill">{selectedEvents.length} step{selectedEvents.length === 1 ? "" : "s"}</span>
              </div>
              {selectedEvents.length === 0 ? (
                <div className="empty-state">
                  <strong>No analysis selected</strong>
                  <p>Start an analysis or choose one from History to see what information was checked.</p>
                </div>
              ) : (
                <ol className="timeline-list">
                  {selectedEvents.map((event) => (
                    <li key={event.event_id} className={`timeline-item tone-${eventTone(event)}`}>
                      <div className="sequence" aria-hidden="true">{String(event.sequence).padStart(2, "0")}</div>
                      <div className="timeline-content">
                        <div className="event-title-row">
                          <strong>{friendlyEventLabel(event)}</strong>
                          <small>{event.latency_ms !== null ? `${event.latency_ms} ms` : event.timestamp ?? ""}</small>
                        </div>
                        {event.message && <p className="event-message">{event.message}</p>}
                        <details className="event-technical-details">
                          <summary>Technical details</summary>
                          <EventMeta event={event} />
                        </details>
                      </div>
                    </li>
                  ))}
                </ol>
              )}
            </article>

            <aside className="side-stack">
              <article className="panel terminal-panel friendly-answer-panel">
                <p className="eyebrow">FINAL ANSWER</p>
                <h2>{friendlyDecisionLabel(selectedRun?.terminal_decision, selectedRun?.terminal_response_mode)}</h2>
                {!selectedRun?.completed ? (
                  <div className="empty-state small">
                    <strong>The analysis is not finished yet</strong>
                    <p>The final answer will appear here only after the analysis is complete.</p>
                  </div>
                ) : (
                  <>
                    <p className="friendly-terminal-message">{valueOrDash(selectedRun.terminal_message)}</p>
                    <details className="technical-disclosure compact-disclosure">
                      <summary>Show internal result codes</summary>
                      <dl className="detail-list">
                        <div><dt>Decision</dt><dd>{valueOrDash(selectedRun.terminal_decision)}</dd></div>
                        <div><dt>Response mode</dt><dd>{valueOrDash(selectedRun.terminal_response_mode)}</dd></div>
                        <div><dt>Reason</dt><dd>{valueOrDash(selectedRun.terminal_reason_code)}</dd></div>
                      </dl>
                    </details>
                  </>
                )}
              </article>

              <article className="panel friendly-source-count">
                <p className="eyebrow">EVIDENCE</p>
                <h2>Sources saved for this answer</h2>
                <div className="evaluation-score"><strong>{metrics.evidenceRefs}</strong><span>source reference{metrics.evidenceRefs === 1 ? "" : "s"}</span></div>
                <p className="muted">Sensitive credentials and private system data are never shown here.</p>
              </article>
            </aside>
          </section>
        </section>

        <section className="workspace-layer" id="workspace-panel-investigation" role="tabpanel" aria-labelledby="workspace-tab-investigation" tabIndex={0} hidden={activeTab !== "investigation"}>
          <LayerIntro
            eyebrow="HISTORY"
            title="Review previous analyses"
            description="Choose an earlier analysis to see its answer and evidence. Detailed runtime activity is available below for people who need it."
          />

          <RunExplorer runs={runsQuery.data?.items ?? []} selectedRunId={historicalRunId} liveRunId={live.accepted?.run_id ?? null} loading={runsQuery.isLoading} onSelect={selectHistoricalRun} />

          <details className="technical-disclosure history-technical-disclosure">
            <summary>
              <span><strong>Show how this analysis ran</strong><small>Runtime status, activity counts and process graph</small></span>
            </summary>
            <div className="technical-disclosure-body">
              <section className="run-strip" aria-live="polite">
                <div><span className="metric-label">View</span><strong>{viewingHistorical ? "SAVED" : live.accepted ? "CURRENT" : "NONE"}</strong></div>
                <div><span className="metric-label">Connection / execution</span><strong>{viewingHistorical ? "SAVED" : `${live.connection.toUpperCase()} / ${executionQuery.data?.status ?? (live.accepted ? "accepted" : "—")}`}</strong></div>
                <div className="run-id-cell"><span className="metric-label">Run ID</span><strong title={selectedRunId ?? undefined}>{selectedRunId ?? "No selected run"}</strong></div>
                <div><span className="metric-label">Config</span><strong title={selectedRun?.config_hash}>{selectedRun?.config_hash?.slice(0, 12) ?? "—"}</strong></div>
              </section>

              <section className="metric-grid">
                {[["Events", metrics.events], ["Model calls", metrics.modelCalls], ["Tool calls", metrics.toolCalls], ["Policy blocks", metrics.policyBlocks], ["Evidence refs", metrics.evidenceRefs], ["Errors", metrics.errors]].map(([label, value]) => <article className="metric-card" key={label}><span>{label}</span><strong>{value}</strong></article>)}
              </section>

              <article className="panel visual-panel">
                <div className="section-heading compact">
                  <div><p className="eyebrow">PROCESS MAP</p><h2>Trace graph</h2></div>
                  <span className="count-pill">{selectedEvents.length} safe events</span>
                </div>
                <TraceGraph events={selectedEvents} />
              </article>
            </div>
          </details>
        </section>

        <section className="workspace-layer" id="workspace-panel-engineering" role="tabpanel" aria-labelledby="workspace-tab-engineering" tabIndex={0} hidden={activeTab !== "engineering"}>
          <LayerIntro
            eyebrow="TECHNICAL DETAILS"
            title="Engineering and evaluation"
            description="This area is intentionally detailed. It exposes the safe runtime, architecture, evaluation and research surfaces without exposing secrets or hidden reasoning."
          />

          <div className="technical-zone">
            <div className="layer-stack">
              <OperationsWorkspace selectedRunId={selectedRunId} />

              <article className="panel evaluation-panel">
                <div className="evaluator-boundary"><p className="eyebrow">POST-RUNTIME ONLY</p><span>Evaluator isolated from agent-time state</span></div>
                <h2>Evaluation</h2>
                {!selectedRun?.completed ? (
                  <div className="empty-state small"><strong>Not evaluated yet</strong><p>Evaluation appears after the runtime has emitted its terminal trace.</p></div>
                ) : !selectedEvaluationReady ? (
                  <p className="muted">Runtime finished. Waiting for post-runtime evaluation persistence…</p>
                ) : selectedEvaluation?.count ? (
                  <>
                    <div className="evaluation-score"><strong>{passedChecks}/{blockingChecks.length}</strong><span>blocking checks passed</span></div>
                    <ul className="check-list">{selectedEvaluation.items.map((check) => <li key={check.check_name}><span className={check.passed ? "check-pass" : "check-fail"}>{check.passed ? "PASS" : "FAIL"}</span><span>{check.check_name}</span></li>)}</ul>
                  </>
                ) : <p className="muted">No safe evaluation rows are available.</p>}
              </article>

              <article className="panel visual-panel">
                <div className="section-heading compact">
                  <div><p className="eyebrow">IMPLEMENTATION-BACKED SYSTEM MAP</p><h2>Architecture Explorer</h2></div>
                  {architectureQuery.data && <span className="count-pill">provider: {architectureQuery.data.provider_selection_state}</span>}
                </div>
                {architectureQuery.data ? (
                  <ArchitectureExplorer manifest={architectureQuery.data} events={selectedEvents} hasRun={Boolean(selectedRunId)} hasEvaluation={Boolean(selectedEvaluation?.count)} />
                ) : (
                  <div className="empty-state graph-empty"><strong>Architecture manifest unavailable</strong><p>The UI will not substitute hard-coded architecture when the backend manifest is missing.</p></div>
                )}
              </article>

              <ActionControl selectedRunId={selectedRunId} onFollowExecution={followActionRun} />
              <Release0CapabilitySurface events={selectedEvents} onUsePrompt={setRequestText} />
              <OperationalValueCollector />
              <SemanticReviewCollector />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
