"""Runtime configuration. Everything is overridable through environment variables."""

from __future__ import annotations

import os
import sys
from pathlib import Path

VERSION = "0.1.0"
PROJECT_URL = "https://github.com/meteofix/wikipedia-interest-research"

# Wikimedia rate-limits clients without contact info in the User-Agent to 10 requests/min;
# identified clients get 200/min. 3 requests/s (180/min) stays under that with headroom.
MAX_RPS = float(os.environ.get("WIKI_MAX_RPS", "3"))
# Wikimedia asks API clients to keep at most 3 concurrent requests.
MAX_CONCURRENCY = 3
# Multi-year daily series are ~100 KB; 30 s covers slow networks without hanging forever.
REQUEST_TIMEOUT = 30
# Transient 429/5xx usually clear by the second or third retry; 4 bounds the total wait.
MAX_RETRIES = 4

# Metadata changes slowly; pageview days older than FINAL_AFTER_DAYS never change.
TTL_SITEMATRIX = 30 * 86400
TTL_ENTITIES = 7 * 86400
TTL_PAGES = 7 * 86400
TTL_SEARCH = 86400
FINAL_AFTER_DAYS = 2

# Pageview data starts on 2015-07-01 (Wikimedia Analytics API).
DATA_START = "2015-07-01"

# At most this many redirects per article are fetched (ranked by recent views): most
# redirects are misspellings with ~0 views, but renamed titles can carry real history.
MAX_REDIRECTS_PER_ARTICLE = 30


def cache_path() -> Path:
    return Path(os.environ.get("WIKI_INTEREST_CACHE", Path.home() / "wiki-interest" / "cache.sqlite")).expanduser()


def out_dir() -> Path:
    return Path(os.environ.get("WIKI_INTEREST_OUT", Path.home() / "wiki-interest" / "analyses")).expanduser()


def contact_configured() -> bool:
    return bool(os.environ.get("WIKI_CONTACT", "").strip())


def user_agent() -> str:
    """Wikimedia User-Agent policy format: name/version (contact) library/version.

    The contact comes from WIKI_CONTACT and is never printed or written to disk.
    """
    contact = os.environ.get("WIKI_CONTACT", "").strip()
    who = f"{PROJECT_URL}; {contact}" if contact else PROJECT_URL
    return f"wikipedia-interest-research/{VERSION} ({who}) python-urllib/{sys.version_info.major}.{sys.version_info.minor}"
