"""git_repo.py: git extractor (CONTRACT.md sections 1, 3, 4, 6).

Self-contained apart from core.py (concatenated for ssh shipping). Read-only git only: log, rev-list, for-each-ref,
rev-parse, ls-remote, cat-file; `clone --mirror` is exposed to clone_mirrors.py and is confined to cache/clones.
Never emits author emails, commit messages, diffs or file names below depth 2.
"""
import json
import os
import re
import sys
import time

try:
    from knownworld.core import *  # noqa: F401,F403
    from knownworld import core as _core
    globals().update({k: getattr(_core, k) for k in dir(_core) if k.startswith("_") and not k.startswith("__")})
except ImportError:  # shipped over ssh: core.py is concatenated ahead of this file
    pass

ALLOWED_SUB = {"log", "rev-list", "for-each-ref", "rev-parse", "ls-remote", "cat-file"}
MAX_DIRS_PER_COMMIT = 64
FMT = "%x01%H%x02%P%x02%an%x02%at%x02%ct%x02%(trailers:key=Co-Authored-By,valueonly)%x03"


def git_argv(path, sub, args):
    if sub not in ALLOWED_SUB:
        raise PermissionError("git subcommand not allowed")
    return ["git", "--no-pager", "--no-optional-locks", "--no-replace-objects", "-c", "core.quotepath=false",
            "-c", "core.fsmonitor=false", "-c", "gc.auto=0", "-C", path, sub] + list(args)


def git_out(path, sub, args, timeout):
    rc, out, errlen, to = run(git_argv(path, sub, args), timeout, env=dict(os.environ))
    return rc, out.decode("utf-8", "replace"), to


def clone_mirror(url, dest, timeout):
    """The only write git ever does: `clone --mirror` into cache/clones."""
    root = os.path.join(KW_ROOT, "cache", "clones")
    d = os.path.realpath(dest)
    if not d.startswith(root + os.sep):
        raise PermissionError("clone outside cache/clones refused")
    os.makedirs(root, exist_ok=True)
    argv = ["git", "-c", "gc.auto=0", "clone", "--mirror", "--quiet", url, d]
    rc, _, _, to = run(argv, timeout, env=dict(os.environ))
    return rc, to


# ---------------------------------------------------------------- repo discovery

def is_bare_like(p):
    return os.path.isfile(os.path.join(p, "HEAD")) and os.path.isdir(os.path.join(p, "objects")) \
        and os.path.isdir(os.path.join(p, "refs"))


def classify_dir(p):
    g = os.path.join(p, ".git")
    try:
        if os.path.isdir(g):
            return "repo"
        if os.path.isfile(g):
            return "worktree"
        if is_bare_like(p):
            return "bare"
    except OSError:
        return "error"
    return None


def discover(roots, scan_depth=0, exclude=()):
    """Expand roots (globs allowed) into [{path, kind}]. scan_depth 0: each root must itself be a repo;
    scan_depth n: also look at subdirectories down to n levels (repos are not descended into)."""
    import fnmatch
    import glob
    found, seen, not_repo, missing, excluded = [], set(), 0, 0, 0
    for r in roots:
        r = os.path.expanduser(r)
        for p in sorted(glob.glob(r)) if any(ch in r for ch in "*?[") else [r]:
            p = os.path.normpath(p)
            if not os.path.isdir(p):
                missing += 1
                continue
            stack = [(p, 0)]
            while stack:
                d, depth = stack.pop(0)
                if d in seen:
                    continue
                seen.add(d)
                if any(fnmatch.fnmatch(d, pat) for pat in exclude):
                    excluded += 1
                    continue
                kind = classify_dir(d)
                if kind in ("repo", "bare", "worktree"):
                    found.append({"path": d, "kind": kind})
                    continue
                if depth < scan_depth:
                    try:
                        names = sorted(os.listdir(d))
                    except OSError:
                        continue
                    for n in names:
                        c = os.path.join(d, n)
                        if n in SKIP_DIR_NAMES or is_never_walk(c) or is_credential_name(n):
                            continue
                        if os.path.isdir(c) and not os.path.islink(c):
                            stack.append((c, depth + 1))
                elif depth == 0:
                    not_repo += 1
    return {"repos": found, "not_repo": not_repo, "missing": missing, "excluded": excluded}


