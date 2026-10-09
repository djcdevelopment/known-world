"""LAP-14 information architecture (zones, centred land, motion budget, player chrome, portrait). Stages:
build stills centre motion compat cut full (or `all`). Exports run under nice; the full export is timed. Every stage pins the corpus hashes
through the compile receipt.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-14-ia/lap.py <stage>
"""
import base64
import json
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "export"))
import numpy as np
import lapkit as K
import common
import camera as cam

FULL = os.path.join(HERE, "build-full")
CUT = os.path.join(HERE, "build-cut")
V4 = os.path.join(HERE, "build-v4")
STILLS = os.path.join(HERE, "stills")
SLICE10 = "0cbec7d"   # the slice-10 renderer (the last commit before this lap's code): the v4 compat check compares against it
DATES = {"2019-05": "2019-05-15", "2023-11": "2023-11-15", "2026-01-20": "2026-01-20", "2026-03-05": "2026-03-05", "2026-07-05": "2026-07-05",
         "2026-09-27": "2026-09-27", "2026-10-03": "2026-10-03"}


def _kw(path):
    t = open(path).read()
    return json.loads(t[len("window.KW_DATA="):].rstrip().rstrip(";"))


def _arr(kw, key, dt, shape=None):
    a = np.frombuffer(base64.b64decode(kw[key]), dtype=dt)
    return a.reshape(shape) if shape else a


def lane_stats(kw):
    """The horizontal stream's statistics from the compiled slot tables: slot constancy, order inversions, occupancy."""
    S = kw["stream"]
    K_ = S["K"]; F = kw["F"]
    sid = np.frombuffer(base64.b64decode(S["sid"]), dtype="u1").reshape(F, K_)
    sx = np.frombuffer(base64.b64decode(S["sx"]), dtype="<f4").reshape(F, K_)
    vis = sid != 255
    nvis = vis.sum(1)
    # slot constancy: a lane's slot never changes between consecutive frames in which it is visible in both
    moves = 0; prev = {}
    inv_frames = 0; inv_total = 0
    for f in range(F):
        cur = {}
        for k in range(K_):
            i = int(sid[f, k])
            if i == 255:
                break
            cur[i] = int(round(float(sx[f, k])))
        for i, sl in cur.items():
            if i in prev and prev[i] != sl:
                moves += 1
        items = sorted(cur.items(), key=lambda kv: kv[1])
        lanes_by_slot = [i for i, _ in items]
        n_inv = sum(1 for a in range(len(lanes_by_slot)) for b in range(a + 1, len(lanes_by_slot)) if lanes_by_slot[a] > lanes_by_slot[b])
        inv_total += n_inv; inv_frames += 1 if n_inv else 0
        prev = cur
    con = np.frombuffer(base64.b64decode(S["con"]), dtype="u1")
    adj_n = adj_d = 0   # lane-frames whose constellation has another visible lane: is a same-constellation lane in the next slot up or down?
    for f in range(0, F, 3):
        cur = {int(round(float(sx[f, k]))): int(sid[f, k]) for k in range(K_) if sid[f, k] != 255}
        for sl, i in cur.items():
            c = int(con[i])
            if c == 255 or not any(j != i and int(con[j]) == c for j in cur.values()):
                continue
            adj_d += 1
            if any(cur.get(sl + d) is not None and int(con[cur[sl + d]]) == c for d in (-1, 1)):
                adj_n += 1
    first_lane = int(np.argmax(nvis > 0)) if (nvis > 0).any() else None
    return {"slots": K_, "frames_with_lanes": int((nvis > 0).sum()), "first_lane_frame": first_lane, "max_concurrent": int(nvis.max()), "mean_visible_with_lanes": round(float(nvis[nvis > 0].mean()), 2),
            "frames_at_cap": int((nvis >= K_).sum()), "slot_moves_while_visible": moves, "frames_with_order_inversion": inv_frames, "inversions_total": inv_total,
            "mean_inversions_per_lane_frame": round(inv_total / max(1, int((nvis > 0).sum())), 3),
            "same_constellation_adjacent_share": round(adj_n / max(1, adj_d), 3), "same_constellation_lane_frames_sampled": adj_d}


