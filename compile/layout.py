"""compile/layout.py: the world (STRATEGY section 3 with section 12 amendment 1). Pure geometry from the tile table.

Axial pointy-top hex lattice, world unit = hex circumradius: x = sqrt(3)(q + r/2), y = 1.5 r.
 - A region (one lineage) is a blob of spiral cells; its tiles take consecutive spiral runs in first-touch order, oldest at the
   core (tree rings).
 - geography `constellations` (iteration 2): the continents are the constellation discs of relations.json (members pack into a
   rigid disc, primary at the centre, intra edges pull partners adjacent) plus one archipelago disc of loose lineages (and the
   ruins when shown). Discs pack first-fit from the world centre in order of earliest first touch with a `geography_gap` sea
   between them. Machines are not land: anchors for the HQ and the seat beacons come from the regions whose first evidenced host
   they are; GitHub repositories are harbour glyphs on their own region's coast (islands are no longer land); bridges are the
   cross-constellation edges only.
Deterministic: no set iteration order, no randomness (positions from sha1 of ids).
"""
import hashlib
import math

import numpy as np

S3 = math.sqrt(3.0)
DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
PULL_TYPES = ("depends_on", "parent", "consumes", "extracted_from", "replaces")
BRIDGE_TYPES = ("bridges_traffic_to", "leases_hardware_to", "control_plane_for", "describes_topology_for")
HOST_ORDER = ("omen-e", "omen-c", "omen-linux", "am4", "fx99")
# unit direction (in world x, y) from a surface toward its partner surface, for anchoring bridged regions
PARTNER_DIR = {
    "omen-e": {"omen-c": (1, 0), "omen-linux": (0.7, 0.7), "am4": (0.3, 0.9), "fx99": (0.3, 0.9)},
    "omen-c": {"omen-e": (-1, 0), "omen-linux": (0, 1), "am4": (-0.3, 0.9), "fx99": (-0.3, 0.9)},
    "omen-linux": {"omen-c": (0, -1), "omen-e": (-0.7, -0.7), "am4": (-1, 0.2), "fx99": (-1, 0.5)},
    "am4": {"omen-linux": (1, 0), "omen-c": (0.4, -0.9), "omen-e": (0, -1), "fx99": (-0.3, 0.9)},
    "fx99": {"omen-linux": (1, -0.3), "omen-c": (0.4, -0.9), "omen-e": (0, -1), "am4": (0.3, -0.9)},
}


def hxy(q, r):
    return S3 * (q + r / 2.0), 1.5 * r


def xy_to_axial(x, y):
    """Cube-rounded axial cell of a world point."""
    r = y / 1.5
    q = x / S3 - r / 2.0
    cx, cz = q, r
    cy = -cx - cz
    rx, ry, rz = round(cx), round(cy), round(cz)
    dx, dy, dz = abs(rx - cx), abs(ry - cy), abs(rz - cz)
    if dx > dy and dx > dz:
        rx = -ry - rz
    elif dy > dz:
        ry = -rx - rz
    else:
        rz = -rx - ry
    return int(rx), int(rz)


def hdist(aq, ar, bq, br):
    dq, dr = aq - bq, ar - br
    return (abs(dq) + abs(dr) + abs(dq + dr)) // 2


def ring(k):
    if k == 0:
        return [(0, 0)]
    out = []
    q, r = DIRS[4][0] * k, DIRS[4][1] * k
    for i in range(6):
        for _ in range(k):
            out.append((q, r))
            q, r = q + DIRS[i][0], r + DIRS[i][1]
    return out


_SPIRAL = []
for _k in range(0, 80):
    _SPIRAL += ring(_k)
SPIRAL = np.array(_SPIRAL, dtype=np.int32)


def spiral(n):
    return SPIRAL[:n]


def sha_unit(s, salt=""):
    return int.from_bytes(hashlib.sha1((salt + s).encode()).digest()[:4], "big") / 4294967296.0


