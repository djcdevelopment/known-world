"""compile/camera.py: camera.f32 (STRATEGY 4.4). Per frame: centre x, y (world units) and scale s (px per world unit =
hex circumradius in px). fit_known steers by the warm, weighty known world (DIRECTION 'What steers the camera'): tiles whose
activity inside the memory window (camera_memory_days, 365 in eras A and B, 120 in C) reaches camera_tile_weight_min (or one
births burst), every launch target (same window), the seat beacons from their first offload, and the HQ and the islands once
the span passes camera_items_min_span. A lone file renders and counts but does not steer. Older doc follows. fit_known: the box of tiles revealed by f + lookahead (plus risen islands and the HQ), scale
min(Wv/bw, Hv/bh)(1 - 2 pad) capped at max_hex_px; from era C scale only decreases; a forward-backward exponential
smoother on centre and log-scale (zero phase: the camera moves before the reveal), clamped so that every tile revealed
at frame f is inside the view. The coda frames the whole world. fixed_world is the control arm.
"""
import math

import numpy as np

LAST_BOX = None   # (F, 4) the known land's box per frame (warm land, launch targets, and what joined), for the centring receipt



def safe_area(params):
    """The frame minus the HUD plates' insets (x, y, w, h). The map owns the whole frame and runs under the plates; the
    camera fits the known world into this rectangle. Derived from the frame size, so a portrait frame needs no new maths."""
    W, H = int(params["frame_w"]), int(params["frame_h"])
    if params.get("layout") == "ia":   # information architecture: ticker strip on top, timeline zone below, nation panel at the right
        return (0, int(params["ia_ticker_h"]), W - int(params["ia_nation_w"]), H - int(params["ia_ticker_h"]) - int(params["ia_timeline_h"]))
    right = int(params["hud_right"]) + (int(params["stream_col_w"]) if params["stream"] == "on" else 0)
    l, t, b = int(params["hud_left"]), int(params["hud_top"]), int(params["hud_bottom"])
    return (l, t, W - l - right, H - t - b)


def centre(params):
    v = safe_area(params)
    return (v[0] + v[2] / 2.0, v[1] + v[3] / 2.0)


def warm_intervals(tT, tI, tW, tB, nT, win_days, thr, t_lo, t_hi):
    """Per tile, the time intervals [a, b) (epoch seconds) in which the weight of touches inside the trailing window of
    win_days reaches thr (a births burst counts as thr on its own), restricted to evaluation times in [t_lo, t_hi).
    Event sweep: each touch adds its weight at t and removes it at t + window. Returns (tile, a, b) arrays."""
    w = np.where(tB, np.maximum(tW, thr), tW)
    win = int(round(win_days * 86400))
    ev_t = np.concatenate([tT, tT + win])
    ev_tile = np.concatenate([tI, tI])
    ev_w = np.concatenate([w, -w])
    cn = np.where(tB, 3.0, 1.0)   # a tile needs three touches' worth: one record, however heavy, is a lone file unless it is a births burst
    ev_c = np.concatenate([cn, -cn])
    ev_kind = np.concatenate([np.zeros(len(tT), dtype=np.int8), np.ones(len(tT), dtype=np.int8)])  # adds before removals at one instant
    o = np.lexsort((np.arange(len(ev_t)), ev_kind, ev_t, ev_tile))
    ev_t, ev_tile, ev_w, ev_c = ev_t[o], ev_tile[o], ev_w[o], ev_c[o]
    cs = np.cumsum(ev_w)
    cc = np.cumsum(ev_c)
    start = np.r_[True, ev_tile[1:] != ev_tile[:-1]]
    base = np.where(start, cs - ev_w, 0.0)
    base = np.maximum.accumulate(np.where(start, np.arange(len(cs)), 0))  # index of the group start
    off = (cs - ev_w)[base]
    S = cs - off
    C = cc - (cc - ev_c)[base]
    warm = (S >= thr - 1e-9) & (C >= 3 - 1e-9)
    prev = np.r_[False, warm[:-1]] & ~start
    up = warm & ~prev
    last = np.r_[ev_tile[1:] != ev_tile[:-1], True]
    dn = (~warm & prev)
    ia, ib = np.nonzero(up)[0], np.nonzero(dn | (warm & last))[0]
    assert len(ia) == len(ib)
    a, b = ev_t[ia], np.where(warm[ib], ev_t[ib] + 1, ev_t[ib])
    a, b = np.maximum(a, t_lo), np.minimum(b, t_hi)
    keep = b > a
    return ev_tile[ia][keep], a[keep], b[keep]