# ---------------------------------------------------------------- small file readers (never credentials)

def _read(p, limit=1 << 20):
    guard_read(p)
    with open(p, "rb") as f:
        return f.read(limit).decode("utf-8", "replace")


def read_remotes(gitdir):
    """Remote urls from <gitdir>/config. Only [remote "x"] url lines are looked at; userinfo is stripped."""
    try:
        txt = _read(os.path.join(gitdir, "config"))
    except (OSError, PermissionError):
        return []
    urls, in_remote = [], False
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("["):
            in_remote = bool(re.match(r'^\[remote\s+"', s))
            continue
        if in_remote:
            m = re.match(r"^url\s*=\s*(.+)$", s)
            if m:
                u = norm_remote(m.group(1))
                if u and u not in urls:
                    urls.append(u)
    return urls


def read_shallow(gitdir):
    try:
        txt = _read(os.path.join(gitdir, "shallow"))
    except (OSError, PermissionError):
        return []
    return [l.strip() for l in txt.splitlines() if re.match(r"^[0-9a-f]{40}$", l.strip())]


def birth_epoch(path):
    rc, out, _, to = run(["stat", "-c", "%W %Y", path], 30)
    if rc != 0:
        return None
    try:
        b, m = out.decode().split()
        b, m = int(b), int(m)
    except ValueError:
        return None
    return good_epoch(b if b > 0 else m)


def map_path(p):
    """A path as stored in a git file (posix or Windows drive form) -> local filesystem path or None."""
    if re.match(r"^[A-Za-z]:[\\/]", p):
        return win_path_to_mount(p)
    return p if p.startswith("/") else None


# ---------------------------------------------------------------- the per-repo extraction

def _dominant(dirs):
    best, bn = None, -1
    for d, n in dirs.items():
        if n > bn:
            best, bn = d, n
    return best


def _parse_log(stream, ident, rl, host, counters, with_numstat):
    commits = []
    cur = None
    in_header = False
    hdr = []

    def finish():
        nonlocal cur
        if cur is not None:
            commits.append(cur)
        cur = None

    for raw in stream.lines():
        line = raw.decode("utf-8", "replace")
        if in_header:
            hdr.append(line)
            if "\x03" in line:
                in_header = False
                text = "".join(hdr)
                hdr = []
                head, _, _ = text.partition("\x03")
                cur = _make_commit(head, ident)
            continue
        if line.startswith("\x01"):
            finish()
            hdr = [line[1:]]
            if "\x03" in line:
                head, _, _ = line[1:].partition("\x03")
                cur = _make_commit(head, ident)
                hdr = []
            else:
                in_header = True
            continue
        if cur is None or not with_numstat:
            continue
        s = line.rstrip("\n")
        if not s:
            continue
        parts = s.split("\t", 2)
        if len(parts) != 3:
            continue
        a, d, path = parts
        try:
            ia = int(a) if a != "-" else 0
            idl = int(d) if d != "-" else 0
        except ValueError:
            continue
        cur["files"] += 1
        cur["ins"] += ia
        cur["del"] += idl
        dd = depth2(os.path.dirname(path))
        cur["dirs"][dd] = cur["dirs"].get(dd, 0) + ia + idl + 1
    finish()
    return commits


def _make_commit(head, ident):
    f = head.split("\x02")
    if len(f) < 6:
        return {"sha": None}
    sha, parents, an, at, ct, trailers = f[0].strip(), f[1].split(), f[2], f[3], f[4], f[5]
    ai = None
    for t in trailers.splitlines():
        t = t.strip()
        if t:
            ai = ident.trailer(t)
            if ai:
                break
    return {"sha": sha, "parents": parents, "an": an, "at": at, "ct": ct, "ai": ai,
            "files": 0, "ins": 0, "del": 0, "dirs": {}}


