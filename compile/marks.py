"""compile/marks.py: marks.json (DIRECTION 'The player'). Hashmarks on the scrubber and faint ticks on the exported ticker
hairline. Each mark is {kind, frame, label}. Kinds: era (boundaries), surface (a new continent), nation (entry), migration (the HQ
crossing to omen-linux), storm (the offload storm), regime (a break in the piecewise-linear fit of log10(cumulative + 1) against
story days, for commits, launches and files).

Regime fit. y = log10(cum + 1) on a daily grid from the first event. Top-down binary segmentation: a segment is split at the day
that minimises the summed squared error of two independent least-squares lines, provided each side is at least `min_days` long
(one year in era A, one month in B, 30 days in C: the era of the candidate day) and the slopes differ by more than
marks_slope_threshold in log10 units per `marks_slope_unit`: "year" (default) or "era" (the era's rate unit: year in A, month
in B, week in C, the literal reading; at threshold 0.5 it finds no break in this corpus, see LAP-13 RESULT). The split recurses on both sides. The
words come from the raw cumulative inside each segment: `idle` (under one event per era unit), else the rate in its second
half against its first half: above 1.5 `accelerating`, below 1/1.5 `slowing`, otherwise `linear` (a constant rate).
"""
import numpy as np

UNIT_DAYS = (365.2425, 30.436875, 7.0)
UNIT_NAMES = ("year", "month", "week")


def _era_of_day(d, bounds):
    return 0 if d < bounds[0] else (1 if d < bounds[1] else 2)


def _fit(cs, cy, cxx, cxy, a, b):
    """Least-squares slope and sse of y on x over index range [a, b) from prefix sums."""
    n = b - a
    sx, sy = cs[b] - cs[a], cy[b] - cy[a]
    sxx, sxy = cxx[b] - cxx[a], cxy[b] - cxy[a]
    den = n * sxx - sx * sx
    slope = (n * sxy - sx * sy) / den if abs(den) > 1e-12 else 0.0
    ic = (sy - slope * sx) / n
    return slope, ic


def segments(y, days, bounds, thr, min_days, slope_unit="year"):
    """Breakpoint indices of the piecewise-linear fit (sorted, excluding the ends)."""
    n = len(y)
    x = days.astype(np.float64)
    xm = x[0]
    xs = x - xm
    P = lambda a: np.concatenate([[0.0], np.cumsum(a)])
    cs, cy, cxx, cxy, cyy = P(xs), P(y), P(xs * xs), P(xs * y), P(y * y)
    era_idx = np.array([_era_of_day(d, bounds) for d in days])
    unit = np.array(UNIT_DAYS)[era_idx] if slope_unit == "era" else np.full(len(days), UNIT_DAYS[0])  # slopes in log10 per unit
    mind = np.array(min_days)[era_idx]

    def sse(a, b):
        m = b - a
        sx, sy, sxx, sxy, syy = cs[b] - cs[a], cy[b] - cy[a], cxx[b] - cxx[a], cxy[b] - cxy[a], cyy[b] - cyy[a]
        den = m * sxx - sx * sx
        if abs(den) < 1e-12:
            return syy - sy * sy / m
        sl = (m * sxy - sx * sy) / den
        ic = (sy - sl * sx) / m
        return syy - 2 * sl * sxy - 2 * ic * sy + sl * sl * sxx + 2 * sl * ic * sx + m * ic * ic

    breaks = []
    slopes = {}

    def rec(a, b):
        if b - a < 2:
            return
        best, bk = None, None
        for k in range(a + 2, b - 1):
            ml = int(np.ceil(mind[k]))
            if k - a < ml or b - k < ml:
                continue
            e = sse(a, k) + sse(k, b)
            if best is None or e < best - 1e-12:
                best, bk = e, k
        if bk is None:
            return
        s1, _ = _fit(cs, cy, cxx, cxy, a, bk)
        s2, _ = _fit(cs, cy, cxx, cxy, bk, b)
        if abs(s2 - s1) * unit[bk] <= thr:
            return
        breaks.append(bk)
        slopes[bk] = (s1, s2)
        rec(a, bk)
        rec(bk, b)

    rec(0, n)
    return sorted(breaks), slopes


