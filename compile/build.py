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
import marks as mk
import layout as lay
import names as nm
import nations as nat
import series as ser
import stream as stm
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


def region_of_(Tl, lin, host):
    hs = Tl.hosts_of.get(lin) or []
    h = host if (lin, host) in Tl.reg_index else (hs[0] if hs else None)
    return Tl.reg_index.get((lin, h)) if h else None


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
    rt = ser.running_totals(c, params, clock, nat_index, SURFACES, HOSTS, launches)
    assert np.array_equal(rt["ccum"].astype(np.float32), ccum) and np.array_equal(rt["fcum"].astype(np.float32), fcum)
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
    # launch targets are placed further down (rows); the camera needs them now, so they are located here from the same position maths
    cam_launch_pts = []
    for l in launches:
        ri_ = region_of_(Tl, l["lineage"], l.get("host"))
        if ri_ is None:
            continue
        tsl = [Tl.tile_of.get((Tl.regions[ri_][0], Tl.regions[ri_][1], d)) for d in l["_dirs"]]
        tsl = [t for t in tsl if t is not None] or [Tl.tile_of[(Tl.regions[ri_][0], Tl.regions[ri_][1], ".")]]
        cam_launch_pts.append((int(frames_of(clock, [l["ts_start"]])[0]), float(np.mean(Wd.tile_x[tsl])), float(np.mean(Wd.tile_y[tsl])), int(l["ts_start"]), int(l["yield"]["class"])))
    cam_beacons = []
    for h in ser.SEAT_HOSTS:
        sv = series["seat_" + h]
        if h in Wd.beacon and (sv > 0).any():
            cam_beacons.append((int(np.argmax(sv > 0)), float(Wd.beacon[h][0]), float(Wd.beacon[h][1])))
    cam_report = {}
    camera, cam_box = cam.build(params, clock, tfirst, tbx, items, np.stack([hq_x, hq_y], 1), Wd.bbox, coda_f, F,
                       tmask=None if params["camera_ruins_in_box"] else (tkind != 2),
                       touches=(Tt, Rt, Wt, Tl.touch_burst), launch_pts=cam_launch_pts, beacons=cam_beacons, report=cam_report)
    rec["camera"] = cam_report
    cam_x, cam_y, cam_s = camera[:, 0].astype(np.float64), camera[:, 1].astype(np.float64), camera[:, 2].astype(np.float64)

    cam_cx = cam.centre(params)[0]

    def screen_x(x, f):
        return cam_cx + (x - cam_x[f]) * cam_s[f]

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
    tp = rt["totals"]["third"]
    lu = rt["totals"]["lines_uncapped"]
    bulk = rt["totals"]["bulk_copy_excluded"]
    footer = ["no chat source covers 2026-04",
              "no Claude Code transcript before 2026-05-08 survives: Claude is known from commit trailers only, 2026-01 to 2026-04"]
    if params["bulk_copy_footer"] and bulk:
        footer.append("bulk copies are not counted: %s births and %s updates left out of files created and updated" % (format(bulk["file_birth"], ","), format(bulk["file_update"], ",")))
    if lu["cap"]:
        footer.append("lines are capped at %s per commit, as in launch yield (%s commits); uncapped total %s added + removed" % (
            format(lu["cap"], ","), format(lu["commits_capped"], ","), format(lu["total"], ",")))
    card_third = None
    if params["third_party_clones_row"] == "tally_card":
        tl = tp.get("clone_lines_capped", 0) if lu["cap"] else tp.get("clone_lines", 0)
        card_third = "third-party clones, explored not built: %s commits, %s lines, %s without line counts" % (
            format(tp.get("clone_commits", 0), ","), format(int(tl), ","), format(tp.get("clone_no_numstat", 0), ","))
    for i, r in enumerate(card):
        k = nat_rows[i]["nation"]; tn = rt["totals"]["nation"][k]
        r["commits"] = format(tn["commits"], ","); r["files"] = format(tn["files_changed"], ",")
        r["lines"] = "+%s / \u2212%s" % (compact(tn["lines_added"]), compact(tn["lines_removed"]))
    wt = rt["totals"]["world"]
    card_world = {"name": "world", "tests": int(sum(r["tests"] for r in card)), "commits": format(wt["commits"], ","), "files": format(wt["files"], ","),
                  "lines": "%s" % compact(wt["lines"])}
    # ---- marks (the scrubber's hashmarks, the ticker hairline's ticks) -------------------------------------------------------
    marks, marks_diag = [], {}
    if params["marks"] == "on":
        sw_f = [int(np.argmax(clock.era_frames() >= i + 1)) for i in range(2)]
        hq_lin = hq_hosts.index("omen-linux")
        hq_cross = int(np.argmax(hq_host == hq_lin)) if (hq_host == hq_lin).any() else None
        marks, marks_diag = mk.build(params, clock, sw_f, [(SURFACE_LABEL[s_], int(sf_first[s_])) for s_ in SURFACES],
                                     [(DISPLAY[r_["nation"]], int(entry_f[i_])) for i_, r_ in enumerate(nat_rows)], hq_cross, series["local_model"],
                                     {"commits": rt["w"][0], "files": rt["w"][1], "launches": np.cumsum(tests_cum.sum(0))})
        rec["marks_counts"] = {k_: sum(1 for m_ in marks if m_["kind"] == k_) for k_ in ("era", "surface", "nation", "migration", "storm", "regime")}
        rec["marks_diag"] = marks_diag
    # ---- the stream ---------------------------------------------------------------------------------------------------------
    st = stm.build(params, c, clock, launches, Wd, Tl, rfirst, nat_index) if params["stream"] == "on" else None
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
        "hqx": f32(hq_x), "hqy": f32(hq_y), "hqh": bd.b64(hq_host.astype("u1")), "camera": f32(camera.reshape(-1)), "camera_box": f32(cam_box.reshape(-1)),
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
        "ins_cum": f32(rt["icum"]), "del_cum": f32(rt["dcum"]), "rate_nat": f32(rt["rate"]), "w_cum": f32(rt["w"]),
        "sc_created": f32(rt["sc_created"]), "sc_updated": f32(rt["sc_updated"]),
        "created_nat": f32(rt["created_nat"]) if rt["created_nat"] is not None else None,
        "rate_unit_names": list(ser.ERA_UNIT_NAMES), "rate_window": params["rate_window"],
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
        "marks": marks,
        "card": card, "card_world": card_world, "card_footer": footer, "card_third": card_third,
        "layout": {"W": int(params["frame_w"]), "H": int(params["frame_h"]), "kind": params["layout"], "hud": params["hud"], "alpha": params["hud_alpha"] if params["hud"] == "plates" else 1.0,
                   "left": int(params["hud_left"]), "top": int(params["hud_top"]), "right": int(params["hud_right"]), "bottom": int(params["hud_bottom"]),
                   "safe": list(cam.safe_area(params))},
        "layout_portrait": params["hud_portrait"],
        "ia": ia_block(params, fps) if params["layout"] == "ia" else None,
        "coast": bool(params["layout"] == "ia" and params["ia_coast_labels"] == "on"),
        "terrain_L": params["terrain_L"], "terrain_C": params["terrain_C"], "collapse_thr": params["collapse_events_per_s"], "labels": params["labels"],
    })
    if st is not None:
        blk["stream"] = stream_block(st, params, fps)
    os.makedirs(outdir, exist_ok=True)
    data_path = os.path.join(outdir, "kw-data.js")
    rec["marks_sha256"] = common.write_json(os.path.join(outdir, "marks.json"), marks)
    rec["kw_data_sha256"] = bd.write_data_js(data_path, blk)
    rec["kw_data_bytes"] = os.path.getsize(data_path)
    audio, astats = synth.synthesize(F, fps, seed, probe_f, synth_l, None, nat_rows, series, params, env, gen_idx,
                                     bells=bells, coda_f=coda_f, off_series=series["local_model"])
    rec["audio_sha256"] = common.sha256_bytes(aud.wav_bytes(audio))
    rec["audio_samples"] = int(len(audio)); rec["audio_expected"] = F * 1600
    rec["audio_stats"] = astats
    rec["clock"] = clock.summary()
    rec["running_totals"] = rt["totals"]
    if st is not None:
        rec["stream"] = st["stats"]
        rec["stream"]["edge_types"] = dict(st["edge_types"])
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