def centring(kw, box, clock):
    cam_ = _arr(kw, "camera", "<f4").reshape(-1, 3)
    L = kw["layout"]["safe"]
    F = len(cam_)
    c0 = F - int(round(clock.coda_s * 30))
    dxa = ((box[:, 0] + box[:, 2]) / 2 - cam_[:, 0]) * cam_[:, 2]; dya = ((box[:, 1] + box[:, 3]) / 2 - cam_[:, 1]) * cam_[:, 2]
    dd = np.hypot(dxa, dya)[:c0]
    out = {"safe": L, "centre": [L[0] + L[2] / 2.0, L[1] + L[3] / 2.0], "dates": {},
           "story_frames_share_within": {"2px": round(float((dd <= 2).mean()), 4), "10px": round(float((dd <= 10).mean()), 4), "50px": round(float((dd <= 50).mean()), 4)}, "max_offset_px": round(float(dd.max()), 1)}
    for name in ("2019-05", "2023-11", "2026-01-20", "2026-03-05"):
        f = K.frame_of(clock, DATES[name])
        cx, cy, s = [float(v) for v in cam_[f]]
        b = box[f]
        dx, dy = ((b[0] + b[2]) / 2 - cx) * s, ((b[1] + b[3]) / 2 - cy) * s
        out["dates"][name] = {"frame": f, "scale_px_per_hex": round(s, 3), "box_world": [round(float(v), 2) for v in b], "box_px": [round((b[2] - b[0]) * s, 1), round((b[3] - b[1]) * s, 1)],
                              "offset_px": [round(dx, 2), round(dy, 2)], "within_2px": bool(abs(dx) <= 2 and abs(dy) <= 2)}
    return out


def stage_build(params):
    out = {}
    for name, cut, d in (("full", None, FULL), ("cut", 90, CUT)):
        rec, audio, path, clock, extra = K.build_piece(params, cut, d)
        box = cam.LAST_BOX.copy()
        r = K.build.strip_private(rec)
        r["compile_twice"] = K.compile_twice(rec, cut or 0, HERE, name)
        r["code"] = K.code_hashes()
        kw = _kw(path)
        r["lane_stats"] = lane_stats(kw)
        r["centring"] = centring(kw, box, extra["clock"])
        r["ia"] = kw["ia"]
        r["coast"] = kw["coast"]
        clock_ = extra["clock"]
        tau = clock_.tau_frames()
        r["marks_table"] = [{"kind": m["kind"], "frame": m["frame"], "date": K.build.common.iso(int((clock_.epoch0 + float(tau[m["frame"]])) * 86400))[:10], "label": m["label"]} for m in kw["marks"]]
        out[name] = r
    K.save(HERE, "receipt-build.json", out)
    print(json.dumps({k: {"compile_s": v["compile_s"], "twice": v["compile_twice"]["kw_data_equal"] and v["compile_twice"]["audio_equal"], "frames": v["clock"]["frames"],
                          "lanes": v["lane_stats"], "centring": v["centring"]["dates"], "events_sha": v["inputs"]["events.ndjson"]} for k, v in out.items()}, indent=1))


def _frames(clock, F):
    c0 = F - int(round(clock.coda_s * 30))
    ln = F - c0
    fr = {n: K.frame_of(clock, d) for n, d in DATES.items()}
    fr["tally-card"] = c0 + int(ln * 14 / 18)
    return fr


def _clock():
    rec, audio, path, clock, extra = K.build_piece(common.load_params(), None, FULL, write_audio=False)
    return rec, path, clock