def process_repo(path, host, disp, ident, opts=None):
    """Extract one repository. Returns {status, reason, repo, events, raw, warnings}."""
    opts = opts or {}
    log_timeout = opts.get("log_timeout_s", 600)
    rl = repo_local(host, disp)
    res = {"status": "ok", "reason": None, "repo": None, "events": [], "raw": 0, "warnings": []}
    kind = classify_dir(path)
    if kind is None or kind == "error":
        res.update(status="skipped", reason="not_a_repo" if kind is None else "io_error")
        return res
    now = int(time.time())

    if kind == "worktree":
        common = "unresolved"
        try:
            gd = _read(os.path.join(path, ".git")).strip()
            m = re.match(r"^gitdir:\s*(.+)$", gd)
            if m:
                mp = map_path(m.group(1).strip().replace("\\", "/"))
                if mp and os.path.isdir(mp):
                    cd = os.path.dirname(os.path.dirname(mp))
                    h2, r2 = host_and_rel(cd[:-5] if cd.endswith("/.git") else cd, host)
                    common = repo_local(h2, r2)
        except (OSError, PermissionError):
            pass
        res["repo"] = {"repo_local": rl, "host": host, "path": disp, "remotes": [], "roots": [], "root_tree": None,
                       "tip_tree": None, "shallow": False, "shallow_boundary": [], "is_bare": False,
                       "is_worktree": True, "common_dir": common, "empty": False, "first_ts": None, "last_ts": None,
                       "commits": 0, "refs": 0, "authors": {}, "third_party": False, "derek_share": 0.0}
        return res

    is_bare = kind == "bare"
    gitdir = path if is_bare else os.path.join(path, ".git")
    remotes = read_remotes(gitdir)
    shallow_b = read_shallow(gitdir)

    # refs
    rc, out, to = git_out(path, "for-each-ref", ["--format=%(refname)%00%(objectname)%00%(objecttype)"], 180)
    if to:
        res.update(status="skipped", reason="timeout:for-each-ref")
        return res
    refs, branch_tips = 0, {}
    if rc == 0:
        for ln in out.splitlines():
            p = ln.split("\x00")
            if len(p) != 3:
                continue
            refs += 1
            rn, sha, ot = p
            if ot != "commit":
                continue
            name = None
            if rn.startswith("refs/heads/"):
                name = rn[len("refs/heads/"):]
            elif rn.startswith("refs/remotes/"):
                rest = rn[len("refs/remotes/"):].split("/", 1)
                name = rest[1] if len(rest) == 2 else None
            if name and name != "HEAD" and not name.endswith("/HEAD"):
                branch_tips.setdefault(name, set()).add(sha)

    # log (numstat first; on timeout or a git error such as a partial clone with missing blobs, counts-free retry)
    with_numstat = True
    args = ["--all", "--topo-order", "--no-color", "--no-ext-diff", "--no-textconv", "--no-renames", "--numstat",
            "--format=" + FMT]
    st = Stream(git_argv(path, "log", args), log_timeout, env=dict(os.environ))
    commits = _parse_log(st, ident, rl, host, {}, True)
    rc = st.close()
    if st.timed_out or rc != 0:
        res["warnings"].append("numstat_skipped" if st.timed_out else "numstat_failed:" + err_class(st.err_head))
        with_numstat = False
        args2 = ["--all", "--topo-order", "--no-color", "--format=" + FMT]
        st = Stream(git_argv(path, "log", args2), min(log_timeout, 400), env=dict(os.environ))
        commits = _parse_log(st, ident, rl, host, {}, False)
        rc = st.close()
        if st.timed_out:
            res.update(status="skipped", reason="timeout:log")
            return res
    if rc != 0:
        cls = err_class(st.err_head)
        if not commits and cls in ("no_commits", "none"):
            pass  # an empty repository
        else:
            res["warnings"].append("log_failed:" + cls)
            if not commits:
                res.update(status="skipped", reason="git_error:" + cls)
                return res
    commits = [c for c in commits if c.get("sha")]
    res["raw"] = len(commits)
    rc2, out2, to2 = git_out(path, "rev-list", ["--count", "--all"], 120)
    if rc2 == 0 and out2.strip().isdigit() and int(out2.strip()) != len(commits):
        res["warnings"].append("commit_count_mismatch")

    # per-commit events + authorship tally
    authors, tp, human_c, ai_c = {}, 0, 0, 0
    ts_list, roots = [], []
    sb = set(shallow_b)
    idx = {}
    for c in commits:
        ae = good_epoch(int(c["at"]), now) if c["at"].lstrip("-").isdigit() else None
        ce = good_epoch(int(c["ct"]), now) if c["ct"].lstrip("-").isdigit() else None
        c["ae"] = ae
        cls, nm = ident.classify(c["an"])
        human_authored = None
        if c["ai"]:
            ai_c += 1
            if cls == "human":
                human_authored = True
                human_c += 1
            cls, nm = c["ai"]
        elif cls == "human":
            human_c += 1
        if cls == "third_party":
            tp += 1
        authors[cls] = authors.get(cls, 0) + 1
        if ae:
            ts_list.append(ae)
        if not c["parents"] and c["sha"] not in sb:
            roots.append((c["sha"], ae))
        dirs = c["dirs"]
        top = sorted(dirs.items(), key=lambda kv: -kv[1])
        capped = len(top) > MAX_DIRS_PER_COMMIT
        meta = {}
        if human_authored:
            meta["human_authored"] = True
        if capped:
            meta["files_capped"] = True
        if not with_numstat:
            meta["no_numstat"] = True
        ev = {"ts": iso(ae) if ae else None, "ts_author": iso(ae) if ae else None, "ts_commit": iso(ce) if ce else None,
              "kind": "commit", "actor": {"class": cls, "name": nm}, "host": host, "repo": None, "repo_local": rl,
              "path": clip(_dominant(dirs), 120) if dirs else None,
              "files": [clip(d, 120) for d, _ in top[:MAX_DIRS_PER_COMMIT]],
              "magnitude": {"n": 1, "files": c["files"], "ins": c["ins"], "del": c["del"]},
              "ref": c["sha"], "src": "git_repo"}
        if meta:
            ev["meta"] = meta
        res["events"].append(ev)
        idx[c["sha"]] = c

    total = len(commits)
    derek_share = round(1.0 - (tp / total), 4) if total else 0.0
    orgs = {remote_org(u) for u in remotes if remote_org(u)}
    derek_ident = (human_c + ai_c) > 0
    third = bool(total) and (derek_share < 0.05 or (bool(orgs) and not (orgs & ident.derek_orgs) and not derek_ident))

    # roots, trees
    root_shas = sorted(r for r, _ in roots)
    root_tree = tip_tree = None
    if root_shas:
        rc, out, to = git_out(path, "rev-parse", ["--verify", "-q", root_shas[0] + "^{tree}"], 60)
        root_tree = out.strip() if rc == 0 and re.match(r"^[0-9a-f]{40}$", out.strip()) else None
    rc, out, to = git_out(path, "rev-parse", ["--verify", "-q", "HEAD^{tree}"], 60)
    tip_tree = out.strip() if rc == 0 and re.match(r"^[0-9a-f]{40}$", out.strip()) else None

    # repo_born
    if roots:
        born = min((a for _, a in roots if a), default=None)
        born_ref = min(roots, key=lambda x: (x[1] is None, x[1] or 0, x[0]))[0]
    else:
        born, born_ref = (min(ts_list) if ts_list else None), sha1hex(rl)
    res["events"].append({"ts": iso(born) if born else None, "kind": "repo_born",
                          "actor": {"class": "human", "name": "derek"}, "host": host, "repo": None, "repo_local": rl,
                          "path": None, "magnitude": {"n": 1}, "ref": born_ref, "src": "git_repo"})

    # branches: unique-commit reachability by bitset, children before parents (topo order)
    names = sorted(branch_tips)
    bit_of = {n: 1 << i for i, n in enumerate(names)}
    tipbits = {}
    for n, shas in branch_tips.items():
        for s in shas:
            tipbits[s] = tipbits.get(s, 0) | bit_of[n]
    reach = {}
    for c in commits:
        b = reach.get(c["sha"], 0) | tipbits.get(c["sha"], 0)
        reach[c["sha"]] = b
        if b:
            for p in c["parents"]:
                reach[p] = reach.get(p, 0) | b
    uniq = {n: [0, None] for n in names}
    bit_to_name = {v: k for k, v in bit_of.items()}
    for c in commits:
        n = bit_to_name.get(reach.get(c["sha"], 0))
        if n is not None:
            u = uniq[n]
            u[0] += 1
            if c["ae"] and (u[1] is None or c["ae"] < u[1]):
                u[1] = c["ae"]
    for n in names:
        cnt, first = uniq[n]
        res["events"].append({"ts": iso(first) if first else None, "kind": "branch",
                              "actor": {"class": "human", "name": "derek"}, "host": host, "repo": None,
                              "repo_local": rl, "path": None, "magnitude": {"n": cnt},
                              "ref": sha1hex(rl + "|branch|" + n), "src": "git_repo"})

    # linked worktrees, read from the parent's .git/worktrees/*
    wtdir = os.path.join(gitdir, "worktrees")
    try:
        wnames = sorted(os.listdir(wtdir)) if os.path.isdir(wtdir) else []
    except OSError:
        wnames = []
    for wn in wnames:
        base = os.path.join(wtdir, wn)
        wpath, headref, unresolved = None, None, False
        try:
            g = _read(os.path.join(base, "gitdir")).strip().replace("\\", "/")
            wp = g[:-5] if g.endswith("/.git") else g
            wpath = map_path(wp)
            if wpath is None or not os.path.isdir(wpath):
                unresolved = True
        except (OSError, PermissionError):
            unresolved = True
        try:
            headref = _read(os.path.join(base, "HEAD")).strip()
        except (OSError, PermissionError):
            headref = None
        ts = None
        if headref and headref.startswith("ref: refs/heads/"):
            bn = headref[len("ref: refs/heads/"):]
            ts = uniq.get(bn, [0, None])[1]
        elif headref and re.match(r"^[0-9a-f]{40}$", headref) and headref in idx:
            ts = idx[headref]["ae"]
        if ts is None:
            ts = birth_epoch(wpath if (wpath and not unresolved) else base)
        if wpath:
            h2, r2 = host_and_rel(wpath, host)
            rel = r2[2:] if r2.startswith("~/") else r2
            wp_path = clip(depth2(rel), 120)
        else:
            wp_path = None
        ev = {"ts": iso(ts) if ts else None, "kind": "worktree", "actor": {"class": "human", "name": "derek"},
              "host": host, "repo": None, "repo_local": rl, "path": wp_path, "magnitude": {"n": 1},
              "ref": sha1hex(rl + "|worktree|" + wn), "src": "git_repo"}
        if unresolved:
            ev["meta"] = {"unresolved": True}
        res["events"].append(ev)

    res["repo"] = {"repo_local": rl, "host": host, "path": disp, "remotes": remotes, "roots": root_shas,
                   "root_tree": root_tree, "tip_tree": tip_tree, "shallow": bool(shallow_b),
                   "shallow_boundary": shallow_b, "is_bare": is_bare, "is_worktree": False, "common_dir": None,
                   "empty": total == 0, "first_ts": iso(min(ts_list)) if ts_list else None,
                   "last_ts": iso(max(ts_list)) if ts_list else None, "commits": total, "refs": refs,
                   "authors": authors, "third_party": third, "derek_share": derek_share}
    return res


