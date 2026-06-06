import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { KpiCard } from "@/components/charts/KpiCard";

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={new QueryClient()}>
      {children}
    </QueryClientProvider>
  );
}

describe("KpiCard", () => {
  it("renders title and formatted value", () => {
    render(<KpiCard title="Total Crimes" value={57931} />, { wrapper });
    expect(screen.getByText("Total Crimes")).toBeInTheDocument();
    expect(screen.getByText("57,931")).toBeInTheDocument();
  });

  it("formats percent values", () => {
    render(<KpiCard title="Arrest Rate" value={18.0} format="percent" />, {
      wrapper,
    });
    expect(screen.getByText("18.0%")).toBeInTheDocument();
  });
});
