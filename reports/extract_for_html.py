"""Extract all data needed for embedding in the HTML case study."""
import json, csv

apps = json.load(open("data/apps.json", encoding="utf-8"))
accuracy = json.load(open("verification/accuracy_report.json", encoding="utf-8"))
cat_analysis = json.load(open("reports/category_analysis.json", encoding="utf-8"))
summary = json.load(open("reports/research_summary.json", encoding="utf-8"))

# Read verification results CSV
verif_rows = []
with open("verification/verification_results.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        verif_rows.append(dict(row))

print("APPS (first record keys):", list(apps[0].keys()))
print("TOTAL APPS:", len(apps))
print("VERIF ROWS:", len(verif_rows))
print("VERIF COLUMNS:", list(verif_rows[0].keys()) if verif_rows else "NONE")
print()
print("--- SUMMARY AUTH ---")
print(json.dumps(summary["authentication_analysis"]["distribution"], indent=2))
print()
print("--- SUMMARY CRED ---")
print(json.dumps(summary["credential_access_analysis"]["distribution"], indent=2))
print()
print("--- BUILDABILITY ---")
print(json.dumps(summary["buildability_analysis"]["distribution"], indent=2))
print()
print("--- COMPOSIO ---")
print("Official:", summary["composio_coverage_analysis"]["official_toolkit_count"])
print("Opportunity:", summary["composio_coverage_analysis"]["new_opportunity_count"])
print()
print("--- MCP ---")
print("Official:", summary["mcp_analysis"]["official_mcp_count"])
print("Third-party:", summary["mcp_analysis"]["third_party_mcp_count"])
print("Not found:", summary["mcp_analysis"]["not_found_count"])
print()
print("--- TOP 15 CANDIDATES ---")
for c in summary["priority_new_integrations"]["top_15_candidates"]:
    print(f"  {c['app_name']}: score={c['priority_score']} cat={c['category']} auth={c['auth_type']} build={c['buildability']}")
print()
print("--- VERIF ROWS sample ---")
if verif_rows:
    for k, v in verif_rows[0].items():
        print(f"  {k}: {v[:60] if isinstance(v, str) else v}")