def stage_stills(params):
    rec, path, clock = _clock()
    F = rec["clock"]["frames"]
    fr = _frames(clock, F)
    os.makedirs(STILLS, exist_ok=True)
    err = K.stills(path, STILLS, list(fr.values()))
    for n, f in fr.items():
        os.replace(os.path.join(STILLS, "f%05d.png" % f), os.path.join(STILLS, n + ".png"))
    rel = K.rel_render(path)
    perr = []
    for vw, vh in ((390, 844), (1080, 1920)):
        frames = [fr["2026-09-27"], fr["2023-11"]]
        cmd = ["node", os.path.join(ROOT, "export", "still.mjs"), "--data", rel, "--out", STILLS, "--frames", ",".join(map(str, frames)), "--vw", str(vw), "--vh", str(vh), "--prefix", "p%dx%d-" % (vw, vh)]
        r = subprocess.run(cmd, capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise SystemExit(r.stderr[-2000:])
        perr.append(json.loads(r.stdout.strip().splitlines()[-1]))
        for n, f in (("2026-09-27", fr["2026-09-27"]), ("2023-11", fr["2023-11"])):
            os.replace(os.path.join(STILLS, "p%dx%d-%05d.png" % (vw, vh, f)), os.path.join(STILLS, "portrait-%dx%d-%s.png" % (vw, vh, n)))
    # the portrait tally card, and the surfaces toggle (the old tallies) over the landscape map
    for vw, vh in ((390, 844),):
        r = subprocess.run(["node", os.path.join(ROOT, "export", "still.mjs"), "--data", rel, "--out", STILLS, "--frames", str(fr["tally-card"]), "--vw", str(vw), "--vh", str(vh), "--prefix", "pc-"],
                           capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
        os.replace(os.path.join(STILLS, "pc-%05d.png" % fr["tally-card"]), os.path.join(STILLS, "portrait-390x844-tally-card.png"))
    r = subprocess.run(["node", os.path.join(ROOT, "export", "still.mjs"), "--data", rel, "--out", STILLS, "--frames", str(fr["2026-09-27"]), "--vw", "390", "--vh", "844", "--ui", '{"lanes":true}', "--prefix", "pl-"],
                       capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
    os.replace(os.path.join(STILLS, "pl-%05d.png" % fr["2026-09-27"]), os.path.join(STILLS, "portrait-390x844-lanes-open-2026-09-27.png"))
    r = subprocess.run(["node", os.path.join(ROOT, "export", "still.mjs"), "--data", rel, "--out", STILLS, "--frames", str(fr["2026-09-27"]), "--ui", '{"surfaces":true}', "--prefix", "s-"],
                       capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
    os.replace(os.path.join(STILLS, "s-%05d.png" % fr["2026-09-27"]), os.path.join(STILLS, "surfaces-toggle-2026-09-27.png"))
    # 2026-04-27 (the date of the design system's reference render): one frame per export orientation, from the full piece and from the 90 s cut
    extra = {}
    recc, _a, pathc, clockc, _x = K.build_piece(params, 90, CUT, write_audio=False)
    for tag, dpath, clk in (("full", path, clock), ("cut", pathc, clockc)):
        f27 = K.frame_of(clk, "2026-04-27")
        extra[tag] = f27
        relp = K.rel_render(dpath)
        for name, args in (("landscape", []), ("portrait", ["--vw", "360", "--vh", "640", "--dsf", "3", "--query", "dpr=3"])):
            r = subprocess.run(["node", os.path.join(ROOT, "export", "still.mjs"), "--data", relp, "--out", STILLS, "--frames", str(f27), "--prefix", "x-"] + args,
                               capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
            if r.returncode:
                raise SystemExit(r.stderr[-2000:])
            os.replace(os.path.join(STILLS, "x-%05d.png" % f27), os.path.join(STILLS, "%s-%s-2026-04-27.png" % (name, tag)))
    fr["2026-04-27 (full, cut)"] = extra
    K.save(HERE, "receipt-stills.json", {"frames": fr, "errors": err, "portrait_errors": perr, "sha256": K.sha_tree(STILLS, sorted(os.listdir(STILLS)))})
    print(fr, err, perr)


def stage_centre(params):
    """Pixel check: the drawn land's bbox (the land layer alone) against the safe-area centre, and the compile's box offsets."""
    rec, path, clock = _clock()
    fr = {n: K.frame_of(clock, DATES[n]) for n in ("2019-05", "2023-11", "2026-01-20", "2026-03-05")}
    r = subprocess.run(["node", os.path.join(ROOT, "export", "landbox.mjs"), "--data", K.rel_render(path), "--frames", ",".join(map(str, fr.values()))],
                       capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    j = json.loads(r.stdout)
    j["frames"] = fr
    K.save(HERE, "receipt-centre.json", j)
    print(json.dumps(j))


def stage_motion(params):
    """Diff consecutive frames outside the map and timeline rects in 10 random seconds (seeded)."""
    rec, path, clock = _clock()
    F = rec["clock"]["frames"]
    kw = _kw(path)
    I = kw["ia"]
    c0 = F - int(round(clock.coda_s * 30))
    rng = random.Random(14)
    seconds = sorted(rng.sample(range(2, (c0 // 30) - 1), 10))
    starts = [s * 30 for s in seconds]
    nat_entry = [int(v) for v in np.frombuffer(base64.b64decode(kw["nat_entry_f"]), dtype="<i4")]
    r = subprocess.run(["nice", "node", os.path.join(ROOT, "export", "motion.mjs"), "--data", K.rel_render(path), "--starts", ",".join(map(str, starts)),
                        "--map", ",".join(map(str, I["map"])), "--timeline", ",".join(map(str, I["timeline"]))], capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    res = json.loads(r.stdout)
    for x in res:
        x["second"] = x["start"] // 30
        x["date"] = None
        x["near_nation_entry"] = any(x["start"] - 1 <= e <= x["start"] + 30 for e in nat_entry)
    out = {"seed": 14, "seconds": seconds, "map_rect": I["map"], "timeline_rect": I["timeline"], "results": res,
           "worst_max_share_excluding_entries": max([x["max_share"] for x in res if not x["near_nation_entry"]] or [0]),
           "worst_max_share_all": max(x["max_share"] for x in res)}
    K.save(HERE, "receipt-motion.json", out)
    print(json.dumps(out))


def stage_compat(params):
    """layout v4 must stay reachable and unchanged: compile with layout=v4 and hash 30 frames with the slice-10 renderer (git archive of SLICE10)
    and with the new page on the same data."""
    h = K.cli_build(0, V4, ["layout=v4"], hash_only=True)
    tmp = os.path.join(HERE, ".slice10")
    os.makedirs(tmp, exist_ok=True)
    subprocess.run("git archive %s render | tar -x -C %s" % (SLICE10, tmp), shell=True, cwd=ROOT, check=True)
    data = os.path.join(V4, "kw-data.js")
    F = _kw(data)["F"]
    frames = [int((i + 0.5) * F / 30) for i in range(30)]
    js = os.path.join(ROOT, "export", "hashpage.mjs")
    res = {}
    for name, url in (("slice10", "file://" + tmp + "/render/index.html?export=1&data=" + os.path.relpath(data, tmp + "/render")),
                      ("new_v4", "file://" + ROOT + "/render/index.html?export=1&data=" + K.rel_render(data))):
        r = subprocess.run(["node", js, "--url", url, "--frames", ",".join(map(str, frames))], capture_output=True, text=True, env=K.NODE_ENV, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise SystemExit(r.stderr[-2000:])
        res[name] = json.loads(r.stdout)
    eq = sum(1 for f in frames if res["slice10"][str(f)] == res["new_v4"][str(f)])
    out = {"slice10_commit": SLICE10, "v4_build": h, "frames": frames, "equal": eq, "hashes": res}
    K.save(HERE, "receipt-compat.json", out)
    subprocess.run(["rm", "-rf", tmp])
    print({"frames": len(frames), "equal": eq})


PORTRAIT_Q = "vw=360&vh=640&dpr=3"   # the design system's primary frame: laid out at 360 x 640 css, rendered at 3x = 1080 x 1920


def _export(name, d, query=None):
    audio = K.read_wav(os.path.join(d, "audio.wav"))
    F = len(audio) // 1600
    t = time.time()
    r = K.export_piece(os.path.join(d, "kw-data.js"), audio, F, 0, F, K.PROBE_F, os.path.join(HERE, "out", name), query=query)
    r["total_wall_s"] = round(time.time() - t, 1)
    r["query"] = query
    r["rehash"] = K.rehash(os.path.join(d, "kw-data.js"), os.path.join(HERE, "out", name), 0, F, query=query)
    K.save(HERE, "receipt-export-%s.json" % name, r)
    print(json.dumps({k: r[k] for k in ("frames", "frames_wall_s", "total_wall_s", "ms_per_frame_effective", "rehash", "final_bytes") if k in r}), r["probe"]["pass"], r["probe"]["delta_ms_onset"], r["page_errors"])


def stage_cut(params):
    _export("cut", CUT)


def stage_full(params):
    _export("full", FULL)


def stage_cutp(params):
    _export("cut-portrait", CUT, PORTRAIT_Q)


def stage_fullp(params):
    _export("full-portrait", FULL, PORTRAIT_Q)


if __name__ == "__main__":
    params = common.load_params()
    for s in (["build", "stills", "centre", "motion", "compat", "cut", "full", "cutp", "fullp"] if sys.argv[1] == "all" else [sys.argv[1]]):
        globals()["stage_" + s](params)
