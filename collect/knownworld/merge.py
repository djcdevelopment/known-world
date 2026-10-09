#!/usr/bin/env python3
"""merge.py: the deterministic Merge step of the Known World corpus run (CONTRACT.md sections 3, 4, 7).

Reads corpus/raw/<item>/{events.ndjson, repos.ndjson, manifest.json} and collect/knownworld/identity.json, writes
corpus/merged/{events.ndjson, repos.json, actors.json, hosts.json, sessions.json, stats.json}. Standard library only.
No clock, no network, no randomness: the same raw corpus gives byte-identical output. Prints counts only.

What it does, in order:
  1. identity: re-applies identity.json to every actor (humans -> derek, unknown people -> sha1(name)[:12]).
  2. lineage components: union-find over repo records. Links, strongest first:
       root             shared root-commit sha (CONTRACT section 3)
       worktree         a linked worktree record and the repo its common_dir names
       sha_overlap      a commit sha seen in two repo records (shallow clones have no usable roots)
       shallow_boundary a shallow clone's boundary sha is a commit of another record
       shallow_remote   a shallow clone with no sha link joins the non-shallow record with the same remote URL
       squash_remote / squash_root_tree
                        squash-imported mirrors (path holds 'private-migration-') join by remote URL, else root_tree
     Name-only matches, remote matches between records that share no history, and equal root trees outside squash
     mirrors are never merged: they are written as {"link": "candidate"} records.
     Lineage id = smallest root sha of the component; components with no root commit get dir:<host>:<path>.
  3. events: commits fold per sha (earliest ts, meta.hosts); hearth/continuity events, chat sessions and messages
     (zip + live trees) dedupe on (kind, ref); repo_born folds per lineage; branch events dedupe per (lineage, ts)
     across copies; null-ts events are dropped and counted; chat, deepagents and ledger events join a lineage by
     (host, depth-2 path) where a repo owns that path.
Rootless components (empty repos, shallow clones with no shared history) get github:<owner>/<name> when a
     remote names one, else dir:<host>:<path>; repos.json marks them rooted=false.
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
KW_ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(KW_ROOT, "corpus", "raw")
OUT = os.path.join(KW_ROOT, "corpus", "merged")
IDENTITY = os.path.join(HERE, "identity.json")

HOST_RANK = {"omen-linux": 0, "omen-c": 1, "omen-e": 2, "am4": 3, "fx99": 4, "github": 5, "cloud": 6}
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbf2156"
HEX12 = re.compile(r"^[0-9a-f]{12}$")
GENERIC_NAMES = {"work", "src", "repo", "repos", "git", "test", "tests", "tmp", "temp", "app", "root", "main", "code"}
KIND_ORDER = {"repo_born": 0, "branch": 1, "worktree": 2, "commit": 3, "file_birth": 4, "file_update": 4, "chat_session": 5,
              "chat_msg": 6, "offload_call": 7, "receipt": 8, "run": 9}


def sha1_12(s):
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:12]


def jdump(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def hrank(h):
    return HOST_RANK.get(h, 9)


def pkey(host, path):
    """Join key: Windows hosts compare paths case-insensitively."""
    return (host, path.lower() if host in ("omen-c", "omen-e") else path)


# ---------------------------------------------------------------- identity (CONTRACT section 4)

class Identity:
    def __init__(self, path):
        d = json.load(open(path))
        self.humans = {h.lower() for h in d.get("human_names", [])}
        self.rules = [(re.compile(r["regex"], re.I), r["class"]) for r in d.get("rules", [])]
        self.derek_orgs = {o.lower() for o in d.get("derek_orgs", [])}
        self.fixed = Counter()

    def apply(self, a, src=None):
        cls, nm = a.get("class"), a.get("name")
        if not isinstance(nm, str) or not nm:
            self.fixed["empty_name"] += 1
            return {"class": "third_party", "name": sha1_12("unknown")}
        if nm.lower() in self.humans:
            if (cls, nm) != ("human", "derek"):
                self.fixed["human_to_derek"] += 1
            return {"class": "human", "name": "derek"}
        if cls == "human":
            self.fixed["unknown_human_to_third_party"] += 1
            return {"class": "third_party", "name": sha1_12(nm)}
        if cls == "third_party":
            if not HEX12.match(nm):
                self.fixed["third_party_name_hashed"] += 1
                return {"class": "third_party", "name": sha1_12(nm)}
            return a
        if src != "git_repo":
            return a   # chat/ledger actors are the agent class by construction; rules classify git authors only
        for rx, rcls in self.rules:
            if rx.search(nm):
                if rcls != cls:
                    self.fixed["class_by_rule"] += 1
                    return {"class": rcls, "name": nm}
                break
        return a


# ---------------------------------------------------------------- union-find

class UF:
    def __init__(self):
        self.p = {}
        self.basis = Counter()

    def add(self, x):
        self.p.setdefault(x, x)

    def find(self, x):
        p = self.p
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a, b, basis):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if rb < ra:
            ra, rb = rb, ra
        self.p[rb] = ra
        self.basis[basis] += 1
        return True


# ---------------------------------------------------------------- helpers

def remote_key(u):
    """URL-like remote -> 'host/owner/name' lower case; None for local paths and unusable values."""
    if not isinstance(u, str) or "://" not in u:
        return None
    s = u.split("://", 1)[1].lower().rstrip("/")
    if s.endswith(".git"):
        s = s[:-4]
    if "@" in s:
        s = s.split("@", 1)[1]
    return s or None


def remote_org(key):
    parts = key.split("/")
    return parts[1] if len(parts) >= 3 else None


def norm_path(p):
    if not isinstance(p, str):
        return ""
    p = p.replace("\\", "/")
    if p == "~":
        return ""
    if p.startswith("~/"):
        p = p[2:]
    return p.strip("/")


def basename(p):
    n = norm_path(p).rsplit("/", 1)[-1].lower()
    return n[:-4] if n.endswith(".git") else n


def read_ndjson(path):
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if raw:
                yield json.loads(raw)


def ts_min(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a if a <= b else b


def ts_max(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a if a >= b else b


# ---------------------------------------------------------------- merge

def merge(raw_dir=RAW, out_dir=OUT):
    ident = Identity(IDENTITY)
    items = sorted(d for d in os.listdir(raw_dir) if os.path.isfile(os.path.join(raw_dir, d, "manifest.json")))
    manifests = {i: json.load(open(os.path.join(raw_dir, i, "manifest.json"))) for i in items}
    stats = {"items": {}}

    # ---- repo records
    nodes = {}
    dup_nodes = 0
    for it in items:
        p = os.path.join(raw_dir, it, "repos.ndjson")
        if not os.path.isfile(p):
            continue
        for r in read_ndjson(p):
            k = r["repo_local"]
            if k in nodes:
                dup_nodes += 1
                continue
            r = dict(r)
            r["_item"] = it
            nodes[k] = r
    stats["repo_records"] = len(nodes)
    stats["repo_records_duplicate_skipped"] = dup_nodes

    # ---- events (loaded once, tagged by item)
    evs = []
    for it in items:
        p = os.path.join(raw_dir, it, "events.ndjson")
        if not os.path.isfile(p):
            continue
        n = 0
        for e in read_ndjson(p):
            evs.append((it, e))
            n += 1
        stats["items"][it] = {"events_loaded": n, "manifest_events": manifests[it].get("events"),
                              "status": manifests[it].get("status"), "src": manifests[it].get("src")}
    stats["events_loaded"] = len(evs)

    # ---- lineage components
    uf = UF()
    for k in nodes:
        uf.add(k)
    root_owner = {}
    for k in sorted(nodes):
        for r in nodes[k]["roots"]:
            if r in root_owner:
                uf.union(k, root_owner[r], "root")
            else:
                root_owner[r] = k
    for k in sorted(nodes):
        r = nodes[k]
        if r["is_worktree"] and isinstance(r.get("common_dir"), str) and r["common_dir"] in nodes:
            uf.union(k, r["common_dir"], "worktree")
    commit_owner = {}
    commit_copies = Counter()   # repo_local -> raw commit events
    for it, e in evs:
        if e["kind"] != "commit" or e.get("repo_local") not in nodes:
            continue
        rl, sha = e["repo_local"], e["ref"]
        commit_copies[rl] += 1
        o = commit_owner.get(sha)
        if o is None:
            commit_owner[sha] = rl
        elif o != rl:
            uf.union(rl, o, "sha_overlap")
    for k in sorted(nodes):
        for b in nodes[k]["shallow_boundary"]:
            o = commit_owner.get(b)
            if o is not None:
                uf.union(k, o, "shallow_boundary")
    by_remote = defaultdict(list)
    for k in sorted(nodes):
        for u in nodes[k]["remotes"]:
            rk = remote_key(u)
            if rk:
                by_remote[rk].append(k)
    for k in sorted(nodes):
        r = nodes[k]
        if not r["shallow"]:
            continue
        me = uf.find(k)
        if any(not nodes[m]["shallow"] and uf.find(m) == me for m in nodes):
            continue
        for u in r["remotes"]:
            rk = remote_key(u)
            for m in by_remote.get(rk, []):
                if m != k and not nodes[m]["shallow"]:
                    uf.union(k, m, "shallow_remote")
                    break
    by_tree = defaultdict(list)
    for k in sorted(nodes):
        t = nodes[k].get("root_tree")
        if t and t != EMPTY_TREE:
            by_tree[t].append(k)
    for k in sorted(nodes):
        if "private-migration-" not in nodes[k]["path"]:
            continue
        done = False
        for u in nodes[k]["remotes"]:
            rk = remote_key(u)
            for m in by_remote.get(rk, []):
                if m != k and "private-migration-" not in nodes[m]["path"]:
                    uf.union(k, m, "squash_remote")
                    done = True
        if not done:
            for m in by_tree.get(nodes[k].get("root_tree"), []):
                if m != k and "private-migration-" not in nodes[m]["path"]:
                    uf.union(k, m, "squash_root_tree")

    comp_members = defaultdict(list)
    for k in sorted(nodes):
        comp_members[uf.find(k)].append(k)

    def lineage_id(members):
        roots = sorted({r for m in members for r in nodes[m]["roots"]})
        if roots:
            return roots[0], True
        gh = sorted({remote_key(u) for m in members for u in nodes[m]["remotes"]
                     if (remote_key(u) or "").startswith("github.com/")})
        if gh and len(gh[0].split("/")) == 3:
            return ("github:" + gh[0].split("/", 1)[1])[:106], False
        first = sorted(members, key=lambda m: (hrank(nodes[m]["host"]), nodes[m]["path"], m))[0]
        return ("dir:%s:%s" % (nodes[first]["host"], nodes[first]["path"]))[:110], False

    lin_of_node, lin_info = {}, {}
    for c, members in sorted(comp_members.items()):
        lid, rooted = lineage_id(members)
        if lid in lin_info:   # two rootless components with one display path: keep both, disambiguated
            lid = lid[:104] + "#" + sha1_12(c)[:5]
        lin_info[lid] = {"members": members, "rooted": rooted}
        for m in members:
            lin_of_node[m] = lid

    # ---- candidate links (never merged)
    cands = {}

    def cand(a, b, basis, key):
        if a == b:
            return
        if b < a:
            a, b = b, a
        cands.setdefault((a, b, basis), key)

    def pairs(ls):
        ls = sorted(ls)
        for i in range(len(ls)):
            for j in range(i + 1, len(ls)):
                yield ls[i], ls[j]

    for rk, ms in sorted(by_remote.items()):
        for a, b in pairs({lin_of_node[m] for m in ms}):
            cand(a, b, "remote", rk)
    for t, ms in sorted(by_tree.items()):
        for a, b in pairs({lin_of_node[m] for m in ms}):
            cand(a, b, "root_tree", t[:12])
    by_name = defaultdict(set)
    for k, r in nodes.items():
        if r["host"] == "github" or r["is_worktree"]:
            continue
        n = basename(r["path"])
        if len(n) >= 3 and n not in GENERIC_NAMES:
            by_name[n].add(lin_of_node[k])
    for n, ls in sorted(by_name.items()):
        for a, b in pairs(ls):
            cand(a, b, "name", n)
    node_by_abs = {}
    for k, r in nodes.items():
        if r["host"] == "omen-linux" and r["path"].startswith("~/"):
            node_by_abs["/home/derek/" + r["path"][2:].rstrip("/")] = k
    for k, r in sorted(nodes.items()):
        for u in r["remotes"]:
            if isinstance(u, str) and u.startswith("/"):
                m = node_by_abs.get(u.rstrip("/"))
                if m:
                    cand(lin_of_node[k], lin_of_node[m], "local_remote_path", basename(u))

    # ---- path -> lineage index for chat / ledger joins
    lin_commits_decl = Counter()
    for k, r in nodes.items():
        lin_commits_decl[lin_of_node[k]] += r["commits"]
    path_idx = defaultdict(set)
    for k, r in nodes.items():
        if r["host"] == "github" or r["is_worktree"]:
            continue
        np_ = norm_path(r["path"])
        if np_ and len(np_.split("/")) <= 2:
            path_idx[pkey(r["host"], np_)].add(lin_of_node[k])

    dir_idx = {}
    for it, e in evs:
        if e["kind"] in ("file_birth", "file_update") and isinstance(e.get("repo"), str) and e["repo"].startswith("dir:"):
            _, dh, dp = e["repo"].split(":", 2)
            dir_idx[pkey(dh, dp)] = e["repo"]

    def join_path(host, path):
        if not path or path == ".":
            return None, "no_path"
        keys = [path] + ([path.split("/")[0]] if "/" in path else [])
        for c in keys:
            ls = path_idx.get(pkey(host, c))
            if ls:
                if len(ls) == 1:
                    return next(iter(ls)), "joined"
                return max(sorted(ls), key=lambda x: lin_commits_decl[x]), "joined_ambiguous"
        d = dir_idx.get(pkey(host, path))
        if d:
            return d, "joined_dir"
        return None, "unmatched"

    remote_lin = defaultdict(set)
    for rk, ms in by_remote.items():
        for m in ms:
            remote_lin[rk].add(lin_of_node[m])

    # ---- fold events
    commit_best = {}            # sha -> [rank, event, hosts]
    born = {}                   # lineage -> [ts, event, hosts]
    branch_groups = defaultdict(lambda: defaultdict(dict))   # lineage -> ts -> repo_local -> [events]
    simple = {}                 # (kind, ref) -> [item, event]
    dropped_null = Counter()
    dup = Counter()
    join_stats = defaultdict(Counter)
    zip_live_overlap = Counter()
    dup_items = Counter()
    gh_match = Counter()
    out_events = []

    def rank_commit(e):
        m = e.get("meta") or {}
        return (e.get("ts") is None, e.get("ts") or "", 1 if m.get("no_numstat") else 0, hrank(e["host"]))

    for it, e in evs:
        e = dict(e)
        e["actor"] = ident.apply(e["actor"], e["src"])
        kind, src = e["kind"], e["src"]
        rl = e.get("repo_local")
        if kind == "commit":
            e["repo"] = lin_of_node.get(rl)
            r = rank_commit(e)
            cur = commit_best.get(e["ref"])
            if cur is None:
                commit_best[e["ref"]] = [r, e, {e["host"]}]
            else:
                dup["commit"] += 1
                cur[2].add(e["host"])
                if r < cur[0]:
                    cur[0], cur[1] = r, e
            continue
        if kind == "repo_born" and src == "git_repo":
            lid = lin_of_node.get(rl)
            e["repo"] = lid
            cur = born.get(lid)
            if cur is None:
                born[lid] = [e.get("ts"), e, {e["host"]}]
            else:
                dup["repo_born"] += 1
                cur[2].add(e["host"])
                if e.get("ts") is not None and (cur[0] is None or e["ts"] < cur[0]):
                    cur[0], cur[1] = e["ts"], e
            continue
        if kind == "branch":
            lid = lin_of_node.get(rl)
            e["repo"] = lid
            if e.get("ts") is None:
                dropped_null[(src, kind)] += 1
                continue
            branch_groups[lid][e["ts"]].setdefault(rl, []).append(e)
            continue
        if src == "git_repo" and e.get("repo") is None:
            e["repo"] = lin_of_node.get(rl)   # worktree events
        if kind == "repo_born" and src == "github_api":
            lid = lin_of_node.get(rl)
            if lid is not None:
                gh_match["repo_local_node"] += 1
            else:
                m = re.match(r"^github:([^/]+/[^/]+)$", rl or "")
                ls = sorted(remote_lin.get("github.com/" + m.group(1).lower(), ())) if m else []
                if len(ls) == 1:
                    lid = ls[0]
                    gh_match["remote_url"] += 1
                elif len(ls) > 1:
                    lid = max(ls, key=lambda x: (lin_commits_decl[x], x))
                    gh_match["remote_url_ambiguous"] += 1
                else:
                    lid = (rl or "github:unknown")[:106]
                    gh_match["github_only"] += 1
            e["repo"] = lid
        elif kind in ("chat_msg", "chat_session", "run", "receipt", "offload_call") and e.get("repo") is None:
            lid, how = join_path(e["host"], e.get("path"))
            join_stats[src][how] += 1
            if lid is not None:
                e["repo"] = lid
        key = (kind, e["ref"])
        cur = simple.get(key)
        if cur is None:
            simple[key] = [it, e]
            continue
        dup[kind] += 1
        dup_items["%s:%s>%s" % (kind, cur[0], it)] += 1
        old = cur[1]
        if kind in ("chat_session", "chat_msg"):
            a, b = (old.get("meta") or {}).get("source"), (e.get("meta") or {}).get("source")
            if a != b and "zip" in (a, b):
                zip_live_overlap[kind] += 1
        n_old, n_new = old["magnitude"].get("n", 0), e["magnitude"].get("n", 0)
        if n_new > n_old or (n_new == n_old and (e.get("ts") or "~") < (old.get("ts") or "~")):
            simple[key] = [it, e]

    for sha, (r, e, hosts) in commit_best.items():
        e["meta"] = dict(e.get("meta") or {}, hosts=sorted(hosts, key=hrank))
        e.pop("repo_local", None)
        out_events.append(e)
    for lid, (tsv, e, hosts) in born.items():
        e["meta"] = dict(e.get("meta") or {}, hosts=sorted(hosts, key=hrank))
        e.pop("repo_local", None)
        out_events.append(e)
    branches_in = branches_out = 0
    for lid, by_ts in branch_groups.items():
        for tsv, by_rl in by_ts.items():
            branches_in += sum(len(v) for v in by_rl.values())
            best_rl = max(sorted(by_rl), key=lambda x: len(by_rl[x]))
            hosts = sorted({x["host"] for v in by_rl.values() for x in v}, key=hrank)
            for e in by_rl[best_rl]:
                e["meta"] = {"hosts": hosts}
                e.pop("repo_local", None)
                out_events.append(e)
                branches_out += 1
    dup["branch"] += branches_in - branches_out
    for (kind, ref), (it, e) in simple.items():
        e.pop("repo_local", None)
        out_events.append(e)

    kept = []
    for e in out_events:
        if e.get("ts") is None:
            dropped_null[(e["src"], e["kind"])] += 1
        else:
            kept.append(e)
    out_events = kept
    out_events.sort(key=lambda e: (e["ts"], KIND_ORDER.get(e["kind"], 9), e["src"], hrank(e["host"]), e["ref"],
                                   e.get("role", "")))

    # ---- per-lineage records
    lin_commit_stats = defaultdict(lambda: {"n": 0, "first": None, "last": None, "classes": Counter()})
    lin_kind = defaultdict(Counter)
    for e in out_events:
        lid = e.get("repo")
        if lid is None:
            continue
        lin_kind[lid][e["kind"]] += 1
        if e["kind"] == "commit":
            s = lin_commit_stats[lid]
            s["n"] += 1
            s["first"] = ts_min(s["first"], e["ts"])
            s["last"] = ts_max(s["last"], e["ts"])
            s["classes"][e["actor"]["class"]] += 1

    lin_rec = {}
    for lid in sorted(set(lin_info) | {e["repo"] for e in out_events if e.get("repo")}):
        kd = "git" if lid in lin_info else "dir" if lid.startswith("dir:") else "github"
        rec = {"id": lid, "kind": kd, "names": [], "paths": {}, "remotes": [], "roots": [], "region": None,
               "events": dict(sorted(lin_kind[lid].items()))}
        if kd == "git":
            ms = lin_info[lid]["members"]
            names, paths, remotes, roots = set(), defaultdict(list), set(), set()
            first = last = None
            copies = refs = wt = 0
            for m in ms:
                r = nodes[m]
                wt += 1 if r["is_worktree"] else 0
                if basename(r["path"]):
                    names.add(basename(r["path"]))
                paths[r["host"]].append(r["path"])
                for u in r["remotes"]:
                    remotes.add(remote_key(u) or u)
                roots.update(r["roots"])
                first, last = ts_min(first, r["first_ts"]), ts_max(last, r["last_ts"])
                copies += r["commits"]
                refs = max(refs, r["refs"])
            cs = lin_commit_stats.get(lid)
            tot = cs["n"] if cs else 0
            tp = cs["classes"].get("third_party", 0) if cs else 0
            share = round(1.0 - tp / tot, 4) if tot else 0.0
            orgs = {remote_org(x) for x in remotes if x.startswith("github.com/") and remote_org(x)}
            third = bool(tot) and (share < 0.05 or (bool(orgs) and not (orgs & ident.derek_orgs) and tot == tp))
            real = [m for m in ms if not nodes[m]["is_worktree"]]
            rec.update({"names": sorted(names), "paths": {h: sorted(set(v)) for h, v in sorted(paths.items())},
                        "remotes": sorted(remotes), "roots": sorted(roots), "rooted": lin_info[lid]["rooted"],
                        "members": len(ms), "worktree_records": wt,
                        "hosts": sorted({nodes[m]["host"] for m in ms}, key=hrank),
                        "first_ts": (cs["first"] if cs else None) or first,
                        "last_ts": (cs["last"] if cs else None) or last,
                        "commits": tot, "commit_copies": copies, "refs": refs,
                        "authors": dict(sorted(cs["classes"].items())) if cs else {},
                        "third_party": third, "derek_share": share,
                        "foreign_org": bool(orgs) and not (orgs & ident.derek_orgs),
                        "shallow_only": bool(real) and all(nodes[m]["shallow"] for m in real)})
        elif kd == "dir":
            host, path = lid.split(":", 2)[1], lid.split(":", 2)[2]
            rec.update({"names": [basename(path)], "hosts": [host], "paths": {host: [path]}})
        else:
            rec.update({"names": [lid.split(":", 1)[-1]], "hosts": ["github"]})
        lin_rec[lid] = rec
    fl = {}
    for e in out_events:
        lid = e.get("repo")
        if lid is None or lin_rec[lid]["kind"] == "git":
            continue
        a = fl.get(lid)
        fl[lid] = [ts_min(a[0] if a else None, e["ts"]), ts_max(a[1] if a else None, e["ts"])]
    for lid, (a, b) in fl.items():
        lin_rec[lid]["first_ts"], lin_rec[lid]["last_ts"] = a, b

    cand_list = [{"link": "candidate", "a": a, "b": b, "basis": basis, "key": key}
                 for (a, b, basis), key in sorted(cands.items())]

    # ---- actors, hosts, sessions
    actors, hosts = {}, {}
    per_class, per_kind = Counter(), Counter()
    per_ym = defaultdict(Counter)
    for e in out_events:
        a = e["actor"]
        ar = actors.setdefault((a["class"], a["name"]), {"class": a["class"], "name": a["name"], "events": 0,
                                                         "first_ts": e["ts"], "last_ts": e["ts"],
                                                         "kinds": Counter(), "hosts": set()})
        ar["events"] += 1
        ar["last_ts"] = e["ts"]
        ar["kinds"][e["kind"]] += 1
        ar["hosts"].add(e["host"])
        h = hosts.setdefault(e["host"], {"host": e["host"], "events": 0, "first_ts": e["ts"], "last_ts": e["ts"],
                                         "kinds": Counter(), "classes": Counter(), "srcs": Counter()})
        h["events"] += 1
        h["last_ts"] = e["ts"]
        h["kinds"][e["kind"]] += 1
        h["classes"][a["class"]] += 1
        h["srcs"][e["src"]] += 1
        per_class[a["class"]] += 1
        per_kind[e["kind"]] += 1
        per_ym[e["ts"][:7]][e["kind"]] += 1
    actors_out = sorted(({"class": v["class"], "name": v["name"], "events": v["events"], "first_ts": v["first_ts"],
                          "last_ts": v["last_ts"], "kinds": dict(sorted(v["kinds"].items())),
                          "hosts": sorted(v["hosts"], key=hrank)} for v in actors.values()),
                        key=lambda x: (x["class"], -x["events"], x["name"]))
    lin_per_host = defaultdict(set)
    for lid, r in lin_rec.items():
        for h in r.get("hosts", []):
            lin_per_host[h].add(lid)
    hosts_out = [{"host": hn, "events": hosts[hn]["events"], "first_ts": hosts[hn]["first_ts"],
                  "last_ts": hosts[hn]["last_ts"], "kinds": dict(sorted(hosts[hn]["kinds"].items())),
                  "classes": dict(sorted(hosts[hn]["classes"].items())),
                  "srcs": dict(sorted(hosts[hn]["srcs"].items())), "lineages": len(lin_per_host.get(hn, ()))}
                 for hn in sorted(hosts, key=hrank)]

    sess = {}
    for e in out_events:
        if e["kind"] != "chat_session":
            continue
        m = e.get("meta") or {}
        dur = e["magnitude"].get("duration_s") or 0
        s = sess.get((e["actor"]["class"], m.get("session")))
        if s is None:
            s = sess[(e["actor"]["class"], m.get("session"))] = {
                "session": m.get("session"), "class": e["actor"]["class"], "name": e["actor"]["name"],
                "host": e["host"], "path": e.get("path"), "repo": e.get("repo"), "first_ts": e["ts"],
                "duration_s": dur, "messages": 0, "segments": 0, "sidechain_segments": 0, "source": set(),
                "models": set()}
        s["segments"] += 1
        s["messages"] += e["magnitude"].get("n", 0)
        s["duration_s"] = max(s["duration_s"], dur)
        s["sidechain_segments"] += 1 if m.get("sidechain") else 0
        if m.get("source"):
            s["source"].add(m["source"])
        s["models"].update(m.get("model") or [])
        if s["repo"] is None and e.get("repo"):
            s["repo"] = e["repo"]
    sessions_out = sorted(({**{k: v for k, v in s.items() if k not in ("source", "models")},
                            "source": sorted(s["source"]), "models": sorted(s["models"])[:24]}
                           for s in sess.values()), key=lambda x: (x["first_ts"], x["class"], str(x["session"])))

    # ---- write
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "events.ndjson"), "w") as f:
        for e in out_events:
            f.write(jdump(e) + "\n")

    def wjson(name, obj):
        with open(os.path.join(out_dir, name), "w") as f:
            json.dump(obj, f, sort_keys=True, indent=1, ensure_ascii=True)
            f.write("\n")

    wjson("repos.json", {"version": 1, "as_of": out_events[-1]["ts"] if out_events else None,
                         "lineages": [lin_rec[k] for k in sorted(lin_rec)], "candidates": cand_list,
                         "link_basis": dict(sorted(uf.basis.items()))})
    wjson("actors.json", {"version": 1, "actors": actors_out, "identity_fixes": dict(sorted(ident.fixed.items()))})
    wjson("hosts.json", {"version": 1, "hosts": hosts_out})
    wjson("sessions.json", {"version": 1, "sessions": sessions_out})

    # ---- stats (counts only; the report is built from this)
    node_rows = [{"repo_local": k, "host": nodes[k]["host"], "path": nodes[k]["path"], "item": nodes[k]["_item"],
                  "lineage": lin_of_node[k], "commits": nodes[k]["commits"], "commit_events": commit_copies[k],
                  "refs": nodes[k]["refs"], "worktree": nodes[k]["is_worktree"], "bare": nodes[k]["is_bare"],
                  "shallow": nodes[k]["shallow"], "empty": nodes[k]["empty"]} for k in sorted(nodes)]
    raw_item_kind = defaultdict(Counter)
    raw_src_kind = Counter()
    chat_per_item = defaultdict(Counter)
    for it, e in evs:
        raw_item_kind[it][e["kind"]] += 1
        raw_src_kind[(e["src"], e["kind"])] += 1
        if e["kind"] == "chat_session":
            chat_per_item[it]["chat_session_records"] += 1
            chat_per_item[it]["messages"] += e["magnitude"].get("n", 0)
    fa_item = defaultdict(Counter)
    for it, e in evs:
        if e["kind"] in ("file_birth", "file_update"):
            k = "birth" if e["kind"] == "file_birth" else "update"
            fa_item[it][k + "_records"] += 1
            fa_item[it][k + "_files"] += e["magnitude"].get("n", 0)
            fa_item[it][k + "_bytes"] += e["magnitude"].get("bytes", 0) or 0
            if (e.get("meta") or {}).get("bulk_copy"):
                fa_item[it][k + "_bulk_records"] += 1
    fa_hym = defaultdict(lambda: defaultdict(Counter))
    for e in out_events:
        if e["kind"] in ("file_birth", "file_update"):
            c = fa_hym[e["host"]][e["ts"][:7]]
            c[e["kind"] + "_files"] += e["magnitude"].get("n", 0)
            c[e["kind"] + "_records"] += 1
    stats["file_activity"] = {
        "per_item": {i: dict(sorted(c.items())) for i, c in sorted(fa_item.items())},
        "per_host_ym": {h: {ym: dict(sorted(c.items())) for ym, c in sorted(v.items())}
                        for h, v in sorted(fa_hym.items())}}
    stats.update({
        "items_order": items,
        "events_out": len(out_events),
        "lineages": {"git": sum(1 for r in lin_rec.values() if r["kind"] == "git"),
                     "dir": sum(1 for r in lin_rec.values() if r["kind"] == "dir"),
                     "github_only": sum(1 for r in lin_rec.values() if r["kind"] == "github")},
        "link_basis": dict(sorted(uf.basis.items())),
        "components_multi": sum(1 for v in lin_info.values() if len(v["members"]) > 1),
        "largest_components": sorted((len(v["members"]) for v in lin_info.values()), reverse=True)[:8],
        "candidates": len(cand_list),
        "candidates_by_basis": dict(sorted(Counter(c["basis"] for c in cand_list).items())),
        "dropped_null_ts": {"%s/%s" % k: v for k, v in sorted(dropped_null.items())},
        "dropped_null_ts_total": sum(dropped_null.values()),
        "deduped": dict(sorted(dup.items())),
        "zip_live_overlap": dict(zip_live_overlap),
        "dup_items": dict(sorted(dup_items.items())),
        "github_event_match": dict(gh_match),
        "join": {s: dict(c) for s, c in sorted(join_stats.items())},
        "identity_fixes": dict(sorted(ident.fixed.items())),
        "per_kind": dict(sorted(per_kind.items())),
        "per_host": {h["host"]: h["events"] for h in hosts_out},
        "per_class": dict(sorted(per_class.items())),
        "per_ym": {k: dict(sorted(v.items())) for k, v in sorted(per_ym.items())},
        "per_src_kind": {"%s/%s" % k: v for k, v in sorted(Counter((e["src"], e["kind"]) for e in out_events).items())},
        "raw_src_kind": {"%s/%s" % k: v for k, v in sorted(raw_src_kind.items())},
        "raw_item_kind": {i: dict(sorted(c.items())) for i, c in sorted(raw_item_kind.items())},
        "chat_per_item": {i: dict(c) for i, c in sorted(chat_per_item.items())},
        "sessions": len(sessions_out),
        "sessions_by_class": dict(sorted(Counter(s["class"] for s in sessions_out).items())),
        "chat_session_records": per_kind.get("chat_session", 0),
        "chat_msg_records": per_kind.get("chat_msg", 0),
        "chat_msg_folded_messages": sum(e["magnitude"].get("n", 0) for e in out_events if e["kind"] == "chat_msg"),
        "actors": len(actors_out),
        "first_ts": out_events[0]["ts"] if out_events else None,
        "last_ts": out_events[-1]["ts"] if out_events else None,
        "repo_nodes": node_rows,
        "manifests": {i: {"status": m.get("status"), "events": m.get("events"), "repos": m.get("repos"),
                          "dropped": m.get("dropped"),
                          "coverage": {k: (len(v) if isinstance(v, list) else v)
                                       for k, v in (m.get("coverage") or {}).items()},
                          "warnings": m.get("warnings"), "src": m.get("src"),
                          "raw_sum": sum((s.get("raw") or 0) for s in m.get("sources", []))}
                      for i, m in manifests.items()},
    })
    wjson("stats.json", stats)
    return stats


def main(argv):
    raw = argv[1] if len(argv) >= 2 else RAW
    out = argv[2] if len(argv) >= 3 else OUT
    st = merge(raw, out)
    print("events_loaded=%d events_out=%d lineages=%s repo_records=%d sessions=%d chat_msg=%d candidates=%d "
          "null_ts_dropped=%d first=%s last=%s" % (
              st["events_loaded"], st["events_out"], st["lineages"], st["repo_records"], st["sessions"],
              st["chat_msg_records"], st["candidates"], st["dropped_null_ts_total"], st["first_ts"], st["last_ts"]))
    print("link_basis=%s multi=%d largest=%s" % (st["link_basis"], st["components_multi"], st["largest_components"]))
    print("deduped=%s zip_live=%s" % (st["deduped"], st["zip_live_overlap"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
