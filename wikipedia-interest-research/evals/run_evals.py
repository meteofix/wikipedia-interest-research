#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Run eval question sets against a headless Claude Code agent (default model: Claude Haiku 4.5).

Every item x run gets its own project directory. In the `skill` config only the runtime part of
the skill (SKILL.md, scripts/, references/, assets/) is installed into the project, so the agent
never sees eval labels, tests or docs. Transcripts are stored with the Wikimedia contact redacted.

Examples:
  uv run evals/run_evals.py --set dev --iteration it1
  uv run evals/run_evals.py --set dev --no-skill --limit 15 --iteration baseline
  uv run evals/run_evals.py --set heldout --runs 2 --iteration heldout-1
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

SKILL_NAME = "wikipedia-interest-research"
SKILL_DIR = Path(__file__).resolve().parents[1]
# Private data (held-out set, raw transcripts) lives next to the repo, never inside it.
PRIVATE_DIR = Path(
    os.environ.get("WIKI_EVAL_PRIVATE", SKILL_DIR.parent.parent / f"{SKILL_DIR.parent.name}_private")
)
DEV_SET = SKILL_DIR / "evals" / "dev.jsonl"
HELDOUT_SET = PRIVATE_DIR / "heldout" / "heldout.jsonl"
DEFAULT_ROOT = PRIVATE_DIR / "eval-runs"

RUNTIME_PARTS = ("SKILL.md", "scripts", "references", "assets")
ALLOWED_TOOLS = ("Bash", "Read", "Write", "Edit", "Glob", "Grep", "Skill")
# result.json keeps a readable excerpt of each tool output; the full events stay in transcript.jsonl.
OUTPUT_LIMIT = 4000
# Wikimedia allows ~200 requests/min for an identified client; 3 req/s is split across parallel agents.
TOTAL_RPS = 3.0
TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".txt", ".csv", ".html", ".svg", ".log"}
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", ".pytest_cache")

_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- inputs


def load_items(set_arg: str) -> tuple[list[dict], str]:
    if set_arg == "dev":
        path, name = DEV_SET, "dev"
    elif set_arg == "heldout":
        path, name = HELDOUT_SET, "heldout"
    else:
        path = Path(set_arg).expanduser().resolve()
        name = f"custom:{path.stem}"
    if not path.exists():
        sys.exit(f"error: question set not found: {path}")
    items = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            sys.exit(f"error: {path.name} line {n} is not valid JSON ({e})")
        if not item.get("id") or not item.get("turns"):
            sys.exit(f"error: {path.name} line {n} needs 'id' and 'turns'")
        items.append(item)
    return items, name


def read_contact() -> str:
    """Wikimedia User-Agent contact: env var first, else the export line in ~/.zshrc."""
    value = os.environ.get("WIKI_CONTACT", "").strip()
    if value:
        return value
    try:
        for line in (Path.home() / ".zshrc").read_text(errors="ignore").splitlines():
            m = re.match(r'^\s*export\s+WIKI_CONTACT="(.*)"\s*$', line)
            if m:
                return m.group(1).strip()
    except OSError:
        pass
    return ""


def snapshot_hash() -> str:
    """Hash of the runtime skill files, so every run records which skill version it evaluated."""
    h = hashlib.sha256()
    for part in RUNTIME_PARTS:
        src = SKILL_DIR / part
        if src.is_file():
            files = [src]
        elif src.is_dir():
            files = sorted(
                p for p in src.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
            )
        else:
            files = []
        for f in files:
            h.update(str(f.relative_to(SKILL_DIR)).encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:12]


def git_head() -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(SKILL_DIR), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


# ---------------------------------------------------------------- run one agent turn


def install_skill(project: Path) -> None:
    dest = project / ".claude" / "skills" / SKILL_NAME
    dest.mkdir(parents=True, exist_ok=True)
    for part in RUNTIME_PARTS:
        src = SKILL_DIR / part
        if src.is_dir():
            shutil.copytree(src, dest / part, ignore=IGNORE, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, dest / part)


