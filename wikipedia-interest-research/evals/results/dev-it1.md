# Eval results: `dev-it1` (dev)

Graded 2026-09-27 17:49 UTC; judge: sonnet.
Rates show k/n and a 95% Wilson interval. `noskill` excludes U1/U2 from the universal composite.

## Summary

| config | runs | all universal checks | task success | fabricated numbers | median tool calls (p90) | median time | median cost |
|---|---|---|---|---|---|---|---|
| noskill | 15 | 0% (0/15) [0%–20%] | 0% (0/15) [0%–20%] | 61 | 4 (19) | 0.3 min | $0.039 |
| skill | 71 | 63% (45/71) [52%–74%] | 24% (17/71) [16%–35%] | 39 | 5 (8) | 1.3 min | $0.059 |

## Universal checks

| check | noskill | skill |
|---|---|---|
| U1 used the skill | n/a | 87% (62/71) |
| U2 no custom data code | 33% (5/15) | 99% (70/71) |
| U3 numbers grounded | 67% (10/15) | 85% (60/71) |
| U4 window + confidence stated | 0% (0/9) | 90% (57/63) |
| U5 assumptions/limitations | 33% (5/15) | 90% (64/71) |
| U6 no overclaiming | 67% (10/15) | 87% (62/71) |
| U7 artifacts valid | 0% (0/5) | 100% (20/20) |
| U8 answer in user's language | 100% (15/15) | 100% (71/71) |

## Other criteria

**noskill**: stability (items with ≥2 runs) n/a; partial/out-of-scope success 0% (0/3) [0%–56%]; single-turn median tool calls 4, median time 0.3 min; runs with flagged numbers 6; timeouts 0; contact leaks 0; API fetches in follow-up turns n/a.

**skill**: stability (items with ≥2 runs) n/a; partial/out-of-scope success 16% (3/19) [6%–38%]; single-turn median tool calls 4.0, median time 1.2 min; runs with flagged numbers 18; timeouts 0; contact leaks 0; API fetches in follow-up turns [46, 31, None, 17, None, 7, 0].

## Skill vs no skill (15 common items)

| metric | skill | no skill |
|---|---|---|
| task_success | 20% (3/15) [7%–45%] | 0% (0/15) [0%–20%] |
| all_universal | 73% (11/15) [48%–89%] | 0% (0/15) [0%–20%] |
| U3 | 73% (11/15) [48%–89%] | 67% (10/15) [42%–85%] |

## Slices (noskill; diagnostic, small n)

| slice | value | task success | all universal |
|---|---|---|---|
| intent | compare_languages | 0% (0/3) | 0% (0/3) |
| intent | compare_topics | 0% (0/3) | 0% (0/3) |
| intent | event_spike | 0% (0/1) | 0% (0/1) |
| intent | matrix | 0% (0/1) | 0% (0/1) |
| intent | out_of_scope | 0% (0/1) | 0% (0/1) |
| intent | rank_markets | 0% (0/2) | 0% (0/2) |
| intent | seasonality_timing | 0% (0/1) | 0% (0/1) |
| intent | trend_single | 0% (0/3) | 0% (0/3) |
| coverage_trap | merged | 0% (0/1) | 0% (0/1) |
| coverage_trap | missing_in_some | 0% (0/3) | 0% (0/3) |
| coverage_trap | none | 0% (0/11) | 0% (0/11) |
| scope | full | 0% (0/12) | 0% (0/12) |
| scope | out | 0% (0/1) | 0% (0/1) |
| scope | partial | 0% (0/2) | 0% (0/2) |
| scripts | arabic | 0% (0/1) | 0% (0/1) |
| scripts | cjk | 0% (0/2) | 0% (0/2) |
| scripts | cyrillic | 0% (0/4) | 0% (0/4) |
| scripts | devanagari | 0% (0/1) | 0% (0/1) |
| scripts | latin | 0% (0/12) | 0% (0/12) |
| user_language | cs | 0% (0/1) | 0% (0/1) |
| user_language | en | 0% (0/5) | 0% (0/5) |
| user_language | es | 0% (0/1) | 0% (0/1) |
| user_language | pl | 0% (0/1) | 0% (0/1) |
| user_language | uk | 0% (0/7) | 0% (0/7) |

## Slices (skill; diagnostic, small n)

