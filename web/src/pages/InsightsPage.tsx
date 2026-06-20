import { useState } from "react";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import insightsData from "@/config/insights.json";

type Insight = {
  id: string;
  title: string;
  topic: string;
  tag: string;
  difficulty: number;
  finding_preview: string;
  finding_full: string;
  chart_type: string;
  data_points: number;
  notebook_section: string;
};

type TopicFilter = "all" | "temporal" | "spatial" | "categorical" | "relational";
type TagFilter = "all" | "distribution" | "trend" | "comparison" | "correlation" | "composition" | "clustering";

const TOPIC_COLORS: Record<string, string> = {
  temporal: "bg-accent-cyan/15 text-accent-cyan border-accent-cyan/30",
  spatial: "bg-accent-green/15 text-accent-green border-accent-green/30",
  categorical: "bg-accent-amber/15 text-accent-amber border-accent-amber/30",
  relational: "bg-accent-rose/15 text-accent-rose border-accent-rose/30",
};

const TAG_COLORS: Record<string, string> = {
  distribution: "bg-primary/15 text-primary-bright border-primary/30",
  trend: "bg-accent-cyan/15 text-accent-cyan border-accent-cyan/30",
  comparison: "bg-accent-amber/15 text-accent-amber border-accent-amber/30",
  correlation: "bg-accent-rose/15 text-accent-rose border-accent-rose/30",
  composition: "bg-accent-green/15 text-accent-green border-accent-green/30",
  clustering: "bg-accent-orange/15 text-accent-orange border-accent-orange/30",
};

function DifficultyDots({ level }: { level: number }) {
  return (
    <span className="inline-flex gap-0.5" title={`Difficulty: ${level}/5`}>
      {Array.from({ length: 5 }).map((_, i) => (
        <span
          key={i}
          className={`inline-block h-2 w-2 rounded-full ${
            i < level ? "bg-accent-amber" : "bg-bg-muted"
          }`}
        />
      ))}
    </span>
  );
}

function InsightCard({ insight }: { insight: Insight }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card transition-all duration-200 hover:border-primary/50">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[10px] font-medium ${TOPIC_COLORS[insight.topic] ?? ""}`}>
              {insight.topic}
            </span>
            <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[10px] font-medium ${TAG_COLORS[insight.tag] ?? ""}`}>
              {insight.tag}
            </span>
            <DifficultyDots level={insight.difficulty} />
          </div>
          <h3 className="text-sm font-semibold text-text">{insight.title}</h3>
          <p className="mt-1.5 text-xs text-text-muted">{insight.finding_preview}</p>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex-shrink-0 rounded-lg border border-border bg-bg-muted px-2.5 py-1 text-xs text-text-muted transition-colors hover:border-primary hover:text-primary-bright"
        >
          {expanded ? "Less" : "More"}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 border-t border-border pt-4">
          <p className="text-xs leading-relaxed text-text-muted">{insight.finding_full}</p>
          <div className="mt-3 flex items-center gap-4 text-[10px] text-text-dim">
            <span>Chart: {insight.chart_type}</span>
            <span>Data points: {insight.data_points}</span>
            <span>Notebook §{insight.notebook_section}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export function InsightsPage() {
  const [topicFilter, setTopicFilter] = useState<TopicFilter>("all");
  const [tagFilter, setTagFilter] = useState<TagFilter>("all");
  const [minDiff, setMinDiff] = useState(1);
  const [maxDiff, setMaxDiff] = useState(5);

  const insights = insightsData as Insight[];

  const filtered = insights.filter((i) => {
    if (topicFilter !== "all" && i.topic !== topicFilter) return false;
    if (tagFilter !== "all" && i.tag !== tagFilter) return false;
    if (i.difficulty < minDiff || i.difficulty > maxDiff) return false;
    return true;
  });

  const topics = ["all", "temporal", "spatial", "categorical", "relational"] as const;
  const tags = ["all", "distribution", "trend", "comparison", "correlation", "composition", "clustering"] as const;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-text">Insights</h2>
        <p className="mt-1 text-sm text-text-muted">Exploratory Data Analysis findings from the crime warehouse</p>
        <p className="mt-2 rounded-lg bg-bg-muted p-3 text-xs text-text-dim">
          16 insights from real Chicago crime data (2019–2025, 51,996 records)
          across temporal, spatial, categorical, and relational analyses.
          Use filters to narrow by topic, tag, or difficulty.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 rounded-lg border border-border bg-bg-card p-3">
        <div>
          <label className="mb-1 block text-[10px] font-medium uppercase tracking-wider text-text-dim">Topic</label>
          <div className="flex gap-1">
            {topics.map((t) => (
              <button
                key={t}
                onClick={() => setTopicFilter(t)}
                className={`rounded-md px-2 py-1 text-xs transition-colors ${
                  topicFilter === t
                    ? "bg-primary text-white"
                    : "bg-bg-muted text-text-muted hover:text-text"
                }`}
              >
                {t === "all" ? "All" : t}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="mb-1 block text-[10px] font-medium uppercase tracking-wider text-text-dim">Tag</label>
          <select
            value={tagFilter}
            onChange={(e) => setTagFilter(e.target.value as TagFilter)}
            className="rounded-lg border border-border bg-bg-muted px-2 py-1 text-xs text-text outline-none transition-colors focus:border-primary"
          >
            {tags.map((t) => (
              <option key={t} value={t}>
                {t === "all" ? "All tags" : t}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-[10px] font-medium uppercase tracking-wider text-text-dim">Difficulty</label>
          <div className="flex items-center gap-2">
            <select
              value={minDiff}
              onChange={(e) => setMinDiff(Number(e.target.value))}
              className="rounded-lg border border-border bg-bg-muted px-2 py-1 text-xs text-text outline-none focus:border-primary"
            >
              {[1, 2, 3, 4, 5].map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
            <span className="text-xs text-text-dim">to</span>
            <select
              value={maxDiff}
              onChange={(e) => setMaxDiff(Number(e.target.value))}
              className="rounded-lg border border-border bg-bg-muted px-2 py-1 text-xs text-text outline-none focus:border-primary"
            >
              {[1, 2, 3, 4, 5].map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="ml-auto text-xs text-text-dim">
          {filtered.length} of {insights.length} insights
        </div>
      </div>

      {/* Insight Cards */}
      <ErrorBoundary>
        {filtered.length === 0 ? (
          <div className="card py-12 text-center">
            <p className="text-sm text-text-muted">No insights match these filters.</p>
            <p className="mt-1 text-xs text-text-dim">Try broadening your topic or tag selection.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {filtered.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        )}
      </ErrorBoundary>

      {/* Data Notes */}
      <div className="card">
        <h3 className="mb-3 text-sm font-semibold text-text">Data Notes</h3>
        <div className="space-y-2 text-xs text-text-dim">
          <p>
            <strong className="text-text-muted">Source:</strong> All insights are derived from the Chicago Crime Dataset
            (51,996 real reported incidents, 2019–2025) sourced from Kaggle.
          </p>
          <p>
            <strong className="text-text-muted">Methodology:</strong> Analyses follow a Topic × Tag taxonomy with difficulty ratings.
            Each insight includes a chart type, data point count, and notebook section reference.
          </p>
          <p>
            <strong className="text-text-muted">Coverage:</strong> 30 crime types across 7 years, 25 police districts,
            and hundreds of location types. Analyses include arrest rates, temporal patterns, spatial distributions, and cross-dimensional correlations.
          </p>
        </div>
      </div>
    </div>
  );
}
