"""compile/build.py: the compile (slice 4+). launches + nations + tiles + layout + camera + deltas + radio tables +
audio -> world.json, kw-data.js, audio, receipt.

    from build import build;  build(params, cut_s=None|90, outdir, probe_f, seed)
Only compile reads parameters; every output is hashed into the receipt. Deterministic.
"""
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as aud
import build_data as bd
import camera as cam
import clock as clk
import common
import corpus as corp
import launches as L
import layout as lay
import names as nm
import nations as nat
import series as ser
import synth
import tiles as til

BLOOM_LIFE = [0.40, 0.60, 0.90, 1.35, 2.0, 3.0]
RADIUS_PX = [6, 10, 15, 23, 35, 52]
DISPLAY = {"human": "human", "chatgpt": "ChatGPT", "claude": "Claude", "codex": "Codex", "opencode": "OpenCode",
           "local_model": "local", "automation": "automation"}
HOSTS = ("omen-e", "omen-c", "omen-linux", "am4", "fx99")
SURFACES = ("omen-c", "omen-e", "omen-linux", "am4", "fx99", "github")
SURFACE_LABEL = {"omen-c": "C:", "omen-e": "E:", "omen-linux": "linux", "am4": "AM4", "fx99": "FX99", "github": "GitHub"}
KIND = {"git": 0, "dir": 1, "third": 2}
SHAPE = {"single": 0, "mirv": 1, "unified": 2}


def frames_of(clock, t):
    return clock.frame(np.asarray(t, dtype=np.int64))


