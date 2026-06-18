import { Routes, Route, Link } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ThemeProvider } from "@/context/ThemeContext";
import { DashboardPage } from "@/pages/DashboardPage";
import { CrimeTypesPage } from "@/pages/CrimeTypesPage";
import { LocationsPage } from "@/pages/LocationsPage";
import { AnalysisPage } from "@/pages/AnalysisPage";
import { InsightsPage } from "@/pages/InsightsPage";
import AboutPage from "@/pages/AboutPage";
import { useUrlSync } from "@/hooks/useUrlSync";

export default function App() {
  useUrlSync();
  return (
    <ThemeProvider>
      <AppShell>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/crime-types" element={<CrimeTypesPage />} />
            <Route path="/locations" element={<LocationsPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/insights" element={<InsightsPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </ErrorBoundary>
      </AppShell>
    </ThemeProvider>
  );
}

function NotFound() {
  return (
    <div className="flex h-full flex-col items-center justify-center p-8 text-center">
      <h1 className="text-6xl font-bold text-text-dim">404</h1>
      <p className="mt-4 text-lg text-text-muted">Page not found</p>
      <p className="mt-2 text-sm text-text-dim">
        The page you're looking for doesn't exist.
      </p>
      <Link
        to="/"
        className="mt-6 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-bright transition-colors"
      >
        Go to Dashboard
      </Link>
    </div>
  );
}
