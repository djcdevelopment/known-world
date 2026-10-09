"""PROBE-00: launches under the payload model, default thresholds. Counts only; never prints a corpus line.

Run from the repo root: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/PROBE-00-launches/probe.py
Reference implementation of DIRECTION.md episode detection for compile/launches.py (CONTRACT.md section 8).
"""
import collections
import datetime as dt
import json

GAP = dt.timedelta(hours=2)
OVERLAP = dt.timedelta(minutes=30)
MIN_LINES, MIN_FILES = 50, 3


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    repos = json.load(open("corpus/merged/repos.json"))
    third_party = {l["id"] for l in repos["lineages"] if l.get("third_party")}
    sessions = json.load(open("corpus/merged/sessions.json"))["sessions"]
    sess_by_repo = collections.defaultdict(list)
    for s in sessions:
        if s.get("repo") and s.get("first_ts"):
            t0 = ts(s["first_ts"])
            sess_by_repo[s["repo"]].append((t0, t0 + dt.timedelta(seconds=s.get("duration_s") or 0), s.get("class")))
    commits = collections.defaultdict(list)
    first = {}
    with open("corpus/merged/events.ndjson") as f:
        for line in f:
            e = json.loads(line)
            t, k = e.get("ts"), e.get("kind")
            if not t:
                continue
            a = e.get("actor") or {}
            c = a.get("class")
            if c and c != "third_party" and k in ("commit", "chat_session", "offload_call", "chat_msg"):
                if c not in first or t < first[c]:
                    first[c] = t
            if k == "commit" and e.get("repo") not in third_party:
                m = e.get("magnitude") or {}
                commits[e["repo"]].append((ts(t), c, (m.get("ins") or 0) + (m.get("del") or 0), m.get("files") or 0,
                                           tuple(e.get("files") or [])))
    episodes = []
    for repo, cs in commits.items():
        cs.sort(key=lambda c: c[0])
        cur = None
        for c in cs:
            if cur and c[0] - cur["end"] <= GAP:
                cur["end"] = c[0]; cur["n"] += 1; cur["lines"] += c[2]; cur["files"] += c[3]
                cur["dirs"].update(c[4]); cur["cls"][c[1]] += 1
            else:
                if cur:
                    episodes.append(cur)
                cur = {"repo": repo, "start": c[0], "end": c[0], "n": 1, "lines": c[2], "files": c[3],
                       "dirs": set(c[4]), "cls": collections.Counter([c[1]])}
        if cur:
            episodes.append(cur)
    tests = [e for e in episodes if e["lines"] >= MIN_LINES or e["files"] >= MIN_FILES]
    for e in tests:
        sc = collections.Counter()
        for s0, s1, cl in sess_by_repo.get(e["repo"], []):
            if s0 <= e["end"] + OVERLAP and s1 >= e["start"] - OVERLAP:
                sc[cl] += 1
        ai = [c for c in e["cls"] if c in ("claude", "codex", "opencode", "automation", "local_model")]
        e["nation"] = max(ai, key=e["cls"].get) if ai else (sc.most_common(1)[0][0] if sc else "human")
    tests.sort(key=lambda e: e["start"])
    launches, cur = [], None
    for e in tests:
        if cur and e["start"] - cur["last"] <= GAP:
            cur["eps"].append(e); cur["last"] = max(cur["last"], e["end"])
        else:
            if cur:
                launches.append(cur)
            cur = {"eps": [e], "last": e["end"], "start": e["start"]}
    if cur:
        launches.append(cur)
    by_month = collections.defaultdict(collections.Counter)
    bands, nations, warheads = collections.Counter(), collections.Counter(), collections.Counter()
    for l in launches:
        n = len({e["repo"] for e in l["eps"]})
        lines = sum(e["lines"] for e in l["eps"])
        by_month[l["start"].strftime("%Y-%m")]["mirv" if n >= 2 else "single"] += 1
        bands["<100" if lines < 100 else "<1k" if lines < 1000 else "<10k" if lines < 10000 else "<100k" if lines < 100000 else ">=100k"] += 1
        nations[collections.Counter(e["nation"] for e in l["eps"]).most_common(1)[0][0]] += 1
        warheads[min(n, 10)] += 1
    print("lineages", len(commits), "episodes", len(episodes), "tests", len(tests), "launches", len(launches))
    for ym in sorted(by_month):
        print(ym, by_month[ym]["single"], by_month[ym]["mirv"])
    print("warheads", dict(sorted(warheads.items())))
    print("bands", dict(bands))
    print("nations", dict(nations))
    print("first appearance", sorted(first.items(), key=lambda kv: kv[1]))


if __name__ == "__main__":
    main()