def _word(cum, a, b, unit):
    """Regime word of the raw cumulative between day indices a and b."""
    total = cum[b - 1] - cum[a]
    L = b - 1 - a
    if L <= 0 or total / L * unit < 1.0:
        return "idle"
    mid = a + L // 2
    r1, r2 = cum[mid] - cum[a], cum[b - 1] - cum[mid]
    ratio = (r2 + 1.0) / (r1 + 1.0)
    return "accelerating" if ratio > 1.5 else ("slowing" if ratio < 1 / 1.5 else "linear")


def regimes(name, cum_f, clock, params):
    tau = clock.tau_frames()
    bounds = clock.bounds_days
    d_end = int(np.floor(clock.end_days))
    nz = np.nonzero(cum_f > 0)[0]
    if len(nz) == 0:
        return []
    d0 = max(0, int(np.floor(tau[nz[0]])))
    days = np.arange(d0, d_end + 1)
    cum = np.interp(days + 1.0, tau, cum_f)
    y = np.log10(cum + 1.0)
    md = [float(params["marks_min_days"][k]) for k in "ABC"]
    br, slopes = segments(y, days, bounds, float(params["marks_slope_threshold"]), md, params["marks_slope_unit"])
    edges = [0] + br + [len(days)]
    words = []
    for a, b in zip(edges[:-1], edges[1:]):
        era = _era_of_day(days[(a + b) // 2], bounds)
        words.append(_word(cum, a, b, UNIT_DAYS[era]))
    out = []
    for i, k in enumerate(br):
        w0, w1 = words[i], words[i + 1]
        if w0 == w1:
            label = "%s: %s \u2192 %s (%s)" % (name, w0, w1, "steeper" if slopes[k][1] > slopes[k][0] else "shallower")
        else:
            label = "%s: %s \u2192 %s" % (name, w0, w1)
        epoch = int(round((clock.epoch0 + float(days[k])) * 86400))
        out.append({"kind": "regime", "frame": int(clock.frame(np.array([epoch]))[0]), "label": label,
                    "_series": name, "_day": int(days[k])})
    return out


def build(params, clock, era_switch_f, surface_entry, nation_entry, hq_cross_f, offload_f, series):
    """surface_entry: [(label, frame)], nation_entry: [(name, frame)], hq_cross_f: frame or None, offload_f: (F,) offload calls
    per frame, series: {'commits': cum (F,), 'launches': cum, 'files': cum}."""
    F = clock.F
    marks = []
    for i, f in enumerate(era_switch_f):
        marks.append({"kind": "era", "frame": int(f), "label": "era %s begins" % "BC"[i]})
    for lab, f in surface_entry:
        if f < F:
            marks.append({"kind": "surface", "frame": int(f), "label": "new continent: %s" % lab})
    for name, f in nation_entry:
        marks.append({"kind": "nation", "frame": int(f), "label": "%s enters" % name})
    if hq_cross_f is not None:
        marks.append({"kind": "migration", "frame": int(hq_cross_f), "label": "the migration: HQ crosses to linux"})
    # the offload storm: the first day the trailing 7-day offload count reaches marks_storm_frac of its peak
    tau = clock.tau_frames()
    nd = int(np.ceil(clock.end_days)) + 2
    daily = np.bincount(np.clip(np.floor(tau + 1e-9).astype(np.int64), 0, nd - 1), weights=offload_f, minlength=nd)
    roll = np.convolve(daily, np.ones(7), "full")[:nd]
    if roll.max() > 0:
        frac = float(params["marks_storm_frac"])
        d = int(np.argmax(roll >= frac * roll.max()))
        f = int(np.argmax(tau >= d)) if (tau >= d).any() else F - 1
        marks.append({"kind": "storm", "frame": f, "label": "the offload storm begins"})
    reg = []
    for name in ("commits", "launches", "files"):
        reg += regimes(name, series[name], clock, params)
    marks += reg
    marks.sort(key=lambda m: (m["frame"], m["kind"], m["label"]))
    diag = {"regime_breaks": [{"series": m["_series"], "day": m["_day"], "frame": m["frame"], "label": m["label"]} for m in marks if m["kind"] == "regime"],
            "storm_peak_7d_calls": int(roll.max())}
    for m in marks:
        m.pop("_series", None); m.pop("_day", None)
    return marks, diag
