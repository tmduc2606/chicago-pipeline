import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { ChoroplethMap } from "@/components/maps/ChoroplethMap";
import { ClusterMap } from "@/components/maps/ClusterMap";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { titleCase } from "@/lib/utils";

type SortKey = "name" | "count";
type SortDir = "asc" | "desc";

export function LocationsPage() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);
  const [sortKey, setSortKey] = useState<SortKey>("count");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [search, setSearch] = useState("");
  const [copied, setCopied] = useState(false);

  const { data: locations, isLoading, isError } = useQuery({
    queryKey: ["locations", params.toString()],
    queryFn: ({ signal }) => api.topLocations(params, signal),
  });

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "name" ? "asc" : "desc");
    }
  };

  const sortArrow = (key: SortKey) => {
    if (sortKey !== key) return "";
    return sortDir === "asc" ? " \u25B2" : " \u25BC";
  };

  const filtered = (locations ?? [])
    .filter((loc) =>
      search ? loc.location_description.toLowerCase().includes(search.toLowerCase()) : true
    )
    .slice()
    .sort((a, b) => {
      if (sortKey === "name") {
        const cmp = a.location_description.localeCompare(b.location_description);
        return sortDir === "asc" ? cmp : -cmp;
      }
      return sortDir === "asc" ? a.count - b.count : b.count - a.count;
    });

  const handleCopy = async () => {
    const text = (locations ?? [])
      .map((loc, i) => `${i + 1}. ${titleCase(loc.location_description)} — ${loc.count.toLocaleString()}`)
      .join("\n");
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-text">Locations</h2>
        <p className="mt-1 text-sm text-text-muted">Geographic distribution of crimes</p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ErrorBoundary>
          <ChoroplethMap />
        </ErrorBoundary>
        <ErrorBoundary>
          <ClusterMap />
        </ErrorBoundary>
      </div>

      {/* Map legend */}
      <div className="flex flex-wrap gap-4 rounded-lg bg-bg-card px-4 py-2 text-xs text-text-dim">
        <span className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-full border border-primary bg-primary/70" />
          Choropleth: crime count by district (larger = more)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-full border border-accent-orange bg-accent-orange/70" />
          Clusters: individual crime locations (larger = denser)
        </span>
      </div>

      {/* Hottest district summary */}
      {!isLoading && locations && locations.length > 0 && (
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold text-text">Busiest Location</h3>
          <p className="text-xs text-text-muted">
            <span className="font-medium text-text">{titleCase(locations[0]!.location_description)}</span> is the
            most common location type with <span className="font-medium text-text">{locations[0]!.count.toLocaleString()}</span> incidents
            {locations.length > 1 ? (
              <> — nearly <span className="font-medium text-text">
                {(locations[0]!.count / locations[locations.length - 1]!.count).toFixed(0)}x
              </span> more than the least common in the top 10</>
            ) : null}.
          </p>
        </div>
      )}

      <div className="card">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Top Locations</h3>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Search locations..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="rounded-lg border border-border bg-bg-muted px-3 py-1.5 text-xs text-text outline-none transition-colors focus:border-primary"
            />
            <button
              onClick={handleCopy}
              className="rounded-lg border border-border bg-bg-muted px-3 py-1.5 text-xs text-text-muted transition-colors hover:border-primary hover:text-primary-bright"
            >
              {copied ? "Copied!" : "Copy list"}
            </button>
          </div>
        </div>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="shimmer h-4 w-6 rounded" />
                <div className="shimmer h-4 flex-1 rounded" />
                <div className="shimmer h-4 w-16 rounded" />
              </div>
            ))}
          </div>
        ) : isError ? (
          <p className="py-6 text-center text-sm text-text-dim">Failed to load location data</p>
        ) : !locations || locations.length === 0 ? (
          <p className="py-6 text-center text-sm text-text-dim">No location data available. Try adjusting your filters.</p>
        ) : (
          <>
            <div className="mb-2 flex items-center justify-between text-[10px] uppercase tracking-wider text-text-dim">
              <button
                className="cursor-pointer pr-4 text-left font-medium transition-colors hover:text-text"
                onClick={() => toggleSort("name")}
              >
                Location{sortArrow("name")}
              </button>
              <button
                className="cursor-pointer pl-4 text-right font-medium transition-colors hover:text-text"
                onClick={() => toggleSort("count")}
              >
                Count{sortArrow("count")}
              </button>
            </div>
            <div className="space-y-3">
              {filtered.map((loc, i) => (
                <div key={loc.location_description} className="flex items-center gap-4 text-sm">
                  <span className="w-6 text-right font-mono text-xs text-text-dim">
                    {(i + 1).toString().padStart(2, "0")}
                  </span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-text">{titleCase(loc.location_description)}</span>
                      <span className="tabular-nums text-text-muted">{loc.count.toLocaleString()}</span>
                    </div>
                    <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-bg-muted">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-accent-orange to-accent-amber transition-all duration-500"
                        style={{ width: `${(loc.count / (locations[0]?.count ?? 1)) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
              {filtered.length === 0 && search && (
                <p className="py-4 text-center text-xs text-text-dim">No locations match "{search}"</p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
