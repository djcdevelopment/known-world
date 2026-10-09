"""compile/synth.py: the slice-3 audio (STRATEGY section 6): launch tones by band and nation, lineage bells, nation-first
octave doubling, MIRV pips and unified octave, collapse (125 ms chord bins then a 16 Hz roll), hum from the commit rate,
static per class from the message rate. Every onset is sample f * 1,600. Seeded; byte-deterministic.
"""
import math

import numpy as np

import audio as aud

SR = aud.SR
TONE_S = [0.12, 0.19, 0.31, 0.49, 0.79, 1.26]
GAIN_DB = [-27, -24, -21, -18, -15, -12]
PITCH = {"human": 220.0, "claude": 329.63, "codex": 392.0, "opencode": 493.88, "local_model": 130.81, "automation": 293.66,
         "chatgpt": 349.23}
STATIC_HZ = {"chatgpt": 1200.0, "claude": 2000.0, "codex": 2800.0, "opencode": 3600.0, "local_model": 800.0}
BELL_PARTIALS = [(1.0, 1.0), (2.76, 0.5), (5.40, 0.25), (8.93, 0.12)]
C2 = 65.41


def db(x):
    return 10 ** (x / 20.0)


def tone(freq, length_s, gain_db, gen_partial=None, sub=False):
    n = max(8, int(length_s * SR))
    t = np.arange(n) / SR
    y = np.sin(2 * math.pi * freq * t) + 0.25 * np.sin(2 * math.pi * 2 * freq * t) + 0.1 * np.sin(2 * math.pi * 3 * freq * t)
    if gen_partial:
        y = y + db(-24) * np.sin(2 * math.pi * freq * (3 + gen_partial) * t)
    if sub:
        y = y + 0.6 * np.sin(2 * math.pi * freq * 0.5 * t)
    env = np.exp(-t / (length_s / 4.5)) * np.minimum(1.0, t / 0.004)
    k = min(n, int(0.005 * SR))
    env[n - k:] *= np.linspace(1, 0, k)
    return (y * env * db(gain_db) / 1.35).astype(np.float32)


def bell(length_s=3.0, gain_db=-26, base=C2):
    n = int(length_s * SR)
    t = np.arange(n) / SR
    y = sum(a * np.sin(2 * math.pi * base * m * t) * np.exp(-t / (length_s / (4.0 + 0.8 * i))) for i, (m, a) in enumerate(BELL_PARTIALS))
    y = y * np.minimum(1.0, t / 0.006)
    return (y * db(gain_db) / 2.0).astype(np.float32)


def pip(freq, gain_db, length_s=0.06):
    n = int(length_s * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * math.pi * freq * t) * np.exp(-t / (length_s / 4)) * np.minimum(1, t / 0.002) * db(gain_db)).astype(np.float32)


def bandpass_fft(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x)).astype(np.float32)


def colored_noise(N, fc, seed):
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(N, dtype=np.float32)
    X = np.fft.rfft(w)
    f = np.fft.rfftfreq(N, 1 / SR)
    f[0] = 1.0
    H = np.exp(-0.5 * (np.log(f / fc) / 0.35) ** 2).astype(np.float32)
    X *= H
    y = np.fft.irfft(X, N).astype(np.float32)
    return y / (np.std(y) + 1e-12)


def pan_gains(px, W=1920.0):
    p = 0.6 * (2 * px / W - 1)
    a = (p + 1) * math.pi / 4
    return math.cos(a), math.sin(a)


def collapse_mask(onset_frames, F, thr, fps=30):
    cnt = np.bincount(onset_frames, minlength=F + 1)[:F].astype(np.int64)
    cs = np.concatenate([[0], np.cumsum(cnt)])
    win = np.array([cs[min(F, f + 1)] - cs[max(0, f + 1 - fps)] for f in range(F)])
    mask = np.zeros(F, dtype=bool)
    on = False
    for f in range(F):
        if not on and win[f] > thr:
            on = True
        elif on and win[f] < 0.8 * thr:
            on = False
        mask[f] = on
    return mask


def rolling(a, n):
    cs = np.concatenate([[0], np.cumsum(a)])
    idx = np.arange(len(a))
    return cs[idx + 1] - cs[np.maximum(0, idx + 1 - n)]


def mix(out, x, s, gl, gr):
    e = min(len(out), s + len(x))
    if e <= s:
        return
    seg = x[: e - s]
    out[s:e, 0] += seg * gl
    out[s:e, 1] += seg * gr


