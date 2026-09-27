"""Charts for an analysis: relative-interest trend and year-over-year growth with intervals.

Both charts read only results.json (see schema.py). Design rules:
- one categorical hue per series, in a fixed order (colour follows the series, not its rank);
- a single y-axis: raw views for a lone series go into a second small panel, never a twin axis;
- hairline grid and a legend whenever two or more lines are shown;
- confidence as an ordinal blue ramp plus a text label, so it never relies on colour alone.
"""

from __future__ import annotations

import json
import math
import unicodedata
from datetime import date
from functools import lru_cache
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from .numbers import fmt_pct  # noqa: E402

# Categorical palette in its validated order: adjacent pairs clear colour-vision-deficiency
# ΔE >= 8 on a white surface. Series beyond eight are left out (named in the title) because a
# ninth hue would not be distinguishable.
SERIES_COLORS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948")
MAX_LINES = len(SERIES_COLORS)

# Ordinal ramp (one hue, light -> dark = less -> more confident); the lightest step keeps
# 2.1:1 contrast on white, so Low bars stay visible.
CONFIDENCE_COLORS = {"High": "#184f95", "Medium": "#3987e5", "Low": "#86b6ef", "n/a": "#c3c2b7"}

INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
RAW_BARS = "#b9b8b1"

MAX_BARS = 16  # rows in the growth chart before the tail is summarised as "+N more"
SPIKE_MONTH_SHARE = 0.2  # a month is marked when spike excess is at least 20% of its views
DPI = 150

ASSETS = Path(__file__).resolve().parents[2] / "assets"
_FONT_DIR = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
FONT_REGULAR = _FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = _FONT_DIR / "DejaVuSans-Bold.ttf"

# Right-to-left scripts need shaping and bidi reordering that neither matplotlib nor the PDF
# writer does here, so they are replaced like unsupported glyphs instead of printed garbled.
_RTL_RANGES = ((0x0590, 0x08FF), (0xFB1D, 0xFDFF), (0xFE70, 0xFEFF))


@lru_cache(maxsize=1)
def _font_codepoints() -> frozenset[int]:
    from fontTools.ttLib import TTFont  # matplotlib depends on fontTools

    return frozenset(TTFont(str(FONT_REGULAR)).getBestCmap().keys())


def sanitize(text: str) -> tuple[str, set[str]]:
    """Replace characters DejaVu Sans cannot draw correctly with "?"; return (text, replaced)."""
    if not text:
        return text or "", set()
    cps = _font_codepoints()
    out, replaced = [], set()
    for ch in text:
        cp = ord(ch)
        if ch in "\n\t":
            out.append(ch)
        elif unicodedata.category(ch) in ("Cc", "Cf"):
            continue
        elif cp not in cps or any(lo <= cp <= hi for lo, hi in _RTL_RANGES):
            out.append("?")
            replaced.add(ch)
        else:
            out.append(ch)
    return "".join(out), replaced


@lru_cache(maxsize=8)
def load_labels(lang: str = "en") -> dict:
    """UI labels for charts and the report; unknown languages fall back to English."""
    data = json.loads((ASSETS / "report_labels.json").read_text(encoding="utf-8"))
    return data.get(lang) or data["en"]


def series_label(s: dict) -> str:
    return f"{s.get('topic_label') or s.get('topic_id', '?')} · {s.get('lang', '?')}"


def _clean(text: str, limit: int | None = None) -> str:
    text = sanitize(text)[0]
    if limit and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def _wrap(fig, text: str, font_pt: float, bold: bool = False, max_lines: int = 2, frac: float = 0.96) -> str:
    """Wrap `text` to `frac` of the figure width using measured glyph widths (figures are created at the
    save DPI, so hinting matches the saved image)."""
    renderer = fig.canvas.get_renderer()
    prop = FontProperties(family="DejaVu Sans", size=font_pt, weight="bold" if bold else "normal")
    limit = fig.bbox.width * frac

    def width(t: str) -> float:
        return renderer.get_text_width_height_descent(t, prop, ismath=False)[0]

    lines, cur = [], ""
    for word in text.split():
        cand = f"{cur} {word}".strip()
        if not cur or width(cand) <= limit:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and width(last + "…") > limit:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return "\n".join(lines)


