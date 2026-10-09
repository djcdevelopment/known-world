"""LAP-02 runner: clock tables, 10 s probe export, 90 s cut (ticker only) rendered twice.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-02-clock-sync/lap.py [probe10|cut|all]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "compile"))
sys.path.insert(0, os.path.join(ROOT, "export"))
import audio as aud
import build_data as bd
import clock as clk
import common
import run as ex

PROBE_F = 15


def main(which):
    params = common.load_params()
    ph = common.params_hash(params)
    snap = common.parse_ts(json.load(open(os.path.join(common.MERGED, "repos.json")))["as_of"])
    full = clk.Clock(params, snap)
    cut = clk.Clock(params, snap, cut_s=90)
    rec = {"params_hash": ph, "full_clock": full.summary(), "cut_clock": cut.summary(), "inputs": {"repos.json": common.sha256_file(os.path.join(common.MERGED, "repos.json"))}}
    rec["code"] = {f: common.sha256_file(os.path.join(ROOT, f)) for f in ("compile/clock.py", "compile/audio.py", "compile/build_data.py", "render/index.html", "render/data.js", "render/border.js", "render/main.js", "export/frames.mjs", "export/encode.py", "export/probe.py", "export/run.py")}
    rec["tables"] = {"full_tau_sha256": common.sha256_bytes(full.tau_frames().astype("<f8").tobytes()),
                     "cut_tau_sha256": common.sha256_bytes(cut.tau_frames().astype("<f8").tobytes())}
    rec["rate_labels_full"], rec["rate_labels_cut"] = full.rate_labels(), cut.rate_labels()
    rec["data"] = {}
    rec["data"]["full"] = bd.write_data_js(os.path.join(HERE, "kw-data-full.js"), bd.clock_block(full, PROBE_F))
    rec["data"]["cut"] = bd.write_data_js(os.path.join(HERE, "kw-data-cut.js"), bd.clock_block(cut, PROBE_F))
    wav_full = aud.render_skeleton(full.F, 30, seed=20261009, probe_f=PROBE_F)
    wav_cut = aud.render_skeleton(cut.F, 30, seed=20261009, probe_f=PROBE_F)
    rec["audio"] = {"full_samples": int(len(wav_full)), "full_expected": full.F * 1600, "cut_samples": int(len(wav_cut)), "cut_expected": cut.F * 1600,
                    "full_sha256": common.sha256_bytes(aud.wav_bytes(wav_full)), "cut_sha256": common.sha256_bytes(aud.wav_bytes(wav_cut))}
    out = os.path.join(HERE, "out")
    if which in ("probe10", "all"):
        rec["probe10"] = ex.run_export(os.path.join(HERE, "kw-data-full.js"), wav_full, full.F, 0, 300, PROBE_F, os.path.join(out, "probe10"))
    if which in ("cut", "all"):
        a = ex.run_export(os.path.join(HERE, "kw-data-cut.js"), wav_cut, cut.F, 0, cut.F, PROBE_F, os.path.join(out, "cut-a"))
        b = ex.run_export(os.path.join(HERE, "kw-data-cut.js"), wav_cut, cut.F, 0, cut.F, PROBE_F, os.path.join(out, "cut-b"))
        rec["cut_a"], rec["cut_b"] = a, b
        rec["cut_frame_hashes_equal"] = a["frame_hashes_sha256"] == b["frame_hashes_sha256"]
    path = os.path.join(HERE, "receipt-%s.json" % which)
    json.dump(rec, open(path, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in rec if k.startswith("probe10") or k.endswith("equal")}, indent=1)[:3000])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "probe10")
