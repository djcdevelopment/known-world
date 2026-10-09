"""export/lapkit.py: shared lap helpers (build, compile twice, stills, receipts, exports, measures, frame grids).

Every lap runs from the repo root:  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-NN-name/lap.py <stage>
The corpus is corpus/merged read directly; its hashes are pinned in every receipt (common.corpus_inputs()).
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "compile"))
sys.path.insert(0, os.path.join(ROOT, "export"))
import audio as aud
import build
import clock as clk
import common
import corpus as corp
import run as ex

NODE_ENV = {"PATH": os.environ["PATH"], "NODE_PATH": "/home/derek/work/founderOS/node_modules", "HOME": os.environ["HOME"]}
PROBE_F = 15
SNAP_NOTE = "corpus/merged read directly"


def rel_render(p):
    return os.path.relpath(p, os.path.join(ROOT, "render"))


def save(here, name, obj):
    json.dump(obj, open(os.path.join(here, name), "w"), indent=1, sort_keys=True)


def code_hashes():
    out = {}
    for d, exts in (("compile", (".py", ".json")), ("render", (".js", ".html")), ("export", (".py", ".mjs"))):
        for f in sorted(os.listdir(os.path.join(ROOT, d))):
            if f.endswith(exts):
                out[d + "/" + f] = common.sha256_file(os.path.join(ROOT, d, f))
    return out


def read_wav(path):
    b = open(path, "rb").read()
    return np.frombuffer(b, dtype="<f4", offset=44).reshape(-1, 2).copy()


def frame_of(clock, date):
    return int(clock.frame(np.array([common.parse_ts(date if "T" in date else date + "T12:00:00Z")]))[0])


def build_piece(params, cut, outdir, probe_f=PROBE_F, write_audio=True, corpus=None):
    rec, audio, path, clock, extra = build.build(params, cut_s=cut, outdir=outdir, probe_f=probe_f, corpus=corpus)
    if write_audio:
        aud.write_wav(os.path.join(outdir, "audio.wav"), audio)
    return rec, audio, path, clock, extra


def cli_build(cut, out, sets=(), hash_only=True):
    cmd = ["nice", sys.executable, "-I", os.path.join(ROOT, "compile", "build_cli.py"), "--cut", str(cut), "--out", out]
    if hash_only:
        cmd.append("--hash-only")
    for s in sets:
        cmd += ["--set", s]
    r = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def compile_twice(rec, cut, here, tag, sets=()):
    d = os.path.join(here, ".twice-" + tag)
    h = cli_build(cut, d, sets)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    os.rmdir(d)
    return {"kw_data_equal": h["kw_data_sha256"] == rec["kw_data_sha256"], "audio_equal": h["audio_sha256"] == rec["audio_sha256"], "second": h}


def stills(datajs, outdir, frames):
    os.makedirs(outdir, exist_ok=True)
    r = subprocess.run(["node", os.path.join(ROOT, "export", "still.mjs"), "--data", rel_render(datajs), "--out", outdir, "--frames", ",".join(map(str, frames))],
                       capture_output=True, text=True, env=NODE_ENV, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def verify_page(datajs, state_frames=()):
    r = subprocess.run(["nice", "node", os.path.join(ROOT, "export", "verify.mjs"), "--data", rel_render(datajs), "--state", ",".join(map(str, state_frames))],
                       capture_output=True, text=True, env=NODE_ENV, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout)


def state_check(params, datajs, extra, rec, dates=("2026-04-20", "2026-07-20", "2026-09-30")):
    """buildState under Node (vm sandbox) vs a Python brute-force sum over every raw touch, three frames."""
    clock = extra["clock"]
    nT, nG = extra["nT"], len(extra["nat_index"])
    frames = [frame_of(clock, d) for d in dates]
    r = subprocess.run(["node", os.path.join(ROOT, "export", "state_node.mjs"), "--data", datajs, "--frames", ",".join(map(str, frames))],
                       capture_output=True, text=True, env=NODE_ENV, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    j = json.loads(r.stdout)
    T, R, G, W = extra["T"], extra["R"], extra["G"], extra["W"]
    fe = clock.frame(T)
    tau = clock.tau_frames()
    rows = []
    for f in frames:
        A = np.zeros(nT * nG)
        m = fe <= f
        d = 2.0 ** (-(tau[f] - tau[fe[m]]) / params["fog_half_life_days"])
        np.add.at(A, R[m] * nG + G[m], W[m] * d)
        n = np.array(j["state"][str(f)])
        rows.append({"frame": f, "max_abs_err": float(np.abs(A - n).max()), "max_A": float(A.max()), "rel_err": float(np.abs(A - n).max() / A.max()),
                     "nonzero": int((A > 0).sum()), "checkpoint_frame": (f // 900) * 900})
    return {"node": j["node"], "frames": rows, "tiles": nT, "groups": nG, "events": int(len(T)), "checkpoint_every": 900}


def export_piece(datajs, audio, F_total, f0, f1, probe_f, outdir, workers=10, query=None):
    return ex.run_export(datajs, audio, F_total, f0, f1, probe_f, outdir, workers=workers, query=query)


def montage(frames_dir, frames, out_png, cols=6, rows=4, thumb=(480, 270)):
    """4 x 6 grid of stills (PIL), labelled with the frame number."""
    from PIL import Image, ImageDraw
    W, H = thumb
    img = Image.new("RGB", (cols * W, rows * H), (7, 9, 14))
    d = ImageDraw.Draw(img)
    for i, f in enumerate(frames[: cols * rows]):
        p = os.path.join(frames_dir, "f%05d.png" % f)
        im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
        x, y = (i % cols) * W, (i // cols) * H
        img.paste(im, (x, y))
        d.text((x + 6, y + H - 16), "f%d" % f, fill=(200, 200, 160))
    img.save(out_png)


def sha_tree(here, names):
    return {n: common.sha256_file(os.path.join(here, n)) for n in names if os.path.exists(os.path.join(here, n))}


def rehash(datajs, outdir, f0, f1, n=30, query=None):
    """Re-render n frames of an export in a fresh Chromium (reverse order) and compare with the export's per-frame hashes."""
    hs = {}
    for line in open(os.path.join(outdir, "frame-hashes.txt")):
        if line.strip():
            f, h = line.split()
            hs[int(f)] = h
    frames = [f0 + int((i + 0.5) * (f1 - f0) / n) for i in range(n)]
    r = subprocess.run(["node", os.path.join(ROOT, "export", "rehash.mjs"), "--data", rel_render(datajs), "--frames", ",".join(map(str, frames))] + (["--query", query] if query else []),
                       capture_output=True, text=True, env=NODE_ENV, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    got = json.loads(r.stdout)
    eq = sum(1 for f in frames if got[str(f)] == hs[f])
    return {"frames": n, "equal": eq, "mismatched": [f for f in frames if got[str(f)] != hs[f]]}