def run_process(cmd: list[str], cwd: Path, env: dict, timeout: float) -> tuple[str, str, int | None, bool, float]:
    t0 = time.monotonic()
    proc = subprocess.Popen(
        cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", start_new_session=True,
    )
    timed_out = False
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        for sig, wait in ((signal.SIGTERM, 15), (signal.SIGKILL, None)):
            try:
                os.killpg(proc.pid, sig)
            except ProcessLookupError:
                pass
            try:
                out, err = proc.communicate(timeout=wait)
                break
            except subprocess.TimeoutExpired:
                continue
    return out or "", err or "", proc.returncode, timed_out, time.monotonic() - t0


def tool_result_text(block: dict) -> str:
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


def compact_input(name: str, inp: dict) -> dict:
    if name == "Bash":
        return {"command": inp.get("command", ""), "description": inp.get("description")}
    if name == "Write":
        content = inp.get("content") or ""
        return {"file_path": inp.get("file_path"), "content_len": len(content), "content_head": content[:400]}
    if name == "Edit":
        return {"file_path": inp.get("file_path"), "new_head": (inp.get("new_string") or "")[:300]}
    if name == "Read":
        return {k: inp.get(k) for k in ("file_path", "offset", "limit") if inp.get(k) is not None}
    text = json.dumps(inp, ensure_ascii=False)
    return inp if len(text) <= 1000 else {"truncated": text[:1000]}


def parse_events(lines: list[str], turn: int) -> dict:
    events, calls, texts = [], [], []
    pending: dict[str, dict] = {}
    result = None
    session_id = model = None
    for line in lines:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(ev, dict):
            continue
        ev["_turn"] = turn
        events.append(ev)
        kind = ev.get("type")
        if kind == "system" and ev.get("subtype") == "init":
            session_id = ev.get("session_id") or session_id
            model = ev.get("model") or model
        elif kind == "assistant":
            msg = ev.get("message")
            for block in (msg.get("content") if isinstance(msg, dict) else None) or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    call = {
                        "turn": turn, "id": block.get("id"), "name": block.get("name"),
                        "input": compact_input(block.get("name") or "", block.get("input") or {}),
                        "output": "", "is_error": None,
                    }
                    pending[block.get("id")] = call
                    calls.append(call)
                elif block.get("type") == "text" and block.get("text"):
                    texts.append(block["text"])
        elif kind == "user":
            msg = ev.get("message")
            content = msg.get("content") if isinstance(msg, dict) else None
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        call = pending.get(block.get("tool_use_id"))
                        if call is not None:
                            call["output"] = tool_result_text(block)[:OUTPUT_LIMIT]
                            call["is_error"] = bool(block.get("is_error"))
        elif kind == "result":
            result = ev
            session_id = ev.get("session_id") or session_id
    final_text = (result or {}).get("result")
    if final_text is None:
        final_text = texts[-1] if texts else ""
    return {
        "events": events, "calls": calls, "result": result or {},
        "session_id": session_id, "model": model, "final_text": final_text,
    }


def list_files(run_dir: Path) -> list[dict]:
    found = []
    for base in (run_dir / "outputs", run_dir / "project"):
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            rel = p.relative_to(base)
            if not p.is_file() or ".claude" in rel.parts:
                continue
            if p.suffix.lower() in {".pdf", ".png", ".jpg", ".svg", ".json", ".md", ".csv", ".txt", ".html"}:
                found.append({"path": str(p.relative_to(run_dir)), "bytes": p.stat().st_size})
    return found


def scrub_leaks(run_dir: Path, secret: str) -> list[str]:
    """Find files the agent/skill produced that contain the contact; redact text files in place."""
    if not secret:
        return []
    needle = secret.encode()
    leaks = []
    for p in run_dir.rglob("*"):
        if not p.is_file() or {".claude"} & set(p.relative_to(run_dir).parts):
            continue
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if needle in data:
            leaks.append(str(p.relative_to(run_dir)))
            if p.suffix.lower() in TEXT_SUFFIXES:
                p.write_bytes(data.replace(needle, b"<contact>"))
    return leaks


