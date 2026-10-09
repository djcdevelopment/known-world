"""LAP-13 the player (camera steering, marks, the player page, portrait). Stages: build stills arms compat cut full (or `all`).
Exports run under nice; the full export is timed. Every stage pins the corpus hashes through the compile receipt.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-13-player/lap.py <stage>
"""
import base64
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "export"))
import numpy as np
import lapkit as K
import common

FULL = os.path.join(HERE, "build-full")
CUT = os.path.join(HERE, "build-cut")
STILLS = os.path.join(HERE, "stills")
SLICE9 = "0054343"   # the last commit before this lap: the slice-9 renderer the compat check compares against
KEY = {"f0": 0, "f394": 394, "f543": 543}


def _kw(path):
    t = open(path).read()
    return json.loads(t[len("window.KW_DATA="):].rstrip().rstrip(";"))


def _cam(kw):
    a = np.frombuffer(base64.b64decode(kw["camera"]), dtype="<f4").reshape(-1, 3)
    return a


def cam_numbers(cam, fps=30):
    s = cam[:, 2].astype(np.float64)
    s0 = float(s[0])

    def first_below(frac):
        k = np.nonzero(s < frac * s0)[0]
        return int(k[0]) if len(k) else None

    out = {"scale_f0": round(s0, 2), "scale_f394": round(float(s[394]), 2), "scale_f543": round(float(s[543]), 2), "scale_end": round(float(s[-1]), 2),
           "frames": int(len(s))}
    for name, frac in (("tight_start_90pct", 0.9), ("tight_start_50pct", 0.5), ("tight_start_25pct", 0.25)):
        k = first_below(frac)
        out[name + "_frame"] = k
        out[name + "_s"] = None if k is None else round(k / fps, 2)
    return out


def stage_build(params):
    out = {}
    for name, cut, d in (("full", None, FULL), ("cut", 90, CUT)):
        rec, audio, path, clock, extra = K.build_piece(params, cut, d)
        r = K.build.strip_private(rec)
        r["compile_twice"] = K.compile_twice(rec, cut or 0, HERE, name)
        r["code"] = K.code_hashes()
        kw = _kw(path)
        r["camera_numbers"] = cam_numbers(_cam(kw))
        # marks with their dates (the RESULT table)
        clock_ = extra["clock"]
        tau = clock_.tau_frames()
        r["marks_table"] = [{"kind": m["kind"], "frame": m["frame"], "date": K.build.common.iso(int((clock_.epoch0 + float(tau[m["frame"]])) * 86400))[:10], "label": m["label"]} for m in kw["marks"]]
        out[name] = r
    K.save(HERE, "receipt-build.json", out)
    print(json.dumps({k: {"compile_s": v["compile_s"], "twice": v["compile_twice"]["kw_data_equal"] and v["compile_twice"]["audio_equal"], "frames": v["clock"]["frames"],
                          "marks": v["marks_counts"], "camera": v["camera_numbers"], "events_sha": v["inputs"]["events.ndjson"]} for k, v in out.items()}, indent=1))


def _stills_set(clock, F):
    c0 = F - int(round(clock.coda_s * 30))
    ln = F - c0
    fr = {}
    for n, d in (("2023-11", "2023-11-15"), ("2024-06", "2024-06-15"), ("2026-01-20", "2026-01-20"), ("2026-03-05", "2026-03-05"), ("2026-03-15", "2026-03-15"),
                 ("2026-07-05", "2026-07-05"), ("2026-09-27", "2026-09-27")):
        fr[n] = K.frame_of(clock, d)
    fr["tally-card"] = c0 + int(ln * 14 / 18)
    return fr


