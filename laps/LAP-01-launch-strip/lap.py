"""LAP-01 runner: both grouping arms, strips, compile-twice check, receipt.json. Counts only.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-01-launch-strip/lap.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "compile"))
import clock as clk
import common
import corpus as corp
import strip

ARMS = {
    "session": ["engagement_union=\"session\""],
    "time_window": ["engagement_union=\"time_window\"", "engagement_max_span_h=12"],
    "session_or_nation": ["engagement_union=\"session_or_nation\""],
}


def run_cli(outdir, sets):
    cmd = [sys.executable, "-I", os.path.join(ROOT, "compile", "launches.py"), "--out", outdir]
    for s in sets:
        cmd += ["--set", s]
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    r = subprocess.run(["nice"] + cmd, capture_output=True, text=True, env=env, cwd=ROOT, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout)


def main():
    receipt = {"lap": "LAP-01-launch-strip", "inputs": common.corpus_inputs(), "arms": {}}
    receipt["relations"] = "present" if receipt["inputs"]["relations.json"] else "absent"
    receipt["chatgpt_links"] = "present" if receipt["inputs"]["chatgpt_links.json"] else "absent"
    receipt["code"] = {f: common.sha256_file(os.path.join(ROOT, "compile", f)) for f in ("launches.py", "nations.py", "corpus.py", "names.py", "clock.py", "strip.py", "common.py", "params.json")}
    results = {}
    for arm, sets in ARMS.items():
        out = os.path.join(HERE, arm)
        a = run_cli(out, sets)
        b = run_cli(os.path.join(HERE, ".twice-" + arm), sets)
        same = (a["launches_sha256"], a["nations_sha256"]) == (b["launches_sha256"], b["nations_sha256"])
        a["compile_twice_identical"] = same
        for f in os.listdir(os.path.join(HERE, ".twice-" + arm)):
            os.remove(os.path.join(HERE, ".twice-" + arm, f))
        os.rmdir(os.path.join(HERE, ".twice-" + arm))
        receipt["arms"][arm] = a
        results[arm] = json.load(open(os.path.join(out, "launches.json")))
    params = common.load_params()
    snap = common.parse_ts(results["session"]["as_of"])
    clock = clk.Clock(params, snap)
    c = corp.load(params)
    dens = strip.density(c, clock)
    names = {"session": "default arm: engagement_union = session (shared joined session, activity join)",
             "time_window": "control arm: engagement_union = time_window (2 h chain, span cap 12 h; PROBE-00 rule)"}
    arms = [(k, results[k]["launches"], names[k]) for k in ("session", "time_window")]
    strip.render(arms, clock, dens, {k: os.path.join(HERE, f"strip-{k}.png") for k in ("session", "time_window")},
                 os.path.join(HERE, "strip-compare.png"))
    receipt["strip_sha256"] = {f: common.sha256_file(os.path.join(HERE, f)) for f in sorted(os.listdir(HERE)) if f.endswith(".png")}
    receipt["outputs"] = {f"{arm}/{n}": common.sha256_file(os.path.join(HERE, arm, n)) for arm in ARMS for n in ("launches.json", "nations.json")}
    receipt["clock"] = clock.summary()
    json.dump(receipt, open(os.path.join(HERE, "receipt.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps({a: {"twice": v["compile_twice_identical"], **{k: v["counts"][k] for k in ("launches", "single", "mirv", "unified")}} for a, v in receipt["arms"].items()}))


if __name__ == "__main__":
    main()
