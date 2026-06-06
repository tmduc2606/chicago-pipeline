import ReactECharts from "echarts-for-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const HOUR_LABELS = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, "0")}:00`);

export function HourlyHeatmap() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data: heatmap, isLoading } = useQuery({
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
      bottom: "0%",
      inRange: {
        color: ["#1a1a26", "#312e81", "#4338ca", "#6366f1", "#818cf8"],
      },
      textStyle: { color: "#8888a0", fontSize: 9 },
      formatter: (v: number) => {
        if (v === 0) return "Fewer";
        if (v >= max) return "More";
        return "";
      },
      text: ["Fewer", "More"],
    },
    grid: { top: 10, bottom: 40, left: 30, right: 5 },
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
      <h3 className="mb-4 text-sm font-semibold text-text">Crimes by Hour of Day</h3>
      <ReactECharts option={option} style={{ height: 180 }} />
    </div>
  );
}
