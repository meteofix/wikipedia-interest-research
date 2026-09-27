"""Pure metric functions on daily series (numpy only, no I/O) — see docs/SPEC.md section 7."""

from __future__ import annotations

from datetime import date

import numpy as np

# Spike rule: a day is a spike when it exceeds 3x the 29-day centred median AND the median
# by at least 30 views. The ratio catches relative jumps; the absolute floor stops 1 -> 4
# views on tiny pages from counting as "spikes".
SPIKE_WINDOW = 29
SPIKE_RATIO = 3.0
SPIKE_MIN_EXCESS = 30
# Seasonality is reported when the monthly share profile's (max - min) / mean >= 0.3.
SEASONALITY_MIN_AMPLITUDE = 0.3
BOOTSTRAP_SAMPLES = 2000
BOOTSTRAP_SEED = 20260927  # fixed so the same data always gives the same interval


def month_list(first: str, last: str) -> list[str]:
    y, m = map(int, first.split("-"))
    y2, m2 = map(int, last.split("-"))
    out = []
    while (y, m) <= (y2, m2):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def month_bounds(first: str, last: str) -> tuple[date, date]:
    y, m = map(int, first.split("-"))
    y2, m2 = map(int, last.split("-"))
    nxt = date(y2 + 1, 1, 1) if m2 == 12 else date(y2, m2 + 1, 1)
    return date(y, m, 1), date.fromordinal(nxt.toordinal() - 1)


def monthly_sums(days: list[str], values: np.ndarray, months: list[str]) -> np.ndarray:
    idx = {m: i for i, m in enumerate(months)}
    out = np.zeros(len(months), dtype=float)
    for d, v in zip(days, values):
        i = idx.get(d[:7])
        if i is not None:
            out[i] += v
    return out


def rolling_median(x: np.ndarray, window: int = SPIKE_WINDOW) -> np.ndarray:
    half = window // 2
    n = len(x)
    out = np.empty(n, dtype=float)
    for i in range(n):
        out[i] = np.median(x[max(0, i - half) : min(n, i + half + 1)])
    return out


