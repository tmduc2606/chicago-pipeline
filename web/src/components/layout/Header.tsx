import { useFilterStore } from "@/stores/filters";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function Header() {
  const from = useFilterStore((s) => s.from);
  const to = useFilterStore((s) => s.to);
  const types = useFilterStore((s) => s.types);

  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: ({ signal }) => api.health(signal),
    refetchInterval: 30000,
  });

  const { data: filters } = useQuery({
    queryKey: ["filters"],
    queryFn: ({ signal }) => api.filters(signal),
  });

  const activeFilters = [
    from ? `From: ${from}` : null,
    to ? `To: ${to}` : null,
    types?.length ? `${types.length} types` : null,
  ].filter(Boolean);

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-bg-card px-6">
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-semibold text-text">Chicago Crime Dashboard</h1>
      </div>
      <div className="flex items-center gap-3">
        {activeFilters.length > 0 && (
          <div className="flex gap-1.5">
            {activeFilters.map((f) => (
              <span
                key={f}
                className="rounded-full bg-primary/15 px-2.5 py-0.5 text-xs font-medium text-primary-bright"
              >
                {f}
              </span>
            ))}
          </div>
        )}
        {filters?.date_max && (
          <span className="hidden truncate text-xs text-text-dim sm:block">
            Data as of {filters.date_max}
          </span>
        )}
        <div className="flex items-center gap-1.5">
          <span
            className={`h-2 w-2 rounded-full ${
              health?.status === "healthy" ? "bg-accent-green" : "bg-accent-rose"
            }`}
          />
          <span className="text-xs text-text-dim">API</span>
        </div>
      </div>
    </header>
  );
}
