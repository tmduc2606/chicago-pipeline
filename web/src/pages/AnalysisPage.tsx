import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { TimeseriesChart } from "@/components/charts/TimeseriesChart";
import { ArrestRateChart } from "@/components/charts/ArrestRateChart";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { TypeTrendChart } from "@/components/charts/TypeTrendChart";
import { formatCrimeType } from "@/lib/utils";

export function AnalysisPage() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ["overview", params.toString()],
    queryFn: ({ signal }) => api.overview(params, signal),
  });

  const { data: topTypes } = useQuery({
    queryKey: ["crime-types-top", params.toString()],
    queryFn: ({ signal }) => api.crimeTypesTop(params, signal),
  });

  const { data: topLocations } = useQuery({
    queryKey: ["locations", params.toString()],
    queryFn: ({ signal }) => api.topLocations(params, signal),
  });

  const topTypeNames = (topTypes ?? []).slice(0, 5).map((t) => t.primary_type);
  const trendsParams = new URLSearchParams(params);
  if (topTypeNames.length > 0) {
    trendsParams.set("types", topTypeNames.join(","));
  }

  const yoyDisplay = overview && overview.prev_total > 0
    ? `${overview.delta_pct}%`
    : "—";

  const dateRange = filters.from && filters.to
    ? `${filters.from} to ${filters.to}`
    : "the full dataset period";

  const typeCount = filters.types?.length ?? 0;

  const csvUrl = api.exportCsv(params);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-text">Analysis</h2>
        <p className="mt-1 text-sm text-text-muted">Deep dive into crime patterns</p>
        <p className="mt-2 rounded-lg bg-bg-muted p-3 text-xs text-text-dim">
          Explore crime trends over time and by district. Use the sidebar filters
          to narrow by date range and crime type. All numbers update automatically
          as you change filters.
        </p>
      </div>

      {loadingOverview ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card">
              <div className="shimmer h-3 w-24 rounded" />
              <div className="shimmer mt-2 h-7 w-20 rounded" />
            </div>
          ))}
        </div>
      ) : (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Crimes" value={overview?.total.toLocaleString() ?? "—"} color="text-primary-bright" />
        <StatCard label="Arrest Rate" value={`${overview?.arrest_rate ?? 0}%`} color="text-accent-cyan" subtitle="Crimes resulting in arrest" />
        <StatCard label="Domestic Incidents" value={`${overview?.domestic_pct ?? 0}%`} color="text-accent-amber" subtitle="Involving family or household" />
        <StatCard label="Year-over-Year Change" value={yoyDisplay} color="text-accent-green" subtitle={overview && overview.prev_total > 0 ? "vs same period year prior" : "Single-period dataset"} />
      </div>
      )}

      <ErrorBoundary>
        <TimeseriesChart />
      </ErrorBoundary>

      {/* Multi-type trend chart */}
      {topTypes && topTypes.length >= 2 && (
        <ErrorBoundary>
          <TypeTrendChart typesParam={topTypeNames.join(",")} />
        </ErrorBoundary>
      )}

      <ErrorBoundary>
        <ArrestRateChart />
      </ErrorBoundary>

      {loadingOverview ? (
        <div className="card py-8">
          <div className="shimmer mx-auto h-4 w-48 rounded" />
          <div className="shimmer mx-auto mt-3 h-3 w-64 rounded" />
          <div className="shimmer mx-auto mt-2 h-3 w-56 rounded" />
        </div>
      ) : (
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">Key Insights</h3>
        <ul className="space-y-3 text-sm text-text-muted">
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary" />
            <span>
              <strong className="mr-1 text-text">{overview?.total.toLocaleString()}</strong>
              crime incidents recorded{typeCount > 0 ? ` across ${typeCount} selected crime type${typeCount > 1 ? "s" : ""}` : ""} from {dateRange}.
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent-cyan" />
            <span>
              Arrest rate: <strong className="mr-1 text-text">{overview?.arrest_rate}%</strong>
              — roughly 1 in {overview && overview.arrest_rate > 0 ? Math.round(100 / overview.arrest_rate) : "—"} crimes leads to an arrest.
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent-amber" />
            <span>
              Domestic incidents make up <strong className="mr-1 text-text">{overview?.domestic_pct}%</strong>
              {" "}of all crimes — involving family or household members.
            </span>
          </li>
          {topTypes && topTypes.length > 0 && (
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent-rose" />
              <span>
                Most common type: <strong className="mr-1 text-text">{formatCrimeType(topTypes[0]!.primary_type)}</strong>
                {" "}with {topTypes[0]!.count.toLocaleString()} incidents
                {topTypes.length > 1 ? `, followed by ${formatCrimeType(topTypes[1]!.primary_type)} (${topTypes[1]!.count.toLocaleString()})` : ""}.
              </span>
            </li>
          )}
          {topLocations && topLocations.length > 0 && (
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent-green" />
              <span>
                Most crimes occur at <strong className="mr-1 text-text">
                  {topLocations[0]!.location_description.charAt(0).toUpperCase() + topLocations[0]!.location_description.slice(1).toLowerCase().replace(/_/g, " ")}
                </strong>
                {" "}({topLocations[0]!.count.toLocaleString()} incidents).
              </span>
            </li>
          )}
        </ul>
      </div>
      )}

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

function StatCard({ label, value, color, subtitle }: { label: string; value: string; color: string; subtitle?: string }) {
  return (
    <div className="card">
      <p className="text-xs font-medium uppercase tracking-wider text-text-muted">{label}</p>
      <p className={`mt-2 text-2xl font-bold ${color}`}>{value}</p>
      {subtitle && <p className="mt-1 text-xs text-text-dim">{subtitle}</p>}
    </div>
  );
}
