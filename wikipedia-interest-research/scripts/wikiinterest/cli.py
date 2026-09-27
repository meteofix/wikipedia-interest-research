"""Command-line interface: find | analyze | views | top | report."""

from __future__ import annotations

import argparse
import csv
import shlex
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from . import config

EXIT_OK, EXIT_INPUT, EXIT_NOT_FOUND, EXIT_NETWORK = 0, 2, 3, 4

EPILOG = """\
examples:
  wiki.py find "chess" --langs tr,vi,id
  wiki.py analyze Q718 --langs tr,vi,id
  wiki.py analyze Q718 Q12195 --langs uk --rank-by growth         (two topics compared)
  wiki.py analyze "Chess=Q718+uk:Шахова задача" --langs uk         (basket summed as one topic)
  wiki.py analyze Q718 --langs de,fr --months 24 --min-views 100 --min-growth 10
  wiki.py views Q718 --langs de --access desktop --granularity monthly --start 2024-01
  wiki.py top --lang cs --month 2026-08 --match zatmění
  wiki.py report ~/wiki-interest/analyses/<dir> --notes notes.md --lang uk

topics: Q123 (Wikidata item) | lang:Title (one article) | A+B (summed basket) | Label=A+B | free text (resolved
        to the best Wikidata match; ambiguous text is rejected with candidates)
exit codes: 0 ok, 2 invalid input or ambiguous topic, 3 nothing found / no data, 4 network or API failure
env: WIKI_CONTACT (contact for the Wikimedia User-Agent), WIKI_INTEREST_OUT, WIKI_INTEREST_CACHE, WIKI_MAX_RPS
"""