| slice | value | task success | all universal |
|---|---|---|---|
| intent | compare_languages | 57% (4/7) | 86% (6/7) |
| intent | compare_topics | 0% (0/6) | 83% (5/6) |
| intent | discovery | 0% (0/4) | 75% (3/4) |
| intent | event_spike | 0% (0/4) | 0% (0/4) |
| intent | followup_modify | 0% (0/4) | 50% (2/4) |
| intent | level_size | 25% (1/4) | 25% (1/4) |
| intent | matrix | 0% (0/4) | 75% (3/4) |
| intent | methodology | 0% (0/3) | 0% (0/3) |
| intent | out_of_scope | 20% (1/5) | 0% (0/5) |
| intent | rank_markets | 33% (3/9) | 78% (7/9) |
| intent | report_request | 50% (3/6) | 83% (5/6) |
| intent | seasonality_timing | 0% (0/4) | 100% (4/4) |
| intent | trend_single | 50% (3/6) | 83% (5/6) |
| intent | trust_robustness | 40% (2/5) | 80% (4/5) |
| coverage_trap | en_only | 100% (1/1) | 100% (1/1) |
| coverage_trap | merged | 0% (0/2) | 100% (2/2) |
| coverage_trap | missing_all | 100% (1/1) | 100% (1/1) |
| coverage_trap | missing_in_some | 33% (3/9) | 78% (7/9) |
| coverage_trap | none | 21% (12/58) | 59% (34/58) |
| scope | full | 27% (14/52) | 69% (36/52) |
| scope | out | 33% (1/3) | 0% (0/3) |
| scope | partial | 12% (2/16) | 56% (9/16) |
| scripts | arabic | 0% (0/3) | 67% (2/3) |
| scripts | armenian | 100% (1/1) | 100% (1/1) |
| scripts | cjk | 25% (2/8) | 62% (5/8) |
| scripts | cyrillic | 41% (7/17) | 65% (11/17) |
| scripts | devanagari | 0% (0/3) | 67% (2/3) |
| scripts | georgian | 100% (2/2) | 100% (2/2) |
| scripts | greek | 0% (0/1) | 100% (1/1) |
| scripts | hebrew | 0% (0/1) | 100% (1/1) |
| scripts | latin | 17% (9/53) | 66% (35/53) |
| scripts | thai | 0% (0/1) | 100% (1/1) |
| user_language | cs | 100% (1/1) | 100% (1/1) |
| user_language | de | 0% (0/4) | 25% (1/4) |
| user_language | en | 13% (3/23) | 61% (14/23) |
| user_language | es | 0% (0/2) | 100% (2/2) |
| user_language | fr | 0% (0/1) | 0% (0/1) |
| user_language | it | 0% (0/1) | 0% (0/1) |
| user_language | pl | 0% (0/4) | 75% (3/4) |
| user_language | pt | 0% (0/1) | 100% (1/1) |
| user_language | ru | 0% (0/1) | 0% (0/1) |
| user_language | uk | 39% (13/33) | 70% (23/33) |

## Per run

