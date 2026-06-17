# M8 — Production Hardening Plan

> **Status:** APPROVED — authored 2026-06-17, the project architect agent.
> **Owner:** SRE (lead), all agents contribute.
> **Duration:** ~1.5 working days.
> **Depends on:** M7 user test sign-off.

---

## 1. Scope

M8 is the final milestone. It hardens the platform for a clean portfolio presentation.

### In Scope
- ✅ Healthcheck verification (all 13 services)
- ✅ Prometheus + Grafana dashboard verification
- ✅ Light mode toggle (dark/light theme switch)
- ✅ About / Data Sources / Methodology page
- ✅ Full assessment run (8-phase pipeline)
- ✅ Critic persona evaluations (8-persona rubric)
- ✅ Security scan (`gitleaks`)
- ✅ README update (screenshots, FAQ)
- ✅ CHANGELOG update (v0.8.0)
- ✅ Architect sign-off

### Out of Scope
- ❌ Auth (JWT/API key) — public dashboard
- ❌ Agentic AI / LLM integration — removed
- ❌ New data pipeline features
- ❌ New API endpoints
- ❌ New dashboard pages (beyond About)

---

## 2. Pre-Conditions

Before M8 begins, verify:

```bash
# M7 gate passed
cat docs/milestones/M7-test.md  # exists and user-confirmed

# M0–M6 regression gate
make lint && make test && make pipeline && make contracts-validate
# All green

# Stack is up
make up && make health
# All 13 services healthy
```

---

## 3. Implementation Steps

### Step 1: SRE Healthcheck Verification

**Agent:** SRE
**Files:** `docker-compose.yaml`, `observability/`

```bash
# 1a. Bring up the full stack
make up

# 1b. Verify all services healthy
make health

# 1c. Verify Prometheus scrapes
curl -s http://localhost:9090/api/v1/targets | python -m json.tool | grep -c "health"

# 1d. Verify Grafana dashboards load
# Open http://localhost:3000 → dashboards → pipeline-health, api-latency
```

**Pass criteria:** All 13 services healthy in < 60s. Prometheus targets all up. Grafana dashboards render.

---

### Step 2: Light Mode Toggle

**Agent:** Frontend
**Files:** `web/src/`

#### 2a. Theme context

Create or update `web/src/context/ThemeContext.tsx`:

```tsx
// ThemeContext.tsx — dark/light mode toggle
import { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'dark' | 'light';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: 'dark',
  toggleTheme: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem('theme');
    return (stored as Theme) || 'dark';
  });

  useEffect(() => {
    document.documentElement.classList.toggle('light', theme === 'light');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => (t === 'dark' ? 'light' : 'dark'));

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
```

#### 2b. Light theme CSS variables

Add to `web/src/index.css`:

```css
/* Light theme overrides */
.light {
  --color-bg-primary: #f8fafc;
  --color-bg-secondary: #ffffff;
  --color-bg-tertiary: #f1f5f9;
  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-text-dim: #64748b;
  --color-border: #e2e8f0;
  --color-card-bg: #ffffff;
  --color-card-border: #e2e8f0;
  --color-accent: #4f46e5;
  --color-accent-hover: #4338ca;
  --color-success: #059669;
  --color-warning: #d97706;
  --color-danger: #dc2626;
}
```

#### 2c. Toggle button

Add a sun/moon toggle to `web/src/components/layout/Header.tsx`:

```tsx
import { useTheme } from '@/context/ThemeContext';
import { Sun, Moon } from 'lucide-react';

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      className="p-2 rounded-lg hover:bg-[var(--color-bg-tertiary)] transition-colors"
    >
      {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
```

#### 2d. Wrap App with ThemeProvider

In `web/src/App.tsx`:

```tsx
import { ThemeProvider } from '@/context/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <AppShell>
        <Router />
      </AppShell>
    </ThemeProvider>
  );
}
```

