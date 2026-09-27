"""One-page PDF report built from results.json plus the agent's short notes (notes.md).

The code writes every number, table and chart; the agent only supplies the words (headline,
key points, recommendation, next steps). Before rendering, each number in the notes is looked
up in results.json, so a report can never carry a figure the analysis did not produce.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import MethodReturnValue, XPos, YPos

from . import charts, i18n
from .numbers import fmt_ci, fmt_pct, fmt_share, fmt_views, ungrounded_numbers


class NotesError(ValueError):
    """The notes file is missing, malformed or cites numbers that are not in the results."""


NOTES_TEMPLATE = """\
## Headline
One sentence that answers the user's question (about 120 characters).

## Key points
- A finding with a number copied from summary.md (e.g. relative growth and its confidence)
- A second finding
- A third finding (optional)

## Recommendation
Two or three sentences: what to do next and why.

## Next steps
- A concrete follow-up check (e.g. a landing-page test in the leading market)
- Another step (optional)

## Caveats
- Optional: limitations specific to this question (the standard ones are added automatically)
"""
NOTES_HINT = (
    "Write notes.md in the user's language with the sections below. Use only numbers that appear in "
    "summary.md / results.json; numbers the user gave you (e.g. their thresholds) go to --allow-numbers."
)

# --- page geometry (millimetres, A4 portrait) -------------------------------------------------
PAGE_W, PAGE_H = 210.0, 297.0
MARGIN = 12.0
CONTENT_W = PAGE_W - 2 * MARGIN
COL_GAP = 6.0
CHART_GAP = 4.0
TREND_SHARE = 0.57  # the trend chart gets a bit more width than the growth bars
BLOCK_GAP = 2.6
MIN_CHART_H = 34.0  # below this the charts stop being readable
MAX_CHART_H = 70.0
# When the page has room, the charts are stacked at full width instead of side by side:
# a wider trend chart and one bar row per series read better than two narrow panels.
STACK_TREND_MIN, STACK_TREND_MAX = 52.0, 78.0

INK = (11, 11, 11)
INK_2 = (82, 81, 78)
MUTED = (137, 135, 129)
HAIRLINE = (225, 224, 217)

_SECTION_ALIASES = {
    "headline": ("headline", "title", "заголовок"),
    "key_points": ("key points", "key findings", "findings", "ключові висновки", "ключові пункти", "висновки"),
    "recommendation": ("recommendation", "recommendations", "рекомендація", "рекомендації"),
    "next_steps": ("next steps", "наступні кроки", "кроки"),
    "caveats": ("caveats", "limitations", "застереження", "обмеження"),
}
_HEADING_RE = re.compile(r"^\s{0,3}#{1,4}\s+(.+?)\s*#*\s*$")
_BULLET_RE = re.compile(r"^\s*(?:[-*•–]|\d+[.)])\s+(.*)$")


@dataclass(frozen=True)
class Density:
    """One step of the auto-fit ladder: smaller type and shorter lists as the level rises."""

    body: float
    small: float
    headline: float
    key_points: int
    text_cap: int  # characters per bullet / paragraph
    table_rows: int
    reasons: int
    caveats: int
    next_steps: int
    line: float = 1.35  # line height as a multiple of the font size


LEVELS = (
    Density(body=8.6, small=7.4, headline=15, key_points=3, text_cap=420, table_rows=14,
            reasons=5, caveats=6, next_steps=3),
    Density(body=8.1, small=7.1, headline=14, key_points=3, text_cap=320, table_rows=12,
            reasons=5, caveats=5, next_steps=3),
    Density(body=7.6, small=6.8, headline=13, key_points=3, text_cap=250, table_rows=10,
            reasons=4, caveats=4, next_steps=3),
    Density(body=7.1, small=6.4, headline=12, key_points=3, text_cap=200, table_rows=8,
            reasons=3, caveats=3, next_steps=2),
    Density(body=6.6, small=6.0, headline=11, key_points=3, text_cap=160, table_rows=6,
            reasons=3, caveats=3, next_steps=2),
)


# --- notes ------------------------------------------------------------------------------------
def _strip_md(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(\*\*|__|`)", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _section_key(heading: str) -> str | None:
    h = heading.strip().rstrip(":").lower()
    for key, aliases in _SECTION_ALIASES.items():
        if h in aliases:
            return key
    return None


def parse_notes(text: str) -> dict:
    """Split notes.md into headline, key_points, recommendation, next_steps and caveats."""
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            current = _section_key(m.group(1))
            if current:
                sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)

    def items(lines: list[str]) -> list[str]:
        out: list[str] = []
        for line in lines:
            if not line.strip():
                continue
            b = _BULLET_RE.match(line)
            if b:
                out.append(b.group(1))
            elif out:
                out[-1] += " " + line.strip()
            else:
                out.append(line.strip())
        return [_strip_md(i) for i in out if _strip_md(i)]

    def paragraph(lines: list[str]) -> str:
        return " ".join(items(lines))

    return {
        "headline": paragraph(sections.get("headline", [])),
        "key_points": items(sections.get("key_points", [])),
        "recommendation": paragraph(sections.get("recommendation", [])),
        "next_steps": items(sections.get("next_steps", [])),
        "caveats": items(sections.get("caveats", [])),
    }


def _citable(results: dict) -> dict:
    """The part of results.json whose numbers the notes may quote (no raw monthly arrays or paths)."""
    pruned = {k: v for k, v in results.items() if k not in ("files", "created_at", "series")}
    pruned["series"] = [{k: v for k, v in s.items() if k != "monthly"} for s in results.get("series") or []]
    return pruned


def check_notes_numbers(notes: dict, results: dict, allow_numbers=()) -> list[str]:
    text = "\n".join([notes["headline"], *notes["key_points"], notes["recommendation"],
                      *notes["next_steps"], *notes["caveats"]])
    return ungrounded_numbers(text, [_citable(results), results.get("params") or {}], allow=allow_numbers)


# --- text helpers -----------------------------------------------------------------------------
def _cap(text: str, limit: int) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


class _Sanitizer:
    def __init__(self) -> None:
        self.replaced: set[str] = set()

    def __call__(self, text) -> str:
        clean, bad = charts.sanitize("" if text is None else str(text))
        self.replaced |= bad
        return clean


# --- layout -----------------------------------------------------------------------------------
class _Page:
    """Thin wrapper over FPDF with measuring helpers; auto page breaks are off, so the
    document can never grow a second page — overflow is handled by the auto-fit ladder."""

    def __init__(self) -> None:
        self.pdf = FPDF(orientation="P", unit="mm", format="A4")
        self.pdf.set_auto_page_break(False)
        self.pdf.set_margins(MARGIN, MARGIN, MARGIN)
        self.pdf.add_font("DejaVu", "", str(charts.FONT_REGULAR))
        self.pdf.add_font("DejaVu", "B", str(charts.FONT_BOLD))
        self.pdf.add_page()

    def font(self, size: float, bold: bool = False, color=INK) -> None:
        self.pdf.set_font("DejaVu", "B" if bold else "", size)
        self.pdf.set_text_color(*color)

    def height(self, text: str, w: float, size: float, bold: bool = False, line: float = 1.35) -> float:
        if not text:
            return 0.0
        self.font(size, bold)
        return self.pdf.multi_cell(w, size * line * 0.3528, text, dry_run=True, output=MethodReturnValue.HEIGHT)

    def write(self, x: float, y: float, text: str, w: float, size: float, bold: bool = False,
              color=INK, line: float = 1.35, align: str = "L") -> float:
        if not text:
            return y
        self.font(size, bold, color)
        self.pdf.set_xy(x, y)
        self.pdf.multi_cell(w, size * line * 0.3528, text, align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        return self.pdf.get_y()

    def bullets_height(self, items: list[str], w: float, size: float, line: float) -> float:
        return sum(self.height("• " + i, w, size, line=line) for i in items)

    def write_bullets(self, x: float, y: float, items: list[str], w: float, size: float, line: float,
                      color=INK) -> float:
        for item in items:
            y = self.write(x, y, "• " + item, w, size, color=color, line=line)
        return y

    def hline(self, y: float, x0: float = MARGIN, x1: float = PAGE_W - MARGIN) -> None:
        self.pdf.set_draw_color(*HAIRLINE)
        self.pdf.set_line_width(0.2)
        self.pdf.line(x0, y, x1, y)

    def fit(self, text: str, w: float) -> str:
        """Shorten `text` with an ellipsis until it fits in one table cell of width `w`."""
        if self.pdf.get_string_width(text) <= w:
            return text
        while text and self.pdf.get_string_width(text + "…") > w:
            text = text[:-1]
        return text + "…"


def _row_order(results: dict) -> list[dict]:
    return charts._ordered_rows(results)


def _table_rows(results: dict, labels: dict, clean: _Sanitizer) -> list[list[str] | dict]:
    rows = []
    for s in _row_order(results):
        m = s.get("metrics") or {}
        v = s.get("verdict") or {}
        direction = v.get("direction") or "n/a"
        conf = v.get("confidence") or "n/a"
        arrow = {"growing": "↑ ", "declining": "↓ ", "flat": "→ ", "uncertain": "? "}.get(direction, "")
        if s.get("status") == "ok":
            yoy = m.get("yoy_rel")
            yoy_text = f"{fmt_pct(yoy)} {fmt_ci(m.get('yoy_rel_ci'))}" if yoy is not None else "n/a"
            cells = [clean(s.get("topic_label")), clean(s.get("lang")), fmt_views(m.get("avg_daily_views_12m")),
                     fmt_share(m.get("share_ppm_12m")), yoy_text, fmt_pct(m.get("yoy_raw")),
                     arrow + labels["direction"].get(direction, direction), labels["confidence"].get(conf, conf)]
        else:
            status_text = labels["status"].get(s.get("status"), s.get("status") or "n/a")
            cells = [clean(s.get("topic_label")), clean(s.get("lang")), "—", "—", status_text, "—",
                     labels["direction"]["n/a"], labels["confidence"]["n/a"]]
        rows.append({"cells": cells, "confidence": conf if s.get("status") == "ok" else "n/a"})
    return rows


def _how_sure(results: dict, labels: dict, clean: _Sanitizer, lang: str = "en") -> list[str]:
    lines = []
    comp = results.get("comparison") or {}
    ranking = comp.get("ranking") or []
    if len(ranking) >= 2:
        rank_by = labels["rank_by"].get(comp.get("rank_by"), comp.get("rank_by") or "")
        sentence = labels["leader"].format(rank_by=rank_by, label=clean(ranking[0].get("label")))
        if comp.get("leader_stable"):
            sentence += " " + labels["leader_stable"].format(stable=comp["leader_stable"])
        if comp.get("leader_ci_overlap") is not None:
            sentence += "; " + (labels["overlap_yes"] if comp["leader_ci_overlap"] else labels["overlap_no"])
        lines.append(sentence + ".")
    note_codes = comp.get("note_codes")
    if note_codes:
        label_of = {s["key"]: charts.series_label(s) for s in results.get("series", [])}
        for n in note_codes:
            if n["code"] == "overlap" and comp.get("leader_ci_overlap") is not None:
                continue  # already said in the leader sentence above
            params = dict(n["params"])
            if params.get("keys"):
                params["labels"] = ", ".join(label_of.get(k, k) for k in params["keys"])
            lines.append(clean(i18n.render(n["code"], params, lang)))
    else:
        lines += [clean(n) for n in comp.get("notes") or []]
    grouped: dict[str, list[str]] = {}
    for s in _row_order(results):
        if s.get("status") != "ok":
            continue
        v = s.get("verdict") or {}
        texts = ([i18n.render(c["code"], c["params"], lang) for c in v["reason_codes"]]
                 if v.get("reason_codes") else v.get("reasons") or [])
        for reason in texts:
            grouped.setdefault(clean(reason), []).append(clean(charts.series_label(s)))
    for reason, who in grouped.items():
        names = ", ".join(who[:3]) + (f" +{len(who) - 3}" if len(who) > 3 else "")
        lines.append(f"{names}: {reason}")
    return lines


def _limitations(results: dict, notes: dict, clean: _Sanitizer, lang: str = "en") -> list[str]:
    seen, out = set(), []
    if "warning_codes" in results:
        warnings = [i18n.render(w["code"], w["params"], lang) for w in results["warning_codes"]]
    else:
        warnings = results.get("warnings") or []
    if results.get("caveat_codes"):
        caveats = [i18n.render(c, None, lang) for c in results["caveat_codes"]]
    else:
        caveats = results.get("caveats") or []
    for item in [*warnings, *notes["caveats"], *caveats]:
        text = clean(item)
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _meta_line(results: dict, labels: dict, clean: _Sanitizer) -> str:
    p = results.get("params") or {}
    parts = [labels["source"]]
    if p.get("start") and p.get("end"):
        window = f"{labels['window']}: {p['start']} – {p['end']}"
        if p.get("months"):
            window += f" ({p['months']} {labels['months']})"
        parts.append(window)
    if p.get("langs"):
        parts.append(f"{labels['languages']}: {', '.join(clean(x) for x in p['langs'])}")
    parts.append(f"{labels['generated']}: {datetime.now(timezone.utc).date().isoformat()}")
    return " · ".join(parts)


def _footer(results: dict, labels: dict, clean: _Sanitizer) -> list[str]:
    cmd = (results.get("params") or {}).get("command")
    lines = []
    if cmd:
        lines.append(f"{labels['reproduce']}: {_cap(clean(cmd), 260)}")
    lines.append(f"wikipedia-interest-research {results.get('tool_version', '')}".strip())
    return lines


# column widths (mm) of the metrics table; they add up to CONTENT_W
_TABLE_COLS = (34.0, 11.0, 20.0, 18.0, 43.0, 18.0, 24.0, 18.0)
_TABLE_KEYS = ("topic", "lang", "views", "share", "yoy_rel", "yoy_raw", "direction", "confidence")


def _header_lines(page: _Page, labels: dict, d: Density) -> list[list[str]]:
    """Column headers wrapped to at most two lines each; every column gets the same line count."""
    page.font(d.small - 0.6, bold=True)
    out = []
    for w, key in zip(_TABLE_COLS, _TABLE_KEYS):
        words, lines, cur = labels["table"][key].split(), [], ""
        for word in words:
            cand = f"{cur} {word}".strip()
            if page.pdf.get_string_width(cand) <= w - 1.0 or not cur:
                cur = cand
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
        if len(lines) > 2:
            lines = [lines[0], " ".join(lines[1:])]
        out.append([page.fit(line, w - 1.0) for line in lines])
    depth = max(len(c) for c in out)
    return [c + [""] * (depth - len(c)) for c in out]


def _render(results: dict, notes: dict, labels: dict, d: Density, clean: _Sanitizer, assets_dir: Path,
            lang: str, final: bool) -> FPDF | None:
    """Lay the page out at density `d`; return None if it does not fit (unless `final`)."""
    page = _Page()
    lh = d.line
    half_w = (CONTENT_W - COL_GAP) / 2

    headline = _cap(clean(notes["headline"]), 200)
    meta = _meta_line(results, labels, clean)
    key_points = [_cap(clean(k), d.text_cap) for k in notes["key_points"][: d.key_points]]
    rows = _table_rows(results, labels, clean)
    hidden_rows = max(0, len(rows) - d.table_rows)
    rows = rows[: d.table_rows]
    reasons = [_cap(r, d.text_cap) for r in _how_sure(results, labels, clean, lang)][: d.reasons]
    limits = [_cap(c, d.text_cap) for c in _limitations(results, notes, clean, lang)][: d.caveats]
    recommendation = _cap(clean(notes["recommendation"]), d.text_cap * 2)
    next_steps = [_cap(clean(s), d.text_cap) for s in notes["next_steps"][: d.next_steps]]
    footer = _footer(results, labels, clean)

    row_h = d.small * 1.75 * 0.3528
    header_lines = _header_lines(page, labels, d)
    header_h = row_h * 0.8 * len(header_lines[0]) + row_h * 0.25

    def block_heights() -> dict:
        h = {}
        h["headline"] = page.height(headline, CONTENT_W, d.headline, bold=True, line=1.2)
        h["meta"] = page.height(meta, CONTENT_W, d.small - 0.4, line=lh)
        h["key_points"] = (page.height(labels["key_points"], CONTENT_W, d.body, bold=True, line=lh)
                           + page.bullets_height(key_points, CONTENT_W, d.body, lh)) if key_points else 0.0
        h["table"] = header_h + row_h * len(rows) + (row_h if hidden_rows else 0) + 1.0
        left = page.height(labels["how_sure"], half_w, d.body, bold=True, line=lh) + \
            page.bullets_height(reasons, half_w, d.small, lh)
        right = page.height(labels["assumptions"], half_w, d.body, bold=True, line=lh) + \
            page.bullets_height(limits, half_w, d.small, lh)
        h["sure_limits"] = max(left, right)
        left = (page.height(labels["recommendation"], half_w, d.body, bold=True, line=lh)
                + page.height(recommendation, half_w, d.body, line=lh)) if recommendation else 0.0
        right = (page.height(labels["next_steps"], half_w, d.body, bold=True, line=lh)
                 + page.bullets_height(next_steps, half_w, d.body, lh)) if next_steps else 0.0
        h["rec_next"] = max(left, right)
        h["footer"] = sum(page.height(f, CONTENT_W, d.small - 1.0, line=1.25) for f in footer)
        return h

    heights = block_heights()
    n_blocks = sum(1 for v in heights.values() if v > 0) + 1  # + charts (a second gap if stacked)
    fixed = sum(heights.values()) + BLOCK_GAP * n_blocks
    available = PAGE_H - 2 * MARGIN - fixed
    while available < MIN_CHART_H:
        if not final:
            return None
        # last level: drop the least important lines until the charts fit
        if next_steps and len(next_steps) > 1:
            next_steps.pop()
        elif len(limits) > 1:
            limits.pop()
        elif len(reasons) > 1:
            reasons.pop()
        elif len(rows) > 3:
            rows.pop()
            hidden_rows += 1
        elif len(key_points) > 1:
            key_points.pop()
        elif recommendation and len(recommendation) > 120:
            recommendation = _cap(recommendation, 120)
        else:
            break  # nothing left to trim; charts get the minimum height below
        heights = block_heights()
        fixed = sum(heights.values()) + BLOCK_GAP * n_blocks
        available = PAGE_H - 2 * MARGIN - fixed
    n_bars = min(len(charts._ordered_rows(results)), charts.MAX_BARS)
    stacked_growth_h = min(85.0, max(38.0, 20.0 + 5.4 * n_bars))
    stacked = available >= STACK_TREND_MIN + stacked_growth_h + BLOCK_GAP
    mm = 1 / 25.4
    if stacked:
        trend_w = growth_w = CONTENT_W
        trend_h = min(STACK_TREND_MAX, available - stacked_growth_h - BLOCK_GAP)
        growth_h = stacked_growth_h
        chart_pt = max(6.0, d.small - 0.2)
    else:
        trend_w = (CONTENT_W - CHART_GAP) * TREND_SHARE
        growth_w = CONTENT_W - CHART_GAP - trend_w
        trend_h = growth_h = max(MIN_CHART_H * 0.8, min(MAX_CHART_H, available))
        chart_pt = max(5.6, d.small - 0.6)
    # charts are rendered at their box size and placed 1:1, so type sizes in points stay true
    trend_png = charts.render_trend(results, assets_dir / f"trend.{lang}.png", lang=lang, width_in=trend_w * mm,
                                    height_in=trend_h * mm, font_pt=chart_pt, source_line=False)
    # about 4 mm per bar row plus title/axis/legend keeps labels legible in a short panel
    bar_rows = charts.MAX_BARS if stacked else max(3, int((growth_h - 26.0) / 4.0))
    growth_png = charts.render_growth(results, assets_dir / f"growth.{lang}.png", lang=lang,
                                      width_in=growth_w * mm, height_in=growth_h * mm, font_pt=chart_pt,
                                      source_line=False, max_rows=bar_rows)

    # --- draw ---
    x0 = MARGIN
    y = MARGIN
    y = page.write(x0, y, headline, CONTENT_W, d.headline, bold=True, line=1.2)
    y = page.write(x0, y + 0.6, meta, CONTENT_W, d.small - 0.4, color=MUTED, line=lh)
    y += BLOCK_GAP
    if key_points:
        y = page.write(x0, y, labels["key_points"], CONTENT_W, d.body, bold=True, color=INK_2, line=lh)
        y = page.write_bullets(x0, y, key_points, CONTENT_W, d.body, lh)
        y += BLOCK_GAP

    if stacked:
        page.pdf.image(str(trend_png), x=x0, y=y, w=trend_w, h=trend_h)
        y += trend_h + BLOCK_GAP
        page.pdf.image(str(growth_png), x=x0, y=y, w=growth_w, h=growth_h)
        y += growth_h + BLOCK_GAP
    else:
        page.pdf.image(str(trend_png), x=x0, y=y, w=trend_w, h=trend_h)
        page.pdf.image(str(growth_png), x=x0 + trend_w + CHART_GAP, y=y, w=growth_w, h=growth_h)
        y += trend_h + BLOCK_GAP

    # metrics table
    page.font(d.small - 0.6, bold=True, color=INK_2)
    x = x0
    for w, lines in zip(_TABLE_COLS, header_lines):
        for k, line in enumerate(lines):
            page.pdf.set_xy(x, y + k * row_h * 0.8)
            page.pdf.cell(w, row_h * 0.8, line)
        x += w
    y += header_h
    page.hline(y)
    for row in rows:
        x = x0
        for i, (w, cell) in enumerate(zip(_TABLE_COLS, row["cells"])):
            page.font(d.small, color=INK)
            page.pdf.set_xy(x, y)
            if i == len(_TABLE_COLS) - 1 and row["confidence"] in charts.CONFIDENCE_COLORS:
                r, g, b = (int(charts.CONFIDENCE_COLORS[row["confidence"]][k:k + 2], 16) for k in (1, 3, 5))
                page.pdf.set_fill_color(r, g, b)
                sq = row_h * 0.42
                page.pdf.rect(x, y + (row_h - sq) / 2, sq, sq, style="F")
                page.pdf.set_xy(x + sq + 1.0, y)
                page.pdf.cell(w - sq - 1.0, row_h, page.fit(cell, w - sq - 2.0))
            else:
                page.pdf.cell(w, row_h, page.fit(cell, w - 1.2))
            x += w
        y += row_h
        page.hline(y)
    if hidden_rows:
        y = page.write(x0, y + 0.3, labels["more_rows"].format(n=hidden_rows), CONTENT_W, d.small - 0.4,
                       color=MUTED, line=lh)
    y += BLOCK_GAP + 1.0

    # how sure | assumptions & limitations
    top = y
    yl = page.write(x0, top, labels["how_sure"], half_w, d.body, bold=True, color=INK_2, line=lh)
    yl = page.write_bullets(x0, yl, reasons, half_w, d.small, lh)
    xr = x0 + half_w + COL_GAP
    yr = page.write(xr, top, labels["assumptions"], half_w, d.body, bold=True, color=INK_2, line=lh)
    yr = page.write_bullets(xr, yr, limits, half_w, d.small, lh, color=INK_2)
    y = max(yl, yr) + BLOCK_GAP

    # recommendation | next steps
    if recommendation or next_steps:
        top = y
        yl, yr = top, top
        if recommendation:
            yl = page.write(x0, top, labels["recommendation"], half_w, d.body, bold=True, color=INK_2, line=lh)
            yl = page.write(x0, yl, recommendation, half_w, d.body, line=lh)
        if next_steps:
            yr = page.write(xr, top, labels["next_steps"], half_w, d.body, bold=True, color=INK_2, line=lh)
            yr = page.write_bullets(xr, yr, next_steps, half_w, d.body, lh)
        y = max(yl, yr)

    # footer pinned to the bottom margin
    fy = PAGE_H - MARGIN - heights["footer"]
    page.hline(fy - 1.0)
    for line in footer:
        fy = page.write(x0, fy, line, CONTENT_W, d.small - 1.0, color=MUTED, line=1.25)
    return page.pdf


def localized(results: dict, lang: str) -> dict:
    """Copy of the results with topic labels in the report language (Wikidata labels when available)."""
    view = copy.deepcopy(results)
    names = {t["id"]: (t.get("labels") or {}).get(lang) for t in (view.get("params") or {}).get("topics", [])}
    by_key = {}
    for s in view.get("series", []):
        new = names.get(s.get("topic_id"))
        if new:
            s["topic_label"] = new
        by_key[s["key"]] = f"{s['topic_label']} · {s['lang']}"
    for e in ((view.get("comparison") or {}).get("ranking") or []):
        e["label"] = by_key.get(e["key"], e["label"])
    return view


def build_report(results_path, notes_path, lang: str = "en", out=None, allow_numbers=()) -> dict:
    """Render the one-page PDF for an analysis; returns {"pdf", "pages", "warnings"}."""
    results_path = Path(results_path)
    notes_path = Path(notes_path)
    results = json.loads(results_path.read_text(encoding="utf-8"))
    if not notes_path.exists():
        raise NotesError(f"Notes file not found: {notes_path}\n{NOTES_HINT}\n\n{NOTES_TEMPLATE}")
    notes = parse_notes(notes_path.read_text(encoding="utf-8"))
    if not notes["headline"]:
        raise NotesError(
            f"{notes_path} has no '## Headline' section (or it is empty). Every report needs a one-sentence "
            f"headline that answers the user's question.\n{NOTES_HINT}\n\n{NOTES_TEMPLATE}")
    bad = check_notes_numbers(notes, results, allow_numbers)
    if bad:
        raise NotesError(
            "These numbers in the notes are not in the analysis results: " + ", ".join(bad) + ".\n"
            "Every number in the report must come from the analysis. Fix: replace each with the value shown in "
            "summary.md / results.json, or remove it (describe it in words instead). If a number was given by the "
            "user (e.g. their own threshold), pass it with --allow-numbers, e.g. --allow-numbers "
            + ",".join(re.sub(r"[^\d.,]", "", b).replace(",", ".") for b in bad[:3]) + ".")

    labels = charts.load_labels(lang)
    clean = _Sanitizer()
    view = localized(results, lang)
    assets_dir = results_path.parent / "report_assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    pdf = None
    for i, density in enumerate(LEVELS):
        pdf = _render(view, notes, labels, density, clean, assets_dir, lang, final=i == len(LEVELS) - 1)
        if pdf is not None:
            break
    pages = pdf.pages_count
    if pages != 1:  # auto page breaks are off, so this would be a bug in the layout code
        raise RuntimeError(f"report layout produced {pages} pages instead of 1")

    out_path = Path(out) if out else results_path.parent / "report.pdf"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))

    warnings = []
    if clean.replaced:
        chars = "".join(sorted(clean.replaced))[:20]
        warnings.append(
            f"The PDF font cannot draw some characters ({chars}); they were replaced with '?'. "
            "CJK, Arabic, Hebrew and Indic scripts are not supported in the PDF: write the notes in a Latin or "
            "Cyrillic language or use English labels.")
    results.setdefault("files", {})["report_pdf"] = str(out_path.resolve())
    results_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"pdf": str(out_path.resolve()), "pages": pages, "warnings": warnings}
