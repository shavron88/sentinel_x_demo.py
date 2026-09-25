# Sentinel-X Dashboard Redesign Plan
## Elevating Dashboard UI to Match Landing Page "Superb" Quality

---

## Executive Summary

The landing page (`dashboard/templates/landing.html`) represents a **superb, production-grade design system** with sophisticated visual language, custom effects, and cohesive component architecture. The current dashboard (`dashboard/templates/index.html` + associated CSS) uses a **different, less refined design token system** (`--ev-*` vs landing page's semantic tokens) and lacks the visual polish, animations, and component patterns that make the landing page exceptional.

This plan provides a comprehensive roadmap to redesign the dashboard to match the landing page's quality while preserving all existing functionality.

---

## 1. Design Token Unification

### 1.1 Adopt Landing Page's Semantic Token System

**Current (Dashboard)**: `--ev-bg`, `--ev-surface`, `--ev-primary`, `--ev-border-subtle`, etc.
**Target (Landing Page)**: `--bg`, `--bg-raised`, `--bg-alt`, `--card`, `--border`, `--border-hi`, `--accent`, `--accent-soft`, `--accent-line`, `--mint`, `--amber`, `--danger`, `--grad-text`, `--hero-glow-1`, `--hero-glow-2`, `--grid-line`, `--stage-shadow`, `--btn-glow`, `--btn-glow-hover`

### 1.2 Token Migration Strategy

| Landing Page Token | Dashboard Equivalent | Action |
|---|---|---|
| `--bg` | `--ev-bg` | Rename/unify |
| `--bg-raised` | `--ev-surface-2` | Map |
| `--bg-alt` | `--ev-surface-3` | Map |
| `--card` | `--ev-surface` | Map |
| `--border` | `--ev-border` | Map |
| `--border-hi` | `--ev-border-strong` | Map |
| `--accent` | `--ev-primary` | Map |
| `--accent-soft` | `--ev-primary-soft` | Map |
| `--accent-line` | `--ev-border` (adjusted) | Create new |
| `--mint` | `--ev-success` | Map |
| `--amber` | `--ev-warning` | Map |
| `--danger` | `--ev-danger` | Map |
| `--grad-text` | *New* | Add gradient text token |
| `--hero-glow-1` | *New* | Add atmospheric glow |
| `--hero-glow-2` | *New* | Add secondary glow |
| `--grid-line` | *New* | Add subtle grid pattern |
| `--stage-shadow` | *New* | Add stage/window shadow |
| `--btn-glow` | *New* | Add button glow shadow |
| `--btn-glow-hover` | *New* | Add button hover glow |
| `--mono` | `--ev-font-mono` | Unify (JetBrains Mono) |
| `--sans` | `--ev-font` | Unify (Inter) |

### 1.3 Theme Support
- Keep `[data-theme="light"]` and `[data-theme="dark"]` / `[data-theme="midnight"]` support
- Ensure all new tokens have light/dark variants
- Landing page uses `[data-theme="light"]` override - maintain this pattern

---

## 2. Visual Effects & Atmosphere (Critical for "Superb" Quality)

### 2.1 Custom Scrollbar
```css
/* Landing page has: */
html { scrollbar-width: thin; scrollbar-color: var(--accent) transparent; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { 
  background: linear-gradient(180deg, var(--accent), #4169e6); 
  border-radius: 100px; 
  border: 2px solid var(--bg); 
  background-clip: padding-box; 
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #7ea3ff, var(--accent)); }
```

### 2.2 Scroll Progress Bar
```css
.scroll-progress { 
  position: fixed; top: 0; left: 0; height: 3px; width: 0%; z-index: 999;
  background: linear-gradient(90deg, var(--mint), var(--accent));
  box-shadow: 0 0 8px var(--accent-line);
  transition: width .05s linear;
}
```

### 2.3 Custom Cursor (Desktop Only)
```css
.cursor-dot, .cursor-ring { 
  position: fixed; top: 0; left: 0; pointer-events: none; z-index: 998; 
  border-radius: 50%; transform: translate(-50%,-50%); 
}
.cursor-dot { width: 6px; height: 6px; background: var(--accent); opacity: 0; }
.cursor-ring { width: 34px; height: 34px; border: 1px solid var(--accent-line); opacity: 0; }
.cursor-ring.hover { width: 52px; height: 52px; border-color: var(--accent); background: var(--accent-soft); }
body.cursor-active .cursor-dot, body.cursor-active .cursor-ring { opacity: 1; }
@media (hover: none), (prefers-reduced-motion: reduce) { .cursor-dot, .cursor-ring { display: none; } }
```

### 2.4 Hero/Atmospheric Glows
- Add `--hero-glow-1` and `--hero-glow-2` radial gradients for page-level atmosphere
- Apply to dashboard hero sections (KPI bar area, main content top)

### 2.5 Grid Line Overlay
```css
/* Subtle grid pattern for depth */
.hero-grid-lines {
  position: absolute; inset: 0;
  background-image: linear-gradient(var(--grid-line) 1px, transparent 1px), 
                    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(1200px 600px at 50% 0%, black, transparent 75%);
  pointer-events: none;
}
```

### 2.6 Scanline Animation (for live feed areas)
```css
.scanline {
  position: absolute; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--mint), transparent);
  opacity: 0.5; animation: scan 4s linear infinite;
}
@keyframes scan { 0% { top: 0%; } 100% { top: 100%; } }
```

---

## 3. Typography System Overhaul

### 3.1 Adopt Landing Page Type Scale
```css
/* Landing page uses: */
--mono: 'JetBrains Mono', ui-monospace, monospace;
--sans: 'Inter', -apple-system, sans-serif;

/* Font sizes from landing page: */
.mlabel { font-size: 12.5px; }           /* Micro labels */
.section-title { font-size: 34px; font-weight: 800; letter-spacing: -0.02em; }
.section-sub { font-size: 16px; }
h1.headline { font-size: clamp(36px, 5.4vw, 66px); line-height: 1.08; font-weight: 800; letter-spacing: -0.03em; }
.hero-copy { font-size: 18px; }
.cap-title { font-size: 14.5px; font-weight: 600; }
.cap-desc { font-size: 13px; }
.stat-box .v { font-size: 19px; font-weight: 700; font-family: var(--mono); }
```

### 3.2 Dashboard-Specific Adjustments
- KPI values: Increase to 36px (match landing page headline scale)
- Panel titles: 16px, weight 600 (match `.section-title` at smaller size)
- Micro-labels: Add `.mlabel` component (12.5px, mono, accent color)
- Data values: Use JetBrains Mono for tabular numbers

### 3.3 Gradient Text Utility
```css
.grad-text { 
  background: var(--grad-text); 
  -webkit-background-clip: text; 
  background-clip: text; 
  color: transparent; 
}
```

---

## 4. Component Library Alignment

### 4.1 Button System (`.btn` family)

**Landing Page Buttons:**
- `.btn` base: 38px height, 9px radius, 14px, weight 600
- `.btn-primary`: Gradient background, shine animation (`::after`), glow shadow
- `.btn-ghost`: Transparent, border, hover raises background
- `.btn-lg`: 50px height, 11px radius, 15.5px

**Dashboard Buttons:** Need shine effect, glow shadows, consistent sizing

### 4.2 Card System (`.panel` / `.card`)

**Landing Page Cards (`.cap-card`):**
```css
.cap-card {
  background: var(--card);
  padding: 26px 22px;
  transition: background .15s ease, transform .2s ease;
  transform-style: preserve-3d;
}
.cap-card::before {
  content: ''; position: absolute; inset: 0; opacity: 0;
  background: radial-gradient(220px 220px at var(--cx,50%) var(--cy,50%), var(--accent-soft), transparent 70%);
  transition: opacity .25s ease;
}
.cap-card:hover::before { opacity: 1; }
.cap-card:hover { background: var(--bg-raised); }
.cap-card:hover .cap-scan { opacity: 1; }
.cap-scan { position: absolute; left: 0; right: 0; top: 0; height: 1px; background: linear-gradient(90deg, transparent, var(--mint), transparent); opacity: 0; }
```

**Dashboard Panels:** Add radial gradient hover glow, scanline top border, 3D transform

### 4.3 KPI Cards (`.kpi-card`)

**Current Dashboard:** Left border accent, basic hover lift
**Landing Page Pattern:** 
- Use `.mlabel` for labels (mono, accent)
- Value: Large, mono, gradient text option
- Indicator: Pill with colored dot + text
- Hover: Subtle lift + glow (not heavy transform)

### 4.4 Stage/Window Component (`.stage`)

**Landing Page:** `.stage` with `.stage-bar` (window controls), `.cam-view`, `.stage-footer`
- Window dots (red/yellow/green)
- Title in mono
- Live indicator with pulsing dot
- HUD overlays with corner brackets
- Detection boxes with animated entrance

**Dashboard Application:** Use for camera feeds, preview windows, modal-like panels

### 4.5 Pipeline Strip (`.pipeline-strip`)

**Landing Page:** Horizontal scrollable steps with circles, labels, arrows
- `.pipe-step` with `.pipe-circle` (52px), `.pipe-label` (mono)
- `.pipe-arrow` connectors
- Scroll-snap for smooth navigation

**Dashboard Application:** AI processing pipeline, incident workflow, camera setup steps

### 4.6 Log Panel (`.log-panel`)

**Landing Page:** Terminal aesthetic with `.log-header` (window dots), `.log-body` (grid), `.log-row` with checkmarks
- Two-column grid on desktop
- Mono font throughout
- Green checkmarks for success states

**Dashboard Application:** System status, AI engine logs, audit trails

### 4.7 Evidence Flow (`.evidence-flow`)

**Landing Page:** `.ev-node` with `.ev-circle` (54px), `.ev-label` (mono), `.ev-arrow` connectors

**Dashboard Application:** Incident → Alert → Evidence → Review flow visualization

### 4.8 Tech Strip / Chips (`.tech-strip`, `.tech-chip`)

**Landing Page:** Pill-shaped chips with icon, name, role
- `.tech-chip .ic` (26px circle, accent-soft bg)
- `.tech-chip .name` (weight 600)
- `.tech-chip .role` (mono, faint)

**Dashboard Application:** Technology stack, AI models, integrations

### 4.9 Micro-Label (`.mlabel`)

**Landing Page:** Replaces repeated eyebrow pills
```css
.mlabel { 
  font-family: var(--mono); 
  font-size: 12.5px; 
  color: var(--accent); 
  margin-bottom: 14px; 
  display: flex; 
  align-items: center; 
  gap: 8px; 
}
.mlabel .n { color: var(--faint); }
```

**Dashboard Application:** Section eyebrows, category labels, status prefixes

---

## 5. Layout & Spacing System

### 5.1 Landing Page Spacing
- Section padding: `104px 0` (desktop)
- Container: `max-width: 1220px`, padding `0 32px`
- Component gaps: 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px

### 5.2 Dashboard Adjustments
- Reduce section padding to `64px 0` (more content-dense for dashboard)
- Container max-width: `1400px` (wider for data density)
- Maintain 8px base unit scaling

### 5.3 Border Radius System
| Size | Landing Page | Dashboard Target |
|------|-------------|------------------|
| Small | 9px | 9px |
| Medium | 11px | 11px |
| Large | 14px | 14px |
| XL | 20px | 20px |
| Full | 100px | 100px |

---

## 6. Animation & Motion System

### 6.1 Entrance Animations (`.reveal`, `.stagger`)
```css
.reveal { opacity: 0; transform: translateY(18px); transition: opacity .6s ease, transform .6s ease; }
.reveal.in-view { opacity: 1; transform: translateY(0); }

.stagger > * { opacity: 0; transform: translateY(14px); transition: opacity .5s ease, transform .5s ease; }
.stagger.in-view > * { opacity: 1; transform: translateY(0); }
.stagger.in-view > *:nth-child(1) { transition-delay: .02s; }
/* ... up to 12 children */
```

### 6.2 Hero Entrance (`@keyframes heroIn`)
```css
@keyframes heroIn { from { opacity: 0; transform: translateY(22px); } to { opacity: 1; transform: translateY(0); } }
```

### 6.3 Detection/Item Entrance (`@keyframes detectIn`)
```css
@keyframes detectIn { from { opacity: 0; transform: scale(1.04); } to { opacity: 1; transform: scale(1); } }
```

### 6.4 Count-Up Animation (`.count`)
- Use `font-variant-numeric: tabular-nums` for stable width
- JavaScript-driven count-up for KPI values

### 6.5 Marquee (`.tech-marquee`)
```css
.tech-marquee { overflow: hidden; mask-image: linear-gradient(90deg, transparent, black 6%, black 94%, transparent); }
.tech-track { display: flex; gap: 12px; width: max-content; animation: marquee 26s linear infinite; }
@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
```

### 6.6 Sheen/Sweep Effects
- `.app-image-wrap::after` - diagonal shine on hover
- `.preview-mockup::before` - horizontal sweep
- `.hero-cta::before` - pulsing radial glow

---

## 7. Page-Specific Redesign Plan

### 7.1 Dashboard Home (`/dashboard` / `index.html`)

#### Current Structure:
1. KPI Bar (4 cards)
2. Live Cameras Link Section
3. Monitoring Grid (Evidence Gallery + AI Live Feed + AI Status + AI Intelligence)
4. Demo Scenarios
5. Bottom Grid (Camera Controls + Security Map)
6. AI Performance Panel
7. Detection History Chart

#### Redesign Target:

**Hero/KPI Section:**
- Add atmospheric glow background (like landing page hero)
- Add scroll progress bar
- KPI cards: Use `.mlabel` for labels, gradient text for values, pill indicators
- Staggered entrance animation

**Live Camera Wall Link:**
- Convert to `.stage` component with window bar
- Add live indicator with pulsing dot
- Hover glow effect

**Monitoring Grid:**
- Evidence Gallery: Use `.cap-card` pattern with hover glow
- AI Live Feed: Use `.log-panel` terminal aesthetic
- AI Status: Use `.pipeline-strip` for system health steps
- AI Intelligence: Use `.edge-card` pattern with risk bar

**Demo Scenarios:**
- Use `.tech-strip` chip layout
- Critical scenarios: `.tech-chip` with danger accent

**Bottom Grid:**
- Camera Controls: `.pipeline-strip` horizontal layout
- Security Map: `.stage` component with map inside

**Performance Section:**
- `.ai-performance-panel` → use `.cap-grid` 4-column layout
- Charts: Add `.stage` wrapper with window bar

### 7.2 Other Dashboard Pages (High Priority)

| Page | Key Components to Redesign |
|------|---------------------------|
| `/cameras` | Camera cards → `.cap-card` with stage preview |
| `/cameras_wall` | Grid → `.stage` components, layout buttons → `.pipeline-strip` |
| `/incidents` | Cards → `.cap-card`, filter → `.tech-strip` |
| `/evidence` | Gallery → `.cap-card`, detail → `.stage` with HUD |
| `/analytics` | KPI cards → landing page KPI, charts → `.stage` |
| `/threat_center` | Feed → `.log-panel`, risk gauge → `.stage` |
| `/command_center` | Grid → `.cap-grid` 3-col |
| `/settings` | Sections → `.edge-card`, toggles → styled |
| `/copilot` | Chat → `.log-panel` terminal aesthetic |

---

## 8. Navigation & Shell Redesign

### 8.1 Sidebar
- Current: Functional but basic
- Target: Match landing page header/nav aesthetic
- Add: Micro-label for "NAVIGATION", active indicator glow, hover radial gradient
- Brand: Use landing page logo treatment (`.brand-logo` with drop-shadow)

### 8.2 Topbar
- Current: Glass morphism with controls
- Target: Match landing page `header` (sticky, backdrop-blur, border)
- Page title: Use `.section-title` styling
- Controls: Use `.icon-btn` pattern (44px, 9px radius, border)
- Status chip: Use `.status-chip--primary` pattern
- Avatar: Add gradient border like landing page `.logo`

### 8.3 Mobile Navigation
- Landing page: `.mobile-toggle` hamburger → `.mobile-menu` (fixed, backdrop-blur, animated)
- Dashboard: Adopt same pattern, ensure sidebar overlay matches

---

## 9. JavaScript Enhancements

### 9.1 Scroll Reveal Observer
```javascript
// IntersectionObserver for .reveal and .stagger
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.classList.add('in-view');
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.reveal, .stagger').forEach(el => observer.observe(el));
```

### 9.2 Count-Up Animation
```javascript
function countUp(element, target, duration = 1000) {
  const start = 0;
  const startTime = performance.now();
  function animate(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
    element.textContent = Math.floor(start + (target - start) * eased).toLocaleString();
    if (progress < 1) requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);
}
```

### 9.3 Custom Cursor (Desktop)
```javascript
// Only on desktop, non-touch
if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
  document.body.classList.add('cursor-active');
  // Track mouse, update .cursor-dot and .cursor-ring positions
  // Add .hover class on interactive elements
}
```

### 9.4 Scroll Progress
```javascript
window.addEventListener('scroll', () => {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = (scrollTop / docHeight) * 100;
  document.querySelector('.scroll-progress').style.width = `${progress}%`;
});
```

### 9.5 Sheen/Sweep on Hover
- Add mouse-tracking for radial gradient position (`--cx`, `--cy` CSS variables)
- Used by `.cap-card::before`, `.cap-card::after`, `.preview-mockup::before`

---

## 10. CSS Architecture Reorganization

### 10.1 New CSS File Structure
```
static/css/
├── reset.css              (keep)
├── tokens.css             (NEW - unified design tokens from landing page)
├── base.css               (NEW - base styles, typography, utilities)
├── effects.css            (NEW - scrollbar, cursor, progress, glows, grid, scanlines)
├── animations.css         (NEW - keyframes, reveal, stagger, count-up, marquee)
├── components/
│   ├── buttons.css        (unified .btn system)
│   ├── cards.css          (unified .panel/.card/.cap-card/.kpi-card)
│   ├── forms.css          (inputs, selects, toggles)
│   ├── navigation.css     (sidebar, topbar, mobile menu)
│   ├── kpi.css            (KPI cards, stats)
│   ├── stage.css          (.stage, .stage-bar, .cam-view, HUD)
│   ├── pipeline.css       (.pipeline-strip, .pipe-step)
│   ├── log-panel.css      (.log-panel, .log-row)
│   ├── evidence-flow.css  (.evidence-flow, .ev-node)
│   ├── tech-strip.css     (.tech-strip, .tech-chip)
│   ├── micro-label.css    (.mlabel)
│   └── modals.css         (alert-popup, toast, dropdowns)
├── pages/
│   ├── dashboard.css      (index.html specific)
│   ├── cameras.css
│   ├── incidents.css
│   ├── evidence.css
│   ├── analytics.css
│   ├── threat-center.css
│   ├── command-center.css
│   ├── settings.css
│   ├── copilot.css
│   ├── live-wall.css
│   ├── security-map.css
│   └── replay.css
├── theme-system.css       (keep - but update to use new tokens)
├── responsive.css         (keep - update breakpoints to match new system)
└── polish.css             (keep - refine)
```

### 10.2 Load Order (in base.html)
```html
<!-- 1. Reset -->
<link rel="stylesheet" href="/static/css/reset.css">

<!-- 2. Tokens (MUST be first for all other CSS to use) -->
<link rel="stylesheet" href="/static/css/tokens.css">

<!-- 3. Base & Effects -->
<link rel="stylesheet" href="/static/css/base.css">
<link rel="stylesheet" href="/static/css/effects.css">
<link rel="stylesheet" href="/static/css/animations.css">

<!-- 4. Components (alphabetical) -->
<link rel="stylesheet" href="/static/css/components/buttons.css">
<link rel="stylesheet" href="/static/css/components/cards.css">
<link rel="stylesheet" href="/static/css/components/forms.css">
<link rel="stylesheet" href="/static/css/components/micro-label.css">
<link rel="stylesheet" href="/static/css/components/navigation.css">
<link rel="stylesheet" href="/static/css/components/kpi.css">
<link rel="stylesheet" href="/static/css/components/log-panel.css">
<link rel="stylesheet" href="/static/css/components/pipeline.css">
<link rel="stylesheet" href="/static/css/components/stage.css">
<link rel="stylesheet" href="/static/css/components/tech-strip.css">
<link rel="stylesheet" href="/static/css/components/evidence-flow.css">
<link rel="stylesheet" href="/static/css/components/modals.css">

<!-- 5. Pages (conditional) -->
{% if request.path == '/dashboard' %}
<link rel="stylesheet" href="/static/css/pages/dashboard.css">
{% endif %}
<!-- ... other pages -->

<!-- 6. Theme System (LAST for cascade override) -->
<link rel="stylesheet" href="/static/css/theme-system.css">

<!-- 7. Responsive (LAST) -->
<link rel="stylesheet" href="/static/css/responsive.css">

<!-- 8. Polish (LAST) -->
<link rel="stylesheet" href="/static/css/polish.css">
```

---

## 11. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create `tokens.css` with unified design tokens (landing page + dashboard merged)
- [ ] Create `base.css` with typography, spacing, layout primitives
- [ ] Create `effects.css` with scrollbar, cursor, progress bar, glows, grid, scanlines
- [ ] Create `animations.css` with all keyframes and reveal utilities
- [ ] Update `theme-system.css` to use new tokens
- [ ] Update `base.html` load order

### Phase 2: Core Components (Week 2)
- [ ] `components/buttons.css` - unified button system with shine/glow
- [ ] `components/micro-label.css` - `.mlabel` component
- [ ] `components/cards.css` - `.cap-card` with hover glow, `.panel` updates
- [ ] `components/kpi.css` - redesigned KPI cards matching landing page
- [ ] `components/stage.css` - `.stage` window component
- [ ] `components/pipeline.css` - `.pipeline-strip` horizontal steps
- [ ] `components/log-panel.css` - terminal aesthetic log panel
- [ ] `components/tech-strip.css` - chips for tags/technologies
- [ ] `components/evidence-flow.css` - flow visualization
- [ ] `components/navigation.css` - sidebar, topbar, mobile menu redesign
- [ ] `components/modals.css` - toast, alert-popup, dropdowns

### Phase 3: Dashboard Home Page (Week 3)
- [ ] Rewrite `index.html` using new components
- [ ] Create `pages/dashboard.css` for page-specific layout
- [ ] Implement scroll reveal observer
- [ ] Implement count-up for KPI values
- [ ] Add custom cursor (desktop)
- [ ] Add scroll progress bar
- [ ] Add atmospheric hero glows
- [ ] Test all responsive breakpoints

### Phase 4: High-Priority Pages (Week 4)
- [ ] `/cameras` - camera cards as `.cap-card`, stage previews
- [ ] `/cameras_wall` - grid of `.stage` components
- [ ] `/incidents` - incident cards as `.cap-card`, filter as `.tech-strip`
- [ ] `/evidence` - gallery as `.cap-grid`, detail as `.stage` with HUD
- [ ] `/analytics` - KPI cards, charts in `.stage` wrappers

### Phase 5: Remaining Pages (Week 5)
- [ ] `/threat_center` - feed as `.log-panel`, risk gauge as `.stage`
- [ ] `/command_center` - grid as `.cap-grid` 3-col
- [ ] `/settings` - sections as `.edge-card`
- [ ] `/copilot` - chat as `.log-panel`
- [ ] `/live_wall` - camera cards as `.stage`
- [ ] `/security_map` - map in `.stage`, markers styled
- [ ] `/replay` - video panel as `.stage`
- [ ] `/reports`, `/notifications`, `/camera_view`, `/register_face`

### Phase 6: Polish & QA (Week 6)
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile testing (iOS Safari, Chrome Android)
- [ ] Performance audit (Lighthouse)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Theme switching verification (light/dark/midnight)
- [ ] Reduced motion verification
- [ ] Documentation update

---

## 12. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Token conflicts with existing pages | Use CSS custom properties with fallback; incremental migration per page |
| JavaScript breaking due to class changes | Keep old classes as aliases during transition; use data-attributes for JS hooks |
| Performance regression from new effects | Lazy-load heavy effects; use `prefers-reduced-motion`; GPU-accelerated transforms only |
| Theme breaking in light mode | Test every component in both themes; use landing page's proven light overrides |
| Mobile usability degradation | Touch-target minimums (44px); simplified hover states on touch devices |

---

## 13. Success Criteria

### Visual Parity with Landing Page
- [ ] Same color system, typography, spacing, border radius
- [ ] Same button styles (shine, glow, sizing)
- [ ] Same card hover effects (radial gradient glow, scanline)
- [ ] Same micro-label component
- [ ] Same stage/window component pattern

### Motion & Interaction Quality
- [ ] Scroll progress bar visible
- [ ] Custom cursor on desktop
- [ ] Staggered entrance animations on all pages
- [ ] Count-up on KPI values
- [ ] Sheen/sweep effects on interactive cards
- [ ] Smooth theme transitions (280ms)

### Functional Preservation
- [ ] All existing dashboard features work identically
- [ ] Real-time data updates unaffected
- [ ] WebSocket connections stable
- [ ] Chart.js visualizations render correctly
- [ ] Camera streams play without regression

### Performance
- [ ] Lighthouse Performance ≥ 90
- [ ] Lighthouse Accessibility ≥ 95
- [ ] Lighthouse Best Practices ≥ 90
- [ ] First Contentful Paint < 1.5s
- [ ] Cumulative Layout Shift < 0.1

---

## 14. File Inventory for Reference

### Landing Page (Benchmark)
- `dashboard/templates/landing.html` - Complete self-contained reference

### Dashboard Templates
- `dashboard/templates/base.html` - Shell (sidebar, topbar, main)
- `dashboard/templates/index.html` - Dashboard home
- `dashboard/templates/cameras.html`
- `dashboard/templates/cameras_wall.html`
- `dashboard/templates/incidents.html`
- `dashboard/templates/evidence.html`
- `dashboard/templates/analytics.html`
- `dashboard/templates/threat_center.html`
- `dashboard/templates/command_center.html`
- `dashboard/templates/settings.html`
- `dashboard/templates/copilot.html`
- `dashboard/templates/live_wall.html`
- `dashboard/templates/security_map.html`
- `dashboard/templates/replay.html`
- `dashboard/templates/reports.html`
- `dashboard/templates/notifications.html`
- `dashboard/templates/camera_view.html`
- `dashboard/templates/register_face.html`
- `dashboard/templates/login.html`
- `dashboard/templates/signup.html`

### Dashboard CSS (Current)
- `dashboard/static/css/reset.css`
- `dashboard/static/css/style.css`
- `dashboard/static/css/sidebar.css`
- `dashboard/static/css/cards.css`
- `dashboard/static/css/camera.css`
- `dashboard/static/css/reports.css`
- `dashboard/static/css/settings.css`
- `dashboard/static/css/notifications.css`
- `dashboard/static/css/topbar.css`
- `dashboard/static/css/loading.css`
- `dashboard/static/css/evidence.css`
- `dashboard/static/css/livewall.css`
- `dashboard/static/css/security_map.css`
- `dashboard/static/css/threat_center.css`
- `dashboard/static/css/command_center.css`
- `dashboard/static/css/copilot.css`
- `dashboard/static/css/analytics.css`
- `dashboard/static/css/replay.css`
- `dashboard/static/css/theme-system.css` (2000+ lines)
- `dashboard/static/css/responsive.css` (2000+ lines)
- `dashboard/static/css/polish.css`

### Dashboard JS (Current)
- `dashboard/static/js/app.js` - Core app
- `dashboard/static/js/dashboard.js` - Dashboard home
- `dashboard/static/js/camera.js` - Cameras
- `dashboard/static/js/incidents.js` - Incidents
- `dashboard/static/js/evidence.js` - Evidence
- `dashboard/static/js/live_wall.js` - Live wall
- `dashboard/static/js/security_map.js` - Security map
- `dashboard/static/js/threat_center.js` - Threat center
- `dashboard/static/js/command_center.js` - Command center
- `dashboard/static/js/copilot.js` - Copilot
- `dashboard/static/js/replay.js` - Replay
- `dashboard/static/js/analytics.js` - Analytics
- `dashboard/static/js/reports.js` - Reports
- `dashboard/static/js/settings.js` - Settings
- `dashboard/static/js/notifications.js` - Notifications
- `dashboard/static/js/alerts.js` - Alerts
- `dashboard/static/js/loading.js` - Loading
- `dashboard/static/js/i18n.js` - Internationalization

---

## 15. Quick Reference: Key Landing Page Patterns to Replicate

| Pattern | Landing Page Class | Dashboard Application |
|---------|-------------------|----------------------|
| Section container | `section` (104px padding, border-top, bg-alt) | All major page sections |
| Section title | `.section-title` (34px, 800, -0.02em) | Page/section headers |
| Section subtitle | `.section-sub` (16px, dim) | Page descriptions |
| Micro label | `.mlabel` (mono, 12.5px, accent) | All category labels |
| Primary button | `.btn-primary` (gradient, shine, glow) | All primary CTAs |
| Ghost button | `.btn-ghost` (border, hover raise) | Secondary actions |
| Card with glow | `.cap-card` (radial hover glow) | All data cards |
| Stage window | `.stage` (bar, view, footer) | Camera feeds, previews, modals |
| Pipeline strip | `.pipeline-strip` (horizontal steps) | Workflows, processes |
| Log panel | `.log-panel` (terminal grid) | Status, logs, feeds |
| Evidence flow | `.evidence-flow` (nodes + arrows) | Process visualization |
| Tech chips | `.tech-strip` + `.tech-chip` | Tags, technologies, filters |
| KPI card | Custom (label, value, indicator) | Dashboard metrics |
| Gradient text | `.grad-text` | Hero headlines, key metrics |
| Scroll reveal | `.reveal` + `.stagger` | All content entrance |
| Custom scrollbar | Global | Whole dashboard |
| Scroll progress | `.scroll-progress` | All scrollable pages |
| Custom cursor | `.cursor-dot` + `.cursor-ring` | Desktop dashboard |

---

## 16. Next Steps

1. **Review this plan** with stakeholders
2. **Approve Phase 1** to begin token/foundation work
3. **Set up branch** for redesign work (`redesign/dashboard-v2`)
4. **Begin implementation** following phased approach
5. **Weekly checkpoints** to review visual progress against landing page

---

*Document Version: 1.0*  
*Created: 2026-09-22*  
*Based on: landing.html (benchmark) vs index.html + CSS (current dashboard)*