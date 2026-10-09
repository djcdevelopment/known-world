"""compile/build_data.py: kw-data.js (window.KW_DATA as base64 typed arrays; loads from file://) and audio.wav.

Slice 2 carries the clock tables only; slice 3 extends the same file (launches, regions, series, audio tables).
"""
import base64
import json
import os

import numpy as np

import audio
import common


def b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode("ascii")


def clock_block(clock, probe_f):
    era = clock.era_frames()
    sw = [int(np.argmax(era >= i + 1)) for i in range(2)]
    return {
        "version": 1, "F": clock.F, "fps": clock.fps, "epoch0_days": int(round(clock.epoch0)),
        "tau": b64(clock.tau_frames().astype("<f8")), "era": b64(era), "rate_labels": clock.rate_labels(),
        "era_switch_f": sw, "probe_f": -1 if probe_f is None else int(probe_f), "m": round(clock.m, 6),
        "story_s": round(clock.story_s, 6), "intro_s": clock.intro_s, "coda_s": clock.coda_s,
    }


def write_data_js(path, block):
    s = "window.KW_DATA=" + common.dumps(block) + ";\n"
    data = s.encode()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return common.sha256_bytes(data)
