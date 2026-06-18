export default function AboutPage() {
  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-text">About This Project</h2>
        <p className="mt-1 text-sm text-text-muted">
          Chicago Crime Dashboard — End-to-End Data Platform
        </p>
      </div>

      <section className="space-y-4">
        <h3 className="text-xl font-semibold text-text">Data Sources</h3>
        <p className="text-sm text-text-muted leading-relaxed">
          This platform analyzes the{" "}
          <a
            href="https://www.kaggle.com/datasets/aliafzal9323/chicago-crime-dataset-2024-2026"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-bright underline hover:text-primary"
          >
            Chicago Crime Dataset 2024–2026
          </a>{" "}
          from Kaggle. The dataset contains reported crime incidents from the Chicago Police Department.
          For demonstration purposes, the pipeline uses a synthetic 90-day seed dataset (57,931 records)
          that mirrors the statistical properties of the real data.
        </p>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-semibold text-text">Methodology</h3>
        <ul className="list-disc pl-6 space-y-2 text-sm text-text-muted">
          <li><strong className="text-text">Bronze layer:</strong> Raw CSV ingestion into MinIO (S3-compatible object store).</li>
          <li><strong className="text-text">Silver layer:</strong> PySpark cleaning — snake_case, typed, deduped, validated with Great Expectations.</li>
          <li><strong className="text-text">Gold layer:</strong> Business aggregates and conformed dimensions in Parquet.</li>
          <li><strong className="text-text">Warehouse:</strong> PostgreSQL + PostGIS star schema (fact_crime + 4 dimensions).</li>
          <li><strong className="text-text">Marts:</strong> dbt models for KPI dashboards, hotspot grids, temporal heatmaps, and arrest analytics.</li>
          <li><strong className="text-text">API:</strong> FastAPI async service with Redis caching, 21 endpoints.</li>
          <li><strong className="text-text">Frontend:</strong> React SPA with Recharts, ECharts, MapLibre, dark/light themes.</li>
        </ul>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-semibold text-text">Technology Stack</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {[
            "MinIO", "Apache Airflow", "Apache Spark", "dbt",
            "PostgreSQL + PostGIS", "Great Expectations", "FastAPI",
            "React + TypeScript", "Tailwind CSS", "Recharts",
            "MapLibre GL", "Redis", "Prometheus + Grafana",
          ].map((tech) => (
            <span
              key={tech}
              className="px-3 py-1.5 rounded-full bg-bg-muted text-sm text-text-muted text-center"
            >
              {tech}
            </span>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-semibold text-text">Known Limitations</h3>
        <ul className="list-disc pl-6 space-y-2 text-sm text-text-muted">
          <li>Synthetic data — not real Chicago crime records.</li>
          <li>Choropleth map uses simplified district boundaries (real GeoJSON deferred).</li>
          <li>No real-time streaming — batch-only pipeline.</li>
          <li>No authentication — public read-only dashboard.</li>
          <li>Forecast and anomaly endpoints exist but are not yet visualized on dedicated pages.</li>
        </ul>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-semibold text-text">License</h3>
        <p className="text-sm text-text-muted">
          MIT License. See{" "}
          <a
            href="https://github.com/nickai/chicago-pipeline/blob/main/LICENSE"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-bright underline hover:text-primary"
          >
            LICENSE
          </a>.
        </p>
      </section>
    </div>
  );
}