def detect_spikes(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Boolean spike mask and the rolling-median baseline."""
    base = rolling_median(x)
    mask = (x > SPIKE_RATIO * base) & (x - base >= SPIKE_MIN_EXCESS)
    return mask, base


def growth(recent: np.ndarray, prior: np.ndarray, recent_den: np.ndarray | None = None,
           prior_den: np.ndarray | None = None) -> float | None:
    """(sum recent / sum prior) - 1, optionally of shares (numerator / denominator)."""
    if recent_den is not None:
        if prior_den.sum() <= 0 or recent_den.sum() <= 0 or prior.sum() <= 0:
            return None
        return float((recent.sum() / recent_den.sum()) / (prior.sum() / prior_den.sum()) - 1)
    if prior.sum() <= 0:
        return None
    return float(recent.sum() / prior.sum() - 1)


def growth_ci(recent: np.ndarray, prior: np.ndarray, recent_den: np.ndarray | None = None,
              prior_den: np.ndarray | None = None) -> list[float] | None:
    """95% interval by paired bootstrap over calendar months.

    Month i of the recent year is always paired with month i of the prior year, so the
    seasonal pattern cancels and the interval reflects how consistent growth is across months.
    """
    if growth(recent, prior, recent_den, prior_den) is None:
        return None
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    idx = rng.integers(0, len(recent), size=(BOOTSTRAP_SAMPLES, len(recent)))
    r, p = recent[idx].sum(axis=1), prior[idx].sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        if recent_den is not None:
            rd, pd = recent_den[idx].sum(axis=1), prior_den[idx].sum(axis=1)
            g = (r / rd) / (p / pd) - 1
        else:
            g = r / p - 1
    g = g[np.isfinite(g)]
    if len(g) < BOOTSTRAP_SAMPLES * 0.9:  # too many resamples with an all-zero prior year
        return None
    return [float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))]


def seasonal_profile(share: np.ndarray, months: list[str]) -> list[int] | None:
    """Average share per calendar month (Jan..Dec) as an index, 100 = average month."""
    if len(months) < 24:
        return None
    prof, cnt = np.zeros(12), np.zeros(12)
    for s_, m in zip(share, months):
        prof[int(m[5:7]) - 1] += s_
        cnt[int(m[5:7]) - 1] += 1
    if (cnt == 0).any() or prof.sum() <= 0:
        return None
    prof /= cnt
    return [int(round(x)) for x in prof / prof.mean() * 100]


def seasonality(share: np.ndarray, months: list[str]) -> tuple[int | None, float | None]:
    """Peak calendar month (1..12) and amplitude of the average monthly share profile."""
    if len(months) < 24:
        return None, None
    prof = np.zeros(12)
    cnt = np.zeros(12)
    for s, m in zip(share, months):
        k = int(m[5:7]) - 1
        prof[k] += s
        cnt[k] += 1
    if (cnt == 0).any():
        return None, None
    prof /= cnt
    mean = prof.mean()
    if mean <= 0:
        return None, None
    amp = float((prof.max() - prof.min()) / mean)
    peak = int(prof.argmax()) + 1
    # A one-off event (a championship, a news story) can dominate the average profile. Call it
    # seasonal only if each of at least two separate years peaks within a month of the same month.
    years = [share[len(share) - 12 * (k + 1): len(share) - 12 * k] for k in range(len(share) // 12)]
    year_months = [months[len(months) - 12 * (k + 1): len(months) - 12 * k] for k in range(len(months) // 12)]
    recurring = 0
    for ys, ym in zip(years, year_months):
        if ys.max() <= 0:
            continue
        pm = int(ym[int(ys.argmax())][5:7])
        if min((pm - peak) % 12, (peak - pm) % 12) <= 1:
            recurring += 1
    seasonal = amp >= SEASONALITY_MIN_AMPLITUDE and recurring >= 2
    return (peak if seasonal else None), amp


def cagr(views: np.ndarray, den: np.ndarray, n_months: int) -> float | None:
    """Average yearly change of the share between the first and the last 12 months."""
    if n_months < 36:
        return None
    first = views[:12].sum() / max(den[:12].sum(), 1)
    last = views[-12:].sum() / max(den[-12:].sum(), 1)
    if first <= 0:
        return None
    years = (n_months - 12) / 12
    return float((last / first) ** (1 / years) - 1)


def window_growth(views_m: np.ndarray, den_m: np.ndarray, offset: int = 0) -> tuple[float | None, list[float] | None]:
    """Relative YoY for the 24 months ending `offset` months before the last month."""
    n = len(views_m)
    end = n - offset
    if end - 24 < 0:
        return None, None
    r, p = views_m[end - 12 : end], views_m[end - 24 : end - 12]
    rd, pd = den_m[end - 12 : end], den_m[end - 24 : end - 12]
    return growth(r, p, rd, pd), growth_ci(r, p, rd, pd)


def series_metrics(days: list[str], topic: np.ndarray, main: np.ndarray, total: np.ndarray,
                   months: list[str], exclude_months: set[int] | None = None) -> dict:
    """All metrics for one topic x language series. Arrays are daily and aligned with `days`.

    `exclude_months` (calendar months 1..12) are left out of growth and level metrics in every
    year, e.g. to remove a January effect; seasonality and the monthly table still show them.
    """
    n = len(months)
    excl = set(exclude_months or ())
    spikes, base = detect_spikes(topic)
    excess = np.where(spikes, topic - base, 0.0)
    topic_ex = np.where(spikes, base, topic)

    v_m = monthly_sums(days, topic, months)
    main_m = monthly_sums(days, main, months)
    tot_m = monthly_sums(days, total, months)
    ex_m = monthly_sums(days, topic_ex, months)
    exc_m = monthly_sums(days, excess, months)
    with np.errstate(divide="ignore", invalid="ignore"):
        share_m = np.where(tot_m > 0, v_m / tot_m * 1e6, 0.0)
        share_ex_m = np.where(tot_m > 0, ex_m / tot_m * 1e6, 0.0)

    keep = np.array([int(m[5:7]) not in excl for m in months], dtype=float)
    v_k, tot_k, ex_k, main_k = v_m * keep, tot_m * keep, ex_m * keep, main_m * keep
    recent = set(months[-12:])
    recent_days = sum(1 for d in days if d[:7] in recent and int(d[5:7]) not in excl)
    yoy_rel, yoy_rel_ci = window_growth(v_k, tot_k)
    yoy_raw, yoy_raw_ci = window_growth(v_k, keep)
    project_yoy = growth(tot_k[-12:], tot_k[-24:-12]) if n >= 24 else None
    prior_yoy_rel, _ = window_growth(v_k, tot_k, offset=12) if n >= 36 else (None, None)
    yoy_ex, yoy_ex_ci = window_growth(ex_k, tot_k)
    yoy_shift, yoy_shift_ci = window_growth(v_k, tot_k, offset=6) if n >= 30 else (None, None)
    yoy_main, yoy_main_ci = window_growth(main_k, tot_k)

    window24 = set(months[-24:])
    in24 = np.array([d[:7] in window24 for d in days])
    spike_share = float(excess[in24].sum() / topic[in24].sum()) if topic[in24].sum() > 0 else 0.0
    order = np.argsort(-excess)
    top_spikes = [{"day": days[i], "views": int(topic[i]), "baseline": round(float(base[i]), 1)}
                  for i in order[:3] if excess[i] > 0]
    peak, amp = seasonality(share_ex_m, months)
    nz = np.nonzero(topic > 0)[0]
    total_views = topic.sum()

    metrics = {
        "avg_daily_views_12m": float(v_k[-12:].sum() / max(recent_days, 1)),
        "share_ppm_12m": float(v_k[-12:].sum() / tot_k[-12:].sum() * 1e6) if tot_k[-12:].sum() > 0 else 0.0,
        "cagr_rel": cagr(v_k, tot_k, n),
        "yoy_rel": yoy_rel, "yoy_rel_ci": yoy_rel_ci,
        "yoy_raw": yoy_raw, "yoy_raw_ci": yoy_raw_ci,
        "project_yoy": project_yoy,
        "prior_yoy_rel": prior_yoy_rel,
        "yoy_rel_ex_spikes": yoy_ex,
        "yoy_rel_ex_spikes_ci": yoy_ex_ci,
        "spike_share": spike_share,
        "top_spikes": top_spikes,
        "peak_month": peak,
        "seasonality_amplitude": amp,
        "seasonal_profile": seasonal_profile(share_ex_m, months),
        "redirect_share": float((total_views - main.sum()) / total_views) if total_views > 0 else 0.0,
        "data_start": days[nz[0]] if len(nz) else None,
    }
    variants = {
        "ex_spikes": (yoy_ex, yoy_ex_ci),
        "shifted_6m": (yoy_shift, yoy_shift_ci),
        "no_redirects": (yoy_main, yoy_main_ci),
    }
    monthly = [
        {"month": m, "views": int(v_m[i]), "views_main": int(main_m[i]), "project_views": int(tot_m[i]),
         "share_ppm": round(float(share_m[i]), 4), "spike_excess": int(exc_m[i])}
        for i, m in enumerate(months)
    ]
    return {"metrics": metrics, "variants": variants, "monthly": monthly}
