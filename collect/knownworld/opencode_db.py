"""opencode_db.py: OpenCode sqlite, explicit columns of `session` and `message` only (CONTRACT.md section 2).

Opened with mode=ro&immutable=1 (WAL contents may be missed; recorded as a warning). The account, credential,
part, session_input, todo and event tables are never selected. From `message.data` only json_extract of role,
modelID, model.modelID and token counts is read.
"""
import os
import sqlite3
from urllib.parse import quote

from knownworld import core
from knownworld.chatfold import Fold, safe_model

SRC = "opencode_db"


def enumerate_sources(ctx):
    out = []
    for root in ctx.item["roots"]:
        p = os.path.expanduser(root)
        if os.path.isfile(p):
            out.append({"label": "opencode-db", "kind": "sqlite", "shard_key": p, "spec": {"file": p}})
        else:
            ctx.warn("missing:opencode.db")
    return out


def _int(v):
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else None


def process_source(ctx, src, cursor):
    path = src["spec"]["file"]
    core.guard_read(path)
    ctx.warn("sqlite_immutable_wal_may_be_missed")
    con = sqlite3.connect("file:%s?mode=ro&immutable=1" % quote(path), uri=True, timeout=30)
    try:
        con.execute("pragma query_only=1")
        tables = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
        if not {"session", "message"} <= tables:
            return {"status": "skipped", "reason": "schema_unrecognised"}
        sess = {}
        for sid, parent, directory in con.execute("select id, parent_id, directory from session"):
            sess[sid] = {"side": parent is not None, "dir": directory}
        folds, raw = {}, 0
        q = ("select session_id, time_created, json_extract(data,'$.role'), json_extract(data,'$.modelID'),"
             " json_extract(data,'$.model.modelID'), json_extract(data,'$.tokens.input'),"
             " json_extract(data,'$.tokens.output'), json_extract(data,'$.tokens.cache.read'),"
             " json_extract(data,'$.tokens.cache.write') from message")
        for sid, tc, role, mid, umid, tin, tout, cr, cw in con.execute(q):
            raw += 1
            e = core.good_epoch(core.to_epoch(tc))
            if e is None:
                ctx.drop("null_ts")
                continue
            if role not in ("user", "assistant"):
                ctx.drop("other_role")
                continue
            fo = folds.setdefault(sid, Fold())
            if role == "assistant":
                cache = (_int(cr) or 0) + (_int(cw) or 0) if (cr is not None or cw is not None) else None
                fo.add("assistant", e, mid, _int(tin), _int(tout), cache)
            else:
                fo.add("user", e, umid)
        for sid, fo in folds.items():
            s = sess.get(sid) or {"side": False, "dir": None}
            host, p = core.surface_path(s["dir"]) if s["dir"] else (None, None)
            for ev in fo.events(SRC, "opencode", "opencode", host or "omen-linux", p, sid, sid, sidechain=s["side"]):
                ctx.emit(ev)
    finally:
        con.close()
    return {"status": "done", "raw": raw}
