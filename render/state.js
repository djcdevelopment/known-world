// state.js: buildState(f, out): checkpoint plus delta replay into preallocated scratch; live launches by binary search.
// Activity is per (tile, class group): A(f) = A(c) D(c, f) + sum w_i D(f_i, f), D = 2^-(dtau / half-life), exact.
(function () {
  const KW = window.KW, D = KW.D, U = KW.util;
  if (!D.R || D.version < 2) return;
  KW.R = D.R; KW.T = D.T; KW.G = D.G;
  KW.ds = U.i32(D.ds); KW.dr = U.u16(D.dr); KW.dg = U.u8(D.dg); KW.dw = U.f32(D.dw); KW.cpts = U.f32(D.cpts);
  KW.nl = D.nl; KW.lf = U.i32(D.lf); KW.lx = U.f32(D.lx); KW.ly = U.f32(D.ly); KW.lreg = U.u16(D.lreg); KW.lband = U.u8(D.lband); KW.lnat = U.u8(D.lnat);
  KW.lgen = U.u8(D.lgen); KW.lflags = U.u8(D.lflags); KW.llife = U.u16(D.llife); KW.lshape = U.u8(D.lshape); KW.lpre = U.u8(D.lpre);
  KW.wstart = U.i32(D.wstart); KW.wf = U.i32(D.wf); KW.wreg = U.u16(D.wreg); KW.wband = U.u8(D.wband); KW.wx = U.f32(D.wx); KW.wy = U.f32(D.wy); KW.wkind = U.u8(D.wkind);
  KW.ustart = U.i32(D.ustart); KW.ux = U.f32(D.ux); KW.uy = U.f32(D.uy);
  KW.cmask = U.u8(D.cmask);
  let maxLife = 0, maxPre = 0; for (let i = 0; i < KW.nl; i++) { if (KW.llife[i] > maxLife) maxLife = KW.llife[i]; if (KW.lpre[i] > maxPre) maxPre = KW.lpre[i]; }
  // warheads land after the departure: the longest tail is beam + spread + life
  KW.maxLife = Math.max(maxLife, 90) + 24 + D.beam_f + 40; KW.maxPre = maxPre;
  const RG = D.T * D.G;
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
    // live launches: first launch frame >= f - maxLife by binary search, then scan while lf - pre <= f
    let lo = 0, hi = KW.nl; const t = f - KW.maxLife;
    while (lo < hi) { const m = (lo + hi) >> 1; if (KW.lf[m] < t) lo = m + 1; else hi = m; }
    let n = 0;
    for (let i = lo; i < KW.nl && KW.lf[i] - KW.maxPre <= f; i++) if (KW.lf[i] - KW.lpre[i] <= f) out.live[n++] = i;
    out.nlive = n;
    return out;
  };
})();
