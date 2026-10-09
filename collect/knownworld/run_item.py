#!/usr/bin/env python3
"""run_item.py <item.json> [--budget-s N] [--retry-skipped] [--fresh]

The only entry point of the Known World collectors. Reads a work item (CONTRACT.md section 5), dispatches to the
extractor for its source_type and writes corpus/raw/<id>/{events.ndjson, repos.ndjson, manifest.json,
checkpoint.json, run.log}. Sources are processed incrementally and checkpointed, so a run stops at the time budget
and resumes where it stopped.

Exit codes: 0 complete (manifest status complete, or partial with every gap recorded), 3 budget exhausted with more
to do (run again), 1 failed. Run with: .venv/bin/python -I collect/knownworld/run_item.py item.json --budget-s 540
"""
import argparse
import fcntl
import hashlib
import importlib
import json
import os
import sys
import time
import traceback

sys.dont_write_bytecode = True  # -I ignores PYTHONDONTWRITEBYTECODE
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knownworld import core  # noqa: E402

REGISTRY = {
    "git_repo": "git_repo", "fs_births": "fs_births", "claude_jsonl": "claude_jsonl", "codex_jsonl": "codex_jsonl",
    "chatgpt_export": "chatgpt_export", "opencode_db": "opencode_db", "hearth_ledger": "hearth_ledger",
    "continuity": "continuity", "github_api": "github_api", "deepagents_runs": "deepagents_runs",
}
MOUNT_SLOTS = 3
GRACE_S = 45  # one in-flight source may overrun the budget by this much before it is abandoned


class Ctx:
    def __init__(self, item, out_dir, budget_s):
        self.item = item
        self.out_dir = out_dir
        self.t0 = time.monotonic()
        self.budget_s = budget_s
        self.deadline = self.t0 + budget_s
        self.hard_deadline = self.deadline + GRACE_S
        self.events_buf, self.repos_buf = [], []
        self.dropped = {"null_ts": 0, "polling": 0, "decode_errors": 0}
        self.warnings = []
        self.extra = {"not_repos": 0, "null_ts_emitted": 0, "out_of_range": 0, "invalid_remote_records": 0}
        self.since = core.clean_ts(item.get("since")) if item.get("since") else None
        self.until = core.clean_ts(item.get("until")) if item.get("until") else None
        self.options = item.get("options") or {}
        self.logf = open(os.path.join(out_dir, "run.log"), "a", buffering=1)
        self.ident = None
        self.ident_data = None
        self.elapsed_before = 0.0
        self.sources_this_slice = 0

    # --- time
    def time_left(self):
        return self.deadline - time.monotonic()

    def time_up(self):
        return time.monotonic() >= self.deadline

    def item_time_left(self):
        return float(self.item.get("timeout_s", 1800)) - self.elapsed_before - (time.monotonic() - self.t0)

    def src_timeout(self, cap):
        """Per-subprocess timeout: capped, and never beyond the item's remaining wall time."""
        return max(30, min(cap, self.item_time_left()))

    # --- output
    def emit(self, ev):
        ts = ev.get("ts")
        if ts is None:
            self.extra["null_ts_emitted"] += 1
        else:
            if (self.since and ts < self.since) or (self.until and ts > self.until):
                self.extra["out_of_range"] += 1
                return
        self.events_buf.append(ev)

    def emit_repo(self, rec):
        self.repos_buf.append(rec)

    def drop(self, name, n=1):
        self.dropped[name] = self.dropped.get(name, 0) + n

    def warn(self, code):
        code = core.clip(code, 100)
        if code not in self.warnings and len(self.warnings) < 60:
            self.warnings.append(code)

    def log(self, msg):
        self.logf.write("%s %s\n" % (core.iso(time.time()), core.clip(msg, 300)))

    def get_ident(self):
        if self.ident is None:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "identity.json")) as f:
                self.ident_data = json.load(f)
            self.ident = core.Identity(self.ident_data)
        return self.ident


