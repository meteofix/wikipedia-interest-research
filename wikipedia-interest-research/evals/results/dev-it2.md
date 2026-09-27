# Eval results: `dev-it2` (dev)

Graded 2026-09-27 18:19 UTC; judge: sonnet.
Rates show k/n and a 95% Wilson interval. `noskill` excludes U1/U2 from the universal composite.

## Summary

| config | runs | all universal checks | task success | fabricated numbers | median tool calls (p90) | median time | median cost |
|---|---|---|---|---|---|---|---|
| skill | 71 | 59% (42/71) [48%–70%] | 23% (16/71) [14%–34%] | 42 | 4 (8) | 0.8 min | $0.059 |

## Universal checks

| check | skill |
|---|---|
| U1 used the skill | 93% (66/71) |
| U2 no custom data code | 93% (66/71) |
| U3 numbers grounded | 82% (58/71) |
| U4 window + confidence stated | 91% (58/64) |
| U5 assumptions/limitations | 94% (67/71) |
| U6 no overclaiming | 87% (62/71) |
| U7 artifacts valid | 100% (20/20) |
| U8 answer in user's language | 97% (69/71) |

## Other criteria

**skill**: stability (items with ≥2 runs) n/a; partial/out-of-scope success 16% (3/19) [6%–38%]; single-turn median tool calls 3.5, median time 0.8 min; runs with flagged numbers 15; timeouts 0; contact leaks 0; API fetches in follow-up turns [3, 0, 0, None, 7, None, 0].

## Slices (skill; diagnostic, small n)

| slice | value | task success | all universal |
|---|---|---|---|
| intent | compare_languages | 57% (4/7) | 71% (5/7) |
| intent | compare_topics | 17% (1/6) | 100% (6/6) |
| intent | discovery | 0% (0/4) | 75% (3/4) |
| intent | event_spike | 0% (0/4) | 0% (0/4) |
| intent | followup_modify | 0% (0/4) | 25% (1/4) |
| intent | level_size | 50% (2/4) | 50% (2/4) |
| intent | matrix | 0% (0/4) | 50% (2/4) |
| intent | methodology | 67% (2/3) | 67% (2/3) |
| intent | out_of_scope | 20% (1/5) | 60% (3/5) |
| intent | rank_markets | 22% (2/9) | 67% (6/9) |
| intent | report_request | 17% (1/6) | 50% (3/6) |
| intent | seasonality_timing | 0% (0/4) | 25% (1/4) |
| intent | trend_single | 17% (1/6) | 67% (4/6) |
| intent | trust_robustness | 40% (2/5) | 80% (4/5) |
| coverage_trap | en_only | 0% (0/1) | 100% (1/1) |
| coverage_trap | merged | 0% (0/2) | 50% (1/2) |
| coverage_trap | missing_all | 100% (1/1) | 100% (1/1) |
| coverage_trap | missing_in_some | 33% (3/9) | 56% (5/9) |
| coverage_trap | none | 21% (12/58) | 59% (34/58) |
| scope | full | 25% (13/52) | 60% (31/52) |
| scope | out | 33% (1/3) | 67% (2/3) |
| scope | partial | 12% (2/16) | 56% (9/16) |
| scripts | arabic | 0% (0/3) | 67% (2/3) |
| scripts | armenian | 100% (1/1) | 100% (1/1) |
| scripts | cjk | 25% (2/8) | 50% (4/8) |
| scripts | cyrillic | 18% (3/17) | 71% (12/17) |
| scripts | devanagari | 0% (0/3) | 33% (1/3) |
| scripts | georgian | 50% (1/2) | 100% (2/2) |
| scripts | greek | 0% (0/1) | 100% (1/1) |
| scripts | hebrew | 0% (0/1) | 0% (0/1) |
| scripts | latin | 21% (11/53) | 62% (33/53) |
| scripts | thai | 0% (0/1) | 100% (1/1) |
| user_language | cs | 100% (1/1) | 100% (1/1) |
| user_language | de | 25% (1/4) | 50% (2/4) |
| user_language | en | 26% (6/23) | 57% (13/23) |
| user_language | es | 50% (1/2) | 100% (2/2) |
| user_language | fr | 0% (0/1) | 100% (1/1) |
| user_language | it | 0% (0/1) | 0% (0/1) |
| user_language | pl | 0% (0/4) | 75% (3/4) |
| user_language | pt | 0% (0/1) | 0% (0/1) |
| user_language | ru | 0% (0/1) | 100% (1/1) |
| user_language | uk | 21% (7/33) | 58% (19/33) |

