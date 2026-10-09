"""fs_births.py: file births and last-modified days folded per (depth-2 directory, day) (CONTRACT.md sections 1, 6).

v1.4: also emits `file_update` (one record per (depth-2 directory, day) of mtime days, counted only when the mtime day
differs from the birth day). Hosts am4 and fx99 are walked over ssh with fs_find.py shipped on stdin, folded here.

Uses GNU `find ... -exec stat --printf '%W|%Y|%s|%n\\0' -- {} +` (GNU find has no birth directive; stat %W is the
birth time on the ntfs3 mounts, 0 when unknown, then mtime is used). Only counts and bytes survive; file names are used for exclusion and to find the depth-2 directory, then
dropped. Directories on the never-walk list and credential-bearing files are excluded inside the find expression and
again in Python. Bulk copies (a birth second shared by many files) are flagged, not removed.
"""
import fnmatch
import json
import os
from collections import Counter

from knownworld import core
from knownworld import fs_find
from knownworld.fs_find import PRUNE_NAMES, EXCLUDE_NAMES  # noqa: F401

SRC = "fs_births"
BULK_SECOND_MIN = 100      # files sharing one birth second
BULK_FRACTION = 0.8        # of a (dir, day) group inside such seconds


def _is_git(p):
    from knownworld.git_repo import classify_dir
    return classify_dir(p) is not None


def _remote_host(ctx):
    h = ctx.item.get("host")
    return h if h in ("am4", "fx99") else None


def _src(label_path, disp, path, loose, home=None):
    return {"label": core.clip(os.path.basename(label_path.rstrip("/")) or "root", 30) + ("-loose" if loose else "")
            + "~" + core.sha1hex(label_path)[:4], "kind": "loose" if loose else "tree",
            "shard_key": label_path + ("/*" if loose else ""),
            "spec": {"path": path, "loose": loose, "home": home}}


def _enumerate_remote(ctx, rh):
    from knownworld import remote
    roots = ctx.item.get("roots", [])
    st = remote.ssh_stream(rh, {"cmd": "discover", "roots": roots}, 90, modules=("fs_find.py",))
    lines = list(st.lines())
    st.close()
    if st.timed_out or not lines:
        raise RuntimeError("ssh_discover_failed")
    d = json.loads(lines[-1])
    out, missing = [], 0
    for r in d["roots"]:
        p = r["path"]
        if not r["isdir"] or r["islink"]:
            missing += 1
            continue
        out.append(_src(p, None, p, False, d["home"]))
    if missing:
        ctx.warn("roots_missing:%d" % missing)
    return out


def enumerate_sources(ctx):
    item = ctx.item
    opts = item.get("options") or {}
    rh = _remote_host(ctx)
    if rh:
        return _enumerate_remote(ctx, rh)
    out, missing = [], 0
    for r in item.get("roots", []):
        p = os.path.normpath(os.path.expanduser(r))
        if not os.path.isdir(p):
            missing += 1
            continue
        out.append(_src(p, None, p, False))
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
            if any(fnmatch.fnmatch(n, pat) for pat in opts.get("exclude_patterns", [])):
                continue
            out.append(_src(p, None, p, False))
        if opts.get("loose_files"):
            out.append(_src(c, None, c, True))
    if missing:
        ctx.warn("roots_missing:%d" % missing)
    return out


def process_source(ctx, src, cursor):
    path, loose = src["spec"]["path"], src["spec"]["loose"]
    home = src["spec"].get("home")
    rh = _remote_host(ctx)
    if rh:
        host = rh
        disp = "~/" + path[len(home) + 1:] if home and path.startswith(home + "/") else path
    else:
        host, disp = core.host_and_rel(path, ctx.item["host"] if ctx.item["host"] in ("omen-c", "omen-e", "omen-linux")
                                       else "omen-linux")
    repo = "dir:%s:%s" % (host, core.clip(disp, 100))
    cap = (ctx.item.get("options") or {}).get("find_timeout_s", 900)
    reduced = ctx.time_left() + 40 < cap
    to = max(60, min(cap, ctx.time_left() + 40))
    if rh:
        from knownworld import remote
        st = remote.ssh_stream(rh, {"cmd": "walk", "path": path, "loose": loose, "timeout": to}, to + 30,
                               modules=("fs_find.py",))
    else:
        st = core.Stream(fs_find.find_argv(path, loose), to, env=dict(os.environ))
    groups, upd = {}, {}
    secs = Counter()
    raw = 0
    null_mt = 0
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
        # file_update: needs a real birth and a clean mtime on another day (1970/1980 mtimes are null)
        if be is None:
            continue
        if me is None:
            null_mt += 1
            continue
        if core.day_of(me) == core.day_of(be):
            continue
        uk = (d, core.day_of(me))
        u = upd.get(uk)
        if u is None:
            u = upd[uk] = [0, 0, me, Counter()]
        u[0] += 1
        u[1] += size
        u[2] = min(u[2], me)
        u[3][be] += 1
    st.close()
    if st.timed_out or (rh and st.rc == 124):
        if reduced and ctx.sources_this_slice:
            return {"status": "budget", "cursor": None}
        return {"status": "skipped", "reason": "timeout:find"}
    if st.rc not in (0, 1) and raw == 0:
        return {"status": "skipped", "reason": "find_error:" + core.err_class(st.err_head)}
    if rh and st.rc not in (0, 1) and st.rc is not None:
        return {"status": "skipped", "reason": "ssh_rc:%s" % st.rc}
    if null_mt:
        ctx.extra["update_null_mtime"] = ctx.extra.get("update_null_mtime", 0) + null_mt
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
    for (d, day), (n, size, e, sc) in sorted(upd.items()):
        in_bulk = sum(c for s, c in sc.items() if s in bulk_secs)
        ev = {"ts": core.iso(e), "kind": "file_update", "actor": {"class": "human", "name": "derek"}, "host": host,
              "repo": repo, "path": core.clip(d, 120), "magnitude": {"n": n, "bytes": size},
              "ref": core.sha1hex("%s|%s|%s|u" % (repo, d, day)), "src": SRC}
        if n >= 5 and in_bulk >= BULK_FRACTION * n:
            ev["meta"] = {"bulk_copy": True}
        ctx.emit(ev)
    return {"status": "done", "raw": raw}
