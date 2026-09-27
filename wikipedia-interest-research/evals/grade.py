#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf>=4"]
# ///
"""Grade eval runs: question-agnostic universal checks (U1–U8) plus an LLM judge that must quote evidence.

Examples:
  uv run evals/grade.py --set dev --iteration it1
  uv run evals/grade.py --set heldout --iteration heldout-1      # prints aggregates only
  uv run evals/grade.py --set dev --iteration it1 --no-judge     # automatic checks only
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

SKILL_NAME = "wikipedia-interest-research"
SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from wikiinterest.numbers import ungrounded_numbers  # noqa: E402

PRIVATE_DIR = Path(
    os.environ.get("WIKI_EVAL_PRIVATE", SKILL_DIR.parent.parent / f"{SKILL_DIR.parent.name}_private")
)
DEV_SET = SKILL_DIR / "evals" / "dev.jsonl"
HELDOUT_SET = PRIVATE_DIR / "heldout" / "heldout.jsonl"
DEFAULT_ROOT = PRIVATE_DIR / "eval-runs"
REPO_RESULTS = SKILL_DIR / "evals" / "results"

TRACE_LIMIT = 25_000  # chars of condensed trace given to the judge
WIKI_OUTPUT_LIMIT = 3000  # per wiki.py call: its output is the evidence for numbers
OTHER_OUTPUT_LIMIT = 800
UNIVERSAL = ("U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8")
UNIVERSAL_NAMES = {
    "U1": "used the skill", "U2": "no custom data code", "U3": "numbers grounded",
    "U4": "window + confidence stated", "U5": "assumptions/limitations", "U6": "no overclaiming",
    "U7": "artifacts valid", "U8": "answer in user's language",
}
_lock = threading.Lock()


def log(msg: str) -> None:
    with _lock:
        print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- loading


def load_labels(set_arg: str) -> tuple[dict[str, dict], str]:
    if set_arg == "dev":
        path, name = DEV_SET, "dev"
    elif set_arg == "heldout":
        path, name = HELDOUT_SET, "heldout"
    else:
        path = Path(set_arg).expanduser().resolve()
        name = f"custom:{path.stem}"
    if not path.exists():
        sys.exit(f"error: question set not found: {path}")
    labels = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            labels[item["id"]] = item
    return labels, name


def load_runs(it_dir: Path) -> list[dict]:
    runs = []
    for res_path in sorted(it_dir.glob("*/*/run*/result.json")):
        run_dir = res_path.parent
        try:
            result = json.loads(res_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        runs.append({"dir": run_dir, "result": result, "config": result.get("config"), "item_id": result.get("item_id")})
    return runs


def transcript_outputs(run_dir: Path) -> tuple[list[str], list[dict]]:
    """Full tool outputs (for grounding) and an ordered list of (call, output) for the judge trace."""
    outputs, steps, pending = [], [], {}
    path = run_dir / "transcript.jsonl"
    if not path.exists():
        return outputs, steps
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = ev.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        if ev.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    step = {"turn": ev.get("_turn", 0), "name": b.get("name"), "input": b.get("input") or {}, "output": ""}
                    pending[b.get("id")] = step
                    steps.append(step)
        elif ev.get("type") == "user" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c = b.get("content")
                    text = c if isinstance(c, str) else "\n".join(
                        x.get("text", "") for x in (c or []) if isinstance(x, dict) and x.get("type") == "text"
                    )
                    outputs.append(text)
                    step = pending.get(b.get("tool_use_id"))
                    if step is not None:
                        step["output"] = text
    return outputs, steps


# ---------------------------------------------------------------- automatic checks

INLINE_CODE = re.compile(
    r"\bpython[0-9.]*\s+(?:-[a-zA-Z]*c\b|-\s*<<|<<)|\bnode\s+-[ep]\b|\b(?:Rscript|perl|ruby)\s+-e\b"
)
CODE_FILE_REDIRECT = re.compile(r">>?\s*[^\s;|&]+\.(?:py|js|ts|sh|ipynb|r)\b", re.I)
MANUAL_MATH = re.compile(r"\bawk\b[^\n]*(?:\+=|\$\d+\s*[*/+-])|\|\s*bc\b")
FETCH = re.compile(r"\b(?:curl|wget)\b[^\n|;]*(?:wikimedia\.org|wikipedia\.org|wikidata\.org)", re.I)
PIP = re.compile(r"\b(?:pip3?|uv\s+pip)\s+install\b|\buv\s+add\b")
RUN_SCRIPT = re.compile(r"\b(?:python[0-9.]*|uv\s+run(?:\s+--?[\w-]+(?:[ =][^\s-][^\s]*)?)*)\s+([^\s;|&]+\.py)\b")
CODE_SUFFIXES = (".py", ".ipynb", ".js", ".ts", ".sh", ".r")
WIKI_DOMAINS = ("wikimedia.org", "wikipedia.org", "wikidata.org")


def is_skill_command(cmd: str) -> bool:
    return "scripts/wiki.py" in cmd


def check_u1(result: dict) -> bool:
    for c in result.get("tool_calls", []):
        inp = c.get("input") or {}
        if c.get("name") == "Bash" and is_skill_command(inp.get("command") or ""):
            return True
        if c.get("name") == "Skill" and SKILL_NAME in json.dumps(inp):
            return True
    return False


def check_u2(result: dict) -> tuple[bool, list[str]]:
    problems = []
    for c in result.get("tool_calls", []):
        inp = c.get("input") or {}
        name = c.get("name")
        if name == "Bash":
            cmd = inp.get("command") or ""
            if INLINE_CODE.search(cmd):
                problems.append(f"inline code: {cmd[:120]}")
            if CODE_FILE_REDIRECT.search(cmd):
                problems.append(f"wrote code via shell: {cmd[:120]}")
            if MANUAL_MATH.search(cmd):
                problems.append(f"manual computation: {cmd[:120]}")
            if FETCH.search(cmd):
                problems.append(f"direct API call: {cmd[:120]}")
            if PIP.search(cmd):
                problems.append(f"package install: {cmd[:120]}")
            for script in RUN_SCRIPT.findall(cmd):
                if not script.endswith("scripts/wiki.py") and "/evals/" not in script:
                    problems.append(f"ran own script: {script}")
        elif name in ("Write", "Edit"):
            path = (inp.get("file_path") or "").lower()
            if path.endswith(CODE_SUFFIXES):
                problems.append(f"wrote code file: {inp.get('file_path')}")
        elif name == "WebFetch" and any(d in json.dumps(inp) for d in WIKI_DOMAINS):
            problems.append(f"fetched Wikimedia directly: {json.dumps(inp)[:120]}")
    return (not problems), problems


def pdf_pages(path: Path) -> int | None:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(path)).pages)
    except Exception:
        return None


def check_u7(run_dir: Path, item: dict) -> tuple[bool | None, str]:
    wanted = set((item.get("expected") or {}).get("artifacts") or [])
    if not wanted:
        return None, "no artifacts requested"
    if (item.get("expected") or {}).get("must_clarify") and len(item.get("turns", [])) == 1:
        return None, "clarification required before artifacts"
    files = [p for base in (run_dir / "outputs", run_dir / "project") if base.exists()
             for p in base.rglob("*") if p.is_file() and ".claude" not in p.relative_to(base).parts]
    notes, ok = [], True
    if "pdf" in wanted:
        pdfs = [p for p in files if p.suffix.lower() == ".pdf"]
        pages = {p.name: pdf_pages(p) for p in pdfs}
        if not pdfs:
            ok = False
            notes.append("no PDF produced")
        elif any(n != 1 for n in pages.values()):
            ok = False
            notes.append(f"PDF pages: {pages}")
        else:
            notes.append(f"{len(pdfs)} PDF(s), 1 page each")
    if "chart" in wanted:
        pngs = [p for p in files if p.suffix.lower() in (".png", ".svg", ".jpg")]
        if not pngs:
            ok = False
            notes.append("no chart image produced")
        else:
            notes.append(f"{len(pngs)} chart image(s)")
    return ok, "; ".join(notes)


def auto_language(text: str, lang: str | None) -> bool | None:
    letters = [c for c in text if c.isalpha()]
    if not letters or lang not in ("uk", "en"):
        return None
    cyr = sum(1 for c in letters if "Ѐ" <= c <= "ӿ") / len(letters)
    return cyr > 0.5 if lang == "uk" else cyr < 0.2


CACHE_LINE = re.compile(r"hits\s*=\s*(\d+)[^\n]*?fetched\s*=\s*(\d+)")


def later_turn_fetches(steps: list[dict]) -> int | None:
    """C9 diagnostic: series fetched from the API in follow-up turns (skill logs `cache: hits=H fetched=F`)."""
    found, total = False, 0
    for s in steps:
        if s["turn"] > 0 and s["name"] == "Bash" and is_skill_command((s["input"] or {}).get("command") or ""):
            for m in CACHE_LINE.finditer(s["output"] or ""):
                found = True
                total += int(m.group(2))
    return total if found else None


def analysis_signature(run_dir: Path):
    """What the run concluded: (topic items, language, direction) from its latest results.json."""
    out = run_dir / "outputs"
    files = sorted(out.rglob("results.json"), key=lambda p: p.stat().st_mtime) if out.exists() else []
    if not files:
        return None
    try:
        res = json.loads(files[-1].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    topics = {}
    for t in (res.get("params") or {}).get("topics") or []:
        if isinstance(t, dict) and t.get("id"):
            items = t.get("items") or [*(t.get("qids") or []), *(t.get("titles") or [])]
            topics[t["id"]] = "+".join(sorted(str(x) for x in items)) or str(t.get("label", "")).lower()
    sig = []
    for s in res.get("series") or []:
        topic = topics.get(s.get("topic_id")) or str(s.get("topic_label", "")).lower()
        sig.append((topic, str(s.get("lang")), str((s.get("verdict") or {}).get("direction"))))
    return sorted(sig)


# ---------------------------------------------------------------- judge

RUBRIC = """You are a strict evaluator of an AI agent's answer. A founder of a B2C product asked the agent about
interest in topics on Wikipedia (pageview statistics). The agent may have used a skill whose commands look like
`scripts/wiki.py find|analyze|views|top|report`. Grade ONLY what the final answer(s) and the tool trace show.

