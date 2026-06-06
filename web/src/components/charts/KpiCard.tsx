import { cn } from "@/lib/utils";

type Props = {
  title: string;
  value: number;
  format?: "number" | "percent" | "currency";
  color?: "default" | "red" | "green" | "cyan" | "amber";
  subtitle?: string;
  icon?: React.ReactNode;
};

function formatValue(value: number, format: Props["format"]): string {
  switch (format) {
    case "percent":
      return `${value.toFixed(1)}%`;
    case "currency":
      return `$${value.toLocaleString()}`;
    default:
      return value.toLocaleString();
  }
}

const colorMap = {
  default: "text-text",
  red: "text-accent-rose",
  green: "text-accent-green",
  cyan: "text-accent-cyan",
  amber: "text-accent-amber",
} as const;

const iconBgMap = {
  default: "bg-primary/10 text-primary",
  red: "bg-accent-rose/10 text-accent-rose",
  green: "bg-accent-green/10 text-accent-green",
  cyan: "bg-accent-cyan/10 text-accent-cyan",
  amber: "bg-accent-amber/10 text-accent-amber",
} as const;

export function KpiCard({ title, value, format = "number", color = "default", subtitle, icon }: Props) {
  return (
    <div className="kpi-glow group rounded-xl border border-border bg-bg-card p-5 transition-all duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
            {title}
          </p>
          <p className={cn("mt-2 text-3xl font-bold tracking-tight", colorMap[color])}>
            {formatValue(value, format)}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs text-text-dim">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg", iconBgMap[color])}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

export function KpiSkeleton() {
  return (
    <div className="kpi-glow rounded-xl border border-border bg-bg-card p-5">
      <div className="shimmer h-3 w-24 rounded" />
      <div className="shimmer mt-3 h-8 w-20 rounded" />
    </div>
  );
}
