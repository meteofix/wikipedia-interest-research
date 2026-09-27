# Eval results: `heldout-2` (heldout)

Graded 2026-09-27 20:00 UTC; judge: sonnet.
Rates show k/n and a 95% Wilson interval. `noskill` excludes U1/U2 from the universal composite.

## Summary

| config | runs | all universal checks | task success | fabricated numbers | median tool calls (p90) | median time | median cost |
|---|---|---|---|---|---|---|---|
| skill | 88 | 69% (55/80) [58%–78%] | 44% (35/80) [33%–55%] | 17 | 4 (7) | 0.7 min | $0.056 |

## Universal checks

| check | skill |
|---|---|
| U1 used the skill | 92% (81/88) |
| U2 no custom data code | 98% (86/88) |
| U3 numbers grounded | 89% (78/88) |
| U4 window + confidence stated | 87% (58/67) |
| U5 assumptions/limitations | 90% (72/80) |
| U6 no overclaiming | 95% (76/80) |
| U7 artifacts valid | 93% (13/14) |
| U8 answer in user's language | 100% (86/86) |

## Other criteria

**skill**: stability (items with ≥2 runs) 64% (28/44) [49%–76%]; partial/out-of-scope success n/a; single-turn median tool calls 3.0, median time 0.7 min; runs with flagged numbers 11; timeouts 0; contact leaks 0; API fetches in follow-up turns [17, 0, 0, 0, 0, 0, None, None].

## Slices (skill; diagnostic, small n)

| slice | value | task success | all universal |
|---|---|---|---|
| user_language | ar | 100% (2/2) | 100% (2/2) |
| user_language | de | n/a | n/a |
| user_language | en | 25% (7/28) | 57% (16/28) |
| user_language | es | 50% (1/2) | 100% (2/2) |
| user_language | fr | 50% (1/2) | 0% (0/2) |
| user_language | hi | 0% (0/2) | 50% (1/2) |
| user_language | ja | 0% (0/2) | 100% (2/2) |
| user_language | pl | 0% (0/2) | 0% (0/2) |
| user_language | pt | 100% (2/2) | 100% (2/2) |
| user_language | tr | 100% (2/2) | 100% (2/2) |
| user_language | uk | 56% (20/36) | 78% (28/36) |

## Per run

| item | config | run | U1 | U2 | U3 | U4 | U5 | U6 | U7 | U8 | success | tools | flagged numbers / problems |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ho-001 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-001 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-002 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | 949% |
| ho-002 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-003 | skill | 1 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 0 |  |
| ho-003 | skill | 2 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 0 |  |
| ho-004 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| ho-004 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 6 |  |
| ho-005 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 6 |  |
| ho-005 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 10 |  |
| ho-006 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| ho-006 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| ho-007 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✗ | 0 |  |
| ho-007 | skill | 2 | ✓ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 2 |  |
| ho-008 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-008 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-009 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| ho-009 | skill | 2 | ✓ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 2 |  |
| ho-010 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-010 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-011 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | 4,8, 1,1, 0,6 |
| ho-011 | skill | 2 | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | – | ✓ | ✗ | 4 | 1.1, 0.6 |
| ho-012 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| ho-012 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 7 |  |
| ho-013 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| ho-013 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| ho-014 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| ho-014 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| ho-015 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-015 | skill | 2 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-016 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | 7 |  |
| ho-016 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |  |
| ho-017 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| ho-017 | skill | 2 | ✓ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 1 |  |
| ho-018 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| ho-018 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 4 |  |
| ho-019 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| ho-019 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| ho-020 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| ho-020 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| ho-021 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 5 |  |
| ho-021 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| ho-022 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 4 |  |
| ho-022 | skill | 2 | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 7 | ; inline code: cd /Users/dmytro.vashchuk/repos/pes_task_1_private/eval-runs/heldout-2/skill/ho-022/run2/outputs && python3 << 'EOF'
imp; inline code: pip install scipy numpy -q && cd /Users/dmytro.vashchuk/repos/pes_task_1_private/eval-runs/heldout-2/skill/ho-022/run2/o |
| ho-023 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-023 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-024 | skill | 1 | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 | 14,772, 13,000, 10,000; wrote code via shell: cat > /tmp/chart.py << 'EOF'
import matplotlib.pyplot as plt
from datetime import datetime

data = [
    ("2025-09", 134; ran own script: /tmp/chart.py |
| ho-024 | skill | 2 | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✗ | ✓ | ✗ | 3 |  |
| ho-025 | skill | 1 | ✗ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 2 |  |
| ho-025 | skill | 2 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 1 |  |
| ho-026 | skill | 1 | ✓ | ✓ | ✗ | – | ✓ | ✓ | – | ✓ | ✗ | 1 | 170 |
| ho-026 | skill | 2 | ✓ | ✓ | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | 1 |  |
| ho-027 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 5 |  |
| ho-027 | skill | 2 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | – | ✓ | ✗ | 3 | 80% |
| ho-028 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-028 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-029 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-029 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | – | ✓ | ✗ | 5 |  |
| ho-030 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 5 |  |
| ho-030 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 6 |  |
| ho-031 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | – | ✓ | ✗ | 3 |  |
| ho-031 | skill | 2 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | – | ✓ | ✗ | 4 |  |
| ho-032 | skill | 1 | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | – | ✓ | ✓ | 4 |  |
| ho-032 | skill | 2 | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | – | ✓ | ✗ | 4 |  |
| ho-033 | skill | 1 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 0 |  |
| ho-033 | skill | 2 | ✗ | ✓ | ✓ | – | ✗ | ✓ | – | ✓ | ✗ | 0 |  |
| ho-034 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-034 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-035 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | 5 | 115, 30 |
| ho-035 | skill | 2 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 | 80, 30, 50% |
| ho-036 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-036 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-037 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-037 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 7 |  |
| ho-038 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-038 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-039 | skill | 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-039 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | 3 |  |
| ho-040 | skill | 1 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 | 3.4 |
| ho-040 | skill | 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✗ | 3 |  |
| ho-d01 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 10 | ; judge error: unparseable judge reply: "You've hit your session limit · resets 1:40am (Europe/ |
| ho-d01 | skill | 2 | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | – | 9 | ; judge error: unparseable judge reply: "You've hit your session limit · resets 1:40am (Europe/ |
| ho-d02 | skill | 1 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 7 | 2,551, 1,253, 560, 2,551, 1,253, 560; judge error: unparseable judge reply: "You've hit your session limit · resets 1:40am (Europe/ |
| ho-d02 | skill | 2 | ✓ | ✓ | ✗ | – | – | – | – | ✓ | – | 9 | 271, 111; judge error: unparseable judge reply: "You've hit your session limit · resets 1:40am (Europe/ |
| ho-d03 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 9 | ; judge error: unparseable judge reply: "You've hit your session limit · resets 1:40am (Europe/ |
| ho-d03 | skill | 2 | ✓ | ✓ | ✓ | – | – | – | – | ✓ | – | 11 | ; judge error: unparseable judge reply: "You've hit your session limit · resets 1:40am (Europe/ |
| ho-d04 | skill | 1 | ✓ | ✓ | ✓ | – | – | – | ✓ | – | – | 5 | ; judge error: unparseable judge reply: "You've hit your session limit · resets 1:40am (Europe/ |
| ho-d04 | skill | 2 | ✓ | ✓ | ✓ | – | – | – | ✓ | – | – | 6 | ; judge error: unparseable judge reply: "You've hit your session limit · resets 1:40am (Europe/ |
