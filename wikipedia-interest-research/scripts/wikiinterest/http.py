"""Polite HTTP client for Wikimedia APIs: identified User-Agent, rate limit, retries, cache."""

from __future__ import annotations

import json
import random
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from . import config
from .cache import Cache


class ApiError(RuntimeError):
    """Network or API failure that survived retries (exit code 4 in the CLI)."""


class NotFound(ApiError):
    """HTTP 404: for pageviews this means 'no data' (or no such page)."""


class _RateLimiter:
    def __init__(self, rps: float):
        self.interval = 1.0 / max(rps, 0.01)
        self._next = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            delay = self._next - now
            self._next = max(now, self._next) + self.interval
        if delay > 0:
            time.sleep(delay)


class Http:
    def __init__(self, cache: Cache):
        self.cache = cache
        self._limiter = _RateLimiter(config.MAX_RPS)
        self._slots = threading.BoundedSemaphore(config.MAX_CONCURRENCY)
        self.requests = 0

    def get_json(self, url: str, params: dict | None = None, ttl: float | None = None) -> dict:
        full = url + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
        if ttl is not None:
            hit = self.cache.get_http(full, ttl)
            if hit is not None:
                return hit
        body = self._fetch(full)
        if ttl is not None:
            self.cache.put_http(full, body)
            self.cache.stats["http_fetched"] += 1
        return body

    def _fetch(self, url: str) -> dict:
        headers = {"User-Agent": config.user_agent(), "Accept": "application/json", "Accept-Encoding": "identity"}
        last_err: Exception | None = None
        for attempt in range(config.MAX_RETRIES + 1):
            self._limiter.wait()
            with self._slots:
                self.requests += 1
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=config.REQUEST_TIMEOUT) as resp:
                        return json.loads(resp.read().decode("utf-8"))
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        raise NotFound(f"404 for {_short(url)}") from None
                    if e.code in (429, 500, 502, 503, 504):
                        last_err = e
                        retry_after = e.headers.get("Retry-After") if e.headers else None
                        delay = _retry_delay(retry_after, attempt)
                        print(f"[wiki] HTTP {e.code}, retrying in {delay:.0f}s", file=sys.stderr)
                        time.sleep(delay)
                        continue
                    raise ApiError(f"HTTP {e.code} for {_short(url)}") from None
                except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                    last_err = e
                    time.sleep(_retry_delay(None, attempt))
        raise ApiError(f"Wikimedia API unavailable after {config.MAX_RETRIES + 1} attempts: {last_err}")


def _retry_delay(retry_after: str | None, attempt: int) -> float:
    if retry_after and retry_after.isdigit():
        return min(float(retry_after), 60.0)
    return min(5.0 * (2**attempt), 60.0) + random.uniform(0, 1)  # Wikimedia: wait >= 5 s


def _short(url: str) -> str:
    return url if len(url) < 160 else url[:157] + "..."
