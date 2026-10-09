"""claude_jsonl.py: Claude Code transcripts, metadata only (CONTRACT.md sections 1, 2, 6).

Live project directories and the archived zip (`unzip -Z1` to list, `unzip -p` for allowlisted members only; the
archive is never extracted). Reads, per line: type, timestamp, sessionId, isSidechain, cwd, message.role,
message.model, message.usage.*, the `type` of content items (to tell tool results from prompts) and the `name` of
tool_use items, plus requestId as an in-memory dedupe key for usage only (a streamed reply is logged as several lines
that repeat one usage). Message text is never read, kept or emitted.
"""
import json
import os
import re

from knownworld import core
from knownworld.chatfold import Fold, safe_tool

SRC = "claude_jsonl"
ZIP_MEMBER_RE = re.compile(r"(^|/)\.claude/projects/.+\.jsonl$")
UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def _glob_escape(name):
    return re.sub(r"([\\\[\]\*\?])", r"\\\1", name)


def _project_surface(proj, item_host):
    """Fallback (host, path) from a project directory name when no cwd was seen."""
    m = re.match(r"^([A-Za-z])--(.*)$", proj)
    if m:
        host = core.drive_to_host(m.group(1)) or item_host
        rest = m.group(2)
    else:
        host = item_host
        rest = re.sub(r"^-?(home-[^-]+-|Users-[^-]+-)", "", proj).lstrip("-")
    if "-" in rest:
        a, b = rest.split("-", 1)
        rest = a + "/" + b
    return host, core.clip(core.depth2(rest), 120)


def enumerate_sources(ctx):
    item = ctx.item
    opts = item.get("options") or {}
    out = []
    if opts.get("zip"):
        zp = opts["zip"]
        rc, data, errlen, to = core.run(["unzip", "-Z1", zp], 300)
        if rc != 0 or to:
            raise RuntimeError("unzip_list_failed")
        for name in data.decode("utf-8", "replace").splitlines():
            if ZIP_MEMBER_RE.search(name) and not core.is_credential_name(name):
                proj = name.split(".claude/projects/", 1)[1].split("/", 1)[0]
                out.append({"label": "zip-" + core.sha1hex(name)[:10], "kind": "jsonl_zip", "shard_key": name,
                            "spec": {"zip": zp, "member": name, "project": proj}})
        return out
    for root in item["roots"]:
        root = os.path.expanduser(root)
        is_projects = os.path.basename(root.rstrip("/")) == "projects" or opts.get("projects_dir")
        for dp, dn, fn in os.walk(root):
            dn.sort()
            dn[:] = [d for d in dn if not core.is_never_walk(os.path.join(dp, d))]
            for n in sorted(fn):
                if not n.endswith(".jsonl") or core.is_credential_name(n):
                    continue
                full = os.path.join(dp, n)
                rel = os.path.relpath(full, root)
                proj = rel.split(os.sep, 1)[0] if is_projects else os.path.basename(root.rstrip("/"))
                out.append({"label": "jsonl-" + core.sha1hex(full)[:10], "kind": "jsonl", "shard_key": full,
                            "spec": {"file": full, "project": proj}})
    return out


def _content_kind(content):
    """(is_tool_result_only, {tool name: count}) from a message.content value; text is never touched."""
    if not isinstance(content, list):
        return False, None
    tools, results, other = {}, 0, 0
    for c in content:
        if not isinstance(c, dict):
            other += 1
            continue
        t = c.get("type")
        if t == "tool_use":
            nm = safe_tool(c.get("name"))
            tools[nm] = tools.get(nm, 0) + 1
        elif t == "tool_result":
            results += 1
        else:
            other += 1
    return (results > 0 and other == 0), (tools or None)


def process_source(ctx, src, cursor):
    spec = src["spec"]
    item = ctx.item
    item_host = item["host"] if item["host"] in ("omen-c", "omen-e", "omen-linux") else "omen-linux"
    is_zip = src["kind"] == "jsonl_zip"
    name = spec["member"] if is_zip else spec["file"]
    stem = os.path.basename(name)[:-6]
    timeout = ctx.src_timeout(900)
    fold = Fold()
    stream = None
    if is_zip:
        stream = core.Stream(["unzip", "-p", spec["zip"], _glob_escape(name)], timeout, env=dict(os.environ))
        lines = stream.lines()
    else:
        core.guard_read(name)
        f = open(name, "rb")
        lines = iter(f.readline, b"")
    raw_lines = off = 0
    cwd = sess = None
    sidechain = False
    ver_seen = False
    decode_logged = 0
    try:
        for raw in lines:
            if raw.endswith(b"\n"):
                raw_lines += 1
            try:
                o = json.loads(raw)
            except ValueError:
                ctx.drop("decode_errors")
                if decode_logged < 5:
                    ctx.log("decode_error offset=%d" % off)
                    decode_logged += 1
                off += len(raw)
                continue
            off += len(raw)
            if not isinstance(o, dict):
                continue
            if cwd is None and isinstance(o.get("cwd"), str):
                cwd = o["cwd"]
            if sess is None and isinstance(o.get("sessionId"), str) and UUID_RE.fullmatch(o["sessionId"]):
                sess = o["sessionId"]
            t = o.get("type")
            if t not in ("user", "assistant"):
                continue
            if o.get("isSidechain") is True:
                sidechain = True
            e = core.good_epoch(core.to_epoch(o.get("timestamp")))
            if e is None:
                ctx.drop("null_ts")
                continue
            m = o.get("message")
            if not isinstance(m, dict):
                m = {}
            if t == "assistant":
                u = m.get("usage") if isinstance(m.get("usage"), dict) else {}
                tin = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) if u else None
                tout = u.get("output_tokens") if u else None
                tc = u.get("cache_read_input_tokens") if u else None
                _, tools = _content_kind(m.get("content"))
                rq = o.get("requestId")
                fold.add("assistant", e, m.get("model"), tin if isinstance(tin, int) else None,
                         tout if isinstance(tout, int) else None, tc if isinstance(tc, int) else None, tools,
                         req=rq if isinstance(rq, str) else None)
            else:
                only_results, _ = _content_kind(m.get("content"))
                fold.add("tool" if only_results else "user", e)
    finally:
        if stream is None:
            f.close()
    if stream is not None:
        stream.close()
        if stream.timed_out:
            return {"status": "skipped", "reason": "timeout:unzip"}
        if stream.rc not in (0, None) and raw_lines == 0:
            return {"status": "skipped", "reason": "unzip_error"}
    session = sess or (stem if UUID_RE.fullmatch(stem) else core.sha1hex(stem)[:32])
    host, path = None, None
    if cwd:
        host, path = core.surface_path(cwd)
    if not path or path == ".":
        h2, p2 = _project_surface(spec["project"], item_host)
        host, path = host or h2, p2
    host = host or item_host
    for ev in fold.events(SRC, "claude", "claude", host, path, session, stem, sidechain=sidechain,
                          source="zip" if is_zip else "live"):
        ctx.emit(ev)
    return {"status": "done", "raw": raw_lines}
