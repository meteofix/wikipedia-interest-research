# Methodology

Read this when the user asks how numbers, confidence or rankings are produced.

## Contents
- Data and filters
- Metrics
- Direction and confidence
- Robustness checks
- Comparisons and user criteria
- What the numbers do not say

## Data and filters

- Source: Wikimedia Analytics pageviews API (daily per-article views, daily totals per language
  edition). Wikidata links the same topic across languages.
- Default filters: human traffic (`user` agent), all platforms, 36 full months ending with the last
  complete month. Days with no views are counted as 0 (the API omits them).
- A topic = one or more Wikidata items (their article in each edition) and/or explicit articles,
  plus the redirects pointing to those articles (old titles after renames, spelling variants).
  At most 30 redirects per article are used, ranked by recent views.

## Metrics

| Metric | Definition |
|---|---|
| Views/day (12m) | average daily views over the last 12 full months |
| Share per M | topic views per million views of the whole edition over the last 12 months; comparable across languages of different size |
| Relative growth | (share in the last 12 months) / (share in the previous 12 months) − 1; the main growth metric because it removes platform-wide shifts (e.g. traffic moving to search and AI answers) |
| 95% range | paired bootstrap over calendar months (month i of this year vs month i of last year, 2000 resamples): narrow when growth is consistent across months, wide when it comes from a few months |
| Absolute growth | the same for raw views; edition growth = the same for all views of the edition |
| Year before | relative growth one year earlier (trend consistency) |
| Average yearly change | compound yearly change of the share between the first and the last 12 months (windows of 36+ months) |
| Spikes | days above 3× the 29-day median and at least 30 views above it; growth is also computed with spike days replaced by the median |
| Seasonal peak | calendar month with the highest average share, reported only if the profile varies by ≥ 30% and at least two separate years peak within a month of it |

## Direction and confidence

Direction from relative growth and its 95% range:
- growing: growth ≥ +5% and the whole range above 0
- declining: growth ≤ −5% and the whole range below 0
- flat: |growth| < 5% and the range within ±15%
- uncertain: anything else (the data cannot tell the direction)

Confidence starts at High and is lowered by:
- volume below 10 views/day → Low; 10–50 views/day → at most Medium (few views = noisy months)
- views starting after the comparison period begins (new/renamed article) → Low
- range wider than 50 points → at most Medium; wider than 100 points → Low
- growth that depends on spikes (changes by > 10 points without spike days, or spikes carry > 30%
  of views) → one level down
- robustness checks that change the direction: one → one level down, two or more → Low
- uncertain direction → Low

Thresholds are judgment calls documented in the code; they were checked on synthetic series with
known growth (median error ≤ 3 points, range covers the truth in ≥ 80% of cases).

## Robustness checks

The same growth is recomputed (1) without spike days, (2) with the window shifted 6 months
earlier, (3) without redirects (only when redirects carry ≥ 5% of views). A conclusion that holds
in all checks is robust; one that flips is reported with the reason.

## Comparisons and user criteria

- Ranking uses `--rank-by`: relative growth (default), share, or views/day.
- For growth rankings: how many robustness checks keep the same leader, and whether the
  leader's and runner-up's ranges overlap (overlap = the difference is not certain).
- `--min-views` / `--min-growth` mark each series pass/fail against the user's thresholds.

## What the numbers do not say

- Interest is not purchase intent or willingness to pay.
- A language edition is not a country; many people read English Wikipedia instead.
- Articles are proxies for a topic; a missing article means "not measurable", not "no interest".
- Causes of spikes are not identified (only their dates and size).
