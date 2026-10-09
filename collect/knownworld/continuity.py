"""continuity.py: continuity (`ct`) ledger events plus the run-style parts of deepagents_runs.py (CONTRACT.md 1, 2).

Event body text is never read: only type, recorded_at, runner and id survive. Ledgers on am4 and fx99 are read over
ssh with ct_remote.py (read-only). deepagents run dirs, hearth-production obs-offload files and the C: assessment run
counts are delegated to deepagents_runs.py (their events carry src deepagents_runs).
"""
import glob
import json
import os
import re

from knownworld import core, deepagents_runs
from knownworld.chatfold import safe_model

SRC = "continuity"
TOKEN_OK = re.compile(r"^[A-Za-z0-9_.:/\-]{1,64}$")


def enumerate_sources(ctx):
    out = []
    for i, part in enumerate((ctx.item.get("options") or {}).get("parts") or []):
        if part["kind"] == "ct_ledger":
            out.append({"label": "ct_ledger-%d-%s" % (i, part["host"]), "kind": "ct_ledger",
                        "shard_key": "%s:%s" % (part["host"], part["path"]), "spec": dict(part, idx=i)})
    return [s for s in out] + deepagents_runs.enumerate_sources(ctx)


def runner_actor(r):
    low = (r or "").lower()
    if "claude" in low:
        return "claude", "claude"
    if "codex" in low:
        return "codex", "codex"
    if "opencode" in low:
        return "opencode", "opencode"
    if low in ("human", "derek") or low.startswith("human"):
        return "human", "derek"
    if any(x in low for x in ("qwen", "local", "gemma", "llama", "vllm")):
        return "local_model", safe_model(r) or "local"
    return "automation", "ct"


def _emit_ct(ctx, host, rec):
    t = rec.get("type")
    e = core.good_epoch(core.to_epoch(rec.get("at")))
    if e is None:
        ctx.drop("null_ts")
    cls, nm = runner_actor(rec.get("runner"))
    kind = "receipt" if isinstance(t, str) and t.startswith("receipt") else "run"
    eid = rec.get("id")
    ref = eid if isinstance(eid, str) and re.match(r"^[A-Za-z0-9_.:=\-]{1,80}$", eid) else core.sha1hex("ct|%s|%s|%s" % (host, t, rec.get("at")))
    meta = {}
    if isinstance(t, str) and TOKEN_OK.match(t):
        meta["type"] = t
    if isinstance(rec.get("runner"), str) and TOKEN_OK.match(rec["runner"]):
        meta["runner"] = rec["runner"]
    ev = {"ts": core.iso(e) if e else None, "kind": kind, "actor": {"class": cls, "name": nm}, "host": host,
          "repo": None, "path": None, "magnitude": {"n": 1}, "ref": ref, "src": SRC}
    if meta:
        ev["meta"] = meta
    ctx.emit(ev)


def process_source(ctx, src, cursor):
    if src["kind"] != "ct_ledger":
        return deepagents_runs.process_source(ctx, src, cursor)
    spec = src["spec"]
    host = spec["host"]
    raw = 0
    if host in ("am4", "fx99"):
        from knownworld import remote
        st = remote.ssh_stream(host, {"path": spec["path"]}, ctx.src_timeout(300), modules=("core.py", "ct_remote.py"))
        for ln in st.lines():
            try:
                rec = json.loads(ln)
            except ValueError:
                ctx.drop("decode_errors")
                continue
            if rec.get("bad"):
                ctx.drop("decode_errors")
                continue
            raw += 1
            _emit_ct(ctx, host, rec)
        st.close()
        if st.timed_out or (raw == 0 and st.rc != 0):
            return {"status": "skipped", "reason": "ssh:" + core.err_class(st.err_head)}
        return {"status": "done", "raw": raw}
    d = os.path.join(os.path.expanduser(spec["path"]), "events")
    if not os.path.isdir(d):
        return {"status": "skipped", "reason": "path_missing"}
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            core.guard_read(p)
            with open(p, "rb") as f:
                o = json.load(f)
        except (ValueError, OSError):
            ctx.drop("decode_errors")
            continue
        raw += 1
        r = o.get("runner")
        if isinstance(r, dict):
            r = r.get("kind") or r.get("name") or r.get("id")
        _emit_ct(ctx, host, {"id": o.get("id"), "type": o.get("type"), "at": o.get("recorded_at"), "runner": r})
    return {"status": "done", "raw": raw}