def synthesize(F, fps, seed, probe_f, launches, wh, nations, series, params, env_scale, gens_index):
    """launches: list of dicts {f, px, band, nat (class), gen (int or None), first_test, first_nat, shape, inferred, warheads: [(f, band, px)]}"""
    spf = aud.spf(fps)
    out = aud.render_skeleton(F, fps, seed, probe_f)
    thr = params["collapse_events_per_s"]
    onset_f = np.array([l["f"] for l in launches], dtype=np.int64)
    cmask = collapse_mask(onset_f, F, thr, fps)
    stats = {"collapsed_frames": int(cmask.sum()), "collapse_bins": 0, "roll_bins": 0, "tones": 0, "bells": 0, "pips": 0}
    bins = {}
    for l in launches:
        gl, gr = pan_gains(l["px"])
        s = l["f"] * spf
        key = "chatgpt" if (l["nat"] == "chatgpt") else l["nat"]
        freq = PITCH[key]
        L = TONE_S[l["band"] - 1] * env_scale
        g = GAIN_DB[l["band"] - 1]
        if l["first_test"]:
            mix(out, bell(3.0 * env_scale if env_scale < 1 else 3.0), s, gl, gr); stats["bells"] += 1
        if l["first_nat"]:
            mix(out, tone(freq * 2, 2.0 * env_scale, g - 3), s, gl, gr)
        if cmask[l["f"]]:
            bins.setdefault(s // 6000, []).append(l)
            continue
        if l["shape"] == "mirv":
            y = tone(freq, L, g - 6, l["gen"]); 
        elif l["shape"] == "unified":
            y = tone(freq / 2, L * 1.5, g, l["gen"])
        else:
            y = tone(freq, L, g, l["gen"], sub=l["band"] == 6)
        if l["inferred"]:
            y = bandpass_fft(y, 700.0, 2600.0) * 1.4
        mix(out, y, s, gl, gr); stats["tones"] += 1
        for (wf, wb, wpx) in l["warheads"]:
            a, b = pan_gains(wpx)
            mix(out, pip(freq * 2, GAIN_DB[wb - 1] - 4), wf * spf, a, b); stats["pips"] += 1
    # collapsed bins: chord of distinct nation pitches (<= 4 voices); four in a row become a 16 Hz roll
    run_prev, run_len = None, 0
    for b in sorted(bins):
        run_len = run_len + 1 if run_prev is not None and b - run_prev <= 1 else 1
        run_prev = b
        ls = bins[b]
        cnt = {}
        for l in ls:
            cnt[l["nat"]] = cnt.get(l["nat"], 0) + 1
        voices = sorted(cnt, key=lambda k: (-cnt[k], k))[:4]
        g = max(GAIN_DB[l["band"] - 1] for l in ls) - 3
        L = max(TONE_S[l["band"] - 1] for l in ls) * env_scale
        s = b * 6000
        px = float(np.mean([l["px"] for l in ls]))
        gl, gr = pan_gains(px)
        if run_len >= 4:
            n = 6000
            t = np.arange(n) / SR
            y = np.sin(2 * math.pi * PITCH[voices[0]] * t) * (0.5 + 0.5 * np.sin(2 * math.pi * 16 * t)) * db(g + 3)
            mix(out, y.astype(np.float32), s, gl, gr); stats["roll_bins"] += 1
        else:
            for v in voices:
                mix(out, tone(PITCH[v], max(L, 0.12), g), s, gl, gr)
        stats["collapse_bins"] += 1
    N = F * spf
    sample_t = np.arange(N) / spf
    fr = np.arange(F)
    # hum 55 + 110 Hz from the commit rate (per output second over a 1 s window), gated at zero
    r = rolling(series["commits"], fps)
    lvl = np.minimum(-24.0, -36.0 + 6.0 * np.log10(1 + r))
    amp = db(lvl) * np.minimum(1.0, r / 2.0)
    a_s = np.interp(sample_t, fr, amp).astype(np.float32)
    t = np.arange(N, dtype=np.float64) / SR
    hum = (np.sin(2 * math.pi * 55 * t) + 0.5 * np.sin(2 * math.pi * 110 * t)).astype(np.float32) / 1.5
    out[:, 0] += hum * a_s; out[:, 1] += hum * a_s
    del hum
    # static per class from the log message rate, ceiling -18 dBFS
    for k, (cls, fc) in enumerate(STATIC_HZ.items()):
        r = rolling(series[cls], fps)
        lvl = np.minimum(-18.0, -52.0 + 8.0 * np.log10(1 + r))
        amp = db(lvl) * np.minimum(1.0, r / 3.0)
        if amp.max() <= 0:
            continue
        a_s = np.interp(sample_t, fr, amp).astype(np.float32)
        nz = colored_noise(N, fc, seed + 100 + k)
        out[:, 0] += nz * a_s; out[:, 1] += nz * a_s
    out = aud.soft_limit(out, -1.0).astype(np.float32)
    return out, stats
