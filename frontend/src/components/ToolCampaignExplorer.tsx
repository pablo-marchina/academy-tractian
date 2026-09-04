import { useQuery } from "@tanstack/react-query";

import { fetchToolCampaign } from "../api/client";
import type { ToolCampaignOperation, ToolCampaignResponse } from "../api/toolCoverageTypes";

function dimensionLabel(name: string): string {
  return name.replaceAll("_", " ");
}

function passedDimensions(operation: ToolCampaignOperation): number {
  return operation.dimensions.filter((dimension) => dimension.state === "PASS").length;
}

export function ToolCampaignPanel({ campaign }: { campaign: ToolCampaignResponse }) {
  return (
    <article className="panel coverage-panel" data-testid="tool-campaign-panel">
      <div className="section-heading compact coverage-heading">
        <div>
          <p className="eyebrow">INTEGRATION PROOF CAMPAIGN</p>
          <h2>18-operation claim gate</h2>
        </div>
        <span className="count-pill">
          {campaign.complete_operations}/{campaign.normalized_operations} complete
        </span>
      </div>

      <p className="coverage-claim">{campaign.claim_boundary}</p>

      <section className="coverage-metrics" aria-label="Integration campaign metrics">
        <div className="coverage-metric"><span>Complete</span><strong>{campaign.complete_operations}</strong></div>
        <div className="coverage-metric"><span>Incomplete</span><strong>{campaign.incomplete_operations}</strong></div>
        <div className="coverage-metric"><span>Reads</span><strong>{campaign.reads}</strong></div>
        <div className="coverage-metric"><span>Actions</span><strong>{campaign.actions}</strong></div>
        <div className="coverage-metric"><span>Evidence state</span><strong>{campaign.evidence_state}</strong></div>
      </section>

      <div className="coverage-table-wrap">
        <table className="coverage-table">
          <thead>
            <tr>
              <th>Operation</th>
              <th>Route</th>
              <th>Proof</th>
              <th>Unproven dimensions</th>
            </tr>
          </thead>
          <tbody>
            {campaign.operations.map((operation) => {
              const unproven = operation.dimensions.filter((dimension) => dimension.state !== "PASS");
              return (
                <tr key={operation.operation} data-campaign-tool={operation.operation}>
                  <td>
                    <strong className="coverage-tool-name">{operation.operation}</strong>
                    <span className={`coverage-operation-state tone-${operation.complete ? "success" : "neutral"}`}>
                      {operation.complete ? "COMPLETE" : "INCOMPLETE"}
                    </span>
                  </td>
                  <td className="coverage-route"><b>{operation.method}</b> {operation.path_template}</td>
                  <td>{passedDimensions(operation)}/{operation.dimensions.length}</td>
                  <td>
                    {unproven.length === 0
                      ? "—"
                      : unproven.map((dimension) => dimensionLabel(dimension.name)).join(", ")}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="coverage-footer">
        <span>Schema: {campaign.schema_version}</span>
        <span>Transport telemetry is not semantic proof.</span>
      </div>
    </article>
  );
}

export function ToolCampaignExplorer() {
  const campaignQuery = useQuery({
    queryKey: ["tractian-tool-campaign"],
    queryFn: fetchToolCampaign,
    refetchInterval: 10_000,
    staleTime: 5_000,
  });

  if (campaignQuery.isPending) {
    return (
      <article className="panel coverage-panel">
        <p className="eyebrow">INTEGRATION PROOF CAMPAIGN</p>
        <h2>18-operation claim gate</h2>
        <div className="empty-state small">
          <strong>Loading proof requirements</strong>
          <p>No completion claim is inferred while campaign evidence is unresolved.</p>
        </div>
      </article>
    );
  }

  if (campaignQuery.isError || !campaignQuery.data) {
    return (
      <article className="panel coverage-panel coverage-unavailable" role="status">
        <p className="eyebrow">INTEGRATION PROOF CAMPAIGN</p>
        <h2>18-operation claim gate</h2>
        <div className="empty-state small">
          <strong>Campaign evidence unavailable</strong>
          <p>The frontend fails closed and reports no completed integration proof.</p>
        </div>
      </article>
    );
  }

  return <ToolCampaignPanel campaign={campaignQuery.data} />;
}
