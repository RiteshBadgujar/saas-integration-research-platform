"""
Source Collector: Fetches, normalizes, and locally caches documentation pages.
Includes timeout protection, exponential backoff, headers, and text parsing.
"""

import os
import re
import time
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("source_collector")

CACHE_DIR = Path("scratch/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 ComposioResearchAgent/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}


class SourceCollector:
    """Fetches web documentation and caches raw HTML and cleaned text locally."""

    def __init__(self, cache_dir: Path = CACHE_DIR, timeout: int = 10, max_retries: int = 2):
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", url.replace("https://", "").replace("http://", ""))[:40]
        return self.cache_dir / f"{safe_name}_{url_hash}.html"

    def fetch_url(self, url: str, force_refresh: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetches URL with local caching.
        Returns: (raw_html, error_message)
        """
        cache_file = self._get_cache_path(url)

        if not force_refresh and cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return f.read(), None
            except Exception as e:
                logger.warning(f"Failed to read cache for {url}: {e}")

        # Live fetch with retry
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                if response.status_code == 200:
                    html = response.text
                    try:
                        with open(cache_file, "w", encoding="utf-8") as f:
                            f.write(html)
                    except Exception as e:
                        logger.warning(f"Failed to write cache for {url}: {e}")
                    return html, None
                elif response.status_code in [401, 403, 429]:
                    return None, f"HTTP {response.status_code} (Protected / Rate limited)"
                else:
                    return None, f"HTTP {response.status_code}"
            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    return None, "Request timed out"
                time.sleep(1 * (attempt + 1))
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    return None, str(e)
                time.sleep(1 * (attempt + 1))

        return None, "Unknown network error"

    def extract_text_and_links(self, html: str, base_url: str) -> Dict[str, any]:
        """Parses HTML into searchable text, headings, and relevant documentation links."""
        if not html:
            return {"title": "", "text": "", "headings": [], "links": []}

        soup = BeautifulSoup(html, "html.parser")

        # Strip unhelpful elements
        for element in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        headings = []
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                text = h.get_text().strip()
                if text:
                    headings.append(text)

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            anchor_text = a.get_text().strip()
            if any(term in href.lower() or term in anchor_text.lower() for term in ["auth", "oauth", "api-key", "token", "webhook", "rate-limit", "mcp"]):
                if href.startswith("/"):
                    # Resolve relative link
                    domain = "/".join(base_url.split("/")[:3])
                    href = domain + href
                if href.startswith("http"):
                    links.append({"url": href, "text": anchor_text})

        text = soup.get_text(separator=" ", strip=True)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return {
            "title": title,
            "text": text,
            "headings": headings[:30],
            "relevant_links": links[:15]
        }
