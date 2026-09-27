"""`analyze`: topics x languages -> articles -> zero-filled series -> metrics, verdicts, outputs."""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from . import config, metrics as M, pageviews as PV, resolve as R
from .cache import Cache
from .http import Http
from .schema import SCHEMA_ID
from .sites import Site, SiteIndex, load_sites
from . import i18n
from .verdict import verdict

CAVEAT_CODES = ["interest_not_intent", "language_not_country", "relative_growth", "articles_proxy", "human_traffic"]
CAVEATS = [i18n.render(c) for c in CAVEAT_CODES]


class Warnings:
    """Agent-facing English warnings plus codes the PDF renders in the report language."""

    def __init__(self) -> None:
        self.text: list[str] = []
        self.codes: list[dict] = []

    def add(self, text: str, code: str | None = None, **params) -> None:
        if text not in self.text:
            self.text.append(text)
            if code:
                self.codes.append({"code": code, "params": params})

    def append(self, text: str) -> None:  # plain warnings without a translation
        self.add(text)


class TopicError(ValueError):
    """Bad topic syntax or an ambiguous free-text topic (exit code 2)."""


@dataclass
class Topic:
    id: str
    label: str | None
    qids: list[str] = field(default_factory=list)
    titles: list[tuple[Site, str]] = field(default_factory=list)  # explicit per-edition articles
    resolved_from: str | None = None  # free text the topic was resolved from
    labels: dict = field(default_factory=dict)  # label per language (en, uk, ...) for reports


# "+" separates items only when followed by a QID or "lang:" so titles such as "C++" survive.
_ITEM_SPLIT = re.compile(r"\s*\+\s*(?=(?:[Qq]\d+\b|[A-Za-z][A-Za-z0-9-]{1,11}:))")
_LANG_TITLE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]{1,11}):(.+)$")


def parse_topic(spec: str, n: int, index: SiteIndex) -> tuple[Topic, list[str]]:
    """Parse `[Label=]item[+item...]`; returns the topic and free-text parts still to resolve."""
    label, body = None, spec.strip()
    if "=" in body:
        left, right = body.split("=", 1)
        if ":" not in left and (R.is_qid(right.strip().split("+")[0]) or _LANG_TITLE.match(right.strip())):
            label, body = left.strip() or None, right.strip()
    topic = Topic(id=f"t{n}", label=label)
    free: list[str] = []
    for item in _ITEM_SPLIT.split(body):
        item = item.strip()
        if not item:
            continue
        if R.is_qid(item):
            topic.qids.append(item.upper())
            continue
        m = _LANG_TITLE.match(item)
        if m:
            try:
                site = index.resolve(m.group(1))
            except ValueError:
                site = None
            if site is not None:
                topic.titles.append((site, m.group(2).strip()))
                continue
        free.append(item)
    return topic, free


def last_complete_month(today: date | None = None) -> str:
    t = today or date.today()
    prev = t.replace(day=1) - timedelta(days=1)
    if (t - prev).days <= 1:  # the API needs ~1 day to publish the last day of a month
        prev = prev.replace(day=1) - timedelta(days=1)
    return prev.strftime("%Y-%m")


def month_add(month: str, k: int) -> str:
    y, m = map(int, month.split("-"))
    total = y * 12 + (m - 1) + k
    return f"{total // 12:04d}-{total % 12 + 1:02d}"


def resolve_window(months: int | None, start: str | None, end: str | None, warnings: "Warnings") -> list[str]:
    last = last_complete_month()
    end_m = end or last
    if end_m > last:
        warnings.add(f"end month {end_m} is not complete yet; using {last}", "end_incomplete", end=end_m, last=last)
        end_m = last
    if start:
        start_m = start
    else:
        start_m = month_add(end_m, -((months or 36) - 1))
    first_data = config.DATA_START[:7]
    if start_m < first_data:
        warnings.add(f"pageview data starts in {first_data}; earlier months are not available", "data_start",
                     first=first_data)
        start_m = first_data
    if start_m > end_m:
        raise TopicError(f"start month {start_m} is after end month {end_m}")
    ms = M.month_list(start_m, end_m)
    if len(ms) < 24:
        warnings.add(f"window has {len(ms)} months (< 24): year-over-year growth needs 24 months, "
                     "only levels are reported", "window_short", n=len(ms))
    return ms


def _slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return t[:40] or "analysis"


