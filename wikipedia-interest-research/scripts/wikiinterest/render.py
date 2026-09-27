"""Compact Markdown summaries printed to stdout — the only thing the agent needs to read."""

from __future__ import annotations

from .numbers import fmt_ci, fmt_pct, fmt_share, fmt_views

_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
           "October", "November", "December"]


def analysis_summary(r: dict) -> str:
    p = r["params"]
    langs = ", ".join(p["langs"])
    topics = "; ".join(f"{t['label']} ({'+'.join(t['qids'] + t['titles'])})" for t in p["topics"])
    lines = [f"## Wikipedia interest: {topics} — {langs}", ""]
    red = "redirects included" if p["redirects"] else "redirects excluded"
    lines.append(f"Window: {p['start']} … {p['end']} ({p['months']} months; {p['agent']} views, {p['access']}, {red}).")
    if p.get("prior"):
        lines.append(f"Growth = last 12 months ({p['recent'][0]}…{p['recent'][1]}) vs previous 12 "
                     f"({p['prior'][0]}…{p['prior'][1]}). \"Relative\" = change of the topic's share of all views "
                     "in that language edition (main metric); \"absolute\" = raw views; \"edition\" = all views of the edition.")
    lines.append("Share = views per million views of the whole edition (comparable across languages).")
    used = []
    for s in r["series"]:
        if s["articles"]:
            def art(a):
                bits = [f"since {a['created'][:7]}"] if a.get("created") else []
                if a["redirects_included"]:
                    bits.append(f"+{a['redirects_included']} redirects")
                return a["title"] + (f" ({', '.join(bits)})" if bits else "")
            arts = ", ".join(art(a) for a in s["articles"][:4])
            used.append(f"{s['lang']}: {arts}")
    if used:
        shown = "; ".join(used[:12]) + (f"; … {len(used) - 12} more" if len(used) > 12 else "")
        lines.append(f"Articles measured (name them in your answer; if they stand in for an activity or intent the "
                     f"user asked about, e.g. 'learning X', say they are proxies and also capture unrelated interest): "
                     f"{shown}.")
    lines.append("")
    lines.append("| Topic | Lang | Views/day (12m) | Share per M | Relative growth [95% range] | Absolute growth | Edition growth | Direction | Confidence |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for s in r["series"]:
        m = s["metrics"]
        if s["status"] != "ok":
            lines.append(f"| {s['topic_label']} | {s['lang']} | — | — | not measurable: {s['note']} | | | | |")
            continue
        rel = f"{fmt_pct(m.get('yoy_rel'))} {fmt_ci(m.get('yoy_rel_ci'))}" if m.get("yoy_rel") is not None else "n/a"
        lines.append(
            f"| {s['topic_label']} | {s['lang']} | {fmt_views(m['avg_daily_views_12m'])} | {fmt_share(m['share_ppm_12m'])} "
            f"| {rel} | {fmt_pct(m.get('yoy_raw'))} | {fmt_pct(m.get('project_yoy'))} "
            f"| {s['verdict']['direction']} | {s['verdict']['confidence']} |")
    lines.append("")
    ok = [s for s in r["series"] if s["status"] == "ok"]
    if ok:
        lines.append("Why this confidence:")
        for s in ok:
            reasons = "; ".join(s["verdict"]["reasons"]) or "—"
            lines.append(f"- {s['topic_label']} · {s['lang']}: {reasons}")
        extra = []
        for s in ok:
            m = s["metrics"]
            bits = []
            if m.get("prior_yoy_rel") is not None:
                bits.append(f"year before: {fmt_pct(m['prior_yoy_rel'])}")
            if m.get("cagr_rel") is not None:
                bits.append(f"average yearly change over the window: {fmt_pct(m['cagr_rel'])}")
            prof = m.get("seasonal_profile")
            if prof and len(ok) <= 6:
                bits.append("seasonal profile, 100 = average month: " + " ".join(
                    f"{_MONTHS[i][:3]} {v}" for i, v in enumerate(prof)))
            if m.get("peak_month"):
                bits.append(f"seasonal peak in {_MONTHS[m['peak_month'] - 1]} (profile amplitude "
                            f"{fmt_pct(m['seasonality_amplitude'], signed=False)})")
            if m.get("spike_share", 0) >= 0.05 and m.get("top_spikes"):
                sp = m["top_spikes"][0]
                bits.append(f"biggest spike {sp['day']} ({sp['views']} views vs ~{sp['baseline']:.0f} usual)")
            if m.get("redirect_share", 0) >= 0.05:
                bits.append(f"{fmt_pct(m['redirect_share'], signed=False)} of views come via redirects")
            if bits:
                extra.append(f"- {s['topic_label']} · {s['lang']}: " + "; ".join(bits))
        if extra:
            lines += ["", "Context:"] + extra
    c = r.get("comparison")
    if c:
        what = {"growth": "relative growth", "share": "share of the edition", "views": "views/day"}[c["rank_by"]]
        fmt = fmt_pct if c["rank_by"] == "growth" else fmt_share if c["rank_by"] == "share" else fmt_views
        by_key = {x["key"]: x for x in r["series"]}
        ranked = ", ".join(
            f"{i}) {e['label']} {fmt(e['value'])} ({by_key[e['key']]['verdict']['direction']}, "
            f"{by_key[e['key']]['verdict']['confidence']})" for i, e in enumerate(c["ranking"], 1))
        lines += ["", f"Ranking by {what}: {ranked}"]
        if c["rank_by"] == "growth":
            lines.append("Differences within ±5% or with overlapping ranges are not meaningful; \"flat\" is not growth.")
        if c.get("leader_stable"):
            lines.append(f"Leader stays first in {c['leader_stable']} robustness checks.")
        for n in c["notes"]:
            lines.append(f"Note: {n}")
        wt = c.get("weighted")
        if wt:
            ws = ", ".join(f"{k} {v:g}" for k, v in wt["weights"].items())
            ranked_w = ", ".join(f"{i}) {e['label']} {e['score']:.2f}" for i, e in enumerate(wt["ranking"], 1))
            lines.append(f"Score with the user's weights ({ws}; {wt['method']}): {ranked_w}")
    crit = [(s, s["criteria"]) for s in r["series"] if s.get("criteria")]
    if crit:
        lines += ["", "User criteria:"]
        for s, cr in crit:
            parts = [f"{k} {v['threshold']}: {'pass' if v['pass'] else 'fail'}" for k, v in cr.items()]
            lines.append(f"- {s['topic_label']} · {s['lang']}: " + ", ".join(parts))
    if r["warnings"]:
        lines += ["", "Warnings:"] + [f"- {w}" for w in r["warnings"]]
    lines += ["", "Caveats (tell the user the ones that matter for the decision):"] + [f"- {c}" for c in r["caveats"]]
    lines += ["", "Checklist for your answer (derived from this analysis):"] + [f"- {c}" for c in answer_checklist(r)]
    f = r.get("files", {})
    if f:
        lines += ["", f"Analysis directory (use this exact path): {f.get('dir')}"]
        lines.append("  files: " + ", ".join(v.rsplit("/", 1)[-1] for k, v in f.items() if k != "dir"))
        lines += ["", "Next: answer the user from this summary. Only if the user asked for a report/PDF/one-pager: "
                  f"`uv run scripts/wiki.py report {f.get('dir')} --lang <en|uk> --notes - <<'EOF'` followed by the "
                  "notes (template: `uv run scripts/wiki.py report --template`) and `EOF`."]
    return "\n".join(lines) + "\n"


def answer_checklist(r: dict) -> list[str]:
    """What a complete answer must mention, derived from the shape of the results (not the question)."""
    p, series = r["params"], r["series"]
    ok = [s for s in series if s["status"] == "ok"]
    langs = {s["lang"] for s in series}
    out = []
    if p.get("prior"):
        out.append(f"the window ({p['start']}…{p['end']}) and how growth is measured: the topic's share of the whole "
                   "edition, last 12 months vs the previous 12")
    else:
        out.append(f"the window ({p['start']}…{p['end']}); it is too short for year-over-year growth")
    out.append("direction and confidence for each series with its main reason; copy numbers exactly, do not compute "
               "ratios or differences yourself")
    out.append("which articles were measured (names above); call them proxies if they stand in for an activity, "
               "method or product the user asked about")
    if len(langs) > 1:
        out.append("levels across languages: compare 'Share per M', not views/day (editions differ in size); a "
                   "language edition is not a country (readers of a language live in several countries)")
    missing = [s for s in series if s["status"] != "ok"]
    if missing:
        out.append("not measurable: " + ", ".join(f"{s['topic_label']} · {s['lang']}" for s in missing[:6])
                   + " (no article / no views) — say so, do not fill the gap with guesses")
    red = [s for s in ok if s["metrics"].get("redirect_share", 0) >= 0.3]
    if red:
        out.append("views via redirects (former titles, other names) are included, so renames do not break the series: "
                   + ", ".join(f"{s['topic_label']} · {s['lang']}" for s in red[:4]))
    seas = [s for s in ok if s["metrics"].get("peak_month")]
    if seas:
        out.append("seasonality: " + ", ".join(f"{s['topic_label']} · {s['lang']} peaks in {_MONTHS[s['metrics']['peak_month'] - 1]}"
                                             for s in seas[:4]) + " (year-over-year compares the same months)")
    spiky = [s for s in ok if s["metrics"].get("spike_share", 0) >= 0.05 and s["metrics"].get("top_spikes")]
    if spiky:
        out.append("spikes show when interest jumped, not why; don't state causes as facts")
    low = [s for s in ok if s["verdict"]["confidence"] == "Low"]
    if low:
        out.append("weak signal for " + ", ".join(f"{s['topic_label']} · {s['lang']}" for s in low[:6])
                   + ": don't base a recommendation on it")
    out.append("Wikipedia views = informational interest, not willingness to pay")
    return out


def find_summary(results: list[dict], sites: list) -> str:
    lines = []
    for res in results:
        lines.append(f"## find: \"{res['query']}\"")
        if not res["candidates"]:
            lines.append("No Wikidata items found. Try an English or more general name, or a synonym.")
            lines.append("")
            continue
        b = res["best"]
        lines.append(f"Best match: {b['qid']} — {b['label']} — \"{b['description']}\" — in {b['wikipedias']} Wikipedias")
        lines.append("Check the description: is this what the user means? If it is only related (a person behind a "
                     "method, a company behind a product, a broader field), treat it as a labelled proxy or pick a "
                     "better candidate.")
        others = [c for c in res["candidates"] if c is not b]
        if others:
            lines.append("Other candidates: " + "; ".join(
                f"{c['qid']} {c['label']} (\"{c['description'][:60]}\", {c['wikipedias']} Wikipedias)" for c in others))
        if res["ambiguous"]:
            lines.append("AMBIGUOUS: several widely covered meanings. Choose the QID that matches the user's context; "
                         "if the context does not decide it, ask the user.")
        if res["articles"]:
            lines += ["", "| lang | edition | article for " + b["qid"] + " | status |", "|---|---|---|---|"]
            for a in res["articles"]:
                s = a["site"]
                if a["title"]:
                    lines.append(f"| {s.code} | {s.english} | {a['title']} | ok |")
                else:
                    lines.append(f"| {s.code} | {s.english} | — | NO ARTICLE (not measurable directly) |")
            for a in res["articles"]:
                if not a["title"]:
                    sug = "; ".join(f"{h['title']} — {h['snippet']}" for h in a["suggestions"]) or "no results"
                    lines.append(f"- {a['site'].code} search \"{a['search_query']}\": {sug}")
            missing = [a["site"].code for a in res["articles"] if not a["title"]]
            if missing:
                lines.append(f"For {', '.join(missing)}: say the topic has no dedicated article there. A related article "
                             "can be added as a clearly labelled proxy, e.g. `\"Proxy=" + missing[0] + ":<Title>\"`.")
        lines.append("")
    langs = ",".join(s.code for s in sites) if sites else "<codes>"
    qids = " ".join(r["best"]["qid"] for r in results if r["best"])
    if qids:
        lines.append(f"Next: uv run scripts/wiki.py analyze {qids} --langs {langs}   "
                     "(several topics = several arguments; a basket summed as one topic = Q1+Q2)")
    return "\n".join(lines) + "\n"


def views_table(rows: list[dict], columns: list[str], csv_path: str, note: str) -> str:
    lines = [note, "", "| period | " + " | ".join(columns) + " |", "|---|" + "---|" * len(columns)]
    show = rows if len(rows) <= 40 else rows[:10] + [None] + rows[-20:]
    for row in show:
        if row is None:
            lines.append("| … | " + " | ".join("…" for _ in columns) + " |")
            continue
        lines.append(f"| {row['period']} | " + " | ".join(str(row.get(c, '')) for c in columns) + " |")
    lines += ["", f"CSV: {csv_path}"]
    return "\n".join(lines) + "\n"


def top_summary(site, month: str, rows: list[dict], match: str | None) -> str:
    head = f"## Most viewed articles — {site.english} Wikipedia ({site.code}), {month}"
    if match:
        head += f", titles containing \"{match}\""
    lines = [head, "(from Wikimedia's monthly top-1000 list; main page and special pages removed)", ""]
    lines += ["| rank | article | views |", "|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['rank']} | {r['article'].replace('_', ' ')} | {r['views']} |")
    if not rows:
        lines.append("| — | no matching articles in the top 1000 | — |")
    lines += ["", "Next: to measure a trend for any of these, run `find \"<title>\" --langs " + site.code + "` then `analyze`."]
    return "\n".join(lines) + "\n"
