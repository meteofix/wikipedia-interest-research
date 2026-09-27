# Eval results: `dev-it3` (dev)

Graded 2026-09-27 19:11 UTC; judge: sonnet.
Rates show k/n and a 95% Wilson interval. `noskill` excludes U1/U2 from the universal composite.

## Summary

| config | runs | all universal checks | task success | fabricated numbers | median tool calls (p90) | median time | median cost |
|---|---|---|---|---|---|---|---|
| skill | 71 | 54% (38/71) [42%–65%] | 21% (15/71) [13%–32%] | 42 | 4 (7) | 0.8 min | $0.061 |

## Universal checks

| check | skill |
|---|---|
| U1 used the skill | 89% (63/71) |
| U2 no custom data code | 100% (71/71) |
| U3 numbers grounded | 79% (56/71) |
| U4 window + confidence stated | 90% (57/63) |
| U5 assumptions/limitations | 96% (68/71) |
| U6 no overclaiming | 87% (62/71) |
| U7 artifacts valid | 100% (20/20) |
| U8 answer in user's language | 100% (71/71) |

## Other criteria

**skill**: stability (items with ≥2 runs) n/a; partial/out-of-scope success 11% (2/19) [3%–31%]; single-turn median tool calls 4.0, median time 0.7 min; runs with flagged numbers 16; timeouts 0; contact leaks 0; API fetches in follow-up turns [0, 6, 0, None, None, 8, 0].

## Slices (skill; diagnostic, small n)

| slice | value | task success | all universal |
|---|---|---|---|
| intent | compare_languages | 43% (3/7) | 57% (4/7) |
| intent | compare_topics | 33% (2/6) | 83% (5/6) |
| intent | discovery | 0% (0/4) | 50% (2/4) |
| intent | event_spike | 0% (0/4) | 25% (1/4) |
| intent | followup_modify | 0% (0/4) | 50% (2/4) |
| intent | level_size | 50% (2/4) | 50% (2/4) |
| intent | matrix | 0% (0/4) | 75% (3/4) |
| intent | methodology | 33% (1/3) | 0% (0/3) |
| intent | out_of_scope | 20% (1/5) | 20% (1/5) |
| intent | rank_markets | 33% (3/9) | 67% (6/9) |
| intent | report_request | 17% (1/6) | 67% (4/6) |
| intent | seasonality_timing | 0% (0/4) | 25% (1/4) |
| intent | trend_single | 17% (1/6) | 83% (5/6) |
| intent | trust_robustness | 20% (1/5) | 40% (2/5) |
| coverage_trap | en_only | 0% (0/1) | 0% (0/1) |
| coverage_trap | merged | 50% (1/2) | 50% (1/2) |
| coverage_trap | missing_all | 0% (0/1) | 100% (1/1) |
| coverage_trap | missing_in_some | 33% (3/9) | 89% (8/9) |
| coverage_trap | none | 19% (11/58) | 48% (28/58) |
| scope | full | 25% (13/52) | 58% (30/52) |
| scope | out | 33% (1/3) | 33% (1/3) |
| scope | partial | 6% (1/16) | 44% (7/16) |
| scripts | arabic | 67% (2/3) | 100% (3/3) |
| scripts | armenian | 100% (1/1) | 100% (1/1) |
| scripts | cjk | 12% (1/8) | 38% (3/8) |
| scripts | cyrillic | 29% (5/17) | 71% (12/17) |
| scripts | devanagari | 33% (1/3) | 67% (2/3) |
| scripts | georgian | 50% (1/2) | 50% (1/2) |
| scripts | greek | 0% (0/1) | 100% (1/1) |
| scripts | hebrew | 0% (0/1) | 0% (0/1) |
| scripts | latin | 13% (7/53) | 58% (31/53) |
| scripts | thai | 0% (0/1) | 0% (0/1) |
| user_language | cs | 100% (1/1) | 100% (1/1) |
| user_language | de | 25% (1/4) | 50% (2/4) |
| user_language | en | 9% (2/23) | 43% (10/23) |
| user_language | es | 0% (0/2) | 100% (2/2) |
| user_language | fr | 0% (0/1) | 0% (0/1) |
| user_language | it | 0% (0/1) | 0% (0/1) |
| user_language | pl | 0% (0/4) | 100% (4/4) |
| user_language | pt | 0% (0/1) | 0% (0/1) |
| user_language | ru | 0% (0/1) | 100% (1/1) |
| user_language | uk | 33% (11/33) | 55% (18/33) |

## Per run

| item | config | run | U1 | U2 | U3 | U4 | U5 | U6 | U7 | U8 | success | tools | flagged numbers / problems |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev-001 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-002 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 | 25 |
| dev-003 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-004 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-005 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| dev-006 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 7 |  |
| dev-007 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 12 |  |
| dev-008 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 3 |  |
| dev-009 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-010 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-011 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| dev-012 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 6 | 150, 180 |
| dev-013 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | -20% |
| dev-014 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-015 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-016 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-017 | skill | 1 | ✗ | ✓ | ✗ | – | ✓ | ✓ | – | ✓ | ✗ | 0 | 1000, 1500, 50%, 50, 70% |
| dev-018 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 3 | 17 |
| dev-019 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-020 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 |  |
| dev-021 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | 7 |  |
| dev-022 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 | 2.5, 31, 17 |
| dev-023 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 7 |  |
| dev-024 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 6 | 57, 59 |
| dev-025 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-026 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-027 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-028 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 10 |  |
| dev-029 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-030 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-031 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | – | ✓ | ✗ | 4 |  |
| dev-032 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 3 |  |
| dev-033 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 | 7.742, 34, 1.600, 676.000, 250 |
| dev-034 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-035 | skill | 1 | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | – | ✓ | ✗ | 4 | 2.3, 26, 10.4, 2.3 |
| dev-036 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| dev-037 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-038 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-039 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | – | ✓ | ✗ | 6 | 12.500 |
| dev-040 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-041 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 | 2,5, 11,783, 4,431, 4,431 |
| dev-042 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 6 | 5000 |
| dev-043 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 8 |  |
| dev-044 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-045 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 0 |  |
| dev-046 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-047 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 3 |  |
| dev-048 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-049 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-050 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-051 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-052 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-053 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-054 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 0 |  |
| dev-055 | skill | 1 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-056 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 4 |  |
| dev-057 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-058 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 6 | 180 |
| dev-059 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 12 | 2.2 |
| dev-060 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 2 |  |
| dev-061 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 8 |  |
| dev-062 | skill | 1 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✓ | 0 |  |
| dev-d01 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 | 53%, 45%, 45, 53% |
| dev-d02 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 6 |  |
| dev-d03 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 4 |  |
| dev-d04 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-d05 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 6 | 1.4, 1.75, 1.6, 1.4, 1.75 |
| dev-d06 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 8 |  |
| dev-p01 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 6 |  |
| dev-p02 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-p03 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
