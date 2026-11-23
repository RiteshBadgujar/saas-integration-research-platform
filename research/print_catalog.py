import json

with open("data/seed_apps.json", "r", encoding="utf-8") as f:
    apps = json.load(f)

print(f"Total: {len(apps)} apps\n")
for i, a in enumerate(apps, 1):
    sample = "⭐ AUDIT" if a.get("is_manual_sample") else "  "
    comp = a.get("composio_existing_support")
    slug = f"({a.get('composio_toolkit_slug')})" if a.get("composio_toolkit_slug") else "(none)"
    print(f"{i:3d}. [{a['category']:32s}] {a['app_name']:18s} | {sample:8s} | {comp:18s} {slug:16s} | {a['developer_docs']}")
