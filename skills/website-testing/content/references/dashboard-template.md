# Dashboard Template Reference

Guide for building an interactive audit dashboard using React + Recharts.

---

## Component Architecture

```
Home.tsx (layout)
├── Sidebar.tsx         — collapsible nav, section links, live status dot
├── TopBar.tsx          — section title, quote ticker, issue count pills, clock
└── sections/
    ├── Overview.tsx    — hero score ring, 4 dimension rings, radar chart, KPI list, tech stack
    ├── Performance.tsx — summary cards, horizontal bar chart, resource progress bars, root cause cards
    ├── SEO.tsx         — score ring, pass/fail checklist, first-principles insights
    ├── Security.tsx    — score ring, header checklist, Cloudflare fix code block
    ├── Content.tsx     — issue cards, multi-dimension bar chart, detail list
    ├── Traffic.tsx     — area chart (monthly visits), source breakdown, growth roadmap
    └── Tasks.tsx       — progress bar, filter bar, expandable task cards with toggle
```

---

## Data File Structure (dashboardData.ts)

```typescript
// Score data
export const overallScore: number           // 0-100
export const radarScores: RadarEntry[]      // [{subject, score, fullMark}]

// Performance
export const performanceMetrics: Metric[]   // [{name, value, benchmark, unit, status}]
export const resourceMetrics: Metric[]

// SEO
export const seoChecks: Check[]             // [{item, status, detail, priority}]

// Security
export const securityChecks: Check[]        // [{item, status, detail, risk}]

// Content
export const contentIssues: Issue[]         // [{id, title, page, severity, status, category, description}]

// Traffic
export const trafficData: TrafficPoint[]    // [{month, visits}]
export const trafficSources: Source[]       // [{name, value, color}]

// Tasks
export const optimizationTasks: Task[]      // [{id, title, description, priority, category, status, effort, impact}]
```

---

## Design System (War Room Dark Theme)

```css
/* Background layers */
--background: oklch(0.09 0.008 240)   /* deep dark blue-black */
--card:       oklch(0.12 0.010 240)   /* slightly lighter card */
--secondary:  oklch(0.16 0.012 240)   /* hover states */

/* Accent colors */
--war-red:   #C0392B   /* critical issues, primary accent */
--steel-blue: #2E86C1  /* info, security */
--gold:      #F39C12   /* warnings, SEO */
--success:   #27AE60   /* passing checks */

/* Typography */
font-family: 'Space Grotesk' (headings), 'Noto Sans SC' (body), 'JetBrains Mono' (data)
```

Key CSS patterns:
- `.war-card` — dark gradient card with red top-edge glow line
- `.scanline` — subtle CRT scanline overlay on sidebar
- `.pulse-dot` — animated status indicator
- `.fill-bar` — CSS animation for progress bar fill
- `.nav-item-active` — left red border + gradient background

---

## Animated Score Ring Pattern

```tsx
function ScoreRing({ score, color }: { score: number; color: string }) {
  const animated = useCountUp(score);  // custom hook: counts 0→target
  const circumference = 2 * Math.PI * 36;
  const offset = circumference - (animated / 100) * circumference;
  return (
    <svg viewBox="0 0 80 80" className="-rotate-90">
      <circle cx="40" cy="40" r="36" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6" />
      <circle cx="40" cy="40" r="36" fill="none" stroke={color} strokeWidth="6"
        strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
        style={{ transition: "stroke-dashoffset 0.1s linear" }} />
    </svg>
  );
}
```

---

## Task Board Toggle Pattern

Tasks are stored in local state. Clicking the circle icon toggles `status: "open" | "done"`.
Progress bar updates reactively: `pct = (done / total) * 100`.
Filter bar uses `priority: "urgent" | "high" | "medium" | "all"`.
