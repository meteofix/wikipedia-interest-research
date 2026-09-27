# Eval results: `dev-it2` (dev)

Graded 2026-09-27 17:39 UTC; judge: none (automatic checks only).
Rates show k/n and a 95% Wilson interval. `noskill` excludes U1/U2 from the universal composite.

## Summary

| config | runs | all universal checks | task success | fabricated numbers | median tool calls (p90) | median time | median cost |
|---|---|---|---|---|---|---|---|
| skill | 71 | 65% (46/71) [53%–75%] | n/a | n/a | 4 (8) | 0.8 min | $0.059 |

## Universal checks

| check | skill |
|---|---|
| U1 used the skill | 93% (66/71) |
| U2 no custom data code | 93% (66/71) |
| U3 numbers grounded | 79% (56/71) |
| U4 window + confidence stated | n/a |
| U5 assumptions/limitations | n/a |
| U6 no overclaiming | n/a |
| U7 artifacts valid | 100% (20/20) |
| U8 answer in user's language | 98% (55/56) |

## Other criteria

**skill**: stability (items with ≥2 runs) n/a; partial/out-of-scope success n/a; single-turn median tool calls 3.5, median time 0.8 min; runs with flagged numbers 15; timeouts 0; contact leaks 0; API fetches in follow-up turns [3, 0, 0, None, None, 0, 7].

## Slices (skill; diagnostic, small n)

| slice | value | task success | all universal |
|---|---|---|---|
| intent | compare_languages | n/a | 86% (6/7) |
| intent | compare_topics | n/a | 100% (6/6) |
| intent | discovery | n/a | 100% (4/4) |
| intent | event_spike | n/a | 25% (1/4) |
| intent | followup_modify | n/a | 25% (1/4) |
| intent | level_size | n/a | 50% (2/4) |
| intent | matrix | n/a | 75% (3/4) |
| intent | methodology | n/a | 33% (1/3) |
| intent | out_of_scope | n/a | 40% (2/5) |
| intent | rank_markets | n/a | 67% (6/9) |
| intent | report_request | n/a | 67% (4/6) |
| intent | seasonality_timing | n/a | 25% (1/4) |
| intent | trend_single | n/a | 83% (5/6) |
| intent | trust_robustness | n/a | 80% (4/5) |
| coverage_trap | en_only | n/a | 100% (1/1) |
| coverage_trap | merged | n/a | 100% (2/2) |
| coverage_trap | missing_all | n/a | 100% (1/1) |
| coverage_trap | missing_in_some | n/a | 67% (6/9) |
| coverage_trap | none | n/a | 62% (36/58) |
| scope | full | n/a | 65% (34/52) |
| scope | out | n/a | 33% (1/3) |
| scope | partial | n/a | 69% (11/16) |
| scripts | arabic | n/a | 67% (2/3) |
| scripts | armenian | n/a | 100% (1/1) |
| scripts | cjk | n/a | 62% (5/8) |
| scripts | cyrillic | n/a | 65% (11/17) |
| scripts | devanagari | n/a | 33% (1/3) |
| scripts | georgian | n/a | 100% (2/2) |
| scripts | greek | n/a | 100% (1/1) |
| scripts | hebrew | n/a | 0% (0/1) |
| scripts | latin | n/a | 72% (38/53) |
| scripts | thai | n/a | 100% (1/1) |
| user_language | cs | n/a | 100% (1/1) |
| user_language | de | n/a | 50% (2/4) |
| user_language | en | n/a | 65% (15/23) |
| user_language | es | n/a | 100% (2/2) |
| user_language | fr | n/a | 100% (1/1) |
| user_language | it | n/a | 0% (0/1) |
| user_language | pl | n/a | 100% (4/4) |
| user_language | pt | n/a | 100% (1/1) |
| user_language | ru | n/a | 100% (1/1) |
| user_language | uk | n/a | 58% (19/33) |

## Per run

