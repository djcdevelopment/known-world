"""compile/audio.py: WAV synthesis. Every onset is sample f * SPF (1,600 at 48 kHz / 30 fps). Seeded, byte-deterministic.

Slice 2 holds the skeleton: exact length, a seeded noise floor, the soft-knee limiter, the sync click. Slice 3 adds
tones, bells, hum, static (see synth.py).
"""
import numpy as np

SR = 48000


def spf(fps):
    assert SR % fps == 0
    return SR // fps


def soft_limit(x, ceiling_db=-1.0, knee_db=6.0):
    """Soft-knee limiter: linear to (ceiling - knee), tanh-shaped above, never past the ceiling."""
    ceil = 10 ** (ceiling_db / 20)
    k0 = ceil * 10 ** (-knee_db / 20)
    a = np.abs(x)
    over = a > k0
    y = x.copy()
    if over.any():
        t = (a[over] - k0) / (ceil - k0)
        y[over] = np.sign(x[over]) * (k0 + (ceil - k0) * np.tanh(t))
    return y


def sync_click(n=48, level_db=-6.0):
    """1 ms click: one-sample-attack decaying impulse, peak at its first sample."""
    g = 10 ** (level_db / 20)
    t = np.arange(n)
    return (g * np.exp(-t / 8.0) * np.where(t % 2 == 0, 1.0, -0.8)).astype(np.float32)


def render_skeleton(F, fps, seed, probe_f=None, noise_db=-70.0):
    """Stereo float32 [F * spf, 2]: seeded noise floor plus the sync click at sample probe_f * spf."""
    n = F * spf(fps)
    rng = np.random.default_rng(seed)  # PCG64, seeded
    amp = 10 ** (noise_db / 20)
    out = (rng.standard_normal((n, 2)) * amp).astype(np.float32)
    if probe_f is not None:
        s = probe_f * spf(fps)
        c = sync_click()
        out[s:s + len(c), 0] += c
        out[s:s + len(c), 1] += c
    return out


def wav_bytes(x):
    """IEEE-float32 stereo WAV, 48 kHz. Header written by hand so the bytes are fully deterministic."""
    import struct
    data = np.ascontiguousarray(x, dtype="<f4").tobytes()
    ch = x.shape[1]
    hdr = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 3, ch, SR, SR * ch * 4, ch * 4, 32)
    hdr += b"data" + struct.pack("<I", len(data))
    return hdr + data


def write_wav(path, x):
    b = wav_bytes(x)
    with open(path, "wb") as f:
        f.write(b)
    return len(b)
