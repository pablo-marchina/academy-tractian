import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

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
import { DynamicDataExplorer } from "./DynamicDataExplorer";
import { EChart } from "./EChart";

function percent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function HealthStatus({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  const tone = normalized === "ready" || normalized === "available" || normalized === "selected" || normalized === "provider_free"
    ? "health-good"
    : normalized === "not_instrumented" || normalized === "no_selection"
      ? "health-unknown"
      : "health-bad";
  return <span className={`health-status ${tone}`}>{status}</span>;
}

export function OperationsWorkspace({ selectedRunId }: { selectedRunId: string | null }) {
  const overviewQuery = useQuery({ queryKey: ["overview"], queryFn: fetchOverview, refetchInterval: 3_000 });
  const healthQuery = useQuery({ queryKey: ["production-health"], queryFn: fetchProductionHealth, refetchInterval: 5_000 });
  const toolsQuery = useQuery({ queryKey: ["tools-metrics"], queryFn: fetchToolsMetrics, refetchInterval: 5_000 });
  const policiesQuery = useQuery({ queryKey: ["policies-metrics"], queryFn: fetchPoliciesMetrics, refetchInterval: 5_000 });
  const evaluationMetricsQuery = useQuery({ queryKey: ["evaluation-metrics"], queryFn: fetchEvaluationMetrics, refetchInterval: 5_000 });
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

  const overview = overviewQuery.data;
  const health = healthQuery.data;

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
            <div className="health-grid">
              {health.components.map((item) => (
                <div className="health-card" key={item.component}>
                  <div><strong>{item.component}</strong><HealthStatus status={item.status} /></div>
                  <p>{item.detail}</p>
                </div>
              ))}
            </div>
            <div className="instrumentation-gap">
              <strong>Not measured yet</strong>
              <span>{health.not_measured_yet.join(" · ")}</span>
            </div>
          </>
        ) : <p className="muted">Loading production health…</p>}
      </article>

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
          {toolOption && toolsQuery.data?.items.length ? <><EChart option={toolOption} /><div className="compact-data-list">{toolsQuery.data.items.map((item) => <div key={item.tool_name}><strong>{item.tool_name}</strong><span>{item.calls} calls · {item.results} results · {item.observations} observations</span></div>)}</div></> : <p className="muted">No persisted tool activity yet.</p>}
        </article>
        <article className="panel operations-panel">
          <div className="section-heading compact"><div><p className="eyebrow">DETERMINISTIC SAFETY</p><h2>Policy Analytics</h2></div><span className="count-pill">{policiesQuery.data?.count ?? 0} stages</span></div>
          {policyOption && policiesQuery.data?.items.length ? <><EChart option={policyOption} /><div className="compact-data-list">{policiesQuery.data.items.map((item) => <div key={item.policy_stage}><strong>{item.policy_stage}</strong><span>{item.checks} checks · {percent(item.block_rate)} blocked · {item.contained} contained</span></div>)}</div></> : <p className="muted">No persisted policy checks yet.</p>}
        </article>
      </div>

      <div className="operations-two-column">
        <article className="panel operations-panel">
          <div className="section-heading compact"><div><p className="eyebrow">POST-RUNTIME QUALITY</p><h2>Eval Lab</h2></div>{evaluationMetricsQuery.data && <span className="count-pill">blocking {percent(evaluationMetricsQuery.data.blocking_pass_rate)}</span>}</div>
          {evalOption && evaluationMetricsQuery.data?.checks.length ? <><EChart option={evalOption} height={320} /><div className="eval-summary"><span>overall pass {percent(evaluationMetricsQuery.data.overall_pass_rate)}</span><span>{evaluationMetricsQuery.data.rows} check rows</span></div></> : <p className="muted">No persisted evaluation aggregate yet.</p>}
        </article>

        <article className="panel operations-panel provider-lab">
          <div className="section-heading compact"><div><p className="eyebrow">GOVERNED PROVIDER EVIDENCE</p><h2>Provider D01 / D02 Lab</h2></div>{providerQuery.data && <span className="count-pill" title={providerQuery.data.registry_sha256}>registry {providerQuery.data.registry_sha256.slice(0, 10)}</span>}</div>
          {d01 ? <div className="experiment-card"><div className="experiment-heading"><strong>D01</strong><HealthStatus status={d01.selection ?? d01.status} /></div><div className="experiment-kpis"><span>{d01.attempted_calls}/{d01.expected_calls} calls</span><span>USD {d01.cash_cost_usd?.toFixed(2) ?? "—"}</span><span>{d01.packet_observed_neurons?.toFixed(2) ?? "—"} Neurons</span><span>cap {d01.completion_cap_tokens}</span></div>{d01Option && <EChart option={d01Option} height={260} />}{d01.diagnostic && <div className="diagnostic-note"><strong>Completion-budget diagnostic</strong><p>{d01.diagnostic.interpretation}</p><span>{d01.diagnostic.client_failures_at_completion_cap}/{d01.diagnostic.client_failures} CLIENT_FAILURE at exact cap</span></div>}<p className="panel-copy">{d01.note}</p></div> : <p className="muted">D01 registry unavailable.</p>}
          {d02 && <div className="experiment-card prospective"><div className="experiment-heading"><strong>D02</strong><HealthStatus status={d02.status} /></div><div className="experiment-kpis"><span>{d02.attempted_calls}/{d02.expected_calls} calls</span><span>cap {d02.completion_cap_tokens}</span><span>max {d02.packet_max_neurons.toFixed(3)} Neurons</span></div><p>{d02.note}</p><strong className="no-result-label">No live D02 result exists.</strong></div>}
        </article>
      </div>

      <DynamicDataExplorer />
    </section>
  );
}