def _context(http_cache: Cache | None = None):
    cache = http_cache or Cache()
    http = Http(cache)
    index = SiteIndex(load_sites(http))
    return cache, http, index


def resolve_topics(specs: list[str], sites: list[Site], http: Http, index: SiteIndex) -> tuple[list[Topic], dict]:
    topics, ents_needed = [], []
    for n, spec in enumerate(specs, 1):
        topic, free = parse_topic(spec, n, index)
        for text in free:
            langs = ["en"] if text.isascii() else [*dict.fromkeys(s.lang_code for s in sites), "en"]
            found = None
            for lang in langs:
                found = R.find_topic(http, index, text, [], search_lang=lang)
                if found["best"]:
                    break
            if not found or not found["best"]:
                raise TopicError(f"No Wikidata item found for '{text}'. Try an English name, or run "
                                 f"`find` and pass a QID (e.g. Q718) or lang:Title.")
            if found["ambiguous"]:
                opts = "; ".join(f"{c['qid']} = {c['label']} ({c['description']}, {c['wikipedias']} Wikipedias)"
                                 for c in [found["best"], *found["rivals"]])
                raise TopicError(f"'{text}' is ambiguous: {opts}. Pick the QID that matches the user's meaning "
                                 "(ask the user if the context does not tell).")
            topic.qids.append(found["best"]["qid"])
            topic.resolved_from = text
        topics.append(topic)
        ents_needed += topic.qids
    label_langs = [*dict.fromkeys([s.lang_code for s in sites] + ["en", "uk"])]
    ents = R.get_entities(http, ents_needed, label_langs) if ents_needed else {}
    for t in topics:
        missing = [q for q in t.qids if q not in ents]
        if missing:
            raise TopicError(f"Wikidata item(s) not found: {', '.join(missing)}")
        for lang in ("en", "uk"):
            names = [ents[q].label(lang) for q in t.qids] + [title for _, title in t.titles]
            t.labels[lang] = " + ".join(names) if len(names) <= 3 else f"{names[0]} + {len(names) - 1}"
        if t.label:
            t.labels = {"en": t.label, "uk": t.label}
        else:
            t.label = t.labels["en"]
    return topics, ents


