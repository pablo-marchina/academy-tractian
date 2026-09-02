import { describe, expect, it } from "vitest";

import { buildDrilldownQuery, type AnalyticsDrilldown } from "./analyticsScope";


describe("analytics global scope", () => {
  it("carries selected safe run plus local drilldown filter into one bounded query", () => {
    const drilldown: AnalyticsDrilldown = {
      key: 7,
      dataset: "events",
      dimension: "event_type",
      filterField: "tool_name",
      filterValue: "get_asset",
      chartType: "bar",
    };
    expect(buildDrilldownQuery(drilldown, "run_scope_a")).toEqual({
      dataset: "events",
      run_id: "run_scope_a",
      dimensions: ["event_type"],
      measure: "count",
      chart_type: "bar",
      filters: [{ field: "tool_name", operator: "eq", value: "get_asset" }],
      limit: 200,
    });
  });

  it("keeps global scope explicitly null instead of inventing a run", () => {
    const drilldown: AnalyticsDrilldown = {
      key: 8,
      dataset: "evaluations",
      dimension: "passed",
      filterField: "check_name",
      filterValue: "trace_integrity",
    };
    const query = buildDrilldownQuery(drilldown, null);
    expect(query.run_id).toBeNull();
    expect(query.filters).toEqual([
      { field: "check_name", operator: "eq", value: "trace_integrity" },
    ]);
  });
});
