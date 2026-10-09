"""compile/layout.py: the world (STRATEGY section 3 with section 12 amendment 1). Pure geometry from the tile table.

Axial pointy-top hex lattice, world unit = hex circumradius: x = sqrt(3)(q + r/2), y = 1.5 r.
 - A region (lineage x host) is a blob of spiral cells; its tiles take consecutive spiral runs in first-touch order,
   oldest at the core (tree rings).
 - Constellation discs (relations.json): members of one constellation on one surface pack into a rigid disc with the
   primary at the centre; discs and loose lineages order by earliest first touch and pack first-fit from the centre of the
   continent outwards; edges pull partners adjacent; a bridged region anchors 0.6 R toward its partner's surface; ruins
   sit on the outer ring.
 - Surfaces: omen-e and omen-c share a 3-hex strait; omen-linux lies across an 8-hex sea; AM4 and FX99 off its coast;
   GitHub is a band of islands in the north sea (rising at created_at); harbours, spurs, notches, beacons, HQ anchors.
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
    # --- per-region tiles in first-touch order (tile ids are already globally ordered) --------------------------------
    reg_tiles = [[] for _ in range(nR)]
    for t in range(nT):
        reg_tiles[T.region[t]].append(t)
    reg_cells = np.array([int(T.cells[ts].sum()) if ts else 0 for ts in reg_tiles], dtype=np.int64)
    first_t_reg = np.array([min([T.first_t[t] for t in ts] or [np.inf]) for ts in reg_tiles])
    # --- relations: constellation of a lineage, primary, pull partners ---------------------------------------------------
    group_of, prim = {}, {}
    pull = {}
    bridges_rel = []
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
            if e["type"] in BRIDGE_TYPES or e["scope"] == "cross-constellation":
                bridges_rel.append((la, lb, e["type"]))
    # --- continents -----------------------------------------------------------------------------------------------------
    host_regions = {h: [i for i, r in enumerate(T.regions) if r[1] == h] for h in HOST_ORDER}
    rpos = np.zeros((nR, 2), dtype=np.int64)  # region seed cell in world lattice coordinates
    cont_cells = {}
    R_est = {h: math.sqrt(max(1, sum(reg_cells[i] for i in host_regions[h])) / 3.0 / 0.6) for h in HOST_ORDER}
    # partner hosts per lineage (for bridged-region anchors)
    lin_hosts = {}
    for i, (L, h, k) in enumerate(T.regions):
        lin_hosts.setdefault(L, []).append(h)
    for h in HOST_ORDER:
        ids = host_regions[h]
        if not ids:
            continue
        pk = Packer(max(120, int(R_est[h] * 2.6)))
        # group into discs
        ruin_ids = [i for i in ids if T.regions[i][2] == "third"]
        live = [i for i in ids if T.regions[i][2] != "third"]
        by_con = {}
        for i in live:
            con = group_of.get(T.regions[i][0])
            by_con.setdefault(con if con else ("loose", i), []).append(i)
        discs = []  # (earliest first_t, key, members)
        for key, ms in by_con.items():
            ms.sort(key=lambda i: (first_t_reg[i], T.regions[i][0]))
            discs.append((min(first_t_reg[i] for i in ms), str(key), key, ms))
        discs.sort(key=lambda d: (d[0], d[1]))
        for (_, _, key, ms) in discs:
            # --- internal layout of the disc (local lattice), primary at the centre -----------------------------------
            if len(ms) == 1:
                fp = blob(int(reg_cells[ms[0]]))
                rel_pos = {ms[0]: (0, 0)}
                disc_fp = fp
            else:
                p = prim.get(key)
                order = [i for i in ms if T.regions[i][0] == p] + [i for i in ms if T.regions[i][0] != p]
                lk = Packer(60)
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
                    q, r = lk.first_fit(fpi, anchor)
                    lk.place(fpi, q, r, gap)
                    rel_pos[i] = (q, r)
                disc_fp = np.concatenate([blob(int(reg_cells[i])) + np.array(rel_pos[i]) for i in order])
            # --- anchor toward the partner surfaces of its bridged members ---------------------------------------------
            vx = vy = 0.0
            for i in ms:
                for h2 in lin_hosts.get(T.regions[i][0], []):
                    if h2 != h and h2 in PARTNER_DIR[h]:
                        d = PARTNER_DIR[h][h2]
                        vx += d[0]; vy += d[1]
            anchor = (0, 0)
            nrm = math.hypot(vx, vy)
            if nrm > 1e-9:
                f = 0.6 * R_est[h]
                ax, ay = vx / nrm * f, vy / nrm * f
                r_ = ay / 1.5
                anchor = (int(round(ax / S3 - r_ / 2.0)), int(round(r_)))
            q, r = pk.first_fit(disc_fp, anchor)
            pk.place(disc_fp, q, r, gap)
            for i in ms:
                rpos[i] = (q + rel_pos[i][0], r + rel_pos[i][1])
        cont_cells[h] = np.concatenate([blob(int(reg_cells[i])) + rpos[i] for i in live])
    # --- arrange continents: strait, sea, coast ----------------------------------------------------------------------------
    shift = {}
    placed_cells = {}

    def cen_of(a):
        return a[:, 0].mean(), a[:, 1].mean()

    def put(h, anchor_of, direction, gap_hex):
        """Overlap continent h on anchor_of's centroid, then slide it along `direction` until `gap_hex` empty hexes remain."""
        a = cont_cells[h]
        c0, c1 = cen_of(a), cen_of(placed_cells[anchor_of])
        target = (int(round(c1[0] - c0[0])), int(round(c1[1] - c0[1])))
        s = slide(a, [placed_cells[k] for k in placed_cells], target, direction, gap_hex)
        shift[h] = s
        placed_cells[h] = a + np.array(s)

    if "omen-e" in cont_cells:
        shift["omen-e"] = (0, 0)
        placed_cells["omen-e"] = cont_cells["omen-e"]
    if "omen-c" in cont_cells and "omen-e" in placed_cells:
        put("omen-c", "omen-e", (1.0, 0.0), 3)
    if "omen-linux" in cont_cells and "omen-c" in placed_cells:
        # across the open sea to the south, nested under the strait between the two Windows surfaces (8 empty hexes)
        a = cont_cells["omen-linux"]
        c0 = cen_of(a)
        ce, cc = cen_of(placed_cells["omen-e"]), cen_of(placed_cells["omen-c"])
        mx = (ce[0] + ce[1] / 2.0 + cc[0] + cc[1] / 2.0) / 2.0  # world x (in q units) of the strait
        far_r = int(max(placed_cells["omen-e"][:, 1].max(), placed_cells["omen-c"][:, 1].max()) + 140)
        tq = int(round(mx - far_r / 2.0 - (c0[0] + (c0[1] - 0) / 2.0 - c0[1] / 2.0)))
        target = (int(round(mx - c0[0] - c0[1] / 2.0 + c0[1] / 2.0 - (far_r - c0[1]) / 2.0)), int(far_r - c0[1]))
        s = slide(a, [placed_cells[k] for k in placed_cells], target, (0.5, -1.0), 8, approach=True)
        shift["omen-linux"] = s
        placed_cells["omen-linux"] = a + np.array(s)
    if "am4" in cont_cells and "omen-linux" in placed_cells:
        put("am4", "omen-linux", (-1.0, 0.0), 6)
    if "fx99" in cont_cells and "am4" in placed_cells:
        put("fx99", "am4", (-1.0, 0.0), 5)
    for i in range(nR):
        h = T.regions[i][1]
        if T.regions[i][2] != "third":
            rpos[i] = rpos[i] + np.array(shift[h])
    # --- ruins on the outer ring of their surface, packed against everything already laid ------------------------------------
    allpk = Packer(420)
    for i in range(nR):
        if T.regions[i][2] != "third":
            allpk.place(blob(int(reg_cells[i])), int(rpos[i][0]), int(rpos[i][1]), gap)
    for h in HOST_ORDER:
        ruin_ids = sorted((i for i in host_regions[h] if T.regions[i][2] == "third"), key=lambda i: (first_t_reg[i], T.regions[i][0]))
        if not ruin_ids or h not in placed_cells:
            continue
        pc = placed_cells[h]
        cq, cr = int(round(pc[:, 0].mean())), int(round(pc[:, 1].mean()))
        rad = int(max(hdist(cq, cr, int(a), int(b)) for a, b in pc[::max(1, len(pc) // 400)])) + 3
        for i in ruin_ids:
            fpi = blob(int(reg_cells[i]))
            ang = sha_unit(T.regions[i][0], h) * 2 * math.pi
            ax, ay = rad * S3 * math.cos(ang), rad * 1.5 * math.sin(ang)
            r_ = ay / 1.5
            aq, ar = cq + int(round(ax / S3 - r_ / 2.0)), cr + int(round(r_))
            q, r = allpk.first_fit(fpi, (aq, ar), min_radius=rad, centre=(cq, cr))
            allpk.place(fpi, q, r, gap)
            rpos[i] = (q, r)
            placed_cells[h] = np.concatenate([placed_cells[h], fpi + np.array([q, r])])
    # --- cells of every tile (world lattice), runs of the region's spiral in first-touch order ------------------------------
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
    # tile order is global (first touch); cells above were written region by region, so index by tile start explicitly
    order_cells_q = np.zeros_like(cell_q)
    order_cells_r = np.zeros_like(cell_r)
    new_start = np.zeros(nT + 1, dtype=np.int64)
    p = 0
    for t in range(nT):
        n = int(T.cells[t])
        a = tile_start[t]
        order_cells_q[p:p + n] = cell_q[a:a + n]
        order_cells_r[p:p + n] = cell_r[a:a + n]
        new_start[t] = p
        p += n
    new_start[nT] = p
    W.cell_q, W.cell_r, W.tile_start = order_cells_q, order_cells_r, new_start
    cx_ = S3 * (order_cells_q + order_cells_r / 2.0)
    cy_ = 1.5 * order_cells_r.astype(np.float64)
    W.cell_x, W.cell_y = cx_, cy_
    tx = np.zeros(nT); ty = np.zeros(nT)
    for t in range(nT):
        a, b = new_start[t], new_start[t + 1]
        tx[t], ty[t] = cx_[a:b].mean(), cy_[a:b].mean()
    W.tile_x, W.tile_y = tx, ty
    W.reg_tiles = reg_tiles
    W.rpos = rpos
    W.reg_x = S3 * (rpos[:, 0] + rpos[:, 1] / 2.0)
    W.reg_y = 1.5 * rpos[:, 1].astype(np.float64)
    W.reg_cells = reg_cells
    W.first_t_reg = first_t_reg
    # region cell sets for coast marching
    reg_set = []
    for i in range(nR):
        a = np.concatenate([np.stack([order_cells_q[new_start[t]:new_start[t + 1]], order_cells_r[new_start[t]:new_start[t + 1]]], 1) for t in reg_tiles[i]]) if reg_tiles[i] else np.zeros((0, 2), dtype=np.int32)
        reg_set.append({(int(x), int(y)) for x, y in a})
    W.reg_set = reg_set
    # --- continents' geometry -----------------------------------------------------------------------------------------------
    W.cont = {}
    for h, a in placed_cells.items():
        x = S3 * (a[:, 0] + a[:, 1] / 2.0)
        y = 1.5 * a[:, 1].astype(np.float64)
        W.cont[h] = {"cx": float(x.mean()), "cy": float(y.mean()), "x0": float(x.min()), "x1": float(x.max()), "y0": float(y.min()),
                     "y1": float(y.max()), "cells": int(len(a)), "r": float(np.sqrt(((x - x.mean()) ** 2 + (y - y.mean()) ** 2).max()))}
    # --- GitHub archipelago -----------------------------------------------------------------------------------------------
    W.islands = []  # dict(lineage, t, x, y, cells[(x, y)...], fork)
    gh = [g for g in c.gh_born]
    top = min(v["y0"] for v in W.cont.values())
    ecx = [W.cont[h]["cx"] for h in ("omen-e", "omen-c") if h in W.cont]
    mid_x = sum(ecx) / len(ecx) if ecx else 0.0
    rows = 4
    per_row = int(math.ceil(len(gh) / rows))
    px_, py_ = 7.5, 6.5  # island pitch in world units
    x_lo = mid_x - px_ * (per_row - 1) / 2.0
    for j, (t, L, kb, fork) in enumerate(gh):
        row, col = divmod(j, per_row)
        ncell = max(1, min(5, 1 + int(math.floor(math.log10(1 + kb)))))
        x = x_lo + col * px_ + (px_ / 2.0 if row % 2 else 0.0)
        y = top - 10.0 - (rows - 1 - row) * py_
        q0, r0 = xy_to_axial(x, y)
        sp = spiral(ncell) + np.array([q0, r0])
        cells = [(float(S3 * (a + b / 2.0)), float(1.5 * b)) for a, b in sp.tolist()]
        W.islands.append({"lineage": L, "t": t, "x": float(S3 * (q0 + r0 / 2.0)), "y": float(1.5 * r0), "cells": cells, "fork": fork, "kb": kb})
    gx = [p[0] for i in W.islands for p in i["cells"]]
    gy = [p[1] for i in W.islands for p in i["cells"]]
    W.cont["github"] = {"cx": sum(gx) / len(gx), "cy": sum(gy) / len(gy), "x0": min(gx) - 1, "x1": max(gx) + 1, "y0": min(gy) - 1, "y1": max(gy) + 1,
                        "cells": sum(len(i["cells"]) for i in W.islands), "r": 0.0}
    # --- anchors: HQ per surface, beacons ------------------------------------------------------------------------------------
    W.anchor = {}
    for h, v in W.cont.items():
        W.anchor[h] = (v["cx"], v["cy"])
    W.anchor["cloud"] = W.anchor.get("omen-c", W.anchor.get("omen-e", (0.0, 0.0)))  # ChatGPT years: into the void where omen-c will rise
    W.beacon = {}
    for h in ("omen-linux", "am4", "fx99"):
        if h in W.cont:
            v = W.cont[h]
            W.beacon[h] = (v["cx"] + 0.45 * v["r"] * 0.7, v["cy"] - 0.45 * v["r"] * 0.7)
    # --- harbours (home region coast toward the island) -------------------------------------------------------------------------
    W.harbours = []
    home = {}
    for L, hs in T.hosts_of.items():
        if hs:
            home[L] = T.reg_index.get((L, hs[0]))
    for j, isl in enumerate(W.islands):
        ri = home.get(isl["lineage"])
        if ri is None or not reg_tiles[ri]:
            continue
        cx, cy = W.reg_x[ri], W.reg_y[ri]
        dx, dy = isl["x"] - cx, isl["y"] - cy
        n = math.hypot(dx, dy) or 1.0
        best, bd = None, -1e18
        for (q, r) in sorted(reg_set[ri]):
            x, y = hxy(q, r)
            d = (x - cx) * dx / n + (y - cy) * dy / n
            if d > bd:
                bd, best = d, (x, y)
        W.harbours.append({"island": j, "region": int(ri), "x": best[0], "y": best[1]})
    # --- bridges: a lineage across surfaces, plus relations edges -----------------------------------------------------------------
    W.bridges = []  # (ra, rb, kind)
    for L, hs in T.hosts_of.items():
        ris = [T.reg_index[(L, h)] for h in hs if (L, h) in T.reg_index]
        for a in range(1, len(ris)):
            W.bridges.append({"a": int(ris[0]), "b": int(ris[a]), "kind": "host"})
    for (la, lb, ty) in bridges_rel:
        ra, rb = home.get(la), home.get(lb)
        if ra is not None and rb is not None and ra != rb:
            W.bridges.append({"a": int(ra), "b": int(rb), "kind": "rel"})
    for b in W.bridges:
        ia, ib = b["a"], b["b"]
        ax, ay, bx, by = W.reg_x[ia], W.reg_y[ia], W.reg_x[ib], W.reg_y[ib]
        n = math.hypot(bx - ax, by - ay) or 1.0
        ux, uy = (bx - ax) / n, (by - ay) / n

        def coast(i, ux, uy):
            cx, cy = W.reg_x[i], W.reg_y[i]
            best, bd = (cx, cy), -1e18
            for (q, r) in sorted(reg_set[i]):
                x, y = hxy(q, r)
                d = (x - cx) * ux + (y - cy) * uy
                if d > bd:
                    bd, best = d, (x, y)
            return best
        b["p0"], b["p1"] = coast(ia, ux, uy), coast(ib, -ux, -uy)
    # --- spurs (worktrees) and notches (branches) ---------------------------------------------------------------------------------
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
            cx, cy = W.reg_x[ri], W.reg_y[ri]
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
    W.bridges_rel = bridges_rel
    W.constellations = len({v for v in group_of.values()})
    W.joined = len(group_of)
    W.bbox = (min(float(cx_.min()), min(v["x0"] for v in W.cont.values())), min(float(cy_.min()), min(v["y0"] for v in W.cont.values())),
              max(float(cx_.max()), max(v["x1"] for v in W.cont.values())), max(float(cy_.max()), max(v["y1"] for v in W.cont.values())))
    return W
