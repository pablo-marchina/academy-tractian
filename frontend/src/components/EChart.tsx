import * as echarts from "echarts";
import type { EChartsOption } from "echarts";
import { useEffect, useRef } from "react";

export interface EChartDataPoint {
  name: string;
  seriesName: string;
  value: unknown;
}

export function EChart({
  option,
  height = 280,
  onDataPointClick,
}: {
  option: EChartsOption;
  height?: number;
  onDataPointClick?: (point: EChartDataPoint) => void;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const element = containerRef.current;
    if (!element) return;
    const chart = echarts.init(element);
    chart.setOption(option, { notMerge: true });
    if (onDataPointClick) {
      chart.on("click", (params) => {
        onDataPointClick({
          name: String(params.name ?? ""),
          seriesName: String(params.seriesName ?? ""),
          value: params.value,
        });
      });
    }
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(element);
    return () => {
      observer.disconnect();
      chart.dispose();
    };
  }, [option, onDataPointClick]);

  return <div ref={containerRef} style={{ width: "100%", height }} aria-label="Operational analytics chart" />;
}