def label_for(path, kind=""):
    base = os.path.basename(path.rstrip("/")) or "root"
    return "%s~%s" % (core.clip(base, 36), core.sha1hex(path)[:4])


def hash_label(path, prefix):
    return "%s-%s" % (prefix, core.sha1hex(path)[:10])


def atomic_write_json(path, data):
    core.guard_write(path)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, separators=(",", ":"))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def sha256_file(path):
    h = hashlib.sha256()
    if not os.path.exists(path):
        return h.hexdigest()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class MountSlot:
    """At most 3 concurrent items per mount (CONTRACT.md section 6), enforced with flock slots."""

    def __init__(self, mount):
        self.mount, self.fd = mount, None

    def acquire(self, wait_s=240):
        if self.mount not in ("c", "e"):
            return True
        d = os.path.join(core.KW_ROOT, "cache", "locks")
        os.makedirs(d, exist_ok=True)
        end = time.monotonic() + wait_s
        while True:
            for i in range(MOUNT_SLOTS):
                fd = os.open(os.path.join(d, "mount-%s-%d.lock" % (self.mount, i)), os.O_CREAT | os.O_RDWR, 0o644)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.fd = fd
                    return True
                except OSError:
                    os.close(fd)
            if time.monotonic() >= end:
                return False
            time.sleep(5)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("item")
    ap.add_argument("--budget-s", type=float, default=540)
    ap.add_argument("--retry-skipped", action="store_true")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--list", action="store_true", help="enumerate sources and shard sizes, process nothing")
    a = ap.parse_args(argv)
    core.setup_env()

    with open(a.item) as f:
        item = json.load(f)
    if a.list:
        return list_sources(item)
    out_dir = core.guard_write(item["out_dir"])
    os.makedirs(out_dir, exist_ok=True)

    lockfd = os.open(os.path.join(out_dir, ".lock"), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("item_locked: another run of this item is active")
        return 1

    ev_path, rp_path = os.path.join(out_dir, "events.ndjson"), os.path.join(out_dir, "repos.ndjson")
    ck_path = os.path.join(out_dir, "checkpoint.json")
    if a.fresh:
        for n in ("events.ndjson", "repos.ndjson", "checkpoint.json", "manifest.json", "run.log"):
            try:
                os.remove(os.path.join(out_dir, n))
            except FileNotFoundError:
                pass
    ck = {"version": 1, "started": core.iso(time.time()), "elapsed_s": 0.0, "done": {}, "cursor": {},
          "ev_off": 0, "rp_off": 0, "events": 0, "repos": 0, "dropped": {"null_ts": 0, "polling": 0, "decode_errors": 0},
          "extra": {}, "warnings": [], "slices": 0}
    if os.path.exists(ck_path):
        with open(ck_path) as f:
            ck.update(json.load(f))
    # crash recovery: cut both files back to the last committed offsets
    for p, off in ((ev_path, ck["ev_off"]), (rp_path, ck["rp_off"])):
        if os.path.exists(p) and os.path.getsize(p) > off:
            os.truncate(p, off)
        elif not os.path.exists(p):
            open(p, "w").close()
    if a.retry_skipped:
        ck["done"] = {k: v for k, v in ck["done"].items() if v.get("status") != "skipped"}

    ctx = Ctx(item, out_dir, a.budget_s)
    ctx.elapsed_before = ck["elapsed_s"]
    ctx.dropped.update(ck["dropped"])
    ctx.extra.update(ck["extra"])
    ctx.warnings = list(ck["warnings"])
    ctx.log("slice start budget_s=%d done_sources=%d" % (a.budget_s, len(ck["done"])))

    slot = MountSlot(item.get("mount"))
    if not slot.acquire():
        ctx.log("mount_busy: no slot free, run again")
        print("status=busy (mount slots full); run again")
        return 3

    mod = importlib.import_module("knownworld." + REGISTRY[item["source_type"]])
    ev_f, rp_f = open(ev_path, "ab"), open(rp_path, "ab")
    status_more = False
    skipped_notes = []

    def commit(label, entry, cursor=None):
        for ev in ctx.events_buf:
            ev_f.write((json.dumps(ev, separators=(",", ":")) + "\n").encode())
        for rp in ctx.repos_buf:
            rp_f.write((json.dumps(rp, separators=(",", ":")) + "\n").encode())
        ev_f.flush()
        rp_f.flush()
        ck["events"] += len(ctx.events_buf)
        ck["repos"] += len(ctx.repos_buf)
        entry["events"] = len(ctx.events_buf)
        ctx.events_buf, ctx.repos_buf = [], []
        ck["ev_off"], ck["rp_off"] = ev_f.tell(), rp_f.tell()
        if cursor is None:
            ck["cursor"].pop(label, None)
            ck["done"][label] = entry
            ctx.sources_this_slice += 1
        else:
            ck["cursor"][label] = cursor
        ck["dropped"], ck["extra"], ck["warnings"] = dict(ctx.dropped), dict(ctx.extra), list(ctx.warnings)
        ck["elapsed_s"] = round(ctx.elapsed_before + time.monotonic() - ctx.t0, 1)
        atomic_write_json(ck_path, ck)

    try:
        try:
            sources = mod.enumerate_sources(ctx)
        except Exception as e:  # enumeration failure is fatal for the item
            ctx.log("enumerate failed: %s line=%d" % (type(e).__name__, traceback.extract_tb(e.__traceback__)[-1].lineno))
            write_manifest(item, ck, ctx, [], "failed", out_dir, ["enumerate_failed:" + type(e).__name__])
            print("status=failed (enumeration)")
            return 1
        if not sources:
            ctx.log("no sources found for roots")
            write_manifest(item, ck, ctx, [], "failed", out_dir, ["no_sources_found"])
            print("item=%s status=failed (no sources found for the item's roots)" % item["id"])
            return 1
        shard = item.get("shard") or {}
        n, k = int(shard.get("n", 1) or 1), int(shard.get("k", 0) or 0)
        if n > 1:
            sources = [s for s in sources if int(core.sha1hex(s.get("shard_key") or s["label"]), 16) % n == k]
        ctx.log("sources=%d" % len(sources))
        for s in sources:
            lab = s["label"]
            if lab in ck["done"]:
                continue
            if ctx.item_time_left() <= 0:
                ck["done"][lab] = {"kind": s["kind"], "raw": 0, "status": "skipped", "reason": "item_timeout_s_exhausted"}
                continue
            if ctx.time_up() and ctx.sources_this_slice > 0:
                status_more = True
                break
            ctx.events_buf, ctx.repos_buf = [], []
            try:
                res = mod.process_source(ctx, s, ck["cursor"].get(lab))
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)[-1]
                ctx.log("source failed label=%s %s at %s:%d" % (lab, type(e).__name__, os.path.basename(tb.filename), tb.lineno))
                ctx.events_buf, ctx.repos_buf = [], []
                commit(lab, {"kind": s["kind"], "raw": 0, "status": "skipped", "reason": "exception:" + type(e).__name__})
                continue
            if res["status"] == "budget":
                commit(lab, {}, cursor=res.get("cursor") or {})
                status_more = True
                ctx.log("budget reached inside source label=%s" % lab)
                break
            entry = {"kind": s["kind"], "raw": res.get("raw", 0), "status": res["status"]}
            if "preserved_mtime" in res:
                entry["preserved_mtime"] = res["preserved_mtime"]
            if res.get("reason"):
                entry["reason"] = core.clip(res["reason"], 100)
            if res["status"] == "skipped":
                ctx.events_buf, ctx.repos_buf = [], []
            commit(lab, entry)
            ctx.log("source %s label=%s raw=%s events=%s" % (res["status"], lab, entry["raw"], entry["events"]))
        # sources never reached stay pending
        pending = [s for s in sources if s["label"] not in ck["done"]]
        if pending and not status_more:
            status_more = True
    finally:
        ev_f.close()
        rp_f.close()

    ck["slices"] += 1
    ck["elapsed_s"] = round(ctx.elapsed_before + time.monotonic() - ctx.t0, 1)
    pending = [s for s in sources if s["label"] not in ck["done"]]
    if pending and ctx.item_time_left() <= 0:
        for s in pending:
            ck["done"][s["label"]] = {"kind": s["kind"], "raw": 0, "status": "skipped", "reason": "item_timeout_s_exhausted"}
        pending = []
    seen = {s["label"]: s for s in sources}
    done_here = {k: v for k, v in ck["done"].items() if k in seen}
    n_skipped = sum(1 for v in done_here.values() if v["status"] == "skipped")
    if pending:
        status = "partial"
    elif done_here and n_skipped == len(done_here):
        status = "failed"
    elif n_skipped:
        status = "partial"
    else:
        status = "complete"
    write_manifest(item, ck, ctx, sources, status, out_dir, [], more=bool(pending))
    atomic_write_json(ck_path, ck)
    ctx.log("slice end status=%s pending=%d events=%d" % (status, len(pending), ck["events"]))
    print("item=%s status=%s events=%d repos=%d sources=%d pending=%d skipped=%d dropped=%s" % (
        item["id"], status, ck["events"], ck["repos"], len(sources), len(pending), n_skipped, json.dumps(ck["dropped"])))
    if pending:
        return 3
    return 1 if status == "failed" else 0


