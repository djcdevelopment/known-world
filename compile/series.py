"""compile/series.py: infrastructure deltas, checkpoints and per-frame series (STRATEGY 4.3, slice 3 at region level).

A delta is one record per (frame, region, class group); activity A(f) = A(c) D(c, f) + sum w_i D(f_i, f) with
D(a, b) = 2^-((tau[b] - tau[a]) / fog_half_life_days): exact, so a checkpoint every CP frames bounds replay.
"""
import collections
import json
import math
import os

import numpy as np

import common
from common import MERGED, parse_ts

CP = 900
CLASSES = ("human", "chatgpt", "claude", "codex", "opencode", "local_model", "automation")


def w_commit(lines):
    return 1 + math.log10(1 + lines)


def w_birth(n):
    return 1 + math.log10(1 + n)


def w_chat(n):
    return 0.25 * math.log2(1 + n)


def collect_events(c, params, region_index, nat_index):
    """Raw weighted touches (epoch, region, group, weight) from the loaded corpus. Used by deltas AND the brute-force check."""
    cap = params["yield_cap_lines_per_commit"]
    T, R, G, W = [], [], [], []
    for lin, cs in c.commits.items():
        r = region_index.get(lin)
        if r is None:
            continue
        for (t, ref, cls, name, raw, nfiles, dirs, host, nonum) in cs:
            T.append(t); R.append(r); G.append(nat_index[cls]); W.append(w_commit(min(raw, cap)))
    for lin, ms in c.chat.items():
        r = region_index.get(lin)
        if r is None:
            continue
        for (t, sid, cls, n) in ms:
            T.append(t); R.append(r); G.append(nat_index[cls]); W.append(w_chat(n))
    for lin, days in c.nongit.items():
        r = region_index.get(lin)
        if r is None:
            continue
        for d, v in days.items():
            if v["files"] > 0 and v["t0"] is not None:
                T.append(v["t0"]); R.append(r); G.append(nat_index["human"]); W.append(w_birth(v["files"]))
    return np.array(T, dtype=np.int64), np.array(R, dtype=np.int64), np.array(G, dtype=np.int64), np.array(W, dtype=np.float64)


def class_series(c, params, clock, nat_index):
    """Per-frame message counts by class (all repos, including unmapped), commits, local offloads. One streaming pass."""
    F = clock.F
    chat = {k: [] for k in ("chatgpt", "claude", "codex", "opencode")}
    chatw = {k: [] for k in chat}
    for line in open(os.path.join(MERGED, "events.ndjson")):
        if '"chat_msg"' not in line:
            continue
        e = json.loads(line)
        if e["kind"] != "chat_msg":
            continue
        k = e["actor"]["class"]
        if k in chat:
            chat[k].append(parse_ts(e["ts"])); chatw[k].append(e["magnitude"]["n"])
    out = {}
    for k in chat:
        f = clock.frame(np.array(chat[k], dtype=np.int64))
        out[k] = np.bincount(f, weights=np.array(chatw[k], dtype=np.float64), minlength=F)[:F]
    f = clock.frame(np.array([x[0] for x in c.offloads], dtype=np.int64))
    out["local_model"] = np.bincount(f, minlength=F)[:F].astype(np.float64)
    cm = np.array([x[0] for v in c.commits.values() for x in v], dtype=np.int64)
    out["commits"] = np.bincount(clock.frame(cm), minlength=F)[:F].astype(np.float64)
    return out


def commit_capacity(c, clock, nat_index):
    F = clock.F
    cnt = np.zeros((len(nat_index), F))
    fil = np.zeros((len(nat_index), F))
    for lin, cs in c.commits.items():
        for (t, ref, cls, name, raw, nfiles, dirs, host, nonum) in cs:
            f = int(clock.frame(np.array([t]))[0])
            cnt[nat_index[cls], f] += 1
            fil[nat_index[cls], f] += nfiles
    return np.cumsum(cnt, axis=1).astype(np.float32), np.cumsum(fil, axis=1).astype(np.float32)


def deltas(T, R, G, W, clock, nR, nG):
    F = clock.F
    f = clock.frame(T)
    key = (f * nR + R) * nG + G
    order = np.argsort(key, kind="stable")
    key, W = key[order], W[order]
    uk, idx = np.unique(key, return_index=True)
    sw = np.add.reduceat(W, idx)
    df = uk // (nR * nG)
    rest = uk % (nR * nG)
    dr = rest // nG
    dg = rest % nG
    ds = np.searchsorted(df, np.arange(F + 1)).astype(np.int32)
    return ds, dr.astype(np.uint16), dg.astype(np.uint8), sw.astype(np.float32), df


def checkpoints(ds, dr, dg, dw, df, tau, hl, nR, nG, F):
    """A at frames 0, CP, 2 CP ... (activity after that frame's deltas), built by exact replay in float64."""
    ncp = (F - 1) // CP + 1
    out = np.zeros((ncp, nR * nG))
    A = np.zeros(nR * nG)
    last = 0
    cpi = 0
    for f in range(F):
        if f > 0:
            A *= 2.0 ** (-(tau[f] - tau[f - 1]) / hl)
        a, b = ds[f], ds[f + 1]
        if b > a:
            np.add.at(A, dr[a:b].astype(np.int64) * nG + dg[a:b].astype(np.int64), dw[a:b].astype(np.float64))
        if f % CP == 0:
            out[f // CP] = A
    return out.astype(np.float32)