def stage_stills(params):
    rec, audio, path, clock, extra = K.build_piece(params, None, FULL, write_audio=False)
    F = rec["clock"]["frames"]
    fr = _stills_set(clock, F)
    os.makedirs(STILLS, exist_ok=True)
    err = K.stills(path, STILLS, list(fr.values()))
    for n, f in fr.items():
        os.replace(os.path.join(STILLS, "f%05d.png" % f), os.path.join(STILLS, n + ".png"))
    # portrait stills (390 x 844 and 1080 x 1920), plus the expanded nations and surfaces at 390 x 844
    rel = K.rel_render(path)
    pf = {"2023-11": fr["2023-11"], "2026-07-05": fr["2026-07-05"], "2026-09-27": fr["2026-09-27"], "tally-card": fr["tally-card"]}
    perr = []
    for vw, vh in ((390, 844), (1080, 1920)):
        for ui, tag in ((None, ""), ('{"nations":true}', "-nations"), ('{"surfaces":true}', "-surfaces")):
            if ui and vw != 390:
                continue
            frames = list(pf.values()) if not ui else [pf["2026-09-27"]]
            cmd = ["node", os.path.join(ROOT, "export", "still.mjs"), "--data", rel, "--out", STILLS, "--frames", ",".join(map(str, frames)), "--vw", str(vw), "--vh", str(vh),
                   "--prefix", "p%dx%d%s-" % (vw, vh, tag)]
            if ui:
                cmd += ["--ui", ui]
            r = subprocess.run(cmd, capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
            if r.returncode:
                raise SystemExit(r.stderr[-2000:])
            perr.append(json.loads(r.stdout.strip().splitlines()[-1]))
            for n, f in pf.items():
                p = os.path.join(STILLS, "p%dx%d%s-%05d.png" % (vw, vh, tag, f))
                if os.path.exists(p):
                    os.replace(p, os.path.join(STILLS, "portrait-%dx%d%s-%s.png" % (vw, vh, tag, n)))
    K.save(HERE, "receipt-stills.json", {"frames": fr, "errors": err, "portrait_errors": perr, "sha256": K.sha_tree(STILLS, sorted(os.listdir(STILLS)))})
    print(fr, err, perr)


def _arm(args):
    name, sets = args
    d = os.path.join(HERE, ".arm-" + name)
    h = K.cli_build(0, d, sets, hash_only=True)
    kw = _kw(os.path.join(d, "kw-data.js"))
    r = json.load(open(os.path.join(d, "receipt.json")))
    res = {"sets": list(sets), "kw_data_sha256": h["kw_data_sha256"], "camera_numbers": cam_numbers(_cam(kw)), "marks_counts": r.get("marks_counts"), "camera_report": r.get("camera")}
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    os.rmdir(d)
    return name, res


def stage_arms(params):
    """Compile-only arms: the slice-9 steering (every revealed tile), a weightier threshold, the literal per-era slope unit, a stricter burst."""
    arms = [("revealed_all", ["camera_steer=revealed"]), ("weight_min_6", ["camera_tile_weight_min=6.0"]), ("launch_none", ["camera_launch_steer=none"]),
            ("slope_unit_era", ["marks_slope_unit=era"]), ("slope_threshold_0.25_era", ["marks_slope_unit=era", "marks_slope_threshold=0.25"])]
    out = {}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for name, res in ex.map(_arm, arms):
            out[name] = res
    K.save(HERE, "receipt-arms.json", out)
    print(json.dumps({k: {"cam": v["camera_numbers"], "marks": v["marks_counts"]} for k, v in out.items()}, indent=1))


def stage_compat(params):
    """At 1920 x 1080 the viewport-aware renderer must hash equal to the slice-9 renderer (git archive of SLICE9) on the same data:
    the same 30 frames, the new page in `compat=slice9` mode (no hashmark hairline, the old stream header)."""
    import tempfile
    tmp = os.path.join(HERE, ".slice9")
    os.makedirs(tmp, exist_ok=True)
    subprocess.run("git archive %s render | tar -x -C %s" % (SLICE9, tmp), shell=True, cwd=ROOT, check=True)
    # the old page lives in .slice9/render; it reads the new data file through a relative path
    data = os.path.join(FULL, "kw-data.js")
    F = _kw(data)["F"]
    frames = [int((i + 0.5) * F / 30) for i in range(30)]
    js = os.path.join(ROOT, "export", "hashpage.mjs")
    res = {}
    for name, url in (("slice9", "file://" + tmp + "/render/index.html?export=1&data=" + os.path.relpath(data, tmp + "/render")),
                      ("new_compat", "file://" + ROOT + "/render/index.html?export=1&compat=slice9&data=" + K.rel_render(data)),
                      ("new_default", "file://" + ROOT + "/render/index.html?export=1&data=" + K.rel_render(data))):
        r = subprocess.run(["node", js, "--url", url, "--frames", ",".join(map(str, frames))], capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise SystemExit(r.stderr[-2000:])
        res[name] = json.loads(r.stdout)
    eq = sum(1 for f in frames if res["slice9"][str(f)] == res["new_compat"][str(f)])
    eq_def = sum(1 for f in frames if res["slice9"][str(f)] == res["new_default"][str(f)])
    out = {"slice9_commit": SLICE9, "frames": frames, "equal_slice9_vs_new_compat": eq, "equal_slice9_vs_new_default": eq_def, "hashes": res}
    K.save(HERE, "receipt-compat.json", out)
    for f in os.listdir(tmp + "/render"):
        pass
    subprocess.run(["rm", "-rf", tmp])
    print({"frames": len(frames), "compat_equal": eq, "default_equal": eq_def})


def stage_cut(params):
    audio = K.read_wav(os.path.join(CUT, "audio.wav"))
    F = len(audio) // 1600
    t = time.time()
    r = K.export_piece(os.path.join(CUT, "kw-data.js"), audio, F, 0, F, K.PROBE_F, os.path.join(HERE, "out", "cut"))
    r["total_wall_s"] = round(time.time() - t, 1)
    r["rehash"] = K.rehash(os.path.join(CUT, "kw-data.js"), os.path.join(HERE, "out", "cut"), 0, F)
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
    for s in (["build", "stills", "arms", "compat", "cut", "full"] if sys.argv[1] == "all" else [sys.argv[1]]):
        globals()["stage_" + s](params)