class Packer:
    """Occupancy grid on the lattice. fits() tests a rigid footprint at (q, r); place() marks it dilated by the gap."""

    def __init__(self, rad):
        self.rad = rad
        self.n = 2 * rad + 1
        self.occ = np.zeros((self.n, self.n), dtype=bool)
        self.extent = 0  # max hex distance of any placed cell from the origin

    def fits(self, fp, q, r):
        qi = fp[:, 0] + q + self.rad
        ri = fp[:, 1] + r + self.rad
        if qi.min() < 0 or ri.min() < 0 or qi.max() >= self.n or ri.max() >= self.n:
            return False
        return not self.occ[qi, ri].any()

    def place(self, fp, q, r, gap=1):
        qi = fp[:, 0] + q
        ri = fp[:, 1] + r
        cells = np.stack([qi, ri], axis=1)
        pts = [cells]
        cur = cells
        for _ in range(gap):
            nxt = np.concatenate([cur + np.array(d) for d in DIRS] + [cur])
            nxt = np.unique(nxt, axis=0)
            cur = nxt
        pts = cur
        a = pts[:, 0] + self.rad
        b = pts[:, 1] + self.rad
        ok = (a >= 0) & (b >= 0) & (a < self.n) & (b < self.n)
        self.occ[a[ok], b[ok]] = True
        d = max(int(np.max([hdist(0, 0, int(x), int(y)) for x, y in cells[::max(1, len(cells) // 40)]])), 0)
        self.extent = max(self.extent, d)

    def first_fit(self, fp, anchor=(0, 0), min_radius=0, max_ring=160, centre=(0, 0)):
        aq, ar = anchor
        for k in range(0, max_ring):
            for (dq, dr) in ring(k):
                q, r = aq + dq, ar + dr
                if min_radius and hdist(centre[0], centre[1], q, r) < min_radius:
                    continue
                if self.occ[q + self.rad, r + self.rad] if (abs(q) <= self.rad and abs(r) <= self.rad) else True:
                    continue
                if self.fits(fp, q, r):
                    return q, r
        raise RuntimeError("no room")


def blob(n):
    """Footprint of a region of n cells: the first n spiral cells (compact, round)."""
    return spiral(n)


def boundary(cells):
    """Subset of an (n, 2) cell array having a lattice neighbour outside the set."""
    s = {(int(a), int(b)) for a, b in cells}
    keep = [i for i, (a, b) in enumerate(cells.tolist()) if any((a + dq, b + dr) not in s for dq, dr in DIRS)]
    return cells[keep]


def min_dist(A, B):
    """Minimum hex distance between two cell sets (boundary subsets, numpy pairwise)."""
    best = 1 << 30
    for i in range(0, len(A), 512):
        a = A[i:i + 512]
        dq = a[:, None, 0] - B[None, :, 0]
        dr = a[:, None, 1] - B[None, :, 1]
        d = (np.abs(dq) + np.abs(dr) + np.abs(dq + dr)) // 2
        best = min(best, int(d.min()))
    return best


def slide(shape, others, target, direction, gap, approach=False):
    """Translate `shape` (n,2) so its boundary sits `gap` empty hexes from `others` (list of (m,2)).
    approach=False: start at `target` (overlapping) and move along `direction` (lattice steps per unit t) until clear.
    approach=True: start far away at `target` and move along `direction` until the shape would touch; stop one step short.
    Returns (dq, dr)."""
    sb = boundary(shape)
    ob = np.concatenate([boundary(o) for o in others]) if others else np.zeros((0, 2), dtype=np.int64)
    dq0, dr0 = target

    def pos(t):
        return dq0 + int(round(direction[0] * t)), dr0 + int(round(direction[1] * t))

    def clear(t):
        pq, pr = pos(t)
        return min_dist(sb + np.array([pq, pr]), ob) >= gap + 1

    lo, hi = 0, 800
    if not approach:
        while lo < hi:  # smallest t (closest) that is clear
            mid = (lo + hi) // 2
            if clear(mid):
                hi = mid
            else:
                lo = mid + 1
        return pos(lo)
    t = 0
    while t < 800 and clear(t + 6):  # coarse march toward the others, then refine the last clear step
        t += 6
    while clear(t + 1) and t < 800:
        t += 1
    return pos(t)


def build(T, c, params):
    """T: tiles.Tiles. Returns the World (arrays, per-region/tile geometry, features)."""
    W = type("World", (), {})()
    nT, nR = len(T.path), len(T.regions)
    gap = int(params["coast_gap"])
    dgap = int(params.get("geography_gap", 2))
    reg_tiles = [[] for _ in range(nR)]
    for t in range(nT):
        reg_tiles[T.region[t]].append(t)
    reg_cells = np.array([int(T.cells[ts].sum()) if ts else 0 for ts in reg_tiles], dtype=np.int64)
    first_t_reg = np.array([min([T.first_t[t] for t in ts] or [np.inf]) for ts in reg_tiles])
    group_of, prim, pull, cross = {}, {}, {}, []
    rel = c.relations
    if rel:
        node = {n["name"]: n for n in rel["nodes"]}
        for n in rel["nodes"]:
            lin = n.get("lineage")
            con = n.get("constellation") or ((n.get("constellations") or [None])[0])
            if lin and con:
                group_of[lin] = con
                if n.get("primary"):
                    prim[con] = lin
        for e in rel["edges"]:
            a, b = node.get(e["src"]), node.get(e["dst"])
            la, lb = (a or {}).get("lineage"), (b or {}).get("lineage")
            if not la or not lb or la == lb:
                continue
            if e["type"] in PULL_TYPES and e["scope"] == "intra":
                pull.setdefault(la, []).append(lb)
                pull.setdefault(lb, []).append(la)
            if e["scope"] == "cross-constellation":
                cross.append((la, lb, e["type"], group_of.get(la)))
    # --- discs: constellations plus one archipelago -------------------------------------------------------------------------
    by_con = {}
    for i in range(nR):
        if not reg_tiles[i]:
            continue
        by_con.setdefault(group_of.get(T.regions[i][0]) if T.regions[i][2] != "third" else None, []).append(i)
    discs = []
    for key, ms in by_con.items():
        ms.sort(key=lambda i: (first_t_reg[i], T.regions[i][0]))
        discs.append((min(first_t_reg[i] for i in ms), str(key), key, ms))
    discs.sort(key=lambda d: (d[0], d[1]))
    tot_all = int(reg_cells.sum())
    pk = Packer(int(2.0 * math.sqrt(tot_all)) + 90)
    rpos = np.zeros((nR, 2), dtype=np.int64)
    W.con_names, W.reg_con, W.con_members = [], np.full(nR, 255, dtype=np.int64), []
    disc_cells = []
    for (_, _, key, ms) in discs:
        tot = int(sum(reg_cells[i] for i in ms))
        rad = int(2.2 * math.sqrt(tot)) + 24
        if len(ms) == 1:
            rel_pos = {ms[0]: (0, 0)}
            order = ms
        else:
            p = prim.get(key)
            order = [i for i in ms if T.regions[i][0] == p] + [i for i in ms if T.regions[i][0] != p]
            lk = Packer(rad)
            rel_pos = {}
            for j, i in enumerate(order):
                fpi = blob(int(reg_cells[i]))
                anchor = (0, 0)
                L = T.regions[i][0]
                for pl in pull.get(L, []):
                    for i2 in order[:j]:
                        if T.regions[i2][0] == pl:
                            anchor = rel_pos[i2]
                            break
                    else:
                        continue
                    break
                q, r = lk.first_fit(fpi, anchor, max_ring=rad)
                lk.place(fpi, q, r, gap)
                rel_pos[i] = (q, r)
        disc_fp = np.concatenate([blob(int(reg_cells[i])) + np.array(rel_pos[i]) for i in order])
        q, r = pk.first_fit(disc_fp, (0, 0), max_ring=pk.rad - 2)
        pk.place(disc_fp, q, r, dgap)
        for i in ms:
            rpos[i] = (q + rel_pos[i][0], r + rel_pos[i][1])
        if key is not None:
            cid = len(W.con_names); W.con_names.append(key)
        else:
            cid = 255
        for i in ms:
            W.reg_con[i] = cid
        W.con_members.append((cid, list(ms)))
        disc_cells.append(disc_fp + np.array([q, r]))
    # --- cells of every tile (world lattice) ------------------------------------------------------------------------------------
    cell_q = np.zeros(int(T.cells.sum()), dtype=np.int32)
    cell_r = np.zeros_like(cell_q)
    tile_start = np.zeros(nT + 1, dtype=np.int64)
    k = 0
    for i, ts in enumerate(reg_tiles):
        sp = blob(int(reg_cells[i])) + rpos[i]
        off = 0
        for t in ts:
            n = int(T.cells[t])
            tile_start[t] = k
            cell_q[k:k + n] = sp[off:off + n, 0]
            cell_r[k:k + n] = sp[off:off + n, 1]
            off += n
            k += n
    oq = np.zeros_like(cell_q); orr = np.zeros_like(cell_r)
    new_start = np.zeros(nT + 1, dtype=np.int64)
    p = 0
    for t in range(nT):
        n = int(T.cells[t]); a = tile_start[t]
        oq[p:p + n] = cell_q[a:a + n]; orr[p:p + n] = cell_r[a:a + n]
        new_start[t] = p; p += n
    new_start[nT] = p
    W.cell_q, W.cell_r, W.tile_start = oq, orr, new_start
    cx_ = S3 * (oq + orr / 2.0)
    cy_ = 1.5 * orr.astype(np.float64)
    W.cell_x, W.cell_y = cx_, cy_
    tx = np.zeros(nT); ty = np.zeros(nT)
    for t in range(nT):
        a, b = new_start[t], new_start[t + 1]
        tx[t], ty[t] = cx_[a:b].mean(), cy_[a:b].mean()
    W.tile_x, W.tile_y = tx, ty
    W.reg_tiles, W.rpos, W.reg_cells, W.first_t_reg = reg_tiles, rpos, reg_cells, first_t_reg
    W.reg_x = S3 * (rpos[:, 0] + rpos[:, 1] / 2.0)
    W.reg_y = 1.5 * rpos[:, 1].astype(np.float64)
    reg_set, reg_cxy = [], np.zeros((nR, 2))
    for i in range(nR):
        if reg_tiles[i]:
            a = np.concatenate([np.stack([oq[new_start[t]:new_start[t + 1]], orr[new_start[t]:new_start[t + 1]]], 1) for t in reg_tiles[i]])
            reg_cxy[i] = (cx_[new_start[reg_tiles[i][0]]:new_start[reg_tiles[i][-1] + 1]].mean(), 0)
        else:
            a = np.zeros((0, 2), dtype=np.int32)
        reg_set.append({(int(x), int(y)) for x, y in a})
        if len(a):
            reg_cxy[i] = (float((S3 * (a[:, 0] + a[:, 1] / 2.0)).mean()), float((1.5 * a[:, 1]).mean()))
    W.reg_set = reg_set
    # --- constellation discs' geometry ---------------------------------------------------------------------------------------------
    W.cont = {}
    for (cid, ms), a in zip(W.con_members, disc_cells):
        x = S3 * (a[:, 0] + a[:, 1] / 2.0); y = 1.5 * a[:, 1].astype(np.float64)
        W.cont["arch" if cid == 255 else "c%02d" % cid] = {"cx": float(x.mean()), "cy": float(y.mean()), "x0": float(x.min()), "x1": float(x.max()), "y0": float(y.min()),
                                                           "y1": float(y.max()), "cells": int(len(a)), "r": float(np.sqrt(((x - x.mean()) ** 2 + (y - y.mean()) ** 2).max()))}
    # --- anchors: the first land, and the regions whose first evidenced host is h --------------------------------------------------------
    W.anchor = {"cloud": (W.cont[sorted(W.cont)[0]]["cx"], W.cont[sorted(W.cont)[0]]["cy"]) if False else None}
    first_disc = W.con_members[0][1]
    W.anchor["cloud"] = (float(reg_cxy[first_disc[0]][0]), float(reg_cxy[first_disc[0]][1]))
    wcx, wcy = float(cx_.mean()), float(cy_.mean())
    wr = float(np.sqrt(((cx_ - wcx) ** 2 + (cy_ - wcy) ** 2).max()))
    W.beacon = {}
    for h in HOST_ORDER:
        ids = [i for i in range(nR) if T.regions[i][1] == h and T.regions[i][2] != "third" and reg_tiles[i]]
        if ids:
            w_ = np.array([reg_cells[i] for i in ids], dtype=np.float64)
            W.anchor[h] = (float((reg_cxy[ids, 0] * w_).sum() / w_.sum()), float((reg_cxy[ids, 1] * w_).sum() / w_.sum()))
        else:
            ang = sha_unit(h) * 2 * math.pi
            W.anchor[h] = (wcx + 0.35 * wr * math.cos(ang), wcy + 0.35 * wr * math.sin(ang))
    for h in ("omen-linux", "am4", "fx99"):
        W.beacon[h] = (W.anchor[h][0] + 4.0, W.anchor[h][1] - 4.0)
    # --- harbours: a coast glyph on the lineage's own region -------------------------------------------------------------------------
    home = {}
    for L, hs in T.hosts_of.items():
        if hs and (L, hs[0]) in T.reg_index:
            home[L] = T.reg_index[(L, hs[0])]
    W.islands, W.harbours = [], []
    nth = {}
    for j, (t, L, kb, fork) in enumerate(c.gh_born):
        ri = home.get(L)
        if ri is not None and (not reg_tiles[ri] or T.regions[ri][2] == "third"):
            ri = None
        isl = {"lineage": L, "t": t, "x": None, "y": None, "cells": [], "fork": fork, "kb": kb, "region": ri}
        W.islands.append(isl)
        if ri is None:
            continue
        n = nth.get(ri, 0); nth[ri] = n + 1
        ang = (sha_unit(str(L), "h") + 0.37 * n) * 2 * math.pi
        ux, uy = math.cos(ang), math.sin(ang)
        a0, a1 = new_start[reg_tiles[ri][0]], new_start[reg_tiles[ri][-1] + 1]
        # cells of this region in tile order: farthest in the direction, whichever tile it belongs to
        best, bd = None, -1e18
        for t_ in reg_tiles[ri]:
            for ci in range(new_start[t_], new_start[t_ + 1]):
                d = (cx_[ci] - reg_cxy[ri][0]) * ux + (cy_[ci] - reg_cxy[ri][1]) * uy
                if d > bd:
                    bd, best = d, (ci, t_)
        ci, t_ = best
        isl["x"], isl["y"] = float(cx_[ci]), float(cy_[ci])
        W.harbours.append({"island": j, "region": int(ri), "tile": int(t_), "x": float(cx_[ci]), "y": float(cy_[ci]), "dx": ux, "dy": uy})
    # --- bridges: cross-constellation edges only ------------------------------------------------------------------------------------
    W.bridges = []
    seen = set()
    for (la, lb, ty, con) in cross:
        ra, rb = home.get(la), home.get(lb)
        if ra is None or rb is None or ra == rb or (min(ra, rb), max(ra, rb)) in seen or not reg_tiles[ra] or not reg_tiles[rb]:
            continue
        seen.add((min(ra, rb), max(ra, rb)))
        W.bridges.append({"a": int(ra), "b": int(rb), "kind": "rel", "type": ty, "con": con})
    for b in W.bridges:
        ia, ib = b["a"], b["b"]
        ax, ay, bx, by = reg_cxy[ia][0], reg_cxy[ia][1], reg_cxy[ib][0], reg_cxy[ib][1]
        n = math.hypot(bx - ax, by - ay) or 1.0
        ux, uy = (bx - ax) / n, (by - ay) / n

        def coast(i, ux, uy):
            cx, cy = reg_cxy[i]
            best, bd = (cx, cy), -1e18
            for (q, r) in sorted(reg_set[i]):
                x, y = hxy(q, r)
                d = (x - cx) * ux + (y - cy) * uy
                if d > bd:
                    bd, best = d, (x, y)
            return best
        b["p0"], b["p1"] = coast(ia, ux, uy), coast(ib, -ux, -uy)
    # --- spurs (worktrees) and notches (branches) -------------------------------------------------------------------------------------
    W.spurs, W.notches = [], []
    for L, bl in sorted(c.births.items()):
        hs = T.hosts_of.get(L)
        if not hs:
            continue
        ct = c.commits.get(L, [])
        for (t, kind, ref, host, path) in bl:
            h = host if host in hs else hs[0]
            ri = T.reg_index.get((L, h))
            if ri is None or not reg_tiles[ri]:
                continue
            a = sha_unit(ref, kind) * 2 * math.pi
            ux, uy = math.cos(a), math.sin(a)
            cx, cy = reg_cxy[ri]
            s = reg_set[ri]
            d = 0.0
            while d < 400:
                q, r = xy_to_axial(cx + ux * (d + 0.5), cy + uy * (d + 0.5))
                if (q, r) not in s:
                    break
                d += 0.5
            bx, by = cx + ux * d, cy + uy * d
            if kind == "worktree":
                n = sum(1 for x in ct if t <= x[0] <= t + 86400)
                ln = (2 + math.log2(1 + n)) * S3
                W.spurs.append({"region": int(ri), "t": t, "x0": bx, "y0": by, "x1": bx + ux * ln, "y1": by + uy * ln, "ref": ref, "lineage": L, "commits": n})
            else:
                W.notches.append({"region": int(ri), "t": t, "x": bx, "y": by, "ux": ux, "uy": uy})
    W.bridges_rel = cross
    W.constellations = len(W.con_names)
    W.joined = len(group_of)
    W.bbox = (float(cx_.min()) - 1, float(cy_.min()) - 1, float(cx_.max()) + 1, float(cy_.max()) + 1)
    return W
