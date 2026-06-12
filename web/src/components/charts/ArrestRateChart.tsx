import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { ChartSkeleton } from "./TimeseriesChart";
import { HelpTooltip } from "@/components/ui/HelpTooltip";

export function ArrestRateChart() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data, isLoading, error } = useQuery({
    queryKey: ["arrests-by-district", params.toString()],
    queryFn: ({ signal }) => api.arrestsByDistrict(params, signal),
  });

  if (isLoading || !data) {
    return <ChartSkeleton height={300} title="Arrest Rate by District" />;
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">Arrest Rate by District</h3>
        <div className="flex h-[300px] items-center justify-center rounded-lg bg-bg-muted">
          <p className="text-sm text-text-dim">Failed to load arrest data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-4 flex items-center">
        <h3 className="text-sm font-semibold text-text">Arrest Rate by District</h3>
        <HelpTooltip content="Percentage of crimes resulting in at least one arrest, broken down by police district. Higher rates indicate more active enforcement." />
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3d" />
          <XAxis dataKey="district" tick={{ fontSize: 10, fill: "#8888a0" }} axisLine={{ stroke: "#2a2a3d" }} />
          <YAxis
            tick={{ fontSize: 10, fill: "#8888a0" }}
            tickFormatter={(v) => `${v}%`}
            axisLine={{ stroke: "#2a2a3d" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1a1a26",
              border: "1px solid #2a2a3d",
              borderRadius: "8px",
              fontSize: "12px",
              color: "#e8e8f0",
            }}
            formatter={(value) => [`${Number(value ?? 0).toFixed(1)}%`, "Arrest Rate"]}
          />
          <Bar dataKey="arrest_rate" fill="#22d3ee" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
