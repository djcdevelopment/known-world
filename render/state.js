// state.js: buildState(f, out): checkpoint plus delta replay into preallocated scratch; live launches by binary search.
(function () {
  const KW = window.KW, D = KW.D, U = KW.util;
  if (!D.R) return;
  KW.R = D.R; KW.G = D.G;
  KW.ds = U.i32(D.ds); KW.dr = U.u16(D.dr); KW.dg = U.u8(D.dg); KW.dw = U.f32(D.dw); KW.cpts = U.f32(D.cpts);
  KW.rx = U.f32(D.rx); KW.ry = U.f32(D.ry); KW.rrad = U.f32(D.rrad); KW.rfirst = U.i32(D.rfirst);
  KW.nl = D.nl; KW.lf = U.i32(D.lf); KW.lreg = U.u16(D.lreg); KW.lband = U.u8(D.lband); KW.lnat = U.u8(D.lnat); KW.lgen = U.u8(D.lgen);
  KW.lflags = U.u8(D.lflags); KW.llife = U.u16(D.llife);
  KW.wstart = U.i32(D.wstart); KW.wf = U.i32(D.wf); KW.wreg = U.u16(D.wreg); KW.wband = U.u8(D.wband);
  let maxLife = 0; for (let i = 0; i < KW.nl; i++) if (KW.llife[i] > maxLife) maxLife = KW.llife[i];
  KW.maxLife = Math.max(maxLife, 90) + 24;
  const RG = D.R * D.G;
  KW.newState = () => ({ exact: new Float64Array(RG), shown: new Float64Array(RG), live: new Int32Array(KW.nl + 1), nlive: 0 });
  const dec = (a, b) => Math.pow(2, -(KW.tau[b] - KW.tau[a]) / D.hl);
  let memoF = -1; const memo = KW.newState();
  KW.getState = function (f) { if (f !== memoF) { KW.buildState(f, memo); memoF = f; } return memo; };
  KW.buildState = function (f, out) {
    const cpE = D.cp_every, c = Math.floor(f / cpE) * cpE, ci = c / cpE, ex = out.exact, sh = out.shown;
    const k = dec(c, f), base = ci * RG;
    for (let i = 0; i < RG; i++) ex[i] = KW.cpts[base + i] * k;
    for (let g = c + 1; g <= f; g++) {
      const a = KW.ds[g], b = KW.ds[g + 1];
      if (b > a) { const kk = dec(g, f); for (let j = a; j < b; j++) ex[KW.dr[j] * D.G + KW.dg[j]] += KW.dw[j] * kk; }
    }
    sh.set(ex);
    // 0.3 s attack ramp (9 frames): the newest deltas count partially, so nothing pops
    for (let g = Math.max(0, f - 8); g <= f; g++) {
      const a = KW.ds[g], b = KW.ds[g + 1];
      if (b > a) { const kk = dec(g, f), ramp = (f - g + 1) / 9; for (let j = a; j < b; j++) sh[KW.dr[j] * D.G + KW.dg[j]] -= KW.dw[j] * kk * (1 - ramp); }
    }
    // live launches: first launch frame >= f - maxLife by binary search, then scan to f
    let lo = 0, hi = KW.nl; const t = f - KW.maxLife;
    while (lo < hi) { const m = (lo + hi) >> 1; if (KW.lf[m] < t) lo = m + 1; else hi = m; }
    let n = 0;
    for (let i = lo; i < KW.nl && KW.lf[i] <= f; i++) out.live[n++] = i;
    out.nlive = n;
    return out;
  };
})();
