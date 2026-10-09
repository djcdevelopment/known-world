"""Streams corpus/merged once into the in-memory indexes launches.py and nations.py need. Never prints a corpus line."""
import bisect
import collections
import json
import os

from common import MERGED, parse_ts

AI = ("claude", "codex", "opencode", "automation", "local_model")
SESSION_CLASSES = ("claude", "codex", "opencode")
NATION_PRIORITY = {c: i for i, c in enumerate(("human", "chatgpt", "claude", "codex", "opencode", "local_model", "automation"))}
FIRST_EVENT_KINDS = {"commit", "chat_session", "chat_msg", "offload_call", "repo_born", "file_birth", "file_update", "run", "receipt"}


class Corpus:
    pass


def is_local_backend(b, params):
    return bool(b) and any(b.startswith(p) for p in params["local_backends"])


def load(params):
    c = Corpus()
    repos = json.load(open(os.path.join(MERGED, "repos.json")))
    c.as_of = repos["as_of"]
    c.lineages = {l["id"]: l for l in repos["lineages"]}
    c.third = {i for i, l in c.lineages.items() if l.get("third_party")}
    c.own = {i for i, l in c.lineages.items() if l["kind"] == "git" and not l.get("third_party")}
    c.dirs = {i for i, l in c.lineages.items() if l["kind"] == "dir"}
    sess = json.load(open(os.path.join(MERGED, "sessions.json")))["sessions"]
    c.session_info = {s["session"]: s for s in sess}
    p = os.path.join(MERGED, "relations.json")
    c.relations = json.load(open(p)) if os.path.exists(p) else None
    p = os.path.join(MERGED, "chatgpt_links.json")
    c.chatgpt_links = json.load(open(p)) if os.path.exists(p) else None
    c.rel_integrations = {}
    if c.relations:
        for lid, d in c.relations["integrations"].items():
            c.rel_integrations[lid] = sum(d.get(k, 0) for k in ("contracts_in", "contracts_out", "data_sources", "depends_in", "depends_out"))
    commits = collections.defaultdict(list)
    births = collections.defaultdict(list)  # lineage -> (t, kind, ref)
    chat = collections.defaultdict(list)  # lineage -> (t, session, class, n)
    gpt = []  # (t, session)
    offloads = []  # (t, backend, class) local backends only
    nongit = collections.defaultdict(lambda: collections.defaultdict(lambda: {"files": 0, "bytes": 0, "dirs": set(), "t0": None, "t1": None, "bulk": 0, "nrec": 0}))
    host_first = collections.defaultdict(dict)
    first_event = {}
    third_paths = collections.defaultdict(collections.Counter)
    third_hosts = collections.defaultdict(set)
    chat_all = []
    tot_commits = []  # running totals: (t, class, host, files, ins, del, no_numstat) for counted commits
    fs_rows = []  # running totals: (t, host, kind, n, bulk, lineage) every file_birth / file_update record
    tp = collections.Counter()  # commits not counted in any nation, for the receipt
    sess_events = []
    gh_born = []
    dir_touch = collections.defaultdict(list)
    nc_first = {}  # (lineage, host) -> first non-commit event, for third-party clone time
    first_local_offload = None
    first_backend = {}
    gen_first = {}  # (class, canon-minor-or-raw) -> (t, source)
    sess_models = {}
    n_events = 0
    for line in open(os.path.join(MERGED, "events.ndjson")):
        e = json.loads(line)
        n_events += 1
        k = e["kind"]
        t = parse_ts(e["ts"])
        a = e["actor"]
        cls = a["class"]
        r = e.get("repo")
        if cls != "third_party" and k in FIRST_EVENT_KINDS and (r not in c.third or params["first_event_include_third_party"]):
            if cls not in first_event or t < first_event[cls]:
                first_event[cls] = t
        if r in c.third and k in ("chat_msg", "chat_session", "file_birth", "file_update", "offload_call", "run", "receipt") and e.get("host"):
            kk = (r, e["host"])
            if kk not in nc_first or t < nc_first[kk]:
                nc_first[kk] = t
        if r is not None and r not in c.third and e.get("host"):
            hf = host_first[r]
            if e["host"] not in hf or t < hf[e["host"]]:
                hf[e["host"]] = t
        if k == "commit":
            _m, _nn = e["magnitude"], bool((e.get("meta") or {}).get("no_numstat"))
            if r in c.third:
                tp["clone_commits"] += 1; tp["clone_no_numstat"] += int(_nn)
                tp["clone_files"] += _m.get("files") or 0; tp["clone_lines"] += (_m.get("ins") or 0) + (_m.get("del") or 0)
                tp["clone_lines_capped"] += min((_m.get("ins") or 0) + (_m.get("del") or 0), params["yield_cap_lines_per_commit"])
            elif cls == "third_party" and r in c.own:
                tp["own_third_class_commits"] += 1; tp["own_third_class_no_numstat"] += int(_nn)
                tp["own_third_class_files"] += _m.get("files") or 0; tp["own_third_class_lines"] += (_m.get("ins") or 0) + (_m.get("del") or 0)
            if r in c.third:
                for pth in (e.get("files") or ()):
                    third_paths[r][pth] += 1
                third_hosts[r].update(set((e.get("meta") or {}).get("hosts") or ()) | {e["host"]})
            if r in c.own:
                if cls == "third_party" and params["exclude_third_party_commits"]:
                    continue
                m = e["magnitude"]
                raw = (m.get("ins") or 0) + (m.get("del") or 0)
                mh = tuple(sorted(set((e.get("meta") or {}).get("hosts") or ()) | {e["host"]}))
                commits[r].append((t, e["ref"], cls, a["name"], raw, m.get("files") or 0, tuple(e.get("files") or ()), e["host"], bool((e.get("meta") or {}).get("no_numstat")), mh))
                tot_commits.append((t, cls, e["host"], m.get("files") or 0, m.get("ins") or 0, m.get("del") or 0, bool((e.get("meta") or {}).get("no_numstat"))))
                if cls != "third_party":
                    key = (cls, a["name"])
                    if key not in gen_first or t < gen_first[key]:
                        gen_first[key] = t
        elif k in ("branch", "worktree"):
            if r in c.own:
                births[r].append((t, k, e["ref"][:12], e["host"], e.get("path")))
        elif k == "chat_msg":
            n = e["magnitude"]["n"]
            sid = e["meta"].get("session")
            if cls == "chatgpt":
                gpt.append((t, sid, n))
            elif cls in SESSION_CLASSES:
                chat_all.append((t, e["host"], cls, n))
                if r in c.own or r in c.dirs:
                    chat[r].append((t, sid, cls, n, e.get("path"), e["host"]))
        elif k == "chat_session":
            sid = e["meta"].get("session")
            mods = e["meta"].get("model")
            if isinstance(mods, str):
                mods = [mods]
            sess_models[sid] = (cls, list(mods or []), t, int(e["magnitude"].get("n") or 0))
            sess_events.append((t, cls, e["host"]))
            for mname in mods or []:
                key = (cls, mname)
                if key not in gen_first or t < gen_first[key]:
                    gen_first[key] = t
        elif k == "offload_call":
            b = e["meta"].get("backend")
            if is_local_backend(b, params):
                offloads.append((t, b, cls))
                if b not in first_backend or t < first_backend[b]:
                    first_backend[b] = t
                if first_local_offload is None or t < first_local_offload:
                    first_local_offload = t
        elif k == "repo_born" and e["host"] == "github":
            gh_born.append((t, r, int(e["magnitude"].get("kb") or 0), bool((e.get("meta") or {}).get("fork"))))
        elif k in ("file_birth", "file_update"):
            fs_rows.append((t, e["host"], k, e["magnitude"]["n"], bool((e.get("meta") or {}).get("bulk_copy")), r))
            if r in c.dirs:
                day = t // 86400
                m = e["magnitude"]
                d = nongit[r][day]
                bulk = bool((e.get("meta") or {}).get("bulk_copy"))
                dir_touch[r].append((t, e["host"], e.get("path") or ".", k, m["n"], m.get("bytes") or 0, bulk, cls))
                if bulk and params["nongit_exclude_bulk_copy"]:
                    d["bulk"] += m["n"]
                    continue
                d["files"] += m["n"]
                d["bytes"] += m.get("bytes") or 0
                if e.get("path"):
                    d["dirs"].add(e["path"])
                d["t0"] = t if d["t0"] is None else min(d["t0"], t)
                d["t1"] = t if d["t1"] is None else max(d["t1"], t)
                d["nrec"] += 1
    c.n_events = n_events
    c.tot_commits, c.fs_rows, c.third_totals = sorted(tot_commits), sorted(fs_rows, key=lambda x: (x[0], x[1], x[2], str(x[5]))), dict(tp)
    c.third_paths, c.third_hosts, c.chat_all, c.sess_events, c.gh_born, c.dir_touch, c.nc_first = third_paths, third_hosts, sorted(chat_all), sorted(sess_events), sorted(gh_born, key=lambda x: (x[0], str(x[1]))), dir_touch, nc_first
    for r in dir_touch:
        dir_touch[r].sort()
    # directories that later gain a git lineage (exact path match on the same host): non-git only before its first commit
    gp = {}
    for i in c.own:
        for h, ps in c.lineages[i]["paths"].items():
            for pth in ps:
                gp[(h, pth.rstrip("/"))] = i
    c.dir_git_first = {}
    for i in c.dirs:
        _, h, pth = i.split(":", 2)
        g = gp.get((h, pth.rstrip("/")))
        if g:
            c.dir_git_first[i] = parse_ts(c.lineages[g]["first_ts"])
    for r in commits:
        commits[r].sort(key=lambda x: (x[0], x[1]))
    for r in chat:
        chat[r].sort(key=lambda x: (x[0], str(x[1])))
    gpt.sort(key=lambda x: (x[0], str(x[1])))
    offloads.sort()
    for r in births:
        births[r].sort()
    c.commits, c.births, c.chat, c.gpt, c.offloads, c.nongit = commits, births, chat, gpt, offloads, nongit
    c.chat_t = {r: [x[0] for x in v] for r, v in chat.items()}
    c.gpt_t = [x[0] for x in gpt]
    c.off_t = [x[0] for x in offloads]
    c.births_t = {r: [x[0] for x in v] for r, v in births.items()}
    c.host_first = host_first
    c.first_event = first_event
    c.first_local_offload = first_local_offload
    c.first_backend = first_backend
    c.gen_first = gen_first
    c.sess_models = sess_models
    c.gpt_link = {}
    if c.chatgpt_links:
        for cv in c.chatgpt_links["conversations"]:
            c.gpt_link[cv["conversation_id"]] = set(cv.get("lineages") or [])
    return c


def window(times, lo, hi):
    return bisect.bisect_left(times, lo), bisect.bisect_right(times, hi)
