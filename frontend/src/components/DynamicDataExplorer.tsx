import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { executeAnalyticsQuery, fetchDynamicAnalyticsSchema } from "../api/client";
import type { AnalyticsFilter, AnalyticsQuerySpec, ChartType } from "../api/types";
import { dynamicOption } from "../state/analyticsOptions";
import { buildDrilldownQuery, type AnalyticsDrilldown } from "../state/analyticsScope";
import { EChart, type EChartDataPoint } from "./EChart";

export type { AnalyticsDrilldown } from "../state/analyticsScope";

function parseFilterValue(operator: AnalyticsFilter["operator"], raw: string): AnalyticsFilter["value"] {
  const trimmed = raw.trim();
  if (operator === "in") {
    const values = raw.split(",").map((item) => item.trim()).filter(Boolean);
    if (values.every((value) => value === "true" || value === "false")) return values.map((value) => value === "true");
    if (values.every((value) => value !== "" && Number.isFinite(Number(value)))) return values.map(Number);
    return values;
  }
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (trimmed !== "" && Number.isFinite(Number(trimmed))) return Number(trimmed);
  return trimmed;
}

function scalarToInput(value: string | number | boolean): string {
  return typeof value === "string" ? value : String(value);
}

function humanize(value: string): string {
  const words = value.replaceAll("_", " ").replaceAll("ms", "milliseconds");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function chartLabel(value: ChartType): string {
  const labels: Record<ChartType, string> = {
    table: "Table",
    bar: "Bar chart",
    line: "Line chart",
    heatmap: "Heat map",
    histogram: "Distribution",
  };
  return labels[value];
}

function TableResult({ rows, caption = "Analytics result table" }: { rows: Record<string, string | number | boolean | null>[]; caption?: string }) {
  const columns = rows[0] ? Object.keys(rows[0]) : [];
  if (!rows.length) return <div className="empty-state small"><strong>No matching data</strong><p>Try a broader scope or remove the optional filter.</p></div>;
  return (
    <div className="analytics-table-wrap">
      <table className="analytics-table">
        <caption className="visually-hidden">{caption}</caption>
        <thead><tr>{columns.map((column) => <th scope="col" key={column}>{humanize(column)}</th>)}</tr></thead>
        <tbody>{rows.map((row, index) => <tr key={index}>{columns.map((column) => <td key={column}>{String(row[column] ?? "—")}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}

export function DynamicDataExplorer({
  globalRunId,
  drilldown,
}: {
  globalRunId: string | null;
  drilldown: AnalyticsDrilldown | null;
}) {
  const schemaQuery = useQuery({ queryKey: ["dynamic-schema"], queryFn: fetchDynamicAnalyticsSchema, staleTime: 60_000 });
  const [dataset, setDataset] = useState<AnalyticsQuerySpec["dataset"]>("events");
  const [dimensionA, setDimensionA] = useState("event_type");
  const [dimensionB, setDimensionB] = useState("");
  const [measure, setMeasure] = useState("count");
  const [chartType, setChartType] = useState<ChartType>("bar");
  const [filterField, setFilterField] = useState("");
  const [filterOperator, setFilterOperator] = useState<AnalyticsFilter["operator"]>("eq");
  const [filterValue, setFilterValue] = useState("");

  const datasetSchema = schemaQuery.data?.datasets[dataset];
  const dimensions = useMemo(() => [dimensionA, dimensionB].filter(Boolean), [dimensionA, dimensionB]);
  const validCharts = useMemo<ChartType[]>(() => {
    if (measure === "latency_ms_distribution") return ["histogram"];
    if (dimensions.length === 0) return ["table"];
    if (dimensions.length === 1) return ["table", "bar", "line"];
    return ["table", "heatmap"];
  }, [dimensions.length, measure]);

  const queryMutation = useMutation({ mutationFn: executeAnalyticsQuery });
  const mutateQuery = queryMutation.mutate;

  const resetForDataset = (next: AnalyticsQuerySpec["dataset"]) => {
    setDataset(next);
    setDimensionA("");
    setDimensionB("");
    setMeasure("count");
    setChartType("table");
    setFilterField("");
    setFilterOperator("eq");
    setFilterValue("");
  };

  useEffect(() => {
    if (!drilldown) return;
    const nextChart = drilldown.chartType ?? "bar";
    setDataset(drilldown.dataset);
    setDimensionA(drilldown.dimension);
    setDimensionB("");
    setMeasure("count");
    setChartType(nextChart);
    setFilterField(drilldown.filterField);
    setFilterOperator("eq");
    setFilterValue(scalarToInput(drilldown.filterValue));
    mutateQuery(buildDrilldownQuery(drilldown, globalRunId));
  }, [drilldown, globalRunId, mutateQuery]);

  const runQuery = () => {
    const chosenChart = validCharts.includes(chartType) ? chartType : validCharts[0];
    const filters: AnalyticsFilter[] = filterField && filterValue.trim()
      ? [{ field: filterField, operator: filterOperator, value: parseFilterValue(filterOperator, filterValue) }]
      : [];
    queryMutation.mutate({ dataset, run_id: globalRunId, dimensions, measure, chart_type: chosenChart, filters, limit: 200 });
    setChartType(chosenChart);
  };

  const clearFilter = () => {
    setFilterField("");
    setFilterOperator("eq");
    setFilterValue("");
  };

  const result = queryMutation.data?.run_id === globalRunId ? queryMutation.data : undefined;
  const option = result ? dynamicOption(result) : null;

  const drillIntoResult = (point: EChartDataPoint) => {
    if (!result || result.dimensions.length !== 1 || !point.name) return;
    const dimension = result.dimensions[0];
    const raw = point.name;
    const value = parseFilterValue("eq", raw);
    if (Array.isArray(value)) return;
    setFilterField(dimension);
    setFilterOperator("eq");
    setFilterValue(raw);
    queryMutation.mutate({
      dataset: result.dataset as AnalyticsQuerySpec["dataset"],
      run_id: globalRunId,
      dimensions: result.dimensions,
      measure: result.measure,
      chart_type: result.chart_type,
      filters: [{ field: dimension, operator: "eq", value }],
      limit: 200,
    });
  };

  return (
    <article className="panel operations-panel" id="dynamic-data-explorer" aria-busy={queryMutation.isPending}>
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">SAFE ANALYTICS</p>
          <h2>Dynamic Data Explorer</h2>
          <p className="section-supporting-copy">Build a bounded view of persisted product data without writing SQL. Start with what you want to compare, then add a filter only if it helps answer the question.</p>
        </div>
        {schemaQuery.data && <span className="count-pill">schema {schemaQuery.data.schema_version}</span>}
      </div>

      <div className="analytics-scope-banner">
        <strong>{globalRunId ? "Selected analysis only" : "All saved analyses"}</strong>
        <span className={globalRunId ? "technical-id" : undefined} title={globalRunId ?? undefined}>{globalRunId ?? "global scope"}</span>
      </div>

      {schemaQuery.isLoading && (
        <div className="empty-state small" role="status"><strong>Loading available analytics…</strong><p>The query form appears only after the backend publishes the allowed fields.</p></div>
      )}

      {schemaQuery.error && (
        <div className="error-banner friendly-error" role="alert"><strong>Analytics options could not be loaded.</strong><span>No query will be sent until the safe schema is available.</span></div>
      )}

      {!schemaQuery.isLoading && !datasetSchema ? (
        <div className="empty-state small"><strong>Analytics schema unavailable</strong><p>No query is generated until the backend publishes its allow-list.</p></div>
      ) : datasetSchema ? (
        <>
          <div className="analytics-builder-intro">
            <strong>1. Choose what to summarize</strong>
            <span>Each option is constrained by the server-owned analytics schema.</span>
          </div>
          <div className="query-grid">
            <label>Dataset
              <small>Which saved data should be summarized?</small>
              <select value={dataset} onChange={(event) => resetForDataset(event.target.value as AnalyticsQuerySpec["dataset"])}>
                {Object.keys(schemaQuery.data!.datasets).map((item) => <option key={item} value={item}>{humanize(item)}</option>)}
              </select>
            </label>
            <label>Dimension 1
              <small>Main grouping for the result.</small>
              <select value={dimensionA} onChange={(event) => setDimensionA(event.target.value)}><option value="">No grouping</option>{datasetSchema.dimensions.map((item) => <option key={item} value={item}>{humanize(item)}</option>)}</select>
            </label>
            <label>Dimension 2
              <small>Optional second grouping for comparisons.</small>
              <select value={dimensionB} disabled={!dimensionA} onChange={(event) => setDimensionB(event.target.value)}><option value="">No second grouping</option>{datasetSchema.dimensions.filter((item) => item !== dimensionA).map((item) => <option key={item} value={item}>{humanize(item)}</option>)}</select>
            </label>
            <label>Measure
              <small>What value should be counted or measured?</small>
              <select value={measure} onChange={(event) => { setMeasure(event.target.value); setChartType(event.target.value === "latency_ms_distribution" ? "histogram" : "table"); }}>{datasetSchema.measures.map((item) => <option key={item} value={item}>{humanize(item)}</option>)}</select>
            </label>
            <label>Chart
              <small>How should the result be displayed?</small>
              <select value={validCharts.includes(chartType) ? chartType : validCharts[0]} onChange={(event) => setChartType(event.target.value as ChartType)}>{validCharts.map((item) => <option key={item} value={item}>{chartLabel(item)}</option>)}</select>
            </label>
          </div>

          <details className="technical-disclosure analytics-filter-disclosure" open={filterField ? true : undefined}>
            <summary>2. Optional filter</summary>
            <div className="filter-row">
              <label>Filter field<select value={filterField} onChange={(event) => setFilterField(event.target.value)}><option value="">No local filter</option>{datasetSchema.dimensions.map((item) => <option key={item} value={item}>{humanize(item)}</option>)}</select></label>
              <label>Operator<select value={filterOperator} disabled={!filterField} onChange={(event) => setFilterOperator(event.target.value as AnalyticsFilter["operator"])}><option value="eq">Equals</option><option value="ne">Does not equal</option><option value="in">Matches one of</option></select></label>
              <label>Value<input value={filterValue} disabled={!filterField} onChange={(event) => setFilterValue(event.target.value)} placeholder={filterOperator === "in" ? "value 1, value 2" : "filter value"} /></label>
              {filterField && <button type="button" className="ghost-button" onClick={clearFilter}>Clear filter</button>}
            </div>
          </details>

          <div className="analytics-run-row">
            <div><strong>3. Generate the view</strong><span>The backend enforces allowed fields, operators and a 200-row result limit.</span></div>
            <button type="button" onClick={runQuery} disabled={queryMutation.isPending}>{queryMutation.isPending ? "Generating view…" : "Generate analytics view"}</button>
          </div>

          {queryMutation.error && (
            <div className="error-banner friendly-error" role="alert"><strong>The analytics view could not be generated.</strong><span>Check the selected fields or remove the optional filter and try again.</span><details><summary>Technical detail</summary><code>{queryMutation.error.message}</code></details></div>
          )}

          {result && (
            <section className="analytics-result-section" aria-live="polite">
              <div className="query-result-meta">
                <span>{result.run_id ? "selected analysis" : "all analyses"}</span>
                <span>{result.source_row_count} source rows checked</span>
                <span>{result.rows.length} result rows</span>
                {result.truncated && <span>showing first 200 rows</span>}
              </div>
              {result.chart_type === "table" && <TableResult rows={result.rows} />}
              {option && result.chart_type !== "table" && (
                <>
                  <EChart
                    option={option}
                    height={330}
                    onDataPointClick={drillIntoResult}
                    ariaLabel={`${chartLabel(result.chart_type as ChartType)} of ${humanize(result.measure)} grouped by ${result.dimensions.map(humanize).join(" and ") || "the selected scope"}`}
                    description="The same result rows are available as a table below. Selecting a chart point applies a safe drill-down filter when one grouping dimension is present."
                  />
                  <details className="technical-disclosure analytics-table-alternative">
                    <summary>View the chart data as a table</summary>
                    <TableResult rows={result.rows} caption="Table alternative for the analytics chart" />
                  </details>
                </>
              )}
            </section>
          )}
        </>
      ) : null}
    </article>
  );
}
