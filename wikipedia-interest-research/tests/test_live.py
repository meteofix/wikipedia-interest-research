"""Live checks against the Wikimedia API (acceptance criterion B3). Run with WIKI_LIVE=1.

Our monthly numbers are sums of zero-filled daily series; the API also publishes its own
monthly totals. They are computed independently by Wikimedia, so exact equality verifies
the fetching, zero-filling, date handling and title encoding end to end.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.skipif(os.environ.get("WIKI_LIVE") != "1", reason="set WIKI_LIVE=1 to run live API checks")

# Different scripts, sizes, special characters (":" "+", apostrophes) and a low-traffic page.
CASES = [
    ("en", "5:2 diet"),
    ("cs", "Přerušovaný půst"),
    ("uk", "Шахи"),
    ("zh-yue", "國際象棋"),
    ("en", "C++"),
    ("fr", "Jeanne d'Arc"),
]


@pytest.fixture(scope="module")
def ctx():
    from wikiinterest.analysis import _context
    from wikiinterest.cache import Cache

    tmp = Path(tempfile.mkdtemp()) / "cache.sqlite"
    return _context(Cache(tmp))


@pytest.mark.parametrize("lang,title", CASES)
def test_monthly_sums_match_api(ctx, lang, title):
    from wikiinterest import metrics as M, pageviews as PV

    cache, http, index = ctx
    site = index.resolve(lang)
    months = M.month_list("2024-01", "2025-12")
    first, last = M.month_bounds(months[0], months[-1])
    daily = PV.daily(http, cache, site, title, first, last)
    days = sorted(daily)
    ours = M.monthly_sums(days, np.array([daily[d] for d in days], dtype=float), months)
    api = PV.monthly_api(http, site, title, months[0], months[-1])
    assert api, f"API returned no monthly data for {lang}:{title}"
    for i, m in enumerate(months):
        assert int(ours[i]) == api.get(m, 0), f"{lang}:{title} {m}: ours {int(ours[i])} vs API {api.get(m, 0)}"
