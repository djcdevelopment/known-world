"""compile/score.py: the short score's tables (plan section 4). One stave per nation; a note per launch (head at the yield band's height, a chord of up
to four heads for a MIRV with `+n` for the rest, a tie to lf + lpre for a unified launch, hollow when the nation is inferred); the stipple is the
nation's chatter rate (log-scaled u8, G x F); the wedge reads rate_nat on the page. Everything derives from data the compile already holds."""
import numpy as np

import series as ser

CHAT_OF = {"chatgpt": "chatgpt", "claude": "claude", "codex": "codex", "opencode": "opencode", "local_model": "local_model"}


def build(rows, series, classes, F, fps):
    hs, hb, more = [0], [], []
    for r in rows:
        bands = sorted((w[2] for w in r["whs"]), reverse=True) if r["shape"] == 1 and r["whs"] else [r["band"]]
        if not bands:
            bands = [r["band"]]
        hb += bands[:4]; hs.append(len(hb)); more.append(min(255, max(0, len(bands) - 4)))
    win = max(1, fps // 2)
    chat = np.zeros((len(classes), F), dtype=np.uint8)
    for i, k in enumerate(classes):
        if k in CHAT_OF:
            r_ = ser.rolling(series[CHAT_OF[k]], win) * (fps / win)
            mx = max(float(np.percentile(r_[r_ > 0], 99.5)) if (r_ > 0).any() else 1.0, 1.0)
            chat[i] = np.round(np.clip(np.log10(1 + r_) / np.log10(1 + mx), 0, 1) * 255).astype(np.uint8)
    return {"hs": np.array(hs, dtype="<i4"), "hb": np.array(hb, dtype="u1"), "more": np.array(more, dtype="u1"), "chat": chat}