def _month_date(month: str) -> date:
    year, mon = month.split("-")[:2]
    return date(int(year), int(mon), 1)


def _style(font_pt: float) -> dict:
    return {
        "font.family": "DejaVu Sans",
        "font.size": font_pt,
        "axes.titlesize": font_pt + 1,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": font_pt,
        "axes.labelcolor": INK_2,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
        "xtick.labelsize": font_pt - 1,
        "ytick.labelsize": font_pt - 1,
        "xtick.major.size": 2.5,
        "ytick.major.size": 0,
        "legend.fontsize": font_pt - 1,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    }


def _placeholder(ax, text: str) -> None:
    ax.set_axis_off()
    ax.text(0.5, 0.5, text, ha="center", va="center", color=MUTED, transform=ax.transAxes)


def _grid(ax, axis: str) -> None:
    ax.grid(True, axis=axis, color=GRID, linewidth=0.5, linestyle="-")
    ax.set_axisbelow(True)


def _index(monthly: list[dict]) -> list[float] | None:
    shares = [m.get("share_ppm") or 0.0 for m in monthly]
    base_window = shares[:12]
    base = sum(base_window) / len(base_window) if base_window else 0.0
    if base <= 0:
        return None
    return [v / base * 100 for v in shares]


def _short_labels(chosen: list[dict]) -> list[str]:
    """Direct end-labels: just the part that differs between the plotted series."""
    topics = {s.get("topic_id") for s in chosen}
    langs = {s.get("lang") for s in chosen}
    if len(topics) == 1:
        return [str(s.get("lang", "?")) for s in chosen]
    if len(langs) == 1:
        return [_clean(s.get("topic_label") or "?", 18) for s in chosen]
    return [_clean(series_label(s), 22) for s in chosen]


