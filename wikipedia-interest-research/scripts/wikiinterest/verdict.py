"""Trust verdict: direction of change + High/Medium/Low confidence with reasons (docs/SPEC.md §8)."""

from __future__ import annotations

from . import i18n
from .numbers import fmt_ci, fmt_pct, fmt_views

# Changes smaller than 5% a year are not material for a product decision.
MIN_EFFECT = 0.05
# "Flat" is only claimed when the whole 95% range stays within +-15%; a small point estimate
# with a wide range means "we don't know", not "stable" (amendment 1 in docs/SPEC.md).
FLAT_MAX_RANGE = 0.15
# Below 10 views/day a single external link or bot burst can move monthly totals by >10%;
# 50 views/day is where monthly totals become stable enough for year-over-year comparison.
LOW_VOLUME, MODERATE_VOLUME = 10.0, 50.0
# Interval width (high - low) above which a growth estimate is too imprecise to act on.
WIDE_CI, VERY_WIDE_CI = 0.5, 1.0
# Growth "depends on spikes" when removing spike days moves it by more than 10 points
# or when spikes carry more than 30% of the views.
SPIKE_GAP, SPIKE_SHARE = 0.10, 0.30
# Variants whose growth differs from the base only by rounding are not disagreements.
REDIRECT_VARIANT_MIN_SHARE = 0.05

_LEVELS = ["Low", "Medium", "High"]


def direction(g: float | None, ci: list[float] | None) -> str:
    if g is None:
        return "n/a"
    if ci is None:
        return "growing" if g >= MIN_EFFECT else "declining" if g <= -MIN_EFFECT else "flat"
    lo, hi = ci
    if g >= MIN_EFFECT and lo > 0:
        return "growing"
    if g <= -MIN_EFFECT and hi < 0:
        return "declining"
    if abs(g) < MIN_EFFECT and lo > -FLAT_MAX_RANGE and hi < FLAT_MAX_RANGE:
        return "flat"
    return "uncertain"


def verdict(metrics: dict, variants: dict, yoy_prior_start: str) -> tuple[dict, list[dict]]:
    """Returns (verdict, variant rows). `variants` maps name -> (growth, ci).

    Reasons are recorded as codes with pre-formatted parameters (`reason_codes`) and rendered
    to English for the agent (`reasons`); the PDF renders the codes in the report language.
    """
    g, ci = metrics.get("yoy_rel"), metrics.get("yoy_rel_ci")
    base_dir = direction(g, ci)
    rows = []
    for name, (vg, vci) in variants.items():
        if name == "no_redirects" and metrics.get("redirect_share", 0) < REDIRECT_VARIANT_MIN_SHARE:
            continue  # without meaningful redirect traffic this variant equals the base
        if vg is None:
            continue
        rows.append({"name": name, "yoy_rel": vg, "yoy_rel_ci": vci, "direction": direction(vg, vci)})

    codes: list[dict] = []

    def add(code: str, **params) -> None:
        codes.append({"code": code, "params": params})

    if base_dir == "n/a":
        add("no_yoy")
        return _finish("n/a", "n/a", codes), rows

    level, caps = 2, []
    views = metrics.get("avg_daily_views_12m", 0.0)
    if views < LOW_VOLUME:
        caps.append(0)
        add("volume_low", views=fmt_views(views))
    elif views < MODERATE_VOLUME:
        caps.append(1)
        add("volume_moderate", views=fmt_views(views))
    start = metrics.get("data_start")
    if start and start > yoy_prior_start:
        caps.append(0)
        add("late_start", start=start)
    if ci:
        width = ci[1] - ci[0]
        if width > VERY_WIDE_CI:
            caps.append(0)
            add("ci_very_wide", ci=fmt_ci(ci))
        elif width > WIDE_CI:
            caps.append(1)
            add("ci_wide", ci=fmt_ci(ci))
    g_ex = metrics.get("yoy_rel_ex_spikes")
    spike_share = metrics.get("spike_share", 0.0)
    if (g_ex is not None and abs(g - g_ex) > SPIKE_GAP) or spike_share > SPIKE_SHARE:
        level -= 1
        add("spikes", g=fmt_pct(g), g_ex=fmt_pct(g_ex), share=fmt_pct(spike_share, signed=False))
    disagree = [r for r in rows if r["direction"] != base_dir]
    if len(disagree) == 1:
        level -= 1
    elif len(disagree) >= 2:
        caps.append(0)
    if disagree:
        add("variants_disagree", items=[{"name": r["name"], "direction": r["direction"],
                                         "value": fmt_pct(r["yoy_rel"])} for r in disagree])
    if base_dir == "uncertain":
        caps.append(0)
        add("uncertain_range", ci=fmt_ci(ci))
    level = max(0, min([level, *caps]))

    prior = metrics.get("prior_yoy_rel")
    if prior is not None and base_dir in ("growing", "declining") and direction(prior, None) not in (base_dir, "flat"):
        add("trend_reversed", prior=fmt_pct(prior))
    raw, proj = metrics.get("yoy_raw"), metrics.get("project_yoy")
    if raw is not None and proj is not None and (raw > 0) != (g > 0) and abs(raw - g) > MIN_EFFECT:
        add("platform_shift", raw=fmt_pct(raw), proj=fmt_pct(proj))
    if level == 2 and not disagree:
        codes.insert(0, {"code": "consistent", "params": {"views": fmt_views(views), "n": len(rows)}})
    return _finish(base_dir, _LEVELS[level], codes), rows


def _finish(direction_: str, confidence: str, codes: list[dict]) -> dict:
    return {"direction": direction_, "confidence": confidence,
            "reasons": [i18n.render(c["code"], c["params"], "en") for c in codes], "reason_codes": codes}
