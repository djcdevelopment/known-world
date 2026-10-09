"""export/probe.py: the alignment probe. ffprobe is absent on this host, so ffmpeg -i and raw decodes stand in.

Checks: video frame count = F, audio samples = F * 1,600, the decoded white frame's start time against the decoded
click peak (after the MP4 edit list, which ffmpeg applies on decode), pass under 1 ms.
"""
import json
import re
import subprocess
import sys

import numpy as np

from encode import FFMPEG


def info(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.stderr


def elst_entries(path):
    """Edit-list entries per track, read from the mp4 atoms: (segment_duration, media_time, timescale-less)."""
    import struct
    b = open(path, "rb").read()
    out, i = [], 0
    while True:
        i = b.find(b"elst", i)
        if i < 0:
            return out
        ver = b[i + 4]
        n = struct.unpack(">I", b[i + 8:i + 12])[0]
        p, ents = i + 12, []
        for _ in range(n):
            if ver == 1:
                d, m = struct.unpack(">qq", b[p:p + 16]); p += 20
            else:
                d, m = struct.unpack(">Ii", b[p:p + 8]); p += 12
            ents.append((d, m))
        out.append(ents)
        i += 4


def probe(path, F, fps, first_frame, probe_f, spf=1600):
    txt = info(path)
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", txt)
    dur_s = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3))
    edit = re.findall(r"start: ([\d.]+)", txt)
    v = subprocess.run([FFMPEG, "-v", "error", "-i", path, "-map", "0:v:0", "-vf", "scale=8:8,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, stdin=subprocess.DEVNULL).stdout
    frames = np.frombuffer(v, dtype=np.uint8).reshape(-1, 64)
    white = np.where(frames.min(axis=1) >= 250)[0]
    a = subprocess.run([FFMPEG, "-v", "error", "-i", path, "-map", "0:a:0", "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                       capture_output=True, stdin=subprocess.DEVNULL).stdout
    s = np.frombuffer(a, dtype="<f4").reshape(-1, 2)
    exp = (probe_f - first_frame) * spf
    lo, hi = max(0, exp - 4800), min(len(s), exp + 4800)  # search +-100 ms around the expected click, the page may be loud elsewhere
    seg = np.abs(s[lo:hi, 0])
    peak = lo + int(np.argmax(seg))
    # the click's first strong sample: first |x| above half the window peak (AAC smears the attack by a few samples)
    onset = lo + int(np.argmax(seg > 0.5 * seg.max()))
    t_white = float(white[0]) / fps if len(white) else None
    out = {
        "container_duration_s": dur_s, "expected_duration_s": F / fps, "video_frames": int(len(frames)), "expected_frames": F,
        "elst": elst_entries(path), "audio_samples": int(len(s)), "expected_samples": F * spf, "stream_start_times": edit,
        "white_frames": [int(i) + first_frame for i in white], "expected_probe_frame": probe_f,
        "click_peak_sample": peak, "click_onset_sample": onset, "expected_click_sample": (probe_f - first_frame) * spf,
        "t_white_s": t_white, "t_click_peak_s": peak / 48000, "t_click_onset_s": onset / 48000,
        "delta_ms_onset": None if t_white is None else (onset / 48000 - t_white) * 1000,
        "delta_ms_peak": None if t_white is None else (peak / 48000 - t_white) * 1000,
    }
    out["pass"] = bool(len(white) == 1 and int(white[0]) + first_frame == probe_f and abs(out["delta_ms_onset"]) < 1.0
                       and out["video_frames"] == F and F * spf <= out["audio_samples"] < F * spf + 1024
                       and abs(out["container_duration_s"] - F / fps) < 0.01)
    out["audio_tail_padding_samples"] = out["audio_samples"] - F * spf
    return out


if __name__ == "__main__":
    print(json.dumps(probe(sys.argv[1], int(sys.argv[2]), 30, 0, int(sys.argv[3])), indent=1))