## Per run

| item | config | run | U1 | U2 | U3 | U4 | U5 | U6 | U7 | U8 | success | tools | flagged numbers / problems |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev-001 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-002 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-003 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| dev-004 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-005 | skill | 1 | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 3 | 70%, 27% |
| dev-006 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | 6 | 127, 40, 40 |
| dev-007 | skill | 1 | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | 18 | ; inline code: cd /Users/dmytro.vashchuk/repos/pes_task_1_private/eval-runs/dev-it2/skill/dev-007/run1/outputs/20260927-201651-guitar-p; wrote code file: /Users/dmytro.vashchuk/repos/pes_task_1_private/eval-runs/dev-it2/skill/dev-007/run1/outputs/20260927-201651-guitar-piano-ukulele-pl-de-es-pt/matrix_viz.py |
| dev-008 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✓ | 3 |  |
| dev-009 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | +17, 50 |
| dev-010 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| dev-011 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| dev-012 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | – | ✗ | ✗ | 9 |  |
| dev-013 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-014 | skill | 1 | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | 12 | ; inline code: python3 -c "
import json

# Fix the verdict.py bug
with open('scripts/wikiinterest/verdict.py', 'r') as f:
    content = |
| dev-015 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-016 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-017 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 | 0,5%, 0,6% |
| dev-018 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 5 | 810, 810, 50 |
| dev-019 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| dev-020 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-021 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-022 | skill | 1 | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | 9 | 182 337 |
| dev-023 | skill | 1 | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | 7 | ; inline code: python3 << 'EOF'
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import ; inline code: uv run --with matplotlib python << 'EOF'
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime |
| dev-024 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-025 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-026 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 6 |  |
| dev-027 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-028 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 8 |  |
| dev-029 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-030 | skill | 1 | ✗ | ✗ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 2 | ; fetched Wikimedia directly: {"url": "https://en.wikipedia.org/api/rest_v1/metrics/pageviews/top/de.wikipedia.org/all-access/daily/2026/09/27", "prom |
| dev-031 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | 23%, 27% |
| dev-032 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-033 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 | 34, 676.499 |
| dev-034 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 9 |  |
| dev-035 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 9 | +86% |
| dev-036 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 | 3,6%, 2,3 |
| dev-037 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-038 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-039 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | – | ✓ | ✗ | 5 | 41.159, 2,5, 16.537, 15.381, 32.062, 41 |
| dev-040 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-041 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | 2,5 |
| dev-042 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 8 |  |
| dev-043 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-044 | skill | 1 | ✓ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 2 |  |
| dev-045 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 0 |  |
| dev-046 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-047 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 7 |  |
| dev-048 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-049 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-050 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-051 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-052 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-053 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 4 |  |
| dev-054 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 0 |  |
| dev-055 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-056 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| dev-057 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-058 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 9 | 22 659 |
| dev-059 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 8 |  |
| dev-060 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-061 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 3 |  |
| dev-062 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 0 |  |
| dev-d01 | skill | 1 | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 6 | ; inline code: python3 << 'EOF'
import csv
from datetime import datetime

# Читання даних
with open('/Users/dmytro.vashchuk/repos/pes_t |
| dev-d02 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 | 43 |
| dev-d03 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| dev-d04 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | 6 |  |
| dev-d05 | skill | 1 | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 6 | 23,194, 7.41, 45,370, 5.58, −24.7%, 23,926 |
| dev-d06 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 8 |  |
| dev-p01 | skill | 1 | ✓ | ✓ | ✓ | – | ✓ | ✓ | – | ✗ | ✗ | 3 |  |
| dev-p02 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-p03 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
