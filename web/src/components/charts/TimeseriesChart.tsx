import { useQuery } from "@tanstack/react-query";
import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Area,
  Legend,
  ComposedChart,
  Scatter,
} from "recharts";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { HelpTooltip } from "@/components/ui/HelpTooltip";

export function TimeseriesChart() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data, isLoading, error } = useQuery({
    queryKey: ["timeseries", params.toString()],
    queryFn: ({ signal }) => api.timeseries(params, signal),
  });

  const { data: anomalies } = useQuery({
    queryKey: ["anomalies", params.toString()],
    queryFn: ({ signal }) => api.anomalies(params, signal),
  });

  if (isLoading || !data) {
    return <ChartSkeleton height={300} title="Daily Crime Trend" />;
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">Daily Crime Trend</h3>
        <div className="flex h-[300px] items-center justify-center rounded-lg bg-bg-muted">
          <p className="text-sm text-text-dim">Failed to load trend data</p>
        </div>
      </div>
    );
  }

  const anomalyDates = new Set(anomalies?.map((a) => a.ts) ?? []);

  const chartData = data.map((d) => ({
    date: d.ts,
    count: d.count,
    arrests: d.arrests,
    isAnomaly: anomalyDates.has(d.ts),
  }));

  const scatterData = (anomalies ?? []).map((a) => ({
    date: a.ts,
    count: a.count,
    z: a.z,
  }));

  return (
    <div className="card">
      <div className="mb-4 flex items-center">
        <h3 className="text-sm font-semibold text-text">Daily Crime Trend</h3>
        <HelpTooltip content="Daily count of all crimes (blue) and arrests (green). Red dots mark statistical anomalies where daily counts exceeded 2 standard deviations above the mean." />
      </div>
      {anomalies && anomalies.length > 0 && (
        <p className="mb-3 text-xs text-accent-rose">
          {anomalies.length} anomalous day{anomalies.length > 1 ? "s" : ""} detected (z-score &gt;{" "}
          {anomalies[0]!.z.toFixed(1)})
        </p>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData}>
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
          <Legend
            wrapperStyle={{ fontSize: "11px", color: "#e8e8f0" }}
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
          {scatterData.length > 0 && (
            <Scatter
              data={scatterData}
              dataKey="count"
              name="Anomalies"
              fill="#fb7185"
              stroke="#e11d48"
              strokeWidth={1}
            />
          )}
        </ComposedChart>
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