Rules:
- Every PASS needs concrete evidence: quote the final answer (or a tool output) in `evidence`. No quote -> FAIL.
- A labeled behavior passes only if the answer really does it; a heading or a vague gesture is a FAIL.
- A labeled behavior may be treated as not applicable ONLY when the tool outputs prove it impossible or false
  (for example the label assumes an article is missing but the tool output shows it exists). Then set pass=true
  and start evidence with "N/A:" plus a quote from the tool output.
- clarification: if must_clarify is true, PASS only if the agent asked a clarifying question instead of presenting
  conclusions it could not justify. If clarify_acceptable is true, both asking and proceeding with an explicitly
  stated assumption pass. If both are false, PASS unless the agent stopped to ask instead of answering.
- window_and_confidence: applicable when the agent presented data-based conclusions; PASS if it states the time
  window of the data and a confidence / reliability level for its conclusion.
- limitations: PASS if the answer states at least one relevant assumption or limitation (e.g. Wikipedia views are
  informational interest, not purchase intent; a language edition is not a country; data gaps; low volume).
- no_overclaim: FAIL if the answer claims willingness to pay, revenue, market size in money, or country-level
  conclusions from language editions without a caveat.
- language_match: PASS if the final answer is written in the user's language (user_language); quoted article
  titles in other languages are fine.
