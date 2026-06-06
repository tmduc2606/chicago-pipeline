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

export function TimeseriesChart() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data, isLoading } = useQuery({
    queryKey: ["timeseries", params.toString()],
    queryFn: ({ signal }) => api.timeseries(params, signal),
  });

  if (isLoading || !data) {
    return <ChartSkeleton height={300} title="Daily Crime Trend" />;
  }

  const chartData = data.map((d) => ({
    date: d.ts,
    count: d.count,
    arrests: d.arrests,
  }));

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-text">Daily Crime Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="gradientCount" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradientArrests" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3d" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10, fill: "#8888a0" }}
            tickFormatter={(v) => {
              const d = new Date(v);
              return `${d.getMonth() + 1}/${d.getDate()}`;
            }}
            axisLine={{ stroke: "#2a2a3d" }}
            tickLine={{ stroke: "#2a2a3d" }}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "#8888a0" }}
            axisLine={{ stroke: "#2a2a3d" }}
            tickLine={{ stroke: "#2a2a3d" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1a1a26",
              border: "1px solid #2a2a3d",
              borderRadius: "8px",
              fontSize: "12px",
              color: "#e8e8f0",
            }}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#gradientCount)"
            name="Total"
          />
          <Area
            type="monotone"
            dataKey="arrests"
            stroke="#34d399"
            strokeWidth={1.5}
            fill="url(#gradientArrests)"
            name="Arrests"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ChartSkeleton({ height = 300 }: { height?: number; title?: string }) {
  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <div className="shimmer h-4 w-32 rounded" />
      </div>
      <div className="shimmer rounded" style={{ height }} />
    </div>
  );
}
