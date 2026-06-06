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

export function ArrestRateChart() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data, isLoading } = useQuery({
    queryKey: ["arrests-by-district", params.toString()],
    queryFn: ({ signal }) => api.arrestsByDistrict(params, signal),
  });

  if (isLoading || !data) {
    return <ChartSkeleton height={300} title="Arrest Rate by District" />;
  }

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-text">Arrest Rate by District</h3>
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
