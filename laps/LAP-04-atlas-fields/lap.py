"""LAP-04 atlas and fields. Stages: build audit verify stills (or `all`). Run from the repo root:

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-04-atlas-fields/lap.py <stage>
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "export"))
import lapkit as K
import audit as aud_mod
import clock as clk
import common
import corpus as corp
import launches as L
import strip

BUILD = os.path.join(HERE, "build-full")


def stage_build(params):
    rec, audio, path, clock, extra = K.build_piece(params, None, BUILD)
    r = K.build.strip_private(rec)
    r["compile_twice"] = K.compile_twice(rec, 0, HERE, "full")
    r["code"] = K.code_hashes()
    K.save(HERE, "receipt-build.json", r)
    shutil.copy(os.path.join(BUILD, "world.json"), os.path.join(HERE, "world.json"))
    print(json.dumps({"compile_s": r["compile_s"], "twice": r["compile_twice"]["kw_data_equal"] and r["compile_twice"]["audio_equal"], "counts": {k: r["counts"][k] for k in ("regions", "tiles", "cells", "launches", "deltas", "collapsed_frames")}}))


def stage_audit(params):
    c = corp.load(params)
    a = aud_mod.audit(c, params)
    # the three engagement arms under the new defaults (strip and counts), one corpus load
    arms = {}
    results = {}
    for name, sets in (("combined", {}), ("session", {"engagement_union": "session"}), ("time_window", {"engagement_union": "time_window"})):
        p = dict(params, **sets)
        c2, eps, tests, ng, launches, stats = L.run(p, c)
        arms[name] = {"counts": L.counts(launches, stats, p), "stats": {k: stats[k] for k in ("git_episodes", "git_tests", "nongit_tests", "git_tests_with_session")}}
        results[name] = [L.public_launch(l) for l in launches]
    a["arms"] = arms
    snap = common.parse_ts(c.as_of)
    clock = clk.Clock(params, snap)
    dens = strip.density(c, clock)
    out = {k: os.path.join(HERE, "strip-%s.png" % k) for k in ("combined", "time_window")}
    strip.render([("combined", results["combined"], "default arm: engagement_union = combined (session where observed, 12 h time window otherwise)"),
                  ("time_window", results["time_window"], "control arm: engagement_union = time_window (2 h chain, span cap 12 h)")],
                 clock, dens, out, os.path.join(HERE, "strip-compare.png"))
    a["strip_sha256"] = K.sha_tree(HERE, ["strip-combined.png", "strip-time_window.png", "strip-compare.png"])
    K.save(HERE, "nongit-audit.json", a)
    print(json.dumps({"thresholds": {k: {x: v[x] for x in ("launches", "files", "directories")} for k, v in a["thresholds"].items()}, "gate": a["gate"],
                      "arms": {k: {x: v["counts"][x] for x in ("launches", "launches_git", "launches_nongit", "single", "mirv", "unified")} for k, v in arms.items()}}))


def stage_verify(params):
    c = corp.load(params)
    rec, audio, path, clock, extra = K.build_piece(params, None, BUILD, corpus=c, write_audio=False)
    res = {"state": K.state_check(params, path, extra, rec)}
    cut = os.path.join(HERE, "build-cut")
    rc, a2, p2, cl2, ex2 = K.build_piece(params, 90, cut, corpus=c, write_audio=False)
    v = K.verify_page(p2)
    res["order_check_cut"], res["luminance_cut"] = v["order_check"], v["luminance"]
    res["checkpoints"] = {"every": 900, "count": rec["counts"]["checkpoints"], "deltas": rec["counts"]["deltas"], "touches": rec["counts"]["touches"]}
    K.save(HERE, "receipt-verify.json", res)
    print(json.dumps({"state": [(r["frame"], r["rel_err"]) for r in res["state"]["frames"]], "order": res["order_check_cut"]["equal"], "lum": res["luminance_cut"]["field_max_L"]}))


def stage_stills(params):
    c = corp.load(params)
    rec, audio, path, clock, extra = K.build_piece(params, None, BUILD, corpus=c, write_audio=False)
    coda = rec["clock"]["frames"] - int(round(clock.coda_s * clock.fps))
    dates = {"2026-03-15": K.frame_of(clock, "2026-03-15"), "2026-07-05": K.frame_of(clock, "2026-07-05"), "2026-09-28": K.frame_of(clock, "2026-09-28"),
             "final": coda + int(7 * clock.fps)}
    d = os.path.join(HERE, "stills")
    err = K.stills(path, d, list(dates.values()))
    for name, f in dates.items():
        os.replace(os.path.join(d, "f%05d.png" % f), os.path.join(d, name + ".png"))
    # alt final with a smaller tile area (k = 1) for the legibility verdict
    alt = dict(params, tile_area_k=1)
    ra, aa, pa, ca, ea = K.build_piece(alt, None, os.path.join(HERE, "build-alt"), corpus=c, write_audio=False)
    f = ra["clock"]["frames"] - int(round(ca.coda_s * ca.fps)) + int(7 * ca.fps)
    K.stills(pa, os.path.join(HERE, "build-alt", "stills"), [f])
    os.replace(os.path.join(HERE, "build-alt", "stills", "f%05d.png" % f), os.path.join(d, "final-tile_area_k1.png"))
    out = {"frames": dates, "page_errors": err, "alt_tile_area_k1": {"cells": ra["counts"]["cells"], "tiles": ra["counts"]["tiles"]}, "default_cells": rec["counts"]["cells"],
           "sha256": K.sha_tree(d, sorted(os.listdir(d)))}
    K.save(HERE, "receipt-stills.json", out)
    print(json.dumps(out)[:900])


if __name__ == "__main__":
    params = common.load_params()
    st = sys.argv[1]
    for s in (["build", "audit", "verify", "stills"] if st == "all" else [st]):
        globals()["stage_" + s](params)
