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
        if r is not None and r not in c.third and e.get("host"):
            hf = host_first[r]
            if e["host"] not in hf or t < hf[e["host"]]:
                hf[e["host"]] = t
        if k == "commit":
            if r in c.own:
                if cls == "third_party" and params["exclude_third_party_commits"]:
                    continue
                m = e["magnitude"]
                raw = (m.get("ins") or 0) + (m.get("del") or 0)
                commits[r].append((t, e["ref"], cls, a["name"], raw, m.get("files") or 0, tuple(e.get("files") or ()), e["host"], bool((e.get("meta") or {}).get("no_numstat"))))
                if cls != "third_party":
                    key = (cls, a["name"])
                    if key not in gen_first or t < gen_first[key]:
                        gen_first[key] = t
        elif k in ("branch", "worktree"):
            if r in c.own:
                births[r].append((t, k, e["ref"][:12]))
        elif k == "chat_msg":
            n = e["magnitude"]["n"]
            sid = e["meta"].get("session")
            if cls == "chatgpt":
                gpt.append((t, sid))
            elif cls in SESSION_CLASSES and (r in c.own or r in c.dirs):
                chat[r].append((t, sid, cls, n))
        elif k == "chat_session":
            sid = e["meta"].get("session")
            mods = e["meta"].get("model")
            if isinstance(mods, str):
                mods = [mods]
            sess_models[sid] = (cls, list(mods or []), t, int(e["magnitude"].get("n") or 0))
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
        elif k in ("file_birth", "file_update"):
            if r in c.dirs:
                day = t // 86400
                m = e["magnitude"]
                d = nongit[r][day]
                bulk = bool((e.get("meta") or {}).get("bulk_copy"))
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
    for r in commits:
        commits[r].sort(key=lambda x: (x[0], x[1]))
    for r in chat:
        chat[r].sort()
    gpt.sort()
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