def build(params, cut_s=None, outdir=".", probe_f=15, seed=20261009, corpus=None, quiet=True, write_world=True):
    t_start = time.time()
    rec = {"params_hash": common.params_hash(params), "cut_s": cut_s, "inputs": common.corpus_inputs()}
    c = corpus or corp.load(params)
    rec["relations"] = "present" if c.relations else "absent"
    rec["chatgpt_links"] = "present" if c.chatgpt_links else "absent"
    snap = common.parse_ts(c.as_of)
    clock = clk.Clock(params, snap, cut_s=cut_s)
    F, fps = clock.F, clock.fps
    c, eps, tests, ng, launches, stats = L.run(params, c)
    nrows = nat.build(c, launches, params)
    nat_rows = [r for r in nrows if r["generation"] is None]
    classes = [r["nation"] for r in nat_rows]
    nat_index = {k: i for i, k in enumerate(classes)}
    nN = len(classes)
    env = clock.m ** -0.5 if params["cut_envelope_scale"] == "sqrt" else 1.0 / clock.m
    tau = clock.tau_frames()
    # ---- tiles and world -------------------------------------------------------------------------------------------
    Tl = til.collect(c, params, nat_index)
    Wd = lay.build(Tl, c, params)
    nT, nRg = len(Tl.path), len(Tl.regions)
    tfirst = np.full(nT, F, dtype=np.int64)
    fin = np.isfinite(Tl.first_t)
    tfirst[fin] = frames_of(clock, Tl.first_t[fin].astype(np.int64))
    spread = max(2, int(round(params["copy_reveal_spread_s"] * fps * env)))
    i = 0
    while i < nT:
        if not fin[i] or not Tl.reveal[i]:
            i += 1
            continue
        j = i
        while j < nT and fin[j] and Tl.reveal[j] and Tl.first_t[j] == Tl.first_t[i] and Tl.region[j] == Tl.region[i]:
            j += 1
        n = j - i
        for k in range(i, j):
            tfirst[k] = min(F - 1, tfirst[k] + ((k - i) * spread) // max(1, n))
        i = j
    tregion = Tl.region.astype(np.int64)
    rfirst = np.full(nRg, F, dtype=np.int64)
    np.minimum.at(rfirst, tregion, tfirst)
    thost = np.array([HOSTS.index(Tl.regions[r][1]) for r in tregion], dtype=np.uint8)
    tkind = np.array([KIND[Tl.regions[r][2]] for r in tregion], dtype=np.uint8)
    # ---- fields: deltas, checkpoints ----------------------------------------------------------------------------------
    Tt, Rt, Gt, Wt = Tl.touch_T, Tl.touch_tile, Tl.touch_g, Tl.touch_w
    ds, dr, dg, dw, df = ser.deltas(Tt, Rt, Gt, Wt, clock, nT, nN)
    hl = float(params["fog_half_life_days"])
    cps = ser.checkpoints(ds, dr, dg, dw, df, tau, hl, nT, nN, F)
    # ---- series -------------------------------------------------------------------------------------------------------
    series = ser.class_series(c, params, clock, nat_index)
    ccum, fcum = ser.commit_capacity(c, clock, nat_index)
    pcum = ser.participations(c, clock, nat_index)
    band_names, band_arr = ser.band_series(series, F, fps)
    hq_host, hq_hosts, hq_day_host = ser.hq_track(c, params, clock, tau)
    anchors = dict(Wd.anchor)
    hq_x, hq_y = ser.hq_positions(hq_host, hq_hosts, anchors, fps, max(2, int(round(params["hq_glide_s"] * fps * env))))
    bs, br, bw, bcls = ser.beams(c, params, clock, Tl.reg_index, Tl, params["beams_per_frame"])
    bcn = np.array([nat_index[x] for x in bcls], dtype=np.uint8) if len(bcls) else np.zeros(0, dtype=np.uint8)
    rings = ser.ring_births(series["chatgpt"], fps)
    # ---- islands, harbours, spurs, notches ---------------------------------------------------------------------------------
    isl_f = frames_of(clock, np.array([i["t"] for i in Wd.islands], dtype=np.int64)) if Wd.islands else np.zeros(0, dtype=np.int64)
    ic_x = np.array([x for i in Wd.islands for (x, y) in i["cells"]], dtype=np.float32)
    ic_y = np.array([y for i in Wd.islands for (x, y) in i["cells"]], dtype=np.float32)
    ic_s = np.cumsum([0] + [len(i["cells"]) for i in Wd.islands]).astype(np.int32)
    spur_f = frames_of(clock, np.array([s["t"] for s in Wd.spurs], dtype=np.int64)) if Wd.spurs else np.zeros(0, dtype=np.int64)
    notch_f = frames_of(clock, np.array([s["t"] for s in Wd.notches], dtype=np.int64)) if Wd.notches else np.zeros(0, dtype=np.int64)
    # ---- camera -------------------------------------------------------------------------------------------------------------
    tbx = np.zeros((nT, 4))
    for t in range(nT):
        a, b = Wd.tile_start[t], Wd.tile_start[t + 1]
        tbx[t] = (Wd.cell_x[a:b].min() - 0.87, Wd.cell_y[a:b].min() - 1.0, Wd.cell_x[a:b].max() + 0.87, Wd.cell_y[a:b].max() + 1.0)
    items = []
    for k, isl in enumerate(Wd.islands):
        xs = [p[0] for p in isl["cells"]]; ys = [p[1] for p in isl["cells"]]
        items.append((int(isl_f[k]), min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1))
    coda_f = F - int(round(clock.coda_s * fps))
    camera = cam.build(params, clock, tfirst, tbx, items, np.stack([hq_x, hq_y], 1), Wd.bbox, coda_f, F,
                       tmask=None if params["camera_ruins_in_box"] else (tkind != 2))
    cam_x, cam_y, cam_s = camera[:, 0].astype(np.float64), camera[:, 1].astype(np.float64), camera[:, 2].astype(np.float64)

    def screen_x(x, f):
        return cam.CENTRE[0] + (x - cam_x[f]) * cam_s[f]

    # ---- launches ----------------------------------------------------------------------------------------------------------
    gens = {r["nation"]: [] for r in nat_rows}
    for r in nrows:
        if r["generation"] is not None and r["entered"]:
            gens[r["nation"]].append(r)
    for k in gens:
        gens[k].sort(key=lambda r: r["first_ts"])
    gen_idx = {(k, r["generation"]): i for k, v in gens.items() for i, r in enumerate(v)}
    first_nat_launch = {r["nation"]: r["first_launch_id"] for r in nat_rows}
    spur_by = {(s["lineage"], s["ref"]): k for k, s in enumerate(Wd.spurs)}

    def region_of(lin, host):
        hs = Tl.hosts_of.get(lin) or []
        h = host if (lin, host) in Tl.reg_index else (hs[0] if hs else None)
        return Tl.reg_index.get((lin, h)) if h else None

    def pos_of(ri, dirs):
        ts = [Tl.tile_of.get((Tl.regions[ri][0], Tl.regions[ri][1], d)) for d in dirs]
        ts = [t for t in ts if t is not None] or [Tl.tile_of[(Tl.regions[ri][0], Tl.regions[ri][1], ".")]]
        return float(np.mean(Wd.tile_x[ts])), float(np.mean(Wd.tile_y[ts]))

    beam_f = max(3, int(round(params["beam_s"] * fps * env)))
    spread_w = max(1, int(round(params["warhead_spread_s"] * fps * env)))
    conv_f = max(3, int(round(params["unify_converge_s"] * fps * env)))
    rows = []
    skipped = 0
    by_id = {l["launch_id"]: l for l in launches}
    L_pos = {}
    for l in launches:
        ri = region_of(l["lineage"], l.get("host"))
        if ri is None:
            skipped += 1
            continue
        L_pos[l["launch_id"]] = (ri,) + pos_of(ri, l["_dirs"])
    surf_tests = {s: np.zeros(F) for s in SURFACES}
    surf_lines = {s: np.zeros(F) for s in SURFACES}
    tests_cum = np.zeros((nN, F)); lines_cum = np.zeros((nN, F)); files_cum = np.zeros((nN, F))
    shape_cnt = np.zeros((nN, 3), dtype=np.int64)
    for l in launches:
        if l["launch_id"] not in L_pos:
            continue
        ri, x, y = L_pos[l["launch_id"]]
        f = int(frames_of(clock, [l["ts_start"]])[0])
        band = l["yield"]["class"]
        shape = l["shape"]
        vb = min(6, band + 1) if shape == "unified" else band
        ni = nat_index[l["nation"]]
        gi = gen_idx.get((l["nation"], l["generation"]), 0)
        flags = (1 if l["first_test"] else 0) | (2 if shape == "mirv" else 0) | (4 if shape == "unified" else 0) | (8 if l["nation_inferred"] else 0) | (16 if first_nat_launch.get(l["nation"]) == l["launch_id"] else 0)
        life = max(3, int(round(BLOOM_LIFE[vb - 1] * env * fps)))
        whs = []
        if shape == "mirv" and l["warhead_list"]:
            n = len(l["warhead_list"])
            tot = max(1, sum(w["lines"] for w in l["warhead_list"]))
            for k, w in enumerate(l["warhead_list"]):
                if w["kind"] == "lineage":
                    tr = region_of(w["target"], w.get("host"))
                    if tr is None:
                        continue
                    tx, ty = pos_of(tr, w.get("_dirs") or [])
                    kind = 0
                else:
                    sk = spur_by.get((w.get("lineage"), w["target"]))
                    tr = region_of(w.get("lineage"), w.get("host"))
                    if tr is None:
                        continue
                    if sk is not None:
                        tx, ty, kind = Wd.spurs[sk]["x1"], Wd.spurs[sk]["y1"], 1
                    else:
                        tx, ty = pos_of(tr, []); kind = 0
                fl = f + beam_f + int(round(spread_w * k / max(1, n - 1)))
                share = w["lines"] / tot
                wb = 1 if share <= 0 else max(1, min(band, band + int(math.floor(math.log10(max(share, 1e-4))))))
                whs.append((min(F - 1, fl), tr, wb, tx, ty, kind))
        conv = []
        if shape == "unified":
            for uid in l["unifies"]:
                m = by_id.get(uid)
                if m is None:
                    continue
                for w in m["warhead_list"]:
                    if w["kind"] == "lineage":
                        tr = region_of(w["target"], w.get("host"))
                        if tr is not None:
                            conv.append(pos_of(tr, w.get("_dirs") or []))
                    else:
                        sk = spur_by.get((w.get("lineage"), w["target"]))
                        if sk is not None:
                            conv.append((Wd.spurs[sk]["x1"], Wd.spurs[sk]["y1"]))
            conv = sorted(set(conv))[:24]
        rows.append({"f": f, "ri": ri, "x": x, "y": y, "band": vb, "ni": ni, "gi": gi, "flags": flags, "life": life, "shape": SHAPE[shape],
                     "whs": whs, "conv": conv, "nat": l["nation"], "gen": l["generation"], "first_test": bool(l["first_test"]), "first_nat": bool(flags & 16),
                     "inferred": bool(l["nation_inferred"]), "host": l.get("host"), "lines": l["yield"]["lines"] or 0, "files": l["yield"]["files"] or 0,
                     "ts": l["ts_start"]})
        tests_cum[ni, f] += 1
        lines_cum[ni, f] += l["yield"]["lines"] or 0
        files_cum[ni, f] += l["yield"]["files"] or 0
        shape_cnt[ni, SHAPE[shape]] += 1
        hs = l.get("host") if l.get("host") in SURFACES else None
        if hs:
            surf_tests[hs][f] += 1
            surf_lines[hs][f] += l["yield"]["lines"] or l["yield"]["files"] or 0
    order = sorted(range(len(rows)), key=lambda i: (rows[i]["f"], i))
    rows = [rows[i] for i in order]
    nl = len(rows)
    lf = np.array([r["f"] for r in rows], dtype=np.int32)
    wstart, wf, wreg, wband, wx, wy, wkind = [0], [], [], [], [], [], []
    ustart, ux, uy = [0], [], []
    for r in rows:
        for (fl, tr, wb, tx, ty, kind) in r["whs"]:
            wf.append(fl); wreg.append(tr); wband.append(wb); wx.append(tx); wy.append(ty); wkind.append(kind)
        wstart.append(len(wf))
        for (px_, py_) in r["conv"]:
            ux.append(px_); uy.append(py_)
        ustart.append(len(ux))
    lpre = np.array([conv_f if (r["shape"] == 2 and r["conv"]) else 0 for r in rows], dtype=np.uint8)
    # collapse mask (audio and render share it)
    cmask = synth.collapse_mask(lf.astype(np.int64), F, params["collapse_events_per_s"], fps)
    synth_l = []
    for r in rows:
        whs = [(wf_, wb_, float(screen_x(wx_, min(F - 1, wf_)))) for (wf_, tr_, wb_, wx_, wy_, k_) in r["whs"]]
        synth_l.append({"f": r["f"], "px": float(screen_x(r["x"], r["f"])), "band": r["band"], "nat": r["nat"],
                        "gen": (r["gi"] + 1) if r["gen"] else None, "first_test": r["first_test"], "first_nat": r["first_nat"],
                        "shape": ("single", "mirv", "unified")[r["shape"]], "inferred": r["inferred"], "warheads": whs})
    # repo-born bells (GitHub islands rising; lineage's own first test already carries its bell)
    bells = [(int(isl_f[k]), float(screen_x(isl["x"], int(min(F - 1, isl_f[k]))))) for k, isl in enumerate(Wd.islands)]
    # ---- chips, legend ------------------------------------------------------------------------------------------------------
    chips = []
    for r in nrows:
        if r["generation"] is None or not r["entered"]:
            continue
        chips.append((nat_index[r["nation"]], r["generation"], nm.label_words(r["generation"]), nm.label_short(r["generation"]),
                      int(frames_of(clock, [common.parse_ts(r["first_ts"])])[0])))
    chips.sort(key=lambda x: (x[0], x[4], x[1]))
    entry_f = np.array([int(frames_of(clock, [common.parse_ts(r["first_ts"])])[0]) for r in nat_rows], dtype=np.int32)
    # ---- surfaces ------------------------------------------------------------------------------------------------------------
    sf_first = {}
    for h in HOSTS:
        m = np.array([Tl.regions[r][1] == h for r in tregion])
        sf_first[h] = int(tfirst[m].min()) if m.any() and (tfirst[m] < F).any() else F
    sf_first["github"] = int(isl_f.min()) if len(isl_f) else F
    commits_host = {h: np.zeros(F) for h in HOSTS}
    files_host = {h: np.zeros(F) for h in HOSTS}
    for lin, cs in c.commits.items():
        for x in cs:
            if x[7] in commits_host:
                f = int(frames_of(clock, [x[0]])[0])
                commits_host[x[7]][f] += 1
                files_host[x[7]][f] += x[5]
    for lin, tl in c.dir_touch.items():
        for (t, host, p, kind, n, by, bulk, cls) in tl:
            if host in files_host and not bulk:
                files_host[host][int(frames_of(clock, [t])[0])] += n
    surf = {"names": [SURFACE_LABEL[s] for s in SURFACES], "entry": [sf_first[s] for s in SURFACES]}
    sc_tests = np.stack([np.cumsum(surf_tests[s]) for s in SURFACES]).astype(np.uint16)
    sc_commits = np.stack([np.cumsum(commits_host[s]) if s in commits_host else np.zeros(F) for s in SURFACES]).astype(np.float32)
    sc_files = np.stack([np.cumsum(files_host[s]) if s in files_host else np.zeros(F) for s in SURFACES]).astype(np.float32)
    isl_cum = np.cumsum(np.bincount(isl_f, minlength=F)[:F]).astype(np.uint16) if len(isl_f) else np.zeros(F, dtype=np.uint16)
    # ---- tally card ----------------------------------------------------------------------------------------------------------
    touched = [set() for _ in range(nN)]
    tgt_g = Gt
    for g in range(nN):
        touched[g] = set(np.unique(Rt[tgt_g == g]).tolist())
    card = []
    for i, r in enumerate(nat_rows):
        ft = r["first_test_ts"]
        y = r["yield_total"]
        ys = ("%s lines" % compact(y["lines"])) if y["lines"] > 0 else (("%s files" % compact(y["files"])) if y["files"] > 0 else "0")
        card.append({"name": DISPLAY[r["nation"]], "first": ft[:10] if ft else "", "tests": r["tests"], "yield": ys,
                     "shapes": "%d / %d / %d" % tuple(int(v) for v in shape_cnt[i]), "tiles": "%d / %d" % (len(touched[i]), nT),
                     "parts": r["participations"]})
    footer = ["no chat source covers 2026-04",
              "no Claude Code transcript before 2026-05-09 survives: Claude is known from commit trailers only, 2026-01 to 2026-04"]
    # ---- data block ----------------------------------------------------------------------------------------------------------
    blk = bd.clock_block(clock, probe_f)
    f32 = lambda a: bd.b64(np.asarray(a).astype("<f4"))
    blk.update({
        "version": 2, "R": nRg, "T": nT, "G": nN, "hl": hl, "cp_every": ser.CP, "coda_f": int(coda_f),
        "hosts": list(HOSTS), "surfaces": surf,
        # world
        "ccx": f32(Wd.cell_x), "ccy": f32(Wd.cell_y), "cstart": bd.b64(Wd.tile_start.astype("<i4")),
        "tfirst": bd.b64(tfirst.astype("<i4")), "thost": bd.b64(thost), "tkind": bd.b64(tkind), "tregion": bd.b64(tregion.astype("<u2")),
        "tx": f32(Wd.tile_x), "ty": f32(Wd.tile_y),
        "rx": f32(Wd.reg_x), "ry": f32(Wd.reg_y), "rfirst": bd.b64(rfirst.astype("<i4")),
        "ds": bd.b64(ds.astype("<i4")), "dr": bd.b64(dr.astype("<u2")), "dg": bd.b64(dg.astype("u1")), "dw": f32(dw), "cpts": f32(cps),
        "ni": len(Wd.islands), "ifirst": bd.b64(isl_f.astype("<i4")), "ix": f32([i["x"] for i in Wd.islands]), "iy": f32([i["y"] for i in Wd.islands]),
        "icx": bd.b64(ic_x.astype("<f4")), "icy": bd.b64(ic_y.astype("<f4")), "istart": bd.b64(ic_s), "ifork": bd.b64(np.array([1 if i["fork"] else 0 for i in Wd.islands], dtype="u1")),
        "nh": len(Wd.harbours), "hx": f32([h["x"] for h in Wd.harbours]), "hy": f32([h["y"] for h in Wd.harbours]),
        "hisl": bd.b64(np.array([h["island"] for h in Wd.harbours], dtype="<u2")), "hreg": bd.b64(np.array([h["region"] for h in Wd.harbours], dtype="<u2")),
        "nb": len(Wd.bridges), "b0x": f32([b["p0"][0] for b in Wd.bridges]), "b0y": f32([b["p0"][1] for b in Wd.bridges]),
        "b1x": f32([b["p1"][0] for b in Wd.bridges]), "b1y": f32([b["p1"][1] for b in Wd.bridges]),
        "bra": bd.b64(np.array([b["a"] for b in Wd.bridges], dtype="<u2")), "brb": bd.b64(np.array([b["b"] for b in Wd.bridges], dtype="<u2")),
        "bkind": bd.b64(np.array([0 if b["kind"] == "host" else 1 for b in Wd.bridges], dtype="u1")),
        "nsp": len(Wd.spurs), "spf": bd.b64(spur_f.astype("<i4")), "spx0": f32([s["x0"] for s in Wd.spurs]), "spy0": f32([s["y0"] for s in Wd.spurs]),
        "spx1": f32([s["x1"] for s in Wd.spurs]), "spy1": f32([s["y1"] for s in Wd.spurs]), "spreg": bd.b64(np.array([s["region"] for s in Wd.spurs], dtype="<u2")),
        "nn": len(Wd.notches), "nof": bd.b64(notch_f.astype("<i4")), "nx": f32([s["x"] for s in Wd.notches]), "ny": f32([s["y"] for s in Wd.notches]),
        "nux": f32([s["ux"] for s in Wd.notches]), "nuy": f32([s["uy"] for s in Wd.notches]), "nreg": bd.b64(np.array([s["region"] for s in Wd.notches], dtype="<u2")),
        "bcn": {h: [round(Wd.beacon[h][0], 3), round(Wd.beacon[h][1], 3)] for h in Wd.beacon},
        "ring_xy": [round(Wd.anchor["cloud"][0], 3), round(Wd.anchor["cloud"][1], 3)],
        "hqx": f32(hq_x), "hqy": f32(hq_y), "hqh": bd.b64(hq_host.astype("u1")), "camera": f32(camera.reshape(-1)),
        # launches
        "nl": nl, "lf": bd.b64(lf.astype("<i4")), "lx": f32([r["x"] for r in rows]), "ly": f32([r["y"] for r in rows]),
        "lreg": bd.b64(np.array([r["ri"] for r in rows], dtype="<u2")), "lband": bd.b64(np.array([r["band"] for r in rows], dtype="u1")),
        "lnat": bd.b64(np.array([r["ni"] for r in rows], dtype="u1")), "lgen": bd.b64(np.array([r["gi"] for r in rows], dtype="u1")),
        "lflags": bd.b64(np.array([r["flags"] for r in rows], dtype="u1")), "llife": bd.b64(np.array([r["life"] for r in rows], dtype="<u2")),
        "lshape": bd.b64(np.array([r["shape"] for r in rows], dtype="u1")), "lpre": bd.b64(lpre),
        "wstart": bd.b64(np.array(wstart, dtype="<i4")), "wf": bd.b64(np.array(wf, dtype="<i4")), "wreg": bd.b64(np.array(wreg, dtype="<u2")),
        "wband": bd.b64(np.array(wband, dtype="u1")), "wx": f32(wx), "wy": f32(wy), "wkind": bd.b64(np.array(wkind, dtype="u1")),
        "ustart": bd.b64(np.array(ustart, dtype="<i4")), "ux": f32(ux), "uy": f32(uy),
        "beam_f": beam_f, "split_at": params["beam_split_at"], "conv_f": conv_f,
        "cmask": bd.b64(cmask.astype("u1")),
        "nat_names": [DISPLAY[k] for k in classes], "nat_classes": classes, "nat_entry_f": bd.b64(entry_f.astype("<i4")),
        "tests_cum": bd.b64(np.cumsum(tests_cum, axis=1).astype("<u2")), "lines_cum": bd.b64(np.cumsum(lines_cum, axis=1).astype("<f4")),
        "files_cum": bd.b64(np.cumsum(files_cum, axis=1).astype("<f4")), "commits_cum": bd.b64(ccum.astype("<f4")), "capfiles_cum": bd.b64(fcum.astype("<f4")),
        "parts_cum": bd.b64(pcum.astype("<f4")),
        "chips": [{"n": a, "g": b, "label": lb, "short": s, "f": f_} for (a, b, lb, s, f_) in chips],
        "chip_max": params["chip_max_visible"], "chip_named_f": max(6, int(round(params["chip_named_s"] * fps * env))),
        "sc_tests": bd.b64(sc_tests.astype("<u2")), "sc_commits": bd.b64(sc_commits.astype("<f4")), "sc_files": bd.b64(sc_files.astype("<f4")),
        "isl_cum": bd.b64(isl_cum.astype("<u2")),
        "radius_px": RADIUS_PX, "env_scale": round(env, 6),
        # radio
        "band_names": band_names, "band": bd.b64(band_arr), "band_window_f": int(round(params["band_window_s"] * fps)),
        "bs": bd.b64(bs.astype("<i4")), "br": bd.b64(br.astype("<u2")), "bw": bd.b64(bw), "bcn_n": bd.b64(bcn),
        "ring_f": bd.b64(rings.astype("<i4")),
        "seat": {h: bd.b64(np.minimum(255, series["seat_" + h]).astype("u1")) for h in ser.SEAT_HOSTS},
        "card": card, "card_footer": footer,
        "terrain_L": params["terrain_L"], "terrain_C": params["terrain_C"], "collapse_thr": params["collapse_events_per_s"], "labels": params["labels"],
    })
    os.makedirs(outdir, exist_ok=True)
    data_path = os.path.join(outdir, "kw-data.js")
    rec["kw_data_sha256"] = bd.write_data_js(data_path, blk)
    rec["kw_data_bytes"] = os.path.getsize(data_path)
    audio, astats = synth.synthesize(F, fps, seed, probe_f, synth_l, None, nat_rows, series, params, env, gen_idx,
                                     bells=bells, coda_f=coda_f, off_series=series["local_model"])
    rec["audio_sha256"] = common.sha256_bytes(aud.wav_bytes(audio))
    rec["audio_samples"] = int(len(audio)); rec["audio_expected"] = F * 1600
    rec["audio_stats"] = astats
    rec["clock"] = clock.summary()
    if write_world:
        rec["world_sha256"] = write_world_json(os.path.join(outdir, "world.json"), Tl, Wd, tfirst, rfirst, params)
    hq_cross = None
    ch = np.nonzero(np.diff(hq_host.astype(np.int64)))[0]
    rec["hq"] = {"changes": [(int(f), hq_hosts[int(hq_host[f + 1])]) for f in ch][:40],
                 "first_linux_day_iso": common.iso(int(clock.epoch0 * 86400 + int(np.argmax(hq_day_host == hq_hosts.index("omen-linux"))) * 86400)) if (hq_day_host == hq_hosts.index("omen-linux")).any() else None}
    rec["counts"] = {"regions": nRg, "tiles": nT, "cells": int(Tl.cells.sum()), "tiles_by_kind": {k: int((tkind == v).sum()) for k, v in KIND.items()},
                     "tiles_never_touched": int((tfirst >= F).sum()), "touches": int(len(Tt)), "deltas": int(len(dr)), "checkpoints": int(cps.shape[0]),
                     "launches": nl, "launches_skipped_no_region": skipped, "chips": len(chips), "nations": classes,
                     "peak_launches_per_frame": int(np.bincount(lf).max()) if nl else 0, "launch_counts": L.counts(launches, stats, params),
                     "layout": {"constellations": Wd.constellations, "joined_lineages": Wd.joined, "islands": len(Wd.islands), "harbours": len(Wd.harbours),
                                "bridges": len(Wd.bridges), "spurs": len(Wd.spurs), "notches": len(Wd.notches)},
                     "tiles_stats": Tl.stats, "tiles_counts": Tl.counts, "beams": int(len(br)), "rings": int(len(rings)),
                     "collapsed_frames": int(cmask.sum())}
    rec["compile_s"] = round(time.time() - t_start, 1)
    rec["_tau"] = tau
    extra = {"T": Tt, "R": Rt, "G": Gt, "W": Wt, "nT": nT, "nat_index": nat_index, "series": series, "launches": launches, "nrows": nrows,
             "tiles": Tl, "world": Wd, "tfirst": tfirst, "rfirst": rfirst, "camera": camera, "rows": rows, "clock": clock, "corpus": c,
             "stats": stats, "tests": tests, "ng": ng, "eps": eps, "hq_host": hq_host, "hq_hosts": hq_hosts, "isl_f": isl_f}
    return rec, audio, data_path, clock, extra


def compact(v):
    return "%.1fM" % (v / 1e6) if v >= 1e6 else ("%.1fk" % (v / 1e3) if v >= 1e4 else (("%.1fk" % (v / 1e3)) if v >= 1e3 else str(int(round(v)))))


def write_world_json(path, Tl, Wd, tfirst, rfirst, params):
    """world.json: geometry without names. Tiles by id: region, cells, lattice cells (q, r), first-touch epoch."""
    q, r = Wd.cell_q.tolist(), Wd.cell_r.tolist()
    obj = {
        "version": 2, "hex": "axial pointy-top, world unit = circumradius, x = sqrt3 (q + r/2), y = 1.5 r",
        "regions": [{"host": h, "kind": k} for (L_, h, k) in Tl.regions],
        "tiles": {"region": Tl.region.tolist(), "cells": Tl.cells.tolist(), "first_t": [None if not np.isfinite(x) else int(x) for x in Tl.first_t],
                  "reveal": Tl.reveal.astype(int).tolist(), "start": Wd.tile_start.tolist()},
        "lattice": {"q": q, "r": r},
        "continents": {h: {k: round(v, 3) for k, v in d.items()} for h, d in sorted(Wd.cont.items())},
        "islands": [{"t": i["t"], "x": round(i["x"], 3), "y": round(i["y"], 3), "cells": len(i["cells"]), "fork": i["fork"]} for i in Wd.islands],
        "harbours": [{"island": h["island"], "region": h["region"]} for h in Wd.harbours],
        "bridges": [{"a": b["a"], "b": b["b"], "kind": b["kind"]} for b in Wd.bridges],
        "spurs": len(Wd.spurs), "notches": len(Wd.notches), "bbox": [round(v, 3) for v in Wd.bbox],
        "params": {k: params[k] for k in ("tile_area_k", "coast_gap", "third_party", "geography")},
    }
    return common.write_json(path, obj)


def strip_private(rec):
    return {k: v for k, v in rec.items() if not k.startswith("_")}
