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
import { titleCase } from "@/lib/utils";

export function OffenseBarChart() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data, isLoading } = useQuery({
    queryKey: ["crime-types-top", params.toString()],
    queryFn: ({ signal }) => api.crimeTypesTop(params, signal),
  });

  if (isLoading || !data) {
    return <ChartSkeleton height={300} title="Top Crime Types" />;
  }

  const chartData = data.map((d) => ({
    type: titleCase(d.primary_type),
    count: d.count,
  }));

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-text">Top Crime Types</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3d" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 10, fill: "#8888a0" }} axisLine={{ stroke: "#2a2a3d" }} />
          <YAxis
            type="category"
            dataKey="type"
            width={140}
            tick={{ fontSize: 10, fill: "#8888a0" }}
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
            formatter={(value, name) => [
              Number(value ?? 0).toLocaleString(),
              titleCase(name as string),
            ]}
          />
          <Bar dataKey="count" fill="#6366f1" radius={[0, 6, 6, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
