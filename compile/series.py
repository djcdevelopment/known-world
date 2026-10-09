"""compile/series.py: infrastructure deltas, checkpoints and per-frame series (STRATEGY 4.3), at tile level (slice 4+).

A delta is one record per (frame, tile, class group); activity A(f) = A(c) D(c, f) + sum w_i D(f_i, f) with
D(a, b) = 2^-((tau[b] - tau[a]) / fog_half_life_days): exact, so a checkpoint every CP frames bounds replay.
Also the radio-layer tables: beams, rings, sparks, the band series, the HQ track and the surface tallies.
"""
import collections
import json
import math
import os

import numpy as np

import common
from common import MERGED, parse_ts

CP = 900
SEAT_HOSTS = ("omen-linux", "am4", "fx99")
BAND_CLASSES = ("chatgpt", "claude", "codex", "opencode")


def seat_host(backend):
    if backend.startswith("omen-"):
        return "omen-linux"
    if backend.startswith("am4-"):
        return "am4"
    if backend.startswith("fx99-"):
        return "fx99"
    return None


def deltas(T, R, G, W, clock, nR, nG):
    """T epoch, R tile, G group, W weight -> per-frame index ds, and records (dr, dg, dw) sorted by frame."""
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
    idx = dr.astype(np.int64) * nG + dg.astype(np.int64)
    dwf = dw.astype(np.float64)
    for f in range(F):
        if f > 0:
            A *= 2.0 ** (-(tau[f] - tau[f - 1]) / hl)
        a, b = ds[f], ds[f + 1]
        if b > a:
            np.add.at(A, idx[a:b], dwf[a:b])
        if f % CP == 0:
            out[f // CP] = A
    return out.astype(np.float32)


def rolling(a, n):
    cs = np.concatenate([[0], np.cumsum(a)])
    idx = np.arange(len(a))
    return cs[idx + 1] - cs[np.maximum(0, idx + 1 - n)]


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
    # offloads per seat (omen, am4, fx99)
    for h in SEAT_HOSTS:
        ts = np.array([x[0] for x in c.offloads if seat_host(x[1]) == h], dtype=np.int64)
        out["seat_" + h] = np.bincount(clock.frame(ts), minlength=F)[:F].astype(np.float64) if len(ts) else np.zeros(F)
    return out


def commit_capacity(c, clock, nat_index):
    F = clock.F
    cnt = np.zeros((len(nat_index), F))
    fil = np.zeros((len(nat_index), F))
    for lin, cs in c.commits.items():
        for x in cs:
            f = int(clock.frame(np.array([x[0]]))[0])
            cnt[nat_index[x[2]], f] += 1
            fil[nat_index[x[2]], f] += x[5]
    return np.cumsum(cnt, axis=1).astype(np.float32), np.cumsum(fil, axis=1).astype(np.float32)


def participations(c, clock, nat_index):
    """Cumulative participations per nation: offload calls for local seats, sessions for the rest (for rows with 0 tests)."""
    F = clock.F
    out = np.zeros((len(nat_index), F))
    f = clock.frame(np.array([x[0] for x in c.offloads], dtype=np.int64)) if c.offloads else np.zeros(0, dtype=np.int64)
    if "local_model" in nat_index:
        out[nat_index["local_model"]] += np.bincount(f, minlength=F)[:F]
    for (t, cls, host) in c.sess_events:
        if cls in nat_index and cls != "local_model":
            out[nat_index[cls], int(clock.frame(np.array([t]))[0])] += 1
    return np.cumsum(out, axis=1).astype(np.float32)


def band_series(ser, F, fps):
    """The mirrored radio band: uint8 amplitude per frame, log scale against each series' own ceiling, 0.5 s window."""
    win = max(1, fps // 2)
    names, arrs = [], []
    for k in BAND_CLASSES + ("commits", "local_model"):
        r = rolling(ser[k], win) * (fps / win)
        mx = max(float(np.percentile(r[r > 0], 99.5)) if (r > 0).any() else 1.0, 1.0)
        a = np.clip(np.log10(1 + r) / math.log10(1 + mx), 0, 1)
        names.append(k)
        arrs.append((a * 255).round().astype(np.uint8))
    return names, np.stack(arrs)


def hq_track(c, params, clock, tau):
    """HQ host per frame (the surface with most agent chat over hq_window_days story days; cloud before any), and a
    glided world-space track (2 s smoothstep between surfaces). Returns (host_index_per_frame, hosts list, change days)."""
    F = clock.F
    hosts = ["cloud", "omen-e", "omen-c", "omen-linux", "am4", "fx99"]
    hi = {h: i for i, h in enumerate(hosts)}
    nday = int(math.ceil(clock.end_days)) + 2
    cnt = np.zeros((len(hosts), nday))
    for (t, host, cls, n) in c.chat_all:
        d = int(clock.tau_of_epoch(t) // 1)
        if 0 <= d < nday and host in hi:
            cnt[hi[host], d] += n
    win = int(params["hq_window_days"])
    roll = np.stack([rolling(cnt[i], win) for i in range(len(hosts))])
    day_host = np.zeros(nday, dtype=np.int64)
    cur = 0
    for d in range(nday):
        col = roll[:, d]
        if col[1:].max() > 0:
            best = int(np.argmax(col[1:])) + 1
            # hysteresis: stay on the current surface unless another leads by 20 percent
            if cur == 0 or col[best] > 1.2 * col[cur]:
                cur = best
        day_host[d] = cur
    d_of_f = np.clip(np.floor(tau + 1e-9).astype(np.int64), 0, nday - 1)
    hf = day_host[d_of_f]
    return hf, hosts, day_host


def hq_positions(hf, hosts, anchors, fps, glide_frames):
    """x, y per frame: the anchor of the HQ surface, smoothstep-glided over glide_frames after a change."""
    F = len(hf)
    ax = np.array([anchors.get(h, anchors["cloud"])[0] for h in hosts])
    ay = np.array([anchors.get(h, anchors["cloud"])[1] for h in hosts])
    x = np.zeros(F); y = np.zeros(F)
    cx, cy = ax[hf[0]], ay[hf[0]]
    g0, from_x, from_y, tgt = -10 ** 9, cx, cy, hf[0]
    for f in range(F):
        if hf[f] != tgt:
            tgt, g0, from_x, from_y = hf[f], f, cx, cy
        u = min(1.0, (f - g0) / max(1, glide_frames))
        s = u * u * (3 - 2 * u)
        cx = from_x + (ax[tgt] - from_x) * s
        cy = from_y + (ay[tgt] - from_y) * s
        x[f], y[f] = cx, cy
    return x, y


def beams(c, params, clock, T_reg_index, T, per_frame):
    """Comms beams: per frame the strongest `per_frame` (region, class group) session buckets, HQ -> region centre."""
    F = clock.F
    acc = collections.defaultdict(float)
    for L, ms in c.chat.items():
        hs = T.hosts_of.get(L)
        if not hs:
            continue
        for (t, sid, cls, n, path, host) in ms:
            h = host if host in hs else hs[0]
            ri = T_reg_index.get((L, h))
            if ri is None:
                continue
            f = int(clock.frame(np.array([t]))[0])
            acc[(f, ri, cls)] += n
    byf = collections.defaultdict(list)
    for (f, ri, cls), n in acc.items():
        byf[f].append((-n, ri, cls))
    bs = np.zeros(F + 1, dtype=np.int32)
    br, bw, bc = [], [], []
    for f in range(F):
        lst = sorted(byf.get(f, []))[:per_frame]
        for (mn, ri, cls) in lst:
            br.append(ri); bw.append(min(255, int(round(60 * math.log2(1 - mn))))); bc.append(cls)
        bs[f + 1] = len(br)
    return bs, np.array(br, dtype=np.uint16), np.array(bw, dtype=np.uint8), bc


def ring_births(series_chatgpt, fps, min_gap_s=0.3):
    """Frames at which a ChatGPT ring is born: a frame with messages, at most one per min_gap_s."""
    out = []
    last = -10 ** 9
    gap = max(2, int(round(min_gap_s * fps)))
    for f in np.nonzero(series_chatgpt > 0)[0]:
        if f - last >= gap:
            out.append(int(f)); last = int(f)
    return np.array(out, dtype=np.int32)


ERA_UNIT_DAYS = (365.2425, 30.436875, 7.0)  # year in A, month in B, week in C
ERA_UNIT_NAMES = ("yr", "mo", "wk")


def running_totals(c, params, clock, nat_index, surfaces, hosts_fs, launches=None):
    """Running totals (DIRECTION 'Running totals'): cumulative per nation (commits, files changed, lines added, lines
    removed), per surface (files created, files updated, commits) and for the world, plus the per-nation commit rate per
    era unit. Counted commits only: third-party-class commits in Derek's lineages and every commit in a third-party
    clone are outside every total and are tallied once in `third` for the receipt."""
    F = clock.F
    nN = len(nat_index)
    tau = clock.tau_frames()
    era = clock.era_frames().astype(np.int64)
    cm = c.tot_commits
    t = np.array([x[0] for x in cm], dtype=np.int64)
    fr = clock.frame(t)
    ni = np.array([nat_index[x[1]] for x in cm], dtype=np.int64)
    cnt = np.zeros((nN, F)); fil = np.zeros((nN, F)); ins = np.zeros((nN, F)); dele = np.zeros((nN, F))
    np.add.at(cnt, (ni, fr), 1.0)
    np.add.at(fil, (ni, fr), np.array([x[3] for x in cm], dtype=np.float64))
    np.add.at(ins, (ni, fr), np.array([x[4] for x in cm], dtype=np.float64))
    np.add.at(dele, (ni, fr), np.array([x[5] for x in cm], dtype=np.float64))
    cum = lambda a: np.cumsum(a, axis=-1)
    ccum, fcum, icum, dcum = cum(cnt), cum(fil), cum(ins), cum(dele)
    # surfaces: commits by host, files created / updated by host (bulk copies excluded unless births_exclude_bulk is false)
    nS = len(surfaces)
    sc_commits = np.zeros((nS, F)); sc_created = np.zeros((nS, F)); sc_updated = np.zeros((nS, F))
    sidx = {s: i for i, s in enumerate(surfaces)}
    hh = np.array([sidx.get(x[2], -1) for x in cm], dtype=np.int64)
    m = hh >= 0
    np.add.at(sc_commits, (hh[m], fr[m]), 1.0)
    fs = c.fs_rows
    excl = bool(params["births_exclude_bulk"])
    bulk_n = {"file_birth": 0, "file_update": 0}
    fs_world = np.zeros(F)
    for (tt, host, kind, n, bulk, r) in fs:
        if bulk:
            bulk_n[kind] += n
            if excl:
                continue
        f = int(clock.frame(np.array([tt], dtype=np.int64))[0])
        if host in sidx:
            (sc_created if kind == "file_birth" else sc_updated)[sidx[host], f] += n
        fs_world[f] += n
    sc_commits, sc_created, sc_updated = cum(sc_commits), cum(sc_created), cum(sc_updated)
    # world totals: commits; files = files changed in commits + files created + updated outside git; lines = ins + del
    w_commits = cum(cnt.sum(0)); w_lines = cum(ins.sum(0) + dele.sum(0))
    w_files = cum(fil.sum(0) + fs_world)
    # rate: commits per era unit, trailing, one value per frame per nation
    rate = np.zeros((nN, F))
    mode = params["rate_window"]
    unit = np.array(ERA_UNIT_DAYS)[era]
    if mode == "era_unit":
        g0 = np.searchsorted(tau, tau - unit, side="left")
    elif mode == "rolling_10s":
        g0 = np.maximum(0, np.arange(F) - int(round(10 * clock.fps)))
    else:
        raise ValueError("rate_window")
    ar = np.arange(F)
    for i in range(nN):
        prev = np.where(g0 > 0, ccum[i][np.maximum(g0 - 1, 0)], 0.0)
        n = ccum[i] - prev
        if mode == "era_unit":
            rate[i] = n
        else:
            days = tau - tau[g0]
            rate[i] = np.where(days > 1e-9, n / np.maximum(days, 1e-9) * unit, 0.0)
    # births_to_nation arm: files created inside a launch window and lineage go to the launch's nation (inferred)
    created_nat = None
    if params["births_to_nation"] == "launch_window":
        created_nat = np.zeros((nN, F))
        by_lin = collections.defaultdict(list)
        for l in launches or []:
            by_lin[l["lineage"]].append((l["ts_start"], l["ts_end"], l["nation"]))
        for (tt, host, kind, n, bulk, r) in fs:
            if kind != "file_birth" or (bulk and excl):
                continue
            for (a, b, nat) in by_lin.get(r, ()):
                if a - 86400 <= tt <= b + 86400:
                    created_nat[nat_index[nat], int(clock.frame(np.array([tt], dtype=np.int64))[0])] += n
                    break
        created_nat = cum(created_nat)
    totals = {
        "nation": {k: {"commits": int(ccum[i, -1]), "files_changed": int(fcum[i, -1]), "lines_added": int(icum[i, -1]), "lines_removed": int(dcum[i, -1])} for k, i in nat_index.items()},
        "surface": {s: {"commits": int(sc_commits[i, -1]), "files_created": int(sc_created[i, -1]), "files_updated": int(sc_updated[i, -1])} for s, i in sidx.items()},
        "world": {"commits": int(w_commits[-1]), "files": int(w_files[-1]), "lines": int(w_lines[-1])},
        "bulk_copy_excluded": bulk_n if excl else {}, "no_numstat_counted": int(sum(1 for x in cm if x[6])),
        "third": c.third_totals,
    }
    return {"ccum": ccum, "fcum": fcum, "icum": icum, "dcum": dcum, "sc_commits": sc_commits, "sc_created": sc_created,
            "sc_updated": sc_updated, "w": np.stack([w_commits, w_files, w_lines]), "rate": rate, "created_nat": created_nat, "totals": totals}