# ---------------------------------------------------------------- run_item adapter (local side only)

SRC = "git_repo"


def _label(path):
    return "%s~%s" % (clip(os.path.basename(path.rstrip("/")) or "root", 36), sha1hex(path)[:4])


def _remote_host(ctx):
    h = ctx.item.get("host")
    return h if h in ("am4", "fx99") else None


def enumerate_sources(ctx):
    item = ctx.item
    sd = int((item.get("options") or {}).get("scan_depth", 0))
    rh = _remote_host(ctx)
    if rh:
        from knownworld import remote
        st = remote.ssh_stream(rh, {"cmd": "discover", "roots": item["roots"], "scan_depth": sd,
                                     "exclude": (item.get("options") or {}).get("exclude", [])}, 120)
        lines = list(st.lines())
        st.close()
        if st.timed_out or not lines:
            raise RuntimeError("ssh_discover_failed")
        d = json.loads(lines[-1])
    else:
        d = discover(item["roots"], sd, (item.get("options") or {}).get("exclude", []))
    ctx.extra["not_repos"] = d["not_repo"]
    ctx.extra["excluded"] = d.get("excluded", 0)
    if d["missing"]:
        ctx.warn("roots_missing:%d" % d["missing"])
    return [{"label": _label(r["path"]), "kind": "git", "shard_key": r["path"], "spec": r} for r in d["repos"]]


