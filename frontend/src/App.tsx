import { useQuery } from "@tanstack/react-query";
import { FormEvent, useMemo, useState } from "react";

import {
  fetchEvaluation,
  fetchExecution,
  fetchHealth,
  fetchRun,
} from "./api/client";
import type { SafeEvent } from "./api/types";
import { useLiveRun } from "./hooks/useLiveRun";
import {
  deriveRunEventMetrics,
  eventDisplayLabel,
} from "./state/runEvents";

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
    event.status_code !== null && ["status", String(event.status_code)],
    event.latency_ms !== null && ["latency", `${event.latency_ms} ms`],
    event.reason_code && ["reason", event.reason_code],
  ].filter(Boolean) as [string, string][];

  if (items.length === 0) return null;
  return (
    <div className="event-meta">
      {items.map(([label, value]) => (
        <span key={`${label}:${value}`}>
          <b>{label}</b> {value}
        </span>
      ))}
    </div>
  );
}

export default function App() {
  const [requestText, setRequestText] = useState("");
  const live = useLiveRun();
  const metrics = useMemo(() => deriveRunEventMetrics(live.events), [live.events]);

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    refetchInterval: 5_000,
  });

  const runQuery = useQuery({
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

  const evaluationReady = executionQuery.data?.status === "completed";
  const evaluationQuery = useQuery({
    queryKey: ["evaluation", live.accepted?.run_id],
    queryFn: () => fetchEvaluation(live.accepted!.run_id),
    enabled: Boolean(live.accepted && evaluationReady),
  });

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalized = requestText.trim();
    if (!normalized || live.submitting) return;
    try {
      await live.submit(normalized);
    } catch {
      // Hook exposes sanitized submission error state.
    }
  };

  const blockingChecks = evaluationQuery.data?.items.filter((check) => check.blocking) ?? [];
  const passedChecks = blockingChecks.filter((check) => check.passed).length;
  const run = runQuery.data;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">ACADEMY × TRACTIAN</p>
          <h1>Industrial Agent Operations</h1>
        </div>
        <div className="service-state" aria-live="polite">
          <span className={`status-dot ${healthQuery.data?.status === "ok" ? "online" : "offline"}`} />
          <div>
            <b>{healthQuery.data?.status === "ok" ? "API healthy" : "API unavailable"}</b>
            <small>{healthQuery.data?.version ?? "checking service"}</small>
          </div>
        </div>
      </header>

      <main>
        <section className="control-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">LIVE RUN</p>
              <h2>Execute the production agent</h2>
            </div>
            {live.accepted && (
              <button className="ghost-button" type="button" onClick={live.clear}>
                Clear run
              </button>
            )}
          </div>

          <form className="request-form" onSubmit={submit}>
            <label htmlFor="agent-request">Industrial request</label>
            <textarea
              id="agent-request"
              value={requestText}
              onChange={(event) => setRequestText(event.target.value)}
              placeholder="Inspect the asset evidence, investigate anomalies, and return a safe conclusion."
              maxLength={20_000}
              rows={4}
            />
            <div className="request-actions">
              <span>{requestText.length.toLocaleString()} / 20,000</span>
              <button type="submit" disabled={!requestText.trim() || live.submitting}>
                {live.submitting ? "Submitting…" : "Start production run"}
              </button>
            </div>
          </form>

          {live.error && <div className="error-banner">{live.error}</div>}
        </section>

        <section className="run-strip" aria-live="polite">
          <div>
            <span className="metric-label">Stream</span>
            <strong className={`connection connection-${live.connection}`}>{live.connection}</strong>
          </div>
          <div>
            <span className="metric-label">Execution</span>
            <strong>{executionQuery.data?.status ?? (live.accepted ? "accepted" : "—")}</strong>
          </div>
          <div className="run-id-cell">
            <span className="metric-label">Safe run ID</span>
            <strong title={live.accepted?.run_id}>{live.accepted?.run_id ?? "No active run"}</strong>
          </div>
          <div>
            <span className="metric-label">Config</span>
            <strong title={run?.config_hash}>{run?.config_hash?.slice(0, 12) ?? "—"}</strong>
          </div>
        </section>

        <section className="metric-grid">
          {[
            ["Events", metrics.events],
            ["Model calls", metrics.modelCalls],
            ["Tool calls", metrics.toolCalls],
            ["Policy blocks", metrics.policyBlocks],
            ["Evidence refs", metrics.evidenceRefs],
            ["Errors", metrics.errors],
          ].map(([label, value]) => (
            <article className="metric-card" key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </article>
          ))}
        </section>

        <section className="workspace-grid">
          <article className="panel timeline-panel">
            <div className="section-heading compact">
              <div>
                <p className="eyebrow">RUNTIME TIME</p>
                <h2>Canonical event timeline</h2>
              </div>
              <span className="count-pill">{live.events.length} events</span>
            </div>

            {live.events.length === 0 ? (
              <div className="empty-state">
                <strong>No runtime events yet</strong>
                <p>Submit a request. This panel only grows when the backend emits a real safe event.</p>
              </div>
            ) : (
              <ol className="timeline-list">
                {live.events.map((event) => (
                  <li key={event.event_id} className={`timeline-item tone-${eventTone(event)}`}>
                    <div className="sequence">{String(event.sequence).padStart(2, "0")}</div>
                    <div className="timeline-content">
                      <div className="event-title-row">
                        <div>
                          <span className="origin-badge">{event.origin}</span>
                          <strong>{eventDisplayLabel(event)}</strong>
                        </div>
                        <small>{event.latency_ms !== null ? `${event.latency_ms} ms` : event.timestamp ?? ""}</small>
                      </div>
                      <EventMeta event={event} />
                      {event.message && <p className="event-message">{event.message}</p>}
                    </div>
                  </li>
                ))}
              </ol>
            )}
          </article>

          <aside className="side-stack">
            <article className="panel terminal-panel">
              <p className="eyebrow">CUSTOMER-SAFE OUTPUT</p>
              <h2>Terminal outcome</h2>
              {!run?.completed ? (
                <div className="empty-state small">
                  <strong>Runtime still active</strong>
                  <p>No terminal result is shown until the persisted run is actually complete.</p>
                </div>
              ) : (
                <dl className="detail-list">
                  <div><dt>Decision</dt><dd>{valueOrDash(run.terminal_decision)}</dd></div>
                  <div><dt>Response mode</dt><dd>{valueOrDash(run.terminal_response_mode)}</dd></div>
                  <div><dt>Reason</dt><dd>{valueOrDash(run.terminal_reason_code)}</dd></div>
                  <div className="message-detail"><dt>Message</dt><dd>{valueOrDash(run.terminal_message)}</dd></div>
                </dl>
              )}
            </article>

            <article className="panel evaluation-panel">
              <div className="evaluator-boundary">
                <p className="eyebrow">POST-RUNTIME ONLY</p>
                <span>Evaluator isolated from agent-time state</span>
              </div>
              <h2>Evaluation</h2>
              {!run?.completed ? (
                <div className="empty-state small">
                  <strong>Not evaluated yet</strong>
                  <p>Evaluation appears only after the runtime has emitted its terminal trace.</p>
                </div>
              ) : !evaluationReady ? (
                <p className="muted">Runtime finished. Waiting for post-runtime evaluation persistence…</p>
              ) : evaluationQuery.isLoading ? (
                <p className="muted">Loading safe evaluation…</p>
              ) : evaluationQuery.data?.count ? (
                <>
                  <div className="evaluation-score">
                    <strong>{passedChecks}/{blockingChecks.length}</strong>
                    <span>blocking checks passed</span>
                  </div>
                  <ul className="check-list">
                    {evaluationQuery.data.items.map((check) => (
                      <li key={check.check_name}>
                        <span className={check.passed ? "check-pass" : "check-fail"}>
                          {check.passed ? "PASS" : "FAIL"}
                        </span>
                        <span>{check.check_name}</span>
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <p className="muted">No safe evaluation rows are available.</p>
              )}
            </article>
          </aside>
        </section>
      </main>
    </div>
  );
}
