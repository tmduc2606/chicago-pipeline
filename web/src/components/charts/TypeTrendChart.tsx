import { useQuery } from "@tanstack/react-query";
import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Line,
  LineChart,
  Legend,
} from "recharts";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { formatCrimeType } from "@/lib/utils";
import { ChartSkeleton } from "@/components/charts/TimeseriesChart";
import { HelpTooltip } from "@/components/ui/HelpTooltip";

const COLORS = [
  "#6366f1", "#22d3ee", "#fb7185", "#34d399", "#f97316",
  "#a78bfa", "#fbbf24", "#6b7280",
];

export function TypeTrendChart({ typesParam }: { typesParam: string }) {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const trendParams = new URLSearchParams(params);
  trendParams.set("types", typesParam);

  const { data, isLoading, error } = useQuery({
    queryKey: ["crime-types-trends", trendParams.toString()],
    queryFn: ({ signal }) => api.crimeTypesTrends(trendParams, signal),
    enabled: typesParam.length > 0,
  });

  if (isLoading || !data) {
    return <ChartSkeleton height={300} title="Crime Type Trends" />;
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">Crime Type Trends</h3>
        <div className="flex h-[300px] items-center justify-center rounded-lg bg-bg-muted">
          <p className="text-sm text-text-dim">Failed to load trend data</p>
        </div>
      </div>
    );
  }

  const typeNames = [...new Set(data.map((d) => d.primary_type))];
  const typeColors: Record<string, string> = {};
  typeNames.forEach((t, i) => {
    typeColors[t] = COLORS[i % COLORS.length]!;
  });

  const dateMap = new Map<string, Record<string, number>>();
  for (const d of data) {
    if (!dateMap.has(d.ts)) {
      dateMap.set(d.ts, {});
    }
    dateMap.get(d.ts)![d.primary_type] = d.count;
  }

  const chartData = Array.from(dateMap.entries())
    .map(([ts, counts]) => ({ ts, ...counts }))
    .sort((a, b) => a.ts.localeCompare(b.ts));

  return (
    <div className="card">
      <div className="mb-4 flex items-center">
        <h3 className="text-sm font-semibold text-text">Crime Type Trends</h3>
        <HelpTooltip content="Compare daily trends for multiple crime types. Each line represents a different offense category. Select types in the sidebar to filter." />
      </div>
      <p className="mb-3 text-xs text-text-dim">
        Daily trend comparison for top {typeNames.length} crime types
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3d" />
          <XAxis
            dataKey="ts"
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
            formatter={(value: string) => formatCrimeType(value)}
          />
          {typeNames.map((t) => (
            <Line
              key={t}
              type="monotone"
              dataKey={t}
              name={t}
              stroke={typeColors[t]}
              strokeWidth={2}
              dot={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
