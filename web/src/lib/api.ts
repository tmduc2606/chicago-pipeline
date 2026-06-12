export type AnomalyPoint = {
  ts: string;
  z: number;
  count: number;
};

export type TypeTrendPoint = {
  primary_type: string;
  ts: string;
  count: number;
  arrests: number;
};

const API_BASE = "/api";

type FetchOptions = {
  signal?: AbortSignal;
};

async function fetchJson<T>(path: string, opts?: FetchOptions): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    signal: opts?.signal,
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export type OverviewKpi = {
  total: number;
  arrest_rate: number;
  domestic_pct: number;
  delta_pct: number;
  prev_total: number;
};

export type HeatmapResponse = {
  matrix: number[][];
}

export type GeoCluster = {
  h3: string;
  count: number;
  lat: number;
  lng: number;
};

export type ChoroplethBucket = {
  key: string;
  label: string;
  value: number;
  lat: number;
  lng: number;
};

export type TimeseriesPoint = {
  ts: string;
  count: number;
  arrests: number;
};

export type CrimeTypeCount = {
  primary_type: string;
  count: number;
};

export type DistrictArrest = {
  district: number;
  arrest_rate: number;
  total: number;
};

export type CrimeTypeArrest = {
  primary_type: string;
  arrest_rate: number;
};

export type BooleanSplit = {
  true_count: number;
  false_count: number;
};

export type LocationCount = {
  location_description: string;
  count: number;
};

export type FilterOptions = {
  date_min: string;
  date_max: string;
  primary_types: string[];
  districts: number[];
  community_areas: number[];
};

export type HealthCheck = {
  status: string;
  checks: Record<string, boolean>;
};

export const api = {
  overview: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<OverviewKpi>(`/overview${params ? "?" + params : ""}`, { signal }),

  heatmap: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<HeatmapResponse>(`/heatmap${params ? "?" + params : ""}`, { signal }),

  geoClusters: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<GeoCluster[]>(`/geo/clusters${params ? "?" + params : ""}`, { signal }),

  choropleth: (params?: URLSearchParams, signal?: AbortSignal) => {
    const url = params ? `/geo/choropleth?${params}` : "/geo/choropleth";
    return fetchJson<ChoroplethBucket[]>(url, { signal });
  },

  timeseries: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<TimeseriesPoint[]>(`/timeseries${params ? "?" + params : ""}`, { signal }),

  crimeTypesTop: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<CrimeTypeCount[]>(`/crime-types/top${params ? "?" + params : ""}`, { signal }),

  crimeTypeTrend: (params: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<TimeseriesPoint[]>(`/crime-types/trend?${params}`, { signal }),

  arrestsByDistrict: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<DistrictArrest[]>(`/arrests/by-district${params ? "?" + params : ""}`, { signal }),

  arrestsByType: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<CrimeTypeArrest[]>(`/arrests/by-type${params ? "?" + params : ""}`, { signal }),

  domesticSplit: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<BooleanSplit>(`/context/domestic${params ? "?" + params : ""}`, { signal }),

  topLocations: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<LocationCount[]>(`/context/location${params ? "?" + params : ""}`, { signal }),

  filters: (signal?: AbortSignal) =>
    fetchJson<FilterOptions>("/filters", { signal }),

  health: (signal?: AbortSignal) =>
    fetchJson<HealthCheck>("/health", { signal }),

  anomalies: (params?: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<AnomalyPoint[]>(`/timeseries/anomalies${params ? "?" + params : ""}`, { signal }),

  crimeTypesTrends: (params: URLSearchParams, signal?: AbortSignal) =>
    fetchJson<TypeTrendPoint[]>(`/crime-types/trends?${params}`, { signal }),

  exportCsv: (params?: URLSearchParams) => {
    const url = `${API_BASE}/export/csv${params ? "?" + params : ""}`;
    return url;
  },
};
