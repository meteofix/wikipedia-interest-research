"""Wikimedia pageviews API: per-article and whole-edition daily series (zero-filled), top articles."""

from __future__ import annotations

import urllib.parse
from datetime import date, timedelta

from . import config
from .cache import Cache, missing_ranges
from .http import Http, NotFound
from .sites import Site

API = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
TOTAL = "__TOTAL__"  # pseudo-title under which whole-edition totals are cached

ACCESS = ("all-access", "desktop", "mobile-web", "mobile-app", "mobile")  # "mobile" = web + app
AGENTS = ("user", "all-agents", "automated", "spider")


def daterange(start: date, end: date) -> list[str]:
    return [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]


def clamp(start: date, end: date) -> tuple[date, date]:
    """Pageview data exists from 2015-07-01 until yesterday (UTC)."""
    return max(start, date.fromisoformat(config.DATA_START)), min(end, date.today() - timedelta(days=1))


def _ymd(d: date) -> str:
    return d.strftime("%Y%m%d")


def _parse_items(data: dict) -> dict[str, int]:
    out = {}
    for it in data.get("items", []):
        ts = it["timestamp"]
        out[f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"] = int(it["views"])
    return out


def _fetch_article(http: Http, site: Site, title: str, access: str, agent: str, s: date, e: date) -> dict[str, int]:
    enc = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"{API}/per-article/{site.host}/{access}/{agent}/{enc}/daily/{_ymd(s)}/{_ymd(e)}"
    try:
        return _parse_items(http.get_json(url))
    except NotFound:
        return {}  # no views in the range (the API omits zero days and 404s on all-zero ranges)


def _fetch_total(http: Http, site: Site, access: str, agent: str, s: date, e: date) -> dict[str, int]:
    url = f"{API}/aggregate/{site.host}/{access}/{agent}/daily/{_ymd(s)}00/{_ymd(e)}00"
    try:
        return _parse_items(http.get_json(url))
    except NotFound:
        return {}


def daily(http: Http, cache: Cache, site: Site, title: str, start: date, end: date,
          access: str = "all-access", agent: str = "user") -> dict[str, int]:
    """Zero-filled daily views for one article (or the edition total when title == TOTAL)."""
    if access == "mobile":  # the API has no combined mobile access type
        web = daily(http, cache, site, title, start, end, "mobile-web", agent)
        app = daily(http, cache, site, title, start, end, "mobile-app", agent)
        return {d: web.get(d, 0) + app.get(d, 0) for d in web}
    start, end = clamp(start, end)
    if end < start:
        return {}
    key = (site.host, title, access, agent)
    gaps = missing_ranges(start, end, cache.covered(key))
    if gaps:
        cache.stats["series_fetched"] += 1
    else:
        cache.stats["series_cached"] += 1
    for s, e in gaps:
        got = (_fetch_total(http, site, access, agent, s, e) if title == TOTAL
               else _fetch_article(http, site, title, access, agent, s, e))
        cache.store_views(key, s, e, got)
    stored = cache.load_views(key, start, end)
    return {d: stored.get(d, 0) for d in daterange(start, end)}


def monthly_api(http: Http, site: Site, title: str, first_month: str, last_month: str,
                access: str = "all-access", agent: str = "user") -> dict[str, int]:
    """The API's own monthly totals — used only to cross-check our daily aggregation."""
    y1, m1 = map(int, first_month.split("-"))
    y2, m2 = map(int, last_month.split("-"))
    s = date(y1, m1, 1)
    e = (date(y2 + (m2 == 12), m2 % 12 + 1, 1) - timedelta(days=1))
    enc = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"{API}/per-article/{site.host}/{access}/{agent}/{enc}/monthly/{_ymd(s)}00/{_ymd(e)}00"
    try:
        data = http.get_json(url)
    except NotFound:
        return {}
    return {it["timestamp"][0:4] + "-" + it["timestamp"][4:6]: int(it["views"]) for it in data.get("items", [])}


def top_articles(http: Http, site: Site, year: int, month: int, access: str = "all-access") -> list[dict]:
    url = f"{API}/top/{site.host}/{access}/{year}/{month:02d}/all-days"
    data = http.get_json(url, ttl=30 * 86400)  # a finished month never changes
    items = data.get("items", [])
    return items[0]["articles"] if items else []


def namespace_prefixes(http: Http, site: Site) -> tuple[set[str], str]:
    """Localised non-article namespace prefixes and the main page title, to filter top lists."""
    data = http.get_json(
        site.api,
        {"action": "query", "meta": "siteinfo", "siprop": "general|namespaces|namespacealiases",
         "format": "json", "formatversion": "2"},
        ttl=config.TTL_SITEMATRIX,
    )
    q = data.get("query", {})
    prefixes = set()
    for ns in q.get("namespaces", {}).values():
        if ns.get("id", 0) != 0:
            for k in ("name", "canonical"):
                if ns.get(k):
                    prefixes.add(ns[k].replace(" ", "_").lower())
    for a in q.get("namespacealiases", []):
        if a.get("id", 0) != 0:
            prefixes.add(a["alias"].replace(" ", "_").lower())
    return prefixes, q.get("general", {}).get("mainpage", "").replace(" ", "_")