def collect(specs: list[str], lang_tokens: list[str], first_day: date, last_day: date, *, redirects: bool,
            access: str, agent: str, http: Http, cache: Cache, index: SiteIndex, warnings: Warnings) -> dict:
    """Resolve topics to articles (+ redirects) per edition and fetch all zero-filled daily series."""
    if not lang_tokens:
        raise TopicError("--langs is required, e.g. --langs uk,pl")
    sites = index.resolve_many(lang_tokens)
    topics, ents = resolve_topics(specs, sites, http, index)

    plan: dict[tuple[str, str], list[dict]] = {}
    for site in sites:
        explicit = [title for t in topics for s, title in t.titles if s == site]
        info = R.page_info(http, site, explicit) if explicit else {}
        for t in topics:
            arts: list[dict] = []
            for q in t.qids:
                title = ents[q].sitelinks.get(site.dbname)
                if title:
                    arts.append({"title": title, "source": q})
            for s, title in t.titles:
                if s != site:
                    continue
                pi = info.get(title)
                if pi and pi.title:
                    arts.append({"title": pi.title, "source": "explicit"})
                    if pi.redirected_from:
                        warnings.add(f"{site.code}: '{title}' redirects to '{pi.title}'; using the target article",
                                     "title_redirected", lang=site.code, title=title, target=pi.title)
                else:
                    warnings.add(f"{site.code}: article '{title}' does not exist", "title_missing",
                                 lang=site.code, title=title)
            seen, uniq = set(), []
            for a in arts:
                if a["title"] not in seen:
                    seen.add(a["title"])
                    uniq.append(a)
            plan[(t.id, site.code)] = uniq

    redirect_map: dict[tuple[str, str], list[str]] = {}
    redirect_totals: dict[tuple[str, str], int] = {}
    if redirects:
        for site in sites:
            titles = sorted({a["title"] for (tid, code), arts in plan.items() if code == site.code for a in arts})
            if not titles:
                continue
            reds = R.redirects_of(http, site, titles)
            for title in titles:
                lst = reds.get(title, [])
                total = len(lst)
                redirect_totals[(site.code, title)] = total
                if total > config.MAX_REDIRECTS_PER_ARTICLE:
                    rv = R.recent_views(http, site, lst)
                    lst = sorted(lst, key=lambda x: -rv.get(x, 0))[: config.MAX_REDIRECTS_PER_ARTICLE]
                    warnings.add(f"{site.code}: '{title}' has {total} redirects; the "
                                 f"{config.MAX_REDIRECTS_PER_ARTICLE} most viewed recently are included",
                                 "redirects_capped", lang=site.code, title=title, total=total,
                                 n=config.MAX_REDIRECTS_PER_ARTICLE)
                redirect_map[(site.code, title)] = lst

    site_by_code = {s.code: s for s in sites}
    created: dict[tuple[str, str], str | None] = {}
    main_titles = sorted({(code, a["title"]) for (tid, code), arts in plan.items() for a in arts})
    with ThreadPoolExecutor(max_workers=config.MAX_CONCURRENCY) as ex:
        for key, day in zip(main_titles, ex.map(lambda k: R.creation_date(http, site_by_code[k[0]], k[1]), main_titles)):
            created[key] = day
    jobs: set[tuple[str, str]] = set()
    for (tid, code), arts in plan.items():
        for a in arts:
            jobs.add((code, a["title"]))
            for r in redirect_map.get((code, a["title"]), []):
                jobs.add((code, r))
    jobs |= {(s.code, PV.TOTAL) for s in sites}
    series_data: dict[tuple[str, str], dict[str, int]] = {}
    todo = [j for j in jobs if cache.covered((site_by_code[j[0]].host, j[1], access, agent)) == []]
    if len(todo) > 20:
        eta = len(todo) / max(config.MAX_RPS, 0.1)
        print(f"[wiki] downloading {len(todo)} new series (about {eta:.0f} s); if interrupted, rerun the same "
              "command — finished series are cached", file=sys.stderr, flush=True)

    def fetch(job):
        code, title = job
        return job, PV.daily(http, cache, site_by_code[code], title, first_day, last_day, access, agent)

    with ThreadPoolExecutor(max_workers=config.MAX_CONCURRENCY) as ex:
        for job, data in ex.map(fetch, sorted(jobs)):
            series_data[job] = data
    return {"sites": sites, "topics": topics, "plan": plan, "redirect_map": redirect_map,
            "redirect_totals": redirect_totals, "series_data": series_data, "created": created,
            "days": PV.daterange(first_day, last_day)}


def build_series(t: Topic, site: Site, col: dict) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    """Topic (articles + redirects) and articles-only daily arrays for one topic x edition."""
    days, data = col["days"], col["series_data"]
    main = np.zeros(len(days))
    topic_v = np.zeros(len(days))
    arts_out = []
    for a in col["plan"][(t.id, site.code)]:
        arr = np.array([data[(site.code, a["title"])][d] for d in days], dtype=float)
        main += arr
        topic_v += arr
        reds = col["redirect_map"].get((site.code, a["title"]), [])
        for r in reds:
            topic_v += np.array([data[(site.code, r)][d] for d in days], dtype=float)
        nz = np.nonzero(arr)[0]
        arts_out.append({"title": a["title"], "source": a["source"], "redirects_included": len(reds),
                         "redirects_total": col["redirect_totals"].get((site.code, a["title"]), 0),
                         "created": col.get("created", {}).get((site.code, a["title"])),
                         "data_start": days[nz[0]] if len(nz) else None})
    return topic_v, main, arts_out