def _month(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM, got '{value}'") from None
    return value


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wiki.py",
        description="Wikipedia pageview research for product decisions: resolve topics, measure interest and its "
                    "growth across language editions with a trust verdict, render charts and a one-page PDF.",
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="{find,analyze,views,top,report}")

    f = sub.add_parser("find", help="topic text -> Wikidata candidates and article titles per language")
    f.add_argument("topics", nargs="+", help="one or more topics in plain words (English works best)")
    f.add_argument("--langs", help="comma-separated language editions, e.g. pl,cs,uk")
    f.add_argument("--search-lang", default=None, help="language of the topic text (default: en, or auto for non-Latin text)")
    f.add_argument("--limit", type=int, default=5, help="max candidates per topic (default 5)")

    a = sub.add_parser("analyze", help="growth, level, trust verdict, charts and results.json")
    a.add_argument("topics", nargs="+", help="topics: Q123 | lang:Title | A+B | Label=A+B | free text")
    a.add_argument("--langs", required=True, help="comma-separated language editions, e.g. pl,cs")
    a.add_argument("--months", type=int, default=36, help="window length in full months (default 36, min 24 for growth)")
    a.add_argument("--start", type=_month, help="first month YYYY-MM (overrides --months)")
    a.add_argument("--end", type=_month, help="last month YYYY-MM (default: last complete month)")
    a.add_argument("--no-redirects", action="store_true", help="count only the articles, not their redirects")
    a.add_argument("--access", default="all-access", choices=["all-access", "desktop", "mobile-web", "mobile-app", "mobile"],
                   help="all-access (default), desktop, mobile-web, mobile-app, or mobile (= web + app)")
    a.add_argument("--agent", default="user", choices=["user", "all-agents", "automated", "spider"])
    a.add_argument("--rank-by", default="growth", choices=["growth", "share", "views"],
                   help="order for comparisons (default growth)")
    a.add_argument("--min-views", type=float, help="user criterion: minimum average views/day")
    a.add_argument("--min-growth", type=float, help="user criterion: minimum relative growth in percent, e.g. 15")
    a.add_argument("--exclude-months", help="calendar months to leave out of growth/levels, e.g. 1 or 12,1")
    a.add_argument("--weights", help="user's weighted ranking, e.g. growth=2,share=1 (criteria: growth, share, views, "
                                     "confidence)")
    a.add_argument("--out", help="output directory (default $WIKI_INTEREST_OUT/<timestamp>-<slug>)")

    v = sub.add_parser("views", help="raw series for custom questions (platforms, bots, daily data, totals)")
    v.add_argument("topics", nargs="+")
    v.add_argument("--langs", required=True)
    v.add_argument("--start", type=_month, help="first month YYYY-MM")
    v.add_argument("--end", type=_month, help="last month YYYY-MM (default: last complete month)")
    v.add_argument("--months", type=int, default=24, help="window length if --start is not given (default 24)")
    v.add_argument("--granularity", default="monthly", choices=["monthly", "daily", "yearly"])
    v.add_argument("--exclude-months", help="calendar months to drop before summing, e.g. 1 or 12,1")
    v.add_argument("--days", type=int, help="daily views for the last N days up to yesterday (includes the current month)")
    v.add_argument("--access", default="all-access", choices=["all-access", "desktop", "mobile-web", "mobile-app", "mobile"],
                   help="all-access (default), desktop, mobile-web, mobile-app, or mobile (= web + app)")
    v.add_argument("--agent", default="user", choices=["user", "all-agents", "automated", "spider"])
    v.add_argument("--totals", action="store_true", help="add the whole edition's views and the topic share")
    v.add_argument("--chart", action="store_true", help="also save a line chart (PNG) of the printed series")
    v.add_argument("--no-redirects", action="store_true")
    v.add_argument("--out", help="CSV path (default: in $WIKI_INTEREST_OUT)")

    t = sub.add_parser("top", help="most viewed articles of a language edition in a month (topic discovery)")
    t.add_argument("--lang", required=True)
    t.add_argument("--month", type=_month, help="YYYY-MM (default: last complete month)")
    t.add_argument("--limit", type=int, default=25)
    t.add_argument("--match", help="keep titles containing this text (case-insensitive)")
    t.add_argument("--access", default="all-access", choices=["all-access", "desktop", "mobile-web", "mobile-app", "mobile"],
                   help="all-access (default), desktop, mobile-web, mobile-app, or mobile (= web + app)")

    r = sub.add_parser("report", help="one-page PDF from an analysis directory + your notes.md")
    r.add_argument("dir", nargs="?", help="analysis directory printed by analyze")
    r.add_argument("--notes", help="notes.md with ## Headline, ## Key points, ## Recommendation, ## Next steps; "
                                   "'-' reads them from stdin (heredoc)")
    r.add_argument("--lang", default="en", help="report labels language: en or uk (default en)")
    r.add_argument("--out", help="PDF path (default <dir>/report.pdf)")
    r.add_argument("--allow-numbers", default="", help="comma-separated numbers given by the user (e.g. their thresholds)")
    r.add_argument("--template", action="store_true", help="print the notes.md template and exit")
    return p


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    if not config.contact_configured():
        print("[wiki] note: WIKI_CONTACT is not set; using the project URL as the User-Agent contact.", file=sys.stderr)
    from .http import ApiError
    from .sites import UnknownLanguage

    try:
        return {"find": cmd_find, "analyze": cmd_analyze, "views": cmd_views, "top": cmd_top,
                "report": cmd_report}[args.cmd](args)
    except UnknownLanguage as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_INPUT
    except ApiError as e:
        print(f"Error: {e}. Wait a minute and retry; if it persists the Wikimedia API may be down.", file=sys.stderr)
        return EXIT_NETWORK
    except ValueError as e:  # TopicError, NotesError and other input problems
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_INPUT


def _context():
    from .analysis import _context as ctx

    return ctx()


def cmd_find(args) -> int:
    from . import render
    from .resolve import find_topic
    from .sites import split_langs

    _, http, index = _context()
    sites = index.resolve_many(split_langs(args.langs))
    results = []
    for q in args.topics:
        lang = args.search_lang or ("en" if q.isascii() else (sites[0].lang_code if sites else "en"))
        res = find_topic(http, index, q, sites, search_lang=lang, limit=args.limit)
        if not res["candidates"] and lang != "en":
            res = find_topic(http, index, q, sites, search_lang="en", limit=args.limit)
        results.append(res)
    print(render.find_summary(results, sites))
    return EXIT_OK if any(r["candidates"] for r in results) else EXIT_NOT_FOUND