**Pass criteria:**
- Toggle switches between dark and light
- All pages render correctly in both modes
- No contrast violations (WCAG AA) in either mode
- Preference persists in localStorage

---

### Step 3: About Page

**Agent:** Frontend
**Files:** `web/src/pages/AboutPage.tsx`, `web/src/App.tsx`, `web/src/components/layout/Sidebar.tsx`

#### 3a. Create AboutPage

`web/src/pages/AboutPage.tsx`:

```tsx
export default function AboutPage() {
  return (
    <div className="space-y-8 max-w-4xl">
      <h1 className="text-3xl font-bold">About This Project</h1>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Data Sources</h2>
        <p>
          This platform analyzes the{' '}
          <a href="https://www.kaggle.com/datasets/aliafzal9323/chicago-crime-dataset-2024-2026"
             target="_blank" rel="noopener noreferrer"
             className="text-[var(--color-accent)] underline">
            Chicago Crime Dataset 2024–2026
          </a>{' '}
          from Kaggle. The dataset contains reported crime incidents from the Chicago Police Department.
          For demonstration purposes, the pipeline uses a synthetic 90-day seed dataset (57,931 records)
          that mirrors the statistical properties of the real data.
        </p>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Methodology</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li><strong>Bronze layer:</strong> Raw CSV ingestion into MinIO (S3-compatible object store).</li>
          <li><strong>Silver layer:</strong> PySpark cleaning — snake_case, typed, deduped, validated with Great Expectations.</li>
          <li><strong>Gold layer:</strong> Business aggregates and conformed dimensions in Parquet.</li>
          <li><strong>Warehouse:</strong> PostgreSQL + PostGIS star schema (fact_crime + 4 dimensions).</li>
          <li><strong>Marts:</strong> dbt models for KPI dashboards, hotspot grids, temporal heatmaps, and arrest analytics.</li>
          <li><strong>API:</strong> FastAPI async service with Redis caching, 21 endpoints.</li>
          <li><strong>Frontend:</strong> React SPA with Recharts, ECharts, MapLibre, dark/light themes.</li>
        </ul>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Technology Stack</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {[
            'MinIO', 'Apache Airflow', 'Apache Spark', 'dbt',
            'PostgreSQL + PostGIS', 'Great Expectations', 'FastAPI',
            'React + TypeScript', 'Tailwind CSS', 'Recharts',
            'MapLibre GL', 'Redis', 'Prometheus + Grafana',
          ].map(tech => (
            <span key={tech} className="px-3 py-1.5 rounded-full bg-[var(--color-bg-tertiary)] text-sm text-center">
              {tech}
            </span>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Known Limitations</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li>Synthetic data — not real Chicago crime records.</li>
          <li>Choropleth map uses simplified district boundaries (real GeoJSON deferred).</li>
          <li>No real-time streaming — batch-only pipeline.</li>
          <li>No authentication — public read-only dashboard.</li>
          <li>Forecast and anomaly endpoints exist but are not yet visualized on dedicated pages.</li>
        </ul>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">License</h2>
        <p>MIT License. See <a href="/LICENSE" className="text-[var(--color-accent)] underline">LICENSE</a>.</p>
      </section>
    </div>
  );
}
```

#### 3b. Add route

In `web/src/App.tsx`:

```tsx
import AboutPage from '@/pages/AboutPage';

// Add to routes:
<Route path="/about" element={<AboutPage />} />
```

#### 3c. Add nav item

In `web/src/components/layout/Sidebar.tsx`:

```tsx
{ label: 'About', path: '/about', icon: Info },
```

**Pass criteria:** `/about` renders with all sections. Links work. Responsive layout.

---

### Step 4: Full Assessment Run

**Agent:** QA
**Files:** `docs/assessment/`, `reports/assessment/`

```bash
# 4a. Run the full 8-phase assessment
bash scripts/run_assessment.sh --milestone M8 --full

# 4b. Validate completeness
bash scripts/validate_assessment.sh

# 4c. Check results
cat reports/assessment/summary.md
```

