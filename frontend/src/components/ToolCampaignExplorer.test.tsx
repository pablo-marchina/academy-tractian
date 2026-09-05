import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ToolCampaignResponse } from "../api/toolCoverageTypes";
import { ToolCampaignPanel } from "./ToolCampaignExplorer";


function campaign(): ToolCampaignResponse {
  return {
    schema_version: "tractian-integration-campaign-v3",
    transport_evidence_state: "VALID",
    semantic_evidence_state: "VALID",
    transport_completion_status: "TRANSPORT_PARTIAL_0_OF_18",
    semantic_completion_status: "SEMANTIC_NOT_STARTED_0_OF_18",
    normalized_operations: 18,
    reads: 13,
    actions: 5,
    transport_complete_operations: 0,
    transport_incomplete_operations: 18,
    semantic_complete_operations: 0,
    semantic_incomplete_operations: 18,
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
        transport_complete: false,
        semantic_complete: false,
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
  it("shows transport observations without upgrading them to semantic or end-to-end completion", () => {
    const html = renderToStaticMarkup(<ToolCampaignPanel campaign={campaign()} />);

    expect(html).toContain("0/18 complete");
    expect(html).toContain("Transport gate");
    expect(html).toContain("Semantic gate");
    expect(html).toContain("End-to-end complete");
    expect(html).toContain("TRANSPORT_PARTIAL_0_OF_18");
    expect(html).toContain("SEMANTIC_NOT_STARTED_0_OF_18");
    expect(html).toContain("INCOMPLETE");
    expect(html).toContain("2/6");
    expect(html).toContain("response normalization verified [UNPROVEN]");
    expect(html).toContain("agent evaluator behavior verified [UNPROVEN]");
    expect(html).toContain("Transport evidence");
    expect(html).toContain("Semantic evidence");
    expect(html).toContain("Transport telemetry is not semantic integration proof.");
  });

  it("renders an actually complete operation only when transport and semantic gates pass", () => {
    const base = campaign();
    const completeOperation = {
      ...base.operations[0],
      transport_complete: true,
      semantic_complete: true,
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
          transport_complete_operations: 1,
          transport_incomplete_operations: 17,
          semantic_complete_operations: 1,
          semantic_incomplete_operations: 17,
          complete_operations: 1,
          incomplete_operations: 17,
          transport_completion_status: "TRANSPORT_PARTIAL_1_OF_18",
          semantic_completion_status: "SEMANTIC_PARTIAL_1_OF_18",
          operations: [completeOperation],
        }}
      />,
    );

    expect(html).toContain("1/18 complete");
    expect(html).toContain("COMPLETE");
    expect(html).toContain("6/6");
  });

  it("keeps semantic-only proof separate from missing transport proof", () => {
    const base = campaign();
    const semanticOnly = {
      ...base.operations[0],
      semantic_complete: true,
      transport_complete: false,
      complete: false,
      dimensions: base.operations[0].dimensions.map((dimension) =>
        [
          "invalid_parameters_rejected",
          "response_normalization_verified",
          "agent_evaluator_behavior_verified",
        ].includes(dimension.name)
          ? { ...dimension, state: "PASS" as const, evidence_source: "campaign:test" }
          : dimension,
      ),
    };
    const html = renderToStaticMarkup(
      <ToolCampaignPanel
        campaign={{
          ...base,
          semantic_complete_operations: 1,
          semantic_incomplete_operations: 17,
          semantic_completion_status: "SEMANTIC_PARTIAL_1_OF_18",
          operations: [semanticOnly],
        }}
      />,
    );

    expect(html).toContain("OPEN");
    expect(html).toContain("PASS");
    expect(html).toContain("0/18 complete");
  });

  it("shows semantic proof failures as failures rather than missing evidence", () => {
    const base = campaign();
    const failedOperation = {
      ...base.operations[0],
      dimensions: base.operations[0].dimensions.map((dimension) =>
        dimension.name === "response_normalization_verified"
          ? { ...dimension, state: "FAIL" as const, evidence_source: "campaign:test" }
          : dimension,
      ),
    };
    const html = renderToStaticMarkup(
      <ToolCampaignPanel campaign={{ ...base, operations: [failedOperation] }} />,
    );

    expect(html).toContain("response normalization verified [FAIL]");
  });
});
