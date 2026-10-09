"""LAP-06 radio and camera. Stages: build stills verify. PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-06-radio-camera/lap.py <stage>"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "export"))
import lapkit as K
import common
import numpy as np

BUILD = os.path.join(HERE, "build-full")


def pick(rows):
    m = [r for r in rows if r["shape"] == 1 and 5 <= len(r["whs"]) <= 9 and r["band"] >= 3]
    u = [r for r in rows if r["shape"] == 2 and r["conv"] and r["band"] >= 4]
    return (m[0] if m else [r for r in rows if r["shape"] == 1][0]), (u[0] if u else [r for r in rows if r["shape"] == 2][0])


def stage_build(params):
    rec, audio, path, clock, extra = K.build_piece(params, None, BUILD)
    r = K.build.strip_private(rec)
    r["compile_twice"] = K.compile_twice(rec, 0, HERE, "full")
    r["code"] = K.code_hashes()
    cam = extra["camera"]
    s = cam[:, 2]
    era = clock.era_frames()
    c0 = int(np.argmax(era == 2))
    r["camera_stats"] = {"scale_min": float(s.min()), "scale_max": float(s.max()), "scale_final_coda": float(s[-1]),
                         "era_c_scale_nonincreasing_until_coda": bool(np.all(np.diff(s[c0:rec["clock"]["frames"] - int(clock.coda_s * 30)]) <= 1e-6)),
                         "max_hex_px": params["max_hex_px"], "hex_px_at_era_c_start": float(s[c0]), "hex_px_before_coda": float(s[rec["clock"]["frames"] - int(clock.coda_s * 30) - 1])}
    # revealed tiles outside the view (non-ruin), per frame, sampled every 15 frames
    tf, w = extra["tfirst"], extra["world"]
    F = rec["clock"]["frames"]
    kind = np.array([extra["tiles"].regions[r_][2] for r_ in extra["tiles"].region])
    cx, cy = w.tile_x, w.tile_y
    out = 0; tot = 0
    for f in range(0, F - int(clock.coda_s * 30), 15):
        m = (tf <= f) & (kind != "third")
        if not m.any():
            continue
        sx = 920 + (cx[m] - cam[f, 0]) * cam[f, 2]; sy = 512 + (cy[m] - cam[f, 1]) * cam[f, 2]
        o = ((sx < 240) | (sx > 1600) | (sy < 64) | (sy > 960)).sum()
        out += int(o); tot += int(m.sum())
    r["camera_stats"]["revealed_tile_centres_outside_view_share_pct"] = round(100.0 * out / max(1, tot), 3)
    hq = extra["hq_host"]
    r["hq_crossing"] = {"first_omen_linux_frame": int(np.argmax(hq == extra["hq_hosts"].index("omen-linux"))), "hq_changes": rec["hq"]["changes"]}
    K.save(HERE, "receipt-build.json", r)
    print(json.dumps({"twice": r["compile_twice"]["kw_data_equal"] and r["compile_twice"]["audio_equal"], "camera": r["camera_stats"], "audio": r["audio_stats"], "hq": r["hq_crossing"]}))


def stage_stills(params):
    rec, audio, path, clock, extra = K.build_piece(params, None, BUILD, write_audio=False)
    frames = {"migration-2026-09-25": K.frame_of(clock, "2026-09-25"), "migration-2026-09-27": K.frame_of(clock, "2026-09-27"), "migration-2026-09-29": K.frame_of(clock, "2026-09-29"),
              "storm-2026-10-03": K.frame_of(clock, "2026-10-03"), "chatgpt-2025-06-01": K.frame_of(clock, "2025-06-01")}
    d = os.path.join(HERE, "stills")
    err = K.stills(path, d, list(frames.values()))
    for n, f in frames.items():
        os.replace(os.path.join(d, "f%05d.png" % f), os.path.join(d, n + ".png"))
    K.save(HERE, "receipt-stills.json", {"frames": frames, "errors": err, "sha256": K.sha_tree(d, sorted(os.listdir(d)))})
    print(frames, err)


def stage_verify(params):
    rec, audio, path, clock, extra = K.build_piece(params, 90, os.path.join(HERE, "build-cut"), write_audio=False)
    v = K.verify_page(path)
    K.save(HERE, "receipt-verify.json", {"order_check_cut": v["order_check"], "luminance_cut": v["luminance"]})
    print(v["order_check"]["equal"], v["luminance"]["field_max_L"], v["luminance"]["all_max_L"])


if __name__ == "__main__":
    params = common.load_params()
    for s in (["build", "stills", "verify"] if sys.argv[1] == "all" else [sys.argv[1]]):
        globals()["stage_" + s](params)
