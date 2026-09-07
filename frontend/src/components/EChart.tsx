import * as echarts from "echarts";
import type { EChartsOption } from "echarts";
import { useEffect, useId, useRef } from "react";

export interface EChartDataPoint {
  name: string;
  seriesName: string;
  value: unknown;
}

export function EChart({
  option,
  height = 280,
  onDataPointClick,
  ariaLabel = "Operational analytics chart",
  description,
}: {
  option: EChartsOption;
  height?: number;
  onDataPointClick?: (point: EChartDataPoint) => void;
  ariaLabel?: string;
  description?: string;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const descriptionId = useId();

  useEffect(() => {
    const element = containerRef.current;
    if (!element) return;
    const chart = echarts.init(element);
    chart.setOption({ ...option, aria: { enabled: true } }, { notMerge: true });
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

  return (
    <figure className="accessible-chart">
      <div
        ref={containerRef}
        style={{ width: "100%", height }}
        role="img"
        aria-label={ariaLabel}
        aria-describedby={description ? descriptionId : undefined}
      />
      {description && <figcaption id={descriptionId}>{description}</figcaption>}
    </figure>
  );
}
