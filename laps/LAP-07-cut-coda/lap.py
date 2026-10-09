"""LAP-07 cut and coda. Stages: build stills cut full (or `all`). Exports run under nice; the full export is timed.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-07-cut-coda/lap.py <stage>
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
    fr = {"intro": 20, "coda-decay": c0 + int(ln * 1.5 / 18), "coda-pull": c0 + int(ln * 5 / 18), "coda-whole-world": c0 + int(ln * 8 / 18), "coda-card": c0 + int(ln * 14 / 18), "coda-black": F - 4}
    d = os.path.join(HERE, "stills")
    err = K.stills(path, d, list(fr.values()))
    for n, f in fr.items():
        os.replace(os.path.join(d, "f%05d.png" % f), os.path.join(d, n + ".png"))
    K.save(HERE, "receipt-stills.json", {"frames": fr, "coda_f": c0, "errors": err, "sha256": K.sha_tree(d, sorted(os.listdir(d)))})
    print(fr, err)


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
    for s in (["build", "stills", "cut", "full"] if sys.argv[1] == "all" else [sys.argv[1]]):
        globals()["stage_" + s](params)
