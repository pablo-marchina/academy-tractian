import { useQuery } from "@tanstack/react-query";

import { fetchToolCoverage } from "../api/client";
import type {
  IntegrationEvidenceState,
  ToolCoverageOperation,
  ToolCoverageResponse,
} from "../api/toolCoverageTypes";

function yesNo(value: boolean): string {
  return value ? "YES" : "NO";
}

function evidenceTone(state: IntegrationEvidenceState): string {
  if (state === "VALID") return "success";
  if (state === "INVALID") return "danger";
  return "warning";
}

function operationTone(operation: ToolCoverageOperation): string {
  if (operation.hosted_live_success) return "success";
  if (operation.hosted_live_exercised) return "warning";
  if (operation.hosted_live_blocked_by_safety) return "safe-block";
  if (operation.hosted_live_outcomes.includes("transport_failure")) return "danger";
  if (operation.frozen_route_execution_evidenced) return "historical";
  return "neutral";
}

function operationState(operation: ToolCoverageOperation): string {
  if (operation.hosted_live_success) return "HOSTED SUCCESS";
  if (operation.hosted_live_exercised) return "HOSTED OBSERVED";
  if (operation.hosted_live_blocked_by_safety) return "SAFETY BLOCKED";
  if (operation.hosted_live_outcomes.includes("transport_failure")) return "TRANSPORT FAILURE";
  if (operation.hosted_live_outcomes.includes("unavailable")) return "UNAVAILABLE";
  if (operation.frozen_route_execution_evidenced) return "FROZEN ONLY";
  return "NOT EXERCISED";
}

export function ToolCoveragePanel({ coverage }: { coverage: ToolCoverageResponse }) {
  const { summary, evidence } = coverage;
  const metrics = [
    ["Contract", `${summary.contract_registered}/${summary.normalized_operations}`],
    ["Implementation", `${summary.implementation_routes_present}/${summary.normalized_operations}`],
    ["Hosted exercised", `${summary.hosted_live_exercised}/${summary.normalized_operations}`],
    ["Hosted success", `${summary.hosted_live_success}/${summary.normalized_operations}`],
    ["HTTP error observed", summary.hosted_live_http_error_observed],
    ["Safety blocked", summary.hosted_live_blocked_by_safety],
  ] as const;

  return (
    <article className="panel coverage-panel" data-testid="tool-coverage-panel">
      <div className="section-heading compact coverage-heading">
        <div>
          <p className="eyebrow">TRACTIAN API INTEGRATION</p>
          <h2>18-operation evidence matrix</h2>
        </div>
        <span className={`coverage-status coverage-status-${coverage.status.toLowerCase()}`}>
          {coverage.status.replaceAll("_", " ")}
        </span>
      </div>

      <p className="coverage-claim">{coverage.claim_boundary}</p>

      <section className="coverage-metrics" aria-label="Tool coverage metrics">
        {metrics.map(([label, value]) => (
          <div className="coverage-metric" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </section>

      <div className="coverage-evidence-row" aria-label="Evidence source health">
        {(["frozen", "hosted_live"] as const).map((scope) => {
          const item = evidence[scope];
          return (
            <div className="coverage-evidence-source" key={scope}>
              <span className={`coverage-dot tone-${evidenceTone(item.state)}`} />
              <div>
                <b>{scope === "frozen" ? "Frozen evidence" : "Hosted-live evidence"}</b>
                <small>{item.state} · {item.source}</small>
                {item.validation_errors.length > 0 && (
                  <small className="coverage-validation-error">
                    {item.validation_errors.join(", ")}
                  </small>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="coverage-table-wrap">
        <table className="coverage-table">
          <thead>
            <tr>
              <th>Operation</th>
              <th>Kind</th>
              <th>Route</th>
              <th>Contract</th>
              <th>Impl.</th>
              <th>Frozen</th>
              <th>Hosted</th>
              <th>Success</th>
              <th>Observed outcomes</th>
            </tr>
          </thead>
          <tbody>
            {coverage.operations.map((operation) => (
              <tr key={operation.tool_name} data-tool={operation.tool_name}>
                <td>
                  <strong className="coverage-tool-name">{operation.tool_name}</strong>
                  <span className={`coverage-operation-state tone-${operationTone(operation)}`}>
                    {operationState(operation)}
                  </span>
                </td>
                <td>{operation.kind}{operation.impact ? ` · ${operation.impact}` : ""}</td>
                <td className="coverage-route"><b>{operation.method}</b> {operation.path_template}</td>
                <td className={operation.contract_registered ? "coverage-pass" : "coverage-fail"}>
                  {yesNo(operation.contract_registered)}
                </td>
                <td className={operation.implementation_route_present ? "coverage-pass" : "coverage-fail"}>
                  {yesNo(operation.implementation_route_present)}
                </td>
                <td>{yesNo(operation.frozen_route_execution_evidenced)}</td>
                <td className={operation.hosted_live_exercised ? "coverage-pass" : "coverage-muted"}>
                  {yesNo(operation.hosted_live_exercised)}
                </td>
                <td className={operation.hosted_live_success ? "coverage-pass" : "coverage-muted"}>
                  {yesNo(operation.hosted_live_success)}
                </td>
                <td>
                  {operation.hosted_live_outcomes.length > 0
                    ? operation.hosted_live_outcomes.join(", ")
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="coverage-footer">
        <span>Frozen route evidence: {summary.frozen_route_execution_evidenced}/{summary.normalized_operations}</span>
        <span>Hosted not exercised: {summary.hosted_live_not_exercised}/{summary.normalized_operations}</span>
        <span>Schema: {coverage.schema_version}</span>
      </div>
    </article>
  );
}

export function ToolCoverageExplorer() {
  const coverageQuery = useQuery({
    queryKey: ["tractian-tool-coverage"],
    queryFn: fetchToolCoverage,
    refetchInterval: 10_000,
    staleTime: 5_000,
  });

  if (coverageQuery.isPending) {
    return (
      <article className="panel coverage-panel">
        <p className="eyebrow">TRACTIAN API INTEGRATION</p>
        <h2>18-operation evidence matrix</h2>
        <div className="empty-state small">
          <strong>Loading machine-readable coverage</strong>
          <p>No integration count is inferred while the evidence endpoint is unresolved.</p>
        </div>
      </article>
    );
  }

  if (coverageQuery.isError || !coverageQuery.data) {
    return (
      <article className="panel coverage-panel coverage-unavailable" role="status">
        <p className="eyebrow">TRACTIAN API INTEGRATION</p>
        <h2>18-operation evidence matrix</h2>
        <div className="empty-state small">
          <strong>Coverage evidence unavailable</strong>
          <p>The frontend fails closed and shows no inferred integration coverage.</p>
        </div>
      </article>
    );
  }

  return <ToolCoveragePanel coverage={coverageQuery.data} />;
}
