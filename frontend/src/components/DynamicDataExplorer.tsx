import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { executeAnalyticsQuery, fetchDynamicAnalyticsSchema } from "../api/client";
import type { AnalyticsFilter, AnalyticsQuerySpec, ChartType } from "../api/types";
import { dynamicOption } from "../state/analyticsOptions";
import { EChart } from "./EChart";

function parseFilterValue(operator: AnalyticsFilter["operator"], raw: string): AnalyticsFilter["value"] {
  const trimmed = raw.trim();
  if (operator === "in") {
    const values = raw.split(",").map((item) => item.trim());
    if (values.every((value) => value === "true" || value === "false")) {
      return values.map((value) => value === "true");
    }
    if (values.every((value) => value !== "" && Number.isFinite(Number(value)))) {
      return values.map(Number);
    }
    return values;
  }
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (trimmed !== "" && Number.isFinite(Number(trimmed))) return Number(trimmed);
  return trimmed;
}

function TableResult({ rows }: { rows: Record<string, string | number | boolean | null>[] }) {
  const columns = rows[0] ? Object.keys(rows[0]) : [];
  if (!rows.length) return <div className="empty-state small"><strong>No matching rows</strong><p>The backend returned an empty safe result for this query.</p></div>;
  return (
    <div className="analytics-table-wrap">
      <table className="analytics-table">
        <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
        <tbody>{rows.map((row, index) => <tr key={index}>{columns.map((column) => <td key={column}>{String(row[column] ?? "—")}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}

export function DynamicDataExplorer() {
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

  const resetForDataset = (next: AnalyticsQuerySpec["dataset"]) => {
    setDataset(next);
    setDimensionA("");
    setDimensionB("");
    setMeasure("count");
    setChartType("table");
    setFilterField("");
    setFilterValue("");
  };

  const runQuery = () => {
    const chosenChart = validCharts.includes(chartType) ? chartType : validCharts[0];
    const filters: AnalyticsFilter[] = filterField && filterValue.trim()
      ? [{ field: filterField, operator: filterOperator, value: parseFilterValue(filterOperator, filterValue) }]
      : [];
    queryMutation.mutate({ dataset, dimensions, measure, chart_type: chosenChart, filters, limit: 200 });
    setChartType(chosenChart);
  };

  const result = queryMutation.data;
  const option = result ? dynamicOption(result) : null;

  return (
    <article className="panel operations-panel">
      <div className="section-heading compact">
        <div><p className="eyebrow">ALLOW-LISTED ANALYTICS</p><h2>Dynamic Data Explorer</h2></div>
        {schemaQuery.data && <span className="count-pill">schema {schemaQuery.data.schema_version}</span>}
      </div>
      <p className="panel-copy">The browser sends a constrained query specification, never SQL. Invalid dimensions, measures and chart shapes are rejected by the backend.</p>

      {!datasetSchema ? <div className="empty-state small"><strong>Analytics schema unavailable</strong><p>No query is generated until the backend publishes its allow-list.</p></div> : (
        <>
          <div className="query-grid">
            <label>Dataset<select value={dataset} onChange={(event) => resetForDataset(event.target.value as AnalyticsQuerySpec["dataset"])}>{Object.keys(schemaQuery.data!.datasets).map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>Dimension 1<select value={dimensionA} onChange={(event) => setDimensionA(event.target.value)}><option value="">none</option>{datasetSchema.dimensions.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>Dimension 2<select value={dimensionB} disabled={!dimensionA} onChange={(event) => setDimensionB(event.target.value)}><option value="">none</option>{datasetSchema.dimensions.filter((item) => item !== dimensionA).map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>Measure<select value={measure} onChange={(event) => { setMeasure(event.target.value); setChartType(event.target.value === "latency_ms_distribution" ? "histogram" : "table"); }}>{datasetSchema.measures.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>Chart<select value={validCharts.includes(chartType) ? chartType : validCharts[0]} onChange={(event) => setChartType(event.target.value as ChartType)}>{validCharts.map((item) => <option key={item}>{item}</option>)}</select></label>
          </div>

          <div className="filter-row">
            <label>Filter field<select value={filterField} onChange={(event) => setFilterField(event.target.value)}><option value="">no filter</option>{datasetSchema.dimensions.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>Operator<select value={filterOperator} disabled={!filterField} onChange={(event) => setFilterOperator(event.target.value as AnalyticsFilter["operator"])}><option value="eq">equals</option><option value="ne">not equal</option><option value="in">in (comma separated)</option></select></label>
            <label>Value<input value={filterValue} disabled={!filterField} onChange={(event) => setFilterValue(event.target.value)} placeholder="safe scalar value" /></label>
            <button type="button" onClick={runQuery} disabled={queryMutation.isPending}>Run bounded query</button>
          </div>

          {queryMutation.error && <div className="error-banner">{queryMutation.error.message}</div>}
          {result && <div className="query-result-meta"><span>{result.source_row_count} source rows</span><span>{result.rows.length} result rows</span>{result.truncated && <span>truncated</span>}</div>}
          {result && result.chart_type === "table" && <TableResult rows={result.rows} />}
          {result && option && <EChart option={option} height={330} />}
        </>
      )}
    </article>
  );
}
