"""LAP-03 runner (thin slice). Stages: build verify cut excerpt full. Needs KW_CORPUS (the pinned merge).

    KW_CORPUS=$PWD/cache/corpus-pin-0653 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-03-thin-slice/lap.py <stage>
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "compile"))
sys.path.insert(0, os.path.join(ROOT, "export"))
import audio as aud
import build
import clock as clk
import common
import corpus as corp
import run as ex

PROBE_F = 15
NODE = {"PATH": os.environ["PATH"], "NODE_PATH": "/home/derek/work/founderOS/node_modules", "HOME": os.environ["HOME"]}


def rel(p):
    return os.path.relpath(p, os.path.join(ROOT, "render"))


def save(name, obj):
    json.dump(obj, open(os.path.join(HERE, name), "w"), indent=1, sort_keys=True)


def cli_hash(cut, out):
    r = subprocess.run(["nice", sys.executable, "-I", os.path.join(ROOT, "compile", "build_cli.py"), "--cut", str(cut), "--out", out, "--hash-only"],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def stage_build(params):
    out = {}
    for name, cut in (("full", None), ("cut", 90)):
        d = os.path.join(HERE, "build-" + name)
        rec, audio, path, clock, extra = build.build(params, cut_s=cut, outdir=d, probe_f=PROBE_F)
        aud.write_wav(os.path.join(d, "audio.wav"), audio)
        out[name] = build.strip_private(rec)
        # compile twice: a second process (hash seed randomised by -I) must give the same bytes
        h = cli_hash(cut or 0, os.path.join(HERE, ".twice-" + name))
        out[name]["compile_twice"] = {"kw_data_equal": h["kw_data_sha256"] == rec["kw_data_sha256"], "audio_equal": h["audio_sha256"] == rec["audio_sha256"],
                                      "second": h}
        for f in os.listdir(os.path.join(HERE, ".twice-" + name)):
            os.remove(os.path.join(HERE, ".twice-" + name, f))
        os.rmdir(os.path.join(HERE, ".twice-" + name))
        if name == "full":
            np.save(os.path.join(HERE, "build-full", "_extra_T.npy"), extra["T"])
    save("receipt-build.json", out)
    print(json.dumps({k: {"compile_s": v["compile_s"], "twice": v["compile_twice"]["kw_data_equal"] and v["compile_twice"]["audio_equal"], "audio_stats": v["audio_stats"], "frames": v["clock"]["frames"]} for k, v in out.items()}))


def stage_verify(params):
    res = {}
    # 1+3: order independence and luminance on the cut
    r = subprocess.run(["nice", "node", os.path.join(ROOT, "export", "verify.mjs"), "--data", rel(os.path.join(HERE, "build-cut", "kw-data.js"))],
                       capture_output=True, text=True, env=NODE, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    v = json.loads(r.stdout)
    res["order_check"], res["luminance"] = v["order_check"], v["luminance"]
    # 2: buildState under Node vs a Python brute-force sum, three frames of the full piece
    c = corp.load(params)
    snap = common.parse_ts(c.as_of)
    clock = clk.Clock(params, snap)
    rec, audio, path, _, extra = build.build(params, None, os.path.join(HERE, "build-full"), PROBE_F, corpus=c)
    nR, nG = rec["counts"]["regions"], len(rec["counts"]["nations"])
    frames = [int(clock.frame(np.array([common.parse_ts(t)]))[0]) for t in ("2026-04-20T12:00:00Z", "2026-07-20T12:00:00Z", "2026-09-30T12:00:00Z")]
    r = subprocess.run(["node", os.path.join(ROOT, "export", "state_node.mjs"), "--data", path, "--frames", ",".join(map(str, frames))],
                       capture_output=True, text=True, env=NODE, stdin=subprocess.DEVNULL)
    j = json.loads(r.stdout)
    T, R, G, W = extra["T"], extra["R"], extra["G"], extra["W"]
    fe = clock.frame(T)
    tau = clock.tau_frames()
    rows = []
    for f in frames:
        A = np.zeros(nR * nG)
        m = fe <= f
        d = 2.0 ** (-(tau[f] - tau[fe[m]]) / params["fog_half_life_days"])
        np.add.at(A, R[m] * nG + G[m], W[m] * d)
        n = np.array(j["state"][str(f)])
        rows.append({"frame": f, "max_abs_err": float(np.abs(A - n).max()), "max_A": float(A.max()), "rel_err": float(np.abs(A - n).max() / A.max()), "nonzero": int((A > 0).sum())})
    res["buildState_node_vs_python"] = {"node": j["node"], "frames": rows, "regions": nR, "groups": nG, "events": int(len(T))}
    save("receipt-verify.json", res)
    print(json.dumps(res)[:1500])


def exports(name, stage_params):
    pass


def stage_export(params, which):
    c = corp.load(params)
    snap = common.parse_ts(c.as_of)
    full = clk.Clock(params, snap)
    out = {}
    if which == "cut":
        d = os.path.join(HERE, "build-cut")
        audio = read_wav(os.path.join(d, "audio.wav"))
        out["cut"] = ex.run_export(os.path.join(d, "kw-data.js"), audio, 2700, 0, 2700, PROBE_F, os.path.join(HERE, "out", "cut"))
    elif which == "excerpt":
        f0 = int(full.frame(np.array([common.parse_ts("2026-07-05T00:00:00Z")]))[0])
        rec, audio, path, _, _ = build.build(params, None, os.path.join(HERE, "build-excerpt"), f0, corpus=c)
        out["excerpt"] = ex.run_export(path, audio, full.F, f0, f0 + 1800, f0, os.path.join(HERE, "out", "excerpt"))
        out["excerpt"]["f0"] = f0
    elif which == "full":
        d = os.path.join(HERE, "build-full")
        audio = read_wav(os.path.join(d, "audio.wav"))
        t = time.time()
        out["full"] = ex.run_export(os.path.join(d, "kw-data.js"), audio, full.F, 0, full.F, PROBE_F, os.path.join(HERE, "out", "full"))
        out["full"]["total_wall_s"] = round(time.time() - t, 1)
    save("receipt-export-%s.json" % which, out)
    print(json.dumps(out)[:1800])


def read_wav(path):
    b = open(path, "rb").read()
    return np.frombuffer(b, dtype="<f4", offset=44).reshape(-1, 2).copy()


if __name__ == "__main__":
    assert os.environ.get("KW_CORPUS"), "set KW_CORPUS to the pinned merge"
    params = common.load_params()
    st = sys.argv[1]
    if st == "build":
        stage_build(params)
    elif st == "verify":
        stage_verify(params)
    else:
        stage_export(params, st)
