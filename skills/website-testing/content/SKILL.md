---
name: website-testing
description: |
  First-principles website testing and audit skill. Use for: comprehensive website health checks, pre-launch testing, SEO diagnostics, security header analysis, performance benchmarking, content quality review, SimilarWeb traffic analysis, and generating structured audit reports with prioritized fix recommendations. Triggers on requests like "test this website", "audit my website", "analyze site performance/SEO/security", "generate a website report", or "网站测试/分析/审计报告".
---

# Website Testing Skill

## First-Principles Framework

A website's health reduces to five fundamental questions:

1. **Can users reach it?** (Infrastructure & SSL)
2. **Does it load fast enough?** (Performance)
3. **Can search engines find and rank it?** (SEO)
4. **Is it safe from attacks?** (Security)
5. **Does it deliver value?** (Content Quality)

Every test check maps to one of these root questions. Trace each symptom to its underlying cause before reporting.

---

## Workflow

### Step 1 — Automated Scan

```bash
python /workspace/temp-skills/website-testing/scripts/audit.py <url> --output /tmp/audit_<domain>.json
```

Produces structured JSON across all five dimensions (~30–60 s).

### Step 2 — Browser Verification

Open the site in the browser and visually check:
- Placeholder text (Lorem ipsum, unrelated demo content)
- Broken embeds or iframes (AI widgets, videos, forms)
- Email/contact inconsistencies across pages
- Navigation links returning 403/404
- Mobile layout issues

Save screenshots of critical issues.

### Step 3 — SimilarWeb Analysis (if requested)

Use the `similarweb-analytics` skill for traffic data. For sites under 6 months old, zero data is expected and normal — document this explicitly and advise against paid ads until technical issues are resolved.

### Step 4 — Format Report

```bash
python /workspace/temp-skills/website-testing/scripts/format_report.py /tmp/audit_<domain>.json --output /tmp/audit_report.md
```

Enrich the generated Markdown with browser-observed issues, SimilarWeb data, root-cause analysis, and prioritized fix recommendations.

### Step 5 — Dashboard (optional)

If the user wants an interactive dashboard, build a React + Recharts web app. Key components: animated score rings, radar chart, performance bar charts, SEO/security checklists, and a task board. See `references/dashboard-template.md` for component structure.

---

## Scoring Model

`overall_score = max(0, 100 − deductions)`

| Severity | Deduction | Typical trigger |
|----------|-----------|-----------------|
| CRITICAL | −12 pts | Missing meta description, no H1, missing CSP/HSTS, placeholder content |
| HIGH     | −6 pts  | Missing alt attributes, missing OG tags, missing X-Frame-Options |
| MEDIUM   | −3 pts  | Missing Schema.org, no sitemap, missing robots.txt |
| WARNING  | −1 pt   | Multiple emails found, excess CSS/JS files |

Score labels: 80–100 Good ✅ · 60–79 Needs improvement ⚠️ · 40–59 Poor 🟠 · 0–39 Critical 🔴

---

## Key Benchmarks

| Metric | Benchmark | Common failure cause |
|--------|-----------|----------------------|
| TTFB | < 0.8 s | WordPress without HTML caching |
| Total load | < 3 s | Unoptimized images, too many requests |
| HTML size | < 100 KB | Elementor/Divi inline CSS bloat |
| CSS files | ≤ 10 | Page-builder per-widget stylesheets |
| JS files | ≤ 10 | Plugin proliferation |
| Meta description | Required | Forgotten in CMS setups |
| H1 count | Exactly 1 | Page builders skip semantic HTML |
| Images without alt | 0 | Bulk uploads without metadata |

---

## Root Cause Patterns

**High TTFB on WordPress**: PHP executes DB queries on every uncached request. Fix: install WP Rocket or LiteSpeed Cache, enable full-page HTML caching.

**Oversized HTML (>100 KB)**: Elementor/Divi generate per-element inline CSS. Fix: enable "Improved CSS Loading" + external CSS file mode in the page builder settings.

**Missing security headers**: Default server configs omit them. Fix: add via Cloudflare Dashboard → Transform Rules → Modify Response Headers (no server SSH access needed). See `references/fix-templates.md` for ready-to-paste header values.

**Zero SimilarWeb traffic**: Normal for sites < 3–6 months old. Advise against paid ads until technical issues are resolved — high bounce rate wastes budget.

**Placeholder content**: CMS templates ship with Lorem ipsum. Must be replaced before any SEO or marketing effort begins.

---

## Report Structure

A complete audit report contains:

1. **Executive Summary** — overall score, completion %, top issues
2. **SimilarWeb Traffic** — monthly visits, sources, growth roadmap
3. **Performance** — TTFB, load time, resource counts, root cause
4. **SEO Checklist** — pass/fail per item, priority labels
5. **Security Audit** — header presence, Cloudflare fix snippet
6. **Content Quality** — placeholder detection, broken links, email consistency
7. **Prioritized Fix List** — Urgent (this week) / High (2 weeks) / Medium (ongoing)

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/audit.py <url> [--output path]` | Run all checks, output structured JSON |
| `scripts/format_report.py <json> [--output path]` | Convert JSON → Markdown report |

## References

| File | When to read |
|------|-------------|
| `references/fix-templates.md` | When writing fix recommendations — contains ready-to-use code snippets for Cloudflare headers, WordPress cache config, Schema.org JSON-LD |
| `references/dashboard-template.md` | When building an interactive dashboard — component structure and data mapping guide |
