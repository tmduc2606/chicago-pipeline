// Placeholder. This file is generated from contracts/openapi.yaml
// by the backend agent using `openapi-typescript` (or equivalent).
// Do not hand-edit. The backend agent owns this file.

export interface OverviewKpi {
  total: number;
  arrest_rate: number;
  domestic_pct: number;
  delta_pct: number;
}

export interface TimeseriesPoint {
  ts: string;
  count: number;
  arrests?: number;
}

export interface ForecastPoint {
  ts: string;
  yhat: number;
  yhat_lower: number;
  yhat_upper: number;
}

export interface ForecastBundle {
  history: TimeseriesPoint[];
  forecast: ForecastPoint[];
}

export interface AnomalyPoint {
  ts: string;
  z: number;
  count: number;
}

export type HeatmapMatrix = number[][];
export interface Heatmap {
  matrix: HeatmapMatrix;
}

export interface GeoCluster {
  h3: string;
  lat: number;
  lng: number;
  count: number;
}

export interface ChoroplethBucket {
  key: string;
  value: number;
}

export interface CrimeTypeCount {
  primary_type: string;
  count: number;
}

export interface CrimeTypeArrest {
  primary_type: string;
  arrest_rate: number;
}

export interface DistrictArrest {
  district: number;
  arrest_rate: number;
  total: number;
}

export interface BooleanSplit {
  true_count: number;
  false_count: number;
}

export interface LocationCount {
  location_description: string;
  count: number;
}

export interface FilterOptions {
  date_min: string;
  date_max: string;
  primary_types: string[];
  districts: number[];
}

export type DagState = "success" | "failed" | "running" | "queued" | "none";
export interface DagStatus {
  dag_id: string;
  last_run: string | null;
  state: DagState;
}

export interface DagRun {
  run_id: string;
  dag_id: string;
  state: Exclude<DagState, "none">;
  start: string | null;
  end: string | null;
}

export interface QualitySummary {
  great_expectations: {
    success_pct: number;
    last_run: string | null;
  };
  dbt: {
    passed: number;
    failed: number;
    last_run: string | null;
  };
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    request_id: string;
  };
}
