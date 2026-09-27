# Data notes, API limits and errors

Read this when a command fails, when data looks odd, or when the user asks about data quality.

## Contents
- Coverage and freshness
- Known data effects
- Language editions and codes
- API limits and errors
- Files and cache

## Coverage and freshness

- Pageviews exist from 2015-07-01 until yesterday (UTC). Months are only analysed when complete.
- Older "pagecounts" data (2008–2016) uses a different method and is not used.
- Monthly top lists (`top`) come from Wikimedia's top-1000 list for that month.

## Known data effects

- Platform-wide decline: human pageviews on Wikipedia have been falling (Wikimedia reported about −8%
  year over year in 2025, attributed to search and AI answers). Use relative growth for topic interest.
- Bot re-classification: Wikimedia improved bot detection in 2025 and re-classified traffic for
  March–August 2025; comparisons across that period can shift slightly (the output warns when relevant).
- Undetected bots can create one-day spikes, often on desktop only; check spike dates in the output
  or run `views ... --access desktop` vs `--access mobile-web`.
- Renamed articles keep their old views under the old title, which becomes a redirect; redirects are
  included by default so history is not lost.
- A missing article in some edition is common (smaller editions cover fewer topics). It means the topic
  is not measurable there directly, not that nobody is interested.
- Sections of an article cannot be measured separately.

## Language editions and codes

- Codes follow Wikipedia subdomains: `pl`, `uk`, `zh-yue` (Cantonese), `als` (Alemannic, ISO `gsw`),
  `be-tarask`, `zh-min-nan`, `simple` (Simple English). English/native language names also work.
- Some editions are inflated by bot-created articles (e.g. `ceb`, `war`); judge edition size by views
  (`views ... --totals`), not article counts.
- A language is not a country; for country questions pick the languages read there and state it.

## API limits and errors

- The scripts identify themselves with a User-Agent including WIKI_CONTACT (if set), stay under
  Wikimedia's limits (≤ 3 requests/second, ≤ 3 at a time) and retry 429/5xx automatically.
- Exit codes: 2 = invalid input or ambiguous topic (message says what to fix), 3 = nothing found /
  no data, 4 = network or API failure after retries (wait a minute, retry once, then tell the user).
- "Unknown Wikipedia language": use the wiki code; countries are not accepted as languages.

## Files and cache

- Each `analyze` writes a directory (printed as `Files:`) with results.json, summary.md, series.csv,
  trend.png, growth.png; `report` adds report.pdf there. Default location: ~/wiki-interest/analyses
  (env WIKI_INTEREST_OUT).
- Downloaded data is cached in ~/wiki-interest/cache.sqlite (env WIKI_INTEREST_CACHE); repeated and
  follow-up analyses only fetch days not seen before.
