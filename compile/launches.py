"""compile/launches.py: episodes, activity-based session join, nation, yield, shape and non-git episodes.

CONTRACT.md section 8 (v1.5), STRATEGY.md 4.2. Deterministic; counts only on stdout; never prints a corpus line.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I compile/launches.py --out DIR [--params FILE] [--set key=json ...]
"""
import argparse
import bisect
import collections
import hashlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import corpus as corp
import names as nm
from common import iso, load_params, params_hash, write_json

NONHUMAN = ("claude", "codex", "opencode", "automation", "local_model")


def band_of(lines, files, integrations, pieces, params, bytes_=None, nongit=False):
    if nongit:
        score = math.log10(max(files, 1)) + 0.5 * math.log10(max((bytes_ or 0) / 1e4, 1e-9))
    elif params["yield_score"] == "composite":
        score = (math.log10(max(lines, 1)) + 0.5 * math.log10(max(files, 1)) + 0.25 * integrations + 0.1 * pieces)
    else:
        score = math.log10(max(lines, 1))
    edges = params["yield_bands"]  # lower bounds of bands 1..6 as lines; band 1 includes everything below edges[1]
    # band = clamp(floor(log10 score), 1, 6) generalised to edges: count edges <= 10**score
    v = 10 ** score
    b = 1
    for i, e in enumerate(edges):
        if v >= e:
            b = i + 1
    return max(1, min(6, b)), score


def build_episodes(c, params):
    gap = params["episode_gap_h"] * 3600
    eps = []
    for lin in sorted(c.commits):
        cur = None
        for (t, ref, cls, name, raw, nfiles, dirs, host, nonum) in c.commits[lin]:
            capped = min(raw, params["yield_cap_lines_per_commit"])
            if cur is not None and t - cur["t1"] <= gap:
                cur["t1"] = t
            else:
                if cur:
                    eps.append(cur)
                cur = {"lineage": lin, "t0": t, "t1": t, "n": 0, "lines": 0, "lines_raw": 0, "capped": 0, "files": 0,
                       "dirs": set(), "cls": collections.Counter(), "names": collections.defaultdict(collections.Counter),
                       "hosts": set(), "nonum": 0, "nongit": False}
            cur["n"] += 1
            cur["lines"] += capped
            cur["lines_raw"] += raw
            cur["capped"] += raw > params["yield_cap_lines_per_commit"]
            cur["files"] += nfiles
            cur["dirs"].update(dirs)
            cur["cls"][cls] += 1
            cur["names"][cls][name] += 1
            cur["hosts"].add(host)
            cur["nonum"] += nonum
        if cur:
            eps.append(cur)
    return eps


def attach_context(c, params, ep):
    """Sessions (activity join), seats, hosts, branches/worktrees for a git episode or a non-git burst."""
    ov = params["session_overlap_min"] * 60
    lin = ep["lineage"]
    lo, hi = ep["t0"] - ov, ep["t1"] + ov
    ep["sessions"] = collections.Counter()
    ep["scls"] = collections.Counter()
    ep["smod"] = collections.defaultdict(collections.Counter)  # class -> session -> msgs
    ts = c.chat_t.get(lin)
    if ts:
        a, b = corp.window(ts, lo, hi)
        for (t, sid, cls, n) in c.chat[lin][a:b]:
            ep["sessions"][sid] += n
            ep["scls"][cls] += n
            ep["smod"][cls][sid] += n
    a, b = corp.window(c.off_t, ep["t0"], ep["t1"])
    ep["seats"] = {x[1] for x in c.offloads[a:b]}
    bt = c.births_t.get(lin)
    ep["branches"], ep["worktrees"] = set(), set()
    if bt:
        a, b = corp.window(bt, ep["t0"], ep["t1"])
        for (t, kind, ref) in c.births[lin][a:b]:
            (ep["branches"] if kind == "branch" else ep["worktrees"]).add((t, ref))
    hosts = {h for h, t in c.host_first.get(lin, {}).items() if t <= ep["t1"]}
    ep["hosts"] = set(ep.get("hosts") or ()) | hosts
    return ep


