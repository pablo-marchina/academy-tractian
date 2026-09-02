import type { EChartsOption } from "echarts";

import type {
  DynamicAnalyticsResult,
  EvaluationMetrics,
  PoliciesMetrics,
  ProviderExperimentSummary,
  ToolsMetrics,
} from "../api/types";

const base = (): EChartsOption => ({
  animation: false,
  textStyle: { fontFamily: "Inter, ui-sans-serif, system-ui" },
  tooltip: { trigger: "axis" },
  grid: { left: 42, right: 18, top: 28, bottom: 44, containLabel: true },
});

export function toolsOption(metrics: ToolsMetrics): EChartsOption {
  return {
    ...base(),
    legend: { data: ["proposals", "calls", "results", "observations"] },
    xAxis: { type: "category", data: metrics.items.map((item) => item.tool_name) },
    yAxis: { type: "value", minInterval: 1 },
    series: [
      { name: "proposals", type: "bar", data: metrics.items.map((item) => item.proposals) },
      { name: "calls", type: "bar", data: metrics.items.map((item) => item.calls) },
      { name: "results", type: "bar", data: metrics.items.map((item) => item.results) },
      { name: "observations", type: "bar", data: metrics.items.map((item) => item.observations) },
    ],
  };
}

export function policiesOption(metrics: PoliciesMetrics): EChartsOption {
  return {
    ...base(),
    legend: { data: ["allowed", "blocked", "contained"] },
    xAxis: { type: "category", data: metrics.items.map((item) => item.policy_stage) },
    yAxis: { type: "value", minInterval: 1 },
    series: [
      { name: "allowed", type: "bar", stack: "checks", data: metrics.items.map((item) => item.allowed) },
      { name: "blocked", type: "bar", stack: "checks", data: metrics.items.map((item) => item.blocked) },
      { name: "contained", type: "bar", data: metrics.items.map((item) => item.contained) },
    ],
  };
}

export function evaluationOption(metrics: EvaluationMetrics): EChartsOption {
  return {
    ...base(),
    tooltip: { trigger: "axis", valueFormatter: (value) => `${Number(value).toFixed(1)}%` },
    xAxis: { type: "value", min: 0, max: 100 },
    yAxis: { type: "category", data: metrics.checks.map((item) => item.check_name) },
    series: [
      {
        name: "pass rate",
        type: "bar",
        data: metrics.checks.map((item) => Number((item.pass_rate * 100).toFixed(2))),
      },
    ],
  };
}

export function providerOption(experiment: ProviderExperimentSummary): EChartsOption {
  return {
    ...base(),
    legend: { data: ["structured adherence", "public quality", "success", "stability"] },
    xAxis: { type: "category", data: experiment.candidates.map((item) => item.candidate_id) },
    yAxis: { type: "value", min: 0, max: 1 },
    series: [
      { name: "structured adherence", type: "bar", data: experiment.candidates.map((item) => item.structured_decision_adherence) },
      { name: "public quality", type: "bar", data: experiment.candidates.map((item) => item.public_task_quality) },
      { name: "success", type: "bar", data: experiment.candidates.map((item) => item.success_rate) },
      { name: "stability", type: "bar", data: experiment.candidates.map((item) => item.signature_stability) },
    ],
  };
}

export function dynamicOption(result: DynamicAnalyticsResult): EChartsOption | null {
  if (result.chart_type === "table") return null;

  if (result.chart_type === "histogram") {
    return {
      ...base(),
      xAxis: {
        type: "category",
        data: result.rows.map((row) => `${Number(row.bin_start).toFixed(0)}–${Number(row.bin_end).toFixed(0)}`),
        name: "latency ms",
      },
      yAxis: { type: "value", minInterval: 1 },
      series: [{ type: "bar", name: "events", data: result.rows.map((row) => Number(row.value)) }],
    };
  }

  if (result.chart_type === "heatmap") {
    const [xDimension, yDimension] = result.dimensions;
    const xValues = Array.from(new Set(result.rows.map((row) => String(row[xDimension]))));
    const yValues = Array.from(new Set(result.rows.map((row) => String(row[yDimension]))));
    return {
      ...base(),
      tooltip: { position: "top" },
      xAxis: { type: "category", data: xValues, splitArea: { show: true } },
      yAxis: { type: "category", data: yValues, splitArea: { show: true } },
      visualMap: { min: 0, max: Math.max(1, ...result.rows.map((row) => Number(row.value) || 0)), calculable: true, orient: "horizontal", left: "center", bottom: 0 },
      series: [{
        type: "heatmap",
        data: result.rows.map((row) => [xValues.indexOf(String(row[xDimension])), yValues.indexOf(String(row[yDimension])), Number(row.value)]),
      }],
    };
  }

  const dimension = result.dimensions[0];
  return {
    ...base(),
    xAxis: { type: "category", data: result.rows.map((row) => String(row[dimension])) },
    yAxis: { type: "value" },
    series: [{ type: result.chart_type, name: result.measure, data: result.rows.map((row) => Number(row.value)) }],
  };
}
