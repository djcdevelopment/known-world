"""compile/build.py: the slice-3 compile. launches + nations + layout + deltas + audio -> kw-data.js, audio, receipt.

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
import clock as clk
import common
import corpus as corp
import launches as L
import layout as lay
import nations as nat
import series as ser
import synth

BLOOM_LIFE = [0.40, 0.60, 0.90, 1.35, 2.0, 3.0]
RADIUS_PX = [6, 10, 15, 23, 35, 52]
DISPLAY = {"human": "human", "chatgpt": "ChatGPT", "claude": "Claude", "codex": "Codex", "opencode": "OpenCode",
           "local_model": "local", "automation": "automation"}


def short(label):
    import re
    m = re.match(r"^([a-z]+)-(\d+)$", label)
    return (m.group(1)[0] + m.group(2)) if m else label[:3]


def build(params, cut_s=None, outdir=".", probe_f=15, seed=20261009, corpus=None, quiet=True):
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
    # regions
    cand = set(c.commits) | {k for k in c.chat} | {k for k, d in c.nongit.items() if any(v["files"] > 0 for v in d.values())} | {l["lineage"] for l in launches}
    cand = {x for x in cand if x in c.own or x in c.dirs}
    first_ts = {x: common.parse_ts(c.lineages[x]["first_ts"]) for x in cand}
    ids = sorted(cand, key=lambda x: (first_ts[x], x))
    region_index = {x: i for i, x in enumerate(ids)}
    nR = len(ids)
    evc = {x: sum((c.lineages[x].get("events") or {}).values()) for x in ids}
    pos = lay.build(c, ids, first_ts, evc)
    # deltas, checkpoints
    T, R, G, W = ser.collect_events(c, params, region_index, nat_index)
    ds, dr, dg, dw, df = ser.deltas(T, R, G, W, clock, nR, nN)
    tau = clock.tau_frames()
    hl = float(params["fog_half_life_days"])
    cps = ser.checkpoints(ds, dr, dg, dw, df, tau, hl, nR, nN, F)
    rfirst = np.full(nR, F, dtype=np.int32)
    np.minimum.at(rfirst, dr.astype(np.int64), df.astype(np.int32))
    series = ser.class_series(c, params, clock, nat_index)
    ccum, fcum = ser.commit_capacity(c, clock, nat_index)
    # launches for render and sound
    env = clock.m ** -0.5 if params["cut_envelope_scale"] == "sqrt" else 1.0 / clock.m
    gens = {}
    for r in nat_rows:
        gens[r["nation"]] = []
    for r in nrows:
        if r["generation"] is not None and r["entered"]:
            gens[r["nation"]].append(r)
    for k in gens:
        gens[k].sort(key=lambda r: r["first_ts"])
    gen_idx = {(k, r["generation"]): i for k, v in gens.items() for i, r in enumerate(v)}
    first_nat_launch = {r["nation"]: r["first_launch_id"] for r in nat_rows}
    lf, lreg, lband, lnat, lgen, lflags, llife = [], [], [], [], [], [], []
    wstart, wf, wreg, wband = [0], [], [], []
    synth_l = []
    tests_cum = np.zeros((nN, F), dtype=np.float64); lines_cum = np.zeros((nN, F)); files_cum = np.zeros((nN, F))
    skipped = 0
    for l in launches:
        r = region_index.get(l["lineage"])
        if r is None:
            skipped += 1
            continue
        f = int(clock.frame(np.array([l["ts_start"]]))[0])
        band = l["yield"]["class"]
        shape = l["shape"]
        vb = min(6, band + 1) if shape == "unified" else band
        ni = nat_index[l["nation"]]
        gi = gen_idx.get((l["nation"], l["generation"]), 0)
        flags = (1 if l["first_test"] else 0) | (2 if shape == "mirv" else 0) | (4 if shape == "unified" else 0) | (8 if l["nation_inferred"] else 0) | (16 if first_nat_launch.get(l["nation"]) == l["launch_id"] else 0)
        life = max(3, int(round(BLOOM_LIFE[vb - 1] * env * fps)))
        lf.append(f); lreg.append(r); lband.append(vb); lnat.append(ni); lgen.append(gi); lflags.append(flags); llife.append(life)
        whs = []
        if shape == "mirv" and l["warhead_list"]:
            n = len(l["warhead_list"])
            tot = max(1, sum(w["lines"] for w in l["warhead_list"]))
            spread = max(1, int(round(params["warhead_spread_s"] * fps)))
            for k, w in enumerate(l["warhead_list"]):
                tr = region_index.get(w["target"] if w["kind"] == "lineage" else w.get("lineage"))
                if tr is None:
                    continue
                fl = f + int(round(spread * k / max(1, n - 1)))
                share = w["lines"] / tot
                wb = 1 if share <= 0 else max(1, min(band, band + int(math.floor(math.log10(max(share, 1e-4))))))
                wf.append(fl); wreg.append(tr); wband.append(wb)
                whs.append((fl, wb, float(pos["px"][tr])))
        wstart.append(len(wf))
        synth_l.append({"f": f, "px": float(pos["px"][r]), "band": vb, "nat": l["nation"], "gen": (gi + 1) if (l["generation"] and gi is not None) else None,
                        "first_test": bool(l["first_test"]), "first_nat": bool(flags & 16), "shape": shape,
                        "inferred": bool(l["nation_inferred"]), "warheads": whs})
        tests_cum[ni, f] += 1
        lines_cum[ni, f] += l["yield"]["lines"] or 0
        files_cum[ni, f] += l["yield"]["files"] or 0
    order = np.argsort(np.array(lf, dtype=np.int64), kind="stable")
    # keep launch arrays sorted by f; warhead slices follow the permutation
    def perm(a, dt):
        return np.array(a, dtype=dt)[order]
    ws_old = np.array(wstart)
    wf_a, wr_a, wb_a = np.array(wf, dtype=np.int32), np.array(wreg, dtype=np.uint16), np.array(wband, dtype=np.uint8)
    nw_f, nw_r, nw_b, nw_s = [], [], [], [0]
    for i in order:
        a, b = ws_old[i], ws_old[i + 1]
        nw_f += list(wf_a[a:b]); nw_r += list(wr_a[a:b]); nw_b += list(wb_a[a:b]); nw_s.append(len(nw_f))
    synth_l = [synth_l[i] for i in order]
    entry_f = np.array([int(clock.frame(np.array([common.parse_ts(r["first_ts"])]))[0]) for r in nat_rows], dtype=np.int32)
    chips = [(nat_index[r["nation"]], r["generation"], short(r["generation"]), int(clock.frame(np.array([common.parse_ts(r["first_ts"])]))[0]))
             for r in nrows if r["generation"] is not None and r["entered"]]
    chips.sort(key=lambda x: (x[0], x[3]))
    blk = bd.clock_block(clock, probe_f)
    blk.update({
        "R": nR, "G": nN, "hl": hl, "cp_every": ser.CP,
        "rx": bd.b64(pos["px"].astype("<f4")), "ry": bd.b64(pos["py"].astype("<f4")), "rrad": bd.b64(pos["rad"].astype("<f4")), "rfirst": bd.b64(rfirst.astype("<i4")),
        "ds": bd.b64(ds.astype("<i4")), "dr": bd.b64(dr.astype("<u2")), "dg": bd.b64(dg.astype("u1")), "dw": bd.b64(dw.astype("<f4")),
        "cpts": bd.b64(cps.astype("<f4")),
        "nl": len(lf), "lf": bd.b64(perm(lf, "<i4")), "lreg": bd.b64(perm(lreg, "<u2")), "lband": bd.b64(perm(lband, "u1")),
        "lnat": bd.b64(perm(lnat, "u1")), "lgen": bd.b64(perm(lgen, "u1")), "lflags": bd.b64(perm(lflags, "u1")), "llife": bd.b64(perm(llife, "<u2")),
        "wstart": bd.b64(np.array(nw_s, dtype="<i4")), "wf": bd.b64(np.array(nw_f, dtype="<i4")), "wreg": bd.b64(np.array(nw_r, dtype="<u2")), "wband": bd.b64(np.array(nw_b, dtype="u1")),
        "nat_names": [DISPLAY[k] for k in classes], "nat_classes": classes, "nat_entry_f": bd.b64(entry_f.astype("<i4")),
        "tests_cum": bd.b64(np.cumsum(tests_cum, axis=1).astype("<u2")), "lines_cum": bd.b64(np.cumsum(lines_cum, axis=1).astype("<f4")),
        "files_cum": bd.b64(np.cumsum(files_cum, axis=1).astype("<f4")), "commits_cum": bd.b64(ccum.astype("<f4")), "capfiles_cum": bd.b64(fcum.astype("<f4")),
        "chips": [{"n": a, "label": b, "short": s, "f": f} for (a, b, s, f) in chips],
        "radius_px": RADIUS_PX, "env_scale": round(env, 6),
    })
    os.makedirs(outdir, exist_ok=True)
    data_path = os.path.join(outdir, "kw-data.js")
    rec["kw_data_sha256"] = bd.write_data_js(data_path, blk)
    rec["kw_data_bytes"] = os.path.getsize(data_path)
    audio, astats = synth.synthesize(F, fps, seed, probe_f, synth_l, None, nat_rows, series, params, env, gen_idx)
    rec["audio_sha256"] = common.sha256_bytes(aud.wav_bytes(audio))
    rec["audio_samples"] = int(len(audio)); rec["audio_expected"] = F * 1600
    rec["audio_stats"] = astats
    rec["clock"] = clock.summary()
    rec["counts"] = {"regions": nR, "launches": len(lf), "launches_skipped_no_region": skipped, "deltas": int(len(dr)), "checkpoints": int(cps.shape[0]),
                     "layout": {k: pos[k] for k in ("constellations", "joined", "loose")}, "chips": len(chips), "nations": classes,
                     "peak_launches_per_frame": int(np.bincount(np.array(lf)).max()), "launch_counts": L.counts(launches, stats, params)}
    rec["compile_s"] = round(time.time() - t_start, 1)
    rec["_tau"] = tau
    return rec, audio, data_path, clock, {"T": T, "R": R, "G": G, "W": W, "region_ids": ids, "nat_index": nat_index, "series": series, "launches": launches, "nrows": nrows}


def strip_private(rec):
    return {k: v for k, v in rec.items() if not k.startswith("_")}