def run_item(item: dict, k: int, ctx: dict) -> dict:
    args, secret = ctx["args"], ctx["secret"]
    redact = (lambda s: s.replace(secret, "<contact>")) if secret else (lambda s: s)
    run_dir = ctx["config_dir"] / item["id"] / f"run{k}"
    if (run_dir / "result.json").exists() and not args.force:
        return {"status": "skipped", "item": item["id"], "run": k}
    if run_dir.exists():
        shutil.rmtree(run_dir)
    project = run_dir / "project"
    outputs = run_dir / "outputs"
    project.mkdir(parents=True)
    outputs.mkdir()
    if ctx["config"] == "skill":
        install_skill(project)

    env = dict(os.environ)
    if secret:
        env["WIKI_CONTACT"] = secret
    env["WIKI_INTEREST_CACHE"] = str(ctx["cache_path"])
    env["WIKI_INTEREST_OUT"] = str(outputs)
    env["WIKI_MAX_RPS"] = f"{TOTAL_RPS / max(1, args.parallel):.3f}"

    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    turns, calls, all_events = [], [], []
    session_id = None
    for t, prompt in enumerate(item["turns"]):
        cmd = [
            ctx["claude"], "-p", prompt, "--model", args.model,
            "--output-format", "stream-json", "--verbose",
            "--setting-sources", "project",
            "--max-turns", str(args.max_turns),
            "--allowedTools", *ALLOWED_TOOLS,
        ]
        if t > 0:
            if not session_id:
                turns.append({"turn": t, "prompt": prompt, "skipped": "no session to resume"})
                continue
            cmd[3:3] = ["--resume", session_id]
        out, err, code, timed_out, wall = run_process(cmd, project, env, args.timeout)
        parsed = parse_events([ln for ln in out.splitlines() if ln.strip()], t)
        all_events.extend(parsed["events"])
        calls.extend(parsed["calls"])
        session_id = parsed["session_id"] or session_id
        r = parsed["result"]
        turns.append({
            "turn": t, "prompt": prompt, "final_text": parsed["final_text"],
            "session_id": parsed["session_id"], "model": parsed["model"],
            "num_turns": r.get("num_turns"), "duration_ms": r.get("duration_ms"),
            "total_cost_usd": r.get("total_cost_usd"), "usage": r.get("usage"),
            "is_error": r.get("is_error"), "subtype": r.get("subtype"),
            "exit_code": code, "timed_out": timed_out, "wall_s": round(wall, 1),
            "stderr_tail": err[-2000:],
        })
        if timed_out or not parsed["session_id"]:
            break  # a broken turn makes later turns meaningless

    finished = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with (run_dir / "transcript.jsonl").open("w", encoding="utf-8") as fh:
        for ev in all_events:
            fh.write(redact(json.dumps(ev, ensure_ascii=False)) + "\n")
    leaks = scrub_leaks(run_dir, secret)
    done_turns = [t for t in turns if "skipped" not in t]
    result = {
        "item_id": item["id"], "set": ctx["set_name"], "config": ctx["config"], "model": args.model,
        "run": k, "iteration": args.iteration, "skill_snapshot": ctx["snapshot"], "git_head": ctx["git_head"],
        "started_at": started, "finished_at": finished,
        "turns": turns, "tool_calls": calls,
        "totals": {
            "turns_sent": len(done_turns),
            "turns_expected": len(item["turns"]),
            "num_turns": sum(t.get("num_turns") or 0 for t in done_turns),
            "duration_ms": sum(t.get("duration_ms") or 0 for t in done_turns),
            "wall_s": round(sum(t.get("wall_s") or 0 for t in done_turns), 1),
            "total_cost_usd": round(sum(t.get("total_cost_usd") or 0 for t in done_turns), 5),
            "tool_calls": len(calls),
            "timed_out": any(t.get("timed_out") for t in done_turns),
            "errors": sum(1 for t in done_turns if t.get("is_error") or t.get("exit_code") not in (0, None)),
        },
        "files": list_files(run_dir),
        "leaks": leaks,
    }
    (run_dir / "result.json").write_text(redact(json.dumps(result, ensure_ascii=False, indent=2)), encoding="utf-8")
    status = "timeout" if result["totals"]["timed_out"] else ("error" if result["totals"]["errors"] else "ok")
    return {
        "status": status, "item": item["id"], "run": k, "wall": result["totals"]["wall_s"],
        "tools": len(calls), "leaks": len(leaks),
    }