def render_trend(results: dict, path: Path, lang: str = "en", width_in: float = 8.0,
                 height_in: float = 4.2, font_pt: float = 9.0, source_line: bool = True) -> Path:
    """Monthly relative-interest index (share of the edition's views, first 12 months = 100)."""
    labels = load_labels(lang)["chart"]
    ok = [s for s in results.get("series") or [] if s.get("status") == "ok" and s.get("monthly")]
    indexed, not_indexed = [], []
    for s in ok:
        idx = _index(s["monthly"])
        (indexed if idx else not_indexed).append((s, idx))
    notes = []
    chosen = indexed
    if len(indexed) > MAX_LINES:
        top = sorted(indexed, key=lambda p: -((p[0].get("metrics") or {}).get("avg_daily_views_12m") or 0))
        keep = {id(p[0]) for p in top[:MAX_LINES]}
        chosen = [p for p in indexed if id(p[0]) in keep]  # original order -> stable colours
        notes.append(labels["top_n"].format(k=MAX_LINES, n=len(indexed)))
    if not_indexed:
        names = ", ".join(_clean(series_label(s), 24) for s, _ in not_indexed[:3])
        notes.append(labels["not_indexed"].format(labels=names))

    single = len(chosen) == 1
    with plt.rc_context(_style(font_pt)):
        if single:
            fig, (ax, ax_raw) = plt.subplots(2, 1, figsize=(width_in, height_in), sharex=True,
                                             gridspec_kw={"height_ratios": [2.3, 1]}, layout="constrained",
                                             dpi=DPI)
        else:
            fig, ax = plt.subplots(figsize=(width_in, height_in), layout="constrained", dpi=DPI)
            ax_raw = None
        _reserve_source_strip(fig, font_pt, height_in, source_line)
        subtitle = ([series_label(chosen[0][0])] if single else []) + notes
        fig.suptitle(_wrap(fig, _clean(labels["trend_title"]), font_pt + 0.5, bold=True), x=0.005,
                     ha="left", fontsize=font_pt + 0.5, fontweight="bold", color=INK)
        if subtitle:
            ax.set_title(_wrap(fig, _clean("; ".join(subtitle)), font_pt - 1, max_lines=1, frac=0.85),
                         loc="left", fontsize=font_pt - 1, fontweight="normal", color=INK_2, pad=font_pt * 0.5)

        if not chosen:
            _placeholder(ax, labels["no_data"])
        else:
            lw = max(1.1, font_pt / 6)
            handles = []
            ends = []
            for i, (s, idx) in enumerate(chosen):
                color = SERIES_COLORS[i % MAX_LINES]
                xs = [_month_date(m["month"]) for m in s["monthly"]]
                ax.plot(xs, idx, color=color, linewidth=lw, solid_joinstyle="round", solid_capstyle="round")
                spikes = [(x, y) for x, y, m in zip(xs, idx, s["monthly"])
                          if (m.get("views") or 0) > 0
                          and (m.get("spike_excess") or 0) / m["views"] >= SPIKE_MONTH_SHARE]
                if spikes:
                    ax.plot([p[0] for p in spikes], [p[1] for p in spikes], linestyle="none", marker="o",
                            markersize=font_pt / 2.2, markerfacecolor="white", markeredgecolor=color,
                            markeredgewidth=lw * 0.8)
                handles.append(Line2D([0], [0], color=color, linewidth=lw * 1.4,
                                      label=_clean(series_label(s), 34)))
                ends.append((xs[-1], idx[-1]))
            ax.axhline(100, color=AXIS, linewidth=0.8, zorder=0)
            _grid(ax, "y")
            ax.set_ylabel(labels["trend_y"])
            locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            ax.tick_params(axis="x", labelrotation=0)
            if any((m.get("spike_excess") or 0) for s, _ in chosen for m in s["monthly"]):
                handles.append(Line2D([0], [0], linestyle="none", marker="o", markerfacecolor="white",
                                      markeredgecolor=MUTED, markersize=font_pt / 2.2,
                                      label=labels["spike_month"]))

            if len(chosen) >= 2:
                ncol = min(4, _legend_cols([h.get_label() for h in handles], width_in, font_pt - 1))
                fig.legend(handles=handles, loc="outside lower center", ncol=ncol,
                           handlelength=1.6, columnspacing=1.2)
                ys = sorted(y for _, y in ends)
                span = (ax.get_ylim()[1] - ax.get_ylim()[0]) or 1.0
                separated = all(b - a >= 0.07 * span for a, b in zip(ys, ys[1:]))
                if len(chosen) <= 4 and separated:
                    for (x, y), text in zip(ends, _short_labels([p[0] for p in chosen])):
                        ax.annotate(text, (x, y), xytext=(4, 0), textcoords="offset points",
                                    va="center", ha="left", color=INK_2, fontsize=font_pt - 1)
                    ax.margins(x=0.06)
            elif len(handles) > 1:  # single line: the title names it; only explain spike markers
                ax.legend(handles=handles[1:], loc="upper left")

            if single and ax_raw is not None:
                s = chosen[0][0]
                xs = [_month_date(m["month"]) for m in s["monthly"]]
                ax_raw.bar(xs, [m.get("views") or 0 for m in s["monthly"]], width=20, color=RAW_BARS,
                           linewidth=0)
                ax_raw.set_ylabel(labels["raw_y"])
                ax_raw.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
                _grid(ax_raw, "y")
                ax_raw.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        if source_line:
            fig.text(0.005, 0.005, labels["source"], color=MUTED, fontsize=font_pt - 2, ha="left", va="bottom")
        path = Path(path)
        fig.savefig(path, dpi=DPI)
        plt.close(fig)
    return path


