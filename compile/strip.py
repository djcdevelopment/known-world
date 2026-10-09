"""compile/strip.py: the launch strip (STRATEGY section 10, slice 1). Time on x at the era rates, yield band on y,
nation colour, shape marked (single dot, MIRV vertical scatter, unified ring, inferred open ring); third party
excluded (never in launches); an infrastructure density trace under it. Pillow only; deterministic.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clock as clk
import common

COL = {"human": (242, 230, 201), "chatgpt": (63, 185, 122), "claude": (255, 122, 92), "codex": (53, 208, 224),
       "opencode": (167, 123, 255), "local_model": (216, 67, 47), "automation": (240, 180, 41)}
BG = (7, 9, 14)
SS = 2  # supersample


def font(sz):
    return ImageFont.load_default(size=sz)


def density(c, clock):
    """Per-frame-second infrastructure: commit count and folded chat messages (own lineages and ChatGPT)."""
    tc, wc = [], []
    for lin, v in c.commits.items():
        tc += [x[0] for x in v]
    tm, wm = [], []
    for lin, v in c.chat.items():
        for (t, sid, cls, n) in v:
            tm.append(t); wm.append(n)
    for (t, sid) in c.gpt:
        tm.append(t); wm.append(1)
    return (np.array(tc, dtype=np.float64), np.ones(len(tc))), (np.array(tm, dtype=np.float64), np.array(wm, dtype=np.float64))


def ts_epoch(s):
    return common.parse_ts(s)


def panel(launches, clock, dens, W, H, label, y0=0, img=None, draw=None):
    s = SS
    left, right = 70 * s, 20 * s
    top = y0 + 46 * s
    row_h = 58 * s
    dens_h = 70 * s
    base = top + 6 * row_h
    x_of = lambda T: left + (W * s - left - right) * (T / (clock.intro_s + clock.story_s))
    # grid and band labels
    f12, f16 = font(12 * s), font(16 * s)
    for b in range(1, 7):
        y = base - (b - 0.5) * row_h
        draw.line([(left, y), (W * s - right, y)], fill=(20, 24, 33), width=s)
        draw.text((8 * s, y - 7 * s), f"band {b}", fill=(120, 128, 142), font=f12)
    # era edges and ticks
    edges = clock.era_edges_s()
    labs = clock.rate_labels()
    xs = [x_of(0), x_of(edges[0]), x_of(edges[1]), x_of(clock.intro_s + clock.story_s)]
    for i in range(3):
        draw.text((xs[i] + 6 * s, y0 + 6 * s), f"era {'ABC'[i]}   {labs[i]}", fill=(150, 158, 172), font=f12)
    for x in xs[1:3]:
        draw.line([(x, top - 8 * s), (x, base + dens_h + 22 * s)], fill=(70, 78, 94), width=s)
    import calendar
    for yr in range(2012, 2027):
        t = calendar.timegm((yr, 1, 1, 0, 0, 0))
        if t > clock.epoch0 * 86400:
            Tx = x_of(float(clock.T(t)) - 0.0)
            if yr <= 2026:
                draw.line([(Tx, base + dens_h), (Tx, base + dens_h + 6 * s)], fill=(110, 118, 132), width=s)
                if yr >= 2024 or yr % 2 == 0:
                    draw.text((Tx - 12 * s, base + dens_h + 8 * s), str(yr), fill=(120, 128, 142), font=f12)
    for (yr, mo) in [(2026, m) for m in range(3, 11)]:
        t = calendar.timegm((yr, mo, 1, 0, 0, 0))
        Tx = x_of(float(clock.T(t)))
        draw.line([(Tx, base + dens_h), (Tx, base + dens_h + 4 * s)], fill=(110, 118, 132), width=s)
    draw.text((8 * s, y0 + 22 * s), label, fill=(225, 230, 240), font=f16)
    # infrastructure trace: log counts per x-pixel column
    ncol = int((W * s - left - right) / s)
    for (t, w), colr in zip(dens, ((130, 120, 105), (80, 112, 150))):
        T = clock.T(t)
        hist, _ = np.histogram(T, bins=ncol, range=(0, clock.intro_s + clock.story_s), weights=w)
        h = np.log10(1 + hist)
        h = h / max(h.max(), 1e-9) * (dens_h - 6 * s) / 2
        for i, v in enumerate(h):
            if v > 0.3:
                x = left + i * s
                yb = base + dens_h - 2 * s if colr[0] > 100 else base + dens_h / 2
                draw.rectangle([x, yb - v, x + s - 1, yb], fill=colr)
    draw.text((8 * s, base + 26 * s), "commits", fill=(130, 120, 105), font=f12)
    draw.text((8 * s, base + 10 * s), "chat", fill=(80, 112, 150), font=f12)
    # launches, oldest first
    for l in launches:
        T = float(clock.T(ts_epoch(l["ts_start"])))
        x = x_of(T)
        b = l["yield"]["class"]
        y = base - (b - 0.5) * row_h
        col = COL.get(l["nation"], (200, 200, 200))
        r = (1.6 + 0.55 * b) * s
        rng = np.random.default_rng(int(l["launch_id"], 16) % (2 ** 32))
        inferred = bool(l.get("nation_inferred"))
        if l["shape"] == "mirv":
            n = min(l["warheads"], 12)
            ys = y + (rng.random(n) - 0.5) * row_h * 0.8
            for yy in ys:
                draw.ellipse([x - r * 0.7, yy - r * 0.7, x + r * 0.7, yy + r * 0.7], fill=col)
            draw.line([(x, ys.min()), (x, ys.max())], fill=tuple(int(v * 0.55) for v in col), width=s)
        elif l["shape"] == "unified":
            rr = r * 1.9
            draw.ellipse([x - rr, y - rr, x + rr, y + rr], outline=col, width=2 * s)
            draw.ellipse([x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.5], fill=col)
        elif inferred:
            draw.ellipse([x - r, y - r, x + r, y + r], outline=col, width=s)
        else:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=col)
        if l["nongit"] and not inferred:
            pass


def legend(draw, W, y, s, counts):
    f12 = font(12 * s)
    x = 70 * s
    for nat, col in COL.items():
        draw.ellipse([x, y, x + 9 * s, y + 9 * s], fill=col)
        draw.text((x + 14 * s, y - 2 * s), nat, fill=(190, 196, 208), font=f12)
        x += 105 * s
    draw.text((x + 10 * s, y - 2 * s), "dot = single   scatter = MIRV   ring+dot = unified   open ring = inferred (ChatGPT)", fill=(150, 158, 172), font=f12)


def render(arms, clock, dens, out_png_by_arm, compare_png, W=3600, H_panel=560):
    s = SS
    for name, launches, label in arms:
        img = Image.new("RGB", (W * s, H_panel * s), BG)
        d = ImageDraw.Draw(img)
        panel(launches, clock, dens, W, H_panel, label, 0, img, d)
        legend(d, W, (H_panel - 18) * s, s, None)
        img.resize((W, H_panel), Image.LANCZOS).save(out_png_by_arm[name], optimize=False)
    img = Image.new("RGB", (W * s, H_panel * s * len(arms)), BG)
    d = ImageDraw.Draw(img)
    for i, (name, launches, label) in enumerate(arms):
        panel(launches, clock, dens, W, H_panel, label, i * H_panel * s, img, d)
    legend(d, W, (H_panel * len(arms) - 18) * s, s, None)
    img.resize((W, H_panel * len(arms)), Image.LANCZOS).save(compare_png)
