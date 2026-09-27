# Eval results: `dev-it1` (dev)

Graded 2026-09-27 17:05 UTC; judge: sonnet.
Rates show k/n and a 95% Wilson interval. `noskill` excludes U1/U2 from the universal composite.

## Summary

| config | runs | all universal checks | task success | fabricated numbers | median tool calls (p90) | median time | median cost |
|---|---|---|---|---|---|---|---|
| skill | 19 | 74% (14/19) [51%–88%] | 21% (4/19) [9%–43%] | 12 | 5 (7) | 1.1 min | $0.052 |

## Universal checks

| check | skill |
|---|---|
| U1 used the skill | 89% (17/19) |
| U2 no custom data code | 100% (19/19) |
| U3 numbers grounded | 79% (15/19) |
| U4 window + confidence stated | 94% (16/17) |
| U5 assumptions/limitations | 95% (18/19) |
| U6 no overclaiming | 95% (18/19) |
| U7 artifacts valid | 100% (6/6) |
| U8 answer in user's language | 100% (19/19) |

## Other criteria

**skill**: stability (items with ≥2 runs) n/a; partial/out-of-scope success 0% (0/3) [0%–56%]; single-turn median tool calls 5, median time 1.1 min; runs with flagged numbers 5; timeouts 0; contact leaks 0; API fetches in follow-up turns n/a.

## Slices (skill; diagnostic, small n)

| slice | value | task success | all universal |
|---|---|---|---|
| intent | compare_languages | 67% (2/3) | 67% (2/3) |
| intent | compare_topics | 0% (0/4) | 100% (4/4) |
| intent | event_spike | 0% (0/1) | 0% (0/1) |
| intent | level_size | 0% (0/1) | 100% (1/1) |
| intent | matrix | 0% (0/1) | 100% (1/1) |
| intent | methodology | 0% (0/1) | 0% (0/1) |
| intent | out_of_scope | 0% (0/1) | 0% (0/1) |
| intent | rank_markets | 0% (0/2) | 100% (2/2) |
| intent | seasonality_timing | 0% (0/1) | 100% (1/1) |
| intent | trend_single | 50% (2/4) | 75% (3/4) |
| coverage_trap | merged | 0% (0/1) | 100% (1/1) |
| coverage_trap | missing_all | 100% (1/1) | 100% (1/1) |
| coverage_trap | missing_in_some | 33% (1/3) | 67% (2/3) |
| coverage_trap | none | 14% (2/14) | 71% (10/14) |
| scope | full | 25% (4/16) | 81% (13/16) |
| scope | out | 0% (0/1) | 0% (0/1) |
| scope | partial | 0% (0/2) | 50% (1/2) |
| scripts | arabic | 0% (0/1) | 100% (1/1) |
| scripts | cjk | 50% (1/2) | 100% (2/2) |
| scripts | cyrillic | 20% (1/5) | 80% (4/5) |
| scripts | devanagari | 0% (0/1) | 100% (1/1) |
| scripts | hebrew | 0% (0/1) | 100% (1/1) |
| scripts | latin | 21% (3/14) | 71% (10/14) |
| user_language | cs | 100% (1/1) | 100% (1/1) |
| user_language | en | 17% (1/6) | 83% (5/6) |
| user_language | es | 0% (0/1) | 100% (1/1) |
| user_language | pl | 0% (0/2) | 50% (1/2) |
| user_language | uk | 22% (2/9) | 67% (6/9) |

## Per run

| item | config | run | U1 | U2 | U3 | U4 | U5 | U6 | U7 | U8 | success | tools | flagged numbers / problems |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev-001 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| dev-002 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 4 | 240, 2,5, 20%, 240, 230, 205 |
| dev-003 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-004 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-005 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-006 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 | 115% |
| dev-007 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 10 |  |
| dev-008 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 3 | 2.5 |
| dev-009 | skill | 1 | ✗ | ✓ | ✗ | – | ✓ | ✓ | – | ✓ | ✗ | 0 | 15 |
| dev-010 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| dev-011 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 7 |  |
| dev-012 | skill | 1 | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | – | ✓ | ✗ | 5 | +45%, 15,000, 17.5, +62% |
| dev-013 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-014 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
| dev-015 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| dev-017 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| dev-018 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| dev-019 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 5 |  |
| dev-020 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 5 |  |
