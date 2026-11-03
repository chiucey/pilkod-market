---
name: palantir-bw-dashboard
description: "Build Palantir-inspired interfaces using the exact design language from palantir.com and Palantir product materials. Use whenever the user asks for a Palantir-style UI, intelligence dashboard, data platform site, ontology diagram, bento feature grid, stat showcase, analyst tool, dark ops dashboard, or any interface described as Palantir aesthetic, minimal dark, command center, monochrome data UI, or enterprise data platform. Encodes TWO modes (light marketing + dark ops) and all core patterns including bento grid, entity and ontology cards, stat columns, section numbering, giant display headlines, and line-art illustrations. Always use rather than improvising."
---

# Palantir Design System — Complete Reference

Derived from direct observation of palantir.com, Foundry/AIP product materials, and Gotham platform screenshots. Two canonical modes; all components documented below.

---

## Mode 1: Light — Marketing / Website / Slide Deck

**Background:** `#ffffff`  
**Text:** `#0a0a0a` (near-black, not pure black)  
**Borders:** `#e0e0e0` (thin, 1px)  
**Muted:** `#999999`

Used for: product pages, marketing slides, feature showcases, stat pages, Foundry/ontology diagrams.

## Mode 2: Dark — Ops / Dashboard / AIP Platform

**Background:** `#0d0d0d` or `#111111`  
**Cards:** `#161616` or `#1a1a1a`  
**Text:** `#e8e8e8`  
**Borders:** `#2a2a2a`  
**Muted:** `#555555`

Used for: live dashboards, Gotham/AIP interfaces, bento feature grids, ops rooms.

---

## Typography — Critical

Palantir uses TWO distinct type roles. Getting this right is the most important part.

### Display (Headlines, Product Names, Stats)
```css
/* Observed: very large, bold, geometric sans — NOT monospace */
/* Closest available Google Font substitute: */
font-family: 'DM Sans', sans-serif;

/* Scale */
.display-xl  { font-size: clamp(56px, 10vw, 120px); font-weight: 700; line-height: 1.0; }
.display-lg  { font-size: clamp(36px, 6vw, 72px);   font-weight: 700; line-height: 1.05; }
.stat-number { font-size: clamp(32px, 5vw, 64px);   font-weight: 700; line-height: 1.0; }
```

### Data / UI / Labels (Monospace)
```css
font-family: 'IBM Plex Mono', monospace;   /* UI labels, metadata, table cells */
font-family: 'JetBrains Mono', monospace;  /* numeric readouts, timestamps */

.label   { font-size: 9–10px; letter-spacing: 0.12em; text-transform: uppercase; }
.data    { font-size: 11–12px; }
.caption { font-size: 9px; color: #999; }
```

Google Fonts import:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
```

---

## KEY PATTERN 1 — Section Number Counters (palantir.com)

Fractional section markers `/0.2`, `/0.3`, `/0.4` positioned top-right, muted gray:

```html
<section class="product-section">
  <span class="section-num">/0.2</span>
  <h2 class="display-xl">Gotham</h2>
  <p class="subtitle">Achieve AI-driven combat superiority, from space to mud</p>
</section>
```

```css
.product-section {
  position: relative;
  padding: 80px 40px;
  border-top: 1px solid #e0e0e0;
}

.section-num {
  position: absolute;
  top: 20px; right: 40px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: #bbbbbb;
  letter-spacing: 0.05em;
}
```

---

## KEY PATTERN 2 — Bento Feature Grid (AIP platform)

Variable-size dark cards in a CSS grid. Each card = title (top-left) + abstract line-art.
The gap between cards IS the page background color — creating a "window frame" effect.

```html
<div class="bento-grid">
  <div class="bento-card span-2">
    <span class="card-icon">⚙</span>
    <h3 class="card-title">Secure Access to LLMs</h3>
    <div class="card-pills">
      <span class="pill">Commercial</span>
      <span class="pill">Open Source</span>
      <span class="pill">Fine Tuned</span>
      <span class="pill">Multimodal</span>
    </div>
  </div>
  <div class="bento-card">
    <h3 class="card-title">Vector Management</h3>
    <svg class="card-art" viewBox="0 0 120 60"><!-- line art --></svg>
  </div>
  <div class="bento-card center-card span-2 tall">
    <div class="logo-mark">⬡ AIP°</div>
  </div>
</div>
```

```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-auto-rows: 160px;
  gap: 3px;
  background: #000;   /* gap color = visible black lines */
  padding: 3px;
}

.bento-card {
  background: #161616;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  position: relative;
}

.bento-card.span-2 { grid-column: span 2; }
.bento-card.span-3 { grid-column: span 3; }
.bento-card.tall   { grid-row: span 2; }

.card-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #e8e8e8;
  line-height: 1.3;
  z-index: 1;
}

.card-icon {
  position: absolute;
  top: 14px; right: 14px;
  font-size: 12px;
  color: #444;
}