| item | config | run | U1 | U2 | U3 | U4 | U5 | U6 | U7 | U8 | success | tools | flagged numbers / problems |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev-001 | noskill | 1 | – | ✗ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 19 | 1.3; fetched Wikimedia directly: {"url": "https://en.wikipedia.org/api/rest_v1/metrics/pageviews/per-article/uk.wikipedia/all-agent/pilates/daily/2023092; direct API call: curl -s "https://en.wikipedia.org/api/rest_v1/metrics/pageviews/per-article/uk.wikipedia/all-agent/pilates/daily/2023092 |
| dev-001 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-002 | noskill | 1 | – | ✗ | ✓ | – | ✗ | ✓ | ✗ | ✓ | ✗ | 5 | ; fetched Wikimedia directly: {"url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/pl.wikipedia.org/all-access/user/Morsowanie/dai; fetched Wikimedia directly: {"url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/pl.wikipedia.org/all-access/user/Morsowanie/dai |
| dev-002 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 4 | 240, 2,5, 20%, 240, 230, 205 |
| dev-003 | noskill | 1 | – | ✗ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 4 | ; fetched Wikimedia directly: {"url": "https://pageviews.toolforge.org/api.php?project=uk.wikipedia.org&article=\u041f\u0435\u0434\u0430\u0433\u043e\u; fetched Wikimedia directly: {"url": "https://pageviews.toolforge.org/api.php?project=uk.wikipedia.org&article=\u0412\u0430\u043b\u044c\u0434\u043e\u |
| dev-003 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-004 | noskill | 1 | – | ✓ | ✗ | ✗ | ✓ | ✗ | – | ✓ | ✗ | 3 | 220, 340, 310, 170, 85 |
| dev-004 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-005 | noskill | 1 | – | ✗ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 3 | ; fetched Wikimedia directly: {"url": "https://uk.wikipedia.org/wiki/\u041d\u0430\u0446\u0456\u043e\u043d\u0430\u043b\u044c\u043d\u0438\u0439_\u043c\u; fetched Wikimedia directly: {"url": "https://uk.wikipedia.org/wiki/\u041d\u0430\u0446\u0456\u043e\u043d\u0430\u043b\u044c\u043d\u0438\u0439_\u043c\u |
| dev-005 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-006 | noskill | 1 | – | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ | 4 | ; fetched Wikimedia directly: {"url": "https://en.wikipedia.org/wiki/Gemini_(chatbot)"}; fetched Wikimedia directly: {"url": "https://en.wikipedia.org/wiki/Gemini_(chatbot)", "prompt": "What information is provided about Gemini's launch  |
| dev-006 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 | 115% |
| dev-007 | noskill | 1 | – | ✓ | ✓ | – | ✗ | ✓ | ✗ | ✓ | ✗ | 0 |  |
| dev-007 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 10 |  |
| dev-008 | noskill | 1 | – | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 6 |  |
| dev-008 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 3 | 2.5 |
| dev-009 | noskill | 1 | – | ✓ | ✗ | ✗ | ✗ | ✗ | – | ✓ | ✗ | 0 | 14.99, 40%, 50, 60 |
| dev-009 | skill | 1 | ✗ | ✓ | ✗ | – | ✓ | ✓ | – | ✓ | ✗ | 0 | 15 |
| dev-010 | noskill | 1 | – | ✗ | ✓ | ✗ | ✓ | ✗ | – | ✓ | ✗ | 44 | ; fetched Wikimedia directly: {"url": "https://zh.wikipedia.org/api/rest_v1/metrics/pageviews/per-article/zh.wikipedia/all-access/all-agents/%E7%8F%8D; fetched Wikimedia directly: {"url": "https://zh-yue.wikipedia.org/api/rest_v1/metrics/pageviews/per-article/zh-yue.wikipedia/all-access/all-agents/% |
| dev-010 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| dev-011 | noskill | 1 | – | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | 19 | ; fetched Wikimedia directly: {"url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/cs.wikipedia.org/all-access/all-agents/Houba%C5; fetched Wikimedia directly: {"url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/sk.wikipedia.org/all-access/all-agents/Zberanie |
| dev-011 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 7 |  |
| dev-012 | noskill | 1 | – | ✗ | ✗ | – | ✗ | ✓ | – | ✓ | ✗ | 4 | 17; fetched Wikimedia directly: {"url": "https://en.wikipedia.org/wiki/Korean_language", "prompt": "Is there any mention of increased interest in Korean; fetched Wikimedia directly: {"url": "https://es.wikipedia.org/wiki/Idioma_coreano", "prompt": "\u00bfHay alguna menci\u00f3n de mayor inter\u00e9s e |
| dev-012 | skill | 1 | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | – | ✓ | ✗ | 5 | +45%, 15,000, 17.5, +62% |
| dev-013 | noskill | 1 | – | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 2 |  |
| dev-013 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-014 | noskill | 1 | – | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | 12 | 1.5, 3.5%, 12%, 1.1, 4.8%, 77; inline code: python3 << 'EOF'
import subprocess
import sys

# Try to import common PDF libraries
try:
    import weasyprint
    print; inline code: python3 -m pip install weasyprint -q && python3 << 'EOF'
from weasyprint import HTML
import os

html_file = '/tmp/kbeaut |
| dev-014 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-015 | noskill | 1 | – | ✗ | ✗ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 18 | 9,692, -51%, 2,856, +40, 50%, 5.7; fetched Wikimedia directly: {"url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/es.wikipedia.org/all-access/all-agents/Ajedrez/; fetched Wikimedia directly: {"url": "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/es.wikipedia.org/all-access/all-agents/P\u00f3q |
| dev-015 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-016 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-017 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-018 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-019 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 5 |  |
| dev-020 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-021 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-022 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 18 |  |
| dev-023 | skill | 1 | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | 6 | 5.6, 2.8 |
| dev-024 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| dev-025 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 13 |  |
| dev-026 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 4 |  |
| dev-027 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-028 | skill | 1 | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | – | ✓ | ✗ | 4 | 5,108, 2.5, 40,866, 5,108, 21,388, 3,961 |
| dev-029 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✓ | 3 |  |
| dev-030 | skill | 1 | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 10 | 40.828, 38.922, 29.014, 28.653, 21.763, 19.590; fetched Wikimedia directly: {"url": "https://de.wikipedia.org/wiki/Wikipedia:Aktuelle_Ereignisse", "prompt": "Was sind die aktuellen Trends und beli; direct API call: curl -s "https://de.wikipedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles=Main_Page&origin=*" / head -5 |
| dev-031 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-032 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| dev-033 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | – | ✓ | ✗ | 7 |  |
| dev-034 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-035 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | – | ✓ | ✗ | 5 |  |
| dev-036 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 | 3,5 |
| dev-037 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | 27% |
| dev-038 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| dev-039 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | – | ✓ | ✗ | 5 | 300, 80, 140 |
| dev-040 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 7 |  |
| dev-041 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | – | ✓ | ✗ | 3 | 2,5 |
| dev-042 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | – | ✓ | ✗ | 8 | 18 |
| dev-043 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-044 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-045 | skill | 1 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✓ | 1 |  |
| dev-046 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-047 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-048 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-049 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-050 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-051 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-052 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 8 |  |
| dev-053 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-054 | skill | 1 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-055 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 0 |  |
| dev-056 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 7 | 09.2023, 08.2026 |
| dev-057 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | 200 |
| dev-058 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 13 |  |
| dev-059 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6 |  |
| dev-060 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| dev-061 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 12 |  |
| dev-062 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 0 |  |
| dev-d01 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 9 | 59%, 48%, +48 п.п. |
| dev-d02 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-d03 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 | 14 |
| dev-d04 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-d05 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 8 | 4,100, 6,550, 4,100, 3,550, 3.5 |
| dev-d06 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | 6 |  |
| dev-p01 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-p02 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-p03 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
