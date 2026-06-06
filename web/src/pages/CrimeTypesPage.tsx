import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { titleCase } from "@/lib/utils";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const tooltipStyle = {
  backgroundColor: "#1a1a26",
  border: "1px solid #2a2a3d",
  borderRadius: "8px",
  fontSize: "12px",
  color: "#e8e8f0",
};

type SortKey = "type" | "count" | "arrest_rate";
type SortDir = "asc" | "desc";

export function CrimeTypesPage() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);
  const [sortKey, setSortKey] = useState<SortKey>("count");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const { data: topTypes, isLoading: loadingTop } = useQuery({
    queryKey: ["crime-types-top", params.toString()],
    queryFn: ({ signal }) => api.crimeTypesTop(params, signal),
  });

  const { data: typeArrests, isLoading: loadingArrests } = useQuery({
    queryKey: ["arrests-by-type", params.toString()],
    queryFn: ({ signal }) => api.arrestsByType(params, signal),
  });

  const hasNoData = !loadingTop && !loadingArrests && (!topTypes || topTypes.length === 0);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "type" ? "asc" : "desc");
    }
  };

  const sorted = (topTypes ?? [])
    .slice()
    .sort((a, b) => {
      if (sortKey === "type") {
        const cmp = a.primary_type.localeCompare(b.primary_type);
        return sortDir === "asc" ? cmp : -cmp;
      }
      const aVal = sortKey === "count" ? a.count : (typeArrests?.find((x) => x.primary_type === a.primary_type)?.arrest_rate ?? 0);
      const bVal = sortKey === "count" ? b.count : (typeArrests?.find((x) => x.primary_type === b.primary_type)?.arrest_rate ?? 0);
      return sortDir === "asc" ? aVal - bVal : bVal - aVal;
    });

  const sortArrow = (key: SortKey) => {
    if (sortKey !== key) return "";
    return sortDir === "asc" ? " \u25B2" : " \u25BC";
  };

  const top3 = topTypes?.slice(0, 3) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-text">Crime Types</h2>
        <p className="mt-1 text-sm text-text-muted">Breakdown by offense category</p>
        <p className="mt-2 rounded-lg bg-bg-muted p-3 text-xs text-text-dim">
          Crime types are categories used by the Chicago Police Department to classify incidents.
          Hover over any bar for exact numbers. Use sidebar filters to narrow by date or type.
        </p>
      </div>

      {hasNoData ? (
        <div className="card py-12 text-center">
          <p className="text-sm text-text-muted">No crime types match these filters.</p>
          <p className="mt-1 text-xs text-text-dim">Try broadening your date range or selecting different crime types.</p>
        </div>
      ) : (
        <>
      {/* Top 3 summary */}
      {!loadingTop && top3.length >= 3 && (
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold text-text">Top 3 Crime Types</h3>
          <div className="grid grid-cols-1 gap-2 text-xs text-text-muted sm:grid-cols-3">
            <p><span className="font-medium text-text">{titleCase(top3[0]!.primary_type)}</span> — {top3[0]!.count.toLocaleString()} incidents</p>
            <p><span className="font-medium text-text">{titleCase(top3[1]!.primary_type)}</span> — {top3[1]!.count.toLocaleString()} incidents</p>
            <p><span className="font-medium text-text">{titleCase(top3[2]!.primary_type)}</span> — {top3[2]!.count.toLocaleString()} incidents</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="card">
          <h3 className="mb-4 text-sm font-semibold text-text">Most Common Types</h3>
          {loadingTop ? (
            <div className="shimmer h-[400px] rounded" />
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={topTypes?.map((d) => ({ name: titleCase(d.primary_type), count: d.count })) ?? []}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3d" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: "#8888a0" }} axisLine={{ stroke: "#2a2a3d" }} />
                <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 11, fill: "#8888a0" }} axisLine={{ stroke: "#2a2a3d" }} />
                <Tooltip contentStyle={tooltipStyle} formatter={(value) => [Number(value ?? 0).toLocaleString(), "Count"]} />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <h3 className="mb-4 text-sm font-semibold text-text">Arrest Rate by Type</h3>
          {loadingArrests ? (
            <div className="shimmer h-[400px] rounded" />
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={typeArrests?.map((d) => ({ name: titleCase(d.primary_type), rate: d.arrest_rate })) ?? []}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3d" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: "#8888a0" }} tickFormatter={(v) => `${v}%`} axisLine={{ stroke: "#2a2a3d" }} />
                <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 11, fill: "#8888a0" }} axisLine={{ stroke: "#2a2a3d" }} />
                <Tooltip contentStyle={tooltipStyle} formatter={(value) => [`${Number(value ?? 0).toFixed(1)}%`, "Arrest Rate"]} />
                <Bar dataKey="rate" fill="#22d3ee" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">All Crime Types</h3>
        {!topTypes || topTypes.length === 0 ? (
          <p className="py-6 text-center text-sm text-text-dim">No data available</p>
        ) : (
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-text-muted">
                <th
                  className="cursor-pointer pb-3 pr-4 text-xs font-medium uppercase tracking-wider transition-colors hover:text-text"
                  onClick={() => toggleSort("type")}
                >
                  Type{sortArrow("type")}
                </th>
                <th
                  className="cursor-pointer pb-3 pr-4 text-right text-xs font-medium uppercase tracking-wider transition-colors hover:text-text"
                  onClick={() => toggleSort("count")}
                >
                  Count{sortArrow("count")}
                </th>
                <th
                  className="cursor-pointer pb-3 text-right text-xs font-medium uppercase tracking-wider transition-colors hover:text-text"
                  onClick={() => toggleSort("arrest_rate")}
                >
                  Arrest Rate{sortArrow("arrest_rate")}
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((t) => {
                const arrest = typeArrests?.find((a) => a.primary_type === t.primary_type);
                return (
                  <tr key={t.primary_type} className="border-b border-border/50 transition-colors hover:bg-bg-hover/50">
                    <td className="py-3 pr-4 font-medium text-text">{titleCase(t.primary_type)}</td>
                    <td className="py-3 pr-4 text-right tabular-nums text-text-muted">{t.count.toLocaleString()}</td>
                    <td className="py-3 text-right tabular-nums text-text-muted">
                      {arrest ? `${arrest.arrest_rate.toFixed(1)}%` : "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        )}
      </div>
      </>
      )}
    </div>
  );
}
