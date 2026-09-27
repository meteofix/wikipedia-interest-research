"""Offline tests for the data/analytics core (acceptance criteria B1, B2, B4, B6)."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pytest

from wikiinterest import metrics as M
from wikiinterest.analysis import parse_topic, month_add
from wikiinterest.cache import merge_intervals, missing_ranges
from wikiinterest.numbers import fmt_pct, ungrounded_numbers
from wikiinterest.sites import SiteIndex, Site, UnknownLanguage
from wikiinterest.verdict import direction, verdict

FIX = Path(__file__).parent / "fixtures"


# ---------- helpers: synthetic daily series with known growth -------------------------------------

def synth(growth: float, months: int = 36, level: float = 400.0, seasonal: float = 0.3, noise: float = 0.15,
          spikes: list[tuple[int, float]] = (), seed: int = 1, end: str = "2026-08"):
    """Daily topic views whose relative YoY (last 12 vs previous 12 months) equals `growth` in expectation.

    The edition total declines 10%/year so relative and absolute growth differ, like real data.
    """
    rng = np.random.default_rng(seed)
    ms = M.month_list(month_add(end, -(months - 1)), end)
    first, last = M.month_bounds(ms[0], ms[-1])
    days = [(first + timedelta(days=i)).isoformat() for i in range((last - first).days + 1)]
    n = len(days)
    t_years = np.array([(date.fromisoformat(d) - date.fromisoformat(days[-1])).days / 365.25 for d in days])
    month_idx = np.array([int(d[5:7]) for d in days])
    season = 1 + seasonal * np.cos(2 * np.pi * (month_idx - 1) / 12)
    total = 5e6 * (0.9 ** t_years) * (1 + 0.02 * rng.standard_normal(n))
    share = 1e-4 * ((1 + growth) ** t_years) * season
    topic = total * share / 1e-4 * (level / 5e6) * np.exp(noise * rng.standard_normal(n))
    topic = np.round(topic)
    for day_idx, mult in spikes:
        topic[day_idx] = topic[day_idx] * mult + 500
    return days, topic, total, ms


# ---------- B2: synthetic accuracy ----------------------------------------------------------------

@pytest.mark.parametrize("g", [-0.4, -0.2, -0.05, 0.0, 0.1, 0.25, 0.6])
def test_growth_estimate_accuracy(g):
    errs = []
    covered = 0
    for seed in range(12):
        days, topic, total, ms = synth(g, seed=seed)
        res = M.series_metrics(days, topic, topic, total, ms)["metrics"]
        errs.append(abs(res["yoy_rel"] - g))
        lo, hi = res["yoy_rel_ci"]
        covered += lo <= g <= hi
    assert np.median(errs) <= 0.03, f"median error {np.median(errs):.3f} for growth {g}"
    assert covered / 12 >= 0.8, f"CI coverage {covered}/12 for growth {g}"


def test_spike_detected_and_removed():
    days, topic, total, ms = synth(0.1, seed=3)
    spike_day = len(days) - 40  # inside the last 12 months
    topic = topic.copy()
    topic[spike_day] = topic[spike_day] * 40 + 2000
    res = M.series_metrics(days, topic, topic, total, ms)["metrics"]
    assert res["top_spikes"][0]["day"] == days[spike_day]
    assert abs(res["yoy_rel_ex_spikes"] - 0.1) <= 0.05
    assert res["yoy_rel"] > res["yoy_rel_ex_spikes"]


def test_seasonality_peak_found_for_recurring_pattern_only():
    days, topic, total, ms = synth(0.0, seasonal=0.6, noise=0.05)
    res = M.series_metrics(days, topic, topic, total, ms)["metrics"]
    assert res["peak_month"] == 1  # cos peak at January
    # one-off elevated month in a flat series must not be called seasonal
    days, topic, total, ms = synth(0.0, seasonal=0.0, noise=0.05, seed=4)
    topic = topic.copy()
    idx = [i for i, d in enumerate(days) if d.startswith(ms[5])]
    topic[idx] *= 3
    res = M.series_metrics(days, topic, topic, total, ms)["metrics"]
    assert res["peak_month"] is None


def test_zero_prior_year_gives_no_growth():
    days, topic, total, ms = synth(0.1)
    topic = topic.copy()
    cut = next(i for i, d in enumerate(days) if d.startswith(ms[-12]))
    topic[:cut] = 0
    res = M.series_metrics(days, topic, topic, total, ms)["metrics"]
    assert res["yoy_rel"] is None
    v, _ = verdict(res, {}, f"{ms[-24]}-01")
    assert v["direction"] == "n/a"


# ---------- B6: metamorphic invariants --------------------------------------------------------------

def test_scaling_topic_does_not_change_relative_metrics():
    days, topic, total, ms = synth(0.2, seed=7)
    a = M.series_metrics(days, topic, topic, total, ms)["metrics"]
    b = M.series_metrics(days, topic * 3, topic * 3, total, ms)["metrics"]
    assert a["yoy_rel"] == pytest.approx(b["yoy_rel"])
    c = M.series_metrics(days, topic, topic, total * 5, ms)["metrics"]
    assert a["yoy_rel"] == pytest.approx(c["yoy_rel"])


def test_bootstrap_is_deterministic():
    days, topic, total, ms = synth(0.2, seed=8)
    a = M.series_metrics(days, topic, topic, total, ms)["metrics"]
    b = M.series_metrics(days, topic, topic, total, ms)["metrics"]
    assert a["yoy_rel_ci"] == b["yoy_rel_ci"]


# ---------- verdict rules ------------------------------------------------------------------------------

def test_direction_rules():
    assert direction(0.2, [0.05, 0.35]) == "growing"
    assert direction(-0.2, [-0.3, -0.1]) == "declining"
    assert direction(0.02, [-0.05, 0.08]) == "flat"
    assert direction(0.035, [-0.14, 0.30]) == "uncertain"  # amendment 1: wide range is not "flat"
    assert direction(0.2, [-0.05, 0.4]) == "uncertain"
    assert direction(None, None) == "n/a"


def _metrics(**kw):
    base = {"yoy_rel": 0.2, "yoy_rel_ci": [0.1, 0.3], "avg_daily_views_12m": 500.0, "yoy_rel_ex_spikes": 0.19,
            "spike_share": 0.01, "redirect_share": 0.0, "data_start": "2023-09-01", "yoy_raw": 0.1,
            "project_yoy": -0.08, "prior_yoy_rel": 0.15}
    base.update(kw)
    return base


def test_confidence_high_when_all_checks_pass():
    v, _ = verdict(_metrics(), {"ex_spikes": (0.19, [0.09, 0.29]), "shifted_6m": (0.18, [0.06, 0.3])}, "2024-09-01")
    assert (v["direction"], v["confidence"]) == ("growing", "High")


@pytest.mark.parametrize("kw,expected", [
    ({"avg_daily_views_12m": 5.0}, "Low"),
    ({"avg_daily_views_12m": 30.0}, "Medium"),
    ({"data_start": "2025-10-01"}, "Low"),
    ({"yoy_rel_ex_spikes": 0.02}, "Medium"),
    ({"yoy_rel_ci": [0.01, 0.7]}, "Medium"),
])
def test_confidence_downgrades(kw, expected):
    v, _ = verdict(_metrics(**kw), {}, "2024-09-01")
    assert v["confidence"] == expected
    assert v["reasons"]


def test_variant_disagreement_downgrades():
    one = {"ex_spikes": (0.19, [0.09, 0.29]), "shifted_6m": (0.01, [-0.2, 0.2])}
    v, _ = verdict(_metrics(), one, "2024-09-01")
    assert v["confidence"] == "Medium"
    two = {"ex_spikes": (0.0, [-0.2, 0.2]), "shifted_6m": (0.01, [-0.2, 0.2])}
    v, _ = verdict(_metrics(), two, "2024-09-01")
    assert v["confidence"] == "Low"


# ---------- cache intervals -------------------------------------------------------------------------------

def test_missing_ranges():
    d = date.fromisoformat
    cov = [(d("2024-01-01"), d("2024-06-30")), (d("2024-08-01"), d("2024-12-31"))]
    assert missing_ranges(d("2024-01-01"), d("2024-12-31"), cov) == [(d("2024-07-01"), d("2024-07-31"))]
    assert missing_ranges(d("2023-12-01"), d("2025-01-31"), cov) == [
        (d("2023-12-01"), d("2023-12-31")), (d("2024-07-01"), d("2024-07-31")), (d("2025-01-01"), d("2025-01-31"))]
    assert missing_ranges(d("2024-02-01"), d("2024-03-01"), cov) == []
    assert merge_intervals([(d("2024-01-01"), d("2024-01-31")), (d("2024-02-01"), d("2024-02-10"))]) == [
        (d("2024-01-01"), d("2024-02-10"))]


# ---------- B4: language editions --------------------------------------------------------------------------

class _FakeHttp:
    def get_json(self, url, params=None, ttl=None):
        return json.loads((FIX / "sitematrix.json").read_text())


@pytest.fixture(scope="module")
def index():
    from wikiinterest.sites import load_sites

    return SiteIndex(load_sites(_FakeHttp()))


def test_all_open_wikipedias_resolve_by_code(index):
    assert len(index.sites) >= 340
    for s in index.sites:
        assert index.resolve(s.code) == s
        assert index.resolve(s.dbname) == s


@pytest.mark.parametrize("token,code,dbname", [
    ("yue", "zh-yue", "zh_yuewiki"), ("Cantonese", "zh-yue", "zh_yuewiki"), ("gsw", "als", "alswiki"),
    ("be-tarask", "be-tarask", "be_x_oldwiki"), ("nan", "zh-min-nan", "zh_min_nanwiki"),
    ("lzh", "zh-classical", "zh_classicalwiki"), ("Polish", "pl", "plwiki"), ("polski", "pl", "plwiki"),
    ("nb", "no", "nowiki"), ("pt-BR", "pt", "ptwiki"), ("simple", "simple", "simplewiki"), ("UK", "uk", "ukwiki"),
])
def test_special_codes_and_names(index, token, code, dbname):
    s = index.resolve(token)
    assert (s.code, s.dbname) == (code, dbname)


def test_unknown_language_message(index):
    with pytest.raises(UnknownLanguage) as e:
        index.resolve("Brazil")
    assert "country is not a language" in str(e.value)


def test_order_of_languages_is_preserved_and_deduplicated(index):
    got = [s.code for s in index.resolve_many(["cs", "pl", "Polish", "cs"])]
    assert got == ["cs", "pl"]


# ---------- topic syntax ------------------------------------------------------------------------------------

def test_parse_topic_syntax(index):
    t, free = parse_topic("Chess=Q718+uk:Шахова задача", 1, index)
    assert t.label == "Chess" and t.qids == ["Q718"] and [x[1] for x in t.titles] == ["Шахова задача"] and not free
    t, free = parse_topic("en:C++", 2, index)
    assert [x[1] for x in t.titles] == ["C++"] and not free
    t, free = parse_topic("Q1+Q2", 3, index)
    assert t.qids == ["Q1", "Q2"]
    t, free = parse_topic("en:E=mc2", 4, index)
    assert t.label is None and [x[1] for x in t.titles] == ["E=mc2"]
    t, free = parse_topic("intermittent fasting", 5, index)
    assert free == ["intermittent fasting"]


# ---------- numbers ---------------------------------------------------------------------------------------------

def test_number_grounding():
    res = {"g": 0.1234, "ci": [0.03, 0.225], "v": 1234.4}
    assert ungrounded_numbers("росте на +12% [3%, 22,5%], 1 234 переглядів у 2025", [res]) == []
    assert ungrounded_numbers("росте на 57%", [res]) == ["57%"]
    assert fmt_pct(-0.045) == "-4.5%" and fmt_pct(0.1234) == "+12%"


# ---------- topic disambiguation ---------------------------------------------------------------------------

def _c(qid, label, desc, n):
    return {"qid": qid, "label": label, "description": desc, "wikipedias": n}


def test_pick_best_prefers_widely_covered_exact_label_and_flags_rivals():
    from wikiinterest.resolve import pick_best

    # search order puts the car maker first; the animal is the main meaning of "jaguar"
    cands = [_c("Q30055", "Jaguar Cars", "British car company", 68), _c("Q2732887", "Jaguar", "torpedo boat", 5),
             _c("Q35694", "jaguar", "species of big cat", 128)]
    best, rivals = pick_best("jaguar", cands)
    assert best["qid"] == "Q35694" and [r["qid"] for r in rivals] == ["Q30055"]
    # a second meaning outside the first three search hits still makes the query ambiguous
    cands = [_c("Q308", "Mercury", "planet", 250), _c("Q613883", "Mercury", "car marque", 27),
             _c("Q1231263", "Mercury", "commune in France", 35), _c("Q165745", "Mercury Records", "label", 40),
             _c("Q925", "mercury", "chemical element", 176)]
    best, rivals = pick_best("mercury", cands)
    assert best["qid"] == "Q308" and "Q925" in [r["qid"] for r in rivals]
    # an unambiguous topic stays unambiguous
    cands = [_c("Q718", "chess", "board game", 202), _c("Q843284", "Chess", "musical", 19)]
    best, rivals = pick_best("chess", cands)
    assert best["qid"] == "Q718" and rivals == []


def test_weighted_scores_use_percentile_ranks():
    from wikiinterest.analysis import weighted_scores

    def s(key, g, share, conf):
        return {"key": key, "topic_label": "t", "lang": key, "status": "ok",
                "metrics": {"yoy_rel": g, "share_ppm_12m": share, "avg_daily_views_12m": share},
                "verdict": {"confidence": conf}}
    series = [s("a", 0.3, 10, "High"), s("b", 0.1, 50, "Medium"), s("c", -0.2, 30, "Low")]
    w = weighted_scores(series, {"growth": 2, "share": 1})
    assert [r["key"] for r in w["ranking"]] == ["a", "b", "c"]
    assert w["ranking"][0]["score"] == round((2 * 1 + 1 * 0) / 3, 2)
    w = weighted_scores(series, {"share": 1})
    assert w["ranking"][0]["key"] == "b"


def test_large_clear_growth_is_not_penalised_for_width_or_small_spike_share():
    # amendment 3: [+105%, +220%] is wide but unambiguous; +153% vs +136% without spikes is not spike-driven
    m = _metrics(yoy_rel=1.53, yoy_rel_ci=[1.05, 2.20], yoy_rel_ex_spikes=1.36, yoy_rel_ex_spikes_ci=[0.9, 2.0],
                 spike_share=0.046)
    v, _ = verdict(m, {}, "2024-09-01")
    assert (v["direction"], v["confidence"]) == ("growing", "High")
    # the same width close to zero still lowers confidence
    m = _metrics(yoy_rel=0.35, yoy_rel_ci=[0.02, 0.80], yoy_rel_ex_spikes=0.33)
    v, _ = verdict(m, {}, "2024-09-01")
    assert v["confidence"] == "Medium"


def test_excluding_a_month_removes_its_effect_from_growth():
    days, topic, total, ms = synth(0.1, seasonal=0.0, noise=0.05, seed=11)
    topic = topic.copy()
    jan_recent = [i for i, d in enumerate(days) if d[:7] == ms[-12:][[m[5:] for m in ms[-12:]].index("01")]]
    topic[jan_recent] *= 4  # a one-off January boom in the latest year
    with_jan = M.series_metrics(days, topic, topic, total, ms)["metrics"]["yoy_rel"]
    without_jan = M.series_metrics(days, topic, topic, total, ms, {1})["metrics"]["yoy_rel"]
    assert with_jan > 0.3 and abs(without_jan - 0.1) < 0.05


def test_missing_bootstrap_range_does_not_crash_and_lowers_confidence():
    v, _ = verdict(_metrics(yoy_rel=12.79, yoy_rel_ci=None), {}, "2024-09-01")
    assert v["direction"] == "growing" and v["confidence"] == "Low"
    assert any(c["code"] == "no_range" for c in v["reason_codes"])
