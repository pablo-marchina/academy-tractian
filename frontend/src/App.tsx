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
import { OperationalValueCollector } from "./components/OperationalValueCollector";
import { OperationsWorkspace, type OperationsWorkspaceFocus } from "./components/OperationsWorkspace";
import { PrimaryNavigation, type PrimaryDestination } from "./components/PrimaryNavigation";
import { ProductExperience } from "./components/ProductExperience";
import { Release0CapabilitySurface } from "./components/Release0CapabilitySurface";
import { RunExplorer } from "./components/RunExplorer";
import { RunVerificationPanel } from "./components/RunVerificationPanel";
import { SemanticReviewCollector } from "./components/SemanticReviewCollector";
import { TraceGraph } from "./components/TraceGraph";
import { useLiveRun } from "./hooks/useLiveRun";

type AppView = "home" | "result" | "evidence" | "history" | "technical";
type TechnicalSection = OperationsWorkspaceFocus | "actions" | "studies";

const QUESTION_EXAMPLES = [
  "Which equipment needs attention today, and why?",
  "Why is this equipment vibrating more than usual?",
  "Is there enough evidence to support the maintenance action I am considering?",
] as const;

const TECHNICAL_SECTIONS: Array<{ id: TechnicalSection; label: string; description: string }> = [
  { id: "analysis", label: "Current analysis", description: "Trace, evidence, tools and policy" },
  { id: "quality", label: "Verification", description: "Claim-bounded assurance and provider evidence" },
  { id: "data", label: "Data", description: "Explore persisted analytics" },
  { id: "system", label: "System", description: "Health, architecture and capabilities" },
  { id: "actions", label: "Actions", description: "Governed external actions" },
  { id: "studies", label: "Studies", description: "Human review and operational value" },
];