def run(specs: list[str], lang_tokens: list[str], *, months: int | None = 36, start: str | None = None,
        end: str | None = None, redirects: bool = True, access: str = "all-access", agent: str = "user",
        rank_by: str = "growth", min_views: float | None = None, min_growth: float | None = None,
        weights: dict[str, float] | None = None, out: str | None = None, command: str | None = None,
        cache: Cache | None = None) -> dict:
    cache, http, index = _context(cache)
    warnings = Warnings()
    months_list = resolve_window(months, start, end, warnings)
    first_day, last_day = PV.clamp(*M.month_bounds(months_list[0], months_list[-1]))
    col = collect(specs, lang_tokens, first_day, last_day, redirects=redirects, access=access, agent=agent,
                  http=http, cache=cache, index=index, warnings=warnings)
    sites, topics, days = col["sites"], col["topics"], col["days"]

    yoy_prior_start = f"{months_list[-24]}-01" if len(months_list) >= 24 else f"{months_list[0]}-01"
    all_series = []
    for t in topics:
        for site in sites:
            key = f"{t.id}|{site.code}"
            base = {"key": key, "topic_id": t.id, "topic_label": t.label, "lang": site.code,
                    "project": site.host, "note": None, "articles": [], "monthly": [], "metrics": {},
                    "variants": [], "verdict": {"direction": "n/a", "confidence": "n/a", "reasons": []},
                    "criteria": None}
            if not col["plan"][(t.id, site.code)]:
                qs = ", ".join(t.qids) or "the given titles"
                base.update(status="missing", note=f"no {site.english or site.code} Wikipedia article for {qs}")
                warnings.add(f"{site.code}: no article for '{t.label}' ({qs}) — not measurable in this edition; "
                             "run `find` for local search suggestions or pass a proxy article as "
                             f"{site.code}:Title (and call it a proxy)", "missing_article", lang=site.code, label=t.label)
                all_series.append(base)
                continue
            topic_v, main, arts = build_series(t, site, col)
            base["articles"] = arts
            total = np.array([col["series_data"][(site.code, PV.TOTAL)][d] for d in days], dtype=float)
            if topic_v.sum() == 0:
                base.update(status="no_data", note="articles exist but had no views in the window")
                warnings.add(f"{site.code}: '{t.label}' has no views in the window", "no_data", lang=site.code,
                             label=t.label)
                all_series.append(base)
                continue
            res = M.series_metrics(days, topic_v, main, total, months_list)
            v, rows = verdict(res["metrics"], res["variants"], yoy_prior_start)
            base.update(status="ok", monthly=res["monthly"], metrics=res["metrics"], variants=rows, verdict=v)
            crit = {}
            if min_views is not None:
                crit["min_views"] = {"threshold": min_views, "pass": res["metrics"]["avg_daily_views_12m"] >= min_views}
            if min_growth is not None:
                g = res["metrics"]["yoy_rel"]
                crit["min_growth"] = {"threshold": min_growth, "pass": g is not None and g * 100 >= min_growth}
            base["criteria"] = crit or None
            all_series.append(base)

    comparison = compare(all_series, rank_by)
    if weights and comparison is not None:
        comparison["weighted"] = weighted_scores(all_series, weights)
    if months_list[0] <= "2025-08" and months_list[-1] >= "2025-03":
        warnings.add(i18n.render("bot_reclass"), "bot_reclass")
    results = {
        "schema": SCHEMA_ID,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool_version": config.VERSION,
        "params": {
            "topics": [{"id": t.id, "label": t.label, "labels": t.labels, "qids": t.qids,
                        "titles": [f"{s.code}:{title}" for s, title in t.titles],
                        "resolved_from": t.resolved_from} for t in topics],
            "langs": [s.code for s in sites],
            "start": months_list[0], "end": months_list[-1], "months": len(months_list),
            "recent": [months_list[-12], months_list[-1]] if len(months_list) >= 12 else None,
            "prior": [months_list[-24], months_list[-13]] if len(months_list) >= 24 else None,
            "agent": agent, "access": access, "redirects": redirects, "rank_by": rank_by,
            "min_views": min_views, "min_growth": min_growth, "weights": weights, "command": command,
        },
        "series": all_series,
        "comparison": comparison,
        "caveats": CAVEATS,
        "caveat_codes": CAVEAT_CODES,
        "warnings": warnings.text,
        "warning_codes": warnings.codes,
        "files": {},
    }
    write_outputs(results, out, topics, sites)
    results["_stats"] = {"api_requests": http.requests, **cache.stats}
    return results


