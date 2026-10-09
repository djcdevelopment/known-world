"""LAP-11 running totals. Stages: build stills arms cut full (or `all`). Exports run under nice; the full export is timed.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-11-running-totals/lap.py <stage>
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
    fr = {"running-2023-08-01": K.frame_of(clock, "2023-08-01"), "running-2026-03-15": K.frame_of(clock, "2026-03-15"),
          "running-2026-07-05": K.frame_of(clock, "2026-07-05"), "running-2026-09-27": K.frame_of(clock, "2026-09-27"),
          "running-2026-10-03": K.frame_of(clock, "2026-10-03"), "tally-card": c0 + int(ln * 14 / 18)}
    d = os.path.join(HERE, "stills")
    err = K.stills(path, d, list(fr.values()))
    for n, f in fr.items():
        os.replace(os.path.join(d, "f%05d.png" % f), os.path.join(d, n + ".png"))
    K.save(HERE, "receipt-stills.json", {"frames": fr, "coda_f": c0, "errors": err, "sha256": K.sha_tree(d, sorted(os.listdir(d)))})
    print(fr, err)


def stage_arms(params):
    """Compile-only check of the two arms: rate_window rolling_10s and births_to_nation launch_window (hash-only, scratch dir)."""
    out = {}
    for name, sets in (("rolling_10s", ["rate_window=rolling_10s"]), ("launch_window", ["births_to_nation=launch_window"])):
        d = os.path.join(HERE, ".arm-" + name)
        out[name] = K.cli_build(0, d, sets)
        r = json.load(open(os.path.join(d, "receipt.json")))
        out[name]["running_totals_world"] = r["running_totals"]["world"]
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        os.rmdir(d)
    K.save(HERE, "receipt-arms.json", out)
    print(json.dumps(out))


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