def process_source(ctx, src, cursor):
    item, spec = ctx.item, src["spec"]
    path = spec["path"]
    ident = ctx.get_ident()
    cap = (item.get("options") or {}).get("log_timeout_s", 600)
    rh = _remote_host(ctx)
    if rh:  # ssh runs must finish inside the Bash call: leave margin for the remote's other commands
        reduced = ctx.time_left() - 30 < cap
        log_to = max(60, min(cap, ctx.time_left() - 30))
    else:
        reduced = ctx.time_left() + 40 < cap
        log_to = max(60, min(cap, ctx.time_left() + 40))
    opts = {"log_timeout_s": log_to}
    if rh:
        from knownworld import remote
        from knownworld import allowlists as A
        st = remote.ssh_stream(rh, {"cmd": "repo", "path": path, "host": item["host"], "ident": ctx.ident_data,
                                    "opts": opts}, log_to + 90)
        end = None
        for raw in st.lines():
            try:
                o = json.loads(raw)
            except ValueError:
                ctx.drop("decode_errors")
                continue
            t = o.get("t")
            if t == "e":
                if A.validate_event(o["r"]) or A.scan_value(o["r"]):
                    ctx.extra["invalid_remote_records"] = ctx.extra.get("invalid_remote_records", 0) + 1
                else:
                    ctx.emit(o["r"])
            elif t == "repo":
                if A.validate_repo(o["r"]) or A.scan_value(o["r"]):
                    ctx.extra["invalid_remote_records"] = ctx.extra.get("invalid_remote_records", 0) + 1
                else:
                    ctx.emit_repo(o["r"])
            elif t == "end":
                end = o
        st.close()
        if st.timed_out:
            return {"status": "budget" if (reduced and ctx.sources_this_slice) else "skipped", "reason": "timeout:ssh"}
        if end is None:
            return {"status": "skipped", "reason": "ssh_no_result:" + err_class(st.err_head)}
        for w in end.get("warnings", []):
            ctx.warn(w)
        if end["status"] != "ok":
            return {"status": "skipped", "reason": end.get("reason")}
        return {"status": "done", "raw": end.get("raw", 0)}
    h, disp = host_and_rel(path, item["host"] if item["host"] in HOSTS_LOCAL else "omen-linux")
    o = item.get("options") or {}
    if o.get("host_override"):
        h, disp = o["host_override"], (o.get("display_map") or {}).get(path, os.path.basename(path))
    r = process_repo(path, h, disp, ident, opts)
    if r["status"] != "ok":
        if reduced and ctx.sources_this_slice and str(r["reason"]).startswith("timeout"):
            return {"status": "budget", "cursor": None}
        return {"status": "skipped", "reason": r["reason"]}
    for w in r["warnings"]:
        ctx.warn(w)
    for ev in r["events"]:
        ctx.emit(ev)
    if r["repo"]:
        ctx.emit_repo(r["repo"])
    return {"status": "done", "raw": r["raw"]}


HOSTS_LOCAL = ("omen-linux", "omen-c", "omen-e")


# ---------------------------------------------------------------- ssh entry (python3 - with KW_ARGS header)

def _emit(o):
    sys.stdout.write(json.dumps(o, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _remote_main(args):
    setup_env()
    cmd = args["cmd"]
    if cmd == "discover":
        _emit(discover(args["roots"], args.get("scan_depth", 0), args.get("exclude", [])))
        return 0
    if cmd == "repo":
        ident = Identity(args["ident"])
        host = args["host"]
        h, disp = host_and_rel(args["path"], host)
        r = process_repo(args["path"], host, disp, ident, args.get("opts") or {})
        for ev in r["events"]:
            _emit({"t": "e", "r": ev})
        if r["repo"]:
            _emit({"t": "repo", "r": r["repo"]})
        _emit({"t": "end", "status": r["status"], "reason": r["reason"], "raw": r["raw"], "warnings": r["warnings"]})
        return 0
    return 2


if __name__ == "__main__" and "KW_ARGS" in globals():
    sys.exit(_remote_main(KW_ARGS))  # noqa: F821