def compare(series: list[dict], rank_by: str) -> dict | None:
    ok = [s for s in series if s["status"] == "ok"]
    field_map = {"growth": "yoy_rel", "share": "share_ppm_12m", "views": "avg_daily_views_12m"}
    fld = field_map.get(rank_by, "yoy_rel")
    vals = [(s, s["metrics"].get(fld)) for s in ok]
    ranked = sorted([x for x in vals if x[1] is not None], key=lambda x: -x[1])
    if len(ranked) < 2:
        return None
    ranking = [{"key": s["key"], "label": f"{s['topic_label']} · {s['lang']}", "value": v} for s, v in ranked]
    notes: list[str] = []
    note_codes: list[dict] = []
    leader_stable = overlap = None
    if rank_by == "growth":
        leader = ranked[0][0]["key"]
        same = total = 0
        for name in ("ex_spikes", "shifted_6m", "no_redirects"):
            alt = {}
            for s, v in ranked:
                row = next((r for r in s["variants"] if r["name"] == name), None)
                alt[s["key"]] = row["yoy_rel"] if row else v
            total += 1
            same += max(alt, key=alt.get) == leader
        leader_stable = f"{same}/{total}"
        ci1 = ranked[0][0]["metrics"].get("yoy_rel_ci")
        ci2 = ranked[1][0]["metrics"].get("yoy_rel_ci")
        if ci1 and ci2:
            overlap = ci1[0] <= ci2[1]
            if overlap:
                notes.append(i18n.render("overlap"))
                note_codes.append({"code": "overlap", "params": {}})
    low = [f"{s['topic_label']} · {s['lang']}" for s, _ in ranked if s["verdict"]["confidence"] == "Low"]
    if low:
        notes.append(i18n.render("low_conf_series", {"labels": ", ".join(low)}))
        keys = [s["key"] for s, _ in ranked if s["verdict"]["confidence"] == "Low"]
        note_codes.append({"code": "low_conf_series", "params": {"labels": ", ".join(low), "keys": keys}})
    return {"rank_by": rank_by, "ranking": ranking, "leader_stable": leader_stable,
            "leader_ci_overlap": overlap, "notes": notes, "note_codes": note_codes}


WEIGHT_FIELDS = {"growth": "yoy_rel", "share": "share_ppm_12m", "views": "avg_daily_views_12m"}
_CONF_VALUE = {"High": 2, "Medium": 1, "Low": 0}


def weighted_scores(series: list[dict], weights: dict[str, float]) -> dict:
    """User-weighted ranking. Each criterion is turned into a 0..1 percentile rank across the
    compared series (so units don't matter), then averaged with the user's weights."""
    ok = [s for s in series if s["status"] == "ok"]
    n = len(ok)

    def value(s: dict, crit: str) -> float:
        if crit == "confidence":
            return _CONF_VALUE.get(s["verdict"]["confidence"], 0)
        v = s["metrics"].get(WEIGHT_FIELDS[crit])
        return v if v is not None else float("-inf")

    pct: dict[str, dict[str, float]] = {}
    for crit in weights:
        order = sorted(ok, key=lambda s: value(s, crit))
        pct[crit] = {s["key"]: (i / (n - 1) if n > 1 else 1.0) for i, s in enumerate(order)}
    total_w = sum(weights.values()) or 1.0
    rows = []
    for s in ok:
        score = sum(w * pct[c][s["key"]] for c, w in weights.items()) / total_w
        rows.append({"key": s["key"], "label": f"{s['topic_label']} · {s['lang']}", "score": round(score, 2),
                     "components": {c: round(pct[c][s["key"]], 2) for c in weights}})
    rows.sort(key=lambda r: -r["score"])
    return {"weights": weights, "ranking": rows,
            "method": "weighted average of percentile ranks (0 = worst, 1 = best among the compared series)"}


def write_outputs(results: dict, out: str | None, topics: list[Topic], sites: list[Site]) -> None:
    from . import render

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = _slug("-".join([t.label or t.id for t in topics][:3] + [s.code for s in sites][:4]))
    d = Path(out).expanduser() if out else config.out_dir() / f"{stamp}-{name}"
    d = d.resolve()
    d.mkdir(parents=True, exist_ok=True)
    files = {"dir": str(d), "results": str(d / "results.json"), "summary": str(d / "summary.md"),
             "csv": str(d / "series.csv")}
    with open(files["csv"], "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["topic", "lang", "month", "views", "views_articles_only", "edition_views", "share_per_million"])
        for s in results["series"]:
            for mp in s["monthly"]:
                w.writerow([s["topic_label"], s["lang"], mp["month"], mp["views"], mp["views_main"],
                            mp["project_views"], mp["share_ppm"]])
    try:
        from . import charts

        files.update(charts.render_charts(results, d))
    except ImportError:
        pass
    except Exception as e:  # charts are helpful but must never block the numbers
        results["warnings"].append(f"charts could not be rendered: {e}")
    results["files"] = files
    with open(files["results"], "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    Path(files["summary"]).write_text(render.analysis_summary(results), encoding="utf-8")
