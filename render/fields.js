// fields.js: regions as dots (explored, dim) and the activity glow. Normal compositing, lightness capped at 0.55.
(function () {
  const KW = window.KW, D = KW.D, P = KW.palette;
  if (!D.R) return;
  const TAU = 6.283185307179586;
  KW.fieldMaxL = 0.55;
  function dots(ctx, f) {
    ctx.fillStyle = 'rgba(52,60,76,0.85)';
    ctx.beginPath();
    for (let r = 0; r < D.R; r++) {
      const ff = KW.rfirst[r];
      if (ff <= f && f - ff >= 9) { ctx.moveTo(KW.rx[r] + KW.rrad[r], KW.ry[r]); ctx.arc(KW.rx[r], KW.ry[r], KW.rrad[r], 0, TAU); }
    }
    ctx.fill();
    for (let r = 0; r < D.R; r++) {
      const ff = KW.rfirst[r];
      if (ff <= f && f - ff < 9) { ctx.fillStyle = 'rgba(52,60,76,' + (0.85 * (f - ff + 1) / 9).toFixed(3) + ')'; ctx.beginPath(); ctx.arc(KW.rx[r], KW.ry[r], KW.rrad[r], 0, TAU); ctx.fill(); }
    }
  }
  function glow(ctx, f) {
    const S = KW.getState(f);
    const G = D.G;
    for (let r = 0; r < D.R; r++) {
      if (KW.rfirst[r] > f) continue;
      let tot = 0, best = 0, bg = 0;
      for (let g = 0; g < G; g++) { const v = S.shown[r * G + g]; tot += v; if (v > best) { best = v; bg = g; } }
      const norm = 1 - Math.exp(-tot / 6), q = Math.round(norm * 31) / 31;   // 32 levels
      if (q < 0.04) continue;
      const L = 0.20 + 0.35 * q, rad = KW.rrad[r] * (1.5 + 2.2 * q);
      const g = ctx.createRadialGradient(KW.rx[r], KW.ry[r], 0, KW.rx[r], KW.ry[r], rad);
      g.addColorStop(0, P.rgba(bg, L, 0.35 + 0.5 * q)); g.addColorStop(1, P.rgba(bg, L, 0));
      ctx.fillStyle = g; ctx.fillRect(KW.rx[r] - rad, KW.ry[r] - rad, 2 * rad, 2 * rad);
    }
  }
  KW.registerLayer({ id: 'dots', z: 10, render: dots });
  KW.registerLayer({ id: 'activity', z: 30, render: glow });
})();
