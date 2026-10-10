#!/usr/bin/env python3
"""Bounded, metadata-only evidence discovery. Never opens source file contents.

Private inventory, NOT animation events: directory names are navigation, and mtime
is a discovery hint, never the time at which work happened. Remote workers run this
same file via stdin; all output is written by the local orchestrator.
"""
import argparse
import collections
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

SKIP = {".git", "node_modules", "models", "model", "checkpoints", "venvs", ".venv", "venv",
        ".cache", "__pycache__", "site-packages", "SteamLibrary", "Windows", "Program Files",
        "Program Files (x86)", "$RECYCLE.BIN", "System Volume Information", "Recovery",
        ".pnpm-store", "pip-cache", "browser", "browser_profiles", "extensions", "_retail_"}
CREDENTIAL = re.compile(r"(^\.env|credential|secret|token|(^|[._-])auth([._-]|$)|callers\.json|"
                        r"^id_(rsa|ed25519|ecdsa|dsa)|\.(key|pem|pfx|p12|caddy)$|^\.(netrc|npmrc)$)", re.I)
SIGNAL = re.compile(r"bench|mech|hearth|lab[-_]|research|experiment|campaign|eval|(^|[/_.-])"
                    r"(runs?|results?|receipts?|ledger|metrics|telemetry|observations?|traces?|sessions?|"
                    r"conversations?|history|brain|artifacts?|capacity|schedules?|fleet)([/_.-]|$)", re.I)
FORMATS = {".json", ".jsonl", ".ndjson", ".csv", ".tsv", ".db", ".sqlite", ".sqlite3", ".pb", ".pbtxt"}
MARKERS = re.compile(r"^(result|results|manifest|receipt|metrics|summary|history|events|observations|"
                     r"timeline|schedule|scores|eval|benchmark)([-_.].*)?$", re.I)


def excluded(path):
    parts = Path(path).parts
    if any(p in SKIP or CREDENTIAL.search(p) for p in parts):
        return True
    # CONTRACT §6: only ledger metadata is allowed inside hearth-production/var.
    for i, p in enumerate(parts):
        if p == "hearth-production" and parts[i + 1:i + 2] == ("var",):
            return parts[i + 2:i + 3] != ("ledger",)
    return "amux" in parts and "scratch" in parts


def scan(spec):
    start = time.monotonic()
    root = os.path.abspath(os.path.expanduser(spec["path"]))
    result = {"id": spec["id"], "host": spec["host"], "root": root, "group": spec["group"],
              "status": "complete", "limits": {k: spec[k] for k in ("depth", "seconds", "max_files", "max_candidates")},
              "counts": {}, "candidates": [], "gaps": []}
    counts = collections.Counter()
    if excluded(root) or os.path.islink(root):
        result.update(status="excluded", gaps=["excluded_root_or_symlink"])
        return result
    if not os.path.isdir(root):
        result.update(status="missing", gaps=["root_missing"])
        return result
    # Explicit depth limits and exclusions are coverage boundaries, not full-disk claims.
    todo = collections.deque([(root, 0)])
    while todo:
        if time.monotonic() - start >= spec["seconds"] or counts["files"] >= spec["max_files"]:
            result["status"] = "partial"
            if "time_or_file_budget" not in result["gaps"]:
                result["gaps"].append("time_or_file_budget")
            break
        dp, depth = todo.popleft()
        counts["directories"] += 1
        ext = collections.Counter()
        marker = 0
        git = False
        size = 0
        mtimes = []
        children = []
        try:
            with os.scandir(dp) as entries:
                for e in entries:
                    if time.monotonic() - start >= spec["seconds"] or counts["files"] >= spec["max_files"]:
                        result["status"] = "partial"
                        if "time_or_file_budget" not in result["gaps"]:
                            result["gaps"].append("time_or_file_budget")
                        break
                    if e.name == ".git":
                        git = True
                        continue
                    if e.is_symlink():
                        counts["symlinks_excluded"] += 1
                        continue
                    if excluded(e.path) or e.name.endswith((".gguf", ".safetensors")) or e.path in spec.get("exclude", []):
                        counts["excluded"] += 1
                        continue
                    if e.is_dir(follow_symlinks=False):
                        if depth < spec["depth"]:
                            children.append((e.path, depth + 1))
                        else:
                            counts["directories_beyond_depth"] += 1
                        continue
                    if not e.is_file(follow_symlinks=False):
                        continue
                    counts["files"] += 1
                    st = e.stat(follow_symlinks=False)
                    size += st.st_size
                    mtimes.append(int(st.st_mtime))
                    suffix = Path(e.name).suffix.lower()
                    if suffix in FORMATS:
                        ext[suffix] += 1
                    if MARKERS.match(e.name):
                        marker += 1
        except OSError as exc:
            counts["read_errors"] += 1
            result["status"] = "partial"
            # errno only: exceptions can echo arbitrary paths.
            result["gaps"].append({"directory_id": hashlib.sha256(dp.encode()).hexdigest()[:16], "errno": exc.errno})
            continue
        todo.extend(sorted(children))
        hint = bool(SIGNAL.search(dp))
        if git or marker or (hint and ext) or (depth <= 1 and ext):
            if len(result["candidates"]) >= spec["max_candidates"]:
                counts["candidates_omitted"] += 1
                result["status"] = "partial"
                if "candidate_budget" not in result["gaps"]:
                    result["gaps"].append("candidate_budget")
                continue
            result["candidates"].append({"id": hashlib.sha256((spec["host"] + ":" + dp).encode()).hexdigest()[:16],
                "path": dp, "git_marker": git, "name_hint": hint, "structured_files_direct": dict(ext),
                "marker_files_direct": marker, "bytes_direct": size,
                "mtime_hint_min": min(mtimes) if mtimes else None, "mtime_hint_max": max(mtimes) if mtimes else None})
    result["counts"] = dict(counts)
    result["elapsed_s"] = round(time.monotonic() - start, 3)
    return result


