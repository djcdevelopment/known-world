"""Waterfall from PROBE-00 to the default arm: flip one switch at a time and count git launches. Counts only."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "compile"))
import collections
import common
import launches as L

base = common.load_params()
steps = [
    ("PROBE-00 parity (time_window, no span cap, third-party commits kept, no lines cap, lineage targets only)",
     {"engagement_union": "time_window", "engagement_max_span_h": None, "exclude_third_party_commits": False,
      "yield_cap_lines_per_commit": 10 ** 12, "mirv_count_worktrees": False}),
    ("+ exclude third-party-class commits in own lineages", {"exclude_third_party_commits": True}),
    ("+ lines cap 20,000 per commit", {"yield_cap_lines_per_commit": 20000}),
    ("+ engagement_max_span_h 12 (control arm minus worktree targets)", {"engagement_max_span_h": 12}),
    ("+ worktree births as targets (= control arm: time_window)", {"mirv_count_worktrees": True}),
    ("engagement_union: session (= default arm)", {"engagement_union": "session"}),
]
p = dict(base)
c = None
rows = []
for name, ch in steps:
    p.update(ch)
    if c is None or "exclude_third_party_commits" in ch:
        import corpus
        c = corpus.load(p)
    _, eps, tests, ng, ls, st = L.run(dict(p), c)
    git = [l for l in ls if not l["nongit"]]
    sh = collections.Counter(l["shape"] for l in git)
    rows.append({"step": name, "episodes": st["git_episodes"], "tests": st["git_tests"], "launches": len(git),
                 "single": sh["single"], "mirv": sh["mirv"], "unified": sh["unified"]})
    print(json.dumps(rows[-1]))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "waterfall.json"), "w"), indent=1)
