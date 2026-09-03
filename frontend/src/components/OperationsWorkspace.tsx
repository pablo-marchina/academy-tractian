import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo, useRef, useState } from "react";

import {
  fetchEvaluationMetrics,
  fetchEvidence,
  fetchLineage,
  fetchOverview,
  fetchPoliciesMetrics,
  fetchProductionHealth,
  fetchProviderExperiments,
  fetchToolsMetrics,
} from "../api/client";
import { evaluationOption, policiesOption, providerOption, toolsOption } from "../state/analyticsOptions";
import { DynamicDataExplorer, type AnalyticsDrilldown } from "./DynamicDataExplorer";
import { EChart, type EChartDataPoint } from "./EChart";

function percent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function percentagePoints(value: number): string {
  const points = value * 100;
  return `${points >= 0 ? "+" : ""}${points.toFixed(1)} pp`;
}

function relativeDelta(current: number, baseline: number): string {
  if (baseline === 0) return current === 0 ? "0.0%" : "from 0";
  const delta = ((current / baseline) - 1) * 100;
  return `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}%`;
}

function milliseconds(value: number | null | undefined): string {
  return value === null || value === undefined ? "—" : `${value.toFixed(1)} ms`;
}

function HealthStatus({ status, engagedIsSafe = false }: { status: string; engagedIsSafe?: boolean }) {
  const normalized = status.toLowerCase();
  const good = new Set(["ready", "available", "selected", "provider_free", "instrumented", "measured", "observed", "disengaged"]);
  const unknown = new Set(["not_instrumented", "no_selection", "no_observations", "not_executed"]);
  const tone = good.has(normalized) || (engagedIsSafe && normalized === "engaged")
    ? "health-good"
    : unknown.has(normalized)
      ? "health-unknown"
      : "health-bad";
  return <span className={`health-status ${tone}`}>{status}</span>;
}

