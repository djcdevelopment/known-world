#!/usr/bin/env python3
"""relations.py: corpus/merged/relations.json from the 12 constellation.yaml files plus jepa-graph.v1.json (task 1b).

Reads only (mounts are read-only): constellation.yaml x12, manifest/exports/jepa-graph.v1.json, corpus/merged/repos.json.
Joins manifest repos to lineages: github slug (basis "github": the scanner forbids a key named slug), directory basename of local_path, repo name, alias, known renames.
Needs PyYAML (use the system python3 -I if the venv lacks it). Deterministic; prints counts only.
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
import yaml  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOUNT = {"C": "/mnt/omen-c-read", "E": "/mnt/omen-e-read"}
YAMLS = ["E:/work/gad", "C:/work/commandcenter", "C:/work/baseline", "E:/work/planning",
         "C:/work/steppeintegrations-site", "E:/work/ai-systems-research", "C:/work/lumberjacks-platform",
         "C:/work/irc", "C:/work/404", "C:/work/notebook", "C:/work/contextlandscape", "E:/resume"]
JEPA = "/mnt/omen-e-read/work/manifest/exports/jepa-graph.v1.json"
RENAMES = {"old-goat-new-tricks": "llmquest", "guild": "goatsafterdark", "img": "tempo-imagegen",
           "reader": "indexcard", "planner": "start-planner"}
MAXS = 100


def cut(s):
    s = " ".join(str(s or "").split())
    return s[:MAXS]


def lst(v):
    if v is None:
        return []
    return [str(x).lower() for x in (v if isinstance(v, list) else [v])]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    # --out DIR: read repos.json from and write relations.json to DIR (default corpus/merged)
    outdir = os.path.abspath(argv[argv.index("--out") + 1]) if "--out" in argv else os.path.join(ROOT, "corpus/merged")
    repos = json.load(open(os.path.join(outdir, "repos.json")))
    L = {l["id"]: l for l in repos["lineages"]}
    by_slug, by_name = defaultdict(list), defaultdict(list)
    for l in repos["lineages"]:
        for r in l.get("remotes", []):
            r = r.lower()
            if r.endswith(".git"):
                r = r[:-4]
            if r.startswith("github.com/"):
                by_slug[r[len("github.com/"):]].append(l["id"])
        for n in l.get("names", []):
            by_name[n.lower()].append(l["id"])

    def best(ids):
        ids = sorted(set(ids))
        return max(ids, key=lambda i: (L[i].get("commits", 0), i)) if ids else None

    nodes, cons = {}, {}
    edges = []
    for p in YAMLS:
        d = yaml.safe_load(open(MOUNT[p[0]] + p[2:] + "/constellation.yaml"))
        cn = d["constellation"]["name"]
        members = []
        cons[cn] = {"name": cn, "primary": None, "members": members, "topology": d.get("topology"),
                    "archetype": d.get("archetype")}
        for r in d["repos"]:
            nm = str(r["name"]).lower()
            nd = nodes.setdefault(nm, {"name": nm, "constellation": cn, "constellations": [], "primary": False,
                                       "kind": r.get("kind"), "lifecycle": r.get("lifecycle"),
                                       "role": cut(r.get("role")), "github": r.get("github"), "_aliases": set(),
                                       "_dir": None, "source": "yaml"})
            if cn not in nd["constellations"]:
                nd["constellations"].append(cn)
            if r.get("primary"):
                nd["primary"] = True
                cons[cn]["primary"] = nm
            if not nd["github"] and r.get("github"):
                nd["github"] = r["github"]
            nd["_aliases"].update(lst(r.get("aliases")))
            lp = r.get("local_path")
            if lp and not nd["_dir"]:
                nd["_dir"] = str(lp).replace("\\", "/").rstrip("/").split("/")[-1].lower()
            members.append(nm)
            for dep in lst(r.get("depends_on")):
                edges.append({"src": nm, "dst": dep, "type": "depends_on", "source": "yaml", "_c": cn})
            if r.get("parent"):
                edges.append({"src": nm, "dst": str(r["parent"]).lower(), "type": "parent", "source": "yaml", "_c": cn})
        for c in d.get("contracts") or []:
            if c.get("scope") == "intra-repo":
                continue
            for cr in lst(c.get("consumer_repos")):
                edges.append({"src": str(c.get("producer_repo")).lower(), "dst": cr, "type": "contract",
                              "source": "yaml", "_c": cn})
        for ds in d.get("data_sources") or []:
            for cr in lst(ds.get("consumed_by")):
                edges.append({"src": "data_source:" + cut(ds.get("name"))[:60].lower(), "dst": cr,
                              "type": "data_source", "source": "yaml", "_c": cn, "src_kind": "data_source"})
    for c in cons.values():
        c["members"] = sorted(set(c["members"]))
    # typed jepa edges
    g = json.load(open(JEPA))
    jself = 0
    ninfo = {n["name"].lower(): n for n in g["nodes"]}
    for n in g["nodes"]:
        nm = n["name"].lower()
        if nm not in nodes:
            nodes[nm] = {"name": nm, "constellation": (n.get("constellations") or [None])[0],
                         "constellations": list(n.get("constellations") or []), "primary": False, "kind": None,
                         "lifecycle": n.get("lifecycle"), "role": cut(n.get("role")), "github": None,
                         "_aliases": set(), "_dir": (str(n.get("local_path") or "").replace("\\", "/").rstrip("/")
                                                     .split("/")[-1].lower() or None), "source": "jepa"}
        for r in n["relationships"]:
            dst = r["target_repo"].lower()
            if dst == nm:
                jself += 1
                continue
            e = {"src": nm, "dst": dst, "type": r["type"], "source": "jepa", "inferred_valid_from": r.get("valid_from")}
            if dst not in ninfo and dst not in nodes:
                e["dst_kind"] = "constellation"
            edges.append(e)
    # join
    basis = {}
    for nm, nd in sorted(nodes.items()):
        lid, b = None, "unjoined"
        slug = (nd["github"] or "").lower()
        if slug and by_slug.get(slug):
            lid, b = best(by_slug[slug]), "github"
        elif nd["_dir"] and by_name.get(nd["_dir"]):
            lid, b = best(by_name[nd["_dir"]]), "dirname"
        elif by_name.get(nm):
            lid, b = best(by_name[nm]), "name"
        else:
            for a in sorted(nd["_aliases"]):
                if by_name.get(a):
                    lid, b = best(by_name[a]), "alias"
                    break
            else:
                if nm in RENAMES and by_name.get(RENAMES[nm]):
                    lid, b = best(by_name[RENAMES[nm]]), "rename"
        nd["lineage"], nd["join_basis"] = lid, b
    # edge dedupe, scope, since
    def lin(n):
        return nodes[n]["lineage"] if n in nodes else None

    seen, out = set(), []
    for e in edges:
        key = (e["src"], e["dst"], e["type"], e["source"])
        if key in seen or e["src"] == e["dst"]:
            continue
        seen.add(key)
        s, t = nodes.get(e["src"]), nodes.get(e["dst"])
        if e.get("src_kind") == "data_source":
            scope = "intra"
        elif e.get("dst_kind") == "constellation" or not s or not t:
            scope = "cross-constellation" if e.get("dst_kind") else "intra"
        else:
            scope = "intra" if set(s["constellations"]) & set(t["constellations"]) else "cross-constellation"
        e["scope"] = scope
        ts = [L[x]["first_ts"] for x in (lin(e["src"]), lin(e["dst"])) if x and L[x].get("first_ts")]
        both = (e.get("src_kind") == "data_source" and lin(e["dst"])) or (lin(e["src"]) and lin(e["dst"]))
        e["since"] = max(ts) if ts and both else None
        e.pop("_c", None)
        out.append(e)
    out.sort(key=lambda e: (e["type"], e["src"], e["dst"], e["source"]))
    integ = defaultdict(lambda: Counter())
    for e in out:
        a, b = lin(e["src"]), lin(e["dst"]) if e.get("dst_kind") != "constellation" else None
        if e["type"] == "contract":
            if a: integ[a]["contracts_out"] += 1
            if b: integ[b]["contracts_in"] += 1
        elif e["type"] == "data_source":
            if b: integ[b]["data_sources"] += 1
        elif e["type"] == "depends_on":
            if a: integ[a]["depends_out"] += 1
            if b: integ[b]["depends_in"] += 1
        if e["scope"] == "cross-constellation":
            for x in (a, b):
                if x: integ[x]["cross_constellation"] += 1
    keys = ["contracts_out", "contracts_in", "data_sources", "depends_out", "depends_in", "cross_constellation"]
    integrations = {k: {f: integ[k][f] for f in keys} for k in sorted(integ)}
    nl = []
    for nm in sorted(nodes):
        nd = nodes[nm]
        nl.append({k: nd[k] for k in ("name", "constellation", "constellations", "primary", "kind", "lifecycle",
                                       "role", "github", "lineage", "join_basis", "source")})
    joined = [n for n in nl if n["lineage"]]
    res = {"version": 1, "as_of": repos.get("as_of"), "nodes": nl, "edges": out,
           "constellations": sorted(cons.values(), key=lambda c: c["name"]), "integrations": integrations,
           "coverage": {"manifest_repos": len(nl), "joined": len(joined),
                        "joined_by_basis": dict(sorted(Counter(n["join_basis"] for n in joined).items())),
                        "unjoined": sorted(n["name"] for n in nl if not n["lineage"]),
                        "lineages_without_manifest": len(set(L) - {n["lineage"] for n in joined}),
                        "jepa_self_edges_dropped": jself,
                        "edges_by_type": dict(sorted(Counter(e["type"] for e in out).items())),
                        "edges_by_scope": dict(sorted(Counter(e["scope"] for e in out).items()))}}
    _dst = os.path.join(outdir, "relations.json")
    with open(_dst + ".tmp", "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(_dst + ".tmp", _dst)  # atomic: readers stream corpus/merged
    c = res["coverage"]
    print("nodes=%d joined=%d unjoined=%d edges=%d self_dropped=%d" % (
        c["manifest_repos"], c["joined"], len(c["unjoined"]), len(out), jself))


if __name__ == "__main__":
    main()
