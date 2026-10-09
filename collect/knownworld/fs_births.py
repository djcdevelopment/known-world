"""fs_births.py: file birth times folded per (depth-2 directory, day) (CONTRACT.md sections 1, 6).

Uses GNU `find ... -exec stat --printf '%W|%Y|%s|%n\\0' -- {} +` (GNU find has no birth directive; stat %W is the
birth time on the ntfs3 mounts, 0 when unknown, then mtime is used). Only counts and bytes survive; file names are used for exclusion and to find the depth-2 directory, then
dropped. Directories on the never-walk list and credential-bearing files are excluded inside the find expression and
again in Python. Bulk copies (a birth second shared by many files) are flagged, not removed.
"""
import os
from collections import Counter

from knownworld import core

SRC = "fs_births"
BULK_SECOND_MIN = 100      # files sharing one birth second
BULK_FRACTION = 0.8        # of a (dir, day) group inside such seconds
PRUNE_NAMES = [".git", "node_modules", "models", "checkpoints", "venvs", ".venv", ".cache"]
EXCLUDE_NAMES = [".credentials.json", "auth.json", "callers.json*", "*.pfx", "*.secret", "*.key", ".env*", "*.caddy",
                 ".git-credentials", "*.safetensors", "*.gguf", "*.pem"]


def _is_git(p):
    from knownworld.git_repo import classify_dir
    return classify_dir(p) is not None


def enumerate_sources(ctx):
    item = ctx.item
    opts = item.get("options") or {}
    out, missing = [], 0
    for r in item.get("roots", []):
        p = os.path.normpath(os.path.expanduser(r))
        if not os.path.isdir(p):
            missing += 1
            continue
        out.append({"label": core.clip(os.path.basename(p), 36) + "~" + core.sha1hex(p)[:4], "kind": "tree",
                    "shard_key": p, "spec": {"path": p, "loose": False}})
    for c in opts.get("children_of", []):
        c = os.path.normpath(os.path.expanduser(c))
        try:
            names = sorted(os.listdir(c))
        except OSError:
            missing += 1
            continue
        for n in names:
            p = os.path.join(c, n)
            if n in core.SKIP_DIR_NAMES or core.is_credential_name(n) or core.is_never_walk(p) or not os.path.isdir(p) \
                    or os.path.islink(p):
                continue
            if n in opts.get("exclude_children", []) or _is_git(p):
                continue
            out.append({"label": core.clip(n, 36) + "~" + core.sha1hex(p)[:4], "kind": "tree", "shard_key": p,
                        "spec": {"path": p, "loose": False}})
        if opts.get("loose_files"):
            out.append({"label": core.clip(os.path.basename(c), 30) + "-loose~" + core.sha1hex(c)[:4], "kind": "loose",
                        "shard_key": c + "/*", "spec": {"path": c, "loose": True}})
    if missing:
        ctx.warn("roots_missing:%d" % missing)
    return out


def _find_argv(path, loose):
    if loose:
        argv = ["find", path, "-maxdepth", "1", "-type", "f"]
    else:
        prune = []
        for n in PRUNE_NAMES:
            prune += ["-name", n, "-o"]
        prune += ["-path", "*/ComfyUI/models"]
        argv = ["find", path, "-xdev", "(", "-type", "d", "(", *prune, ")", "-prune", ")", "-o", "-type", "f"]
    for n in EXCLUDE_NAMES:
        argv += ["!", "-name", n]
    return argv + ["-exec", "stat", "--printf", "%W|%Y|%s|%n\\0", "--", "{}", "+"]


def process_source(ctx, src, cursor):
    path, loose = src["spec"]["path"], src["spec"]["loose"]
    host, disp = core.host_and_rel(path, ctx.item["host"] if ctx.item["host"] in ("omen-c", "omen-e", "omen-linux") else "omen-linux")
    if loose:
        top_disp = disp
    else:
        top_disp = disp
    repo = "dir:%s:%s" % (host, core.clip(top_disp, 100))
    cap = (ctx.item.get("options") or {}).get("find_timeout_s", 900)
    reduced = ctx.time_left() + 40 < cap
    to = max(60, min(cap, ctx.time_left() + 40))
    st = core.Stream(_find_argv(path, loose), to, env=dict(os.environ))
    groups = {}
    secs = Counter()
    raw = 0
    for rec in st.records():
        raw += 1
        parts = rec.split(b"|", 3)
        if len(parts) != 4:
            continue
        try:
            b = float(parts[0])
            m = float(parts[1])
            size = int(parts[2])
        except ValueError:
            continue
        full = parts[3].decode("utf-8", "replace")
        rel = full[len(path) + 1:] if full.startswith(path + "/") else os.path.basename(full)
        if core.is_credential_name(rel):
            continue
        be = core.good_epoch(int(b)) if b > 0 else None
        me = core.good_epoch(int(m))
        e = be if be is not None else me
        if e is None:
            ctx.drop("null_ts")
            continue
        d = "." if loose else core.depth2(os.path.dirname(rel))
        key = (d, core.day_of(e))
        g = groups.get(key)
        if g is None:
            g = groups[key] = [0, 0, e, 0, Counter()]
        g[0] += 1
        g[1] += size
        g[2] = min(g[2], e)
        if be is None:
            g[3] += 1
        else:
            secs[be] += 1
            g[4][be] += 1
    st.close()
    if st.timed_out:
        if reduced and ctx.sources_this_slice:
            return {"status": "budget", "cursor": None}
        return {"status": "skipped", "reason": "timeout:find"}
    if st.rc not in (0, 1) and raw == 0:
        return {"status": "skipped", "reason": "find_error:" + core.err_class(st.err_head)}
    bulk_secs = {s for s, c in secs.items() if c >= BULK_SECOND_MIN}
    for (d, day), (n, size, e, nb, sc) in sorted(groups.items()):
        in_bulk = sum(c for s, c in sc.items() if s in bulk_secs)
        meta = {}
        if n >= 5 and in_bulk >= BULK_FRACTION * max(1, n - nb):
            meta["bulk_copy"] = True
        if nb:
            meta["birth_missing"] = True
        ev = {"ts": core.iso(e), "kind": "file_birth", "actor": {"class": "human", "name": "derek"}, "host": host,
              "repo": repo, "path": core.clip(d, 120), "magnitude": {"n": n, "bytes": size},
              "ref": core.sha1hex("%s|%s|%s" % (repo, d, day)), "src": SRC}
        if meta:
            ev["meta"] = meta
        ctx.emit(ev)
    return {"status": "done", "raw": raw}
