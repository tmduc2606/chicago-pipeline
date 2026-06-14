import ReactECharts from "echarts-for-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { HelpTooltip } from "@/components/ui/HelpTooltip";

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const HOUR_LABELS = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, "0")}:00`);

export function HourlyHeatmap() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data: heatmap, isLoading, error } = useQuery({
    queryKey: ["heatmap", params.toString()],
    queryFn: ({ signal }) => api.heatmap(params, signal),
  });

  if (isLoading || !heatmap) {
    return (
      <div className="card">
        <div className="mb-4 shimmer h-4 w-40 rounded" />
        <div className="shimmer h-[120px] rounded" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">Crimes by Hour of Day</h3>
        <div className="flex h-[120px] items-center justify-center rounded-lg bg-bg-muted">
          <p className="text-sm text-text-dim">Failed to load heatmap data</p>
        </div>
      </div>
    );
  }

  const max = Math.max(...heatmap.matrix.flat());
  const data: [number, number, number][] = [];
  for (let day = 0; day < 7; day++) {
    for (let hour = 0; hour < 24; hour++) {
      data.push([hour, day, heatmap.matrix[day]?.[hour] ?? 0]);
    }
  }

  const option = {
    tooltip: {
      position: "top" as const,
      formatter: (p: { data: [number, number, number] }) =>
        `${DAY_LABELS[p.data[1]]} ${HOUR_LABELS[p.data[0]]}<br/><strong>${p.data[2].toLocaleString()}</strong> crimes`,
      backgroundColor: "#1a1a26",
      borderColor: "#2a2a3d",
      textStyle: { color: "#e8e8f0", fontSize: 12 },
    },
    xAxis: {
      type: "category" as const,
      data: HOUR_LABELS,
      splitArea: { show: false },
      axisLabel: { fontSize: 9, color: "#8888a0" },
      axisLine: { lineStyle: { color: "#2a2a3d" } },
    },
    yAxis: {
      type: "category" as const,
      data: DAY_LABELS,
      axisLabel: { fontSize: 9, color: "#8888a0" },
      axisLine: { show: false },
    },
    visualMap: {
      min: 0,
      max,
      calculable: false,
      orient: "horizontal" as const,
      left: "center",
      bottom: -25,
      splitNumber: 5,
      inRange: {
        color: ["#2d2d44", "#312e81", "#4338ca", "#6366f1", "#818cf8"],
      },
      textStyle: { color: "#8888a0", fontSize: 9 },
      text: ["Fewer", "More"],
    },
    grid: { top: 10, bottom: 55, left: 30, right: 5 },
    series: [
      {
        type: "heatmap",
        data,
        label: { show: false },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: "rgba(99, 102, 241, 0.4)" },
        },
      },
    ],
  };

  return (
    <div className="card">
      <div className="mb-4 flex items-center">
        <h3 className="text-sm font-semibold text-text">Crimes by Hour of Day</h3>
        <HelpTooltip content="Heatmap showing crime frequency by day of week and hour. Darker cells indicate higher crime counts. Use this to identify peak crime windows." />
      </div>
      <ReactECharts option={option} style={{ height: 210 }} />
    </div>
  );
}
