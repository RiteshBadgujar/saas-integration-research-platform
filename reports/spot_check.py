"""Quick spot-check of M5 output files."""
import json

# ── Category analysis spot-check ─────────────────────────────────────────────
cat = json.load(open("reports/category_analysis.json"))
print("=== CATEGORY ANALYSIS SPOT-CHECK ===")
for c, d in cat.items():
    bld = d["buildability"]
    comp = d["composio_coverage"]
    mcp = d["mcp_support"]
    total_apps = d["total_apps"]
    buildable = bld["total_feasibly_buildable"]
    composio = comp["official_toolkit"]
    opportunity = comp["not_supported_or_experimental"]
    official_mcp = mcp["official_mcp"]
    third_mcp = mcp["third_party_mcp"]
    print(
        f"{c[:30]:30s} | apps={total_apps} | "
        f"buildable={buildable} | composio={composio} | "
        f"opportunity={opportunity} | official_mcp={official_mcp} | 3rd_mcp={third_mcp}"
    )

# ── Summary spot-check ────────────────────────────────────────────────────────
print()
print("=== RESEARCH SUMMARY SPOT-CHECK ===")
s = json.load(open("reports/research_summary.json"))

print("Auth distribution:")
for k, v in s["authentication_analysis"]["distribution"].items():
    print(f"  {k}: {v['count']} ({v['pct']}%)")

print()
print("Credential access:")
for k, v in s["credential_access_analysis"]["distribution"].items():
    print(f"  {k}: {v['count']} ({v['pct']}%)")

print()
print("Buildability:")
for k, v in s["buildability_analysis"]["distribution"].items():
    print(f"  {k}: {v['count']} ({v['pct']}%)")

print()
print("Composio coverage:")
c2 = s["composio_coverage_analysis"]
print(f"  Official Toolkit:  {c2['official_toolkit_count']} ({c2['official_toolkit_pct']}%)")
print(f"  New Opportunities: {c2['new_opportunity_count']} ({c2['new_opportunity_pct']}%)")

print()
print("Top 10 Priority Integration Candidates:")
for i, p in enumerate(s["priority_new_integrations"]["top_15_candidates"][:10], 1):
    app = p["app_name"]
    cat_name = p["category"][:20]
    score = p["priority_score"]
    print(f"  {i:2d}. {app:<22s} cat={cat_name:<22s} score={score}")

print()
print("Official MCP apps:")
for m in s["mcp_analysis"]["official_mcp_apps"]:
    print(f"  {m['app_name']} ({m['category']})")

print()
print("Webhook analysis:")
wh = s["webhook_analysis"]
print(f"  Supported: {wh['supported_count']} ({wh['support_pct']}%)")
print(f"  Not supported: {wh['not_supported_count']}")
print(f"  Apps without webhooks: {wh['apps_without_webhooks']}")

print()
print("Product Ops Recommendations:")
for r in s["product_ops_recommendations"]:
    print(f"  {r['id']}: {r['title']}")

print()
print("M4 Audit Summary:")
m4 = s["m4_audit_findings"]
print(f"  Overall accuracy: {m4['overall_verdict_accuracy_pct']}%")
print(f"  Correct: {m4['correct_verdicts']}/30")
print(f"  Perfect fields: {m4['perfect_fields']}")
print(f"  Suboptimal fields: {m4['suboptimal_fields']}")
