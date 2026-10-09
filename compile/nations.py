"""compile/nations.py: one record per nation (actor class) and per model generation inside it (CONTRACT section 8).

Ordered by first appearance. A nation's row enters at its first event of any kind (nation_entry: first_event); a
generation's chip enters at its first test (generation_entry: first_test), which drops strays.
"""
import collections

import names as nm
from common import iso

NATIONS = ("human", "chatgpt", "claude", "codex", "opencode", "local_model", "automation")


def build(c, launches, params):
    g = params["generation_granularity"]
    first_event = dict(c.first_event)
    if c.first_local_offload is not None:
        first_event["local_model"] = min(first_event.get("local_model", c.first_local_offload), c.first_local_offload)
    sess_cls = {sid: s["class"] for sid, s in c.session_info.items()}
    tests = collections.defaultdict(list)
    gtests = collections.defaultdict(list)
    for l in launches:
        tests[l["nation"]].append(l)
        if l["generation"]:
            gtests[(l["nation"], l["generation"])].append(l)
    parts = collections.Counter()
    for l in launches:
        cl = {sess_cls.get(s) for s in l["sessions"]}
        for k in ("claude", "codex", "opencode"):
            if k in cl:
                parts[k] += 1
        if l["seats"]:
            parts["local_model"] += 1
    # first-seen per generation from commit trailers, session models and seats
    seen = {}
    for (cls, raw), t in c.gen_first.items():
        gen = nm.canon(raw, g)
        if gen is None or cls == "third_party":
            continue
        key = (cls, gen)
        if key not in seen or t < seen[key]:
            seen[key] = t
    for b, t in c.first_backend.items():
        gen = nm.seat_model(b, params["seat_models"])
        key = ("local_model", gen)
        if key not in seen or t < seen[key]:
            seen[key] = t

    def ytot(ls):
        return {"lines": sum(x["yield"]["lines"] or 0 for x in ls), "files": sum(x["yield"]["files"] or 0 for x in ls),
                "bytes": sum(x["yield"]["bytes"] or 0 for x in ls)}

    rows = []
    for nat in NATIONS:
        if nat not in first_event:
            continue
        ls = sorted(tests.get(nat, []), key=lambda x: x["ts_start"])
        ft = ls[0]["ts_start"] if ls else None
        entry = first_event[nat] if params["nation_entry"] == "first_event" else ft
        if entry is not None and ft is not None and ft < entry:
            entry = ft  # a launch's start can precede the first event of the class that is credited with it
        rows.append({
            "nation": nat, "generation": None, "entered": entry is not None, "first_ts": iso(entry) if entry is not None else None,
            "first_event_ts": iso(first_event[nat]), "first_test_ts": iso(ft) if ft is not None else None,
            "first_launch_id": ls[0]["launch_id"] if ls else None, "tests": len(ls), "yield_total": ytot(ls),
            "last_ts": iso(ls[-1]["ts_end"]) if ls else None, "participations": parts.get(nat, 0),
            "inferred_tests": sum(1 for x in ls if x["nation_inferred"]),
        })
        gens = sorted({k[1] for k in list(seen) + list(gtests) if k[0] == nat})
        for gen in gens:
            gl = sorted(gtests.get((nat, gen), []), key=lambda x: x["ts_start"])
            ft = gl[0]["ts_start"] if gl else None
            fs = seen.get((nat, gen))
            entry = ft if params["generation_entry"] == "first_test" else fs
            rows.append({
                "nation": nat, "generation": gen, "entered": entry is not None, "first_ts": iso(entry) if entry is not None else None,
                "first_event_ts": None, "first_seen_ts": iso(fs) if fs is not None else None,
                "first_test_ts": iso(ft) if ft is not None else None,
                "first_launch_id": gl[0]["launch_id"] if gl else None, "tests": len(gl), "yield_total": ytot(gl),
                "last_ts": iso(gl[-1]["ts_end"]) if gl else None, "participations": 0, "inferred_tests": 0,
            })
    # order by first appearance: nation rows by entry, generation rows after their nation by entry
    nat_order = {r["nation"]: (r["first_ts"] or "9999", i) for i, r in enumerate(r for r in rows if r["generation"] is None)}
    rows.sort(key=lambda r: (nat_order[r["nation"]], r["generation"] is not None, r["first_ts"] or "9999", r["generation"] or ""))
    return rows
