import type { AnalyticsQuerySpec, ChartType } from "../api/types";

export interface AnalyticsDrilldown {
  key: number;
  dataset: AnalyticsQuerySpec["dataset"];
  dimension: string;
  filterField: string;
  filterValue: string | number | boolean;
  chartType?: ChartType;
}

export function buildDrilldownQuery(
  drilldown: AnalyticsDrilldown,
  globalRunId: string | null,
): AnalyticsQuerySpec {
  return {
    dataset: drilldown.dataset,
    run_id: globalRunId,
    dimensions: [drilldown.dimension],
    measure: "count",
    chart_type: drilldown.chartType ?? "bar",
    filters: [
      {
        field: drilldown.filterField,
        operator: "eq",
        value: drilldown.filterValue,
      },
    ],
    limit: 200,
  };
}