/* Pills inside bento — ONLY place border-radius is allowed */
.pill {
  display: inline-block;
  border: 1px solid #333;
  color: #888;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  padding: 2px 8px;
  border-radius: 999px;
  letter-spacing: 0.06em;
  margin: 2px 2px 0 0;
}
```

### Bento Line Art Illustrations
All strokes 1px, colors `#333`–`#555`, placed in bottom-right of card:

```html
<!-- Bar chart art -->
<svg class="card-art" viewBox="0 0 120 60" fill="none">
  <line x1="10" y1="55" x2="110" y2="55" stroke="#333" stroke-width="1"/>
  <rect x="15" y="30" width="10" height="25" fill="#333"/>
  <rect x="30" y="20" width="10" height="35" fill="#3a3a3a"/>
  <rect x="45" y="10" width="10" height="45" fill="#444"/>
  <rect x="60" y="22" width="10" height="33" fill="#3a3a3a"/>
  <rect x="75" y="15" width="10" height="40" fill="#444"/>
  <rect x="90" y="35" width="10" height="20" fill="#333"/>
</svg>

<!-- Cube cluster art -->
<svg class="card-art" viewBox="0 0 120 70" fill="none" stroke="#333" stroke-width="1">
  <polygon points="30,20 50,10 70,20 50,30"/>
  <polygon points="30,20 50,30 50,50 30,40"/>
  <polygon points="50,30 70,20 70,40 50,50"/>
  <polygon points="65,30 85,20 105,30 85,40" stroke="#3a3a3a"/>
  <polygon points="65,30 85,40 85,60 65,50" stroke="#3a3a3a"/>
</svg>

<!-- Node graph art -->
<svg class="card-art" viewBox="0 0 120 70" fill="none">
  <circle cx="60" cy="35" r="8" stroke="#555" stroke-width="1"/>
  <circle cx="25" cy="20" r="5" stroke="#444" stroke-width="1"/>
  <circle cx="95" cy="20" r="5" stroke="#444" stroke-width="1"/>
  <circle cx="25" cy="50" r="5" stroke="#444" stroke-width="1"/>
  <circle cx="95" cy="50" r="5" stroke="#444" stroke-width="1"/>
  <line x1="52" y1="30" x2="30" y2="22" stroke="#333" stroke-width="1"/>
  <line x1="68" y1="30" x2="90" y2="22" stroke="#333" stroke-width="1"/>
  <line x1="52" y1="40" x2="30" y2="48" stroke="#333" stroke-width="1"/>
  <line x1="68" y1="40" x2="90" y2="48" stroke="#333" stroke-width="1"/>
</svg>
```

---

## KEY PATTERN 3 — Stat Column Layout (Foundry slide)

Three columns, large bold numbers, thin horizontal rules, client name as column header:

```html
<div class="stat-page">
  <div class="breadcrumb-pill">What We Do <span>→</span> Outcomes At Scale</div>

  <h2 class="display-lg">
    Foundry harnesses operational complexity —
    to drive <span class="underline-em">scaled outcomes</span>
  </h2>

  <div class="stat-cols">
    <div class="stat-col">
      <span class="col-name">Airbus</span>
      <hr class="rule"/>
      <div class="big-num">$850M</div>
      <p class="num-desc">Yearly revenue opportunity created by Skywise<br><em>(third-party estimate)</em></p>
      <hr class="rule"/>
      <div class="stat-row"><b>25k+</b><span>Users on Skywise, Airbus's Foundry instance</span></div>
      <hr class="rule"/>
      <div class="stat-row"><b>33%</b><span>Improvement in A350 airplane production</span></div>
    </div>
    <!-- repeat cols -->
  </div>
</div>
```

```css
.breadcrumb-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid #ccc;
  border-radius: 999px;
  padding: 4px 14px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: #555;
  margin-bottom: 32px;
}

.underline-em {
  text-decoration: underline;
  text-underline-offset: 6px;
  text-decoration-thickness: 2px;
}

.stat-cols {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border-top: 1px solid #e0e0e0;
}

.stat-col {
  padding: 24px 32px 24px 0;
  border-right: 1px solid #e0e0e0;
}
.stat-col:last-child { border-right: none; }

.col-name { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #555; }

.rule { border: none; border-top: 1px solid #e0e0e0; margin: 12px 0; }

.big-num {
  font-family: 'DM Sans', sans-serif;
  font-size: clamp(40px, 6vw, 80px);
  font-weight: 700;
  line-height: 1.0;
  color: #0a0a0a;
}

.num-desc { font-size: 12px; color: #555; margin-top: 6px; line-height: 1.5; }

.stat-row { display: flex; gap: 16px; align-items: baseline; }
.stat-row b { font-family: 'DM Sans', sans-serif; font-size: 22px; font-weight: 700; color: #0a0a0a; white-space: nowrap; }
.stat-row span { font-size: 12px; color: #555; line-height: 1.4; }
```

---

## KEY PATTERN 4 — Ontology Entity Cards (Foundry diagram)

