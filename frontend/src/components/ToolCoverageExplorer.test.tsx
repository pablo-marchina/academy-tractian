import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ToolCoverageResponse } from "../api/toolCoverageTypes";
import { ToolCoveragePanel } from "./ToolCoverageExplorer";


function coverage(overrides?: Partial<ToolCoverageResponse>): ToolCoverageResponse {
  return {
    schema_version: "tractian-tool-coverage-v2",
    status: "PARTIAL_INTEGRATED_ROUTE_EVIDENCE",
    claim_boundary: "Hosted-live coverage increases only from validated evidence.",
    evidence: {
      frozen: {
        state: "VALID",
        source: "package:research.e2/frozen_tool_integration_evidence.json",
        validation_errors: [],
      },
      hosted_live: {
        state: "VALID",
        source: "hosted_live:postgres",
        validation_errors: [],
      },
    },
    summary: {
      normalized_operations: 18,
      contract_registered: 18,
      implementation_routes_present: 18,
      integrated_route_execution_evidenced: 1,
      integrated_route_execution_not_yet_evidenced: 17,
      frozen_route_execution_evidenced: 1,
      hosted_live_exercised: 0,
      hosted_live_success: 0,
      hosted_live_http_error_observed: 0,
      hosted_live_transport_failure: 0,
      hosted_live_unavailable: 0,
      hosted_live_blocked_by_safety: 0,
      hosted_live_not_exercised: 18,
      actions: 5,
      reads: 13,
    },
    operations: [
      {
        tool_name: "get_asset",
        operation_id: "get_asset",
        method: "GET",
        path_template: "/assets/{assetId}",
        kind: "read",
        impact: null,
        required_permissions: [],
        parameter_count: 1,
        required_parameter_count: 1,
        identity_required: false,
        justification_required: false,
        seed_supported: true,
        contract_registered: true,
        implementation_route_present: true,
        integrated_route_execution_evidenced: true,
        integration_evidence_scope: "frozen_route_test_evidence",
        frozen_route_execution_evidenced: true,
        hosted_live_exercised: false,
        hosted_live_success: false,
        hosted_live_blocked_by_safety: false,
        hosted_live_outcomes: [],
      },
    ],
    ...overrides,
  };
}

describe("ToolCoveragePanel", () => {
  it("shows contract completeness without misrepresenting hosted execution", () => {
    const html = renderToStaticMarkup(<ToolCoveragePanel coverage={coverage()} />);

    expect(html).toContain("Contract");
    expect(html).toContain("18/18");
    expect(html).toContain("Hosted exercised");
    expect(html).toContain("0/18");
    expect(html).toContain("FROZEN ONLY");
    expect(html).toContain("Hosted-live coverage increases only from validated evidence.");
  });

  it("distinguishes a hosted HTTP observation from hosted success", () => {
    const base = coverage();
    const html = renderToStaticMarkup(
      <ToolCoveragePanel
        coverage={{
          ...base,
          status: "PARTIAL_HOSTED_LIVE_EVIDENCE",
          summary: {
            ...base.summary,
            integrated_route_execution_evidenced: 2,
            integrated_route_execution_not_yet_evidenced: 16,
            hosted_live_exercised: 1,
            hosted_live_success: 0,
            hosted_live_http_error_observed: 1,
            hosted_live_not_exercised: 17,
          },
          operations: [
            {
              ...base.operations[0],
              tool_name: "get_company",
              operation_id: "get_company",
              path_template: "/companies/{companyId}",
              frozen_route_execution_evidenced: false,
              hosted_live_exercised: true,
              hosted_live_outcomes: ["http_error_observed"],
            },
          ],
        }}
      />,
    );

    expect(html).toContain("HOSTED OBSERVED");
    expect(html).toContain("http_error_observed");
    expect(html).toContain("Hosted success");
    expect(html).toContain("0/18");
  });

  it("makes invalid evidence visibly fail closed", () => {
    const base = coverage();
    const html = renderToStaticMarkup(
      <ToolCoveragePanel
        coverage={{
          ...base,
          status: "EVIDENCE_INVALID_FAIL_CLOSED",
          evidence: {
            ...base.evidence,
            hosted_live: {
              state: "INVALID",
              source: "hosted_live:postgres",
              validation_errors: ["contract:route_mismatch"],
            },
          },
        }}
      />,
    );

    expect(html).toContain("EVIDENCE INVALID FAIL CLOSED");
    expect(html).toContain("INVALID · hosted_live:postgres");
    expect(html).toContain("contract:route_mismatch");
  });
});