def _legend_cols(texts: list[str], width_in: float, font_pt: float) -> int:
    """Largest column count whose widest row still fits the figure width (estimated)."""
    for ncol in range(len(texts), 0, -1):
        widest = max(len(t) for t in texts)
        row_in = ncol * (widest * 0.56 * font_pt / 72 + 0.45)
        if row_in <= width_in * 0.96:
            return ncol
    return 1


def _reserve_source_strip(fig, font_pt: float, height_in: float, enabled: bool) -> None:
    """Keep a strip at the bottom free for the source line (constrained layout ignores fig.text)."""
    if enabled:
        frac = min(0.2, (font_pt * 1.7 / 72) / height_in)
        fig.get_layout_engine().set(rect=(0, frac, 1, 1 - frac))


def _ordered_rows(results: dict) -> list[dict]:
    series = list(results.get("series") or [])
    by_key = {s.get("key"): s for s in series}
    ranking = ((results.get("comparison") or {}).get("ranking")) or []
    ordered = [by_key[r["key"]] for r in ranking if r.get("key") in by_key]
    seen = {id(s) for s in ordered}
    ok_rest = [s for s in series if id(s) not in seen and s.get("status") == "ok"]
    other = [s for s in series if id(s) not in seen and s.get("status") != "ok"]
    return ordered + ok_rest + other


