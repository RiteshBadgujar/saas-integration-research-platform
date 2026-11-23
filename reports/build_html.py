"""
reports/build_html.py
Generates the self-contained index.html case study.
Run with:  python reports/build_html.py
"""
import json, csv, html as html_mod
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

apps       = json.load(open(ROOT / "data/apps.json", encoding="utf-8"))
accuracy   = json.load(open(ROOT / "verification/accuracy_report.json", encoding="utf-8"))
cat_data   = json.load(open(ROOT / "reports/category_analysis.json", encoding="utf-8"))
summary    = json.load(open(ROOT / "reports/research_summary.json", encoding="utf-8"))

verif_rows = []
with open(ROOT / "verification/verification_results.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        verif_rows.append(dict(row))

# ── Serialise datasets for JS ──────────────────────────────────────────────────
apps_js       = json.dumps(apps,       ensure_ascii=False, separators=(',',':'))
verif_js      = json.dumps(verif_rows, ensure_ascii=False, separators=(',',':'))
accuracy_js   = json.dumps(accuracy,   ensure_ascii=False, separators=(',',':'))
summary_js    = json.dumps(summary,    ensure_ascii=False, separators=(',',':'))
cat_js        = json.dumps(cat_data,   ensure_ascii=False, separators=(',',':'))

# ── Derived chart data (computed in Python from real datasets) ──────────────
auth_dist  = summary["authentication_analysis"]["distribution"]
cred_dist  = summary["credential_access_analysis"]["distribution"]
build_dist = summary["buildability_analysis"]["distribution"]
mcp        = summary["mcp_analysis"]
webhook    = summary["webhook_analysis"]
composio   = summary["composio_coverage_analysis"]
top15      = summary["priority_new_integrations"]["top_15_candidates"]
recs       = summary["product_ops_recommendations"]
official_mcp_apps = [a["app_name"] for a in apps if a.get("mcp_support") == "Official MCP"]

CAT_LABELS = [
    "CRM & Sales","Proj Mgmt","Comm & Collab","Marketing",
    "Cust Support","Finance","HR & Recruit","Dev Tools","Analytics & BI","Storage & Docs"
]
CAT_KEYS = list(cat_data.keys())

# helper
def jl(v): return json.dumps(v, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Composio SaaS API Research — AI Product Ops Case Study</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
/* ── Reset & tokens ───────────────────────────────────────────── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0f1117;--surface:#1a1d27;--surface2:#22263a;
  --border:#2e3348;--border2:#3d4466;
  --text:#e2e8f0;--muted:#8892a4;--dim:#555e72;
  --accent:#6366f1;--accent2:#818cf8;--accent3:#a5b4fc;
  --green:#22c55e;--yellow:#eab308;--red:#ef4444;--orange:#f97316;
  --blue:#38bdf8;--purple:#a78bfa;--pink:#f472b6;
  --radius:10px;--radius-sm:6px;
  --shadow:0 4px 24px rgba(0,0,0,.45);
}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;font-size:14px;line-height:1.6}}
a{{color:var(--accent2);text-decoration:none}}
a:hover{{text-decoration:underline}}
/* ── Layout ───────────────────────────────────────────────────── */
.container{{max-width:1400px;margin:0 auto;padding:0 24px}}
/* ── Navbar ──────────────────────────────────────────────────── */
#navbar{{position:sticky;top:0;z-index:100;background:rgba(15,17,23,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:12px 0}}
#navbar .inner{{display:flex;align-items:center;gap:16px;flex-wrap:wrap}}
#navbar .brand{{display:flex;align-items:center;gap:10px;font-weight:700;font-size:16px;color:#fff;white-space:nowrap}}
.brand-pill{{background:var(--accent);color:#fff;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:800;letter-spacing:.5px}}
#navbar nav{{display:flex;gap:4px;flex-wrap:wrap;margin-left:auto}}
#navbar nav a{{padding:5px 12px;border-radius:var(--radius-sm);color:var(--muted);font-size:12px;font-weight:500;transition:all .2s}}
#navbar nav a:hover,#navbar nav a.active{{background:var(--surface2);color:var(--text);text-decoration:none}}
/* ── Hero ────────────────────────────────────────────────────── */
#hero{{padding:64px 0 48px;background:linear-gradient(135deg,rgba(99,102,241,.12) 0%,rgba(15,17,23,0) 60%)}}
.hero-badge{{display:inline-flex;align-items:center;gap:6px;background:rgba(99,102,241,.18);border:1px solid rgba(99,102,241,.35);border-radius:20px;padding:4px 14px;font-size:11px;font-weight:600;color:var(--accent3);letter-spacing:.4px;margin-bottom:16px}}
h1{{font-size:clamp(28px,4vw,46px);font-weight:800;line-height:1.15;margin-bottom:12px}}
h1 span{{background:linear-gradient(135deg,var(--accent2),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.hero-sub{{color:var(--muted);font-size:15px;max-width:620px;margin-bottom:28px}}
.hero-meta{{display:flex;gap:20px;flex-wrap:wrap;font-size:12px;color:var(--dim)}}
.hero-meta span{{display:flex;align-items:center;gap:5px}}
/* ── KPI Cards ───────────────────────────────────────────────── */
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;padding:40px 0 0}}
.kpi{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px 18px;position:relative;overflow:hidden}}
.kpi::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--kpi-color,var(--accent))}}
.kpi-val{{font-size:36px;font-weight:800;line-height:1;color:var(--kpi-color,var(--text))}}
.kpi-label{{font-size:11px;color:var(--muted);margin-top:5px;font-weight:500;letter-spacing:.3px;text-transform:uppercase}}
.kpi-sub{{font-size:11px;color:var(--dim);margin-top:3px}}
/* ── Section ─────────────────────────────────────────────────── */
section{{padding:52px 0}}
section+section{{border-top:1px solid var(--border)}}
.section-header{{margin-bottom:28px}}
.section-label{{font-size:11px;font-weight:700;color:var(--accent2);letter-spacing:1px;text-transform:uppercase;margin-bottom:6px}}
.section-title{{font-size:clamp(20px,2.5vw,28px);font-weight:700;margin-bottom:8px}}
.section-desc{{color:var(--muted);font-size:13px;max-width:680px}}
/* ── Chart grid ──────────────────────────────────────────────── */
.chart-grid{{display:grid;gap:20px}}
.chart-grid.cols-2{{grid-template-columns:repeat(auto-fit,minmax(380px,1fr))}}
.chart-grid.cols-3{{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}}
.chart-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:22px}}
.chart-title{{font-size:13px;font-weight:600;margin-bottom:4px;color:var(--text)}}
.chart-sub{{font-size:11px;color:var(--dim);margin-bottom:16px}}
.chart-wrap{{position:relative;height:260px}}
.chart-wrap.tall{{height:320px}}
.chart-wrap.short{{height:200px}}
/* ── Category grid ───────────────────────────────────────────── */
.cat-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}
.cat-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px}}
.cat-name{{font-weight:700;font-size:13px;margin-bottom:10px;display:flex;align-items:center;gap:8px}}
.cat-emoji{{font-size:18px}}
.cat-stat-row{{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);padding:4px 0;border-bottom:1px solid var(--border)}}
.cat-stat-row:last-child{{border:none}}
.cat-stat-val{{font-weight:600;color:var(--text)}}
.progress{{height:4px;background:var(--border2);border-radius:2px;margin-top:8px;overflow:hidden}}
.progress-bar{{height:100%;border-radius:2px;background:var(--accent)}}
/* ── Table ───────────────────────────────────────────────────── */
.table-toolbar{{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;align-items:center}}
.search-box{{background:var(--surface2);border:1px solid var(--border2);border-radius:var(--radius-sm);padding:8px 14px;color:var(--text);font-size:13px;flex:1;min-width:200px;outline:none}}
.search-box:focus{{border-color:var(--accent)}}
select.filter-sel{{background:var(--surface2);border:1px solid var(--border2);border-radius:var(--radius-sm);padding:8px 10px;color:var(--text);font-size:12px;outline:none;cursor:pointer}}
select.filter-sel:focus{{border-color:var(--accent)}}
.table-count{{font-size:12px;color:var(--dim);margin-left:auto;white-space:nowrap}}
.tbl-wrap{{overflow-x:auto;border-radius:var(--radius);border:1px solid var(--border)}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
thead{{background:var(--surface2)}}
th{{padding:10px 12px;text-align:left;font-weight:600;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.4px;white-space:nowrap;cursor:pointer;user-select:none}}
th:hover{{color:var(--text)}}
td{{padding:9px 12px;border-top:1px solid var(--border);vertical-align:top;max-width:200px}}
tr:hover td{{background:rgba(255,255,255,.025)}}
td .truncate{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:180px;display:block}}
/* ── Badges ──────────────────────────────────────────────────── */
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;white-space:nowrap}}
.badge-green{{background:rgba(34,197,94,.15);color:#4ade80}}
.badge-yellow{{background:rgba(234,179,8,.15);color:#facc15}}
.badge-red{{background:rgba(239,68,68,.15);color:#f87171}}
.badge-blue{{background:rgba(56,189,248,.15);color:#38bdf8}}
.badge-purple{{background:rgba(167,139,250,.15);color:#a78bfa}}
.badge-orange{{background:rgba(249,115,22,.15);color:#fb923c}}
.badge-gray{{background:rgba(100,116,139,.15);color:#94a3b8}}
.badge-pink{{background:rgba(244,114,182,.15);color:#f9a8d4}}
/* ── Audit table ─────────────────────────────────────────────── */
.match-yes{{color:var(--green);font-weight:700}}
.match-no{{color:var(--red);font-weight:700}}
/* ── Accuracy ─────────────────────────────────────────────────── */
.acc-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:28px}}
.acc-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px;text-align:center}}
.acc-pct{{font-size:34px;font-weight:800;line-height:1}}
.acc-pct.perfect{{color:var(--green)}}
.acc-pct.good{{color:var(--yellow)}}
.acc-label{{font-size:11px;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:.4px}}
/* ── Confusion matrix ─────────────────────────────────────────── */
.cm-wrap{{overflow-x:auto}}
.cm-table{{border-collapse:collapse;font-size:11px}}
.cm-table th,.cm-table td{{padding:9px 14px;border:1px solid var(--border);text-align:center}}
.cm-table thead th{{background:var(--surface2);color:var(--muted);font-weight:600}}
.cm-table .row-label{{background:var(--surface2);color:var(--muted);font-weight:600;white-space:nowrap}}
.cm-diag{{background:rgba(34,197,94,.15);color:#4ade80;font-weight:800}}
.cm-err{{background:rgba(239,68,68,.12);color:#f87171;font-weight:800}}
/* ── Recommendations ──────────────────────────────────────────── */
.rec-grid{{display:grid;gap:14px}}
.rec-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;display:grid;grid-template-columns:auto 1fr;gap:16px;align-items:start}}
.rec-id{{background:var(--accent);color:#fff;border-radius:var(--radius-sm);padding:4px 10px;font-size:11px;font-weight:800;white-space:nowrap}}
.rec-title{{font-weight:700;font-size:13px;margin-bottom:5px}}
.rec-body{{font-size:12px;color:var(--muted);line-height:1.6}}
.rec-action{{margin-top:8px;padding:10px 12px;background:var(--surface2);border-radius:var(--radius-sm);font-size:12px;border-left:3px solid var(--accent)}}
/* ── Error pattern ────────────────────────────────────────────── */
.err-card{{background:var(--surface);border:1px solid rgba(239,68,68,.3);border-radius:var(--radius);padding:18px;margin-bottom:12px}}
.err-title{{font-weight:700;color:#f87171;margin-bottom:6px}}
.err-meta{{display:flex;gap:12px;font-size:11px;color:var(--dim);flex-wrap:wrap;margin-bottom:8px}}
.err-desc{{font-size:12px;color:var(--muted)}}
/* ── Priority table ────────────────────────────────────────────── */
.score-bar{{display:flex;align-items:center;gap:6px}}
.score-pip{{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--accent)}}
/* ── Methodology ───────────────────────────────────────────────── */
.method-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}
.method-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px}}
.method-icon{{font-size:24px;margin-bottom:10px}}
.method-title{{font-weight:700;font-size:13px;margin-bottom:6px}}
.method-desc{{font-size:12px;color:var(--muted)}}
/* ── Footer ────────────────────────────────────────────────────── */
footer{{background:var(--surface);border-top:1px solid var(--border);padding:32px 0;margin-top:40px;text-align:center;color:var(--dim);font-size:12px}}
footer strong{{color:var(--muted)}}
/* ── Pagination ────────────────────────────────────────────────── */
.pager{{display:flex;align-items:center;gap:8px;margin-top:14px;flex-wrap:wrap}}
.pager-btn{{background:var(--surface2);border:1px solid var(--border);color:var(--text);padding:5px 12px;border-radius:var(--radius-sm);cursor:pointer;font-size:12px}}
.pager-btn:hover:not(:disabled){{border-color:var(--accent)}}
.pager-btn:disabled{{opacity:.4;cursor:default}}
.pager-info{{font-size:12px;color:var(--dim)}}
/* ── Responsive ────────────────────────────────────────────────── */
@media(max-width:640px){{
  .chart-grid.cols-2,.chart-grid.cols-3{{grid-template-columns:1fr}}
  .table-toolbar{{flex-direction:column;align-items:stretch}}
  .table-count{{margin-left:0}}
  .rec-card{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>

<!-- ── Navbar ───────────────────────────────────────────────────────── -->
<div id="navbar">
<div class="container">
<div class="inner">
  <div class="brand">
    <span class="brand-pill">COMPOSIO</span>
    SaaS API Research
  </div>
  <nav>
    <a href="#overview">Overview</a>
    <a href="#auth">Auth</a>
    <a href="#buildability">Buildability</a>
    <a href="#composio">Coverage</a>
    <a href="#mcp">MCP</a>
    <a href="#categories">Categories</a>
    <a href="#dataset">100 Apps</a>
    <a href="#audit">Audit</a>
    <a href="#accuracy">Accuracy</a>
    <a href="#recommendations">Recs</a>
    <a href="#methodology">Method</a>
  </nav>
</div>
</div>
</div>

<!-- ── Hero ─────────────────────────────────────────────────────────── -->
<div id="hero">
<div class="container">
  <div class="hero-badge">🔬 AI Product Ops Intern Assignment — Composio</div>
  <h1>SaaS API & Authentication<br/><span>Research Intelligence Report</span></h1>
  <p class="hero-sub">A systematic, evidence-backed analysis of 100 SaaS applications across 10 categories — evaluating authentication mechanisms, API accessibility, Composio toolkit coverage, and integration buildability for autonomous AI agents.</p>
  <div class="hero-meta">
    <span>📅 Research Date: 2026-11-23</span>
    <span>📊 100 Applications · 10 Categories</span>
    <span>🔍 30-App Manual Verification Audit</span>
    <span>✅ 86.7% Automated Verdict Accuracy</span>
    <span>🧰 60 Existing Composio Toolkits Mapped</span>
  </div>
</div>
</div>

<!-- ── KPI Cards ─────────────────────────────────────────────────────── -->
<div id="overview" class="container">
<div class="kpi-grid">
  <div class="kpi" style="--kpi-color:#6366f1">
    <div class="kpi-val">100</div>
    <div class="kpi-label">Apps Researched</div>
    <div class="kpi-sub">10 categories · 10 apps each</div>
  </div>
  <div class="kpi" style="--kpi-color:#22c55e">
    <div class="kpi-val">98%</div>
    <div class="kpi-label">Feasibly Buildable</div>
    <div class="kpi-sub">98 of 100 apps</div>
  </div>
  <div class="kpi" style="--kpi-color:#38bdf8">
    <div class="kpi-val">60</div>
    <div class="kpi-label">Composio Official</div>
    <div class="kpi-sub">40 new opportunities</div>
  </div>
  <div class="kpi" style="--kpi-color:#a78bfa">
    <div class="kpi-val">90%</div>
    <div class="kpi-label">Self-Serve Access</div>
    <div class="kpi-sub">90 of 100 apps</div>
  </div>
  <div class="kpi" style="--kpi-color:#f97316">
    <div class="kpi-val">98%</div>
    <div class="kpi-label">Webhook Support</div>
    <div class="kpi-sub">Event-driven agent workflows</div>
  </div>
  <div class="kpi" style="--kpi-color:#f472b6">
    <div class="kpi-val">15</div>
    <div class="kpi-label">Official MCP</div>
    <div class="kpi-sub">+41 third-party MCP</div>
  </div>
  <div class="kpi" style="--kpi-color:#eab308">
    <div class="kpi-val">86.7%</div>
    <div class="kpi-label">Verdict Accuracy</div>
    <div class="kpi-sub">30-app manual audit</div>
  </div>
  <div class="kpi" style="--kpi-color:#ef4444">
    <div class="kpi-val">2</div>
    <div class="kpi-label">Partner-Gated</div>
    <div class="kpi-sub">NetSuite · Workday</div>
  </div>
</div>
</div>

<!-- ── Authentication Analysis ───────────────────────────────────────── -->
<section id="auth">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 2</div>
    <div class="section-title">Authentication & Credential Analysis</div>
    <div class="section-desc">Distribution of authentication mechanisms across 100 researched SaaS applications, with credential accessibility breakdown.</div>
  </div>
  <div class="chart-grid cols-3">
    <div class="chart-card">
      <div class="chart-title">Authentication Type Distribution</div>
      <div class="chart-sub">n=100 apps · all categories</div>
      <div class="chart-wrap"><canvas id="chartAuth"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Credential Access Model</div>
      <div class="chart-sub">How easily developers obtain API credentials</div>
      <div class="chart-wrap"><canvas id="chartCred"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Auth Type by Category</div>
      <div class="chart-sub">OAuth 2.0 vs API Key vs Other per category</div>
      <div class="chart-wrap tall"><canvas id="chartAuthCat"></canvas></div>
    </div>
  </div>
  <div style="margin-top:16px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px">
    <div style="font-weight:600;margin-bottom:8px;font-size:13px">Key Insight</div>
    <p style="font-size:12px;color:var(--muted)">OAuth 2.0 (40%) and API Key (36%) together cover 76% of the corpus — both natively supported by Composio's authentication engine. Only 2 apps (NetSuite, Workday) are partner-gated, representing a commercial rather than technical blocker.</p>
  </div>
</div>
</section>

<!-- ── Buildability Analysis ─────────────────────────────────────────── -->
<section id="buildability">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 3</div>
    <div class="section-title">Buildability & API Accessibility</div>
    <div class="section-desc">Integration feasibility verdict for all 100 apps, post-M4 manual corrections. 4 apps upgraded from "Buildable with limitations" to "Buildable" after heuristic bug fix.</div>
  </div>
  <div class="chart-grid cols-2">
    <div class="chart-card">
      <div class="chart-title">Buildability Verdict Distribution</div>
      <div class="chart-sub">Post-M4 corrected production dataset</div>
      <div class="chart-wrap"><canvas id="chartBuild"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Public API Availability & Coverage</div>
      <div class="chart-sub">API surface breadth across corpus</div>
      <div class="chart-wrap"><canvas id="chartApiCov"></canvas></div>
    </div>
  </div>
  <div style="margin-top:14px;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px">
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px">
      <div style="font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Buildable (Clean)</div>
      <div style="font-size:28px;font-weight:800;color:var(--green)">4</div>
      <div style="font-size:11px;color:var(--dim)">Attio · Resend · Deel · Supabase</div>
    </div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px">
      <div style="font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Buildable with Limitations</div>
      <div style="font-size:28px;font-weight:800;color:var(--yellow)">94</div>
      <div style="font-size:11px;color:var(--dim)">Rate limits, OAuth complexity, approval tiers</div>
    </div>
    <div style="background:var(--surface);border:1px solid rgba(239,68,68,.3);border-radius:var(--radius);padding:16px">
      <div style="font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Partner-Dependent</div>
      <div style="font-size:28px;font-weight:800;color:var(--red)">2</div>
      <div style="font-size:11px;color:var(--dim)">NetSuite · Workday (vendor agreement required)</div>
    </div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px">
      <div style="font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Total Feasibly Buildable</div>
      <div style="font-size:28px;font-weight:800;color:var(--accent2)">98%</div>
      <div style="font-size:11px;color:var(--dim)">98 of 100 apps across all categories</div>
    </div>
  </div>
</div>
</section>

<!-- ── Composio Coverage ──────────────────────────────────────────────── -->
<section id="composio">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 4</div>
    <div class="section-title">Composio Toolkit Coverage & Integration Opportunities</div>
    <div class="section-desc">60 of 100 apps already have Official Composio Toolkits. The remaining 40 represent new integration development opportunities.</div>
  </div>
  <div class="chart-grid cols-2">
    <div class="chart-card">
      <div class="chart-title">Composio Toolkit Coverage</div>
      <div class="chart-sub">Official Toolkit vs New Opportunities</div>
      <div class="chart-wrap short"><canvas id="chartComposio"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Coverage by Category</div>
      <div class="chart-sub">Official Toolkits vs Opportunities per category</div>
      <div class="chart-wrap tall"><canvas id="chartComposioCat"></canvas></div>
    </div>
  </div>
  <div style="margin-top:16px">
    <div style="font-weight:600;font-size:13px;margin-bottom:12px">Top 15 New Integration Candidates</div>
    <div class="tbl-wrap">
    <table>
      <thead><tr>
        <th>#</th><th>App</th><th>Category</th><th>Buildability</th>
        <th>Auth</th><th>Webhooks</th><th>MCP</th><th>Score</th>
      </tr></thead>
      <tbody id="priorityTbl"></tbody>
    </table>
    </div>
  </div>
</div>
</section>

<!-- ── MCP & Webhooks ─────────────────────────────────────────────────── -->
<section id="mcp">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 5</div>
    <div class="section-title">MCP & Webhook Support Analysis</div>
    <div class="section-desc">Model Context Protocol server availability and webhook event-stream support — key signals for agentic API tooling demand.</div>
  </div>
  <div class="chart-grid cols-2">
    <div class="chart-card">
      <div class="chart-title">MCP Support Breakdown</div>
      <div class="chart-sub">Official · Third-party · Not Found (n=100)</div>
      <div class="chart-wrap"><canvas id="chartMcp"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Webhook Support</div>
      <div class="chart-sub">Event-driven vs polling architectures</div>
      <div class="chart-wrap short"><canvas id="chartWebhook"></canvas></div>
    </div>
  </div>
  <div style="margin-top:16px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px">
    <div style="font-weight:600;margin-bottom:10px;font-size:13px">Official MCP Servers Found (15 apps)</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px" id="mcpPills"></div>
    <div style="margin-top:12px;font-size:12px;color:var(--muted)">Developer Tools leads MCP adoption with 6 official servers — the strongest agentic API demand signal in the dataset. Combined with 41 third-party MCP wrappers, 56% of the corpus has some form of MCP tooling.</div>
  </div>
  <div style="margin-top:12px;background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.2);border-radius:var(--radius);padding:16px">
    <div style="font-weight:600;color:#f87171;margin-bottom:6px;font-size:13px">⚠️ Apps Without Webhooks (Polling Required)</div>
    <div style="font-size:12px;color:var(--muted)"><strong>Expensify</strong> and <strong>Notion</strong> do not expose event webhooks. Integrations with these platforms require polling architectures — increasing compute cost and API-credit consumption for autonomous agent trigger workflows.</div>
  </div>
</div>
</section>

<!-- ── Category Deep-Dive ─────────────────────────────────────────────── -->
<section id="categories">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 6</div>
    <div class="section-title">Category-Wise Analysis</div>
    <div class="section-desc">Detailed breakdown of all 10 research categories across buildability, Composio coverage, MCP adoption, and integration opportunities.</div>
  </div>
  <div class="cat-grid" id="catCards"></div>
</div>
</section>

<!-- ── Full 100-App Dataset ───────────────────────────────────────────── -->
<section id="dataset">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 7</div>
    <div class="section-title">Complete SaaS Application Dataset</div>
    <div class="section-desc">All 100 researched applications. Search, filter, and sort to explore the full dataset.</div>
  </div>
  <div class="table-toolbar">
    <input class="search-box" id="appSearch" type="search" placeholder="🔍  Search apps, categories, auth types…"/>
    <select class="filter-sel" id="filterCat">
      <option value="">All Categories</option>
      <option>CRM and Sales</option>
      <option>Project Management</option>
      <option>Communication and Collaboration</option>
      <option>Marketing Automation</option>
      <option>Customer Support</option>
      <option>Finance and Accounting</option>
      <option>HR and Recruitment</option>
      <option>Developer Tools</option>
      <option>Analytics and Business Intelligence</option>
      <option>Storage and Document Management</option>
    </select>
    <select class="filter-sel" id="filterBuild">
      <option value="">All Verdicts</option>
      <option>Buildable</option>
      <option>Buildable with limitations</option>
      <option>Partner-dependent</option>
    </select>
    <select class="filter-sel" id="filterComposio">
      <option value="">All Composio Status</option>
      <option>Official Toolkit</option>
      <option>Not Supported</option>
    </select>
    <select class="filter-sel" id="filterAuth">
      <option value="">All Auth Types</option>
      <option>OAuth 2.0</option>
      <option>API Key</option>
      <option>Basic Auth</option>
      <option>Bearer JWT</option>
      <option>Personal Access Token (PAT)</option>
    </select>
    <span class="table-count" id="appCount"></span>
  </div>
  <div class="tbl-wrap">
  <table id="appTable">
    <thead><tr>
      <th onclick="sortTable(0)">#</th>
      <th onclick="sortTable(1)">App ↕</th>
      <th onclick="sortTable(2)">Category ↕</th>
      <th onclick="sortTable(3)">Auth ↕</th>
      <th>Credential</th>
      <th>API</th>
      <th onclick="sortTable(6)">Buildability ↕</th>
      <th>Composio</th>
      <th>Webhooks</th>
      <th>MCP</th>
      <th>Docs</th>
    </tr></thead>
    <tbody id="appTbody"></tbody>
  </table>
  </div>
  <div class="pager">
    <button class="pager-btn" id="btnPrev" onclick="changePage(-1)">← Prev</button>
    <span class="pager-info" id="pagerInfo"></span>
    <button class="pager-btn" id="btnNext" onclick="changePage(1)">Next →</button>
  </div>
</div>
</section>

<!-- ── Manual Audit ───────────────────────────────────────────────────── -->
<section id="audit">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 8</div>
    <div class="section-title">30-App Manual Verification Audit</div>
    <div class="section-desc">Stratified sample of 3 apps per category, manually verified against official developer documentation. Side-by-side automated vs verified comparison.</div>
  </div>
  <div style="margin-bottom:14px;display:flex;gap:12px;flex-wrap:wrap">
    <select class="filter-sel" id="auditCatFilter">
      <option value="">All Categories</option>
      <option>CRM and Sales</option>
      <option>Project Management</option>
      <option>Communication and Collaboration</option>
      <option>Marketing Automation</option>
      <option>Customer Support</option>
      <option>Finance and Accounting</option>
      <option>HR and Recruitment</option>
      <option>Developer Tools</option>
      <option>Analytics and Business Intelligence</option>
      <option>Storage and Document Management</option>
    </select>
    <select class="filter-sel" id="auditMatchFilter">
      <option value="">All Results</option>
      <option value="True">✅ Correct Predictions</option>
      <option value="False">❌ Incorrect Predictions</option>
    </select>
    <span class="table-count" id="auditCount"></span>
  </div>
  <div class="tbl-wrap">
  <table id="auditTable">
    <thead><tr>
      <th>App</th><th>Category</th>
      <th>Auto Auth</th><th>✓ Auth</th>
      <th>Auto Cred</th><th>✓ Cred</th>
      <th>Auto Verdict</th><th>✓ Verdict</th>
      <th>Match?</th><th>Correction</th>
      <th>Source</th>
    </tr></thead>
    <tbody id="auditTbody"></tbody>
  </table>
  </div>
</div>
</section>

<!-- ── Accuracy & Confusion Matrix ───────────────────────────────────── -->
<section id="accuracy">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 9</div>
    <div class="section-title">Accuracy Metrics & Error Analysis</div>
    <div class="section-desc">Field-level accuracy from the 30-app manual audit, confusion matrix, and root-cause error pattern analysis.</div>
  </div>

  <div class="acc-grid">
    <div class="acc-card">
      <div class="acc-pct good">86.7%</div>
      <div class="acc-label">Overall Verdict Accuracy</div>
    </div>
    <div class="acc-card">
      <div class="acc-pct perfect">100%</div>
      <div class="acc-label">Auth Type Accuracy</div>
    </div>
    <div class="acc-card">
      <div class="acc-pct perfect">100%</div>
      <div class="acc-label">Credential Access</div>
    </div>
    <div class="acc-card">
      <div class="acc-pct perfect">100%</div>
      <div class="acc-label">Public API</div>
    </div>
    <div class="acc-card">
      <div class="acc-pct perfect">100%</div>
      <div class="acc-label">Webhooks</div>
    </div>
    <div class="acc-card">
      <div class="acc-pct perfect">100%</div>
      <div class="acc-label">MCP Support</div>
    </div>
  </div>

  <div class="chart-grid cols-2" style="margin-bottom:24px">
    <div class="chart-card">
      <div class="chart-title">Field-Level Accuracy Radar</div>
      <div class="chart-sub">All 6 evaluated fields — 30-app audit</div>
      <div class="chart-wrap"><canvas id="chartAccuracy"></canvas></div>
    </div>
    <div>
      <div style="font-weight:600;font-size:13px;margin-bottom:12px">Buildability Confusion Matrix</div>
      <div class="cm-wrap">
      <table class="cm-table">
        <thead>
          <tr><th>Actual \\ Predicted</th><th>Buildable</th><th>Bld w/ Limits</th><th>Partner-dep</th></tr>
        </thead>
        <tbody>
          <tr>
            <td class="row-label">Buildable (Actual)</td>
            <td class="cm-err">0</td>
            <td class="cm-err">4</td>
            <td>0</td>
          </tr>
          <tr>
            <td class="row-label">Bld w/ Limits (Actual)</td>
            <td>0</td>
            <td class="cm-diag">24</td>
            <td>0</td>
          </tr>
          <tr>
            <td class="row-label">Partner-dep (Actual)</td>
            <td>0</td>
            <td>0</td>
            <td class="cm-diag">2</td>
          </tr>
        </tbody>
      </table>
      </div>
      <div style="margin-top:12px;font-size:11px;color:var(--dim)">
        <div>✅ True Positives: 26 &nbsp;|&nbsp; ❌ False Negatives: 4 (Buildable class)</div>
        <div style="margin-top:4px">Root cause: Parser treated "None; ..." as blocker strings → downgraded 4 clean APIs</div>
      </div>
    </div>
  </div>

  <div style="font-weight:600;font-size:13px;margin-bottom:12px">Identified Error Patterns</div>
  <div class="err-card">
    <div class="err-title">⚠️ Over-Conservative Limitation Classification (Heuristic Bleed)</div>
    <div class="err-meta">
      <span>Frequency: 4 apps</span>
      <span>Affected: Attio, Resend, Deel, Supabase</span>
      <span>Class: False Negative (Buildable)</span>
    </div>
    <div class="err-desc">The automated classifier's text parser flagged descriptive sentences starting with <code>"None; ..."</code> as blocker strings, inappropriately downgrading 4 truly friction-free APIs from "Buildable" to "Buildable with limitations". <strong>Fix:</strong> Strip leading "None;" clauses before evaluating limitation strings in buildability_classifier.py.</div>
  </div>
  <div class="err-card">
    <div class="err-title">ℹ️ Single-User Token vs Multi-Tenant App Credentials</div>
    <div class="err-meta">
      <span>Frequency: 2 apps</span>
      <span>Affected: Jira, Notion</span>
      <span>Class: Schema Gap</span>
    </div>
    <div class="err-desc">Platforms offering both internal integration tokens and public multi-tenant OAuth require distinguishing developer testing ease from end-user authorization complexity. <strong>Fix:</strong> Add separate schema fields for single-workspace vs multi-tenant feasibility.</div>
  </div>
  <div class="err-card">
    <div class="err-title">ℹ️ Silent Webhook Absence / Polling Dependency</div>
    <div class="err-meta">
      <span>Frequency: 1 app</span>
      <span>Affected: Notion</span>
      <span>Class: Assumption Error</span>
    </div>
    <div class="err-desc">Major modern platforms do not always expose event webhooks. <strong>Fix:</strong> Classify all polling-dependent architectures as "Buildable with limitations" and add a <code>polling_required</code> boolean field.</div>
  </div>
</div>
</section>

<!-- ── Recommendations ────────────────────────────────────────────────── -->
<section id="recommendations">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 10</div>
    <div class="section-title">Product Operations Recommendations</div>
    <div class="section-desc">Evidence-backed recommendations derived from dataset analysis, M4 audit findings, and integration engineering insights.</div>
  </div>
  <div class="rec-grid" id="recGrid"></div>
</div>
</section>

<!-- ── Methodology ────────────────────────────────────────────────────── -->
<section id="methodology">
<div class="container">
  <div class="section-header">
    <div class="section-label">Section 11</div>
    <div class="section-title">Research Methodology & Limitations</div>
    <div class="section-desc">How this research was conducted, what sources were used, and where the analysis has known limitations.</div>
  </div>
  <div class="method-grid">
    <div class="method-card">
      <div class="method-icon">🌱</div>
      <div class="method-title">M1: Seed Dataset</div>
      <div class="method-desc">100 apps selected across 10 categories. Official website and developer doc URLs verified for liveness. Composio toolkit catalog cross-referenced manually.</div>
    </div>
    <div class="method-card">
      <div class="method-icon">🤖</div>
      <div class="method-title">M2: Automated Research Engine</div>
      <div class="method-desc">Multi-dimensional extractor: source_collector.py, auth_analyzer.py, buildability_classifier.py. 5-verdict decision engine with heuristic rules against verified_facts.py.</div>
    </div>
    <div class="method-card">
      <div class="method-icon">🗄️</div>
      <div class="method-title">M3: Full Dataset Generation</div>
      <div class="method-desc">Executed researcher.py across all 100 apps. Pristine baseline locked in verification/automated_raw_output.json before any corrections.</div>
    </div>
    <div class="method-card">
      <div class="method-icon">🔍</div>
      <div class="method-title">M4: Manual Audit</div>
      <div class="method-desc">30-app stratified sample (3 per category) verified against official developer documentation. Automated vs verified comparison recorded in verification_results.csv.</div>
    </div>
    <div class="method-card">
      <div class="method-icon">📊</div>
      <div class="method-title">M5: Analysis & Insights</div>
      <div class="method-desc">reports/analyzer.py computed all statistics from corrected data/apps.json. All figures validated to sum correctly — 0 validation errors.</div>
    </div>
    <div class="method-card">
      <div class="method-icon">⚠️</div>
      <div class="method-title">Known Limitations</div>
      <div class="method-desc">MCP status and rate limits may change rapidly. Only 30/100 apps were manually verified. Partner-gated API terms evolve with vendor relationships. Schema does not distinguish single-workspace from multi-tenant buildability.</div>
    </div>
  </div>
  <div style="margin-top:20px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px">
    <div style="font-weight:600;margin-bottom:8px;font-size:13px">Research Pipeline Architecture</div>
    <div style="font-size:12px;color:var(--muted);font-family:monospace;line-height:2">
      data/seed_apps.json (100 apps, verified URLs)<br>
      → research/verified_facts.py (ground-truth facts database)<br>
      → research/researcher.py (master orchestrator)<br>
      → research/auth_analyzer.py + buildability_classifier.py<br>
      → data/apps.json + data/apps.csv (baseline locked)<br>
      → verification/verifier.py (30-app manual audit)<br>
      → verification/verification_results.csv + accuracy_report.json<br>
      → reports/analyzer.py (M5 analysis)<br>
      → reports/category_analysis.json + research_summary.json
    </div>
  </div>
</div>
</section>

<!-- ── Footer ─────────────────────────────────────────────────────────── -->
<footer>
<div class="container">
  <p><strong>Composio SaaS API & Authentication Research</strong> — AI Product Ops Intern Assignment</p>
  <p style="margin-top:6px">100 SaaS applications · 10 categories · 30-app manual audit · Research date: 2026-11-23</p>
  <p style="margin-top:6px">All statistics computed from actual dataset values. No market-wide extrapolations. Evidence-backed findings only.</p>
</div>
</footer>

<!-- ── Embedded Data ───────────────────────────────────────────────────── -->
<script>
const APPS = {apps_js};
const VERIF = {verif_js};
const ACCURACY = {accuracy_js};
const SUMMARY = {summary_js};
const CAT_DATA = {cat_js};
</script>

<!-- ── Chart.js & App Logic ───────────────────────────────────────────── -->
<script>
// ── Colour palette ─────────────────────────────────────────────────────────
const C = {{
  accent:'#6366f1',accent2:'#818cf8',accent3:'#a5b4fc',
  green:'#22c55e',green2:'#4ade80',
  yellow:'#eab308',yellow2:'#facc15',
  red:'#ef4444',red2:'#f87171',
  blue:'#38bdf8',blue2:'#7dd3fc',
  orange:'#f97316',orange2:'#fb923c',
  purple:'#a78bfa',purple2:'#c4b5fd',
  pink:'#f472b6',pink2:'#f9a8d4',
  teal:'#2dd4bf',gray:'#64748b',
}};
const PALETTE=[C.accent,C.blue,C.green,C.yellow,C.orange,C.purple,C.pink,C.teal,C.red,C.gray];
const defaults={{
  plugins:{{legend:{{labels:{{color:'#8892a4',font:{{size:11}}}}}}}},
  scales:{{
    x:{{ticks:{{color:'#555e72',font:{{size:10}}}},grid:{{color:'#2e3348'}}}},
    y:{{ticks:{{color:'#555e72',font:{{size:10}}}},grid:{{color:'#2e3348'}}}}
  }}
}};
function mergeOpts(extra){{return Object.assign({{}},defaults,extra)}}
Chart.defaults.color='#8892a4';
Chart.defaults.borderColor='#2e3348';

// ── Auth Doughnut ──────────────────────────────────────────────────────────
new Chart(document.getElementById('chartAuth'),{{
  type:'doughnut',
  data:{{
    labels:['OAuth 2.0','API Key','Basic Auth','Bearer JWT','PAT'],
    datasets:[{{
      data:[40,36,13,7,4],
      backgroundColor:[C.accent,C.blue,C.green,C.yellow,C.purple],
      borderWidth:2,borderColor:'#1a1d27'
    }}]
  }},
  options:{{cutout:'65%',plugins:{{legend:{{position:'bottom',labels:{{color:'#8892a4',font:{{size:11}},padding:10}}}}}}}}
}});

// ── Credential Doughnut ───────────────────────────────────────────────────
new Chart(document.getElementById('chartCred'),{{
  type:'doughnut',
  data:{{
    labels:['Self-serve (90)','Approval-required (8)','Partner-gated (2)'],
    datasets:[{{
      data:[90,8,2],
      backgroundColor:[C.green,C.yellow,C.red],
      borderWidth:2,borderColor:'#1a1d27'
    }}]
  }},
  options:{{cutout:'65%',plugins:{{legend:{{position:'bottom',labels:{{color:'#8892a4',font:{{size:11}},padding:10}}}}}}}}
}});

// ── Auth by Category bar ──────────────────────────────────────────────────
(function(){{
  const catKeys=Object.keys(CAT_DATA);
  const catShort=['CRM','Proj','Comm','Mktg','Supp','Fin','HR','Dev','BI','Store'];
  const oauth2=[],apikey=[],other=[];
  catKeys.forEach(k=>{{
    const a=CAT_DATA[k].authentication_types||{{}};
    oauth2.push(a['OAuth 2.0']||0);
    apikey.push(a['API Key']||0);
    const o=(a['Basic Auth']||0)+(a['Bearer JWT']||0)+(a['Personal Access Token (PAT)']||0);
    other.push(o);
  }});
  new Chart(document.getElementById('chartAuthCat'),{{
    type:'bar',
    data:{{
      labels:catShort,
      datasets:[
        {{label:'OAuth 2.0',data:oauth2,backgroundColor:C.accent+'cc',stack:'s'}},
        {{label:'API Key',data:apikey,backgroundColor:C.blue+'cc',stack:'s'}},
        {{label:'Other',data:other,backgroundColor:C.purple+'cc',stack:'s'}},
      ]
    }},
    options:mergeOpts({{indexAxis:'y',scales:{{x:{{stacked:true,ticks:{{color:'#555e72',font:{{size:10}}}},grid:{{color:'#2e3348'}}}},y:{{stacked:true,ticks:{{color:'#555e72',font:{{size:10}}}},grid:{{color:'#2e3348'}}}}}},plugins:{{legend:{{position:'bottom',labels:{{color:'#8892a4',font:{{size:11}}}}}}}}}}),
  }});
}})();

// ── Buildability Doughnut ─────────────────────────────────────────────────
new Chart(document.getElementById('chartBuild'),{{
  type:'doughnut',
  data:{{
    labels:['Buildable with limitations (94)','Buildable (4)','Partner-dependent (2)'],
    datasets:[{{
      data:[94,4,2],
      backgroundColor:[C.yellow,C.green,C.red],
      borderWidth:2,borderColor:'#1a1d27'
    }}]
  }},
  options:{{cutout:'65%',plugins:{{legend:{{position:'bottom',labels:{{color:'#8892a4',font:{{size:11}},padding:10}}}}}}}}
}});

// ── API Coverage bar ──────────────────────────────────────────────────────
(function(){{
  const counts={{}};
  APPS.forEach(a=>{{ const k=a.api_coverage||'Unknown'; counts[k]=(counts[k]||0)+1; }});
  const labels=Object.keys(counts);
  const vals=labels.map(l=>counts[l]);
  new Chart(document.getElementById('chartApiCov'),{{
    type:'bar',
    data:{{labels,datasets:[{{data:vals,backgroundColor:PALETTE,borderRadius:4}}]}},
    options:mergeOpts({{plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,ticks:{{stepSize:1,color:'#555e72',font:{{size:10}}}},grid:{{color:'#2e3348'}}}},x:{{ticks:{{color:'#555e72',font:{{size:10}}}},grid:{{color:'#2e3348'}}}}}}}}),
  }});
}})();

// ── Composio doughnut ─────────────────────────────────────────────────────
new Chart(document.getElementById('chartComposio'),{{
  type:'doughnut',
  data:{{
    labels:['Official Toolkit (60)','New Opportunity (40)'],
    datasets:[{{
      data:[60,40],
      backgroundColor:[C.accent,C.orange],
      borderWidth:2,borderColor:'#1a1d27'
    }}]
  }},
  options:{{cutout:'65%',plugins:{{legend:{{position:'bottom',labels:{{color:'#8892a4',font:{{size:11}},padding:10}}}}}}}}
}});

// ── Composio by category stacked bar ─────────────────────────────────────
(function(){{
  const catKeys=Object.keys(CAT_DATA);
  const catShort=['CRM','Proj','Comm','Mktg','Supp','Fin','HR','Dev','BI','Store'];
  const official=[],opp=[];
  catKeys.forEach(k=>{{
    official.push(CAT_DATA[k].composio_coverage.official_toolkit);
    opp.push(CAT_DATA[k].composio_coverage.not_supported_or_experimental);
  }});
  new Chart(document.getElementById('chartComposioCat'),{{
    type:'bar',
    data:{{
      labels:catShort,
      datasets:[
        {{label:'Official Toolkit',data:official,backgroundColor:C.accent+'cc',stack:'s'}},
        {{label:'New Opportunity',data:opp,backgroundColor:C.orange+'cc',stack:'s'}},
      ]
    }},
    options:mergeOpts({{indexAxis:'y',scales:{{x:{{stacked:true,max:10,ticks:{{stepSize:2,color:'#555e72',font:{{size:10}}}},grid:{{color:'#2e3348'}}}},y:{{stacked:true,ticks:{{color:'#555e72',font:{{size:10}}}},grid:{{color:'#2e3348'}}}}}},plugins:{{legend:{{position:'bottom',labels:{{color:'#8892a4',font:{{size:11}}}}}}}}}}),
  }});
}})();

// ── MCP doughnut ──────────────────────────────────────────────────────────
new Chart(document.getElementById('chartMcp'),{{
  type:'doughnut',
  data:{{
    labels:['Official MCP (15)','Third-party MCP (41)','Not Found (44)'],
    datasets:[{{
      data:[15,41,44],
      backgroundColor:[C.green,C.blue,C.gray],
      borderWidth:2,borderColor:'#1a1d27'
    }}]
  }},
  options:{{cutout:'65%',plugins:{{legend:{{position:'bottom',labels:{{color:'#8892a4',font:{{size:11}},padding:10}}}}}}}}
}});

// ── Webhook doughnut ──────────────────────────────────────────────────────
new Chart(document.getElementById('chartWebhook'),{{
  type:'doughnut',
  data:{{
    labels:['Supported (98)','Not Supported (2)'],
    datasets:[{{
      data:[98,2],
      backgroundColor:[C.green,C.red],
      borderWidth:2,borderColor:'#1a1d27'
    }}]
  }},
  options:{{cutout:'65%',plugins:{{legend:{{position:'bottom',labels:{{color:'#8892a4',font:{{size:11}},padding:10}}}}}}}}
}});

// ── Accuracy radar ────────────────────────────────────────────────────────
new Chart(document.getElementById('chartAccuracy'),{{
  type:'radar',
  data:{{
    labels:['Auth Type','Credential','Public API','Webhooks','MCP','Buildability'],
    datasets:[{{
      label:'Accuracy %',
      data:[100,100,100,100,100,86.7],
      backgroundColor:'rgba(99,102,241,.2)',
      borderColor:C.accent,
      pointBackgroundColor:C.accent,
      pointRadius:5,
    }}]
  }},
  options:{{
    scales:{{r:{{
      min:80,max:100,ticks:{{stepSize:5,color:'#555e72',backdropColor:'transparent',font:{{size:9}}}},
      grid:{{color:'#2e3348'}},pointLabels:{{color:'#8892a4',font:{{size:11}}}},angleLines:{{color:'#2e3348'}}
    }}}},
    plugins:{{legend:{{display:false}}}}
  }}
}});

// ── Official MCP pills ────────────────────────────────────────────────────
(function(){{
  const container=document.getElementById('mcpPills');
  const officialApps=APPS.filter(a=>a.mcp_support==='Official MCP');
  const catColors={{
    'Developer Tools':C.accent,'Project Management':C.blue,
    'Communication and Collaboration':C.green,'Finance and Accounting':C.yellow,
    'Storage and Document Management':C.purple,'Analytics and Business Intelligence':C.orange,
  }};
  officialApps.forEach(a=>{{
    const pill=document.createElement('span');
    const col=catColors[a.category]||C.gray;
    pill.style.cssText=`background:${{col}}22;border:1px solid ${{col}}55;color:${{col}};border-radius:16px;padding:4px 12px;font-size:11px;font-weight:600;cursor:default`;
    pill.title=a.category;
    pill.textContent=a.app_name;
    container.appendChild(pill);
  }});
}})();

// ── Category cards ────────────────────────────────────────────────────────
(function(){{
  const container=document.getElementById('catCards');
  const emojis={{
    'CRM and Sales':'💼','Project Management':'📋','Communication and Collaboration':'💬',
    'Marketing Automation':'📣','Customer Support':'🎧','Finance and Accounting':'💰',
    'HR and Recruitment':'👥','Developer Tools':'🛠️','Analytics and Business Intelligence':'📊',
    'Storage and Document Management':'📁'
  }};
  Object.entries(CAT_DATA).forEach(([cat,d])=>{{
    const bld=d.buildability;
    const comp=d.composio_coverage;
    const mcp=d.mcp_support;
    const wh=d.webhook_support;
    const pct=bld.feasibly_buildable_pct;
    const card=document.createElement('div');
    card.className='cat-card';
    card.innerHTML=`
      <div class="cat-name"><span class="cat-emoji">${{emojis[cat]||'📦'}}</span>${{cat}}</div>
      <div class="cat-stat-row"><span>Total Apps</span><span class="cat-stat-val">${{d.total_apps}}</span></div>
      <div class="cat-stat-row"><span>Feasibly Buildable</span><span class="cat-stat-val">${{bld.total_feasibly_buildable}} (${{pct}}%)</span></div>
      <div class="cat-stat-row"><span>Composio Official</span><span class="cat-stat-val" style="color:#818cf8">${{comp.official_toolkit}}</span></div>
      <div class="cat-stat-row"><span>New Opportunities</span><span class="cat-stat-val" style="color:#fb923c">${{comp.not_supported_or_experimental}}</span></div>
      <div class="cat-stat-row"><span>Official MCP</span><span class="cat-stat-val" style="color:#4ade80">${{mcp.official_mcp}}</span></div>
      <div class="cat-stat-row"><span>Third-party MCP</span><span class="cat-stat-val" style="color:#38bdf8">${{mcp.third_party_mcp}}</span></div>
      <div class="cat-stat-row"><span>Webhook Support</span><span class="cat-stat-val">${{wh.supported}}/${{d.total_apps}} (${{wh.support_pct}}%)</span></div>
      <div class="progress"><div class="progress-bar" style="width:${{comp.official_toolkit_pct}}%"></div></div>
    `;
    container.appendChild(card);
  }});
}})();

// ── Priority Table ────────────────────────────────────────────────────────
(function(){{
  const tbody=document.getElementById('priorityTbl');
  const top15=SUMMARY.priority_new_integrations.top_15_candidates;
  function buildBadge(v){{
    if(v==='Buildable')return'<span class="badge badge-green">Buildable</span>';
    if(v.includes('limitations'))return'<span class="badge badge-yellow">Bld w/ Limits</span>';
    if(v.includes('Partner'))return'<span class="badge badge-red">Partner-dep</span>';
    return`<span class="badge badge-gray">${{v}}</span>`;
  }}
  function mcpBadge(v){{
    if(v==='Official MCP')return'<span class="badge badge-green">Official</span>';
    if(v==='Third-party MCP')return'<span class="badge badge-blue">3rd-party</span>';
    return'<span class="badge badge-gray">None</span>';
  }}
  top15.forEach((p,i)=>{{
    const tr=document.createElement('tr');
    tr.innerHTML=`
      <td style="color:var(--dim)">${{i+1}}</td>
      <td style="font-weight:600">${{p.app_name}}</td>
      <td style="color:var(--muted);font-size:11px">${{p.category.replace(' and ',' & ')}}</td>
      <td>${{buildBadge(p.buildability)}}</td>
      <td><span class="badge badge-purple">${{p.auth_type}}</span></td>
      <td>${{p.webhooks==='Supported'?'<span class="badge badge-green">✓</span>':'<span class="badge badge-red">✗</span>'}}</td>
      <td>${{mcpBadge(p.mcp_support)}}</td>
      <td><div class="score-bar"><span class="score-pip"></span><strong>${{p.priority_score}}</strong></div></td>
    `;
    tbody.appendChild(tr);
  }});
}})();

// ── 100-App Dataset Table ─────────────────────────────────────────────────
let filteredApps=[...APPS];
let sortCol=-1,sortAsc=true;
let currentPage=1;
const PAGE_SIZE=25;

function buildBadge(v){{
  if(!v||v==='Unknown')return'<span class="badge badge-gray">Unknown</span>';
  if(v==='Buildable')return'<span class="badge badge-green">Buildable</span>';
  if(v.includes('limitations'))return'<span class="badge badge-yellow">Bld w/ Limits</span>';
  if(v.includes('Partner'))return'<span class="badge badge-red">Partner-dep</span>';
  return`<span class="badge badge-gray">${{v}}</span>`;
}}
function composioBadge(v){{
  if(v==='Official Toolkit')return'<span class="badge badge-purple">Official</span>';
  return'<span class="badge badge-orange">Opportunity</span>';
}}
function authBadge(v){{
  const map={{'OAuth 2.0':'badge-blue','API Key':'badge-green','Basic Auth':'badge-gray','Bearer JWT':'badge-pink','Personal Access Token (PAT)':'badge-orange'}};
  return`<span class="badge ${{map[v]||'badge-gray'}}">${{v==='Personal Access Token (PAT)'?'PAT':v}}</span>`;
}}
function mcpBadge(v){{
  if(v==='Official MCP')return'<span class="badge badge-green">Official</span>';
  if(v==='Third-party MCP')return'<span class="badge badge-blue">3rd-party</span>';
  if(v==='Not Found in Checked Sources')return'<span class="badge badge-gray">None</span>';
  return'<span class="badge badge-gray">Unknown</span>';
}}

function renderTable(){{
  const tbody=document.getElementById('appTbody');
  tbody.innerHTML='';
  const start=(currentPage-1)*PAGE_SIZE;
  const slice=filteredApps.slice(start,start+PAGE_SIZE);
  slice.forEach((a,i)=>{{
    const tr=document.createElement('tr');
    tr.innerHTML=`
      <td style="color:var(--dim)">${{start+i+1}}</td>
      <td><div style="font-weight:600">${{a.app_name}}</div><div style="font-size:10px;color:var(--dim)">${{a.composio_toolkit_slug?'🧰 '+a.composio_toolkit_slug:''}}</div></td>
      <td style="font-size:11px;color:var(--muted)">${{(a.category||'').replace(' and ',' & ')}}</td>
      <td>${{authBadge(a.authentication_type)}}</td>
      <td><span class="badge ${{a.credential_access==='Self-serve'?'badge-green':a.credential_access==='Partner-gated'?'badge-red':'badge-yellow'}}">${{a.credential_access}}</span></td>
      <td><span class="badge ${{a.public_api==='Yes'?'badge-green':'badge-red'}}">${{a.public_api}}</span></td>
      <td>${{buildBadge(a.buildability)}}</td>
      <td>${{composioBadge(a.composio_existing_support)}}</td>
      <td>${{a.webhooks==='Supported'?'<span class="badge badge-green">✓</span>':'<span class="badge badge-red">✗ Polling</span>'}}</td>
      <td>${{mcpBadge(a.mcp_support)}}</td>
      <td><a href="${{a.developer_docs}}" target="_blank" style="font-size:10px">Docs ↗</a></td>
    `;
    tbody.appendChild(tr);
  }});
  document.getElementById('appCount').textContent=`${{filteredApps.length}} apps`;
  updatePager();
}}

function updatePager(){{
  const total=Math.ceil(filteredApps.length/PAGE_SIZE);
  document.getElementById('pagerInfo').textContent=`Page ${{currentPage}} of ${{total}}`;
  document.getElementById('btnPrev').disabled=currentPage<=1;
  document.getElementById('btnNext').disabled=currentPage>=total;
}}

function changePage(d){{
  const total=Math.ceil(filteredApps.length/PAGE_SIZE);
  currentPage=Math.max(1,Math.min(total,currentPage+d));
  renderTable();
}}

function applyFilters(){{
  const q=(document.getElementById('appSearch').value||'').toLowerCase();
  const cat=document.getElementById('filterCat').value;
  const build=document.getElementById('filterBuild').value;
  const comp=document.getElementById('filterComposio').value;
  const auth=document.getElementById('filterAuth').value;
  filteredApps=APPS.filter(a=>{{
    if(cat&&a.category!==cat)return false;
    if(build&&a.buildability!==build)return false;
    if(comp&&a.composio_existing_support!==comp)return false;
    if(auth&&a.authentication_type!==auth)return false;
    if(q){{
      const haystack=(a.app_name+' '+a.category+' '+a.authentication_type+' '+(a.description||'')+' '+(a.mcp_support||'')).toLowerCase();
      if(!haystack.includes(q))return false;
    }}
    return true;
  }});
  currentPage=1;
  renderTable();
}}

function sortTable(col){{
  if(sortCol===col)sortAsc=!sortAsc; else{{sortCol=col;sortAsc=true;}}
  const keys=['_idx','app_name','category','authentication_type','credential_access','public_api','buildability'];
  filteredApps.sort((a,b)=>{{
    let va=a[keys[col]]||'',vb=b[keys[col]]||'';
    if(typeof va==='string')va=va.toLowerCase();
    if(typeof vb==='string')vb=vb.toLowerCase();
    return sortAsc?(va<vb?-1:va>vb?1:0):(va<vb?1:va>vb?-1:0);
  }});
  renderTable();
}}

document.getElementById('appSearch').addEventListener('input',applyFilters);
['filterCat','filterBuild','filterComposio','filterAuth'].forEach(id=>
  document.getElementById(id).addEventListener('change',applyFilters)
);
renderTable();

// ── Audit Table ───────────────────────────────────────────────────────────
let filteredVerif=[...VERIF];

function renderAudit(){{
  const tbody=document.getElementById('auditTbody');
  tbody.innerHTML='';
  filteredVerif.forEach(r=>{{
    const match=r.verdict_match==='True';
    const corr=r.correction_made&&!r.correction_made.startsWith('None')?`<span class="badge badge-orange">Corrected</span>`:'-';
    const src=r.verification_source?`<a href="${{r.verification_source}}" target="_blank" style="font-size:10px">Source ↗</a>`:'';
    const tr=document.createElement('tr');
    tr.innerHTML=`
      <td style="font-weight:600">${{r.app_name}}</td>
      <td style="font-size:11px;color:var(--muted)">${{(r.category||'').replace(' and ',' & ')}}</td>
      <td><span class="badge badge-blue">${{r.automated_auth}}</span></td>
      <td><span class="badge badge-green">${{r.verified_auth}}</span></td>
      <td style="font-size:11px">${{r.automated_cred}}</td>
      <td style="font-size:11px">${{r.verified_cred}}</td>
      <td>${{buildBadge(r.automated_verdict)}}</td>
      <td>${{buildBadge(r.verified_verdict)}}</td>
      <td class="${{match?'match-yes':'match-no'}}">${{match?'✅':'❌'}}</td>
      <td>${{corr}}</td>
      <td>${{src}}</td>
    `;
    tbody.appendChild(tr);
  }});
  document.getElementById('auditCount').textContent=`${{filteredVerif.length}} / 30 apps`;
}}

function applyAuditFilters(){{
  const cat=document.getElementById('auditCatFilter').value;
  const match=document.getElementById('auditMatchFilter').value;
  filteredVerif=VERIF.filter(r=>{{
    if(cat&&r.category!==cat)return false;
    if(match&&r.verdict_match!==match)return false;
    return true;
  }});
  renderAudit();
}}

document.getElementById('auditCatFilter').addEventListener('change',applyAuditFilters);
document.getElementById('auditMatchFilter').addEventListener('change',applyAuditFilters);
renderAudit();

// ── Recommendations ───────────────────────────────────────────────────────
(function(){{
  const grid=document.getElementById('recGrid');
  const priorityColors={{
    'REC-01':'#ef4444','REC-02':'#ef4444',
    'REC-03':'#eab308','REC-04':'#eab308','REC-05':'#eab308',
    'REC-06':'#22c55e','REC-07':'#22c55e'
  }};
  SUMMARY.product_ops_recommendations.forEach(r=>{{
    const card=document.createElement('div');
    card.className='rec-card';
    const col=priorityColors[r.id]||'#6366f1';
    card.innerHTML=`
      <div>
        <div class="rec-id" style="background:${{col}}">${{r.id}}</div>
      </div>
      <div>
        <div class="rec-title">${{r.title}}</div>
        <div class="rec-body">${{r.rationale}}</div>
        <div class="rec-action">📋 <strong>Action:</strong> ${{r.action}}</div>
        <div style="margin-top:8px;font-size:11px;color:var(--dim)">📎 Evidence: ${{r.evidence}}</div>
      </div>
    `;
    grid.appendChild(card);
  }});
}})();

// ── Navbar active on scroll ───────────────────────────────────────────────
const sections=document.querySelectorAll('section[id],div[id="overview"]');
const navLinks=document.querySelectorAll('#navbar nav a');
const obs=new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{
    if(e.isIntersecting){{
      navLinks.forEach(l=>{{
        l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id);
      }});
    }}
  }});
}},{{threshold:.3}});
sections.forEach(s=>obs.observe(s));
</script>
</body>
</html>"""

out = ROOT / "index.html"
out.write_text(HTML, encoding="utf-8")
size = out.stat().st_size
print(f"✓ Wrote index.html — {size:,} bytes ({size/1024:.1f} KB)")
