"""Validate index.html: structure, embedded data integrity, JS syntax indicators."""
import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "index.html").read_text(encoding="utf-8")

errors = []
warnings = []

# ── Basic structure ────────────────────────────────────────────────────────
for tag in ["<!DOCTYPE html>", "<html", "</html>", "<head>", "</head>", "<body>", "</body>"]:
    if tag not in html:
        errors.append(f"Missing: {tag}")
    else:
        print(f"  ✓ {tag}")

# ── Chart.js CDN ───────────────────────────────────────────────────────────
if "chart.js" in html.lower() or "Chart.js" in html:
    print("  ✓ Chart.js CDN present")
else:
    errors.append("Missing Chart.js CDN")

# ── Section IDs ──────────────────────────────────────────────────────────
sections = ["overview","auth","buildability","composio","mcp","categories","dataset","audit","accuracy","recommendations","methodology"]
for s in sections:
    if f'id="{s}"' in html:
        print(f"  ✓ section #{s}")
    else:
        errors.append(f"Missing section: #{s}")

# ── Embedded data ─────────────────────────────────────────────────────────
# Extract APPS array
apps_match = re.search(r'const APPS = (\[.*?\]);', html, re.DOTALL)
if apps_match:
    apps = json.loads(apps_match.group(1))
    print(f"  ✓ APPS embedded: {len(apps)} records")
    if len(apps) != 100:
        errors.append(f"APPS count is {len(apps)}, expected 100")
else:
    errors.append("APPS not found in HTML")

verif_match = re.search(r'const VERIF = (\[.*?\]);', html, re.DOTALL)
if verif_match:
    verif = json.loads(verif_match.group(1))
    print(f"  ✓ VERIF embedded: {len(verif)} records")
    if len(verif) != 30:
        errors.append(f"VERIF count is {len(verif)}, expected 30")
else:
    errors.append("VERIF not found in HTML")

summary_match = re.search(r'const SUMMARY = (\{.*?\});', html, re.DOTALL)
if summary_match:
    summary = json.loads(summary_match.group(1))
    print("  ✓ SUMMARY embedded")
    top15_count = len(summary.get("priority_new_integrations", {}).get("top_15_candidates", []))
    print(f"    top 15 candidates: {top15_count}")
    recs_count = len(summary.get("product_ops_recommendations", []))
    print(f"    recommendations: {recs_count}")
else:
    errors.append("SUMMARY not found in HTML")

# ── Canvas IDs for charts ──────────────────────────────────────────────────
chart_ids = ["chartAuth","chartCred","chartAuthCat","chartBuild","chartApiCov",
             "chartComposio","chartComposioCat","chartMcp","chartWebhook","chartAccuracy"]
for cid in chart_ids:
    if f'id="{cid}"' in html:
        print(f"  ✓ canvas #{cid}")
    else:
        errors.append(f"Missing canvas: #{cid}")

# ── Table IDs ──────────────────────────────────────────────────────────────
for tid in ["appTable","appTbody","auditTable","auditTbody","priorityTbl"]:
    if f'id="{tid}"' in html:
        print(f"  ✓ table #{tid}")
    else:
        errors.append(f"Missing table: #{tid}")

# ── Filter controls ────────────────────────────────────────────────────────
for fid in ["appSearch","filterCat","filterBuild","filterComposio","filterAuth","auditCatFilter","auditMatchFilter"]:
    if f'id="{fid}"' in html:
        print(f"  ✓ filter #{fid}")
    else:
        errors.append(f"Missing filter: #{fid}")

# ── Key stats in content ───────────────────────────────────────────────────
for stat in ["86.7%","98%","60","40 new","15","90%"]:
    if stat in html:
        print(f"  ✓ stat '{stat}' found")
    else:
        warnings.append(f"Stat '{stat}' not found in HTML text")

# ── File size check ────────────────────────────────────────────────────────
size = (ROOT / "index.html").stat().st_size
print(f"\n  File size: {size:,} bytes ({size/1024:.1f} KB)")

# ── Report ─────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors: print(f"  ✗ {e}")
else:
    print("✓ All validation checks passed — 0 errors")
if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings: print(f"  ⚠ {w}")