export function OperationsWorkspace({ selectedRunId }: { selectedRunId: string | null }) {
  const [drilldown, setDrilldown] = useState<AnalyticsDrilldown | null>(null);
  const drilldownSequence = useRef(0);

  const overviewQuery = useQuery({ queryKey: ["overview"], queryFn: fetchOverview, refetchInterval: 3_000 });
  const healthQuery = useQuery({ queryKey: ["production-health"], queryFn: fetchProductionHealth, refetchInterval: 2_000 });
  const toolsQuery = useQuery({ queryKey: ["tools-metrics", selectedRunId], queryFn: () => fetchToolsMetrics(selectedRunId), refetchInterval: 5_000 });
  const policiesQuery = useQuery({ queryKey: ["policies-metrics", selectedRunId], queryFn: () => fetchPoliciesMetrics(selectedRunId), refetchInterval: 5_000 });
  const evaluationMetricsQuery = useQuery({ queryKey: ["evaluation-metrics", selectedRunId], queryFn: () => fetchEvaluationMetrics(selectedRunId), refetchInterval: 5_000 });
  const providerQuery = useQuery({ queryKey: ["provider-experiments"], queryFn: fetchProviderExperiments, staleTime: 60_000 });
  const evidenceQuery = useQuery({
    queryKey: ["evidence", selectedRunId],
    queryFn: () => fetchEvidence(selectedRunId!),
    enabled: Boolean(selectedRunId),
    refetchInterval: selectedRunId ? 1_500 : false,
  });
  const lineageQuery = useQuery({
    queryKey: ["lineage", selectedRunId],
    queryFn: () => fetchLineage(selectedRunId!),
    enabled: Boolean(selectedRunId),
    refetchInterval: selectedRunId ? 1_500 : false,
  });

  const d01 = providerQuery.data?.experiments.find((item) => item.experiment_id === "D01");
  const d02 = providerQuery.data?.experiments.find((item) => item.experiment_id === "D02");
  const toolOption = useMemo(() => toolsQuery.data ? toolsOption(toolsQuery.data) : null, [toolsQuery.data]);
  const policyOption = useMemo(() => policiesQuery.data ? policiesOption(policiesQuery.data) : null, [policiesQuery.data]);
  const evalOption = useMemo(() => evaluationMetricsQuery.data ? evaluationOption(evaluationMetricsQuery.data) : null, [evaluationMetricsQuery.data]);
  const d01Option = useMemo(() => d01 && d01.candidates.length ? providerOption(d01) : null, [d01]);
  const d02Option = useMemo(() => d02 && d02.candidates.length ? providerOption(d02) : null, [d02]);
  const providerDeltas = useMemo(() => {
    if (!d01 || !d02 || d02.status !== "COMPLETE") return [];
    return d02.candidates.flatMap((current) => {
      const baseline = d01.candidates.find((item) => item.candidate_id === current.candidate_id);
      if (!baseline) return [];
      return [{ current, baseline }];
    });
  }, [d01, d02]);

  const requestDrilldown = useCallback((request: Omit<AnalyticsDrilldown, "key">) => {
    drilldownSequence.current += 1;
    setDrilldown({ ...request, key: drilldownSequence.current });
  }, []);

  const toolDrilldown = useCallback((point: EChartDataPoint) => {
    if (!point.name) return;
    requestDrilldown({ dataset: "events", dimension: "event_type", filterField: "tool_name", filterValue: point.name, chartType: "bar" });
  }, [requestDrilldown]);

  const policyDrilldown = useCallback((point: EChartDataPoint) => {
    if (!point.name) return;
    requestDrilldown({ dataset: "events", dimension: "policy_allowed", filterField: "policy_stage", filterValue: point.name, chartType: "bar" });
  }, [requestDrilldown]);

  const evaluationDrilldown = useCallback((point: EChartDataPoint) => {
    if (!point.name) return;
    requestDrilldown({ dataset: "evaluations", dimension: "passed", filterField: "check_name", filterValue: point.name, chartType: "bar" });
  }, [requestDrilldown]);

  const overview = overviewQuery.data;
  const health = healthQuery.data;
  const measured = health?.measured;
  const heartbeat = measured?.runtime_heartbeat;
  const pressure = measured?.executor_pressure;
  const observability = measured?.observability;
  const sse = measured?.sse;
  const provider = measured?.provider_operability;
  const adapter = measured?.tractian_adapter_operability;
  const controls = measured?.controls;
  const analyticsScope = selectedRunId ?? "all persisted runs";

  return (
    <section className="operations-workspace">
      <div className="workspace-title">
        <div><p className="eyebrow">OPERATIONS WORKSPACE</p><h2>Evidence, quality, policy and production state</h2></div>
        <span className="count-pill">safe read model only</span>
      </div>

      <article className="panel operations-panel mission-control">
        <div className="section-heading compact">
          <div><p className="eyebrow">GLOBAL PRODUCT STATE</p><h2>Mission Control</h2></div>
          {health && <HealthStatus status={health.overall_status} />}
        </div>
        <div className="mission-kpis">
          {[
            ["Runs", overview?.total_runs ?? 0],
            ["Completed", overview?.completed_runs ?? 0],
            ["Model calls", overview?.model_calls ?? 0],
            ["Tool calls", overview?.tool_calls ?? 0],
            ["Policy blocks", overview?.policy_blocks ?? 0],
            ["Errors", overview?.errors ?? 0],
          ].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}
        </div>
        {health ? (
          <>
            <div className="telemetry-kpis">
              <div><span>Heartbeat age</span><strong>{milliseconds(heartbeat?.age_ms)}</strong><small>{heartbeat?.status ?? "not instrumented"}</small></div>
              <div><span>Executor</span><strong>{pressure ? `${pressure.active_runs} / ${pressure.max_workers}` : "—"}</strong><small>{pressure ? `${pressure.queued_runs} queued` : "not instrumented"}</small></div>
              <div><span>Active SSE</span><strong>{sse?.active_clients ?? "—"}</strong><small>{sse ? `${sse.reconnects} reconnects` : "not instrumented"}</small></div>
              <div><span>Event → persist p95</span><strong>{milliseconds(observability?.runtime_event_to_persistence.p95_ms)}</strong><small>{observability?.runtime_event_to_persistence.count ?? 0} samples</small></div>
              <div><span>Persist → SSE p95</span><strong>{milliseconds(sse?.persistence_to_delivery.p95_ms)}</strong><small>{sse?.persistence_to_delivery.count ?? 0} deliveries</small></div>
              <div><span>Obs overhead p95</span><strong>{milliseconds(observability?.publish_overhead.p95_ms)}</strong><small>{observability?.publisher_failures ?? 0} failures</small></div>
            </div>
            <div className="health-grid">
              {health.components.map((item) => (
                <div className="health-card" key={item.component}>
                  <div><strong>{item.component}</strong><HealthStatus status={item.status} engagedIsSafe={item.component === "action_kill_switch"} /></div>
                  <p>{item.detail}</p>
                </div>
              ))}
            </div>
            <div className="operability-strip">
              <div><strong>Provider passive operability</strong><span>{provider ? `${provider.observations} observations · ${percent(provider.failure_rate)} failures · p95 ${milliseconds(provider.latency.p95_ms)}` : "unavailable"}</span><small>external probe: no</small></div>
              <div><strong>TRACTIAN adapter passive operability</strong><span>{adapter ? `${adapter.status_observations} status observations · ${percent(adapter.http_2xx_rate)} HTTP 2xx` : "unavailable"}</span><small>external probe: no</small></div>
              <div><strong>Kill switches</strong><span>provider {controls?.provider_kill_switch.engaged ? "ENGAGED" : "disengaged"} · actions {controls?.action_kill_switch.engaged ? "ENGAGED" : "disengaged"}</span><small>no public mutation endpoint</small></div>
            </div>
            <div className="instrumentation-gap">
              <strong>Still not measured</strong>
              <span>{health.not_measured_yet.length ? health.not_measured_yet.join(" · ") : "none"}</span>
            </div>
          </>
        ) : <p className="muted">Loading production health…</p>}
      </article>

      <div className="analytics-scope-banner global-scope">
        <strong>Global analytics scope</strong>
        <span title={selectedRunId ?? undefined}>{analyticsScope}</span>
        <small>Evidence, lineage, tools, policy, eval and Dynamic Explorer share this run scope. Product Health and Provider Lab remain global.</small>
      </div>

      <div className="operations-two-column">
        <article className="panel operations-panel">
          <div className="section-heading compact"><div><p className="eyebrow">SELECTED RUN</p><h2>Evidence Explorer</h2></div><span className="count-pill">{evidenceQuery.data?.count ?? 0} refs</span></div>
          {!selectedRunId ? <div className="empty-state small"><strong>No run selected</strong><p>Select a live or historical run to inspect only persisted safe evidence references.</p></div>
            : evidenceQuery.data?.items.length ? (
              <div className="evidence-list">{evidenceQuery.data.items.map((item) => (
                <div className="evidence-card" key={`${item.sequence}:${item.evidence_id}`}>
                  <span className="origin-badge">OBSERVATION</span>
                  <strong>{item.evidence_id}</strong>
                  <dl><div><dt>sequence</dt><dd>{item.sequence}</dd></div><div><dt>tool</dt><dd>{item.tool_name ?? "—"}</dd></div><div><dt>status</dt><dd>{item.status_code ?? "—"}</dd></div></dl>
                </div>
              ))}</div>
            ) : <div className="empty-state small"><strong>No safe evidence refs</strong><p>This run has not emitted a persisted evidence reference.</p></div>}
        </article>

        <article className="panel operations-panel lineage-panel">
          <div className="section-heading compact"><div><p className="eyebrow">PROVENANCE</p><h2>Output Lineage</h2></div><span className="count-pill">{lineageQuery.data?.cards.length ?? 0} cards</span></div>
          {!selectedRunId ? <div className="empty-state small"><strong>No lineage selected</strong><p>Lineage is never synthesized without a real run.</p></div>
            : lineageQuery.data?.cards.length ? (
              <ol className="lineage-list">{lineageQuery.data.cards.map((card) => (
                <li key={card.lineage_id} className={card.origin === "EVALUATOR" ? "lineage-evaluator" : ""}>
                  <span className="lineage-sequence">{card.sequence}</span>
                  <div><div className="lineage-heading"><span className="origin-badge">{card.origin}</span><strong>{card.event_type}</strong></div>
                    <div className="lineage-meta">{card.tool_name && <span>tool {card.tool_name}</span>}{card.decision_kind && <span>decision {card.decision_kind}</span>}{card.policy_stage && <span>policy {card.policy_stage}</span>}{card.evidence_id && <span>evidence {card.evidence_id}</span>}{card.reason_code && <span>reason {card.reason_code}</span>}</div>
                    {card.message && <p>{card.message}</p>}
                    {card.evaluation && <div className="lineage-checks">{card.evaluation.map((check) => <span key={check.check_name} className={check.passed ? "check-pass" : "check-fail"}>{check.passed ? "PASS" : "FAIL"} {check.check_name}</span>)}</div>}
                  </div>
                </li>
              ))}</ol>
            ) : <div className="empty-state small"><strong>No lineage rows</strong><p>The backend has no safe events for this run yet.</p></div>}
        </article>
      </div>

      <div className="operations-two-column">
        <article className="panel operations-panel">
          <div className="section-heading compact"><div><p className="eyebrow">TOOL CONTRACT</p><h2>Tools Analytics</h2></div><span className="count-pill">{toolsQuery.data?.count ?? 0} tools</span></div>
          {toolOption && toolsQuery.data?.items.length ? <><EChart option={toolOption} onDataPointClick={toolDrilldown} /><div className="compact-data-list">{toolsQuery.data.items.map((item) => <div key={item.tool_name}><div><strong>{item.tool_name}</strong><button className="drilldown-button" type="button" onClick={() => requestDrilldown({ dataset: "events", dimension: "event_type", filterField: "tool_name", filterValue: item.tool_name, chartType: "bar" })}>drill down</button></div><span>{item.calls} calls · {item.results} results · {item.observations} observations</span></div>)}</div></> : <p className="muted">No persisted tool activity in this scope.</p>}
        </article>
        <article className="panel operations-panel">
          <div className="section-heading compact"><div><p className="eyebrow">DETERMINISTIC SAFETY</p><h2>Policy Analytics</h2></div><span className="count-pill">{policiesQuery.data?.count ?? 0} stages</span></div>
          {policyOption && policiesQuery.data?.items.length ? <><EChart option={policyOption} onDataPointClick={policyDrilldown} /><div className="compact-data-list">{policiesQuery.data.items.map((item) => <div key={item.policy_stage}><div><strong>{item.policy_stage}</strong><button className="drilldown-button" type="button" onClick={() => requestDrilldown({ dataset: "events", dimension: "policy_allowed", filterField: "policy_stage", filterValue: item.policy_stage, chartType: "bar" })}>drill down</button></div><span>{item.checks} checks · {percent(item.block_rate)} blocked · {item.contained} contained</span></div>)}</div></> : <p className="muted">No persisted policy checks in this scope.</p>}
        </article>
      </div>

      <div className="operations-two-column">
        <article className="panel operations-panel">
          <div className="section-heading compact"><div><p className="eyebrow">POST-RUNTIME QUALITY</p><h2>Eval Lab</h2></div>{evaluationMetricsQuery.data && <span className="count-pill">blocking {percent(evaluationMetricsQuery.data.blocking_pass_rate)}</span>}</div>
          {evalOption && evaluationMetricsQuery.data?.checks.length ? <><EChart option={evalOption} height={320} onDataPointClick={evaluationDrilldown} /><div className="compact-data-list">{evaluationMetricsQuery.data.checks.map((item) => <div key={item.check_name}><div><strong>{item.check_name}</strong><button className="drilldown-button" type="button" onClick={() => requestDrilldown({ dataset: "evaluations", dimension: "passed", filterField: "check_name", filterValue: item.check_name, chartType: "bar" })}>drill down</button></div><span>{percent(item.pass_rate)} pass · {item.evaluations} evaluations</span></div>)}</div><div className="eval-summary"><span>overall pass {percent(evaluationMetricsQuery.data.overall_pass_rate)}</span><span>{evaluationMetricsQuery.data.rows} check rows</span></div></> : <p className="muted">No persisted evaluation aggregate in this scope.</p>}
        </article>

        <article className="panel operations-panel provider-lab">
          <div className="section-heading compact"><div><p className="eyebrow">GOVERNED PROVIDER EVIDENCE · GLOBAL</p><h2>Provider D01 / D02 Lab</h2></div>{providerQuery.data && <span className="count-pill" title={providerQuery.data.registry_sha256}>registry {providerQuery.data.registry_sha256.slice(0, 10)}</span>}</div>
          {d01 ? <div className="experiment-card"><div className="experiment-heading"><strong>D01</strong><HealthStatus status={d01.selection ?? d01.status} /></div><div className="experiment-kpis"><span>{d01.attempted_calls}/{d01.expected_calls} calls</span><span>USD {d01.cash_cost_usd?.toFixed(2) ?? "—"}</span><span>{d01.packet_observed_neurons?.toFixed(2) ?? "—"} Neurons</span><span>cap {d01.completion_cap_tokens}</span></div>{d01Option && <EChart option={d01Option} height={260} />}{d01.diagnostic && <div className="diagnostic-note"><strong>Completion-budget diagnostic</strong><p>{d01.diagnostic.interpretation}</p><span>{d01.diagnostic.client_failures_at_completion_cap}/{d01.diagnostic.client_failures} CLIENT_FAILURE at exact cap</span></div>}<p className="panel-copy">{d01.note}</p></div> : <p className="muted">D01 registry unavailable.</p>}
          {d02 && d02.status === "COMPLETE" ? (
            <div className="experiment-card">
              <div className="experiment-heading"><strong>D02</strong><HealthStatus status={d02.selection ?? d02.status} /></div>
              <div className="experiment-kpis"><span>{d02.attempted_calls}/{d02.expected_calls} calls</span><span>USD {d02.cash_cost_usd?.toFixed(2) ?? "—"}</span><span>{d02.packet_observed_neurons?.toFixed(2) ?? "—"} Neurons</span><span>cap {d02.completion_cap_tokens}</span></div>
              {d02Option && <EChart option={d02Option} height={260} />}
              <p className="panel-copy">{d02.note}</p>
              {d01 && d01.packet_observed_neurons !== null && d02.packet_observed_neurons !== null && (
                <div className="diagnostic-note">
                  <strong>Controlled D01 → D02 effect · only completion cap changed 512 → 1024</strong>
                  <p>Packet Neurons {relativeDelta(d02.packet_observed_neurons, d01.packet_observed_neurons)} · selection {d01.selection} → {d02.selection}. Both candidates remain below frozen M1/M4/M7 gates.</p>
                  <div className="compact-data-list">
                    {providerDeltas.map(({ current, baseline }) => (
                      <div key={current.candidate_id}>
                        <strong>{current.candidate_id}</strong>
                        <span>
                          success {percentagePoints(current.success_rate - baseline.success_rate)} · M1 {percentagePoints(current.structured_decision_adherence - baseline.structured_decision_adherence)} · M4 {percentagePoints(current.public_task_quality - baseline.public_task_quality)} · M7 {percentagePoints(current.signature_stability - baseline.signature_stability)} · median latency {relativeDelta(current.median_latency_ms, baseline.median_latency_ms)} · Neurons {relativeDelta(current.observed_neurons, baseline.observed_neurons)}
                        </span>
                      </div>
                    ))}
                  </div>
                  <small>Attempt-level failure-subtype distribution is not reconstructed because the accepted aggregate result does not contain the 32-row matrix.</small>
                </div>
              )}
            </div>
          ) : d02 ? (
            <div className="experiment-card prospective"><div className="experiment-heading"><strong>D02</strong><HealthStatus status={d02.status} /></div><div className="experiment-kpis"><span>{d02.attempted_calls}/{d02.expected_calls} calls</span><span>cap {d02.completion_cap_tokens}</span><span>max {d02.packet_max_neurons.toFixed(3)} Neurons</span></div><p>{d02.note}</p><strong className="no-result-label">No live D02 result exists.</strong></div>
          ) : null}
        </article>
      </div>

      <DynamicDataExplorer globalRunId={selectedRunId} drilldown={drilldown} />
    </section>
  );
}
