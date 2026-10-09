// launch.js: launches in `lighter` (L 0.55 to 0.95), screen-constant radii by band; the luminance cap keeps 15 blooms
// from whiting out; fields (land, activity) draw in normal compositing capped at L 0.55.
(function () {
  const KW = window.KW, D = KW.D, P = KW.palette;
  if (!D.T || D.version < 2) return;
  const CAP = 2.5, TAU = 6.283185307179586;
  function bloom(ctx, x, y, ni, gi, band, age, life, scale) {
    if (age < 0 || age >= life) return;
    const t = age / life, a = (1 - t) * (1 - t) * scale;
    const R = D.radius_px[band - 1] * (1 + 0.25 * t);
    const g = ctx.createRadialGradient(x, y, 0, x, y, R);
    const L = P.genL(gi);
    g.addColorStop(0, P.rgba(ni, Math.min(0.95, L + 0.08), Math.min(1, a)));
    g.addColorStop(0.35, P.rgba(ni, L, Math.min(1, a * 0.7)));
    g.addColorStop(1, P.rgba(ni, L, 0));
    ctx.fillStyle = g;
    ctx.fillRect(x - R, y - R, 2 * R, 2 * R);
  }
  function weight(band, age, life) { if (age < 0 || age >= life) return 0; const t = age / life, r = D.radius_px[band - 1] / 15; return (1 - t) * (1 - t) * r * r; }
  function render(ctx, f) {
    const S = KW.getState(f), v = KW.view(f);
    ctx.globalCompositeOperation = 'lighter';
    let W = 0;
    for (let q = 0; q < S.nlive; q++) {
      const i = S.live[q];
      W += weight(KW.lband[i], f - KW.lf[i], KW.llife[i]);
      for (let k = KW.wstart[i]; k < KW.wstart[i + 1]; k++) W += weight(KW.wband[k], f - KW.wf[k], KW.llife[i]);
    }
    const sc = W > CAP ? CAP / W : 1;
    for (let q = 0; q < S.nlive; q++) {
      const i = S.live[q], ni = KW.lnat[i], gi = KW.lgen[i], fl = KW.lflags[i];
      const x = KW.sx(KW.lx[i], v), y = KW.sy(KW.ly[i], v), age = f - KW.lf[i], life = KW.llife[i];
      bloom(ctx, x, y, ni, gi, KW.lband[i], age, life, sc);
      for (let k = KW.wstart[i]; k < KW.wstart[i + 1]; k++) bloom(ctx, KW.sx(KW.wx[k], v), KW.sy(KW.wy[k], v), ni, gi, KW.wband[k], f - KW.wf[k], life, sc * 0.8);
      if ((fl & 1) && age >= 0 && age < 36) {   // lineage-first: the ring that goes with the bell
        const t = age / 36;
        ctx.strokeStyle = P.rgba(ni, 0.85, 0.6 * (1 - t) * sc); ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(x, y, 8 + 20 * t, 0, TAU); ctx.stroke();
      }
      if ((fl & 8) && age >= 0 && age < life) {  // inferred (ChatGPT): hollow core, open ring
        ctx.strokeStyle = P.rgba(ni, 0.7, 0.5 * (1 - age / life) * sc); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(x, y, 5 + 3 * age / life, 0, TAU); ctx.stroke();
      }
    }
  }
  KW.registerLayer({ id: 'launches', z: 60, map: true, render });
})();