def cmd_analyze(args) -> int:
    from . import analysis
    from .sites import split_langs

    command = "uv run scripts/wiki.py " + " ".join(shlex.quote(a) for a in sys.argv[1:]) if sys.argv[1:] else None
    weights = None
    if args.weights:
        weights = {}
        for part in args.weights.replace(" ", "").split(","):
            key, _, val = part.partition("=")
            if key not in ("growth", "share", "views", "confidence"):
                raise ValueError(f"--weights: unknown criterion '{key}'; use growth, share, views, confidence")
            try:
                weights[key] = float(val or 1)
            except ValueError:
                raise ValueError(f"--weights: '{part}' must look like growth=2") from None
    res = analysis.run(args.topics, split_langs(args.langs), months=args.months, start=args.start, end=args.end,
                       redirects=not args.no_redirects, access=args.access, agent=args.agent, rank_by=args.rank_by,
                       min_views=args.min_views, min_growth=args.min_growth, weights=weights,
                       exclude_months=_months_arg(args.exclude_months), out=args.out, command=command)
    print(Path(res["files"]["summary"]).read_text(encoding="utf-8"))
    st = res["_stats"]
    print(f"[wiki] {st['api_requests']} API requests; cache: hits={st['series_cached']} "
          f"fetched={st['series_fetched']} (daily series)", file=sys.stderr)
    ok = any(s["status"] == "ok" for s in res["series"])
    return EXIT_OK if ok else EXIT_NOT_FOUND


def _months_arg(value: str | None) -> list[int]:
    if not value:
        return []
    try:
        months = [int(x) for x in value.replace(" ", "").split(",") if x]
    except ValueError:
        raise ValueError("--exclude-months takes month numbers, e.g. 1 or 12,1") from None
    if any(m < 1 or m > 12 for m in months):
        raise ValueError("--exclude-months: months must be 1..12")
    return months


def cmd_views(args) -> int:
    import numpy as np

    from . import analysis, metrics as M, pageviews as PV, render
    from .sites import split_langs

    cache, http, index = _context()
    warnings = analysis.Warnings()
    if args.days:
        last_day = date.today() - timedelta(days=1)
        first_day = last_day - timedelta(days=max(args.days, 1) - 1)
        args.granularity = "daily"
        months_list = M.month_list(first_day.strftime("%Y-%m"), last_day.strftime("%Y-%m"))
    else:
        months_list = analysis.resolve_window(args.months, args.start, args.end, warnings)
        warnings.text = [w for w in warnings.text if "year-over-year" not in w]  # views reports levels anyway
        first_day, last_day = PV.clamp(*M.month_bounds(months_list[0], months_list[-1]))
    col = analysis.collect(args.topics, split_langs(args.langs), first_day, last_day, redirects=not args.no_redirects,
                           access=args.access, agent=args.agent, http=http, cache=cache, index=index, warnings=warnings)
    days = col["days"]
    columns, series = [], {}
    for t in col["topics"]:
        for s in col["sites"]:
            name = f"{t.label} · {s.code}"
            if not col["plan"][(t.id, s.code)]:
                warnings.append(f"{s.code}: no article for '{t.label}'")
                continue
            topic_v, _, _ = analysis.build_series(t, s, col)
            columns.append(name)
            series[name] = topic_v
            if args.totals:
                tot = np.array([col["series_data"][(s.code, PV.TOTAL)][d] for d in days], dtype=float)
                series[f"edition · {s.code}"] = tot
                columns.append(f"edition · {s.code}")
    excl = set(_months_arg(args.exclude_months))
    if excl:
        keep = np.array([int(d[5:7]) not in excl for d in days], dtype=float)
        series = {c: v * keep for c, v in series.items()}
    if args.granularity == "monthly":
        periods = [m for m in months_list if int(m[5:7]) not in excl]
        idx = [months_list.index(m) for m in periods]
        agg = {c: M.monthly_sums(days, v, months_list)[idx] for c, v in series.items()}
    elif args.granularity == "yearly":
        years = sorted({d[:4] for d in days})
        periods = []
        for y in years:
            in_year = [m for m in months_list if m.startswith(y) and int(m[5:7]) not in excl]
            full = len([m for m in months_list if m.startswith(y)]) == 12
            periods.append(y if full else f"{y} (partial: {in_year[0][5:]}–{in_year[-1][5:]})" if in_year else y)
        agg = {c: np.array([sum(v[i] for i, d in enumerate(days) if d[:4] == y) for y in years]) for c, v in series.items()}
    else:
        periods = [d for d in days if int(d[5:7]) not in excl]
        idx = [i for i, d in enumerate(days) if int(d[5:7]) not in excl]
        agg = {c: v[idx] for c, v in series.items()}
    rows = []
    for i, per in enumerate(periods):
        row = {"period": per}
        for c in columns:
            row[c] = int(agg[c][i])
        if args.totals:
            for t in col["topics"]:
                for s in col["sites"]:
                    c, e = f"{t.label} · {s.code}", f"edition · {s.code}"
                    if c in agg and agg[e][i] > 0:
                        row[f"share/M {c}"] = round(agg[c][i] / agg[e][i] * 1e6, 3)
        rows.append(row)
    cols = list(rows[0].keys())[1:] if rows else columns
    out = Path(args.out).expanduser() if args.out else config.out_dir() / f"views-{datetime.now():%Y%m%d-%H%M%S}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["period", *cols])
        w.writeheader()
        w.writerows(rows)
    note = (f"## Views ({args.agent}, {args.access}, {'no redirects' if args.no_redirects else 'redirects included'}), "
            f"{periods[0]} … {periods[-1]}, {args.granularity}")
    if excl:
        note += f"; months excluded: {', '.join(str(m) for m in sorted(excl))}"
    if warnings.text:
        note += "\n" + "\n".join(f"- {w}" for w in warnings.text)
    if args.chart and rows:
        from . import charts

        plot_cols = [c for c in cols if not c.startswith(("edition ·", "share/M"))] or cols
        png = out.with_suffix(".png")
        charts.render_views_chart([r["period"] for r in rows], {c: [r.get(c, 0) for r in rows] for c in plot_cols},
                                  note.splitlines()[0].lstrip("# "), png)
        note += f"\nChart: {png.resolve()}"
    print(render.views_table(rows, cols, str(out.resolve()), note))
    return EXIT_OK if columns else EXIT_NOT_FOUND


