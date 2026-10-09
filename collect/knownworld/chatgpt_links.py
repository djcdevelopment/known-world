#!/usr/bin/env python3
"""chatgpt_links.py: corpus/merged/chatgpt_links.json from the chatGPT_parser projections (task 1b part 2).

Reads metadata fields only, by explicit name, from timeline, session_classification, decision_trace,
artifact_workflow_paths, artifact_index (counts and file_references paths only) and activity_calendar.
Never reads title, title_hint, text*, *_preview, intent_terms, caption_text, segments, search_index, graph nodes.
Paths are model-written intent: drive-letter paths only (D: maps to omen-e per CONTRACT), reduced to the top two
components, joined to lineages by directory name. Relative and /mnt/data paths are dropped. Prints counts only.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJ = "/mnt/omen-e-read/work/chatGPT_parser/data/projections/"
DRIVE = {"C": "omen-c", "D": "omen-e", "E": "omen-e"}
SKIP_TOP = {"users", "python312", "windows", "program files", "program files (x86)", "programdata", "temp", "tmp"}
COMP = re.compile(r"^[A-Za-z0-9._\- ]{1,48}$")
DRV = re.compile(r"^([A-Za-z]):[\\/](.*)$")


def stream(name):
    with open(PROJ + name + ".ndjson", "rb") as f:
        for raw in f:
            raw = raw.strip()
            if raw:
                yield json.loads(raw)


def iso(t):
    if t is None:
        return None
    return datetime.fromtimestamp(float(t), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def project_of(p):
    """(host, 'a/b') or None for a model-written path string."""
    if not isinstance(p, str):
        return None
    m = DRV.match(p.strip())
    if not m or m.group(1).upper() not in DRIVE:
        return None
    parts = [c for c in re.split(r"[\\/]+", m.group(2)) if c]
    if not parts or parts[0].lower() in SKIP_TOP:
        return None
    top = parts[:2] if parts[0].lower() == "work" and len(parts) > 1 else parts[:1]
    if not all(COMP.match(c) for c in top):
        return None
    return DRIVE[m.group(1).upper()], "/".join(top)


def main():
    repos = json.load(open(os.path.join(ROOT, "corpus/merged/repos.json")))
    by_name = defaultdict(list)
    for l in repos["lineages"]:
        for n in l.get("names", []):
            by_name[n.lower()].append(l)

    def match(host, proj):
        base = proj.split("/")[-1].lower()
        c = by_name.get(base, [])
        pref = [l for l in c if host in l.get("hosts", [])]
        pick = pref or c
        return sorted(pick, key=lambda l: (-l.get("commits", 0), l["id"]))[:1]

    conv = {}
    for r in stream("timeline"):
        conv[r["conversation_id"]] = {
            "conversation_id": r["conversation_id"], "create_time": iso(r.get("create_time")),
            "update_time": iso(r.get("update_time")),
            "duration_s": int(round(r["duration_seconds"])) if r.get("duration_seconds") is not None else None,
            "messages": r.get("message_count"), "artifacts": r.get("artifact_count"), "has_code": r.get("has_code"),
            "phase_label": r.get("phase_label"), "strategy_label": None, "_paths": [(r.get("key_file_paths") or [])]}
    for r in stream("session_classification"):
        c = conv.get(r["conversation_id"])
        if c and not c["phase_label"]:
            c["phase_label"] = r.get("phase_label")
        if c and c["has_code"] is None:
            c["has_code"] = r.get("has_code")
    for r in stream("decision_trace"):
        c = conv.get(r["conversation_id"])
        if c:
            c["strategy_label"] = r.get("strategy_label")
            c["_paths"].append(r.get("key_file_paths") or [])
    for r in stream("artifact_workflow_paths"):
        c = conv.get(r["conversation_id"])
        if c:
            c["_paths"].append([r.get("file_path")])
    art = Counter()
    for r in stream("artifact_index"):
        c = conv.get(r["conversation_id"])
        if c:
            art[r.get("artifact_type")] += 1
            c["_paths"].append(r.get("file_references") or [])
    out, matched, ids = [], 0, set()
    for cid in sorted(conv, key=lambda k: (conv[k]["create_time"] or "", k)):
        c = conv[cid]
        projs, hosts = set(), set()
        for grp in c.pop("_paths"):
            for p in grp:
                pr = project_of(p)
                if pr:
                    hosts.add(pr)
        lins = []
        for h, pj in sorted(hosts):
            projs.add(pj)
            for l in match(h, pj):
                lins.append(l["id"])
        c["projects"] = sorted(projs)
        c["lineages"] = sorted(set(lins))
        c["has_code"] = bool(c["has_code"])
        out.append(c)
        if lins:
            matched += 1
            ids.update(lins)
    cal = [{"date": r["date"], "conversations": r["conversation_count"], "messages": r["message_count"],
            "artifacts": r["artifact_count"], "commands": r["command_invocation_count"],
            "error_conversations": r["error_conversation_count"]} for r in stream("activity_calendar")]
    cal.sort(key=lambda r: r["date"])
    year = Counter((c["create_time"] or "0000")[:4] for c in out)
    year_p = Counter((c["create_time"] or "0000")[:4] for c in out if c["projects"])
    res = {"version": 1, "conversations": out,
           "series": {"chatgpt_activity": cal},
           "coverage": {"conversations": len(out), "with_projects": sum(1 for c in out if c["projects"]),
                        "with_lineages": matched, "lineages_matched": len(ids),
                        "by_year": dict(sorted(year.items())), "with_projects_by_year": dict(sorted(year_p.items())),
                        "artifacts_by_type": dict(sorted((k or "none", v) for k, v in art.items())),
                        "calendar_days": len(cal)}}
    _dst = os.path.join(ROOT, "corpus/merged/chatgpt_links.json")
    with open(_dst + ".tmp", "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(_dst + ".tmp", _dst)  # atomic: readers stream corpus/merged
    c = res["coverage"]
    print("conversations=%d with_projects=%d with_lineages=%d lineages_matched=%d days=%d" % (
        c["conversations"], c["with_projects"], c["with_lineages"], c["lineages_matched"], c["calendar_days"]))


if __name__ == "__main__":
    main()