class BoxSet:
    """Boxes with activity intervals [f0, f1) in frames; the union box of those active at each frame (sticky: a frame with
    nothing active keeps the last box, and before any box the fallback)."""

    def __init__(self, F):
        self.F = F
        self.f0, self.f1, self.b = [], [], []

    def add(self, f0, f1, box):
        self.f0.append(f0); self.f1.append(f1); self.b.append(box)

    def union_by_frame(self, fallback):
        F = self.F
        f0 = np.asarray(self.f0, dtype=np.int64); f1 = np.asarray(self.f1, dtype=np.int64)
        b = np.asarray(self.b, dtype=np.float64).reshape(-1, 4)
        keep = (f1 > f0) & (f0 < F)
        f0, f1, b = f0[keep], np.minimum(f1[keep], F), b[keep]
        out = np.zeros((F, 4))
        n = len(f0)
        starts = np.argsort(f0, kind="stable")
        ends = np.argsort(f1, kind="stable")
        evf = np.unique(np.concatenate([f0, f1[f1 < F], [0]]))
        active = np.zeros(n, dtype=bool)
        si = ei = 0
        cur = np.array(fallback, dtype=np.float64)
        evl = evf.tolist()
        nxt = 0
        for k, e in enumerate(evl):
            while ei < n and f1[ends[ei]] <= e:
                active[ends[ei]] = False; ei += 1
            while si < n and f0[starts[si]] <= e:
                j = starts[si]
                if f1[j] > e:
                    active[j] = True
                si += 1
            if active.any():
                bb = b[active]
                cur = np.array([bb[:, 0].min(), bb[:, 1].min(), bb[:, 2].max(), bb[:, 3].max()])
            end = evl[k + 1] if k + 1 < len(evl) else F
            out[e:end] = cur
        return out


def _fb(x, alpha):
    """Forward then backward first-order filter: zero phase, two-sided exponential kernel."""
    y = np.empty_like(x)
    a = x[0]
    for i in range(len(x)):
        a += alpha * (x[i] - a)
        y[i] = a
    a = y[-1]
    for i in range(len(x) - 1, -1, -1):
        a += alpha * (y[i] - a)
        y[i] = a
    return y


def _hann(x, half):
    """Finite-support zero-phase smoothing (Hann window of 2 * half + 1 samples, edges held): no influence from further than `half`
    samples away, so a centre that has not changed for 2 * half samples is reproduced exactly."""
    half = max(1, int(half))
    k = np.hanning(2 * half + 3)[1:-1]
    k = k / k.sum()
    xp = np.concatenate([np.full(half, x[0]), x, np.full(half, x[-1])])
    return np.convolve(xp, k, mode="valid")


