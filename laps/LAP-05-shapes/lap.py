"""LAP-05 shapes. Stages: build stills verify. PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-05-shapes/lap.py <stage>"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "export"))
import lapkit as K
import common

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
    mirv, uni = pick(extra["rows"])
    r["picked"] = {"mirv": {"f": mirv["f"], "warheads": len(mirv["whs"]), "band": mirv["band"], "nation": mirv["nat"], "land": [w[0] for w in mirv["whs"]]},
                   "unified": {"f": uni["f"], "sources": len(uni["conv"]), "band": uni["band"], "nation": uni["nat"]}}
    rows = extra["rows"]
    r["shapes"] = {"mirv_launches": sum(1 for x in rows if x["shape"] == 1), "unified": sum(1 for x in rows if x["shape"] == 2),
                   "inferred": sum(1 for x in rows if x["inferred"]), "warheads_total": sum(len(x["whs"]) for x in rows),
                   "warheads_on_spurs": sum(1 for x in rows for w in x["whs"] if w[5] == 1), "unified_with_sources": sum(1 for x in rows if x["shape"] == 2 and x["conv"])}
    K.save(HERE, "receipt-build.json", r)
    print(json.dumps({"twice": r["compile_twice"]["kw_data_equal"] and r["compile_twice"]["audio_equal"], "picked": r["picked"], "shapes": r["shapes"], "audio": r["audio_stats"]}))


def stage_stills(params):
    r = json.load(open(os.path.join(HERE, "receipt-build.json")))
    pm, pu = r["picked"]["mirv"], r["picked"]["unified"]
    B = r["clock"]["frames"]
    rec, audio, path, clock, extra = K.build_piece(params, None, BUILD, write_audio=False)
    import numpy as np
    bf = max(3, int(round(params["beam_s"] * 30)))
    cf = max(3, int(round(params["unify_converge_s"] * 30)))
    last = max(pm["land"])
    frames = {"mirv-a": pm["f"] + 3, "mirv-b": pm["f"] + int(bf * 0.6) + 4, "mirv-c": last + 4,
              "unified-a": pu["f"] - cf + 4, "unified-b": pu["f"] - 2, "unified-c": pu["f"] + 4}
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