def ia_block(params, fps):
    """The information-architecture zones (DIRECTION rev 5): pixel rects of the landscape frame and the portrait recipe. The page lays out
    from these; nothing in the page names 1920 or 1080."""
    W, H = int(params["frame_w"]), int(params["frame_h"])
    th, nw, tl = int(params["ia_ticker_h"]), int(params["ia_nation_w"]), int(params["ia_timeline_h"])
    rh, bh, pitch, nl = int(params["ia_ruler_h"]), int(params["ia_band_h"]), int(params["ia_lane_pitch"]), int(params["ia_lanes_max"])
    ty = H - tl
    ax1 = W - int(params["ia_axis_pad_r"])
    ax0 = ax1 - 3 * int(round(params["stream_window_s"] * fps))   # 3 px per film frame: a steady, integer scroll
    return {"ticker": [0, 0, 720, th], "map": list(cam.safe_area(params)), "nations": [W - nw, 0, nw, ty],
            "timeline": [0, ty, W, tl], "ruler": [0, ty, W, rh], "band": [0, ty + rh, W, bh], "lanes": [0, ty + rh + bh + 3, W, nl * pitch],
            "ax0": ax0, "ax1": ax1, "name_w": int(params["ia_name_w"]), "pitch": pitch, "nl": nl, "window_f": int(round(params["stream_window_s"] * fps)),
            "nation_fade_f": max(2, int(round(float(params["ia_nation_fade_s"]) * fps))), "portrait": params["ia_portrait"],
            "nation_row": int(params["ia_nation_row_fit"]), "design": params["design_system"] == "on"}


