import { useQuery } from "@tanstack/react-query";
import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Area,
  AreaChart,
} from "recharts";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { ChartSkeleton } from "@/components/charts/TimeseriesChart";
import { HelpTooltip } from "@/components/ui/HelpTooltip";

export function LocationTrendChart() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data, isLoading, error } = useQuery({
    queryKey: ["timeseries-locations", params.toString()],
    queryFn: ({ signal }) => api.timeseries(params, signal),
  });

  if (isLoading || !data) {
    return <ChartSkeleton height={200} title="Location Trend" />;
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">Location Trend</h3>
        <div className="flex h-[200px] items-center justify-center rounded-lg bg-bg-muted">
          <p className="text-sm text-text-dim">Failed to load trend data</p>
        </div>
      </div>
    );
  }

  const chartData = data.map((d) => ({
    date: d.ts,
    count: d.count,
  }));

  return (
    <div className="card">
      <div className="mb-4 flex items-center">
        <h3 className="text-sm font-semibold text-text">Location Trend</h3>
        <HelpTooltip content="Daily crime count for the currently selected area and filters. Use the sidebar to filter by district or community area." />
      </div>
      <p className="mb-2 text-xs text-text-dim">
        Daily crime count for the selected area and filters
      </p>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="gradientLocationTrend" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3d" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 9, fill: "#8888a0" }}
            tickFormatter={(v) => {
              const d = new Date(v);
              return `${d.getMonth() + 1}/${d.getDate()}`;
            }}
            axisLine={{ stroke: "#2a2a3d" }}
            tickLine={{ stroke: "#2a2a3d" }}
          />
          <YAxis
            tick={{ fontSize: 9, fill: "#8888a0" }}
            axisLine={{ stroke: "#2a2a3d" }}
            tickLine={{ stroke: "#2a2a3d" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1a1a26",
              border: "1px solid #2a2a3d",
              borderRadius: "8px",
              fontSize: "11px",
              color: "#e8e8f0",
            }}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#f97316"
            strokeWidth={2}
            fill="url(#gradientLocationTrend)"
            name="Crimes"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
