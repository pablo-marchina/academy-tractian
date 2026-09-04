import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ToolCampaignResponse } from "../api/toolCoverageTypes";
import { ToolCampaignPanel } from "./ToolCampaignExplorer";


function campaign(): ToolCampaignResponse {
  return {
    schema_version: "tractian-integration-campaign-v1",
    evidence_state: "VALID",
    normalized_operations: 18,
    reads: 13,
    actions: 5,
    complete_operations: 0,
    incomplete_operations: 18,
    claim_boundary: "Transport telemetry is not semantic integration proof.",
    operations: [
      {
        operation: "get_asset",
        operation_id: "getAsset",
        kind: "read",
        method: "GET",
        path_template: "/assets/{assetId}",
        complete: false,
        dimensions: [
          { name: "canonical_route_observed", state: "PASS", evidence_source: "hosted_transport_ledger" },
          { name: "valid_request_success", state: "PASS", evidence_source: "hosted_transport_ledger" },
          { name: "http_error_behavior_observed", state: "UNPROVEN", evidence_source: "not_observed" },
          { name: "invalid_parameters_rejected", state: "UNPROVEN", evidence_source: "campaign_proof_required" },
          { name: "response_normalization_verified", state: "UNPROVEN", evidence_source: "campaign_proof_required" },
          { name: "agent_evaluator_behavior_verified", state: "UNPROVEN", evidence_source: "campaign_proof_required" },
        ],
      },
    ],
  };
}

describe("ToolCampaignPanel", () => {
  it("shows transport observations without upgrading them to a completed integration claim", () => {
    const html = renderToStaticMarkup(<ToolCampaignPanel campaign={campaign()} />);

    expect(html).toContain("0/18 complete");
    expect(html).toContain("INCOMPLETE");
    expect(html).toContain("2/6");
    expect(html).toContain("response normalization verified");
    expect(html).toContain("agent evaluator behavior verified");
    expect(html).toContain("Transport telemetry is not semantic integration proof.");
  });

  it("renders an actually complete operation only when every dimension is passed", () => {
    const base = campaign();
    const completeOperation = {
      ...base.operations[0],
      complete: true,
      dimensions: base.operations[0].dimensions.map((dimension) => ({
        ...dimension,
        state: "PASS" as const,
        evidence_source: "bounded_campaign_evidence",
      })),
    };
    const html = renderToStaticMarkup(
      <ToolCampaignPanel
        campaign={{
          ...base,
          complete_operations: 1,
          incomplete_operations: 17,
          operations: [completeOperation],
        }}
      />,
    );

    expect(html).toContain("1/18 complete");
    expect(html).toContain("COMPLETE");
    expect(html).toContain("6/6");
  });
});
