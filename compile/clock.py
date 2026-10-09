"""Clock: era schedule with glides (STRATEGY 4.1). One integer frame axis; every judgement downstream uses it.

Story time is tau, in days since the era-A start (2011-08-01Z). Output time s is seconds from the first story
frame (intro excluded). A is 4 s per calendar year (1/3 s per calendar month), B 2.5 s per calendar month, C 2.4 s
per UTC day. Each boundary gets glide_s seconds of log-rate smoothstep, integrated at 1 ms, centred on the boundary
in output time (the boundary date sits at the glide's midpoint). Deterministic; numpy only.
"""
import calendar
import datetime as dt

import numpy as np

DAY = 86400.0


def _epoch_days(date):
    y, m, d = map(int, date.split("-"))
    return calendar.timegm((y, m, d, 0, 0, 0)) / DAY


def _months(start_days, end_days):
    """Knot days at every calendar month start in [start, end]."""
    a = dt.datetime.fromtimestamp(start_days * DAY, dt.UTC)
    out = []
    y, m = a.year, a.month
    while True:
        t = calendar.timegm((y, m, 1, 0, 0, 0)) / DAY
        if t > end_days + 1e-9:
            break
        out.append(t)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


class Clock:
    def __init__(self, params, snapshot_epoch):
        self.p = params
        self.fps = params["fps"]
        e0 = _epoch_days(params["era_bounds"]["A"])
        eB = _epoch_days(params["era_bounds"]["B"])
        eC = _epoch_days(params["era_bounds"]["C"])
        eN = snapshot_epoch / DAY
        self.epoch0 = e0
        self.bounds_days = [eB - e0, eC - e0]
        self.end_days = eN - e0
        rA, rB, rC = (params["era_rates"][k]["seconds"] for k in "ABC")
        # base knots: (tau days, output seconds), piecewise linear, exact per calendar unit
        ks = [(0.0, 0.0)]
        s = 0.0
        for a, b in zip(_months(e0, eB)[:-1], _months(e0, eB)[1:]):
            s += rA / 12.0
            ks.append((b - e0, s))
        ms = _months(eB, eC)
        for a, b in zip(ms[:-1], ms[1:]):
            s += rB
            ks.append((b - e0, s))
        s += rC * (eN - eC)
        ks.append((eN - e0, s))
        # the C-era day grid is linear so one knot at the snapshot is exact
        self.base_tau = np.array([k[0] for k in ks])
        self.base_s = np.array([k[1] for k in ks])
        # mean rates in story days per output second
        r_A = 365.2425 / rA
        r_B = 30.436875 / rB
        r_C = 1.0 / rC
        g = float(params["glide_s"])
        self.rates = [r_A, r_B, r_C]
        windows = []
        if g > 0:
            for tb, r0, r1 in ((self.bounds_days[0], r_A, r_B), (self.bounds_days[1], r_B, r_C)):
                t = np.arange(0, int(round(g * 1000)) + 1) / 1000.0  # 1 ms grid across the window
                u = t / g
                r = np.exp(np.log(r0) + (np.log(r1) - np.log(r0)) * (3 * u * u - 2 * u ** 3))
                S = np.concatenate([[0.0], np.cumsum((r[1:] + r[:-1]) * 0.5 * 0.001)])  # story days since start
                I = float(S[-1])
                # Place the window so its two ends sit exactly on the base schedule: the glide then consumes
                # the same story span in the same glide_s as the base would, every later frame is unmoved and
                # the era lengths stay 46.7 / 87.5 / 534.1 s. The boundary date lands inside the window.
                lo, hi = 0.0, I
                for _ in range(80):
                    a = (lo + hi) / 2
                    f = np.interp(tb + (I - a), self.base_tau, self.base_s) - np.interp(tb - a, self.base_tau, self.base_s) - g
                    if f > 0:
                        lo = a
                    else:
                        hi = a
                a = (lo + hi) / 2
                windows.append((tb - a + S, t, tb, a))
        tau, out = [], []
        prev_end = -1.0
        self.glide_out = []  # (start s, boundary s, end s) per boundary, story-relative output seconds
        for (gtau, gt, tb, a) in windows:
            tL, tR = gtau[0], gtau[-1]
            for x, y in zip(self.base_tau, self.base_s):
                if prev_end < x < tL:
                    tau.append(float(x)); out.append(float(y))
            sL = float(np.interp(tL, self.base_tau, self.base_s))
            for x, y in zip(gtau, gt):
                tau.append(float(x)); out.append(sL + float(y))
            sb = sL + float(np.interp(tb, gtau, gt))
            self.glide_out.append((sL, sb, sL + g))
            prev_end = tR
        for x, y in zip(self.base_tau, self.base_s):
            if x > prev_end:
                tau.append(float(x)); out.append(float(y))
        self.tau_k = np.array(tau)
        self.s_k = np.array(out)
        # strictly increasing guard
        assert np.all(np.diff(self.tau_k) > 0) and np.all(np.diff(self.s_k) > 0)
        if not self.glide_out:
            self.glide_out = [(float(np.interp(b, self.tau_k, self.s_k)),) * 3 for b in self.bounds_days]
        self.story_s = float(self.s_k[-1])
        self.intro_s = float(params["intro_s"])
        self.coda_s = float(params["coda_s"])
        self.total_s = self.intro_s + self.story_s + self.coda_s
        self.F = int(round(self.total_s * self.fps))

    # --- forward map ---------------------------------------------------
    def tau_of_epoch(self, t_epoch):
        return np.asarray(t_epoch, dtype=np.float64) / DAY - self.epoch0

    def T(self, t_epoch):
        """Output second (intro included) of unix seconds; clamped to the story span."""
        tau = np.clip(self.tau_of_epoch(t_epoch), 0.0, self.end_days)
        return self.intro_s + np.interp(tau, self.tau_k, self.s_k)

    def frame(self, t_epoch):
        return np.floor(self.fps * self.T(t_epoch) + 1e-9).astype(np.int64)

    # --- per-frame series ----------------------------------------------
    def tau_frames(self):
        """tau[f]: story days at the start of each output frame; held through intro and coda."""
        s = np.arange(self.F) / self.fps - self.intro_s
        return np.interp(np.clip(s, 0.0, self.story_s), self.s_k, self.tau_k)

    def era_frames(self):
        """era index per frame (0 A, 1 B, 2 C); switches at the glide midpoint."""
        s = np.arange(self.F) / self.fps - self.intro_s
        era = np.zeros(self.F, dtype=np.uint8)
        for i, (_, mid, _) in enumerate(self.glide_out):
            era[s >= mid] = i + 1
        return era

    def rate_frames(self):
        """Story days per output second at each frame (the cut multiplies it)."""
        tau = self.tau_frames()
        s = np.arange(self.F) / self.fps - self.intro_s
        h = 1.0 / self.fps
        a = np.interp(np.clip(s, 0, self.story_s), self.s_k, self.tau_k)
        b = np.interp(np.clip(s + h, 0, self.story_s), self.s_k, self.tau_k)
        return (b - a) / h

    def rate_labels(self):
        return ["1 yr = %g s" % self.p["era_rates"]["A"]["seconds"],
                "1 mo = %g s" % self.p["era_rates"]["B"]["seconds"],
                "1 day = %g s" % self.p["era_rates"]["C"]["seconds"]]

    def era_edges_s(self):
        """Output second (intro included) of each era boundary (glide midpoint) for strip ticks."""
        return [self.intro_s + m for (_, m, _) in self.glide_out]

    def summary(self):
        return {"frames": self.F, "total_s": round(self.total_s, 3), "story_s": round(self.story_s, 3),
                "intro_s": self.intro_s, "coda_s": self.coda_s,
                "boundary_out_s": [round(x, 3) for x in self.era_edges_s()],
                "era_len_s": [round(self.era_edges_s()[0] - self.intro_s, 3),
                              round(self.era_edges_s()[1] - self.era_edges_s()[0], 3),
                              round(self.intro_s + self.story_s - self.era_edges_s()[1], 3)]}
