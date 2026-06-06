import { useFilterStore } from "@/stores/filters";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { titleCase } from "@/lib/utils";

const QUICK_PERIODS = [
  { label: "All time", days: 0 },
  { label: "90 days", days: 90 },
  { label: "30 days", days: 30 },
  { label: "7 days", days: 7 },
] as const;

function toDateString(date: Date) {
  return date.toISOString().slice(0, 10);
}

export function SidebarFilters() {
  const { from, to, types, setFrom, setTo, setTypes, reset } = useFilterStore();
  const { data: filters } = useQuery({
    queryKey: ["filters"],
    queryFn: ({ signal }) => api.filters(signal),
  });

  const handleQuickPeriod = (days: number) => {
    if (days === 0) {
      setFrom(null);
      setTo(null);
    } else {
      const end = new Date(filters?.date_max ?? Date.now());
      const start = new Date(end);
      start.setDate(start.getDate() - days);
      setFrom(toDateString(start));
      setTo(toDateString(end));
    }
  };

  return (
    <div className="border-t border-border p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted">
          Filters
        </h3>
        <button
          onClick={reset}
          className="rounded px-2 py-0.5 text-xs text-text-dim transition-colors hover:bg-bg-hover hover:text-primary-bright"
        >
          Reset
        </button>
      </div>

      <div className="space-y-3">
        {/* Date From */}
        <div>
          <label className="mb-1 block text-[10px] font-medium uppercase tracking-wider text-text-dim">
            From
          </label>
          <input
            type="date"
            value={from ?? ""}
            min={filters?.date_min}
            max={filters?.date_max}
            onChange={(e) => setFrom(e.target.value || null)}
            className="w-full rounded-lg border border-border bg-bg-muted px-3 py-1.5 text-xs text-text outline-none transition-colors focus:border-primary"
          />
        </div>

        {/* Date To */}
        <div>
          <label className="mb-1 block text-[10px] font-medium uppercase tracking-wider text-text-dim">
            To
          </label>
          <input
            type="date"
            value={to ?? ""}
            min={filters?.date_min}
            max={filters?.date_max}
            onChange={(e) => setTo(e.target.value || null)}
            className="w-full rounded-lg border border-border bg-bg-muted px-3 py-1.5 text-xs text-text outline-none transition-colors focus:border-primary"
          />
        </div>

        {/* Quick period select */}
        <div>
          <label className="mb-1 block text-[10px] font-medium uppercase tracking-wider text-text-dim">
            Quick Select
          </label>
          <div className="flex flex-wrap gap-1.5">
            {QUICK_PERIODS.map((p) => (
              <button
                key={p.days}
                onClick={() => handleQuickPeriod(p.days)}
                className="rounded-md border border-border bg-bg-muted px-2.5 py-1 text-xs text-text-muted transition-colors hover:border-primary hover:text-primary-bright"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Crime Types */}
        <div>
          <label className="mb-1 block text-[10px] font-medium uppercase tracking-wider text-text-dim">
            Crime Types {types?.length ? `(${types.length})` : ""}
          </label>
          <div className="max-h-40 overflow-auto rounded-lg border border-border bg-bg-muted p-2">
            {filters?.primary_types.map((t) => (
              <label
                key={t}
                className="flex cursor-pointer items-center gap-2 rounded px-2 py-1 text-xs transition-colors hover:bg-bg-hover"
              >
                <input
                  type="checkbox"
                  checked={types?.includes(t) ?? false}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setTypes([...(types ?? []), t]);
                    } else {
                      setTypes((types ?? []).filter((x) => x !== t));
                    }
                  }}
                  className="h-3 w-3 rounded border-border-bright accent-primary"
                />
                <span className="text-text-muted">{titleCase(t)}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
