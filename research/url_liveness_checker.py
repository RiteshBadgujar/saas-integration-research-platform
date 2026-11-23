"""
URL Liveness and Documentation Reachability Checker.
Validates HTTP response codes and redirects for seed URLs with connection pooling and timeouts.
"""

import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 ComposioResearchBot/1.0"
}


def check_url(app_name: str, url_type: str, url: str) -> dict:
    try:
        # Use GET with stream=True so we only fetch headers without loading full bodies
        res = requests.get(url, headers=HEADERS, timeout=7, stream=True, allow_redirects=True)
        return {
            "app_name": app_name,
            "url_type": url_type,
            "url": url,
            "status_code": res.status_code,
            "reachable": res.status_code < 400 or res.status_code in [401, 403], # 401/403 means site exists but requires auth/waf
            "final_url": res.url,
            "error": None
        }
    except Exception as e:
        return {
            "app_name": app_name,
            "url_type": url_type,
            "url": url,
            "status_code": None,
            "reachable": False,
            "final_url": url,
            "error": str(e)
        }


def check_seed_urls(seed_file: Path = Path("data/seed_apps.json"), max_workers: int = 10, sample_only: bool = True):
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # If sample_only is True, check the 30 manual verification sample apps
    targets = [item for item in data if item.get("is_manual_sample", False)] if sample_only else data
    print(f"Checking URL liveness for {len(targets)} applications ({len(targets) * 2} URLs)...")

    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for app in targets:
            tasks.append(executor.submit(check_url, app["app_name"], "official_website", app["official_website"]))
            tasks.append(executor.submit(check_url, app["app_name"], "developer_docs", app["developer_docs"]))

        results = []
        for future in as_completed(tasks):
            results.append(future.result())

    reachable_count = sum(1 for r in results if r["reachable"])
    total_urls = len(results)
    print(f"Results: {reachable_count}/{total_urls} URLs reachable ({(reachable_count/total_urls)*100:.1f}%).")

    unreachable = [r for r in results if not r["reachable"]]
    if unreachable:
        print("\nUnreachable or blocked URLs:")
        for u in unreachable:
            print(f"  ✗ {u['app_name']} ({u['url_type']}): {u['url']} -> {u['status_code'] or u['error']}")
    else:
        print("✓ All tested URLs are active and responsive!")

    return results


if __name__ == "__main__":
    check_seed_urls()
