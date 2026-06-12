import { useRef, useCallback } from "react";
import { cn } from "@/lib/utils";

type Props = {
  title: string;
  value: number;
  format?: "number" | "percent" | "currency";
  color?: "default" | "red" | "green" | "cyan" | "amber";
  subtitle?: string;
  icon?: React.ReactNode;
  sparklineData?: number[];
  sparklineColor?: string;
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

const sparklineStrokeMap = {
  default: "var(--color-primary)",
  red: "var(--color-accent-rose)",
  green: "var(--color-accent-green)",
  cyan: "var(--color-accent-cyan)",
  amber: "var(--color-accent-amber)",
} as const;

const sparklineFillMap = {
  default: "var(--color-primary)",
  red: "var(--color-accent-rose)",
  green: "var(--color-accent-green)",
  cyan: "var(--color-accent-cyan)",
  amber: "var(--color-accent-amber)",
} as const;

function Sparkline({ data, color = "default" }: { data: number[]; color?: "default" | "red" | "green" | "cyan" | "amber" }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  const handleExport = useCallback(() => {
    const canvas = canvasRef.current;
    const container = chartRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = 400;
    const height = 120;
    canvas.width = width;
    canvas.height = height;

    ctx.fillStyle = "#12121a";
    ctx.fillRect(0, 0, width, height);

    if (data.length < 2) return;

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const padding = 10;

    ctx.beginPath();
    ctx.strokeStyle = sparklineStrokeMap[color];
    ctx.lineWidth = 2;
    ctx.lineJoin = "round";

    const points: [number, number][] = [];
    for (let i = 0; i < data.length; i++) {
      const x = padding + (i / (data.length - 1)) * (width - padding * 2);
      const y = height - padding - ((data[i]! - min) / range) * (height - padding * 2);
      points.push([x, y]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    const link = document.createElement("a");
    link.download = "sparkline.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
  }, [data, color]);

  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const w = 100;
  const h = 32;
  const padding = 2;

  const points = data
    .map((v, i) => {
      const x = padding + (i / (data.length - 1)) * (w - padding * 2);
      const y = h - padding - ((v - min) / range) * (h - padding * 2);
      return `${x},${y}`;
    })
    .join(" ");

  const areaPoints = `${padding},${h - padding} ${points} ${w - padding},${h - padding}`;

  return (
    <div className="relative mt-3" ref={chartRef}>
      <svg viewBox={`0 0 ${w} ${h}`} className="h-8 w-full">
        <polygon
          points={areaPoints}
          fill={sparklineFillMap[color]}
          fillOpacity={0.15}
        />
        <polyline
          points={points}
          fill="none"
          stroke={sparklineStrokeMap[color]}
          strokeWidth={1.5}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      </svg>
      <button
        onClick={handleExport}
        className="absolute -right-1 -top-1 rounded bg-bg-muted p-0.5 text-text-dim opacity-0 transition-opacity hover:text-text group-hover:opacity-100"
        title="Download chart as PNG"
      >
        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
      </button>
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}

export function KpiCard({ title, value, format = "number", color = "default", subtitle, icon, sparklineData }: Props) {
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
      {sparklineData && sparklineData.length > 1 && (
        <Sparkline data={sparklineData} color={color} />
      )}
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
