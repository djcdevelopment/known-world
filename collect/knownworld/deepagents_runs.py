"""deepagents_runs.py: run directories, per-call offload observations and assessment run counts.

Parts (CONTRACT.md section 2: ids, times and counts only; observation `notes`, run files and transcripts are never
read): deepagents run dirs -> one `run` each (file count, bytes); hearth-production/runs obs-offload-*.json ->
`offload_call` (src stays deepagents_runs, distinct from hearth_ledger); assessment transcript run dirs -> one
`run` each with file counts only.
"""
import json
import os
import re

from knownworld import core
from knownworld.chatfold import safe_model

SRC = "deepagents_runs"
TOKEN_OK = re.compile(r"^[A-Za-z0-9_.:/\-]{1,64}$")


def enumerate_sources(ctx):
    out = []
    for i, part in enumerate((ctx.item.get("options") or {}).get("parts") or []):
        if part["kind"] in ("deepagents_runs", "obs_offload", "assessment_runs"):
            p = os.path.expanduser(part["path"])
            out.append({"label": "%s-%d" % (part["kind"], i), "kind": part["kind"], "shard_key": p,
                        "spec": dict(part, path=p, idx=i)})
    return out


def _tok(v):
    return v if isinstance(v, str) and TOKEN_OK.match(v) else None


def _dir_stats(path):
    files = size = 0
    for dp, dn, fn in os.walk(path):
        dn[:] = [d for d in dn if not core.is_never_walk(os.path.join(dp, d))]
        for n in fn:
            if core.is_credential_name(n):
                continue
            files += 1
            try:
                size += os.path.getsize(os.path.join(dp, n))
            except OSError:
                pass
    return files, size


def _birth(path):
    rc, out, _, to = core.run(["stat", "-c", "%W %Y", path], 30)
    if rc != 0:
        return None
    try:
        b, m = (int(x) for x in out.decode().split())
    except ValueError:
        return None
    return core.good_epoch(b if b > 0 else m)


def run_dirs(ctx, spec, kind_meta, dir_re):
    path = spec["path"]
    host, disp = core.host_and_rel(path, spec.get("host", ctx.item["host"]))
    rel = disp[2:] if disp.startswith("~/") else disp
    n = 0
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        if not os.path.isdir(full) or not dir_re.match(name) or core.is_credential_name(name):
            continue
        n += 1
        files, size = _dir_stats(full)
        e = _birth(full)
        if e is None:
            ctx.drop("null_ts")
        ctx.emit({"ts": core.iso(e) if e else None, "kind": "run",
                  "actor": {"class": "automation", "name": spec.get("actor_name", "deepagents")}, "host": host,
                  "repo": None, "path": core.clip(core.depth2(rel), 120),
                  "magnitude": {"n": 1, "files": files, "bytes": size}, "ref": core.sha1hex("run|" + host + "|" + disp + "|" + name),
                  "src": SRC, "meta": {"type": kind_meta}})
    return n


def obs_offload(ctx, spec):
    root = spec["path"]
    host = spec.get("host", ctx.item["host"])
    n = 0
    for dp, dn, fn in os.walk(root):
        dn.sort()
        dn[:] = [d for d in dn if not core.is_never_walk(os.path.join(dp, d))]
        for name in sorted(fn):
            if not (name.startswith("obs-offload-") and name.endswith(".json")):
                continue
            n += 1
            try:
                core.guard_read(os.path.join(dp, name))
                with open(os.path.join(dp, name), "rb") as f:
                    o = json.load(f)
            except (ValueError, OSError):
                ctx.drop("decode_errors")
                continue
            e = core.good_epoch(core.to_epoch(o.get("timestamp")))
            if e is None:
                ctx.drop("null_ts")
            mid = o.get("model_id") if isinstance(o.get("model_id"), str) else ""
            low = mid.lower()
            if "claude" in low:
                cls, nm = "claude", safe_model(mid) or "claude"
            elif "codex" in low or low.startswith("gpt"):
                cls, nm = "codex", safe_model(mid) or "codex"
            else:
                cls, nm = "local_model", safe_model(mid) or "local"
            ws = o.get("workload_shape") if isinstance(o.get("workload_shape"), dict) else {}
            ob = o.get("observed") if isinstance(o.get("observed"), dict) else {}
            rt, tps = ob.get("runtime_s"), ob.get("tokens_per_s")
            ctxt = ob.get("context_tokens")
            num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0
            mag = {"n": 1, "tokens_in": int(ctxt) if num(ctxt) else None,
                   "tokens_out": int(rt * tps) if num(rt) and num(tps) else None,
                   "duration_ms": int(rt * 1000) if num(rt) else None}
            meta = {}
            for k, v in (("backend", o.get("backend")), ("task_kind", ws.get("task_kind")), ("outcome", o.get("outcome"))):
                if _tok(v):
                    meta[k] = v
            oid = o.get("observation_id")
            ref = oid if isinstance(oid, str) and re.match(r"^[A-Za-z0-9_.:=\-]{1,80}$", oid) else core.sha1hex(os.path.join(dp, name))
            ev = {"ts": core.iso(e) if e else None, "kind": "offload_call", "actor": {"class": cls, "name": nm},
                  "host": host, "repo": None, "path": None, "magnitude": mag, "ref": ref, "src": SRC}
            if meta:
                ev["meta"] = meta
            ctx.emit(ev)
    return n


def assessment_runs(ctx, spec):
    path = spec["path"]
    host, disp = core.host_and_rel(path, spec.get("host", ctx.item["host"]))
    n = 0
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        if not os.path.isdir(full) or not name.startswith("run-"):
            continue
        n += 1
        files, size = _dir_stats(full)
        e = _birth(full)
        if e is None:
            ctx.drop("null_ts")
        ctx.emit({"ts": core.iso(e) if e else None, "kind": "run",
                  "actor": {"class": "automation", "name": "assessment"}, "host": host, "repo": None,
                  "path": core.clip(core.depth2(disp), 120),
                  "magnitude": {"n": 1, "files": files, "bytes": size},
                  "ref": core.sha1hex("assess|" + disp + "|" + name), "src": SRC, "meta": {"type": "assessment_run"}})
    return n


def process_source(ctx, src, cursor):
    spec, kind = src["spec"], src["kind"]
    if not os.path.isdir(spec["path"]):
        return {"status": "skipped", "reason": "path_missing"}
    if kind == "deepagents_runs":
        n = run_dirs(ctx, spec, "authored_run", re.compile(r"^[A-Za-z0-9]"))
    elif kind == "obs_offload":
        n = obs_offload(ctx, spec)
    else:
        n = assessment_runs(ctx, spec)
    return {"status": "done", "raw": n}
