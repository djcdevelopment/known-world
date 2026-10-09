"""compile/stream.py: the stream (DIRECTION 'The stream', slice 9). A vertical lane diagram of Derek's lineages.

Everything the page draws is a lookup: per-frame lane slots (id, x, alpha, entry frame), the commit table (frame, lane,
nation, dot code, surface side), branch / worktree rails, MIRV and association connectors and the time ruler. The lane
simulation is a pure function of the corpus, the clock and the parameters (no clock reads, no randomness).
"""
import calendar
import collections
import hashlib
import math

import numpy as np

K_SLOTS = 18  # lane entries per frame: stream_max_lanes visible plus lanes still fading out
SLOT_NONE = 255
COL_W = 260
RULER_W = 56
LANE_X0_REL = RULER_W  # first lane column, relative to the column's left edge
LANE_W = COL_W - RULER_W - 6
TIERS = (4, 7, 10, 14)
PITCH_CAP = 32.0
DWELL_F = 90        # an incumbent is not displaced in its first 3 s
TIER_DOWN_F = 150   # a narrower tier waits 5 s


def _ss(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def lane_label(name, mode, lineage):
    if mode == "hashed":
        return "h" + hashlib.sha1(("kw-stream:" + lineage).encode()).hexdigest()[:6]
    return name


def build(params, c, clock, launches, Wd, Tl, rfirst, nat_index):
    F, fps = clock.F, clock.fps
    tau = clock.tau_frames()
    Wf = int(round(params["stream_window_s"] * fps))
    fade_f = max(2, int(round(params["stream_fade_s"] * fps)))
    cap = float(params["yield_cap_lines_per_commit"])
    max_lanes = int(params["stream_max_lanes"])
    dormant = float(params["stream_dormant_days"])
    rel = c.relations or {"nodes": [], "constellations": [], "edges": []}
    node_of = {n["lineage"]: n for n in rel["nodes"] if n.get("lineage")}
    # ---- lanes: own lineages with counted commits, ordered by constellation then first_ts ----------------------------
    lins = [l for l in c.commits if c.commits[l]]
    cfirst = {}
    for l in lins:
        cn = node_of.get(l, {}).get("constellation")
        if cn:
            cfirst[cn] = min(cfirst.get(cn, "9999"), c.lineages[l]["first_ts"])
    cord = {cn: i for i, cn in enumerate(sorted(cfirst, key=lambda k: (cfirst[k], k)))}
    ncon = len(cord)

    def key(l):
        cn = node_of.get(l, {}).get("constellation")
        return (cord.get(cn, ncon), c.lineages[l]["first_ts"], l)
    lins.sort(key=key)
    L = len(lins)
    assert L < SLOT_NONE
    lane_of = {l: i for i, l in enumerate(lins)}
    lane_con = [cord.get(node_of.get(l, {}).get("constellation"), -1) for l in lins]
    names = []
    for l in lins:
        nm = node_of.get(l, {}).get("name") or (c.lineages[l].get("names") or [l[:8]])[0]
        names.append(lane_label(nm, params["stream_labels"], l))
    # ---- two-surface lineages: the host bridge frame ----------------------------------------------------------------
    bridge_f = np.full(L, -1, dtype=np.int64)
    side_host = {}  # lane -> host that rides the second rail
    for b in Wd.bridges:
        if b["kind"] != "host":
            continue
        la, ha, _ = Tl.regions[b["a"]]
        lb, hb, _ = Tl.regions[b["b"]]
        if la != lb or la not in lane_of:
            continue
        i = lane_of[la]
        fb = int(max(rfirst[b["a"]], rfirst[b["b"]]))
        if fb >= F:
            continue
        if bridge_f[i] < 0 or fb < bridge_f[i]:
            bridge_f[i] = fb
            side_host[i] = hb if rfirst[b["b"]] >= rfirst[b["a"]] else ha
    # ---- commits table ---------------------------------------------------------------------------------------------------
    rows = []
    for l in lins:
        i = lane_of[l]
        for x in c.commits[l]:
            raw = min(float(x[4]), cap)
            code = int(round(255 * math.log10(1 + raw) / math.log10(1 + cap)))
            side = 1 if (i in side_host and x[7] == side_host[i]) else 0
            rows.append((int(clock.frame(np.array([x[0]], dtype=np.int64))[0]), i, nat_index[x[2]], code, side, x[1]))
    rows.sort()
    cm_f = np.array([r[0] for r in rows], dtype=np.int32)
    cm_lane = np.array([r[1] for r in rows], dtype=np.uint8)
    cm_nat = np.array([r[2] for r in rows], dtype=np.uint8)
    cm_code = np.array([r[3] for r in rows], dtype=np.uint8)
    cm_side = np.array([r[4] for r in rows], dtype=np.uint8)
    # ---- per-lane activity vectors -------------------------------------------------------------------------------------
    cnt = np.zeros((F, L), dtype=np.int32)
    np.add.at(cnt, (cm_f.astype(np.int64), cm_lane.astype(np.int64)), 1)
    cumT = np.cumsum(cnt, axis=0, dtype=np.int32)
    lastT = np.full((F, L), -1, dtype=np.int32)
    ar = np.arange(F, dtype=np.int32)[:, None]
    lastT = np.where(cnt > 0, ar, -1)
    lastT = np.maximum.accumulate(lastT, axis=0)
    first_f = np.array([int(cm_f[cm_lane == i].min()) for i in range(L)])
    # earliest commit inside the trailing window (the entry mark of a lane that enters or returns)
    # ---- the lane simulation ------------------------------------------------------------------------------------------------
    alpha = np.zeros(L)
    inv = np.zeros(L, dtype=bool)
    t_in = np.full(L, -10 ** 9)
    since = np.zeros(L, dtype=np.int64)
    xcur = np.zeros(L); xfrom = np.zeros(L); xto = np.zeros(L); xt0 = np.zeros(L, dtype=np.int64)
    sl_id = np.full((F, K_SLOTS), SLOT_NONE, dtype=np.uint8)
    sl_x = np.zeros((F, K_SLOTS), dtype=np.float32)
    sl_a = np.zeros((F, K_SLOTS), dtype=np.uint8)
    sl_since = np.zeros((F, K_SLOTS), dtype=np.int32)
    quiet = np.zeros(F, dtype=np.uint8)
    nvis = np.zeros(F, dtype=np.uint8)
    tier, tier_low = TIERS[0], 0
    overflow = 0
    swaps = 0
    ratio = float(params["stream_swap_ratio"])
    edges = []
    byname = {n["name"]: n.get("lineage") for n in rel["nodes"]}
    cross = params["stream_assoc"]
    for e in rel["edges"]:
        if e["scope"] != "cross-constellation":
            continue
        if cross == "contract" and e["type"] != "contract":
            continue
        sa, sb = byname.get(e["src"]), byname.get(e["dst"])
        if sa in lane_of and sb in lane_of and sa != sb:
            edges.append((lane_of[sa], lane_of[sb], e["type"]))
    edge_f = [-1] * len(edges)
    order_idx = np.arange(L)
    for f in range(F):
        win0 = cumT[f - Wf] if f - Wf >= 0 else 0
        score = (cumT[f] - win0).astype(np.int64)
        last = lastT[f].astype(np.int64)
        has = last >= 0
        lastc = np.where(has, last, 0)
        alive = has & (((f - lastc) <= Wf) | ((tau[f] - tau[lastc]) <= dormant))
        # lanes leave
        gone = inv & ~alive
        inv[gone] = False
        # lanes enter (free slots first)
        cand = (~inv) & alive & (score > 0) & (first_f <= f)
        nfree = max_lanes - int(inv.sum())
        if cand.any():
            ci = np.nonzero(cand)[0]
            ci = ci[np.lexsort((ci, -score[ci]))]
            for i in ci[:max(0, nfree)]:
                inv[i] = True
                if alpha[i] <= 0:
                    since[i] = max(0, f - Wf + 1) + int(np.nonzero(cnt[max(0, f - Wf + 1):f + 1, i])[0][0])
                    xcur[i] = -1.0  # placed on the first slot assignment
                t_in[i] = f
            rest = ci[max(0, nfree):]
            if len(rest) and nfree <= 0:
                inc = np.nonzero(inv & ((f - t_in) >= DWELL_F))[0]
                if len(inc):
                    w = inc[np.lexsort((-inc, score[inc]))][0]
                    cbest = rest[0]
                    if score[cbest] > ratio * score[w]:
                        inv[w] = False
                        inv[cbest] = True
                        if alpha[cbest] <= 0:
                            since[cbest] = max(0, f - Wf + 1) + int(np.nonzero(cnt[max(0, f - Wf + 1):f + 1, cbest])[0][0])
                            xcur[cbest] = -1.0
                        t_in[cbest] = f
                        swaps += 1
        quiet[f] = min(255, int((alive & (first_f <= f)).sum() - inv.sum()))
        # tier and slots
        n_in = int(inv.sum())
        need = next((t for t in TIERS if t >= n_in), TIERS[-1])
        if need > tier:
            tier, tier_low = need, 0
        elif need < tier:
            tier_low += 1
            if tier_low >= TIER_DOWN_F:
                tier, tier_low = need, 0
        else:
            tier_low = 0
        pitch = min(PITCH_CAP, LANE_W / tier)
        slot = 0
        for i in np.nonzero(inv)[0]:
            tgt = LANE_X0_REL + (slot + 0.5) * pitch
            slot += 1
            if xcur[i] < 0:
                xcur[i] = xfrom[i] = xto[i] = tgt; xt0[i] = f
            elif abs(tgt - xto[i]) > 1e-9:
                xfrom[i], xto[i], xt0[i] = xcur[i], tgt, f
        for i in np.nonzero(inv)[0]:
            xcur[i] = xfrom[i] + (xto[i] - xfrom[i]) * _ss((f - xt0[i]) / fade_f)
        # alpha
        alpha = np.where(inv, np.minimum(1.0, alpha + 1.0 / fade_f), np.maximum(0.0, alpha - 1.0 / fade_f))
        vis = np.nonzero(alpha > 0)[0]
        if len(vis) > K_SLOTS:
            keep = vis[np.lexsort((vis, -alpha[vis]))][:K_SLOTS]
            overflow += len(vis) - K_SLOTS
            vis = np.sort(keep)
        for k, i in enumerate(vis):
            sl_id[f, k] = i; sl_x[f, k] = xcur[i]; sl_a[f, k] = int(round(alpha[i] * 255)); sl_since[f, k] = since[i]
        nvis[f] = int(inv.sum())
        for j, (a, b, _t) in enumerate(edges):
            if edge_f[j] < 0 and inv[a] and inv[b]:
                edge_f[j] = f
    # ---- rails: branch and worktree events, rejoining at a unified launch or fading after stream_rail_days --------------------
    unif = collections.defaultdict(list)
    for l in launches:
        if l["shape"] == "unified" and l["lineage"] in lane_of:
            unif[l["lineage"]].append(l["ts_start"])
    rdays = float(params["stream_rail_days"]) * 86400
    rl = []
    for l in lins:
        i = lane_of[l]
        evs = sorted(c.births.get(l, ()))
        for k, (t, kind, ref, host, path) in enumerate(evs):
            f0 = int(clock.frame(np.array([t], dtype=np.int64))[0])
            end_t = t + rdays
            joined = 0
            for u in sorted(unif.get(l, ())):
                if t < u <= end_t:
                    end_t, joined = u, 1
                    break
            f1 = int(clock.frame(np.array([int(end_t)], dtype=np.int64))[0])
            rl.append((f0, i, max(f1, f0 + 1), (1 if kind == "worktree" else 0) | (joined << 1), k % 4))
    rl.sort()
    # ---- MIRV connectors -----------------------------------------------------------------------------------------------------
    mv = []
    for l in launches:
        if l["shape"] != "mirv":
            continue
        s = {l["lineage"]} if l["lineage"] in lane_of else set()
        for w in l["warhead_list"]:
            t = w["target"] if w["kind"] == "lineage" else w.get("lineage")
            if t in lane_of:
                s.add(t)
        if len(s) >= 2:
            mv.append((int(clock.frame(np.array([l["ts_start"]], dtype=np.int64))[0]), nat_index[l["nation"]], sorted(lane_of[x] for x in s)))
    mv.sort(key=lambda r: (r[0], r[2]))
    # ---- ruler ---------------------------------------------------------------------------------------------------------------------
    ticks = _ruler(params, clock)
    # ---- statistics -------------------------------------------------------------------------------------------------------------------
    ever = set(int(i) for i in np.unique(sl_id[sl_id != SLOT_NONE]))
    stats = {"lanes_total": L, "lanes_ever_visible": len(ever), "max_concurrent": int(nvis.max()),
             "mean_visible": round(float(nvis[clock_story_range(clock)].mean()), 3), "max_quiet": int(quiet.max()),
             "slot_overflow": int(overflow), "swaps": swaps, "rails": len(rl), "rails_joined": int(sum(1 for r in rl if r[3] & 2)),
             "mirv_connectors": len(mv), "mirv_lanes_touched_max": max((len(r[2]) for r in mv), default=0),
             "contract_edges_cross": len(edges), "contract_edges_drawn": int(sum(1 for x in edge_f if x >= 0)),
             "paired_lineages": int((bridge_f >= 0).sum()), "commits": int(len(cm_f)), "constellations_with_lanes": ncon,
             "loose_lanes": int(sum(1 for x in lane_con if x < 0)), "ticks": len(ticks["f"]),
             "frames_at_cap": int((nvis >= max_lanes).sum()), "frames_with_lanes": int((nvis > 0).sum())}
    return {"names": names, "L": L, "K": K_SLOTS, "sl_id": sl_id, "sl_x": sl_x, "sl_a": sl_a, "sl_since": sl_since, "quiet": quiet,
            "cm_f": cm_f, "cm_lane": cm_lane, "cm_nat": cm_nat, "cm_code": cm_code, "cm_side": cm_side,
            "bridge_f": bridge_f.astype(np.int32), "rail": rl, "mirv": mv, "edges": [(a, b, edge_f[j]) for j, (a, b, _t) in enumerate(edges) if edge_f[j] >= 0],
            "edge_types": collections.Counter(t for (_a, _b, t) in edges), "ticks": ticks, "stats": stats, "lane_lineage": lins, "lane_con": lane_con}


def clock_story_range(clock):
    a = int(round(clock.intro_s * clock.fps))
    return slice(a, clock.F - int(round(clock.coda_s * clock.fps)))


def _epoch(y, m, d, h=0):
    return calendar.timegm((y, m, d, h, 0, 0))


def _ruler(params, clock):
    """Tick frames: major (year in A, month in B, day in C), minor (quarter, half month, 6 hours), hard (era boundary)."""
    eb = params["era_bounds"]
    pt = lambda s: calendar.timegm(tuple(map(int, s.split("-"))) + (0, 0, 0))
    eA, eB, eC = pt(eb["A"]), pt(eb["B"]), pt(eb["C"])
    end = int(clock.epoch0 * 86400 + clock.end_days * 86400)
    out = {}
    def add(t, level, label):
        if t > end:
            return
        f = int(clock.frame(np.array([t], dtype=np.int64))[0])
        if f not in out or level > out[f][0]:
            out[f] = (level, label)
    import datetime as dt
    for y in range(2011, 2024):
        for m in (1, 4, 7, 10):
            t = _epoch(y, m, 1)
            if eA <= t < eB:
                add(t, 1 if m == 1 else 0, str(y) if m == 1 else "")
    t = eB
    y, m = 2023, 4
    while t < eC:
        add(t, 1, "%d·%02d" % (y, m))
        add(_epoch(y, m, 15), 0, "")
        m += 1
        if m == 13:
            y, m = y + 1, 1
        t = _epoch(y, m, 1)
    t = eC
    while t <= end:
        d = dt.datetime.fromtimestamp(t, dt.UTC)
        add(t, 1, "%02d·%02d" % (d.month, d.day))
        for hh in (6, 12, 18):
            add(t + hh * 3600, 0, "")
        t += 86400
    add(eB, 2, ""); add(eC, 2, "")
    fs = sorted(out)
    return {"f": fs, "level": [out[f][0] for f in fs], "label": [out[f][1] for f in fs]}