def steering(params, clock, tfirst, tbox, tmask, touches, launch_pts, beacons, F):
    """The warm boxes: (F, 4) union box per frame of the steering tiles, launch targets and seat beacons, plus a report."""
    T, TI, TW, TB = touches
    nT = len(tfirst)
    thr = float(params["camera_tile_weight_min"])
    mem = params["camera_memory_days"]
    c_epoch = int(round((clock.epoch0 + clock.bounds_days[1]) * 86400))
    lo_big, hi_big = -(1 << 60), 1 << 60
    ok = np.ones(len(T), dtype=bool) if tmask is None else tmask[TI]
    T, TI, TW, TB = T[ok], TI[ok], TW[ok], TB[ok]
    bs = BoxSet(F)
    n_tile_iv = 0
    for win, a, b in ((float(mem["A"]), lo_big, c_epoch), (float(mem["C"]), c_epoch, hi_big)):
        tile, ta, tb = warm_intervals(T, TI, TW, TB, nT, win, thr, a, b)
        fa, fb = clock.frame(ta), clock.frame(tb + 0)
        for k in range(len(tile)):
            t = int(tile[k])
            f0 = max(int(fa[k]), int(tfirst[t]))
            if tb[k] >= hi_big or tb[k] > 4e9:
                fb[k] = F
            bs.add(f0, int(fb[k]), tbox[t])
        n_tile_iv += len(tile)
    # launch targets: warm for the memory window of the era they fall in
    pad = 2.0
    lmin = int(params["camera_launch_min_band"])
    for (f, x, y, t_ep, band) in (launch_pts if params["camera_launch_steer"] == "all" else ()):
        if band < lmin:
            continue
        win = float(mem["C"] if t_ep >= c_epoch else mem["A"])
        f1 = int(clock.frame(np.array([t_ep + int(win * 86400)]))[0]) if t_ep + win * 86400 < 4e9 else F
        bs.add(int(f), min(f1, F), (x - pad, y - pad, x + pad, y + pad))
    for (f, x, y) in beacons:
        bs.add(int(f), F, (x - 2.0, y - 2.0, x + 2.0, y + 2.0))
    first = np.nonzero(tfirst < F)[0]
    first = first[np.argmin(tfirst[first])] if len(first) else 0
    fallback = tbox[int(first)]
    return bs.union_by_frame(fallback), {"tile_intervals": int(n_tile_iv), "launch_targets": len(launch_pts), "beacons": len(beacons)}


