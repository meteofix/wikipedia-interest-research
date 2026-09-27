"""Number formatting and the "every number must come from the data" check.

The same extraction is used by `report` (to check the agent's notes against results.json)
and by the eval graders (to check final answers against tool outputs), so a number the
agent copies from a summary always matches, whatever sign, decimal comma or separator
style it uses.
"""

from __future__ import annotations

import json
import math
import re
from typing import Iterable

# Numbers written with a decimal comma ("12,5"), thousands separators ("12 345", "12,345"),
# signs ("+12", "−7") and percent signs are all normalised to plain floats.
_NUM_RE = re.compile(
    r"(?<![\w.])([+\-−–]?)(\d{1,3}(?:[   ,]\d{3})+|\d+)(?:[.,](\d+))?\s*(%|п\.п\.|pp|p\.p\.)?",
    re.UNICODE,
)
_YEAR_MIN, _YEAR_MAX = 1990, 2040


def fmt_pct(x: float | None, signed: bool = True) -> str:
    """Growth as a percentage: one decimal below 10%, integers above (what a founder reads)."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    p = x * 100
    text = f"{abs(p):.1f}" if abs(p) < 10 else f"{abs(p):.0f}"
    if text in ("0.0", "0"):
        return "0%"
    sign = ("+" if p > 0 else "-") if signed else ("-" if p < 0 else "")
    return f"{sign}{text}%"


def fmt_ci(ci: Iterable[float] | None) -> str:
    if not ci:
        return "n/a"
    lo, hi = list(ci)
    return f"[{fmt_pct(lo)}, {fmt_pct(hi)}]"


def fmt_views(x: float | None) -> str:
    if x is None:
        return "n/a"
    if x >= 100:
        return f"{x:.0f}"
    if x >= 10:
        return f"{x:.0f}"
    return f"{x:.1f}"


def fmt_share(x: float | None) -> str:
    """Share of the edition's views per million, 3 significant digits."""
    if x is None:
        return "n/a"
    if x == 0:
        return "0"
    digits = max(0, 2 - int(math.floor(math.log10(abs(x)))))
    return f"{x:.{digits}f}"


def extract_numbers(text: str) -> list[dict]:
    """Return every number in `text` as {"raw", "value", "is_pct"} (value is the absolute number)."""
    out = []
    for m in _NUM_RE.finditer(text):
        sign, whole, frac, unit = m.groups()
        whole_digits = re.sub(r"[   ,]", "", whole)
        value = float(f"{whole_digits}.{frac}" if frac else whole_digits)
        out.append({"raw": m.group(0).strip(), "value": value, "is_pct": bool(unit)})
    return out


def _collect(obj, acc: list[float]) -> None:
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        if not (isinstance(obj, float) and math.isnan(obj)):
            acc.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect(v, acc)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _collect(v, acc)
    elif isinstance(obj, str):
        acc.extend(n["value"] for n in extract_numbers(obj))


def reference_values(sources: Iterable) -> set[float]:
    """All numbers a text is allowed to use: raw values, percentages and their rounded forms."""
    acc: list[float] = []
    for s in sources:
        if isinstance(s, str):
            try:
                _collect(json.loads(s), acc)
                continue
            except (json.JSONDecodeError, ValueError):
                pass
        _collect(s, acc)
    values: set[float] = set()
    for v in acc:
        for cand in (v, v * 100):  # fractions are also written as percentages
            a = abs(cand)
            values.update({a, round(a), round(a, 1), round(a, 2)})
    return values


def is_trivial(n: dict) -> bool:
    v = n["value"]
    if not n["is_pct"] and v.is_integer() and (_YEAR_MIN <= v <= _YEAR_MAX or v <= 12):
        return True  # years, list numbering, "12 months", "3 languages"
    return False


def matches(value: float, refs: set[float]) -> bool:
    for r in refs:
        if abs(value - r) <= max(0.051, 0.01 * abs(r)):  # rounding to 1 decimal or 1% relative
            return True
    return False


ALWAYS_ALLOWED = (95.0, 100.0, 1_000_000.0)  # "95% interval", "index 100", "per million"


def ungrounded_numbers(text: str, sources: Iterable, allow: Iterable[float] = ()) -> list[str]:
    """Numbers in `text` that do not appear (within rounding) in any of `sources`."""
    refs = reference_values(sources)
    refs.update(abs(float(a)) for a in allow)
    refs.update(ALWAYS_ALLOWED)
    bad = []
    for n in extract_numbers(text):
        if is_trivial(n) or matches(n["value"], refs):
            continue
        bad.append(n["raw"])
    return bad
