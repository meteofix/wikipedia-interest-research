"""Contract for `results.json`, the file every analysis writes.

Charts, the PDF report and the eval graders read only this structure, so it is the
single interface between the data/analytics layer and everything downstream.
Ratios (growth, shares of spikes/redirects) are fractions: 0.12 means +12%.
"""

from __future__ import annotations

from typing import TypedDict

SCHEMA_ID = "wiki-interest/analysis@1"

DIRECTIONS = ("growing", "declining", "flat", "uncertain", "n/a")
CONFIDENCE_LEVELS = ("High", "Medium", "Low", "n/a")


class Article(TypedDict):
    title: str  # canonical title with spaces
    source: str  # "Q718" when it came from a Wikidata sitelink, "explicit" when given as lang:Title
    redirects_included: int
    redirects_total: int
    data_start: str | None  # first day with views (YYYY-MM-DD), None if no views at all


class MonthPoint(TypedDict):
    month: str  # "2025-09"
    views: int  # topic views incl. redirects
    views_main: int  # views of the articles themselves (no redirects)
    project_views: int  # all user views of the language edition
    share_ppm: float  # views / project_views * 1e6
    spike_excess: int  # views above the rolling median on spike days


class Spike(TypedDict):
    day: str
    views: int
    baseline: float


class Metrics(TypedDict, total=False):
    avg_daily_views_12m: float
    share_ppm_12m: float
    yoy_rel: float | None  # growth of the share of the edition's views, last 12m vs prior 12m
    yoy_rel_ci: list[float] | None  # 95% interval [low, high]
    yoy_raw: float | None  # growth of absolute views
    yoy_raw_ci: list[float] | None
    project_yoy: float | None  # growth of all views of the edition
    prior_yoy_rel: float | None  # the same relative growth one year earlier
    cagr_rel: float | None  # average yearly change of the share over the whole window
    yoy_rel_ex_spikes: float | None
    spike_share: float  # share of views in the YoY window that are spike excess
    top_spikes: list[Spike]
    peak_month: int | None  # 1..12, set only when seasonality is pronounced
    seasonality_amplitude: float | None
    redirect_share: float
    data_start: str | None


class Variant(TypedDict):
    name: str  # "ex_spikes" | "shifted_6m" | "no_redirects"
    yoy_rel: float | None
    yoy_rel_ci: list[float] | None
    direction: str


class Verdict(TypedDict):
    direction: str  # one of DIRECTIONS
    confidence: str  # one of CONFIDENCE_LEVELS
    reasons: list[str]  # plain-English reasons for the confidence level


class Series(TypedDict):
    key: str  # "<topic_id>|<lang>", e.g. "t1|pl"
    topic_id: str
    topic_label: str
    lang: str  # wiki subdomain code, e.g. "pl", "zh-yue"
    project: str  # "pl.wikipedia.org"
    status: str  # "ok" | "missing" (no article in this edition) | "no_data"
    note: str | None
    articles: list[Article]
    monthly: list[MonthPoint]
    metrics: Metrics
    variants: list[Variant]
    verdict: Verdict
    criteria: dict | None  # {"min_views": {"threshold": 100, "pass": true}, "min_growth": {...}}


class RankEntry(TypedDict):
    key: str
    label: str  # "chess · tr"
    value: float | None


class Comparison(TypedDict):
    rank_by: str  # "growth" | "share" | "views"
    ranking: list[RankEntry]
    leader_stable: str | None  # e.g. "3/3 variants"
    leader_ci_overlap: bool | None  # True when the leader's and runner-up's intervals overlap
    notes: list[str]


class Results(TypedDict):
    schema: str  # SCHEMA_ID
    created_at: str  # ISO timestamp, UTC
    tool_version: str
    params: dict  # topics, langs, start, end, months, recent, prior, agent, access, redirects, rank_by, min_views, min_growth, command
    series: list[Series]
    comparison: Comparison | None
    caveats: list[str]  # always-on limitations (interest != willingness to pay, language != country, ...)
    warnings: list[str]  # data-specific problems (missing articles, new articles, ...)
    files: dict  # dir, results, summary, csv, trend_png, growth_png, report_pdf (after report)