Object cards connected by labeled arrows. Light bg, thin border, monospace text:

```html
<!-- Positioned absolutely or via SVG foreignObject -->
<div class="obj-card">
  <div class="obj-row"><span class="ok">Object Type:</span> <b>Airport</b></div>
  <div class="obj-row"><span class="ok">Object:</span> JFK</div>
  <div class="obj-row"><span class="ok">Properties:</span> Opening Date, Operating Capacity, Lat./Long.</div>
</div>
```

```css
.obj-card {
  border: 1px solid #cccccc;
  background: #f7f7f7;
  padding: 10px 12px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: #333;
  border-radius: 4px;
  min-width: 175px;
  line-height: 1.5;
}
.ok { color: #999; }
.obj-card b { color: #000; font-weight: 500; }
```

SVG arrows with relationship labels:
```html
<svg>
  <defs>
    <marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L7,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
  <line x1="300" y1="180" x2="300" y2="120" stroke="#888" stroke-width="1" marker-end="url(#ah)"/>
  <text x="308" y="155" font-family="'IBM Plex Mono'" font-size="10" fill="#555">Arrived To</text>
</svg>
```

---

## KEY PATTERN 5 — Product Section List (palantir.com)

```html
<div class="products">
  <div class="product-item">
    <span class="p-num">/0.2</span>
    <h2 class="p-name">Gotham</h2>
    <p class="p-desc">Achieve AI-driven combat superiority, from space to mud</p>
  </div>
</div>
```

```css
.product-item {
  position: relative;
  padding: 48px 32px 64px;
  border-bottom: 1px solid #e8e8e8;
}

.p-num {
  position: absolute;
  top: 20px; right: 32px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: #cccccc;
}

.p-name {
  font-family: 'DM Sans', sans-serif;
  font-size: clamp(52px, 14vw, 96px);
  font-weight: 700;
  line-height: 1.0;
  color: #0a0a0a;
  margin-bottom: 16px;
}

.p-desc {
  font-size: 16px;
  color: #333;
  max-width: 480px;
  line-height: 1.5;
}
```

---

## CTA Button (sharp corners — NOT rounded)

```css
.cta {
  border: 1px solid #0a0a0a;
  background: transparent;
  color: #0a0a0a;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 8px 20px;
  cursor: pointer;
  border-radius: 0;
  transition: background 0.15s, color 0.15s;
}
.cta:hover { background: #0a0a0a; color: #fff; }
.cta.filled { background: #0a0a0a; color: #fff; }
```

---

## Ops Dashboard Quick Reference (Dark mode)

| Component | Spec |
|-----------|------|
| Background | `#0d0d0d` |
| Cards | `#161616`, `border: 1px solid #2a2a2a` |
| Display font | `IBM Plex Mono` (monospace throughout — no DM Sans) |
| Active state | `#ffffff` border-left or fill |
| Severity | white=critical, `#888`=high, `#555`=med, `#2a2a2a`=low |
| Top bar | 32px height, `border-bottom: 1px solid #222` |
| Entity list | `border-left: 2px solid #fff` when active |
| Metric numbers | `JetBrains Mono`, `font-weight: 300`, 20–24px |
| Graph background | dot-grid: `radial-gradient(#1a1a1a 1px, transparent 1px) 28px 28px` |
| Timeline "now" | `width:1px; background:#fff` |
| Scrollbar | `width:3px`, thumb `#222` |
| Live clock | UTC, always visible, `IBM Plex Mono` 10px |

---

## Anti-patterns

- ❌ No color anywhere in either mode — pure grayscale only
- ❌ No rounded cards in ops/dark mode (only pills inside bento)
- ❌ No box-shadows or elevation
- ❌ Never use Inter, Roboto, system-ui for display text
- ❌ No gradient backgrounds
- ❌ Bento art: strokes only, `#333–#555`, never filled shapes
- ❌ Section counters must be `/0.x` format — not `01`, not `1.`
- ❌ No animations on data; only entry fade + live-dot pulse

---

## Checklist

**Light mode:**
- [ ] DM Sans for all display headlines
- [ ] IBM Plex Mono for all labels, captions, metadata
- [ ] Section /0.x counters top-right of each section
- [ ] Underline on key phrase in main headline
- [ ] Breadcrumb pill — oval, 1px border, monospace
- [ ] Stat columns with thin `<hr>` rules
- [ ] CTA button: sharp corners, 1px black border

**Dark bento section:**
- [ ] Background `#0d0d0d`, cards `#161616`
- [ ] 3px black gap between cards
- [ ] Variable-span grid (span-2, tall)
- [ ] Abstract SVG stroke-only line art in each card
- [ ] Pills only rounded element

**Ops dashboard:**
- [ ] Pure black `#000–#0d0d0d` base
- [ ] White = selected/critical only
- [ ] Monospace throughout
- [ ] Dot-grid graph canvas
- [ ] Live UTC clock
- [ ] Entity active = white left-border
