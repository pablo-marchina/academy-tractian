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

function LayerIntro({ eyebrow, title, description, depth }: { eyebrow: string; title: string; description: string; depth: string }) {
  return (
    <div className="layer-intro">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      <span className="layer-depth-badge">{depth}</span>
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

  const selectHistoricalRun = (runId: string) => {
    setHistoricalRunId(runId);
    setActiveTab("results");
  };

  const blockingChecks = selectedEvaluation?.items.filter((check) => check.blocking) ?? [];
  const passedChecks = blockingChecks.filter((check) => check.passed).length;
  const viewingHistorical = historicalRunId !== null;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div><p className="eyebrow">ACADEMY × TRACTIAN</p><h1>Industrial Agent Operations</h1></div>
        <div className="service-state" aria-live="polite">
          <span className={`status-dot ${healthQuery.data?.status === "ok" ? "online" : "offline"}`} />
          <div><b>{healthQuery.data?.status === "ok" ? "API healthy" : "API unavailable"}</b><small>{healthQuery.data?.version ?? "checking service"}</small></div>
        </div>
      </header>

      <main>
        <DepthTabs
          activeTab={activeTab}
          onChange={setActiveTab}
          evidenceCount={metrics.evidenceRefs}
          eventCount={metrics.events}
          hasEvaluation={Boolean(selectedEvaluation?.count)}
        />

        <section
          className="workspace-layer"
          id="workspace-panel-results"
          role="tabpanel"
          aria-labelledby="workspace-tab-results"
          tabIndex={0}
          hidden={activeTab !== "results"}
        >
          <LayerIntro
            eyebrow="LAYER 1 · USER OUTCOME"
            title="Answer first"
            description="Start here for the customer-safe result, current progress and the next action you should take. No runtime expertise is required."
            depth="lowest complexity"
          />

          <ProductExperience
            selectedRun={selectedRun}
            events={selectedEvents}
            executionStatus={executionQuery.data?.status}
            connection={live.connection}
            hasLiveRun={Boolean(live.accepted)}
            viewingHistorical={viewingHistorical}
            onUsePrompt={setRequestText}
          />

          <section className="control-panel">
            <div className="section-heading"><div><p className="eyebrow">START AN INVESTIGATION</p><h2>What do you need to understand?</h2></div>{live.accepted && <button className="ghost-button" type="button" onClick={live.clear}>Clear live run</button>}</div>
            <form className="request-form" onSubmit={submit}>
              <label htmlFor="agent-request">Industrial request</label>
              <textarea id="agent-request" value={requestText} onChange={(event) => setRequestText(event.target.value)} placeholder="Describe the alert, asset, analysis or evidence you want the agent to investigate. Include identifiers when you have them." maxLength={20_000} rows={4} />
              <div className="request-actions"><span>{requestText.length.toLocaleString()} / 20,000</span><button type="submit" disabled={!requestText.trim() || live.submitting}>{live.submitting ? "Submitting…" : "Start production run"}</button></div>
            </form>
            {live.error && <div className="error-banner">{live.error}</div>}
          </section>
        </section>

        <section
          className="workspace-layer"
          id="workspace-panel-evidence"
          role="tabpanel"
          aria-labelledby="workspace-tab-evidence"
          tabIndex={0}
          hidden={activeTab !== "evidence"}
        >
          <LayerIntro
            eyebrow="LAYER 2 · EXPLAINABILITY"
            title="See why the answer is supported"
            description="Inspect the persisted customer-safe output and the canonical evidence trail without opening architecture, evaluator or experiment internals."
            depth="evidence detail"
          />

          <section className="workspace-grid">
            <article className="panel timeline-panel">
              <div className="section-heading compact"><div><p className="eyebrow">EVIDENCE TRAIL</p><h2>Canonical event timeline</h2></div><span className="count-pill">{selectedEvents.length} events</span></div>
              {selectedEvents.length === 0 ? <div className="empty-state"><strong>No runtime events selected</strong><p>Submit a live request or open a persisted run from Investigation. This panel never fabricates trace history.</p></div> : <ol className="timeline-list">{selectedEvents.map((event) => <li key={event.event_id} className={`timeline-item tone-${eventTone(event)}`}><div className="sequence">{String(event.sequence).padStart(2, "0")}</div><div className="timeline-content"><div className="event-title-row"><div><span className="origin-badge">{event.origin}</span><strong>{eventDisplayLabel(event)}</strong></div><small>{event.latency_ms !== null ? `${event.latency_ms} ms` : event.timestamp ?? ""}</small></div><EventMeta event={event} />{event.message && <p className="event-message">{event.message}</p>}</div></li>)}</ol>}
            </article>

            <aside className="side-stack">
              <article className="panel terminal-panel"><p className="eyebrow">PERSISTED OUTPUT</p><h2>Terminal outcome</h2>{!selectedRun?.completed ? <div className="empty-state small"><strong>Runtime not complete</strong><p>No terminal result is shown until the persisted run is actually complete.</p></div> : <dl className="detail-list"><div><dt>Decision</dt><dd>{valueOrDash(selectedRun.terminal_decision)}</dd></div><div><dt>Response mode</dt><dd>{valueOrDash(selectedRun.terminal_response_mode)}</dd></div><div><dt>Reason</dt><dd>{valueOrDash(selectedRun.terminal_reason_code)}</dd></div><div className="message-detail"><dt>Message</dt><dd>{valueOrDash(selectedRun.terminal_message)}</dd></div></dl>}</article>
              <article className="panel"><p className="eyebrow">EVIDENCE COVERAGE</p><h2>Safe references</h2><div className="evaluation-score"><strong>{metrics.evidenceRefs}</strong><span>persisted evidence references in this run</span></div><p className="muted">Tool names, safe status metadata and evidence IDs remain visible in the timeline. Raw secret-bearing API payloads are never exposed.</p></article>
            </aside>
          </section>
        </section>

        <section
          className="workspace-layer"
          id="workspace-panel-investigation"
          role="tabpanel"
          aria-labelledby="workspace-tab-investigation"
          tabIndex={0}
          hidden={activeTab !== "investigation"}
        >
          <LayerIntro
            eyebrow="LAYER 3 · OPERATIONAL INVESTIGATION"
            title="Inspect how the investigation ran"
            description="Work with persisted history, runtime metrics, execution topology, all product operations and governed action proposals."
            depth="runtime detail"
          />

          <RunExplorer runs={runsQuery.data?.items ?? []} selectedRunId={historicalRunId} liveRunId={live.accepted?.run_id ?? null} loading={runsQuery.isLoading} onSelect={selectHistoricalRun} />

          <section className="run-strip" aria-live="polite">
            <div><span className="metric-label">View</span><strong>{viewingHistorical ? "HISTORICAL" : live.accepted ? "LIVE" : "IDLE"}</strong></div>
            <div><span className="metric-label">Stream / execution</span><strong>{viewingHistorical ? "HISTORICAL" : `${live.connection.toUpperCase()} / ${executionQuery.data?.status ?? (live.accepted ? "accepted" : "—")}`}</strong></div>
            <div className="run-id-cell"><span className="metric-label">Selected safe run ID</span><strong title={selectedRunId ?? undefined}>{selectedRunId ?? "No selected run"}</strong></div>
            <div><span className="metric-label">Config</span><strong title={selectedRun?.config_hash}>{selectedRun?.config_hash?.slice(0, 12) ?? "—"}</strong></div>
          </section>

          <section className="metric-grid">
            {[["Events", metrics.events], ["Model calls", metrics.modelCalls], ["Tool calls", metrics.toolCalls], ["Policy blocks", metrics.policyBlocks], ["Evidence refs", metrics.evidenceRefs], ["Errors", metrics.errors]].map(([label, value]) => <article className="metric-card" key={label}><span>{label}</span><strong>{value}</strong></article>)}
          </section>

          <div className="layer-stack">
            <article className="panel visual-panel"><div className="section-heading compact"><div><p className="eyebrow">EXECUTION TOPOLOGY</p><h2>Trace Graph</h2></div><span className="count-pill">derived from {selectedEvents.length} safe events</span></div><TraceGraph events={selectedEvents} /></article>
            <ActionControl selectedRunId={selectedRunId} onFollowExecution={followActionRun} />
            <OperationsWorkspace selectedRunId={selectedRunId} />
          </div>
        </section>

        <section
          className="workspace-layer"
          id="workspace-panel-engineering"
          role="tabpanel"
          aria-labelledby="workspace-tab-engineering"
          tabIndex={0}
          hidden={activeTab !== "engineering"}
        >
          <LayerIntro
            eyebrow="LAYER 4 · ENGINEERING & EVALUATION"
            title="Open the full observability surface"
            description="Deep inspection of evaluator isolation, implementation-backed architecture, capability contracts and controlled research collectors. Hidden reasoning and secrets remain excluded."
            depth="maximum detail"
          />

          <div className="layer-stack">
            <article className="panel evaluation-panel"><div className="evaluator-boundary"><p className="eyebrow">POST-RUNTIME ONLY</p><span>Evaluator isolated from agent-time state</span></div><h2>Evaluation</h2>{!selectedRun?.completed ? <div className="empty-state small"><strong>Not evaluated yet</strong><p>Evaluation appears only after the runtime has emitted its terminal trace.</p></div> : !selectedEvaluationReady ? <p className="muted">Runtime finished. Waiting for post-runtime evaluation persistence…</p> : selectedEvaluation?.count ? <><div className="evaluation-score"><strong>{passedChecks}/{blockingChecks.length}</strong><span>blocking checks passed</span></div><ul className="check-list">{selectedEvaluation.items.map((check) => <li key={check.check_name}><span className={check.passed ? "check-pass" : "check-fail"}>{check.passed ? "PASS" : "FAIL"}</span><span>{check.check_name}</span></li>)}</ul></> : <p className="muted">No safe evaluation rows are available.</p>}</article>

            <article className="panel visual-panel">
              <div className="section-heading compact"><div><p className="eyebrow">IMPLEMENTATION-BACKED SYSTEM MAP</p><h2>Architecture Explorer</h2></div>{architectureQuery.data && <span className="count-pill">provider: {architectureQuery.data.provider_selection_state}</span>}</div>
              {architectureQuery.data ? <ArchitectureExplorer manifest={architectureQuery.data} events={selectedEvents} hasRun={Boolean(selectedRunId)} hasEvaluation={Boolean(selectedEvaluation?.count)} /> : <div className="empty-state graph-empty"><strong>Architecture manifest unavailable</strong><p>The UI will not substitute hard-coded architecture when the backend manifest is missing.</p></div>}
            </article>

            <Release0CapabilitySurface events={selectedEvents} onUsePrompt={setRequestText} />
            <OperationalValueCollector />
            <SemanticReviewCollector />
          </div>
        </section>
      </main>
    </div>
  );
}
