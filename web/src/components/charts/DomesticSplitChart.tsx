import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { HelpTooltip } from "@/components/ui/HelpTooltip";

export function DomesticSplitChart() {
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data, isLoading, error } = useQuery({
    queryKey: ["domestic", params.toString()],
    queryFn: ({ signal }) => api.domesticSplit(params, signal),
  });

  if (isLoading || !data) {
    return (
      <div className="card">
        <div className="mb-4 shimmer h-4 w-40 rounded" />
        <div className="flex items-center gap-4">
          <div className="shimmer h-32 w-32 rounded-full" />
          <div className="space-y-3">
            <div className="shimmer h-4 w-32 rounded" />
            <div className="shimmer h-4 w-36 rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-text">Domestic vs Non-Domestic</h3>
        <div className="flex h-[160px] items-center justify-center rounded-lg bg-bg-muted">
          <p className="text-sm text-text-dim">Failed to load domestic data</p>
        </div>
      </div>
    );
  }

  const total = data.true_count + data.false_count;
  const domesticPct = total > 0 ? (data.true_count / total) * 100 : 0;
  const nonDomesticPct = 100 - domesticPct;

  return (
    <div className="card">
      <div className="mb-4 flex items-center">
        <h3 className="text-sm font-semibold text-text">Domestic vs Non-Domestic</h3>
        <HelpTooltip content="Crimes are classified as domestic when they involve family or household members. This metric helps identify patterns in interpersonal violence." />
      </div>
      <div className="flex items-center gap-6">
        {/* Donut chart */}
        <div className="relative h-36 w-36 flex-shrink-0">
          <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
            <circle cx="18" cy="18" r="16" fill="none" stroke="#2a2a3d" strokeWidth="3" />
            <circle
              cx="18"
              cy="18"
              r="16"
              fill="none"
              stroke="#fb7185"
              strokeWidth="3"
              strokeDasharray={`${domesticPct} ${100 - domesticPct}`}
              strokeDashoffset="25"
              strokeLinecap="round"
              className="transition-all duration-700"
            />
            <circle
              cx="18"
              cy="18"
              r="16"
              fill="none"
              stroke="#6366f1"
              strokeWidth="3"
              strokeDasharray={`${nonDomesticPct} ${domesticPct}`}
              strokeDashoffset={`${25 - domesticPct}`}
              strokeLinecap="round"
              className="transition-all duration-700"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xl font-bold text-text">{domesticPct.toFixed(1)}%</span>
          </div>
        </div>
        {/* Legend */}
        <div className="space-y-3 text-sm">
          <div className="flex items-center gap-3">
            <span className="h-3 w-3 rounded-full bg-accent-rose" />
            <div>
              <div className="font-medium text-text">Domestic</div>
              <div className="text-xs text-text-muted">{data.true_count.toLocaleString()}</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="h-3 w-3 rounded-full bg-primary" />
            <div>
              <div className="font-medium text-text">Non-Domestic</div>
              <div className="text-xs text-text-muted">{data.false_count.toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
