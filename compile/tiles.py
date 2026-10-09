"""compile/tiles.py: regions (one per lineage), tiles (depth-2 directory per region) and the weighted touches that
drive the fog fields (STRATEGY sections 3 and 4.3; iteration 2: projects are the land, machines are the weather).

A region is a lineage, wherever its bytes lived: `reg_index[(lineage, host)]` and `tile_of[(lineage, host, path)]` are aliases for
every host of the lineage (the old (lineage x host) keys keep resolving), a shared tile is touched once, and a tile carries the host of
its first touch (`first_host`). A copy no longer reveals anything: a tile is explored from its own first touch, nothing else. Tiles
never touched stay unknown (void forever); the tally card counts explored against laid out. Names serve joins only.
"""
import collections
import math

import numpy as np

import corpus as corp
from common import iso

NOLAND_HOSTS = ("github", "cloud")


def w_commit(lines, nfiles):
    return 1 + math.log10(1 + lines / max(1, nfiles))


def w_birth(n):
    return 1 + math.log10(1 + n)


def w_chat(n):
    return 0.25 * math.log2(1 + n)


class Tiles:
    pass


def collect(c, params, nat_index):
    cap = params["yield_cap_lines_per_commit"]
    k_area = params["tile_area_k"]
    hide3 = params["third_party"] == "hidden"
    stats = collections.Counter()
    # ---- which lineages become regions, and on which surfaces -----------------------------------------------------
    own = sorted(i for i in c.own if i in c.commits or i in c.chat)
    dirs = sorted(i for i in c.dirs if (i in c.nongit and any(v["files"] > 0 for v in c.nongit[i].values())) or i in c.chat)
    third = [] if hide3 else sorted(c.third_paths)
    hosts_of = {}
    for L in own:
        hf = c.host_first.get(L, {})
        hs = sorted((h for h in c.lineages[L]["hosts"] if h in hf and h not in NOLAND_HOSTS), key=lambda h: (hf[h], h))
        if not hs:
            hs = sorted(h for h in hf if h not in NOLAND_HOSTS)[:1]
            stats["own_hosts_fallback"] += 1
        hosts_of[L] = hs
    for L in dirs:
        hosts_of[L] = [L.split(":")[1]]
    for L in third:
        hs = sorted(h for h in (c.third_hosts[L] | set(c.lineages[L]["hosts"])) if h not in NOLAND_HOSTS)
        hosts_of[L] = hs
    # ---- per (lineage, path): area weight and first touch anywhere ------------------------------------------------
    pw = collections.defaultdict(lambda: collections.defaultdict(float))
    pfirst = collections.defaultdict(dict)

    def seen(L, p, t):
        d = pfirst[L]
        if p not in d or t < d[p]:
            d[p] = t

    for L in own:
        pw[L]["."] += 0.0
        for (t, ref, cls, name, raw, nfiles, ds, host, nonum, mh) in c.commits.get(L, ()):
            ps = ds or (".",)
            for p in ps:
                pw[L][p] += max(nfiles, 0) / len(ps)
                seen(L, p, t)
    for L in dirs:
        pw[L]["."] += 0.0
        for (t, host, p, kind, n, by, bulk, cls) in c.dir_touch.get(L, ()):
            pw[L][p] += n
            seen(L, p, t)
    for L in third:
        pw[L]["."] += 0.0
        for p, n in c.third_paths[L].items():
            pw[L][p] += n
    # ---- tile table ----------------------------------------------------------------------------------------------
    regions = []  # (lineage, home host = the first evidenced host, kind)
    reg_index = {}
    tile_of = {}
    t_region, t_path, t_w = [], [], []
    for L in own + dirs + third:
        if not hosts_of[L]:
            continue
        kind = "third" if L in c.third else ("dir" if L in c.dirs else "git")
        ri = len(regions)
        regions.append((L, hosts_of[L][0], kind))
        for h in hosts_of[L]:
            reg_index[(L, h)] = ri
        for p in sorted(pw[L]):
            tid = len(t_region)
            for h in hosts_of[L]:
                tile_of[(L, h, p)] = tid
            t_region.append(ri); t_path.append(p); t_w.append(pw[L][p])
    nT = len(t_region)
    first_touch = np.full(nT, np.inf)
    first_host = [None] * nT      # the host of the earliest touch of the tile
    reveal = np.zeros(nT, dtype=bool)
    # ---- touches ---------------------------------------------------------------------------------------------------
    T, TI, G, W, BU = [], [], [], [], []
    burst_min = int(params["nongit_min_files"])
    excl_bulk = bool(params["nongit_exclude_bulk_copy"])

    def touch(t, tile, g, w, burst=False, host=None):
        T.append(t); TI.append(tile); G.append(g); W.append(w); BU.append(burst)
        if t < first_touch[tile] or (t == first_touch[tile] and host is not None and first_host[tile] is None):
            first_touch[tile] = t
            first_host[tile] = host

    for L in own:
        hf = c.host_first.get(L, {})
        hs = hosts_of[L]
        for (t, ref, cls, name, raw, nfiles, ds, host, nonum, mh) in c.commits.get(L, ()):
            g = nat_index.get(cls)
            if g is None:
                continue
            ps = ds or (".",)
            w = w_commit(min(raw, cap), nfiles)
            h = host if host in hs else hs[0]
            if host not in hs:
                stats["commit_host_fallback"] += 1
            for p in ps:   # one touch per tile, whatever number of surfaces carry the commit
                touch(t, tile_of[(L, hs[0], p)], g, w, host=h)
        for (t, sid, cls, n, path, host) in c.chat.get(L, ()):
            g = nat_index.get(cls)
            if g is None:
                continue
            h = host if host in hs else hs[0]
            p = path if (L, h, path) in tile_of else "."
            touch(t, tile_of[(L, h, p)], g, w_chat(n), host=h)
    for L in dirs:
        h = hosts_of[L][0]
        gate = c.dir_git_first.get(L)
        for (t, host, p, kind, n, by, bulk, cls) in c.dir_touch.get(L, ()):
            g = nat_index.get(cls, nat_index.get("human"))
            # a births burst (n >= nongit_min_files, not a bulk copy) steers the camera on its own (DIRECTION 'What steers the camera')
            touch(t, tile_of[(L, h, p)], g, w_birth(n) * (0.5 if bulk else 1.0), burst=(kind == "file_birth" and n >= burst_min and not (bulk and excl_bulk)), host=host if host in hosts_of[L] else h)
        for (t, sid, cls, n, path, host) in c.chat.get(L, ()):
            g = nat_index.get(cls)
            if g is None:
                continue
            p = path if (L, h, path) in tile_of else "."
            touch(t, tile_of[(L, h, p)], g, w_chat(n), host=h)
    # ---- ruins: whole, explored, at clone time ------------------------------------------------------------------------
    clone = {}
    for L in third:
        for h in hosts_of[L]:
            t = c.nc_first.get((L, h))
            basis = "event"
            if t is None:
                t = corp.parse_ts(c.lineages[L]["last_ts"])
                basis = "last_ts"
            clone[(L, h)] = (t, basis)
            stats["ruin_clone_" + basis] += 1
            for p in pw[L]:
                ti = tile_of[(L, h, p)]
                first_touch[ti] = t
                reveal[ti] = True
    # ---- area ---------------------------------------------------------------------------------------------------------
    w = np.array(t_w, dtype=np.float64)
    cells = np.clip(1 + np.floor(k_area * np.log10(1 + w)), 1, 7).astype(np.int32)
    # ---- global tile order: by first touch (epoch), then region, then path -----------------------------------------------
    order = sorted(range(nT), key=lambda i: (first_touch[i], t_region[i], t_path[i]))
    newid = np.empty(nT, dtype=np.int64)
    for k, i in enumerate(order):
        newid[i] = k
    o = np.array(order, dtype=np.int64)
    Tl = Tiles()
    Tl.regions = regions
    Tl.reg_index = reg_index
    Tl.region = np.array(t_region, dtype=np.int32)[o]
    Tl.path = [t_path[i] for i in order]
    Tl.w = w[o]
    Tl.cells = cells[o]
    Tl.first_t = first_touch[o]
    Tl.reveal = reveal[o]
    Tl.touch_T = np.array(T, dtype=np.int64)
    Tl.touch_tile = newid[np.array(TI, dtype=np.int64)] if TI else np.zeros(0, dtype=np.int64)
    Tl.touch_g = np.array(G, dtype=np.int64)
    Tl.touch_w = np.array(W, dtype=np.float64)
    Tl.touch_burst = np.array(BU, dtype=bool)
    Tl.tile_of = {k: int(newid[v]) for k, v in tile_of.items()}
    Tl.hosts_of = hosts_of
    Tl.clone = clone
    Tl.first_host = [first_host[i] for i in order]
    Tl.stats = dict(stats)
    Tl.counts = {"regions": len(regions), "tiles": nT, "cells": int(cells.sum()),
                 "tiles_never_touched": int(np.isinf(first_touch).sum()), "touches": len(T),
                 "regions_git": sum(1 for r in regions if r[2] == "git"), "regions_dir": sum(1 for r in regions if r[2] == "dir"),
                 "regions_third": sum(1 for r in regions if r[2] == "third"),
                 "regions_by_host": dict(sorted(collections.Counter(r[1] for r in regions).items()))}
    return Tl
