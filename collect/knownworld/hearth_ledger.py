"""hearth_ledger.py: HEARTH ledger copies -> offload_call events (CONTRACT.md sections 1, 2).

Reads exactly <ledger dir>/events.ndjson (and the primary's index.sqlite event_id column for de-duplication). Dispatch
tools are kept; polling tools are counted and dropped. args_preview, result_digest, error text, intent and reason are
never read into the output; the caller id is hashed. Nothing else in hearth-var (secrets, callers.json) is opened.
"""
import json
import os
import re
import sqlite3
from urllib.parse import quote

from knownworld import core
from knownworld.chatfold import safe_model

SRC = "hearth_ledger"
DISPATCH = {"local_generate", "submit_task", "submit_local_work", "submit_execution", "submit_batch",
            "submit_delegated_execution"}
TOKEN_OK = re.compile(r"^[A-Za-z0-9_.:/\-]{1,64}$")
NODE_HOST = {"am4": "am4", "fx99": "fx99", "omen-linux": "omen-linux", "omen-c": "omen-c", "omen-e": "omen-e"}
CHECK_EVERY = int(os.environ.get("KW_CHECK_EVERY", "5000"))


def enumerate_sources(ctx):
    out = []
    for i, led in enumerate((ctx.item.get("options") or {}).get("ledgers") or []):
        p = os.path.join(os.path.expanduser(led["path"]), "events.ndjson")
        if os.path.isfile(p):
            out.append({"label": "ledger-%d-%s" % (i, led["host"]), "kind": "ledger", "shard_key": p,
                        "spec": {"file": p, "dir": os.path.dirname(p), "host": led["host"], "idx": i}})
        else:
            ctx.warn("missing:ledger-%d" % i)
    return out


def _primary_ids(ctx, spec):
    """event_ids already covered by earlier (primary) ledgers."""
    ids = set()
    leds = (ctx.item.get("options") or {}).get("ledgers") or []
    for led in leds[:spec["idx"]]:
        d = os.path.expanduser(led["path"])
        ix = os.path.join(d, "index.sqlite")
        if os.path.isfile(ix):
            con = sqlite3.connect("file:%s?mode=ro&immutable=1" % quote(ix), uri=True, timeout=30)
            try:
                ids.update(r[0] for r in con.execute("select event_id from events"))
            finally:
                con.close()
        else:
            rx = re.compile(rb'"event_id":\s*"([^"]+)"')
            with open(os.path.join(d, "events.ndjson"), "rb") as f:
                for raw in f:
                    m = rx.search(raw[:400])
                    if m:
                        ids.add(m.group(1).decode())
    return ids


def _tok(v):
    return v if isinstance(v, str) and TOKEN_OK.match(v) else None


def _int(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)) and v >= 0:
        return int(round(v))
    return None


def process_source(ctx, src, cursor):
    spec = src["spec"]
    path, host = spec["file"], spec["host"]
    core.guard_read(path)
    seen = _primary_ids(ctx, spec) if spec["idx"] > 0 else set()
    st = {"off": 0, "raw": 0}
    if cursor:
        st.update(cursor["st"])
    f = open(path, "rb")
    try:
        f.seek(st["off"])
        off, nl = st["off"], 0
        for raw in iter(f.readline, b""):
            nl += 1
            if nl % CHECK_EVERY == 0 and ctx.time_up():
                st["off"] = off  # start of this unprocessed line
                return {"status": "budget", "cursor": {"st": st}}
            off += len(raw)
            if raw.endswith(b"\n"):
                st["raw"] += 1
            try:
                o = json.loads(raw)
            except ValueError:
                ctx.drop("decode_errors")
                continue
            if not isinstance(o, dict):
                continue
            tool = o.get("tool")
            if tool not in DISPATCH:
                ctx.drop("polling")
                continue
            eid = o.get("event_id")
            if not isinstance(eid, str):
                ctx.drop("decode_errors")
                continue
            if eid in seen:
                ctx.extra["deduped"] = ctx.extra.get("deduped", 0) + 1
                continue
            e = core.good_epoch(core.to_epoch(o.get("ts")))
            caller = o.get("caller") if isinstance(o.get("caller"), dict) else {}
            rc = caller.get("runner_class")
            cid = caller.get("id") if isinstance(caller.get("id"), str) else ""
            if rc == "frontier":
                cls = "codex" if "codex" in cid.lower() else "claude"
                name = cls
            elif rc == "local":
                cls, name = "local_model", safe_model(o.get("model")) or "local"
            elif rc == "human":
                cls, name = "human", "derek"
            else:
                cls, name = "automation", "hearth"
            node = caller.get("node")
            h = NODE_HOST.get(node.lower()) if isinstance(node, str) else None
            cost = o.get("cost") if isinstance(o.get("cost"), dict) else {}
            mag = {"n": 1, "tokens_in": _int(cost.get("tokens_in")), "tokens_out": _int(cost.get("tokens_out")),
                   "duration_ms": _int(o.get("duration_ms"))}
            meta = {"tool": tool}
            if isinstance(o.get("ok"), bool):
                meta["ok"] = o["ok"]
            for k in ("task_class", "backend", "routed_by", "outcome", "error_code"):
                v = _tok(o.get(k))
                if v:
                    meta[k] = v
            if cid:
                meta["caller"] = core.sha1_12(cid)
            ref = eid if re.match(r"^[A-Za-z0-9_.:=\-]{1,80}$", eid) else core.sha1hex(eid)
            if e is None:
                ctx.extra["null_ts_event"] = ctx.extra.get("null_ts_event", 0) + 1
            ctx.emit({"ts": core.iso(e) if e else None, "kind": "offload_call", "actor": {"class": cls, "name": name},
                      "host": h or host, "repo": None, "path": None, "magnitude": mag, "ref": ref, "src": SRC,
                      "meta": meta})
    finally:
        f.close()
    return {"status": "done", "raw": st["raw"]}