# ---------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", required=True, help="dev | heldout | path/to/set.jsonl")
    ap.add_argument("--iteration", required=True, help="name of this eval iteration (directory name)")
    ap.add_argument("--ids", help="comma-separated item ids to run")
    ap.add_argument("--limit", type=int, help="run only the first N items (after --ids filtering)")
    ap.add_argument("--runs", type=int, default=1, help="runs per item (default 1)")
    ap.add_argument("--model", default="haiku", help="agent model alias or id (default haiku)")
    ap.add_argument("--parallel", type=int, default=4, help="concurrent agents (default 4)")
    ap.add_argument("--no-skill", action="store_true", help="baseline: run without the skill installed")
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help=f"runs root (default {DEFAULT_ROOT})")
    ap.add_argument("--timeout", type=float, default=600, help="seconds per user turn (default 600)")
    ap.add_argument("--max-turns", type=int, default=40, help="agent turns per user turn (default 40)")
    ap.add_argument("--force", action="store_true", help="re-run items that already have result.json")
    args = ap.parse_args()

    claude = shutil.which("claude")
    if not claude:
        sys.exit("error: the `claude` CLI is not on PATH")
    items, set_name = load_items(args.set)
    heldout = set_name == "heldout"
    if args.ids:
        wanted = {i.strip() for i in args.ids.split(",") if i.strip()}
        items = [it for it in items if it["id"] in wanted]
    if args.limit:
        items = items[: args.limit]
    if not items:
        sys.exit("error: no items selected")

    config = "noskill" if args.no_skill else "skill"
    root = Path(args.root).expanduser().resolve()
    it_dir = root / args.iteration
    config_dir = it_dir / config
    config_dir.mkdir(parents=True, exist_ok=True)
    secret = read_contact()
    if not secret:
        log("warning: WIKI_CONTACT not found; Wikimedia limits clients without contact info to ~10 requests/min")

    ctx = {
        "args": args, "secret": secret, "config": config, "config_dir": config_dir, "set_name": set_name,
        "cache_path": root / "cache.sqlite", "claude": claude,
        "snapshot": snapshot_hash() if config == "skill" else None, "git_head": git_head(),
    }
    meta_path = it_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"iteration": args.iteration, "set": set_name, "runs": []}
    meta["runs"].append({
        "config": config, "model": args.model, "runs_per_item": args.runs, "items": len(items),
        "parallel": args.parallel, "skill_snapshot": ctx["snapshot"], "git_head": ctx["git_head"],
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    meta_path.write_text(json.dumps(meta, indent=2))

    tasks = [(it, k) for it in items for k in range(1, args.runs + 1)]
    total = len(tasks)
    counts: dict[str, int] = {}
    leaks = 0
    log(f"{set_name} / {config}: {len(items)} items x {args.runs} runs = {total} runs, parallel {args.parallel}, model {args.model}")
    with cf.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(run_item, it, k, ctx) for it, k in tasks]
        for n, fut in enumerate(cf.as_completed(futures), 1):
            try:
                res = fut.result()
            except Exception as e:  # keep the batch going; the failure is reported in the counts
                res = {"status": "crash", "item": "?", "run": 0, "error": repr(e)}
            counts[res["status"]] = counts.get(res["status"], 0) + 1
            leaks += res.get("leaks", 0)
            if heldout:
                log(f"[{n}/{total}] {res['status']}")
            else:
                extra = f" ({res.get('wall', 0):.0f}s, {res.get('tools', 0)} tool calls)" if res["status"] != "skipped" else ""
                err = f" {res.get('error')}" if res["status"] == "crash" else ""
                log(f"[{n}/{total}] {res['item']} run{res['run']}: {res['status']}{extra}{err}")
    summary = {"set": set_name, "config": config, "runs": total, **counts, "contact_leaks": leaks, "dir": str(config_dir)}
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