def run_source(spec, source):
    if not spec.get("ssh"):
        return scan(spec)
    argv = ["python3", "-", "--worker", json.dumps(spec, separators=(",", ":"))]
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", spec["ssh"], shlex.join(argv)]
    try:
        proc = subprocess.run(cmd, input=source, capture_output=True, text=True, timeout=spec["seconds"] + 15)
        if proc.returncode == 0:
            return json.loads(proc.stdout)
        reason = "ssh_exit_%d" % proc.returncode
    except subprocess.TimeoutExpired:
        reason = "ssh_timeout"
    except (OSError, ValueError):
        reason = "remote_output_unavailable"
    return {"id": spec["id"], "host": spec["host"], "root": spec["path"], "group": spec["group"],
            "status": "failed", "counts": {}, "candidates": [], "gaps": [reason]}


def validate_output(out):
    resolved = out.resolve()
    repo = Path(__file__).resolve().parents[2]
    if not resolved.is_relative_to(repo):
        raise ValueError("Output must stay in the Known World repository")
    if any(p == "runs" or p == "hybrid-context-trial" or p.startswith("jepa-") for p in resolved.parts):
        raise ValueError("Immutable output path refused")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--roots", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--only", nargs="*", help="source ids (omit for all)")
    ap.add_argument("--worker", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker:
        print(json.dumps(scan(json.loads(args.worker)), separators=(",", ":")))
        return
    if not args.roots or not args.out:
        ap.error("--roots and --out required")
    validate_output(args.out)
    specs = json.loads(args.roots.read_text())["sources"]
    for spec in specs:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", spec["id"]):
            ap.error("Invalid source id")
        if spec.get("ssh") and spec["ssh"] not in {"10.44.0.2", "100.122.130.124"}:
            ap.error("Remote host is outside the known lab registry")
        if any(not isinstance(spec[k], int) or spec[k] < 0 for k in ("depth", "seconds", "max_files", "max_candidates")):
            ap.error("Source limits must be nonnegative integers")
    if args.only:
        unknown = set(args.only) - {s["id"] for s in specs}
        if unknown:
            ap.error("Unknown source id")
        specs = [s for s in specs if s["id"] in args.only]
    source = Path(__file__).read_text()
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out / "inventory.json").exists():
        ap.error("Completed inventory exists; choose a fresh output directory")
    (args.out / "roots-snapshot.json").write_text(args.roots.read_text())
    (args.out / "scanner-snapshot.py").write_text(source)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # One task per mount/host group: below CONTRACT's maximum of three per mount.
    groups = collections.defaultdict(list)
    for spec in specs:
        groups[spec.get("ssh") or spec["host"]].append(spec)

    def group_run(items):
        found = []
        for spec in items:
            result = run_source(spec, source)
            (args.out / (spec["id"] + ".json")).write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps({"id": spec["id"], "status": result["status"], "candidates": len(result["candidates"])}), flush=True)
            found.append(result)
        return found

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for rows in pool.map(group_run, groups.values()):
            results.extend(rows)
    summary = {"version": 1, "started": started, "roots_sha256": hashlib.sha256(args.roots.read_bytes()).hexdigest(),
               "scanner_sha256": hashlib.sha256(source.encode()).hexdigest(), "source_contents_read": False,
               "privacy": "Private directory metadata only. No files opened, no transcript bodies, no credential contents.",
               "coverage_rule": "Complete means enumerated within declared depth and exclusions. Missing/partial/failed are not zero activity.",
               "sources": [{k: r[k] for k in ("id", "host", "root", "group", "status", "counts", "gaps")} for r in results],
               "unique_candidate_directories": len({(r["host"], c["id"]) for r in results for c in r["candidates"]})}
    (args.out / "inventory.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
