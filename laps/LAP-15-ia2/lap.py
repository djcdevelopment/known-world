"""LAP-15 information architecture 2 (single era from 2026-01-01, constellations, host evidence, panel geometry, short score, causal camera and marks,
future-leak verifier). Stages (run from the repo root, `all` runs the build-to-export chain):

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I laps/LAP-15-ia2/lap.py <stage>

step checks: check-a ... check-g (each a small receipt run under `ct receipt`); lap stages: build stills leak panel motion score cut full cutp fullp public.
"""
import base64
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "export"))
import numpy as np
import lapkit as K
import common

FULL = os.path.join(HERE, "build-full")
CUT = os.path.join(HERE, "build-cut")
PUB = os.path.join(HERE, "build-public")
STILLS = os.path.join(HERE, "stills")
PORTRAIT_Q = "vw=360&vh=640&dpr=3"


def _kw(path):
    t = open(path).read()
    return json.loads(t[len("window.KW_DATA="):].rstrip().rstrip(";"))


def _arr(kw, key, dt):
    return np.frombuffer(base64.b64decode(kw[key]), dtype=dt)


def check_a(params):
    """Step A: one era from start_date; the prologue tallies earlier evidence; the compile is byte-identical twice; nothing is dated before the start."""
    h1 = K.cli_build(90, CUT, [], hash_only=True)
    h2 = K.cli_build(90, os.path.join(HERE, ".twice-a"), [], hash_only=True)
    subprocess.run(["rm", "-rf", os.path.join(HERE, ".twice-a")])
    kw = _kw(os.path.join(CUT, "kw-data.js"))
    tau = _arr(kw, "tau", "<f8")
    out = {"twice_equal": h1 == h2, "eras": kw["era_count"], "era_switch_f": kw["era_switch_f"], "tau_min": float(tau.min()), "tau_max": float(tau.max()),
           "epoch0_days": kw["epoch0_days"], "intro_f": kw["intro_f"], "prologue": kw["prologue"], "rate_labels": kw["rate_labels"], "F": kw["F"],
           "marks": sorted({m["kind"] for m in kw["marks"]}), "ruler_first_label": kw["stream"]["tlab"][:3]}
    assert out["twice_equal"] and out["eras"] == 1 and out["tau_min"] == 0.0
    K.save(HERE, "receipt-a.json", out)
    print(json.dumps(out))


if __name__ == "__main__":
    params = common.load_params()
    for s in sys.argv[1:]:
        globals()[s.replace("-", "_")](params)