def cmd_top(args) -> int:
    from . import analysis, pageviews as PV, render

    _, http, index = _context()
    site = index.resolve(args.lang)
    month = args.month or analysis.last_complete_month()
    y, m = map(int, month.split("-"))
    arts = PV.top_articles(http, site, y, m, args.access)
    prefixes, mainpage = PV.namespace_prefixes(http, site)
    rows = []
    for a in arts:
        title = a["article"]
        low = title.lower()
        if title == mainpage or title == "-" or (":" in title and low.split(":", 1)[0] in prefixes):
            continue
        if args.match and args.match.lower().replace(" ", "_") not in low:
            continue
        rows.append(a)
        if len(rows) >= args.limit:
            break
    print(render.top_summary(site, month, rows, args.match))
    return EXIT_OK if rows else EXIT_NOT_FOUND


def cmd_report(args) -> int:
    from . import report

    if args.template:
        print(report.NOTES_TEMPLATE)
        return EXIT_OK
    if not args.dir or not args.notes:
        print("Error: report needs the analysis directory and --notes notes.md "
              "(print a template with: uv run scripts/wiki.py report --template)", file=sys.stderr)
        return EXIT_INPUT
    d = Path(args.dir).expanduser()
    results_path = d / "results.json" if d.is_dir() else d
    if not results_path.exists():
        print(f"Error: {results_path} not found — pass the directory printed by analyze", file=sys.stderr)
        return EXIT_INPUT
    allow = [float(x) for x in args.allow_numbers.replace(" ", "").split(",") if x]
    if args.notes == "-":  # notes piped via a heredoc: saved next to the results for reproducibility
        notes_path = results_path.parent / "notes.md"
        notes_path.write_text(sys.stdin.read(), encoding="utf-8")
    else:
        notes_path = Path(args.notes).expanduser()
    if not notes_path.exists():
        print(f"Error: notes file {notes_path} not found", file=sys.stderr)
        return EXIT_INPUT
    res = report.build_report(results_path, notes_path, lang=args.lang,
                              out=Path(args.out).expanduser() if args.out else None, allow_numbers=allow)
    print(f"PDF: {res['pdf']} ({res['pages']} page)")
    for w in res.get("warnings", []):
        print(f"- warning: {w}")
    print("Next: reply to the user with the full answer, not just the link: direct answer; per language/topic the "
          "growth [range], direction and confidence; the data window; the articles measured (proxies called proxies); "
          "key limitations; then the PDF path.")
    return EXIT_OK