function friendlyToolName(tool: string | null): string {
  if (!tool) return "Checked information";
  const known: Record<string, string> = {
    get_current_user: "Workspace context",
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

function evidenceItems(events: SafeEvent[]) {
  const seen = new Set<string>();
  return events.flatMap((event) => {
    if (!event.evidence_id || seen.has(event.evidence_id)) return [];
    seen.add(event.evidence_id);
    return [{
      id: event.evidence_id,
      label: friendlyToolName(event.tool_name),
      message: event.message,
      tool: event.tool_name,
      status: event.status_code,
    }];
  });
}

function technicalHeading(section: TechnicalSection): { title: string; description: string } {
  switch (section) {
    case "analysis": return { title: "How did this analysis run?", description: "Inspect the safe trace, persisted evidence, lineage, tool activity and deterministic policy checks for the selected analysis." };
    case "quality": return { title: "What has actually been verified?", description: "Separate runtime integrity from functional success, evidence sufficiency, trajectory quality, availability, safety and human-calibrated evidence." };
    case "data": return { title: "What do the persisted data show?", description: "Build quantitative views over runs, events and evaluations using the safe analytics contract." };
    case "system": return { title: "Is the production system healthy?", description: "Inspect measured runtime health, the implementation-backed architecture and the capabilities currently exposed by the release." };
    case "actions": return { title: "What external action is being proposed?", description: "Review exact server-held action state, consequence and confirmation boundaries before any governed execution." };
    case "studies": return { title: "What do human reviewers observe?", description: "Collect blinded semantic review and operational-value evidence without leaking private evaluator truth." };
  }
}

export default function App() {
  const [requestText, setRequestText] = useState("");
  const [historicalRunId, setHistoricalRunId] = useState<string | null>(null);
  const [view, setView] = useState<AppView>("home");
  const [technicalSection, setTechnicalSection] = useState<TechnicalSection>("analysis");
  const live = useLiveRun();

  const healthQuery = useQuery({ queryKey: ["health"], queryFn: fetchHealth, refetchInterval: 5_000 });
  const architectureQuery = useQuery({
    queryKey: ["architecture"],
    queryFn: fetchArchitecture,
    staleTime: 60_000,
    enabled: view === "technical" && technicalSection === "system",
  });
  const runsQuery = useQuery({
    queryKey: ["runs"],
    queryFn: () => fetchRuns(100),
    refetchInterval: live.accepted && live.connection !== "completed" ? 2_000 : 5_000,
    enabled: view === "history" || Boolean(live.accepted),
  });
  const liveRunQuery = useQuery({
    queryKey: ["run", live.accepted?.run_id],
    queryFn: () => fetchRun(live.accepted!.run_path),
    enabled: Boolean(live.accepted),
    refetchInterval: (query) => (query.state.data?.completed ? false : 1_000),
  });
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
  const liveEvaluationQuery = useQuery({
    queryKey: ["evaluation", live.accepted?.run_id],
    queryFn: () => fetchEvaluation(live.accepted!.run_id),
    enabled: Boolean(live.accepted && liveEvaluationReady),
  });
  const historicalRunQuery = useQuery({
    queryKey: ["historical-run", historicalRunId],
    queryFn: () => fetchRunById(historicalRunId!),
    enabled: Boolean(historicalRunId),
  });
  const historicalEventsQuery = useQuery({
    queryKey: ["historical-events", historicalRunId],
    queryFn: () => fetchRunEvents(historicalRunId!),
    enabled: Boolean(historicalRunId),
  });
  const historicalEvaluationQuery = useQuery({
    queryKey: ["historical-evaluation", historicalRunId],
    queryFn: () => fetchEvaluation(historicalRunId!),
    enabled: Boolean(historicalRunId),
  });

  const selectedRun = historicalRunId ? historicalRunQuery.data : liveRunQuery.data;
  const selectedEvents = historicalRunId ? historicalEventsQuery.data?.items ?? [] : live.events;
  const selectedEvaluation = historicalRunId ? historicalEvaluationQuery.data : liveEvaluationQuery.data;
  const selectedEvaluationReady = historicalRunId ? Boolean(historicalRunQuery.data?.completed) : liveEvaluationReady;
  const selectedRunId = historicalRunId ?? live.accepted?.run_id ?? null;
  const evidence = useMemo(() => evidenceItems(selectedEvents), [selectedEvents]);
  const serviceOnline = healthQuery.data?.status === "ok";
  const viewingHistorical = historicalRunId !== null;

  const currentPrimaryDestination: PrimaryDestination = view === "history" ? "history" : view === "technical" ? "technical" : "home";

  const navigate = (destination: PrimaryDestination) => {
    if (destination === "home") setView("home");
    if (destination === "history") setView("history");
    if (destination === "technical") setView("technical");
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalized = requestText.trim();
    if (!normalized || live.submitting || !serviceOnline) return;
    setHistoricalRunId(null);
    try {
      await live.submit(normalized);
      setView("result");
    } catch {
      setView("home");
    }
  };

  const startNew = () => {
    setHistoricalRunId(null);
    live.clear();
    setRequestText("");
    setView("home");
    window.requestAnimationFrame(() => document.getElementById("agent-request")?.focus());
  };

  const useExample = (example: string) => {
    setRequestText(example);
    window.requestAnimationFrame(() => document.getElementById("agent-request")?.focus());
  };

  const selectHistoricalRun = (runId: string | null) => {
    setHistoricalRunId(runId);
    setView("result");
  };

  const followActionRun = (run: RunAccepted) => {
    setHistoricalRunId(null);
    live.follow(run);
    setView("result");
  };

  const useTechnicalPrompt = (prompt: string) => {
    setRequestText(prompt);
    setView("home");
    window.requestAnimationFrame(() => document.getElementById("agent-request")?.focus());
  };

  const openTechnical = (section: TechnicalSection = "analysis") => {
    setTechnicalSection(section);
    setView("technical");
  };

  const technicalCopy = technicalHeading(technicalSection);
  const isCoreTechnicalSection = technicalSection === "analysis" || technicalSection === "quality" || technicalSection === "data" || technicalSection === "system";

  return (
    <div className="app-shell task-driven-shell">
      <a className="skip-link" href="#main-content">Skip to main content</a>

      <header className="task-header">
        <div className="task-brand">
          <strong>Academy × TRACTIAN</strong>
        </div>
        <div className="task-service-state" aria-live="polite">
          <span className={`status-dot ${serviceOnline ? "online" : "offline"}`} aria-hidden="true" />
          <span>{serviceOnline ? "Online" : "Unavailable"}</span>
        </div>
      </header>

      <PrimaryNavigation current={currentPrimaryDestination} onNavigate={navigate} />

      <main id="main-content">
        {view === "home" && (
          <section className="task-home" aria-labelledby="home-question-heading">
            <div className="task-home-inner">
              <h1 id="home-question-heading">What do you want to understand?</h1>
              <form className="task-question-form" onSubmit={submit}>
                <label className="visually-hidden" htmlFor="agent-request">Question about your equipment</label>
                <textarea
                  id="agent-request"
                  value={requestText}
                  onChange={(event) => setRequestText(event.target.value)}
                  placeholder="For example: Why is Compressor 04 vibrating more than usual?"
                  maxLength={20_000}
                  rows={5}
                  autoFocus
                />
                <div className="task-question-actions">
                  <button className="task-primary-action" type="submit" disabled={!requestText.trim() || live.submitting || !serviceOnline}>
                    {live.submitting ? "Starting…" : "Analyse"}
                  </button>
                </div>
              </form>

              {live.error && (
                <div className="task-error" role="alert">
                  <strong>We could not start the analysis.</strong> Try again. If the problem continues, Technical contains the system details.
                </div>
              )}

              <details className="task-examples">
                <summary>See example questions</summary>
                <div className="task-example-list">
                  {QUESTION_EXAMPLES.map((example) => <button key={example} type="button" onClick={() => useExample(example)}>{example}</button>)}
                </div>
              </details>

              {live.accepted && (
                <button className="task-text-button" type="button" onClick={() => setView("result")}>Return to current analysis</button>
              )}
            </div>
          </section>
        )}

        {view === "result" && (
          <section className="task-screen task-screen-reading" aria-label="Analysis result">
            <button className="task-back-button" type="button" onClick={() => setView(viewingHistorical ? "history" : "home")}>← {viewingHistorical ? "Analyses" : "Home"}</button>
            {viewingHistorical && historicalRunQuery.isLoading ? (
              <div className="task-empty" role="status">Loading saved analysis…</div>
            ) : (
              <ProductExperience
                selectedRun={selectedRun}
                events={selectedEvents}
                executionStatus={viewingHistorical ? undefined : executionQuery.data?.status}
                connection={live.connection}
                hasLiveRun={Boolean(live.accepted)}
                viewingHistorical={viewingHistorical}
                onOpenEvidence={() => setView("evidence")}
                onOpenTechnical={() => openTechnical("analysis")}
                onStartNew={startNew}
              />
            )}
          </section>
        )}

        {view === "evidence" && (
          <section className="task-screen task-screen-reading" aria-labelledby="evidence-heading">
            <button className="task-back-button" type="button" onClick={() => setView("result")}>← Result</button>
            <header className="task-screen-header">
              <h1 id="evidence-heading">Why did we reach this conclusion?</h1>
              <p>These are the persisted information sources that support the selected analysis. Runtime mechanics stay in Technical.</p>
            </header>

            {selectedRun?.terminal_message && (
              <div className="task-context-summary">
                <span>Conclusion being explained</span>
                <p>{selectedRun.terminal_message}</p>
              </div>
            )}

            {evidence.length ? (
              <ol className="task-evidence-list">
                {evidence.map((item, index) => (
                  <li className="task-evidence-item" key={item.id}>
                    <span className="task-evidence-number" aria-hidden="true">{index + 1}</span>
                    <div>
                      <h3>{item.label}</h3>
                      <p>{item.message || "This source was persisted as supporting evidence for the analysis."}</p>
                      <small>{item.status && item.status >= 200 && item.status < 300 ? "Checked successfully" : "Saved for review"}</small>
                    </div>
                  </li>
                ))}
              </ol>
            ) : (
              <div className="task-empty">No user-visible evidence reference was saved for this analysis.</div>
            )}

            <div className="task-evidence-actions">
              <button type="button" className="task-secondary-action" onClick={() => openTechnical("data")}>Explore full data</button>
              <button type="button" className="task-tertiary-action" onClick={() => openTechnical("analysis")}>Analysis technical details</button>
            </div>
          </section>
        )}

        {view === "history" && (
          <section className="task-screen task-screen-reading" aria-labelledby="analyses-heading">
            <header className="task-screen-header">
              <h1 id="analyses-heading">Analyses</h1>
              <p>Open a previous result to review its conclusion and evidence.</p>
            </header>
            <RunExplorer
              runs={runsQuery.data?.items ?? []}
              selectedRunId={historicalRunId}
              liveRunId={live.accepted?.run_id ?? null}
              loading={runsQuery.isLoading}
              onSelect={selectHistoricalRun}
            />
          </section>
        )}

        {view === "technical" && (
          <section className="task-screen" aria-labelledby="technical-heading">
            <header className="task-screen-header">
              <h1 id="technical-heading">Technical</h1>
              <p>Specialist tools are grouped by the question you are trying to answer. Only one family is shown at a time.</p>
            </header>

            <div className="technical-task-layout">
              <nav className="technical-task-menu" aria-label="Technical tasks">
                {TECHNICAL_SECTIONS.map((section) => (
                  <button
                    key={section.id}
                    type="button"
                    className={technicalSection === section.id ? "is-active" : undefined}
                    aria-current={technicalSection === section.id ? "page" : undefined}
                    onClick={() => setTechnicalSection(section.id)}
                  >
                    <strong>{section.label}</strong>
                    <small>{section.description}</small>
                  </button>
                ))}
              </nav>

              <div className="technical-task-content">
                <header className="task-screen-header">
                  <h2>{technicalCopy.title}</h2>
                  <p>{technicalCopy.description}</p>
                </header>

                {technicalSection === "analysis" && (
                  <article className="panel visual-panel">
                    <div className="section-heading compact"><div><h2>Trace</h2><p className="section-supporting-copy">Safe event sequence for the selected analysis.</p></div></div>
                    <TraceGraph events={selectedEvents} />
                  </article>
                )}

                {isCoreTechnicalSection && (
                  <OperationsWorkspace
                    key="operations-workspace"
                    selectedRunId={selectedRunId}
                    focus={technicalSection as OperationsWorkspaceFocus}
                    onFocusChange={(focus) => setTechnicalSection(focus)}
                  />
                )}

                {technicalSection === "quality" && (
                  <RunVerificationPanel runId={selectedRunId} completed={Boolean(selectedRun?.completed)} />
                )}

                {technicalSection === "system" && (
                  <>
                    <article className="panel visual-panel">
                      <div className="section-heading compact"><div><h2>Architecture</h2><p className="section-supporting-copy">Implementation-backed components and trust boundaries.</p></div></div>
                      {architectureQuery.data ? (
                        <ArchitectureExplorer manifest={architectureQuery.data} events={selectedEvents} hasRun={Boolean(selectedRunId)} hasEvaluation={Boolean(selectedEvaluation?.count)} />
                      ) : <div className="task-empty">Loading architecture manifest…</div>}
                    </article>
                    <Release0CapabilitySurface events={selectedEvents} onUsePrompt={useTechnicalPrompt} />
                  </>
                )}

                {technicalSection === "actions" && <ActionControl selectedRunId={selectedRunId} onFollowExecution={followActionRun} />}

                {technicalSection === "studies" && (
                  <div className="layer-stack">
                    <OperationalValueCollector />
                    <SemanticReviewCollector />
                  </div>
                )}
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
