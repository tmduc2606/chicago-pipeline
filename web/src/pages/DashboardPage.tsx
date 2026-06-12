import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { KpiCard, KpiSkeleton } from "@/components/charts/KpiCard";
import { TimeseriesChart } from "@/components/charts/TimeseriesChart";
import { OffenseBarChart } from "@/components/charts/OffenseBarChart";
import { ArrestRateChart } from "@/components/charts/ArrestRateChart";
import { DomesticSplitChart } from "@/components/charts/DomesticSplitChart";
import { HourlyHeatmap } from "@/components/charts/HourlyHeatmap";
import { ChoroplethMap } from "@/components/maps/ChoroplethMap";
import { ClusterMap } from "@/components/maps/ClusterMap";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { formatCrimeType } from "@/lib/utils";

function AboutThisData() {
  const [open, setOpen] = useState(false);
  return (
    <div className="card">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between text-left"
        aria-expanded={open}
      >
        <span className="text-sm font-semibold text-text">About this dashboard</span>
        <svg
          className={`h-4 w-4 text-text-muted transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="mt-4 space-y-2 text-sm text-text-muted">
          <p>
            This dashboard visualizes synthetic Chicago crime data covering a 90-day period from
            2024-01-01 to 2026-05-31. It uses a medallion architecture (Bronze → Silver → Gold)
            powered by Apache Spark and dbt.
          </p>
          <ul className="list-inside list-disc space-y-1 pl-1">
            <li>Use the <strong className="text-text">sidebar filters</strong> to narrow by date range and crime type</li>
            <li>Hover over any chart for exact values</li>
            <li>Navigate between pages using the sidebar</li>
            <li>Filters persist across all pages</li>
          </ul>
          <p className="pt-1 text-xs text-text-dim">
            Data source: Kaggle Chicago Crime 2024–2026 (synthetic). Pipeline runs on every startup.
          </p>
        </div>
      )}
    </div>
  );
}

export function DashboardPage() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ["overview", params.toString()],
    queryFn: ({ signal }) => api.overview(params, signal),
  });

  const { data: timeseries } = useQuery({
    queryKey: ["timeseries-kpi", params.toString()],
    queryFn: ({ signal }) => api.timeseries(params, signal),
  });

  const { data: topLocations, isLoading: loadingLocations } = useQuery({
    queryKey: ["locations", params.toString()],
    queryFn: ({ signal }) => api.topLocations(params, signal),
  });

  const { data: topTypes } = useQuery({
    queryKey: ["crime-types-top", params.toString()],
    queryFn: ({ signal }) => api.crimeTypesTop(params, signal),
  });

  const sparklineCounts = timeseries?.map((d) => d.count) ?? [];
  const sparklineArrests = timeseries?.map((d) => d.arrests) ?? [];

  const csvUrl = api.exportCsv(params);
  const dateRange = filters.from && filters.to
    ? `${filters.from} to ${filters.to}`
    : "the full dataset period";

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-text">Dashboard</h2>
        <p className="mt-1 text-sm text-text-muted">
          Chicago crime data overview 2024–2026
        </p>
      </div>

      {/* Onboarding section */}
      <AboutThisData />

      {/* KPI Row */}
      {loadingOverview ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <KpiSkeleton key={i} />
          ))}
        </div>
      ) : (
        <>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Total Crimes"
            value={overview?.total ?? 0}
            format="number"
            color="cyan"
            subtitle="All incidents in selected period"
            sparklineData={sparklineCounts}
          />
          <KpiCard
            title="Arrest Rate"
            value={overview?.arrest_rate ?? 0}
            format="percent"
            color="cyan"
            subtitle="Crimes resulting in arrest"
            sparklineData={sparklineArrests}
          />
          <KpiCard
            title="Domestic Incidents"
            value={overview?.domestic_pct ?? 0}
            format="percent"
            color="amber"
            subtitle="Crimes involving family or household"
          />
          {overview && overview.prev_total > 0 ? (
            <KpiCard
              title="Year-over-Year Change"
              value={overview.delta_pct}
              format="percent"
              color={overview.delta_pct > 0 ? "red" : "green"}
              subtitle="Compared to same period one year prior"
            />
          ) : (
            <div className="kpi-glow group rounded-xl border border-border bg-bg-card p-5 transition-all duration-200">
              <div className="flex-1">
                <p className="text-xs font-medium uppercase tracking-wider text-text-muted">Year-over-Year Change</p>
                <p className="mt-2 text-3xl font-bold tracking-tight text-text-dim">&mdash;</p>
                <p className="mt-1 text-xs text-text-dim">Single-period dataset</p>
              </div>
            </div>
          )}
        </div>

        {/* Summary section */}
        {overview && (
          <div className="card">
            <h3 className="mb-3 text-sm font-semibold text-text">At a Glance</h3>
            <div className="grid grid-cols-1 gap-2 text-xs text-text-muted sm:grid-cols-3">
              <p>
                <span className="font-medium text-text">{overview.total.toLocaleString()}</span> total crimes
                in the selected period
              </p>
              <p>
                <span className="font-medium text-text">{overview.arrest_rate.toFixed(1)}%</span> of incidents
                resulted in an arrest
              </p>
              <p>
                <span className="font-medium text-text">{overview.domestic_pct.toFixed(1)}%</span> of incidents
                were domestic-related
              </p>
            </div>
          </div>
        )}
        </>
      )}

      {/* Key Findings */}
      {!loadingOverview && overview && topTypes && topTypes.length > 0 && (
        <div className="card">
          <h3 className="mb-3 text-sm font-semibold text-text">Key Findings</h3>
          <div className="space-y-2 text-xs text-text-dim">
            <p>
              <span className="text-accent-rose">&bull;</span>{" "}
              <strong className="text-text-muted">{overview.total.toLocaleString()}</strong> total crimes recorded
              {filters.from || filters.to ? ` (${dateRange})` : ""}.
            </p>
            <p>
              <span className="text-accent-cyan">&bull;</span>{" "}
              <strong className="text-text-muted">{formatCrimeType(topTypes[0]!.primary_type)}</strong> is the most common crime type
              with <strong className="text-text-muted">{topTypes[0]!.count.toLocaleString()}</strong> incidents
              {topTypes.length > 1
                ? ` — ${(topTypes[0]!.count / topTypes[1]!.count).toFixed(1)}x more than ${formatCrimeType(topTypes[1]!.primary_type)}`
                : ""}.
            </p>
            {overview.arrest_rate > 0 && (
              <p>
                <span className="text-accent-green">&bull;</span>{" "}
                Arrest rate is <strong className="text-text-muted">{overview.arrest_rate}%</strong>
                {" "}(roughly 1 in {Math.round(100 / overview.arrest_rate)} crimes leads to an arrest).
              </p>
            )}
            {overview.prev_total > 0 && (
              <p>
                <span className={overview.delta_pct < 0 ? "text-accent-green" : "text-accent-rose"}>&bull;</span>{" "}
                Year-over-year crime totals are{" "}
                <strong className={overview.delta_pct < 0 ? "text-accent-green" : "text-accent-rose"}>
                  {overview.delta_pct > 0 ? "up" : "down"} {Math.abs(overview.delta_pct).toFixed(1)}%
                </strong>
                {" "}compared to the same period last year.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Timeseries */}
      <TimeseriesChart />

      {/* Heatmap + Domestic */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <HourlyHeatmap />
        </div>
        <DomesticSplitChart />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <OffenseBarChart />
        <ArrestRateChart />
      </div>

      {/* Maps */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ErrorBoundary>
          <ChoroplethMap />
        </ErrorBoundary>
        <ErrorBoundary>
          <ClusterMap />
        </ErrorBoundary>
      </div>

      {/* Top Locations */}
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">Top Locations</h3>
        {loadingLocations ? (
          <div className="space-y-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="shimmer h-4 w-6 rounded" />
                <div className="shimmer h-4 flex-1 rounded" />
                <div className="shimmer h-4 w-16 rounded" />
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {topLocations?.slice(0, 10).map((loc, i) => (
              <div key={loc.location_description} className="flex items-center gap-4 text-sm">
                <span className="w-6 text-right font-mono text-xs text-text-dim">
                  {(i + 1).toString().padStart(2, "0")}
                </span>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-text">
                      {loc.location_description.charAt(0).toUpperCase() + loc.location_description.slice(1).toLowerCase().replace(/_/g, " ")}
                    </span>
                    <span className="tabular-nums text-text-muted">
                      {loc.count.toLocaleString()}
                    </span>
                  </div>
                  <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-bg-muted">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary to-primary-bright transition-all duration-500"
                      style={{
                        width: `${(loc.count / (topLocations[0]?.count ?? 1)) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Data Notes */}
      <div className="card">
        <h3 className="mb-3 text-sm font-semibold text-text">Data Notes</h3>
        <div className="space-y-2 text-xs text-text-dim">
          <p>
            <strong className="text-text-muted">Data source:</strong> Chicago Crime Database — Kaggle Chicago Crime 2024–2026 (synthetic data).
            Data is refreshed on every pipeline startup.
          </p>
          <p>
            <strong className="text-text-muted">Methodology:</strong> Crimes are aggregated from the Gold layer of a medallion pipeline
            (Bronze → Silver → Gold) using Apache Spark and dbt. Arrest rates represent the percentage of incidents where
            at least one arrest was made.
          </p>
          <p>
            <strong className="text-text-muted">Limitations:</strong> This is synthetic data and should not be used for real-world
            policy decisions. Figures may differ from official Chicago Police Department statistics.
          </p>
          <div className="flex gap-3 pt-1">
            <a
              href={csvUrl}
              download
              className="inline-flex items-center gap-1.5 rounded-md border border-border bg-bg-muted px-3 py-1.5 text-xs text-text-muted transition-colors hover:border-primary hover:text-primary-bright"
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download CSV
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
