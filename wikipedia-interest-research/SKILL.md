---
name: wikipedia-interest-research
description: Measures public interest in topics across Wikipedia language editions using Wikimedia pageview data — growth with confidence ratings, comparisons of languages/markets or topics, seasonality, topic discovery, charts and a one-page PDF report. Use when someone (often a founder or product manager) asks whether interest in a topic, course, skill, product category or hobby is growing, which languages, markets or topics look most promising, when interest peaks, how reliable such a signal is, or wants a shareable report based on Wikipedia views.
compatibility: Requires Python 3.10+ with uv (or pip) and internet access to wikimedia.org and wikidata.org. Optional env WIKI_CONTACT (email or URL) identifies you to the Wikimedia API.
metadata:
  version: "0.1.0"
---

# Wikipedia interest research

The scripts do all data work and statistics. Your job: turn the question into topics and
language editions, run the commands, and explain the results honestly.

## Rules

- Never calculate numbers yourself and never write your own code or curl calls to get or
  analyze data. Every number you give the user must be copied from command output.
- Run commands from this skill's directory: `uv run scripts/wiki.py <command>` (the first run
  installs dependencies in ~10 s). No uv? `pip install numpy matplotlib fpdf2` and use `python3`.
- Answer in the user's language.

## Workflow

1. **Parse the request**: topic(s), language editions, period, the user's criteria of
   "promising" (e.g. "growth above 15%"), wanted output (answer, chart, PDF).
   - Use English topic names for search. Map languages to Wikipedia codes (Polish → `pl`,
     Czech → `cs`, Cantonese → `zh-yue`). For countries or regions pick the languages people
     there read and say which you picked.
   - Ask the user only when the topic is ambiguous and context does not decide it, when they
     mention "our/selected languages" without listing them, or when a topic has no article and
     no sensible proxy. Ask only for what is missing (period and metric have defaults).
     Otherwise proceed and state your assumptions.
2. **Find articles**: `uv run scripts/wiki.py find "<topic>" --langs pl,cs`
   - Check that the best match's description fits the user's meaning. On `AMBIGUOUS`, choose by
     context or ask.
   - `NO ARTICLE` for a language = not directly measurable there. Tell the user. You may add a
     related article as a clearly labelled proxy: `"Topic=Q123+pl:Related title"`.
   - A broad theme ("learning languages", "home fitness") is better measured by 2–5 core
     articles summed into one topic: `find "a" "b" "c"`, then `analyze "Label=Q1+Q2+Q3"`.
   - Activities and intents ("learning X", "getting into Y") have no article of their own: you
     measure them through proxy articles (e.g. the article about X). Say so in the answer —
     which article stands in for what the user asked, and that it also captures other interest.
3. **Analyze**: `uv run scripts/wiki.py analyze Q123 --langs pl,cs`
   - Period: default 36 full months; "last two years" → `--months 24` (growth needs ≥ 24).
   - Compare topics: `analyze Q1 Q2 Q3 --langs uk`. User thresholds: `--min-growth 15
     --min-views 100`. Ranking: `--rank-by growth|share|views`.
4. **Answer** with the template below.
5. **Shareable report** — only when the user asks for a report, PDF, one-pager or something
   to share. Pipe your notes (sections from `report --template`; numbers only from the summary)
   and use the exact "Analysis directory" path printed by `analyze`:

   ```bash
   uv run scripts/wiki.py report <analysis dir> --lang uk --notes - <<'EOF'
   ## Headline
   ...
   ## Key points
   - ...
   ## Recommendation
   ...
   ## Next steps
   - ...
   EOF
   ```
   `--lang` is en or uk (other user languages: en labels, your notes in the user's language).
   If it lists numbers not found in the results, fix the notes and rerun.

## Reading the output

- **Relative growth** (main metric): change of the topic's share of all views in that edition,
  last 12 months vs the previous 12. It removes platform-wide traffic shifts. Absolute and
  edition growth sit next to it; if they differ in sign, say so.
- **Direction** (growing / declining / flat / uncertain) and **confidence** (High / Medium / Low)
  come with reasons. Always report the confidence and its main reason.
- **Share per M** compares interest level across editions of different size; **views/day** is the
  absolute audience.
- Ranking notes say whether the leader is robust and whether ranges overlap; overlapping ranges
  mean no clear winner.

## Answer template

1. Direct answer in 1–2 sentences with the key numbers.
2. Per language/topic: views/day, relative growth [95% range], direction, confidence.
3. Why we are (not) confident: 1–3 reasons from the output.
4. Data used: the exact window (e.g. 2023-09…2026-08) and the articles measured per language
   (the "Articles measured" line), marking proxies as proxies.
5. Limitations that matter here: languages without an article, interest is not willingness to
   pay, a language is not a country.
6. Suggested next step. Include chart and PDF paths when produced.

## Other commands

- Follow-ups ("add Slovak", "only last 2 years", "without redirects", new thresholds): rerun
  `analyze` with changed flags. Cached data is reused, so it takes seconds.
- `views <topic> --langs de --access desktop|mobile-web|mobile-app --totals` — raw monthly or daily
  (`--granularity daily`) series for custom questions such as platform split or exact months.
- `top --lang cs [--month 2026-08] [--match word]` — most viewed articles, for "what is popular".
- `uv run scripts/wiki.py --help` lists every flag.
- Methodology questions ("how is confidence computed?"): read
  [references/methodology.md](references/methodology.md).
- Data caveats, API limits, errors: read [references/data-notes.md](references/data-notes.md).

## Gotchas

- Data starts July 2015 and ends yesterday; the current month is incomplete and excluded.
- Exit code 2 with "ambiguous" lists candidate QIDs: pick one and rerun. Exit code 4 is a
  network/API problem: wait a minute and retry once.
- Spikes (news, launches, eclipses, deaths) inflate growth; the reasons say when growth depends
  on spikes. A series that starts inside the window (new or renamed article) is flagged.
- Below ~10 views/day the signal is weak (Low confidence): don't rank or recommend on it alone.
- Name results by edition ("Vietnamese Wikipedia"), not by country, and never mix in other
  editions (e.g. English Wikipedia) unless you analysed them.