- fabricated_numbers: count numbers in the final answer that state data facts (views, growth, shares, ranks,
  intervals) and do NOT appear in, and cannot be read directly off, the tool outputs. Numbers from the user's
  question, simple counts ("3 languages"), dates/years and methodology constants do not count. The flagged list is
  an automatic pre-filter: check each flagged number against the trace. For an out-of-scope or clarification answer
  with no data, count invented statistics as fabricated.
- answers_question: PASS if the final answer (last turn, in the context of the whole dialogue) directly addresses
  what the user asked, or, for requests that cannot be answered from Wikipedia data, clearly explains what cannot be
  answered and offers the closest measurable alternative.
- task_success = answers_question AND every behavior passes AND no forbidden item is violated AND clarification passes.

Return ONLY one JSON object (no prose, no code fence) with exactly these keys:
{"answers_question": {"pass": bool, "evidence": str},
 "behaviors": [{"text": str, "pass": bool, "evidence": str}],
 "forbidden": [{"text": str, "violated": bool, "evidence": str}],
 "clarification": {"pass": bool, "evidence": str},
 "window_and_confidence": {"pass": bool, "applicable": bool, "evidence": str},
 "limitations": {"pass": bool, "evidence": str},
 "no_overclaim": {"pass": bool, "evidence": str},
 "language_match": {"pass": bool, "evidence": str},
 "fabricated_numbers": {"count": int, "evidence": str},
 "task_success": bool}
