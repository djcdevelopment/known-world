"""LAP-12 the stream (HUD plates, tight start). Stages: build stills arms cut full (or `all`). Exports run under nice; the full export is timed.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-12-stream/lap.py <stage>
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "export"))
import lapkit as K
import common

FULL = os.path.join(HERE, "build-full")
CUT = os.path.join(HERE, "build-cut")


def stage_build(params):
    out = {}
    for name, cut, d in (("full", None, FULL), ("cut", 90, CUT)):
        rec, audio, path, clock, extra = K.build_piece(params, cut, d)
        r = K.build.strip_private(rec)
        r["compile_twice"] = K.compile_twice(rec, cut or 0, HERE, name)
        r["code"] = K.code_hashes()
        out[name] = r
        rows = extra["rows"]
        import numpy as np
        lf = np.array([x["f"] for x in rows])
        F = r["clock"]["frames"]
        per_s = np.convolve(np.bincount(lf, minlength=F), np.ones(30, dtype=int), "valid")
        out[name]["peak_launches_per_film_second"] = int(per_s.max())
        out[name]["collapsed_share_pct"] = round(100.0 * r["counts"]["collapsed_frames"] / F, 2)
    K.save(HERE, "receipt-build.json", out)
    print(json.dumps({k: {"compile_s": v["compile_s"], "twice": v["compile_twice"]["kw_data_equal"] and v["compile_twice"]["audio_equal"], "peak": v["peak_launches_per_film_second"],
                          "collapsed_pct": v["collapsed_share_pct"], "frames": v["clock"]["frames"], "env": v["clock"]["m"]} for k, v in out.items()}))


def stage_stills(params):
    rec, audio, path, clock, extra = K.build_piece(params, None, FULL, write_audio=False)
    F = rec["clock"]["frames"]
    c0 = F - int(round(clock.coda_s * 30))
    ln = F - c0
    fr = {"stream-2023-11": K.frame_of(clock, "2023-11-15"), "stream-2026-03-05": K.frame_of(clock, "2026-03-05"), "stream-2026-03-15": K.frame_of(clock, "2026-03-15"), "stream-2026-05-20": K.frame_of(clock, "2026-05-20"),
          "stream-2026-07-05": K.frame_of(clock, "2026-07-05"), "stream-2026-09-27": K.frame_of(clock, "2026-09-27"),
          "stream-2026-10-03": K.frame_of(clock, "2026-10-03"), "tally-card": c0 + int(ln * 14 / 18)}
    d = os.path.join(HERE, "stills")
    err = K.stills(path, d, list(fr.values()))
    for n, f in fr.items():
        os.replace(os.path.join(d, "f%05d.png" % f), os.path.join(d, n + ".png"))
    import subprocess
    # slide-in clip check: rows enter at 2026-09-27 (OpenCode) and at the first entries; nothing may land in the outer 8 px of the nation panel or tallies
    f0 = fr["stream-2026-09-27"]
    r = subprocess.run(["node", os.path.join(ROOT, "export", "edgecheck.mjs"), "--data", K.rel_render(path), "--frames", ",".join(str(f0 + k) for k in range(-6, 14, 2))],
                       capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
    edge = json.loads(r.stdout)
    K.save(HERE, "receipt-stills.json", {"frames": fr, "coda_f": c0, "errors": err, "edge_check": edge, "sha256": K.sha_tree(d, sorted(os.listdir(d)))})
    print(edge)
    print(fr, err)


def _kw(path):
    t = open(path).read()
    return json.loads(t[len("window.KW_DATA="):].rstrip().rstrip(";"))


def stage_arms(params):
    """Compile-only checks of the arms (scratch dir): rate_window rolling_10s, births_to_nation launch_window, and the
    stream_labels hashed arm, which must carry none of the lane names that the default arm carries."""
    out = {}
    names = _kw(os.path.join(FULL, "kw-data.js"))["stream"]["names"]
    for name, sets in (("rolling_10s", ["rate_window=rolling_10s"]), ("launch_window", ["births_to_nation=launch_window"]),
                       ("stream_hashed", ["stream_labels=hashed"])):
        d = os.path.join(HERE, ".arm-" + name)
        out[name] = K.cli_build(0, d, sets, hash_only=True)
        r = json.load(open(os.path.join(d, "receipt.json")))
        out[name]["running_totals_world"] = r["running_totals"]["world"]
        if name == "stream_hashed":
            blk = _kw(os.path.join(d, "kw-data.js"))
            txt = open(os.path.join(d, "kw-data.js")).read()
            out[name]["lane_names_in_file"] = sum(1 for n in set(names) if len(n) >= 3 and ('"' + n + '"') in txt)
            out[name]["label_sample_shape"] = [len(x) for x in blk["stream"]["names"][:3]]
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        os.rmdir(d)
    K.save(HERE, "receipt-arms.json", out)
    print(json.dumps(out))


def stage_perf(params):
    """Frame-time budget in Chromium: 40 blocks of 30 consecutive frames, with and without the stream layer (forced raster flush)."""
    import subprocess
    res = {}
    for name, d in (("full", FULL), ("cut", CUT)):
        r = subprocess.run(["nice", "node", os.path.join(ROOT, "export", "perf.mjs"), "--data", K.rel_render(os.path.join(d, "kw-data.js"))],
                           capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise SystemExit(r.stderr[-2000:])
        res[name] = json.loads(r.stdout)
    K.save(HERE, "receipt-perf.json", res)
    print(json.dumps(res))


def stage_cut(params):
    audio = K.read_wav(os.path.join(CUT, "audio.wav"))
    t = time.time()
    r = K.export_piece(os.path.join(CUT, "kw-data.js"), audio, 2700, 0, 2700, K.PROBE_F, os.path.join(HERE, "out", "cut"))
    r["total_wall_s"] = round(time.time() - t, 1)
    r["rehash"] = K.rehash(os.path.join(CUT, "kw-data.js"), os.path.join(HERE, "out", "cut"), 0, 2700)
    K.save(HERE, "receipt-export-cut.json", r)
    print(json.dumps({k: r[k] for k in ("frames", "frames_wall_s", "total_wall_s", "ms_per_frame_effective", "rehash")}), r["probe"]["pass"], r["probe"]["delta_ms_onset"], r["page_errors"])


def stage_full(params):
    audio = K.read_wav(os.path.join(FULL, "audio.wav"))
    F = len(audio) // 1600
    t = time.time()
    r = K.export_piece(os.path.join(FULL, "kw-data.js"), audio, F, 0, F, K.PROBE_F, os.path.join(HERE, "out", "full"))
    r["total_wall_s"] = round(time.time() - t, 1)
    r["rehash"] = K.rehash(os.path.join(FULL, "kw-data.js"), os.path.join(HERE, "out", "full"), 0, F)
    K.save(HERE, "receipt-export-full.json", r)
    print(json.dumps({k: r[k] for k in ("frames", "frames_wall_s", "total_wall_s", "ms_per_frame_effective", "rehash", "final_bytes")}), r["probe"]["pass"], r["probe"]["delta_ms_onset"], r["page_errors"])


if __name__ == "__main__":
    params = common.load_params()
    for s in (["build", "stills", "arms", "cut", "full"] if sys.argv[1] == "all" else [sys.argv[1]]):
        globals()["stage_" + s](params)
