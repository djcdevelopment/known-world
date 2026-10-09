"""compile/camera.py: camera.f32 (STRATEGY 4.4). Per frame: centre x, y (world units) and scale s (px per world unit =
hex circumradius in px). fit_known: the box of tiles revealed by f + lookahead (plus risen islands and the HQ), scale
min(Wv/bw, Hv/bh)(1 - 2 pad) capped at max_hex_px; from era C scale only decreases; a forward-backward exponential
smoother on centre and log-scale (zero phase: the camera moves before the reveal), clamped so that every tile revealed
at frame f is inside the view. The coda frames the whole world. fixed_world is the control arm.
"""
import math

import numpy as np



def safe_area(params):
    """The frame minus the HUD plates' insets (x, y, w, h). The map owns the whole frame and runs under the plates; the
    camera fits the known world into this rectangle. Derived from the frame size, so a portrait frame needs no new maths."""
    W, H = int(params["frame_w"]), int(params["frame_h"])
    right = int(params["hud_right"]) + (int(params["stream_col_w"]) if params["stream"] == "on" else 0)
    l, t, b = int(params["hud_left"]), int(params["hud_top"]), int(params["hud_bottom"])
    return (l, t, W - l - right, H - t - b)


def centre(params):
    v = safe_area(params)
    return (v[0] + v[2] / 2.0, v[1] + v[3] / 2.0)


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


def build(params, clock, tfirst, tbox, items, hq_xy, world_bbox, coda_f, F, tmask=None):
    """tfirst: (nT,) first frame per tile (F = never). tbox: (nT, 4) x0, y0, x1, y1 of each tile's cells (half hex margin
    included). items: list of (frame, x0, y0, x1, y1) extra revealed things (islands, harbours). hq_xy: (F, 2).
    Returns float32 (F, 3)."""
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
        return out
    # revealed boxes by frame (cumulative min/max in frame order): land (tiles) and, separately, the risen islands. The HQ and the
    # islands join the fit only once the explored land is no longer one cluster (span >= camera_items_min_span world units), so
    # the start is tight on the first region (DIRECTION 'Start tight') and the archipelago and HQ come in at the first pull-back.
    sel = (tfirst < F) if tmask is None else ((tfirst < F) & tmask)  # ruins stay out of the box unless camera_ruins_in_box

    def cum(fr, bx):
        order = np.argsort(fr, kind="stable")
        fr, bx = fr[order], bx[order]
        return fr, (np.minimum.accumulate(bx[:, 0]), np.minimum.accumulate(bx[:, 1]), np.maximum.accumulate(bx[:, 2]), np.maximum.accumulate(bx[:, 3]))

    tfr, tcum = cum(tfirst[sel], tbox[sel])
    ifr, icum = cum(np.array([i[0] for i in items], dtype=np.int64), np.array([[i[1], i[2], i[3], i[4]] for i in items])) if len(items) else (np.zeros(0, dtype=np.int64), None)

    def at(fr, cm, f):
        k = int(np.searchsorted(fr, f, side="right")) - 1
        return None if k < 0 else (cm[0][k], cm[1][k], cm[2][k], cm[3][k])

    def union(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))

    first_box = (tcum[0][0], tcum[1][0], tcum[2][0], tcum[3][0])
    span_thr = float(params["camera_items_min_span"])
    hx, hy = hq_xy[:, 0], hq_xy[:, 1]
    hqx0, hqx1 = np.minimum.accumulate(hx), np.maximum.accumulate(hx)
    hqy0, hqy1 = np.minimum.accumulate(hy), np.maximum.accumulate(hy)
    tgt = np.zeros((F, 3))
    contain = np.zeros(F)
    bxs = np.zeros((F, 4))
    joined = False
    fend = float(params["camera_end_fill"])
    fb_ = at(tfr, tcum, F - 1) or first_box
    span0, spanF = max(max(first_box[2] - first_box[0], first_box[3] - first_box[1]), 6.0), max(fb_[2] - fb_[0], fb_[3] - fb_[1])
    for f in range(F):
        fl = min(F - 1, f + look)
        bt = at(tfr, tcum, fl) or first_box
        if not joined and max(bt[2] - bt[0], bt[3] - bt[1]) >= span_thr:
            joined = True
        b = bt
        if joined:
            b = union(b, at(ifr, icum, fl) if icum else None)
            b = union(b, (hqx0[fl], hqy0[fl], hqx1[fl], hqy1[fl]))
        x0, y0, x1, y1 = b
        bw, bh = max(x1 - x0, 6.0), max(y1 - y0, 4.0)
        u = min(1.0, max(0.0, math.log(max(bw, bh) / span0) / math.log(max(spanF / span0, 1.0001))))  # growth of the world since the first region
        s = min(Wv / bw, Hv / bh) * (fill + (fend - fill) * u)  # tight at the start (fill), roomier as the world grows (fend)
        tgt[f] = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, min(s, smax))
        b0 = at(tfr, tcum, f) or first_box
        if joined:
            b0 = union(b0, at(ifr, icum, f) if icum else None)
            b0 = union(b0, (hx[f] - 2, hy[f] - 2, hx[f] + 2, hy[f] + 2))
        a0, a1, a2, a3 = b0
        bxs[f] = (a0, a1, a2, a3)
        contain[f] = min(Wv / max(a2 - a0, 1e-6), Hv / max(a3 - a1, 1e-6)) * 0.97
    ls = np.log(tgt[:, 2])
    era = clock.era_frames()
    c0 = int(np.argmax(era == 2)) if (era == 2).any() else F
    if not params["zoom_in_allowed"]:
        ls = np.minimum.accumulate(ls)  # pull back only, from the first frame: the growth of scale is experienced as zoom
    alpha = 1.0 - math.exp(-1.0 / (params["camera_tau_s"] * fps))
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
    return out.astype(np.float32)