**Pass criteria:**
- No S1 findings
- Overall score ≥ 90% (Grade A)
- Critic composite ≥ 8.0
- All personas ≥ 7.0

---

### Step 5: Critic Persona Evaluations

**Agent:** QA
**Files:** `docs/assessment/rubric.md`, `reports/assessment/evidence/critic-evaluations/`

Evaluate all 8 personas using the 10-point rubric:

| Persona | Weight | Perspective |
|---------|--------|-------------|
| Data Analyst | 25% | "Can I trust the numbers?" |
| Citizen | 15% | "Can I understand this?" |
| Executive | 15% | "30-second insight?" |
| Journalist | 10% | "Can I find stories?" |
| First-Timer | 10% | "Figure out in 2 min?" |
| Policy Maker | 10% | "Defensible for policy?" |
| Community Organizer | 5% | "Can I use this for my community?" |
| News Editor | 10% | "Is this publication-ready?" |

**Pass criteria:** All personas ≥ 7.0, composite ≥ 8.0.

---

### Step 6: Security Scan

**Agent:** Security

```bash
# 6a. Secret scan
gitleaks detect --source . --verbose

# 6b. Dependency audit (if tools available)
# pip audit / npm audit in respective containers
```

**Pass criteria:** No secrets found. No critical vulnerabilities.

---

### Step 7: README Update

**Agent:** Docs
**Files:** `README.md`

Update the README with:
- Final architecture diagram (if changed)
- Screenshot placeholders for dashboard pages
- FAQ section (common questions a reviewer might have)
- Final service URLs table
- "What's next?" section (future enhancements)

---

### Step 8: CHANGELOG Update

**Agent:** Docs
**Files:** `CHANGELOG.md`

Add v0.8.0 entry documenting:
- M7 EDA integration (Insights page, 39 reports)
- M8 Production hardening (light mode, About page, assessment results)
- Final grade and critic scores

---

### Step 9: Architect Sign-Off

**Agent:** Architect

Final review of all DoD items:

```markdown
## Architect Sign-off — M8 Production Hardening

- [x] All agent-owned tests pass
- [x] OpenAPI snapshot updated and diff reviewed
- [x] dbt manifest committed
- [x] README + CHANGELOG updated
- [x] gitleaks scan clean
- [x] Light mode toggle works
- [x] About page renders
- [x] All services healthy
- [x] Assessment: Grade A, no S1 findings
- [x] Critic composite ≥ 8.0

**Verdict:** ✅ APPROVED for portfolio presentation.
```

---

## 4. Post-M8: Known Limitations (Document, Don't Fix)

These are explicitly deferred and documented in the About page:

| Limitation | Reason | Future Work |
|-----------|--------|-------------|
| Synthetic data | Real Kaggle download requires auth | Add Kaggle API key support |
| Simplified map boundaries | Real GeoJSON is large | Add PMTiles with real boundaries |
| No real-time streaming | Batch-only scope | Add Kafka + Spark Structured Streaming |
| No auth | Public portfolio piece | Add JWT via reverse proxy |
| Forecast/anomaly not visualized | API exists, UI deferred | Add dedicated forecast page |
| EDA notebook is static | Pre-computed insights | Add on-demand notebook execution |

---

## 5. Definition of Done (Release-Level)

- [x] All agent-owned tests pass
- [x] OpenAPI snapshot updated and diff reviewed
- [x] dbt manifest committed and dbt docs published
- [x] README + CHANGELOG updated
- [x] `gitleaks` scan clean (no secrets)
- [x] Architect sign-off recorded in PR description
- [x] Light mode toggle works
- [x] About page renders
- [x] All 13 services healthy
- [x] Assessment: Grade A, no S1 findings
- [x] Critic composite ≥ 8.0

---

*End of M8 Production Hardening Plan.*