def render_growth(results: dict, path: Path, lang: str = "en", width_in: float = 8.0,
                  height_in: float | None = None, font_pt: float = 9.0, source_line: bool = True,
                  max_rows: int = MAX_BARS) -> Path:
    """Horizontal bars of relative YoY growth with 95% intervals, coloured by confidence."""
    all_labels = load_labels(lang)
    labels = all_labels["chart"]
    rows = _ordered_rows(results)
    max_rows = max(1, min(max_rows, MAX_BARS))
    hidden = max(0, len(rows) - max_rows)
    rows = rows[:max_rows]
    if height_in is None:
        height_in = min(7.5, max(2.2, 1.2 + 0.3 * len(rows)))

    with plt.rc_context(_style(font_pt)):
        fig, ax = plt.subplots(figsize=(width_in, height_in), layout="constrained", dpi=DPI)
        _reserve_source_strip(fig, font_pt, height_in, source_line)
        fig.suptitle(_wrap(fig, _clean(labels["growth_title"]), font_pt + 0.5, bold=True), x=0.005,
                     ha="left", fontsize=font_pt + 0.5, fontweight="bold", color=INK)
        values = []
        for s in rows:
            m = s.get("metrics") or {}
            v = m.get("yoy_rel")
            if s.get("status") == "ok" and v is not None and not math.isnan(v):
                ci = m.get("yoy_rel_ci") or [v, v]
                values.append((s, v * 100, ci[0] * 100, ci[1] * 100))
            else:
                values.append((s, None, None, None))
        if not rows or all(v is None for _, v, _, _ in values):
            _placeholder(ax, labels["no_data"])
        else:
            n = len(values)
            ys = list(range(n))[::-1]  # first ranked row on top
            finite = [x for _, v, lo, hi in values if v is not None for x in (v, lo, hi)]
            lo_lim, hi_lim = min(finite + [0.0]), max(finite + [0.0])
            span = (hi_lim - lo_lim) or 10.0
            pad = span * 0.08
            bar_h = min(0.55, 0.9 * 24 / (height_in * DPI / max(n, 1)))  # bars stay <= ~24 px thick
            used_levels = []
            for y, (s, v, lo, hi) in zip(ys, values):
                if v is None:
                    status = s.get("status")
                    text = labels["not_measurable"] if status in ("missing", "no_data") else labels["no_estimate"]
                    ax.text(0, y, "  " + text, va="center", ha="left", color=MUTED, fontsize=font_pt - 1,
                            style="italic")
                    continue
                conf = (s.get("verdict") or {}).get("confidence") or "n/a"
                color = CONFIDENCE_COLORS.get(conf, CONFIDENCE_COLORS["n/a"])
                if conf not in used_levels:
                    used_levels.append(conf)
                ax.barh(y, v, height=bar_h, color=color, linewidth=0, zorder=2)
                ax.plot([lo, hi], [y, y], color=INK_2, linewidth=0.9, zorder=3, solid_capstyle="butt")
                for x in (lo, hi):
                    ax.plot([x, x], [y - bar_h * 0.28, y + bar_h * 0.28], color=INK_2, linewidth=0.9, zorder=3)
                conf_text = all_labels["confidence"].get(conf, conf)
                text = f"{fmt_pct(v / 100)} · {conf_text}"
                if v >= 0:
                    ax.text(max(v, hi) + pad * 0.3, y, text, va="center", ha="left", color=INK,
                            fontsize=font_pt - 1)
                else:
                    ax.text(min(v, lo) - pad * 0.3, y, text, va="center", ha="right", color=INK,
                            fontsize=font_pt - 1)
            label_room = span * 0.45  # space for the value labels outside the whiskers
            ax.set_xlim(lo_lim - pad - (label_room if lo_lim < 0 else 0), hi_lim + pad + label_room)
            ax.set_ylim(-0.7, n - 0.3)
            ax.set_yticks(ys)
            ax.set_yticklabels([_clean(series_label(s), 26 if width_in >= 5 else 20) for s, *_ in values])
            ax.axvline(0, color=INK_2, linewidth=0.8, zorder=1)
            _grid(ax, "x")
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:+.0f}%" if x else "0%"))
            ax.set_xlabel(labels["growth_x"])
            ax.spines["left"].set_visible(False)
            order = [lvl for lvl in ("High", "Medium", "Low", "n/a") if lvl in used_levels]
            handles = [Patch(color=CONFIDENCE_COLORS[lvl],
                             label=labels["confidence_legend"].format(
                                 level=all_labels["confidence"].get(lvl, lvl)))
                       for lvl in order]
            subtitle = labels["growth_subtitle"]
            if hidden:
                subtitle += " · " + labels["more_bars"].format(n=hidden)
            if handles:
                fig.legend(handles=handles, loc="outside lower center",
                           ncol=_legend_cols([h.get_label() for h in handles], width_in, font_pt - 1),
                           handlelength=1.2, title=_wrap(fig, _clean(subtitle), font_pt - 1.5),
                           title_fontsize=font_pt - 1.5)
        if source_line:
            fig.text(0.005, 0.005, labels["source"], color=MUTED, fontsize=font_pt - 2, ha="left", va="bottom")
        path = Path(path)
        fig.savefig(path, dpi=DPI)
        plt.close(fig)
    return path


def render_charts(results: dict, out_dir: Path, lang: str = "en") -> dict:
    """Write trend.png and growth.png for an analysis; return their absolute paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if lang == "en" else f".{lang}"
    trend = render_trend(results, out_dir / f"trend{suffix}.png", lang=lang)
    growth = render_growth(results, out_dir / f"growth{suffix}.png", lang=lang)
    return {"trend_png": str(trend.resolve()), "growth_png": str(growth.resolve())}


def render_views_chart(periods: list[str], series: dict[str, list[float]], title: str, path) -> str:
    """Simple line chart for `views --chart` (custom periods, platforms, daily data)."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=150)
    for name, values in list(series.items())[:8]:
        ax.plot(range(len(periods)), values, label=sanitize(name)[0], linewidth=1.4)
    step = max(1, len(periods) // 10)
    ax.set_xticks(range(0, len(periods), step))
    ax.set_xticklabels([str(p)[:10] for p in periods[::step]], rotation=30, ha="right", fontsize=7)
    ax.set_title(sanitize(title)[0], fontsize=9)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, frameon=False)
    fig.text(0.01, 0.01, "Source: Wikimedia pageviews API", fontsize=6, color="#666")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return str(path)