def build(params, clock, tfirst, tbox, items, hq_xy, world_bbox, coda_f, F, tmask=None, touches=None, launch_pts=(), beacons=(), report=None):
    """tfirst: (nT,) first frame per tile (F = never). tbox: (nT, 4) x0, y0, x1, y1 of each tile's cells (half hex margin
    included). items: list of (frame, x0, y0, x1, y1) extra revealed things (islands, harbours). hq_xy: (F, 2).
    touches: (epoch, tile, weight, burst) arrays of every touch (the steering weight). Returns float32 (F, 3)."""
    fps = clock.fps
    VIEW = safe_area(params)
    Wv, Hv = VIEW[2], VIEW[3]
    fill = float(params["camera_start_fill"])
    pad = params["camera_pad"]
    smax = float(params["max_hex_px"])
    look = int(round(params["camera_lookahead_s"] * fps))
    mode = params["camera"]
    ww = world_bbox
    s_world = min(Wv / (ww[2] - ww[0]), Hv / (ww[3] - ww[1])) * (1 - 2 * pad)
    cx_w, cy_w = (ww[0] + ww[2]) / 2.0, (ww[1] + ww[3]) / 2.0
    if mode == "fixed_world":
        out = np.zeros((F, 3), dtype=np.float32)
        out[:, 0], out[:, 1], out[:, 2] = cx_w, cy_w, s_world
        return out, np.tile(np.array([[ww[2] - ww[0], ww[3] - ww[1]]], dtype=np.float32), (F, 1))
    # The steering box per frame (warm tiles, launch targets, beacons). The islands and the HQ join the fit only once the steering
    # span reaches camera_items_min_span world units, so the start is tight on the first region (DIRECTION 'Start tight').
    sel = (tfirst < F) if tmask is None else ((tfirst < F) & tmask)  # ruins stay out of the box unless camera_ruins_in_box
    if touches is not None and params["camera_steer"] == "warm":
        steer, rep = steering(params, clock, tfirst, tbox, sel, touches, launch_pts, beacons, F)
        if report is not None:
            report.update(rep)
    else:  # control arm 'revealed': every tile ever revealed steers (LAP-12)
        fr = tfirst[sel]; bx = tbox[sel]
        o = np.argsort(fr, kind="stable"); fr, bx = fr[o], bx[o]
        cm = np.stack([np.minimum.accumulate(bx[:, 0]), np.minimum.accumulate(bx[:, 1]), np.maximum.accumulate(bx[:, 2]), np.maximum.accumulate(bx[:, 3])], 1)
        k = np.clip(np.searchsorted(fr, np.arange(F), side="right") - 1, 0, None)
        steer = cm[k]
    ifr, icum = None, None
    if len(items):
        arr = np.array([[i[1], i[2], i[3], i[4]] for i in items], dtype=np.float64)
        frs = np.array([i[0] for i in items], dtype=np.int64)
        o = np.argsort(frs, kind="stable"); frs, arr = frs[o], arr[o]
        ifr = frs
        icum = (np.minimum.accumulate(arr[:, 0]), np.minimum.accumulate(arr[:, 1]), np.maximum.accumulate(arr[:, 2]), np.maximum.accumulate(arr[:, 3]))

    def at_items(f):
        if ifr is None:
            return None
        k = int(np.searchsorted(ifr, f, side="right")) - 1
        return None if k < 0 else (icum[0][k], icum[1][k], icum[2][k], icum[3][k])

    def union(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))

    span_thr = float(params["camera_items_min_span"])
    hx, hy = hq_xy[:, 0], hq_xy[:, 1]
    # The HQ (and with it the cloud anchor the ChatGPT ring broadcasts from) steers only from era C, or from the first launch that lands
    # within camera_hq_launch_units world units of it (coordinator 2026-10-09): in eras A and B the box is warm tiles and launch targets.
    era_f = clock.era_frames()
    hq_join = int(np.argmax(era_f == 2)) if (era_f == 2).any() else F
    for (lf, lx_, ly_, _t, _b) in launch_pts:
        if lf < hq_join and math.hypot(lx_ - hx[lf], ly_ - hy[lf]) <= float(params["camera_hq_launch_units"]):
            hq_join = int(lf)
    if report is not None:
        report["hq_join_frame"] = hq_join
    hxm = np.where(np.arange(F) >= hq_join, hx, np.nan); hym = np.where(np.arange(F) >= hq_join, hy, np.nan)
    hqx0, hqx1 = np.fmin.accumulate(np.nan_to_num(hxm, nan=1e18)), np.fmax.accumulate(np.nan_to_num(hxm, nan=-1e18))
    hqy0, hqy1 = np.fmin.accumulate(np.nan_to_num(hym, nan=1e18)), np.fmax.accumulate(np.nan_to_num(hym, nan=-1e18))
    tgt = np.zeros((F, 3))
    bdim = np.zeros((F, 2))  # box width and height the fit was made for (floors included): the page refits other safe areas from it
    contain = np.zeros(F)
    bxs = np.zeros((F, 4))
    joined = False
    fend = float(params["camera_end_fill"])
    centred = params.get("layout") == "ia"
    # first and final spans of the steering box (including the join), for the fill ramp
    st_span = np.maximum(steer[:, 2] - steer[:, 0], steer[:, 3] - steer[:, 1])
    span0, spanF = max(st_span[0], 6.0), max(st_span.max(), 6.0)
    for f in range(F):
        fl = min(F - 1, f + look)
        bt = tuple(steer[fl])
        if not joined and max(bt[2] - bt[0], bt[3] - bt[1]) >= span_thr:
            joined = True
        b = bt
        if joined:
            b = union(b, at_items(fl))
            if fl >= hq_join:
                b = union(b, (hqx0[fl], hqy0[fl], hqx1[fl], hqy1[fl]))
        x0, y0, x1, y1 = b
        bw, bh = max(x1 - x0, 6.0), max(y1 - y0, 4.0)
        u = min(1.0, max(0.0, math.log(max(bw, bh) / span0) / math.log(max(spanF / span0, 1.0001))))  # growth of the world since the first region
        s = min(Wv / bw, Hv / bh) * (fill + (fend - fill) * u)  # tight at the start (fill), roomier as the world grows (fend)
        tgt[f] = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, min(s, smax))
        bdim[f] = (bw, bh)
        b0 = tuple(steer[f])
        if joined:
            b0 = union(b0, at_items(f))
            if f >= hq_join:
                b0 = union(b0, (hx[f] - 2, hy[f] - 2, hx[f] + 2, hy[f] + 2))
        a0, a1, a2, a3 = b0
        if centred:   # information architecture: the scale looks ahead, the centre does not: the known land stays centred while the view eases out
            tgt[f, 0], tgt[f, 1] = (a0 + a2) / 2.0, (a1 + a3) / 2.0
        bxs[f] = (a0, a1, a2, a3)
        contain[f] = min(Wv / max(a2 - a0, 1e-6), Hv / max(a3 - a1, 1e-6)) * 0.97
    ls = np.log(tgt[:, 2])
    era = clock.era_frames()
    c0 = int(np.argmax(era == 2)) if (era == 2).any() else F
    if not params["zoom_in_allowed"]:
        ls = np.minimum.accumulate(ls)  # pull back only, from the first frame: the growth of scale is experienced as zoom
    alpha = 1.0 - math.exp(-1.0 / (params["camera_tau_s"] * fps))
    if centred:   # the centre follows the known land's box through a finite window: exactly centred whenever the box is steady
        hw_f = float(params["camera_centre_halfwidth_s"]) * fps
        cxs, cys, lss = _hann(tgt[:, 0], hw_f), _hann(tgt[:, 1], hw_f), _fb(ls, alpha)
    else:
        cxs, cys, lss = _fb(tgt[:, 0], alpha), _fb(tgt[:, 1], alpha), _fb(ls, alpha)
    lss = np.minimum(lss, np.log(smax))
    lss = np.minimum(lss, np.log(contain))
    if not params["zoom_in_allowed"]:
        lss = np.minimum.accumulate(lss)
    s = np.exp(lss)
    hw, hh = Wv / (2 * s), Hv / (2 * s)
    cxs = np.clip(cxs, bxs[:, 2] - hw, bxs[:, 0] + hw) if True else cxs
    cys = np.clip(cys, bxs[:, 3] - hh, bxs[:, 1] + hh)
    # when the box is wider than the view the clip bounds invert; keep the smoothed centre then
    bad = (bxs[:, 2] - hw) > (bxs[:, 0] + hw)
    cxs = np.where(bad, (bxs[:, 0] + bxs[:, 2]) / 2, cxs)
    bad = (bxs[:, 3] - hh) > (bxs[:, 1] + hh)
    cys = np.where(bad, (bxs[:, 1] + bxs[:, 3]) / 2, cys)
    out = np.stack([cxs, cys, s], axis=1)
    global LAST_BOX
    LAST_BOX = bxs.copy()
    # box dimensions follow the scale: pulled back only (running max), smoothed like the log-scale
    bdim = np.maximum.accumulate(bdim, axis=0)
    bdim = np.exp(np.stack([_fb(np.log(bdim[:, 0]), alpha), _fb(np.log(bdim[:, 1]), alpha)], axis=1))
    bdim = np.maximum.accumulate(bdim, axis=0)
    # coda: after the decay (3 s) pull to the whole world over 4 s (smoothstep on log-scale and centre)
    if coda_f is not None:
        clen = F - coda_f
        a = coda_f + int(round(clen * 3 / 18))
        n = int(round(clen * 4 / 18))
        base = out[min(a, F - 1)].copy()
        for f in range(a, F):
            u = min(1.0, (f - a) / max(1, n))
            e = u * u * (3 - 2 * u)
            out[f, 0] = base[0] + (cx_w - base[0]) * e
            out[f, 1] = base[1] + (cy_w - base[1]) * e
            out[f, 2] = math.exp(math.log(base[2]) + (math.log(min(s_world, base[2])) - math.log(base[2])) * e)  # the coda never zooms in
        # the fitted box dimensions blend to the whole world's with the same easing (a refit to another safe area stays consistent)
        bb = bdim[min(a, F - 1)].copy()
        for f in range(a, F):
            u = min(1.0, (f - a) / max(1, n)); e = u * u * (3 - 2 * u)
            bdim[f] = (bb[0] + ((ww[2] - ww[0]) - bb[0]) * e, bb[1] + ((ww[3] - ww[1]) - bb[1]) * e)
    return out.astype(np.float32), bdim.astype(np.float32)