def stream_block(st, params, fps):
    f32 = lambda a: bd.b64(np.asarray(a).astype("<f4"))
    i32 = lambda a: bd.b64(np.asarray(a).astype("<i4"))
    u8 = lambda a: bd.b64(np.asarray(a).astype("u1"))
    rl, mv, tk = st["rail"], st["mirv"], st["ticks"]
    ms, ml = [0], []
    for (_f, _n, lanes) in mv:
        ml += lanes; ms.append(len(ml))
    return {"L": st["L"], "K": st["K"], "names": st["names"], "labels": params["stream_labels"],
            "horizontal": bool(st["horizontal"]), "max_lanes": int(st["max_lanes"]),
            "col_x": 1600 - int(params["stream_col_w"]), "col_w": int(params["stream_col_w"]), "ruler_w": stm.RULER_W,
            "window_f": int(round(params["stream_window_s"] * fps)), "fade_f": max(2, int(round(params["stream_fade_s"] * fps))),
            "conn_f": max(2, int(round(params["stream_connector_s"] * fps))),
            "sid": u8(st["sl_id"].reshape(-1)), "sx": f32(st["sl_x"].reshape(-1)), "sa": u8(st["sl_a"].reshape(-1)),
            "ss": i32(st["sl_since"].reshape(-1)), "sq": u8(st["quiet"]),
            "n": int(len(st["cm_f"])), "cf": i32(st["cm_f"]), "cl": u8(st["cm_lane"]), "cn": u8(st["cm_nat"]), "cc": u8(st["cm_code"]), "cs": u8(st["cm_side"]),
            "bf": i32(st["bridge_f"]), "con": u8([255 if x < 0 else x for x in st["lane_con"]]),
            "nr": len(rl), "rf0": i32([r[0] for r in rl]), "rlane": u8([r[1] for r in rl]), "rf1": i32([r[2] for r in rl]),
            "rflag": u8([r[3] for r in rl]), "rside": u8([r[4] for r in rl]),
            "nm": len(mv), "mf": i32([r[0] for r in mv]), "mnat": u8([r[1] for r in mv]), "mstart": i32(ms), "mlane": u8(ml),
            "ne": len(st["edges"]), "ea": u8([e[0] for e in st["edges"]]), "eb": u8([e[1] for e in st["edges"]]), "ef": i32([e[2] for e in st["edges"]]),
            "nt": len(tk["f"]), "tf": i32(tk["f"]), "tl": u8(tk["level"]), "tlab": tk["label"]}


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
