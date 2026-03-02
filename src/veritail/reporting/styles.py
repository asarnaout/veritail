"""Shared CSS design system for all HTML report templates."""

SHARED_CSS: str = """
/* ── Primitive Tokens ─────────────────────────────────────────── */
:root {
  /* Gray palette */
  --gray-50:  #f9fafb; --gray-100: #f3f4f6; --gray-200: #e5e7eb;
  --gray-300: #d1d5db; --gray-400: #9ca3af; --gray-500: #6b7280;
  --gray-600: #4b5563; --gray-700: #374151; --gray-800: #1f2937;
  --gray-900: #111827;

  /* Indigo palette */
  --indigo-50: #eef2ff; --indigo-100: #e0e7ff; --indigo-200: #c7d2fe;
  --indigo-500: #6366f1; --indigo-600: #4f46e5; --indigo-700: #4338ca;

  /* Green palette */
  --green-50: #f0fdf4; --green-100: #dcfce7; --green-500: #22c55e;
  --green-600: #16a34a; --green-700: #15803d;

  /* Amber palette */
  --amber-50: #fffbeb; --amber-100: #fef3c7; --amber-500: #f59e0b;
  --amber-600: #d97706; --amber-700: #b45309;

  /* Orange palette */
  --orange-500: #f97316; --orange-600: #ea580c; --orange-700: #c2410c;

  /* Red palette */
  --red-50: #fef2f2; --red-100: #fee2e2; --red-500: #ef4444;
  --red-600: #dc2626; --red-700: #b91c1c; --red-800: #991b1b;

  /* Spacing (8px grid) */
  --sp-1: 4px; --sp-2: 8px; --sp-3: 12px; --sp-4: 16px;
  --sp-5: 20px; --sp-6: 24px; --sp-8: 32px; --sp-10: 40px;
  --sp-12: 48px;

  /* Typography scale (1.2 ratio) */
  --text-xs:  11px; --text-sm:  13px; --text-base: 14px;
  --text-lg:  16px; --text-xl:  18px; --text-2xl:  22px;
  --text-3xl: 28px;

  /* Border radius */
  --radius-sm: 4px; --radius-md: 6px; --radius-lg: 8px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-lg: 0 4px 12px rgba(0,0,0,0.1);

  /* ── Semantic Tokens (Light) ────────────────────────────────── */
  --bg-page:       var(--gray-50);
  --bg-surface:    #ffffff;
  --bg-surface-alt: var(--gray-100);
  --border-default: var(--gray-200);
  --border-subtle:  var(--gray-100);

  --text-primary:   var(--gray-900);
  --text-secondary: var(--gray-500);
  --text-muted:     var(--gray-400);
  --text-heading:   var(--gray-800);

  --accent:         #4f6bed;
  --accent-hover:   #3d5bd9;
  --accent-bg:      #f0f4ff;

  /* Score colors */
  --score-3:    var(--green-600);
  --score-3-bg: var(--green-50);
  --score-2:    var(--amber-600);
  --score-2-bg: var(--amber-50);
  --score-1:    var(--orange-600);
  --score-1-bg: #fff7ed;
  --score-0:    var(--red-600);
  --score-0-bg: var(--red-50);

  --positive:  var(--green-600);
  --negative:  var(--red-600);

  /* Chart */
  --chart-grid:   var(--gray-200);
  --chart-axis:   var(--gray-300);
  --chart-label:  var(--gray-400);
  --chart-text:   var(--gray-600);

  /* Tooltip */
  --tooltip-bg:   var(--gray-800);
  --tooltip-text: var(--gray-100);

  /* KPI tier borders */
  --tier-good: var(--green-600);
  --tier-fair: var(--amber-500);
  --tier-poor: var(--orange-600);
  --tier-bad:  var(--red-600);

  /* Severity */
  --severity-fail-bg:    var(--red-100);
  --severity-fail-text:  var(--red-800);
  --severity-warn-bg:    var(--amber-100);
  --severity-warn-text:  var(--amber-700);
  --severity-info-bg:    #dbeafe;
  --severity-info-text:  #1e40af;
}

/* ── Dark Mode ────────────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-page:        #0f1117;
    --bg-surface:     #1a1d2e;
    --bg-surface-alt: #242838;
    --border-default: #2e3348;
    --border-subtle:  #242838;

    --text-primary:   #e5e7eb;
    --text-secondary: #9ca3af;
    --text-muted:     #6b7280;
    --text-heading:   #f3f4f6;

    --accent:       #7c8cf5;
    --accent-hover: #6b7ef0;
    --accent-bg:    rgba(99,102,241,0.12);

    --score-3:    #4ade80; --score-3-bg: rgba(74,222,128,0.1);
    --score-2:    #fbbf24; --score-2-bg: rgba(251,191,36,0.1);
    --score-1:    #fb923c; --score-1-bg: rgba(251,146,60,0.1);
    --score-0:    #f87171; --score-0-bg: rgba(248,113,113,0.1);

    --positive: #4ade80;
    --negative: #f87171;

    --chart-grid:  #2e3348;
    --chart-axis:  #3d4258;
    --chart-label: #6b7280;
    --chart-text:  #9ca3af;

    --tooltip-bg:   #242838;
    --tooltip-text: #e5e7eb;

    --tier-good: #4ade80;
    --tier-fair: #fbbf24;
    --tier-poor: #fb923c;
    --tier-bad:  #f87171;

    --severity-fail-bg:   rgba(248,113,113,0.15);
    --severity-fail-text: #fca5a5;
    --severity-warn-bg:   rgba(251,191,36,0.15);
    --severity-warn-text: #fcd34d;
    --severity-info-bg:   rgba(96,165,250,0.15);
    --severity-info-text: #93c5fd;

    --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md: 0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
    --shadow-lg: 0 4px 12px rgba(0,0,0,0.4);
  }
}

/* ── Base Reset & Layout ──────────────────────────────────────── */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  line-height: 1.6;
  color: var(--text-primary);
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--sp-8) var(--sp-6);
  background: var(--bg-page);
}

h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: var(--sp-6);
  color: var(--text-heading);
  border-bottom: 2px solid var(--border-default);
  padding-bottom: var(--sp-3);
}

h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  margin: var(--sp-8) 0 var(--sp-3);
  color: var(--text-heading);
}

h3 {
  font-size: 15px;
  color: var(--text-secondary);
  margin: var(--sp-3) 0 var(--sp-2);
}

/* ── Navigation ───────────────────────────────────────────────── */
.report-nav {
  position: sticky;
  top: var(--sp-3);
  z-index: 50;
  margin-bottom: var(--sp-6);
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-default);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.report-nav ul {
  display: flex;
  justify-content: center;
  list-style: none;
  gap: var(--sp-1);
  padding: var(--sp-1);
  margin: 0;
  white-space: nowrap;
}

.report-nav a {
  display: block;
  padding: 5px var(--sp-3);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: color 0.15s, background 0.15s;
}

.report-nav a:hover {
  color: var(--text-primary);
  background: var(--accent-bg);
}

.report-nav a.active {
  color: var(--accent);
  background: var(--accent-bg);
  font-weight: 600;
}

/* ── KPI Cards ────────────────────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--sp-4);
  margin-bottom: var(--sp-6);
}

.kpi-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--sp-4) var(--sp-5);
  box-shadow: var(--shadow-md);
  border-top: 3px solid var(--border-default);
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
}

.kpi-card--good  { border-top-color: var(--tier-good); }
.kpi-card--fair  { border-top-color: var(--tier-fair); }
.kpi-card--poor  { border-top-color: var(--tier-poor); }
.kpi-card--bad   { border-top-color: var(--tier-bad); }

.kpi-card__label {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.kpi-card__value {
  font-size: var(--text-3xl);
  font-weight: 700;
  font-family: 'Menlo', 'Consolas', monospace;
  color: var(--text-heading);
  line-height: 1.1;
}

.kpi-card__ci {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-family: 'Menlo', 'Consolas', monospace;
}

.kpi-card__desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
  line-height: 1.3;
  margin-top: var(--sp-1);
}

/* ── Tables ───────────────────────────────────────────────────── */
.table-wrap {
  border-radius: var(--radius-lg);
  overflow-x: auto;
  box-shadow: var(--shadow-md);
  margin-bottom: var(--sp-6);
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
}

thead tr:first-child th:first-child { border-top-left-radius: var(--radius-lg); }
thead tr:first-child th:last-child  { border-top-right-radius: var(--radius-lg); }
tbody tr:last-child td:first-child  { border-bottom-left-radius: var(--radius-lg); }
tbody tr:last-child td:last-child   { border-bottom-right-radius: var(--radius-lg); }

th {
  background: var(--bg-surface);
  color: var(--text-secondary);
  padding: var(--sp-3) var(--sp-4);
  text-align: left;
  font-weight: 600;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--border-default);
}

td {
  padding: 10px var(--sp-4);
  border-bottom: 1px solid var(--border-subtle);
  font-size: var(--text-base);
  color: var(--text-primary);
  word-wrap: break-word;
  overflow-wrap: break-word;
}

tr:last-child td { border-bottom: none; }
tr:hover { background: var(--accent-bg); }

.metric-value {
  font-family: 'Menlo', 'Consolas', monospace;
  font-weight: 600;
}

.positive { color: var(--positive); }
.negative { color: var(--negative); }
.neutral  { color: var(--text-secondary); }

/* ── Cards ────────────────────────────────────────────────────── */
.card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--sp-5);
  margin-bottom: var(--sp-6);
  box-shadow: var(--shadow-md);
}

/* ── Score Badges ─────────────────────────────────────────────── */
.score-badge {
  display: inline-block;
  padding: 1px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 600;
  font-family: 'Menlo', 'Consolas', monospace;
}

.score-badge--3 { background: var(--score-3-bg); color: var(--score-3); }
.score-badge--2 { background: var(--score-2-bg); color: var(--score-2); }
.score-badge--1 { background: var(--score-1-bg); color: var(--score-1); }
.score-badge--0 { background: var(--score-0-bg); color: var(--score-0); }

/* ── Severity Badges ──────────────────────────────────────────── */
.severity-fail {
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--severity-fail-bg);
  color: var(--severity-fail-text);
}

.severity-warning {
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--severity-warn-bg);
  color: var(--severity-warn-text);
}

.severity-info {
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--severity-info-bg);
  color: var(--severity-info-text);
}

/* ── Tooltips ─────────────────────────────────────────────────── */
.tip {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px; height: 16px;
  margin-left: 5px;
  border-radius: var(--radius-full);
  background: var(--bg-surface-alt);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 600;
  cursor: default;
  vertical-align: middle;
}

.tip::after {
  content: attr(data-tip);
  position: absolute;
  left: 0; bottom: calc(100% + 8px);
  padding: 8px 12px;
  background: var(--tooltip-bg);
  color: var(--tooltip-text);
  font-size: 12px; font-weight: 400;
  line-height: 1.4;
  white-space: normal;
  width: max-content; max-width: 280px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  pointer-events: none;
  opacity: 0; transition: opacity 0.15s;
  z-index: 100;
}

.tip::before {
  content: "";
  position: absolute;
  left: 4px; bottom: calc(100% + 2px);
  border: 5px solid transparent;
  border-top-color: var(--tooltip-bg);
  pointer-events: none;
  opacity: 0; transition: opacity 0.15s;
  z-index: 100;
}

.tip:hover::after, .tip:hover::before { opacity: 1; }

/* ── Footer ───────────────────────────────────────────────────── */
.footer {
  margin-top: var(--sp-8);
  padding-top: var(--sp-4);
  border-top: 1px solid var(--border-default);
  color: var(--text-muted);
  font-size: 12px;
}

.footer strong, .footer b {
  color: var(--text-secondary);
}

.footer-meta {
  margin-top: 10px;
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 4px 12px;
  align-items: baseline;
}

.footer-key {
  color: var(--text-secondary);
  font-weight: 600;
}

.footer-value {
  color: var(--text-primary);
  font-family: 'Menlo', 'Consolas', monospace;
  word-break: break-all;
}

/* ── Pagination ───────────────────────────────────────────────── */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-1);
  margin-top: var(--sp-5);
  flex-wrap: wrap;
}

.pagination button {
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
  color: var(--text-primary);
  padding: 6px 12px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
  min-width: 36px;
}

.pagination button:hover:not(:disabled) {
  background: var(--accent-bg);
  border-color: var(--accent);
  color: var(--accent);
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: default;
}

.pagination button.active {
  background: var(--accent);
  color: #ffffff;
  border-color: var(--accent);
  font-weight: 600;
}

.pagination .page-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 var(--sp-2);
}

/* ── Details / Summary ────────────────────────────────────────── */
details summary::-webkit-details-marker { display: none; }
details summary::marker { display: none; content: ""; }
details[open] > summary .check-arrow { transform: rotate(90deg); }

/* ── Banner Link ──────────────────────────────────────────────── */
.banner-link {
  background: var(--accent-bg);
  border-left: 4px solid var(--accent);
  padding: var(--sp-3) var(--sp-4);
  margin-bottom: var(--sp-6);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
}

.banner-link a {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
}

.banner-link a:hover {
  text-decoration: underline;
}

/* ── Suggestion List (autocomplete) ───────────────────────────── */
.suggestion-list { list-style: none; padding: 0; margin: 0; }
.suggestion-list li {
  display: inline-block;
  background: var(--bg-surface-alt);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  margin: 2px 4px 2px 0;
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.failed-check {
  color: var(--negative);
  font-size: var(--text-sm);
  margin-top: var(--sp-2);
}

/* ── Utility Classes ──────────────────────────────────────────── */
.text-secondary { color: var(--text-secondary); }
.text-muted     { color: var(--text-muted); }
.text-sm        { font-size: var(--text-sm); }
.text-xs        { font-size: var(--text-xs); }

/* ── Print ────────────────────────────────────────────────────── */
@media print {
  .report-nav { display: none; }
  .pagination { display: none; }
  body { background: white; color: black; }
  .card, .table-wrap { box-shadow: none; border: 1px solid #d1d5db; }
  .paginated-item { display: block !important; }
  a { color: inherit; text-decoration: underline; }
}
"""
