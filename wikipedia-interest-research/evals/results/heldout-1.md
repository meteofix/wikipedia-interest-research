# Eval results: `heldout-1` (heldout)

Graded 2026-09-27 18:50 UTC; judge: sonnet.
Rates show k/n and a 95% Wilson interval. `noskill` excludes U1/U2 from the universal composite.

## Summary

| config | runs | all universal checks | task success | fabricated numbers | median tool calls (p90) | median time | median cost |
|---|---|---|---|---|---|---|---|
| skill | 88 | 73% (64/88) [63%–81%] | 43% (38/88) [33%–54%] | 33 | 4 (8) | 0.8 min | $0.054 |

## Universal checks

| check | skill |
|---|---|
| U1 used the skill | 93% (82/88) |
| U2 no custom data code | 100% (88/88) |
| U3 numbers grounded | 89% (78/88) |
| U4 window + confidence stated | 89% (64/72) |
| U5 assumptions/limitations | 89% (78/88) |
| U6 no overclaiming | 97% (85/88) |
| U7 artifacts valid | 93% (13/14) |
| U8 answer in user's language | 100% (88/88) |

## Other criteria

**skill**: stability (items with ≥2 runs) 61% (27/44) [47%–74%]; partial/out-of-scope success n/a; single-turn median tool calls 3.0, median time 0.7 min; runs with flagged numbers 22; timeouts 0; contact leaks 0; API fetches in follow-up turns [4, 1, 2, 5, 0, None, 25, None].