"behaviors" and "forbidden" must contain one entry per labeled item, in the same order."""


def condensed_trace(steps: list[dict]) -> str:
    parts = []
    for s in steps:
        inp = s["input"] or {}
        if s["name"] == "Bash":
            head = inp.get("command", "")
        elif s["name"] in ("Read", "Write", "Edit"):
            head = inp.get("file_path", "")
        else:
            head = json.dumps(inp, ensure_ascii=False)[:300]
        limit = WIKI_OUTPUT_LIMIT if (s["name"] == "Bash" and is_skill_command(head)) else OTHER_OUTPUT_LIMIT
        out = (s["output"] or "").strip()
        if len(out) > limit:
            out = out[:limit] + f"\n...[{len(out) - limit} more chars]"
        parts.append(f"[turn {s['turn'] + 1}] {s['name']}: {head}\n-> {out}")
    text = "\n\n".join(parts)
    if len(text) <= TRACE_LIMIT:
        return text
    # keep the beginning (what was fetched) and the end (what was concluded)
    keep_head, keep_tail = [], []
    budget = TRACE_LIMIT // 2
    for p in parts:
        if sum(len(x) for x in keep_head) + len(p) > budget:
            break
        keep_head.append(p)
    for p in reversed(parts[len(keep_head):]):
        if sum(len(x) for x in keep_tail) + len(p) > budget:
            break
        keep_tail.insert(0, p)
    omitted = len(parts) - len(keep_head) - len(keep_tail)
    return "\n\n".join(keep_head + [f"... [{omitted} tool calls omitted] ..."] + keep_tail)


def build_judge_prompt(item: dict, result: dict, steps: list[dict], flagged: list[str]) -> str:
    exp = item.get("expected") or {}
    item_view = {
        "user_language": item.get("user_language"),
        "turns": item.get("turns"),
        "must_clarify": bool(exp.get("must_clarify")),
        "clarify_acceptable": bool(exp.get("clarify_acceptable")),
        "expected_behaviors": exp.get("behaviors") or [],
        "forbidden": exp.get("forbidden") or [],
        "artifacts_requested": exp.get("artifacts") or [],
        "acceptable_wikis": exp.get("wikis") or [],
        "grader_notes": item.get("notes") or "",
    }
    answers = "\n\n".join(
        f"--- final answer after user turn {t['turn'] + 1} ---\n{t.get('final_text') or '(no answer)'}"
        for t in result.get("turns", []) if "skipped" not in t
    )
    return (
        f"{RUBRIC}\n\n=== ITEM (labels) ===\n{json.dumps(item_view, ensure_ascii=False, indent=1)}"
        f"\n\n=== AGENT FINAL ANSWER(S) ===\n{answers}"
        f"\n\n=== TOOL TRACE (condensed) ===\n{condensed_trace(steps) or '(no tool calls)'}"
        f"\n\n=== NUMBERS FLAGGED AS NOT FOUND IN TOOL OUTPUTS (automatic pre-filter) ===\n{json.dumps(flagged, ensure_ascii=False)}"
        "\n\nReturn the JSON object now."
    )


def extract_json(text: str) -> dict | None:
    dec = json.JSONDecoder()
    fallback = None
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "task_success" in obj:
            return obj
        if fallback is None and isinstance(obj, dict) and len(obj) > 3:
            fallback = obj
    return fallback


def run_judge(prompt: str, model: str, timeout: float) -> tuple[dict | None, str]:
    last_err = ""
    for attempt in range(2):
        text = prompt if attempt == 0 else prompt + "\n\nYour previous reply was not a valid JSON object. Reply with ONLY the JSON object."
        with tempfile.TemporaryDirectory(prefix="judge-") as tmp:
            try:
                proc = subprocess.run(
                    ["claude", "-p", "--model", model, "--output-format", "json",
                     "--setting-sources", "project", "--max-turns", "3"],
                    input=text, capture_output=True, text=True, encoding="utf-8", errors="replace",
                    cwd=tmp, timeout=timeout,
                )
            except subprocess.TimeoutExpired:
                last_err = "judge timeout"
                continue
        try:
            outer = json.loads(proc.stdout)
            reply = outer.get("result") or ""
        except json.JSONDecodeError:
            reply = proc.stdout
        verdict = extract_json(reply)
        if verdict is not None:
            return verdict, ""
        last_err = f"unparseable judge reply: {reply[:300]!r} {proc.stderr[-300:]!r}"
    return None, last_err


def normalize_judge(v: dict, item: dict) -> dict:
    def part(key):
        x = v.get(key)
        return x if isinstance(x, dict) else {"pass": False, "evidence": "missing in judge output"}
    exp = item.get("expected") or {}
    behaviors = v.get("behaviors") if isinstance(v.get("behaviors"), list) else []
    forbidden = v.get("forbidden") if isinstance(v.get("forbidden"), list) else []
    n_beh, n_forb = len(exp.get("behaviors") or []), len(exp.get("forbidden") or [])
    behaviors = (behaviors + [{"text": "(missing)", "pass": False, "evidence": "not graded"}] * n_beh)[:n_beh]
    forbidden = (forbidden + [{"text": "(missing)", "violated": False, "evidence": "not graded"}] * n_forb)[:n_forb]
    out = {
        "answers_question": part("answers_question"),
        "behaviors": behaviors,
        "forbidden": forbidden,
        "clarification": part("clarification"),
        "window_and_confidence": part("window_and_confidence"),
        "limitations": part("limitations"),
        "no_overclaim": part("no_overclaim"),
        "language_match": part("language_match"),
        "fabricated_numbers": v.get("fabricated_numbers") if isinstance(v.get("fabricated_numbers"), dict) else {"count": 0, "evidence": ""},
        "task_success_judge": bool(v.get("task_success")),
    }
    try:
        out["fabricated_numbers"]["count"] = int(out["fabricated_numbers"].get("count") or 0)
    except (TypeError, ValueError):
        out["fabricated_numbers"]["count"] = 0
    # recompute from the parts so a self-contradicting judge cannot inflate success
    out["task_success"] = bool(
        out["answers_question"].get("pass")
        and all(b.get("pass") for b in behaviors)
        and not any(f.get("violated") for f in forbidden)
        and out["clarification"].get("pass")
    )
    return out


# ---------------------------------------------------------------- grading one run


def grade_run(run: dict, labels: dict, args) -> dict:
    run_dir, result = run["dir"], run["result"]
    cached = run_dir / "grade.json"
    if cached.exists() and not args.force:
        g = json.loads(cached.read_text(encoding="utf-8"))
        if args.no_judge or g.get("judge") is not None:
            return g
    item = labels.get(run["item_id"])
    if item is None:
        return {"item_id": run["item_id"], "config": run["config"], "error": "no label for this item"}
    outputs, steps = transcript_outputs(run_dir)
    turns = [t for t in result.get("turns", []) if "skipped" not in t]
    final = turns[-1].get("final_text", "") if turns else ""
    user_texts = [t for t in item.get("turns", [])]
    flagged = ungrounded_numbers(final, outputs + user_texts)
    u2_ok, u2_problems = check_u2(result)
    u7, u7_note = check_u7(run_dir, item)
    g = {
        "item_id": run["item_id"], "config": run["config"], "run": result.get("run"),
        "run_dir": str(run_dir),
        "U1": check_u1(result) if run["config"] == "skill" else None,
        "U2": u2_ok, "U2_problems": u2_problems,
        "U3_auto": not flagged, "U3_flagged": flagged,
        "U7": u7, "U7_note": u7_note,
        "U8_auto": auto_language(final, item.get("user_language")),
        "tool_calls": len(result.get("tool_calls", [])),
        "wall_s": (result.get("totals") or {}).get("wall_s"),
        "duration_ms": (result.get("totals") or {}).get("duration_ms"),
        "cost_usd": (result.get("totals") or {}).get("total_cost_usd"),
        "timed_out": (result.get("totals") or {}).get("timed_out"),
        "turns_expected": len(item.get("turns", [])),
        "turns_answered": len(turns),
        "later_turn_fetches": later_turn_fetches(steps),
        "leaks": result.get("leaks", []),
        "judge": None,
    }
    if not args.no_judge:
        verdict, err = run_judge(build_judge_prompt(item, result, steps, flagged), args.judge_model, args.judge_timeout)
        g["judge"] = normalize_judge(verdict, item) if verdict else None
        g["judge_error"] = err or None
    j = g["judge"]
    g["U3"] = g["U3_auto"] or (j is not None and j["fabricated_numbers"]["count"] == 0)
    if j:
        wc = j["window_and_confidence"]
        g["U4"] = bool(wc.get("pass")) if wc.get("applicable", True) else None
        g["U5"] = bool(j["limitations"].get("pass"))
        g["U6"] = bool(j["no_overclaim"].get("pass"))
        g["U8"] = bool(j["language_match"].get("pass"))
        g["task_success"] = j["task_success"]
        g["fabricated"] = j["fabricated_numbers"]["count"]
    else:
        g["U4"] = g["U5"] = g["U6"] = None
        g["U8"] = g["U8_auto"]
        g["task_success"] = None
        g["fabricated"] = None
    checks = [g[u] for u in UNIVERSAL if not (u in ("U1", "U2") and run["config"] == "noskill")]
    if j is None and not args.no_judge:
        g["all_universal"] = None  # judge failed: undecided rather than silently passed
    else:
        g["all_universal"] = all(c is not False for c in checks)  # None = not applicable / not judged
    if g["turns_answered"] < g["turns_expected"] or g["timed_out"]:
        g["all_universal"] = False
        g["task_success"] = False if g["task_success"] is not None else None
    cached.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
    return g


# ---------------------------------------------------------------- aggregation


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def rate(values: list) -> dict:
    vals = [v for v in values if v is not None]
    k, n = sum(1 for v in vals if v), len(vals)
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": (k / n) if n else None, "ci": [lo, hi] if n else None}


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{100 * x:.0f}%"


def fmt_rate(r: dict, ci: bool = True) -> str:
    if not r["n"]:
        return "n/a"
    s = f"{pct(r['rate'])} ({r['k']}/{r['n']})"
    if ci and r["ci"]:
        s += f" [{pct(r['ci'][0])}–{pct(r['ci'][1])}]"
    return s


def p90(values: list[float]) -> float | None:
    vals = sorted(v for v in values if v is not None)
    return vals[max(0, math.ceil(0.9 * len(vals)) - 1)] if vals else None


def median(values: list) -> float | None:
    vals = [v for v in values if v is not None]
    return statistics.median(vals) if vals else None


def aggregate(grades: list[dict], labels: dict) -> dict:
    agg = {}
    for config in sorted({g["config"] for g in grades}):
        gs = [g for g in grades if g["config"] == config and "error" not in g]
        single = [g for g in gs if g["turns_expected"] == 1]
        by_item: dict[str, list[dict]] = {}
        for g in gs:
            by_item.setdefault(g["item_id"], []).append(g)
        stable = []
        for item_id, lst in by_item.items():
            if len(lst) < 2:
                continue
            sigs = [analysis_signature(Path(g["run_dir"])) for g in lst]
            if all(s is not None for s in sigs):
                stable.append(all(s == sigs[0] for s in sigs))
            else:
                stable.append(len({g["task_success"] for g in lst}) == 1)
        scoped = [g for g in gs if ((labels.get(g["item_id"]) or {}).get("taxonomy") or {}).get("scope") in ("partial", "out")]
        dialogues = [g for g in gs if g["turns_expected"] > 1]
        agg[config] = {
            "runs": len(gs),
            "items": len(by_item),
            "all_universal": rate([g["all_universal"] for g in gs]),
            "task_success": rate([g["task_success"] for g in gs]),
            "universal": {u: rate([g.get(u) for g in gs]) for u in UNIVERSAL},
            "fabricated_total": sum(g["fabricated"] or 0 for g in gs) if any(g["fabricated"] is not None for g in gs) else None,
            "runs_with_flagged_numbers": sum(1 for g in gs if g["U3_flagged"]),
            "timeouts": sum(1 for g in gs if g["timed_out"]),
            "contact_leaks": sum(len(g.get("leaks") or []) for g in gs),
            "tool_calls_median": median([g["tool_calls"] for g in gs]),
            "tool_calls_p90": p90([g["tool_calls"] for g in gs]),
            "single_turn_tool_calls_median": median([g["tool_calls"] for g in single]),
            "single_turn_minutes_median": (median([g["wall_s"] for g in single]) or 0) / 60 if single else None,
            "wall_s_median": median([g["wall_s"] for g in gs]),
            "cost_usd_median": median([g["cost_usd"] for g in gs]),
            "stability": rate(stable),
            "partial_out_scope_success": rate([g["task_success"] for g in scoped]),
            "dialogue_later_turn_fetches": [g["later_turn_fetches"] for g in dialogues],
        }
        slices = {}
        for field in ("intent", "coverage_trap", "scope"):
            groups: dict[str, list[dict]] = {}
            for g in gs:
                val = ((labels.get(g["item_id"]) or {}).get("taxonomy") or {}).get(field)
                if val is not None:
                    groups.setdefault(str(val), []).append(g)
            if groups:
                slices[field] = {k: {"task_success": rate([x["task_success"] for x in v]),
                                     "all_universal": rate([x["all_universal"] for x in v])} for k, v in sorted(groups.items())}
        groups = {}
        for g in gs:
            for s in ((labels.get(g["item_id"]) or {}).get("taxonomy") or {}).get("scripts") or []:
                groups.setdefault(str(s), []).append(g)
        if groups:
            slices["scripts"] = {k: {"task_success": rate([x["task_success"] for x in v]),
                                     "all_universal": rate([x["all_universal"] for x in v])} for k, v in sorted(groups.items())}
        groups = {}
        for g in gs:
            lang = (labels.get(g["item_id"]) or {}).get("user_language")
            if lang:
                groups.setdefault(str(lang), []).append(g)
        if groups:
            slices["user_language"] = {k: {"task_success": rate([x["task_success"] for x in v]),
                                           "all_universal": rate([x["all_universal"] for x in v])} for k, v in sorted(groups.items())}
        agg[config]["slices"] = slices
    if "skill" in agg and "noskill" in agg:
        common = {g["item_id"] for g in grades if g["config"] == "skill"} & {g["item_id"] for g in grades if g["config"] == "noskill"}
        def on_common(config, key):
            return rate([g[key] for g in grades if g["config"] == config and g["item_id"] in common and "error" not in g])
        agg["delta"] = {
            "common_items": len(common),
            "task_success": {"skill": on_common("skill", "task_success"), "noskill": on_common("noskill", "task_success")},
            "all_universal": {"skill": on_common("skill", "all_universal"), "noskill": on_common("noskill", "all_universal")},
            "U3": {"skill": on_common("skill", "U3"), "noskill": on_common("noskill", "U3")},
        }
    return agg


def render_markdown(iteration: str, set_name: str, agg: dict, grades: list[dict], labels: dict, per_item: bool, judge_model: str | None) -> str:
    lines = [
        f"# Eval results: `{iteration}` ({set_name})",
        "",
        f"Graded {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}; judge: {judge_model or 'none (automatic checks only)'}.",
        "Rates show k/n and a 95% Wilson interval. `noskill` excludes U1/U2 from the universal composite.",
        "",
        "## Summary",
        "",
        "| config | runs | all universal checks | task success | fabricated numbers | median tool calls (p90) | median time | median cost |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for config, a in agg.items():
        if config == "delta":
            continue
        mt = f"{a['wall_s_median'] / 60:.1f} min" if a["wall_s_median"] else "n/a"
        mc = f"${a['cost_usd_median']:.3f}" if a["cost_usd_median"] is not None else "n/a"
        tc = f"{a['tool_calls_median']:.0f} ({a['tool_calls_p90']:.0f})" if a["tool_calls_median"] is not None else "n/a"
        fab = "n/a" if a["fabricated_total"] is None else str(a["fabricated_total"])
        lines.append(f"| {config} | {a['runs']} | {fmt_rate(a['all_universal'])} | {fmt_rate(a['task_success'])} | {fab} | {tc} | {mt} | {mc} |")
    lines += ["", "## Universal checks", "", "| check | " + " | ".join(c for c in agg if c != "delta") + " |",
              "|---|" + "---|" * len([c for c in agg if c != "delta"])]
    for u in UNIVERSAL:
        row = [fmt_rate(agg[c]["universal"][u], ci=False) for c in agg if c != "delta"]
        lines.append(f"| {u} {UNIVERSAL_NAMES[u]} | " + " | ".join(row) + " |")
    lines += ["", "## Other criteria", ""]
    for config, a in agg.items():
        if config == "delta":
            continue
        st = a["single_turn_minutes_median"]
        lines += [
            f"**{config}**: stability (items with ≥2 runs) {fmt_rate(a['stability'])}; "
            f"partial/out-of-scope success {fmt_rate(a['partial_out_scope_success'])}; "
            f"single-turn median tool calls {a['single_turn_tool_calls_median'] if a['single_turn_tool_calls_median'] is not None else 'n/a'}, "
            f"median time {f'{st:.1f} min' if st is not None else 'n/a'}; "
            f"runs with flagged numbers {a['runs_with_flagged_numbers']}; timeouts {a['timeouts']}; contact leaks {a['contact_leaks']}; "
            f"API fetches in follow-up turns {a['dialogue_later_turn_fetches'] or 'n/a'}.",
            "",
        ]
    if "delta" in agg:
        d = agg["delta"]
        lines += [f"## Skill vs no skill ({d['common_items']} common items)", "",
                  "| metric | skill | no skill |", "|---|---|---|"]
        for key in ("task_success", "all_universal", "U3"):
            lines.append(f"| {key} | {fmt_rate(d[key]['skill'])} | {fmt_rate(d[key]['noskill'])} |")
        lines.append("")
    for config, a in agg.items():
        if config == "delta" or not a["slices"]:
            continue
        lines += [f"## Slices ({config}; diagnostic, small n)", "", "| slice | value | task success | all universal |", "|---|---|---|---|"]
        for field, groups in a["slices"].items():
            for val, r in groups.items():
                lines.append(f"| {field} | {val} | {fmt_rate(r['task_success'], ci=False)} | {fmt_rate(r['all_universal'], ci=False)} |")
        lines.append("")
    if per_item:
        lines += ["## Per run", "", "| item | config | run | U1 | U2 | U3 | U4 | U5 | U6 | U7 | U8 | success | tools | flagged numbers / problems |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        mark = {True: "✓", False: "✗", None: "–"}
        for g in sorted(grades, key=lambda x: (x["item_id"], x["config"], x.get("run") or 0)):
            if "error" in g:
                lines.append(f"| {g['item_id']} | {g['config']} | | | | | | | | | | | | {g['error']} |")
                continue
            notes = ", ".join(g["U3_flagged"][:6]) + (("; " + "; ".join(g["U2_problems"][:2])) if g["U2_problems"] else "")
            if g.get("judge_error"):
                notes += f"; judge error: {g['judge_error'][:80]}"
            cells = [mark[g.get(u)] for u in UNIVERSAL]
            lines.append(f"| {g['item_id']} | {g['config']} | {g.get('run')} | " + " | ".join(cells)
                         + f" | {mark[g['task_success']]} | {g['tool_calls']} | {notes.replace('|', '/')} |")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", required=True, help="dev | heldout | path/to/set.jsonl (labels)")
    ap.add_argument("--iteration", required=True)
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--judge-model", default="sonnet")
    ap.add_argument("--judge-timeout", type=float, default=300)
    ap.add_argument("--no-judge", action="store_true", help="automatic checks only")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--force", action="store_true", help="re-grade runs that already have grade.json")
    args = ap.parse_args()

    labels, set_name = load_labels(args.set)
    heldout = set_name == "heldout"
    it_dir = Path(args.root).expanduser().resolve() / args.iteration
    runs = load_runs(it_dir)
    if not runs:
        sys.exit(f"error: no runs found under {it_dir}")
    log(f"grading {len(runs)} runs ({set_name}), judge: {'off' if args.no_judge else args.judge_model}")
    grades = []
    with cf.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(grade_run, r, labels, args) for r in runs]
        for n, fut in enumerate(cf.as_completed(futures), 1):
            g = fut.result()
            grades.append(g)
            if heldout:
                log(f"[{n}/{len(runs)}] graded")
            else:
                log(f"[{n}/{len(runs)}] {g['item_id']} {g['config']} run{g.get('run')}: "
                    f"success={g.get('task_success')} universal={g.get('all_universal')} flagged={len(g.get('U3_flagged') or [])}")
    agg = aggregate(grades, labels)
    judge_model = None if args.no_judge else args.judge_model
    (it_dir / "grades.json").write_text(json.dumps({"set": set_name, "iteration": args.iteration, "aggregate": agg, "grades": grades},
                                                   ensure_ascii=False, indent=2), encoding="utf-8")
    full_md = render_markdown(args.iteration, set_name, agg, grades, labels, per_item=True, judge_model=judge_model)
    (it_dir / "summary.md").write_text(full_md, encoding="utf-8")
    public_md = render_markdown(args.iteration, set_name, agg, grades, labels, per_item=not heldout, judge_model=judge_model)
    if heldout:
        # the held-out set has no taxonomy; drop any slice that could hint at item content
        public_md = public_md.split("## Slices")[0].rstrip() + "\n"
    if set_name in ("dev", "heldout"):
        REPO_RESULTS.mkdir(parents=True, exist_ok=True)
        (REPO_RESULTS / f"{args.iteration}.md").write_text(public_md, encoding="utf-8")
        log(f"wrote {REPO_RESULTS / (args.iteration + '.md')}")
    print(public_md)
    log(f"full results: {it_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
