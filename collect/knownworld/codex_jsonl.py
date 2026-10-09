"""codex_jsonl.py: Codex session rollouts, metadata only (CONTRACT.md sections 1, 2, 6).

Streams files that can reach gigabytes. The line envelope (timestamp, type, payload.type) is read from the head of
the line with a regex; a line is parsed as JSON only when it is a session_meta, a turn_context (model name) or a
token_count. Message bodies, arguments and outputs are never parsed. A source interrupted by the time budget saves
its byte offset and fold state in the checkpoint and resumes there.
"""
import json
import os
import re

from knownworld import core
from knownworld.chatfold import Fold, safe_model

SRC = "codex_jsonl"
HEAD_RE = re.compile(rb'^\{"timestamp":"([^"]+)"(?:,"ordinal":\d+)?,"type":"([a-z_]+)","payload":\{(?:"type":"([A-Za-z_]+)")?')
UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
TOOL_PTYPES = {"function_call", "custom_tool_call", "local_shell_call", "web_search_call", "tool_search_call"}
CHECK_EVERY = int(os.environ.get("KW_CHECK_EVERY", "4000"))


def enumerate_sources(ctx):
    out = []
    for root in ctx.item["roots"]:
        root = os.path.expanduser(root)
        for dp, dn, fn in os.walk(root):
            dn.sort()
            for n in sorted(fn):
                if not n.endswith(".jsonl") or core.is_credential_name(n):
                    continue
                full = os.path.join(dp, n)
                out.append({"label": "codex-" + core.sha1hex(full)[:10], "kind": "jsonl", "shard_key": full,
                            "spec": {"file": full}})
    return out


def _int(v):
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else None


def process_source(ctx, src, cursor):
    path = src["spec"]["file"]
    core.guard_read(path)
    item_host = ctx.item["host"] if ctx.item["host"] in ("omen-c", "omen-e", "omen-linux") else "omen-linux"
    st = {"off": 0, "raw": 0, "cwd": None, "sess": None, "model": None, "last_total": None, "cli": None, "prov": None,
          "first": None}
    fold = Fold()
    if cursor:
        st.update(cursor["st"])
        fold = Fold.from_state(cursor["fold"])
    stem = os.path.basename(path)[:-6]
    m = UUID_RE.search(stem)
    stem_sess = m.group(0) if m else None
    f = open(path, "rb")
    try:
        f.seek(st["off"])
        off, nl = st["off"], 0
        for raw in iter(f.readline, b""):
            nl += 1
            if nl % CHECK_EVERY == 0 and ctx.time_up():
                st["off"] = off  # start of this unprocessed line
                return {"status": "budget", "cursor": {"st": st, "fold": fold.to_state()}}
            off += len(raw)
            if raw.endswith(b"\n"):
                st["raw"] += 1
            hm = HEAD_RE.match(raw)
            if hm is None:
                continue
            tsr, typ, ptyp = hm.group(1).decode(), hm.group(2).decode(), (hm.group(3) or b"").decode()
            if typ == "session_meta" or typ == "turn_context" or (typ == "event_msg" and ptyp == "token_count"):
                try:
                    o = json.loads(raw)
                except ValueError:
                    ctx.drop("decode_errors")
                    continue
                p = o.get("payload") if isinstance(o.get("payload"), dict) else {}
                if typ == "session_meta":
                    if st["cwd"] is None and isinstance(p.get("cwd"), str):
                        st["cwd"] = p["cwd"]
                    for k in ("session_id", "id"):
                        if st["sess"] is None and isinstance(p.get(k), str) and UUID_RE.fullmatch(p[k]):
                            st["sess"] = p[k]
                    if isinstance(p.get("cli_version"), str):
                        st["cli"] = core.clip(p["cli_version"], 40)
                    if isinstance(p.get("model_provider"), str):
                        st["prov"] = safe_model(p["model_provider"])
                    continue
                if typ == "turn_context":
                    mm = safe_model(p.get("model"))
                    if mm:
                        st["model"] = mm
                    continue
                e = core.good_epoch(core.to_epoch(tsr))
                if e is None:
                    ctx.drop("null_ts")
                    continue
                info = p.get("info") if isinstance(p.get("info"), dict) else None
                if not info:
                    continue
                tot = info.get("total_token_usage") if isinstance(info.get("total_token_usage"), dict) else {}
                tt = _int(tot.get("total_tokens"))
                if tt is not None and tt == st["last_total"]:
                    continue
                st["last_total"] = tt
                last = info.get("last_token_usage") if isinstance(info.get("last_token_usage"), dict) else {}
                inp, cached, outp = _int(last.get("input_tokens")), _int(last.get("cached_input_tokens")), _int(last.get("output_tokens"))
                if inp is None and outp is None:
                    continue
                fold.add("assistant", e, st["model"], max(0, (inp or 0) - (cached or 0)), outp or 0, cached, n=0)
                continue
            role = None
            if typ == "event_msg":
                role = "user" if ptyp == "user_message" else "assistant" if ptyp == "agent_message" else None
            elif typ == "response_item" and ptyp in TOOL_PTYPES:
                role = "tool"
            if role is None:
                continue
            e = core.good_epoch(core.to_epoch(tsr))
            if e is None:
                ctx.drop("null_ts")
                continue
            fold.add(role, e, st["model"] if role == "assistant" else None)
    finally:
        f.close()
    session = st["sess"] or stem_sess or core.sha1hex(stem)[:32]
    host, p = (None, None)
    if st["cwd"]:
        host, p = core.surface_path(st["cwd"])
    host = host or item_host
    extra = {}
    if st["cli"]:
        extra["cli_version"] = st["cli"]
    if st["prov"]:
        extra["provider"] = st["prov"]
    for ev in fold.events(SRC, "codex", "codex", host, p, session, stem, extra_meta=extra or None):
        ctx.emit(ev)
    return {"status": "done", "raw": st["raw"]}
