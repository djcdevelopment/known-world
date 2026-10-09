"""compile/build_cli.py: build one piece (full or cut) to a directory. Prints hashes; `--hash-only` skips the WAV write.

    KW_CORPUS=<pinned merge> python -I compile/build_cli.py --cut 90|0 --out DIR [--probe 15] [--hash-only]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as aud
import build
import common

ap = argparse.ArgumentParser()
ap.add_argument("--cut", type=int, default=0)
ap.add_argument("--out", required=True)
ap.add_argument("--probe", type=int, default=15)
ap.add_argument("--hash-only", action="store_true")
ap.add_argument("--set", action="append", default=[])
a = ap.parse_args()
params = common.load_params(overrides=a.set)
rec, audio, path, clock, extra = build.build(params, cut_s=a.cut or None, outdir=a.out, probe_f=a.probe)
if not a.hash_only:
    aud.write_wav(os.path.join(a.out, "audio.wav"), audio)
r = build.strip_private(rec)
json.dump(r, open(os.path.join(a.out, "receipt.json"), "w"), indent=1, sort_keys=True)
print(json.dumps({"kw_data_sha256": r["kw_data_sha256"], "audio_sha256": r["audio_sha256"], "frames": r["clock"]["frames"]}))
