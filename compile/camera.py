"""compile/camera.py: camera.f32 (STRATEGY 4.4). Per frame: centre x, y (world units) and scale s (px per world unit =
hex circumradius in px). fit_known: the box of tiles revealed by f + lookahead (plus risen islands and the HQ), scale
min(Wv/bw, Hv/bh)(1 - 2 pad) capped at max_hex_px; from era C scale only decreases; a forward-backward exponential
smoother on centre and log-scale (zero phase: the camera moves before the reveal), clamped so that every tile revealed
at frame f is inside the view. The coda frames the whole world. fixed_world is the control arm.
"""
import math

import numpy as np

VIEW = (240, 64, 1360, 896)  # map area on the 1920 x 1080 canvas
CENTRE = (VIEW[0] + VIEW[2] / 2.0, VIEW[1] + VIEW[3] / 2.0)


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
    Wv, Hv = VIEW[2], VIEW[3]
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
    # revealed boxes by frame (cumulative min/max over everything, in frame order)
    sel = (tfirst < F) if tmask is None else ((tfirst < F) & tmask)  # ruins stay out of the box unless camera_ruins_in_box
    fr = np.concatenate([tfirst[sel], np.array([i[0] for i in items], dtype=np.int64)]) if len(items) else tfirst[sel]
    bx = np.concatenate([tbox[sel]] + ([np.array([[i[1], i[2], i[3], i[4]] for i in items])] if len(items) else []))
    order = np.argsort(fr, kind="stable")
    fr, bx = fr[order], bx[order]
    cmin_x, cmin_y = np.minimum.accumulate(bx[:, 0]), np.minimum.accumulate(bx[:, 1])
    cmax_x, cmax_y = np.maximum.accumulate(bx[:, 2]), np.maximum.accumulate(bx[:, 3])

    def box_at(f):
        k = int(np.searchsorted(fr, f, side="right")) - 1
        if k < 0:
            return None
        return cmin_x[k], cmin_y[k], cmax_x[k], cmax_y[k]

    frames = np.arange(F)
    hx, hy = hq_xy[:, 0], hq_xy[:, 1]
    # cumulative HQ box
    hqx0, hqx1 = np.minimum.accumulate(hx), np.maximum.accumulate(hx)
    hqy0, hqy1 = np.minimum.accumulate(hy), np.maximum.accumulate(hy)
    tgt = np.zeros((F, 3))
    contain = np.zeros(F)
    bxs = np.zeros((F, 4))
    for f in range(F):
        b = box_at(min(F - 1, f + look))
        b0 = box_at(f)
        if b is None:
            b = (cx_w - 12, cy_w - 8, cx_w + 12, cy_w + 8)
        x0, y0, x1, y1 = b
        fl = min(F - 1, f + look)
        x0, y0, x1, y1 = min(x0, hqx0[fl]), min(y0, hqy0[fl]), max(x1, hqx1[fl]), max(y1, hqy1[fl])
        bw, bh = max(x1 - x0, 6.0), max(y1 - y0, 4.0)
        s = min(Wv / bw, Hv / bh) * (1 - 2 * pad)
        tgt[f] = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, min(s, smax))
        if b0 is None:
            b0 = (hx[f] - 3, hy[f] - 3, hx[f] + 3, hy[f] + 3)
        a0, a1, a2, a3 = b0
        a0, a1, a2, a3 = min(a0, hx[f] - 2), min(a1, hy[f] - 2), max(a2, hx[f] + 2), max(a3, hy[f] + 2)
        bxs[f] = (a0, a1, a2, a3)
        contain[f] = min(Wv / max(a2 - a0, 1e-6), Hv / max(a3 - a1, 1e-6)) * 0.97
    ls = np.log(tgt[:, 2])
    era = clock.era_frames()
    c0 = int(np.argmax(era == 2)) if (era == 2).any() else F
    if not params["zoom_in_allowed"]:
        ls[c0:] = np.minimum.accumulate(ls[c0:])
    alpha = 1.0 - math.exp(-1.0 / (params["camera_tau_s"] * fps))
    cxs, cys, lss = _fb(tgt[:, 0], alpha), _fb(tgt[:, 1], alpha), _fb(ls, alpha)
    lss = np.minimum(lss, np.log(smax))
    lss = np.minimum(lss, np.log(contain))
    if not params["zoom_in_allowed"]:
        lss[c0:] = np.minimum.accumulate(lss[c0:])
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
            out[f, 2] = math.exp(math.log(base[2]) + (math.log(s_world) - math.log(base[2])) * e)
    return out.astype(np.float32)