| item | config | run | U1 | U2 | U3 | U4 | U5 | U6 | U7 | U8 | success | tools | flagged numbers / problems |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev-001 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-002 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | – | – | 6 |  |
| dev-003 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 4 |  |
| dev-004 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-005 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 3 | 70%, 27% |
| dev-006 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | ✓ | ✓ | – | 6 | 127, 40, 40 |
| dev-007 | skill | 1 | ✓ | ✗ | ✓ | – | – | – | ✓ | ✓ | – | 18 | ; inline code: cd /Users/dmytro.vashchuk/repos/pes_task_1_private/eval-runs/dev-it2/skill/dev-007/run1/outputs/20260927-201651-guitar-p; wrote code file: /Users/dmytro.vashchuk/repos/pes_task_1_private/eval-runs/dev-it2/skill/dev-007/run1/outputs/20260927-201651-guitar-piano-ukulele-pl-de-es-pt/matrix_viz.py |
| dev-008 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-009 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 3 | +17, 50 |
| dev-010 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 4 |  |
| dev-011 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | – | – | 5 |  |
| dev-012 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 9 |  |
| dev-013 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-014 | skill | 1 | ✓ | ✗ | ✓ | – | – | – | ✓ | ✓ | – | 12 | ; inline code: python3 -c "
import json

# Fix the verdict.py bug
with open('scripts/wikiinterest/verdict.py', 'r') as f:
    content = |
| dev-015 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | – | – | 3 |  |
| dev-016 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | – | – | 5 |  |
| dev-017 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 3 | 0,5%, 0,6% |
| dev-018 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 5 | 810, 810, 50 |
| dev-019 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 4 |  |
| dev-020 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | – | – | 6 |  |
| dev-021 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 6 |  |
| dev-022 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | ✓ | ✓ | – | 9 | 182 337 |
| dev-023 | skill | 1 | ✓ | ✗ | ✓ | – | – | – | ✓ | ✓ | – | 7 | ; inline code: python3 << 'EOF'
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import ; inline code: uv run --with matplotlib python << 'EOF'
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime |
| dev-024 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-025 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 5 |  |
| dev-026 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | – | – | 6 |  |
| dev-027 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-028 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 8 |  |
| dev-029 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-030 | skill | 1 | ✗ | ✗ | ✓ | – | – | – | – | – | – | 2 | ; fetched Wikimedia directly: {"url": "https://en.wikipedia.org/api/rest_v1/metrics/pageviews/top/de.wikipedia.org/all-access/daily/2026/09/27", "prom |
| dev-031 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 3 | 23%, 27% |
| dev-032 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 5 |  |
| dev-033 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | – | – | 4 | 34, 676.499 |
| dev-034 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 9 |  |
| dev-035 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 9 | +86% |
| dev-036 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | ✓ | ✓ | – | 5 | 3,6%, 2,3 |
| dev-037 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-038 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 6 |  |
| dev-039 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | – | – | 5 | 41.159, 2,5, 16.537, 15.381, 32.062, 41 |
| dev-040 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-041 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 3 | 2,5 |
| dev-042 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 8 |  |
| dev-043 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 5 |  |
| dev-044 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | – | – | 2 |  |
| dev-045 | skill | 1 | ✗ | ✓ | ✓ | – | – | – | – | ✓ | – | 0 |  |
| dev-046 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-047 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | – | – | 7 |  |
| dev-048 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-049 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | – | – | 3 |  |
| dev-050 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-051 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-052 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-053 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | – | – | 4 |  |
| dev-054 | skill | 1 | ✗ | ✓ | ✓ | – | – | – | – | ✓ | – | 0 |  |
| dev-055 | skill | 1 | ✗ | ✓ | ✓ | – | – | – | – | ✓ | – | 0 |  |
| dev-056 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 5 |  |
| dev-057 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | – | – | 3 |  |
| dev-058 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | ✓ | ✓ | – | 9 | 22 659 |
| dev-059 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 8 |  |
| dev-060 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-061 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-062 | skill | 1 | ✗ | ✓ | ✓ | – | – | – | – | ✓ | – | 0 |  |
| dev-d01 | skill | 1 | ✓ | ✗ | ✓ | – | – | – | – | ✓ | – | 6 | ; inline code: python3 << 'EOF'
import csv
from datetime import datetime

# Читання даних
with open('/Users/dmytro.vashchuk/repos/pes_t |
| dev-d02 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 5 | 43 |
| dev-d03 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 4 |  |
| dev-d04 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | – | – | 6 |  |
| dev-d05 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 6 | 23,194, 7.41, 45,370, 5.58, −24.7%, 23,926 |
| dev-d06 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 8 |  |
| dev-p01 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✗ | – | 3 |  |
| dev-p02 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 3 |  |
| dev-p03 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 5 |  |
