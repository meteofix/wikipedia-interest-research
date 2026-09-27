"""SQLite cache shared by all runs: HTTP metadata responses and daily pageview series.

Daily views are stored per (project, title, access, agent, day) together with the date
ranges that were actually fetched, so zero-view days (which the API omits) are known to be
zero rather than missing, and follow-up questions only fetch the days not seen before.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from datetime import date, timedelta
from pathlib import Path

from . import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS http_cache (key TEXT PRIMARY KEY, fetched_at REAL, body TEXT);
CREATE TABLE IF NOT EXISTS views (
    project TEXT, title TEXT, access TEXT, agent TEXT, day TEXT, views INTEGER,
    PRIMARY KEY (project, title, access, agent, day)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS coverage (
    project TEXT, title TEXT, access TEXT, agent TEXT, start TEXT, end TEXT, fetched_at REAL);
CREATE INDEX IF NOT EXISTS coverage_key ON coverage (project, title, access, agent);
"""


class Cache:
    def __init__(self, path: Path | None = None):
        self.path = Path(path or config.cache_path())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, timeout=60, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=60000")
        self._conn.executescript(_SCHEMA)
        self.stats = {"series_cached": 0, "series_fetched": 0, "http_cached": 0, "http_fetched": 0}

    # ---- generic HTTP metadata -------------------------------------------------
    def get_http(self, key: str, ttl: float) -> object | None:
        with self._lock:
            row = self._conn.execute("SELECT fetched_at, body FROM http_cache WHERE key=?", (key,)).fetchone()
        if row and time.time() - row[0] < ttl:
            self.stats["http_cached"] += 1
            return json.loads(row[1])
        return None

    def put_http(self, key: str, body: object) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO http_cache VALUES (?,?,?)", (key, time.time(), json.dumps(body))
            )
            self._conn.commit()

    # ---- daily pageviews -------------------------------------------------------
    def covered(self, key: tuple[str, str, str, str]) -> list[tuple[date, date]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT start, end FROM coverage WHERE project=? AND title=? AND access=? AND agent=?", key
            ).fetchall()
        return merge_intervals([(date.fromisoformat(s), date.fromisoformat(e)) for s, e in rows])

    def store_views(self, key: tuple[str, str, str, str], start: date, end: date, daily: dict[str, int]) -> None:
        """Store fetched days and mark [start, end] as covered (only days that are final)."""
        final_end = min(end, date.today() - timedelta(days=config.FINAL_AFTER_DAYS))
        with self._lock:
            self._conn.executemany(
                "INSERT OR REPLACE INTO views VALUES (?,?,?,?,?,?)",
                [(*key, d, v) for d, v in daily.items()],
            )
            if final_end >= start:
                self._conn.execute(
                    "INSERT INTO coverage VALUES (?,?,?,?,?,?,?)",
                    (*key, start.isoformat(), final_end.isoformat(), time.time()),
                )
            self._conn.commit()

    def load_views(self, key: tuple[str, str, str, str], start: date, end: date) -> dict[str, int]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT day, views FROM views WHERE project=? AND title=? AND access=? AND agent=? "
                "AND day BETWEEN ? AND ?",
                (*key, start.isoformat(), end.isoformat()),
            ).fetchall()
        return {d: v for d, v in rows}


def merge_intervals(intervals: list[tuple[date, date]]) -> list[tuple[date, date]]:
    merged: list[tuple[date, date]] = []
    for s, e in sorted(intervals):
        if merged and s <= merged[-1][1] + timedelta(days=1):
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def missing_ranges(start: date, end: date, covered: list[tuple[date, date]]) -> list[tuple[date, date]]:
    """Sub-ranges of [start, end] not inside any covered interval."""
    gaps = []
    cur = start
    for s, e in merge_intervals(covered):
        if e < cur:
            continue
        if s > end:
            break
        if s > cur:
            gaps.append((cur, min(end, s - timedelta(days=1))))
        cur = max(cur, e + timedelta(days=1))
        if cur > end:
            break
    if cur <= end:
        gaps.append((cur, end))
    return gaps