def list_sources(item):
    """Counts only: sources found, and the size of every shard (they must add up and never overlap)."""
    tmp = os.path.join(core.KW_ROOT, "cache", "tmp", "list-" + item["id"])
    os.makedirs(tmp, exist_ok=True)
    ctx = Ctx(dict(item, out_dir=tmp), tmp, 60)
    mod = importlib.import_module("knownworld." + REGISTRY[item["source_type"]])
    sources = mod.enumerate_sources(ctx)
    n = int((item.get("shard") or {}).get("n", 1) or 1)
    sizes = [0] * n
    for s in sources:
        sizes[int(core.sha1hex(s.get("shard_key") or s["label"]), 16) % n] += 1
    k = int((item.get("shard") or {}).get("k", 0) or 0)
    print("item=%s sources=%d shards=%s this_shard(k=%d)=%d not_repos=%s excluded=%s warnings=%s" % (
        item["id"], len(sources), sizes, k, sizes[k], ctx.extra.get("not_repos"), ctx.extra.get("excluded"),
        json.dumps(ctx.warnings)))
    return 0


def write_manifest(item, ck, ctx, sources, status, out_dir, extra_warnings, more=False):
    seen = {s["label"] for s in sources}
    done = {k: v for k, v in ck["done"].items() if (k in seen or not sources)}
    man = {
        "item": item["id"], "src": item["source_type"], "started": ck["started"],
        "finished": core.iso(time.time()) if status in ("complete", "failed") or (status == "partial" and not more) else None,
        "status": status, "events": ck["events"], "events_sha256": sha256_file(os.path.join(out_dir, "events.ndjson")),
        "repos": ck["repos"], "dropped": ck["dropped"],
        "coverage": dict({"sources_seen": len(sources),
                          "sources_skipped": [{"label": k, "reason": v.get("reason", "?")} for k, v in done.items()
                                              if v["status"] == "skipped"]}, **ck["extra"]),
        "warnings": ck["warnings"] + extra_warnings,
        "sources": [dict({"label": k, "kind": v["kind"], "raw": v.get("raw", 0)},
                         **({"preserved_mtime": v["preserved_mtime"]} if "preserved_mtime" in v else {}))
                    for k, v in done.items() if v["status"] == "done"],
        "slices": ck["slices"],
    }
    atomic_write_json(os.path.join(out_dir, "manifest.json"), man)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
