import { useFilterStore } from "@/stores/filters";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useTheme } from "@/context/ThemeContext";

export function Header() {
  const from = useFilterStore((s) => s.from);
  const to = useFilterStore((s) => s.to);
  const types = useFilterStore((s) => s.types);
  const { theme, toggleTheme } = useTheme();

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
        <button
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-bg-hover hover:text-text"
        >
          {theme === "dark" ? (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
            </svg>
          ) : (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
            </svg>
          )}
        </button>
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
