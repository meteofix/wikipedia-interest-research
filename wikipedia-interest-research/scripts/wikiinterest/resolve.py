"""Topic resolution: Wikidata search and sitelinks, MediaWiki page lookups, redirects, local search."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

from . import config
from .http import Http
from .sites import Site, SiteIndex

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
_BATCH = 50  # MediaWiki and Wikidata accept up to 50 titles/ids per request for normal clients
_QID_RE = re.compile(r"^[Qq]\d+$")


@dataclass
class Entity:
    qid: str
    labels: dict[str, str] = field(default_factory=dict)
    descriptions: dict[str, str] = field(default_factory=dict)
    sitelinks: dict[str, str] = field(default_factory=dict)  # dbname -> title

    def label(self, *langs: str) -> str:
        for lang in (*langs, "en"):
            if lang in self.labels:
                return self.labels[lang]
        return next(iter(self.labels.values()), self.qid)

    def description(self, *langs: str) -> str:
        for lang in (*langs, "en"):
            if lang in self.descriptions:
                return self.descriptions[lang]
        return next(iter(self.descriptions.values()), "")


def is_qid(token: str) -> bool:
    return bool(_QID_RE.match(token.strip()))


def search_entities(http: Http, query: str, lang: str, limit: int = 7) -> list[dict]:
    data = http.get_json(
        WIKIDATA_API,
        {"action": "wbsearchentities", "search": query, "language": lang, "uselang": lang, "type": "item",
         "limit": limit, "format": "json"},
        ttl=config.TTL_SEARCH,
    )
    return data.get("search", [])


def get_entities(http: Http, qids: list[str], label_langs: list[str]) -> dict[str, Entity]:
    """Fetch labels, descriptions and sitelinks. Keys include both requested and redirect-target ids."""
    out: dict[str, Entity] = {}
    langs = "|".join(dict.fromkeys([*label_langs, "en"]))
    ids = list(dict.fromkeys(q.upper() for q in qids))
    for i in range(0, len(ids), _BATCH):
        chunk = ids[i : i + _BATCH]
        data = http.get_json(
            WIKIDATA_API,
            {"action": "wbgetentities", "ids": "|".join(chunk), "props": "labels|descriptions|sitelinks",
             "languages": langs, "format": "json"},
            ttl=config.TTL_ENTITIES,
        )
        for key, e in data.get("entities", {}).items():
            if "missing" in e:
                continue
            ent = Entity(
                qid=e["id"],
                labels={k: v["value"] for k, v in e.get("labels", {}).items()},
                descriptions={k: v["value"] for k, v in e.get("descriptions", {}).items()},
                sitelinks={k: v["title"] for k, v in e.get("sitelinks", {}).items()},
            )
            out[e["id"]] = ent
            out[key] = ent
            redirect = e.get("redirects", {}).get("from")
            if redirect:
                out[redirect] = ent
    return out


def wikipedia_count(entity: Entity, index: SiteIndex) -> int:
    return sum(1 for db in entity.sitelinks if db in index.dbnames)


@dataclass
class PageInfo:
    input: str
    title: str | None  # canonical target title, None if the page does not exist
    redirected_from: str | None = None


def page_info(http: Http, site: Site, titles: list[str]) -> dict[str, PageInfo]:
    """Normalise titles and follow redirects; missing pages get title=None."""
    out: dict[str, PageInfo] = {}
    for i in range(0, len(titles), _BATCH):
        chunk = titles[i : i + _BATCH]
        data = http.get_json(
            site.api,
            {"action": "query", "titles": "|".join(chunk), "redirects": "1", "format": "json", "formatversion": "2"},
            ttl=config.TTL_PAGES,
        )
        q = data.get("query", {})
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        redir = {r["from"]: r["to"] for r in q.get("redirects", [])}
        pages = {p["title"]: p for p in q.get("pages", [])}
        for t in chunk:
            n = norm.get(t, t)
            target = redir.get(n, n)
            page = pages.get(target)
            exists = page is not None and not page.get("missing") and not page.get("invalid") and page.get("ns", 0) == 0
            out[t] = PageInfo(t, target if exists else None, n if target != n else None)
    return out


def redirects_of(http: Http, site: Site, titles: list[str]) -> dict[str, list[str]]:
    """Main-namespace redirects pointing to each title."""
    out: dict[str, list[str]] = {t: [] for t in titles}
    for i in range(0, len(titles), _BATCH):
        chunk = titles[i : i + _BATCH]
        params = {"action": "query", "titles": "|".join(chunk), "prop": "redirects", "rdnamespace": "0",
                  "rdlimit": "max", "rdprop": "title", "format": "json", "formatversion": "2"}
        while True:
            data = http.get_json(site.api, params, ttl=config.TTL_PAGES)
            for p in data.get("query", {}).get("pages", []):
                out.setdefault(p["title"], []).extend(r["title"] for r in p.get("redirects", []))
            cont = data.get("continue")
            if not cont:
                break
            params = {**params, **cont}
    return out


def recent_views(http: Http, site: Site, titles: list[str], days: int = 60) -> dict[str, int]:
    """Sum of views over the last `days` days (MediaWiki PageViewInfo), used to rank redirects."""
    out: dict[str, int] = {}
    for i in range(0, len(titles), _BATCH):
        chunk = titles[i : i + _BATCH]
        data = http.get_json(
            site.api,
            {"action": "query", "titles": "|".join(chunk), "prop": "pageviews", "pvipdays": str(days),
             "format": "json", "formatversion": "2"},
            ttl=config.TTL_PAGES,
        )
        for p in data.get("query", {}).get("pages", []):
            out[p["title"]] = sum(v or 0 for v in (p.get("pageviews") or {}).values())
    return out


def local_search(http: Http, site: Site, query: str, limit: int = 3) -> list[dict]:
    data = http.get_json(
        site.api,
        {"action": "query", "list": "search", "srsearch": query, "srlimit": str(limit), "srnamespace": "0",
         "srprop": "snippet", "format": "json", "formatversion": "2"},
        ttl=config.TTL_SEARCH,
    )
    hits = []
    for h in data.get("query", {}).get("search", []):
        snippet = html.unescape(re.sub(r"<[^>]+>", "", h.get("snippet", "")))
        hits.append({"title": h["title"], "snippet": re.sub(r"\s+", " ", snippet).strip()[:110]})
    return hits


# A second meaning counts as a real alternative when it is covered by at least 10 Wikipedias
# and by at least 30% as many as the main one (e.g. mercury the element vs the planet).
RIVAL_MIN_WIKIS, RIVAL_MIN_RATIO = 10, 0.3


def pick_best(query: str, cands: list[dict]) -> tuple[dict, list[dict]]:
    """Main concept = the most widely covered candidate whose label matches the query.

    Search order alone is not enough: for "jaguar" the car maker ranks above the animal.
    Rivals are other matching meanings with substantial coverage (the query is ambiguous).
    """
    q = query.strip().lower()

    def matches(c: dict) -> bool:
        label = c["label"].lower()
        return q in label or label in q

    exact = [c for c in cands if c["label"].lower() == q]
    related = [c for c in cands if matches(c)]
    pool = exact or related or cands[:3]
    best = max(pool, key=lambda c: c["wikipedias"])
    rivals = [c for c in related if c is not best and c["wikipedias"] >= RIVAL_MIN_WIKIS
              and c["wikipedias"] >= RIVAL_MIN_RATIO * max(best["wikipedias"], 1)
              and c["description"].lower() != best["description"].lower()]
    return best, rivals


def find_topic(http: Http, index: SiteIndex, query: str, sites: list[Site], search_lang: str = "en",
               limit: int = 5) -> dict:
    """Wikidata candidates for a free-text topic plus article titles in the requested editions."""
    hits = search_entities(http, query, search_lang, limit=max(limit, 7))
    if not hits and search_lang != "en":
        hits = search_entities(http, query, "en", limit=max(limit, 7))
    label_langs = [search_lang, *[s.lang_code for s in sites]]
    ents = get_entities(http, [h["id"] for h in hits], label_langs) if hits else {}
    cands = []
    for h in hits:
        e = ents.get(h["id"])
        if not e:
            continue
        cands.append({"qid": e.qid, "label": e.label(search_lang), "description": e.description(search_lang),
                      "wikipedias": wikipedia_count(e, index), "entity": e})
    result = {"query": query, "candidates": cands[:limit], "best": None, "ambiguous": False, "articles": []}
    if not cands:
        return result
    best, rivals = pick_best(query, cands)
    if best not in result["candidates"]:
        result["candidates"] = [best, *[c for c in result["candidates"] if c is not best]][:limit]
    result["best"] = best
    result["ambiguous"] = bool(rivals)
    result["rivals"] = rivals
    ent: Entity = best["entity"]
    for s in sites:
        title = ent.sitelinks.get(s.dbname)
        row = {"site": s, "title": title, "suggestions": []}
        if not title:
            q = ent.labels.get(s.lang_code) or ent.label(search_lang)
            row["suggestions"] = local_search(http, s, q)
            row["search_query"] = q
        result["articles"].append(row)
    return result
