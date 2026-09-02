import { describe, expect, it } from "vitest";

import type { DynamicAnalyticsResult, ToolsMetrics } from "../api/types";
import { dynamicOption, toolsOption } from "./analyticsOptions";


describe("operational chart adapters", () => {
  it("maps tool API counts directly into chart series", () => {
    const metrics: ToolsMetrics = {
      schema_version: "tools-metrics-v2",
      scope: { run_id: "run_safe_scope" },
      count: 2,
      items: [
        { tool_name: "get_asset", proposals: 3, calls: 2, results: 2, observations: 2, status_codes: { "200": 2 } },
        { tool_name: "list_analyses", proposals: 1, calls: 1, results: 1, observations: 1, status_codes: { "200": 1 } },
      ],
    };
    const option = toolsOption(metrics) as any;
    expect(option.xAxis.data).toEqual(["get_asset", "list_analyses"]);
    expect(option.series[0].data).toEqual([3, 1]);
    expect(option.series[1].data).toEqual([2, 1]);
    expect(option.series[2].data).toEqual([2, 1]);
    expect(option.series[3].data).toEqual([2, 1]);
  });

  it("maps one-dimensional scoped rows without manufacturing points", () => {
    const result: DynamicAnalyticsResult = {
      schema_version: "dynamic-analytics-result-v2",
      dataset: "events",
      run_id: "run_safe_scope",
      dimensions: ["event_type"],
      measure: "count",
      chart_type: "bar",
      source_row_count: 7,
      rows: [
        { event_type: "model_call", value: 4 },
        { event_type: "tool_call", value: 3 },
      ],
      truncated: false,
    };
    const option = dynamicOption(result) as any;
    expect(option.xAxis.data).toEqual(["model_call", "tool_call"]);
    expect(option.series[0].data).toEqual([4, 3]);
    expect(option.series[0].data).toHaveLength(result.rows.length);
  });

  it("uses exactly backend heatmap cells and values", () => {
    const result: DynamicAnalyticsResult = {
      schema_version: "dynamic-analytics-result-v2",
      dataset: "events",
      run_id: null,
      dimensions: ["event_type", "origin"],
      measure: "count",
      chart_type: "heatmap",
      source_row_count: 5,
      rows: [
        { event_type: "model_call", origin: "MODEL", value: 2 },
        { event_type: "tool_call", origin: "TOOL", value: 3 },
      ],
      truncated: false,
    };
    const option = dynamicOption(result) as any;
    expect(option.series[0].data).toHaveLength(2);
    expect(option.series[0].data.map((cell: number[]) => cell[2])).toEqual([2, 3]);
  });

  it("does not create an ECharts option for table results", () => {
    const result: DynamicAnalyticsResult = {
      schema_version: "dynamic-analytics-result-v2",
      dataset: "runs",
      run_id: null,
      dimensions: [],
      measure: "count",
      chart_type: "table",
      source_row_count: 1,
      rows: [{ value: 1 }],
      truncated: false,
    };
    expect(dynamicOption(result)).toBeNull();
  });
});
