"""export/run.py: one export end to end. frames.mjs -> concat -> AAC mux -> alignment probe -> receipt.json.

run_export(data_js, audio, F_total, f0, f1, probe_f, outdir, workers) where `audio` is the full-length stereo float32
array (F_total * 1,600 samples); the excerpt [f0, f1) is cut from it at frame boundaries.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "compile"))
sys.path.insert(0, os.path.join(ROOT, "export"))
import audio as aud
import common
import encode
import probe as probe_mod

NODE_PATH = "/home/derek/work/founderOS/node_modules"


def run_export(data_js, audio, F_total, f0, f1, probe_f, outdir, workers=10, query=None, fps=30):
    os.makedirs(outdir, exist_ok=True)
    spf = aud.spf(fps)
    wav = os.path.join(outdir, "audio.wav")
    seg = audio[f0 * spf:f1 * spf]
    aud.write_wav(wav, seg)
    env = {"PATH": os.environ["PATH"], "NODE_PATH": NODE_PATH, "FFMPEG": encode.FFMPEG, "HOME": os.environ["HOME"]}
    rel = os.path.relpath(data_js, os.path.join(ROOT, "render"))
    cmd = ["nice", "node", os.path.join(ROOT, "export", "frames.mjs"), "--data", rel, "--out", outdir, "--from", str(f0), "--to", str(f1),
           "--workers", str(workers)]
    if query:
        cmd += ["--query", query]
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-3000:] + r.stdout[-1000:])
    wall = time.time() - t
    final = os.path.join(outdir, "final.mp4")
    encode.encode(outdir, wav, final)
    pr = probe_mod.probe(final, f1 - f0, fps, f0, probe_f)
    timing = json.load(open(os.path.join(outdir, "timing.json")))
    hashes = []
    for fn in sorted(os.listdir(os.path.join(outdir, "hashes"))):
        hashes += open(os.path.join(outdir, "hashes", fn)).read().split("\n")
    hashes = [h for h in hashes if h]
    allh = common.sha256_bytes("\n".join(hashes).encode())
    rec = {"frames": f1 - f0, "from": f0, "to": f1, "workers": workers, "frames_wall_s": round(wall, 2),
           "ms_per_frame_effective": round(timing["ms_per_frame_effective"], 2), "frame_hashes_sha256": allh,
           "wav_sha256": common.sha256_file(wav), "probe": pr, "page_errors": timing["errors"],
           "capture_ms_per_frame_per_worker_median": sorted(s["capture_ms_per_frame"] for s in timing["per_segment"])[len(timing["per_segment"]) // 2] if timing["per_segment"] else None,
           "final_bytes": os.path.getsize(final)}
    json.dump(rec, open(os.path.join(outdir, "receipt.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(outdir, "frame-hashes.txt"), "w").write("\n".join(hashes) + "\n")
    return rec