def nation_of(ep, params):
    rule = params["nation_rule"]
    cls = ep["cls"]
    sc = ep["scls"]
    best_session = None
    if sc:
        best_session = sorted(sc.items(), key=lambda kv: (-kv[1], corp.NATION_PRIORITY[kv[0]]))[0][0]
    if rule == "commit_dominant":
        if cls:
            return sorted(cls.items(), key=lambda kv: (-kv[1], corp.NATION_PRIORITY[kv[0]]))[0][0]
        return best_session or "human"
    ai = {k: v for k, v in cls.items() if k in NONHUMAN}
    if ai:
        return sorted(ai.items(), key=lambda kv: (-kv[1], corp.NATION_PRIORITY[kv[0]]))[0][0]
    return best_session or "human"


def generation_of(ep, nation, c, params):
    g = params["generation_granularity"]
    cand = collections.Counter()
    for nme, n in ep["names"].get(nation, {}).items():
        gg = nm.canon(nme, g)
        if gg:
            cand[gg] += n
    if cand:
        return sorted(cand.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    sm = ep["smod"].get(nation)
    if sm:
        sid = sorted(sm.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        info = c.sess_models.get(sid)
        if info and info[1]:
            for mname in info[1]:
                gg = nm.canon(mname, g)
                if gg:
                    return gg
    return None


def mk_test(c, params, ep):
    ep = attach_context(c, params, ep)
    ep["pieces_classes"] = {k for k in set(ep["cls"]) | set(ep["scls"]) if k in NONHUMAN or k in corp.SESSION_CLASSES}
    ep["nation"] = nation_of(ep, params)
    ep["nation_inferred"] = None
    ep["gen"] = generation_of(ep, ep["nation"], c, params)
    ep["id"] = hashlib.sha1((ep["lineage"] + iso(ep["t0"])).encode()).hexdigest()[:12]
    return ep


def passes_min(ep, params):
    m = params["min_yield"]
    return ep["lines"] >= m["lines"] or ep["files"] >= m["files"]


# --- non-git ---------------------------------------------------------------
def nongit_tests(c, params):
    out = []
    ms = params["min_yield"]["files"]
    gap_days = params["episode_gap_days"]
    ov = params["session_overlap_min"] * 60
    for lin in sorted(c.nongit):
        days = c.nongit[lin]
        active = sorted(d for d, v in days.items() if v["files"] >= ms)
        cur = None
        groups = []
        for d in active:
            if cur is not None and d - cur[-1] <= gap_days:
                cur.append(d)
            else:
                cur = [d]
                groups.append(cur)
        for g in groups:
            files = sum(days[d]["files"] for d in g)
            by = sum(days[d]["bytes"] for d in g)
            dirs = set()
            for d in g:
                dirs |= days[d]["dirs"]
            t0 = min(days[d]["t0"] for d in g)
            t1 = max(days[d]["t1"] for d in g)
            ep = {"lineage": lin, "t0": t0, "t1": t1, "n": 0, "lines": None, "lines_raw": None, "capped": 0, "files": files,
                  "bytes": by, "dirs": dirs, "cls": collections.Counter(), "names": collections.defaultdict(collections.Counter),
                  "hosts": set(), "nonum": 0, "nongit": True, "nrec": sum(days[d]["nrec"] for d in g), "bulk_skipped": sum(days[d]["bulk"] for d in g)}
            # sessions whose cwd lies under the directory and overlaps the burst
            ep["_win"] = (g[0] * 86400, (g[-1] + 1) * 86400)
            out.append(ep)
    tests = []
    for ep in out:
        t0, t1 = ep["t0"], ep["t1"]
        ep["t0"], ep["t1"] = ep["_win"][0], ep["_win"][1] - 1
        attach_context(c, params, ep)
        ep["t0"], ep["t1"] = t0, t1
        ep["hosts"] = {ep["lineage"].split(":")[1]}
        ep["pieces_classes"] = {k for k in ep["scls"] if k in NONHUMAN or k in corp.SESSION_CLASSES}
        # nation: session class, else ChatGPT within +-2h (path+time before time), else human
        sc = ep["scls"]
        nation, infer = None, None
        if sc:
            nation = sorted(sc.items(), key=lambda kv: (-kv[1], corp.NATION_PRIORITY[kv[0]]))[0][0]
        elif params["inferred_nation"] != "human" and c.gpt_t:
            a, b = corp.window(c.gpt_t, ep["_win"][0] - 7200, ep["_win"][1] + 7200)
            if b > a:
                convs = {x[1] for x in c.gpt[a:b]}
                infer = "path+time" if any(ep["lineage"] in c.gpt_link.get(cv, ()) for cv in convs) else "time"
                nation = "chatgpt"
        ep["nation"] = nation or "human"
        ep["nation_inferred"] = infer
        ep["gen"] = generation_of(ep, ep["nation"], c, params)
        ep["id"] = hashlib.sha1((ep["lineage"] + iso(ep["t0"])).encode()).hexdigest()[:12]
        tests.append(ep)
    return tests


# --- clustering --------------------------------------------------------------
class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def cluster(tests, params):
    mode = params["engagement_union"]
    n = len(tests)
    if mode == "time_window":
        order = sorted(range(n), key=lambda i: (tests[i]["t0"], tests[i]["lineage"]))
        gap = params["episode_gap_h"] * 3600
        cap = params["engagement_max_span_h"] * 3600 if params["engagement_max_span_h"] is not None else None
        groups, cur, last, start = [], None, None, None
        for i in order:
            e = tests[i]
            if cur is not None and e["t0"] - last <= gap and (cap is None or e["t0"] - start <= cap):
                cur.append(i)
                last = max(last, e["t1"])
            else:
                cur = [i]
                groups.append(cur)
                last, start = e["t1"], e["t0"]
        return groups
    uf = UF(n)
    by_sid = collections.defaultdict(list)
    for i, e in enumerate(tests):
        for sid in e["sessions"]:
            by_sid[sid].append(i)
    for sid, idx in sorted(by_sid.items()):
        if len({tests[i]["lineage"] for i in idx}) >= 2:
            for i in idx[1:]:
                uf.union(idx[0], i)
    if mode == "session_or_nation":
        # information arm: also union different-lineage tests of one nation whose padded windows intersect
        ov = params["session_overlap_min"] * 60
        order = sorted(range(n), key=lambda i: tests[i]["t0"])
        for a_i, i in enumerate(order):
            for j in order[a_i + 1:]:
                if tests[j]["t0"] - ov > tests[i]["t1"] + ov:
                    break
                if tests[i]["lineage"] != tests[j]["lineage"] and tests[i]["nation"] == tests[j]["nation"]:
                    uf.union(i, j)
    g = collections.defaultdict(list)
    for i in range(n):
        g[uf.find(i)].append(i)
    return [sorted(v, key=lambda i: tests[i]["t0"]) for k, v in sorted(g.items())]


def assemble(c, params, tests, groups):
    L = []
    for idx in groups:
        eps = [tests[i] for i in idx]
        eps.sort(key=lambda e: (e["t0"], e["lineage"]))
        lineages = sorted({e["lineage"] for e in eps})
        wt = {}
        for e in eps:
            for (t, ref) in e["worktrees"]:
                wt[ref] = (t, e["lineage"])
        targets = list(lineages)
        if params["mirv_count_worktrees"]:
            targets += sorted(wt)
        lines = sum(e["lines"] or 0 for e in eps)
        files = sum(e["files"] for e in eps)
        seats = set().union(*[e["seats"] for e in eps])
        hosts = set().union(*[e["hosts"] for e in eps])
        dirs = {(e["lineage"], d) for e in eps for d in e["dirs"]}
        branches = {r for e in eps for (t, r) in e["branches"]}
        classes = set().union(*[e["pieces_classes"] for e in eps])
        rel = sum(c.rel_integrations.get(l, 0) for l in lineages)
        integ = len(lineages) + len(hosts) + len(seats) + rel
        pieces = len(dirs) + len(branches) + len(wt) + len(classes)
        nongit = all(e["nongit"] for e in eps)
        by = sum(e.get("bytes") or 0 for e in eps)
        band, score = band_of(lines, files, integ, pieces, params, bytes_=by, nongit=nongit)
        nat = collections.Counter()
        natw = collections.Counter()
        for e in eps:
            nat[e["nation"]] += 1
            natw[e["nation"]] += e["lines"] or e["files"]
        nation = sorted(nat, key=lambda k: (-nat[k], -natw[k], corp.NATION_PRIORITY[k]))[0]
        prim = sorted(eps, key=lambda e: (-(e["lines"] if e["lines"] is not None else e["files"]), e["t0"]))[0]
        pe = [e for e in eps if e["nation"] == nation]
        gens = collections.Counter(e["gen"] for e in pe if e["gen"])
        gen = sorted(gens, key=lambda k: (-gens[k], k))[0] if gens else None
        inferred = None
        if nation == "chatgpt":
            vals = [e["nation_inferred"] for e in pe if e["nation_inferred"]]
            inferred = "path+time" if "path+time" in vals else ("time" if vals else None)
        sessions = collections.Counter()
        for e in eps:
            sessions.update(e["sessions"])
        t0 = min(e["t0"] for e in eps)
        t1 = max(e["t1"] for e in eps)
        shape = "mirv" if (not nongit and len(targets) >= params["mirv_min_targets"]) else "single"
        wh = []
        if shape == "mirv":
            by_lin = collections.defaultdict(lambda: [10 ** 12, 0])
            for e in eps:
                x = by_lin[e["lineage"]]
                x[0] = min(x[0], e["t0"]); x[1] += e["lines"] or 0
            for l, (t, ln) in by_lin.items():
                wh.append({"target": l, "kind": "lineage", "ts": t, "lines": ln})
            if params["mirv_count_worktrees"]:
                for ref, (t, l) in wt.items():
                    wh.append({"target": ref, "kind": "worktree", "ts": t, "lines": 0, "lineage": l})
            wh.sort(key=lambda w: (w["ts"], w["target"]))
        L.append({
            "launch_id": hashlib.sha1((prim["lineage"] + iso(t0)).encode()).hexdigest()[:12],
            "lineage": prim["lineage"], "ts_start": t0, "ts_end": t1, "nation": nation, "nation_inferred": inferred,
            "generation": gen,
            "sessions": sorted(sessions), "commits": sum(e["n"] for e in eps), "hosts": sorted(hosts), "seats": sorted(seats),
            "yield": {"lines": None if nongit else lines, "files": files, "bytes": by if nongit else None,
                      "integrations": integ, "moving_pieces": pieces, "class": band, "score": round(score, 3)},
            "shape": shape, "warheads": len(wh) if wh else 1, "targets": targets if shape == "mirv" else [prim["lineage"]],
            "warhead_list": wh, "unifies": [], "episodes": len(eps), "nongit": nongit,
            "capped_commits": sum(e["capped"] for e in eps), "lines_raw": None if nongit else sum(e["lines_raw"] for e in eps),
            "commits_no_numstat": sum(e["nonum"] for e in eps),
            "first_test": False, "first_of_nation": None, "first_of_generation": None,
            "_lineages": lineages,
        })
    L.sort(key=lambda l: (l["ts_start"], l["launch_id"]))
    return L


def unify(launches, params):
    win = params["unify_window_h"] * 3600
    used = set()
    n = 0
    for u in launches:
        if u["shape"] != "single" or u["nongit"] or u["yield"]["class"] < params["unify_min_band"]:
            continue
        best = None
        for m in launches:
            if m["ts_start"] >= u["ts_start"]:
                break
            if m["shape"] != "mirv" or m["launch_id"] in used:
                continue
            if u["lineage"] not in m["_lineages"] and u["lineage"] not in [w.get("lineage") for w in m["warhead_list"]]:
                continue
            if not (0 <= u["ts_start"] - m["ts_end"] <= win):
                continue
            if u["yield"]["lines"] < 0.5 * m["yield"]["lines"]:
                continue
            best = m
        if best:
            u["shape"] = "unified"
            u["unifies"] = [best["launch_id"]]
            u["warheads"] = best["warheads"]
            used.add(best["launch_id"])
            n += 1
    return n


def firsts(launches, params):
    seen_lin, seen_nat, seen_gen = set(), set(), set()
    for l in launches:
        l["first_test"] = any(x not in seen_lin for x in l["_lineages"])
        l["new_lineages"] = sum(1 for x in l["_lineages"] if x not in seen_lin)
        seen_lin.update(l["_lineages"])
        if l["nation"] not in seen_nat:
            l["first_of_nation"] = l["nation"]
            seen_nat.add(l["nation"])
        if l["generation"] and (l["nation"], l["generation"]) not in seen_gen:
            l["first_of_generation"] = l["nation"] + ":" + l["generation"]
            seen_gen.add((l["nation"], l["generation"]))


def run(params, c=None):
    c = c or corp.load(params)
    eps = build_episodes(c, params)
    git_tests = []
    n_tests_all = 0
    for ep in eps:
        if passes_min(ep, params):
            git_tests.append(mk_test(c, params, ep))
    ng = nongit_tests(c, params)
    groups = cluster(git_tests, params)
    launches = assemble(c, params, git_tests, groups)
    launches += assemble(c, params, ng, [[i] for i in range(len(ng))])
    launches.sort(key=lambda l: (l["ts_start"], l["launch_id"]))
    n_unified = unify(launches, params)
    firsts(launches, params)
    stats = {
        "git_episodes": len(eps), "git_tests": len(git_tests), "nongit_tests": len(ng),
        "nongit_days_bulk_excluded": sum(v["bulk"] for d in c.nongit.values() for v in d.values()),
        "capped_commits": sum(e["capped"] for e in eps), "lineages_with_commits": len(c.commits),
        "episodes_below_min": len(eps) - len(git_tests),
        "git_tests_with_session": sum(1 for t in git_tests if t["sessions"]),
        "git_tests_with_session_by_ym": dict(sorted(collections.Counter(iso(t["t0"])[:7] for t in git_tests if t["sessions"]).items())),
        "git_tests_by_ym": dict(sorted(collections.Counter(iso(t["t0"])[:7] for t in git_tests).items())),
        "sessions_multi_lineage": len({s for s, v in __import__("itertools").groupby(sorted((s, t["lineage"]) for t in git_tests for s in t["sessions"]), key=lambda x: x[0]) if len({x[1] for x in v}) >= 2}),
    }
    return c, eps, git_tests, ng, launches, stats


def counts(launches, stats, params):
    sh = collections.Counter(l["shape"] for l in launches)
    git = [l for l in launches if not l["nongit"]]
    ng = [l for l in launches if l["nongit"]]
    out = {
        "episodes_git": stats["git_episodes"], "tests_git": stats["git_tests"], "tests_nongit": stats["nongit_tests"],
        "launches": len(launches), "launches_git": len(git), "launches_nongit": len(ng),
        "single": sh["single"], "mirv": sh["mirv"], "unified": sh["unified"],
        "single_git": sum(1 for l in git if l["shape"] == "single"),
        "bands": dict(sorted(collections.Counter(l["yield"]["class"] for l in launches).items())),
        "bands_git": dict(sorted(collections.Counter(l["yield"]["class"] for l in git).items())),
        "nations": dict(sorted(collections.Counter(l["nation"] for l in launches).items())),
        "nations_git": dict(sorted(collections.Counter(l["nation"] for l in git).items())),
        "nongit_nations": dict(sorted(collections.Counter(l["nation"] + (":" + l["nation_inferred"] if l["nation_inferred"] else "") for l in ng).items())),
        "first_tests": sum(1 for l in launches if l["first_test"]),
        "first_of_nation": sum(1 for l in launches if l["first_of_nation"]),
        "first_of_generation": sum(1 for l in launches if l["first_of_generation"]),
        "capped_commits": stats["capped_commits"], "max_warheads": max([l["warheads"] for l in launches] or [0]),
        "warheads_hist": dict(sorted(collections.Counter(min(l["warheads"], 10) for l in launches if l["shape"] == "mirv").items())),
    }
    return out


def public_launch(l):
    d = {k: v for k, v in l.items() if not k.startswith("_")}
    d["ts_start"] = iso(d["ts_start"])
    d["ts_end"] = iso(d["ts_end"])
    d["warhead_list"] = [dict(w, ts=iso(w["ts"])) for w in d["warhead_list"]]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", default=common.DEFAULT_PARAMS)
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    params = load_params(a.params, a.set)
    c, eps, tests, ng, launches, stats = run(params)
    import nations as nat
    nrec = nat.build(c, launches, params)
    ph = params_hash(params)
    h1 = write_json(os.path.join(a.out, "launches.json"), {
        "version": 1, "params_hash": ph, "params": params, "as_of": c.as_of,
        "relations": "present" if c.relations else "absent", "chatgpt_links": "present" if c.chatgpt_links else "absent",
        "launches": [public_launch(l) for l in launches]})
    h2 = write_json(os.path.join(a.out, "nations.json"), {"version": 1, "params_hash": ph, "nations": nrec})
    cnt = counts(launches, stats, params)
    print(common.dumps({"counts": cnt, "stats": stats, "launches_sha256": h1, "nations_sha256": h2, "params_hash": ph}))


if __name__ == "__main__":
    main()
