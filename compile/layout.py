"""compile/layout.py: provisional region positions (slice 3). Relations discs when relations.json exists
(constellation discs, primary at the centre, discs packed first-fit along a spiral by earliest first_ts, members by
first_ts); unjoined lineages fall back to single-dot discs packed the same way (STRATEGY 3.3 and section 12.1).
Positions are world units; `fit` maps them to screen pixels for the fixed-world camera.
"""
import math

import numpy as np

GOLDEN = math.pi * (3 - math.sqrt(5))


def _pack(discs, gap=0.6):
    """discs: list of (key, radius); returns {key: (x, y)}; first-fit on an Archimedean spiral, deterministic."""
    placed = []
    out = {}
    for key, r in discs:
        k = 0
        while True:
            ang = 0.55 * k
            rad = 0.18 * ang
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            if all((x - px) ** 2 + (y - py) ** 2 >= (r + pr + gap) ** 2 for px, py, pr in placed):
                break
            k += 1
        placed.append((x, y, r))
        out[key] = (x, y)
    return out


def build(c, region_ids, first_ts, events_count, map_rect=(240, 64, 1360, 896), pad=0.12):
    """region_ids: lineage ids in region order; first_ts: {id: epoch}; returns dict of arrays and group info."""
    members = {}
    prim = {}
    group_of = {}
    rset = set(region_ids)
    if c.relations:
        for n in c.relations["nodes"]:
            lin = n.get("lineage")
            if lin in rset:
                con = n.get("constellation") or (n.get("constellations") or [None])[0]
                if con:
                    group_of[lin] = con
                    if n.get("primary"):
                        prim[con] = lin
    for lin in region_ids:
        if lin in group_of:
            members.setdefault(group_of[lin], []).append(lin)
    discs, local = [], {}
    for con, ms in members.items():
        ms.sort(key=lambda l: (first_ts.get(l, 1 << 60), l))
        p = prim.get(con)
        order = ([p] if p in ms else []) + [m for m in ms if m != p]
        pos = {}
        for i, m in enumerate(order):
            if i == 0 and p in ms:
                pos[m] = (0.0, 0.0)
            else:
                j = i if (p in ms) else i + 1
                rr = 1.05 * math.sqrt(j)
                pos[m] = (rr * math.cos(GOLDEN * j), rr * math.sin(GOLDEN * j))
        R = max(math.hypot(*v) for v in pos.values()) + 0.8
        local[con] = pos
        discs.append((("c", con), R, min(first_ts.get(m, 1 << 60) for m in ms)))
    loose = [l for l in region_ids if l not in group_of]
    for l in loose:
        discs.append((("l", l), 0.7, first_ts.get(l, 1 << 60)))
    discs.sort(key=lambda d: (d[2], str(d[0])))
    centres = _pack([(d[0], d[1]) for d in discs])
    P = {}
    for key, (cx, cy) in centres.items():
        if key[0] == "l":
            P[key[1]] = (cx, cy)
        else:
            for m, (dx, dy) in local[key[1]].items():
                P[m] = (cx + dx, cy + dy)
    xs = np.array([P[l][0] for l in region_ids]); ys = np.array([P[l][1] for l in region_ids])
    x0, y0, w, h = map_rect
    bw, bh = xs.max() - xs.min() + 1e-9, ys.max() - ys.min() + 1e-9
    sc = min(w / bw, h / bh) * (1 - 2 * pad)
    px = x0 + w / 2 + (xs - (xs.max() + xs.min()) / 2) * sc
    py = y0 + h / 2 + (ys - (ys.max() + ys.min()) / 2) * sc
    rad = np.clip(1.8 + 0.9 * np.log10(1 + np.array([events_count.get(l, 0) for l in region_ids], dtype=float)), 1.8, 6.5)
    return {"px": px.astype(np.float32), "py": py.astype(np.float32), "rad": rad.astype(np.float32), "scale": float(sc),
            "constellations": len(members), "joined": len(group_of), "loose": len(loose)}
