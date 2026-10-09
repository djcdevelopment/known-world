"""chatgpt_export.py: the normalized ChatGPT export, ids/roles/times/model_slug only (CONTRACT.md section 2).

Reads conversations.ndjson (one chat_session per conversation) and messages.ndjson (chat_msg folded per
conversation, role and minute). Titles, text, parts and every other column are never kept.
"""
import json
import os

from knownworld import core
from knownworld.chatfold import Fold, safe_model

SRC = "chatgpt_export"


def enumerate_sources(ctx):
    out = []
    for root in ctx.item["roots"]:
        d = os.path.expanduser(root)
        for n, kind in (("conversations.ndjson", "conversations"), ("messages.ndjson", "messages")):
            p = os.path.join(d, n)
            if os.path.isfile(p):
                out.append({"label": kind, "kind": kind, "shard_key": p, "spec": {"file": p, "dir": d}})
            else:
                ctx.warn("missing:" + n)
    return out


def _lines(ctx, path):
    core.guard_read(path)
    with open(path, "rb") as f:
        for raw in iter(f.readline, b""):
            yield raw


def _sid(v):
    return core.clip(str(v), 80) if isinstance(v, (str, int)) and str(v) else None


def _convs(ctx, d):
    convs = {}
    for raw in _lines(ctx, os.path.join(d, "conversations.ndjson")):
        try:
            o = json.loads(raw)
        except ValueError:
            continue
        cid = _sid(o.get("conversation_id"))
        if cid:
            convs[cid] = {"model": safe_model(o.get("model_slug")), "create": core.good_epoch(core.to_epoch(o.get("create_time"))),
                          "update": core.good_epoch(core.to_epoch(o.get("update_time"))),
                          "n": o.get("message_count"), "un": o.get("user_message_count"),
                          "an": o.get("assistant_message_count"), "br": o.get("has_branches"),
                          "ar": o.get("is_archived"), "vo": o.get("voice")}
    return convs


def process_source(ctx, src, cursor):
    d = src["spec"]["dir"]
    path = src["spec"]["file"]
    raw_n = 0
    if src["kind"] == "conversations":
        for raw in _lines(ctx, path):
            if raw.endswith(b"\n"):
                raw_n += 1
        for cid, c in _convs(ctx, d).items():
            meta = {"session": cid}
            if c["model"]:
                meta["model"] = [c["model"]]
            if isinstance(c["un"], int):
                meta["user_n"] = c["un"]
            if isinstance(c["an"], int):
                meta["assistant_n"] = c["an"]
            for k, key in (("br", "branches"), ("ar", "archived"), ("vo", "voice")):
                if isinstance(c[k], bool):
                    meta[key] = c[k]
            if c["create"] is None:
                ctx.drop("null_ts")
            dur = max(0, (c["update"] or 0) - c["create"]) if (c["create"] and c["update"]) else 0
            ctx.emit({"ts": core.iso(c["create"]) if c["create"] else None, "kind": "chat_session",
                      "actor": {"class": "chatgpt", "name": c["model"] or "chatgpt"}, "host": "cloud", "repo": None,
                      "path": None, "magnitude": {"n": c["n"] if isinstance(c["n"], int) and c["n"] >= 0 else 0,
                                                  "duration_s": dur},
                      "ref": core.sha1hex("chatgpt-conv|" + cid), "src": SRC, "meta": meta})
        return {"status": "done", "raw": raw_n}
    convs = _convs(ctx, d)
    folds = {}
    for raw in _lines(ctx, path):
        if raw.endswith(b"\n"):
            raw_n += 1
        try:
            o = json.loads(raw)
        except ValueError:
            ctx.drop("decode_errors")
            continue
        role = o.get("role")
        if role not in ("user", "assistant", "tool"):
            ctx.drop("other_role")
            continue
        cid = _sid(o.get("conversation_id"))
        e = core.good_epoch(core.to_epoch(o.get("create_time")))
        if cid is None or e is None:
            ctx.drop("null_ts")
            continue
        fo = folds.get(cid)
        if fo is None:
            fo = folds[cid] = Fold()
        fo.add(role, e, (convs.get(cid) or {}).get("model") or safe_model(o.get("model_slug")))
    for cid, fo in folds.items():
        c = convs.get(cid) or {}
        for ev in fo.events(SRC, "chatgpt", c.get("model") or "chatgpt", "cloud", None, cid, "msgs", emit_session=False):
            ctx.emit(ev)
    return {"status": "done", "raw": raw_n}
