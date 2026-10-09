"""compile/audit.py: the non-git launch audit (Fable review of slices 1 to 3). Non-git launches by top-level directory and
year with files and bytes, counts at nongit_min_files 3 / 10 / 20, and the git-lineage gate (a directory that later gains a
git lineage counts as non-git only before its first commit). Directories are labelled host#hash: names never leave the corpus.
"""
import collections
import hashlib

import launches as L
from common import iso


def label(lin):
    h = lin.split(":")[1]
    return "%s#%s" % (h, hashlib.sha1(lin.encode()).hexdigest()[:5])


def audit(c, params, thresholds=(3, 10, 20)):
    out = {"thresholds": {}, "by_dir_year": {}, "gate": {"dirs_with_git_lineage": len(c.dir_git_first)}}
    for thr in thresholds:
        ng = L.nongit_tests(c, params, min_files=thr)
        rows = collections.defaultdict(lambda: {"launches": 0, "files": 0, "bytes": 0})
        for e in ng:
            k = (label(e["lineage"]), iso(e["t0"])[:4])
            r = rows[k]
            r["launches"] += 1; r["files"] += e["files"]; r["bytes"] += e["bytes"]
        nat = collections.Counter(e["nation"] + (":" + e["nation_inferred"] if e["nation_inferred"] else "") for e in ng)
        yrs = collections.Counter(iso(e["t0"])[:4] for e in ng)
        out["thresholds"][str(thr)] = {
            "launches": len(ng), "files": sum(e["files"] for e in ng), "bytes": sum(e["bytes"] for e in ng),
            "directories": len({e["lineage"] for e in ng}), "by_year": dict(sorted(yrs.items())), "nations": dict(sorted(nat.items())),
            "first": iso(min(e["t0"] for e in ng)) if ng else None}
        out["by_dir_year"][str(thr)] = [{"dir": k[0], "year": k[1], **v} for k, v in sorted(rows.items(), key=lambda kv: (kv[0][1], -kv[1]["files"], kv[0][0]))]
    # launches the gate removed at the default threshold (days on or after the first commit of the same directory)
    ms = params["nongit_min_files"]
    removed = 0
    for lin, gate in c.dir_git_first.items():
        removed += sum(1 for d, v in c.nongit.get(lin, {}).items() if v["files"] >= ms and v["t0"] is not None and v["t0"] >= gate)
    out["gate"]["active_days_removed_at_default"] = removed
    return out
