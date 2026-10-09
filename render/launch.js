// launch.js: launches in `lighter` (L 0.55 to 0.95), screen-constant radii by band (one band table). Shapes:
//  single   one bloom at the touched tiles;
//  mirv     one beam from the HQ that splits at 60 % of its path into warheads arcing to their targets (regions or spurs),
//           each landing as a bloom sized by its share of the lines;
//  unified  lines converging from the warheads' sites, then a bloom one band larger (the compile already raised the band);
//  inferred hollow core and an open ring (reduced chroma: the nation is a guess).
// Under collapse (cmask) blooms merge per region into one bloom of the largest band. Total bloom luminance is capped.
(function () {
  const KW = window.KW, D = KW.D, P = KW.palette, U = KW.util;
  if (!D.T || D.version < 2) return;
  const CAP = 2.5, TAU = 6.283185307179586, hqx = U.f32(D.hqx), hqy = U.f32(D.hqy);
  function bloom(ctx, x, y, ni, gi, band, age, life, scale, hollow) {
    if (age < 0 || age >= life) return;
    const t = age / life, a = (1 - t) * (1 - t) * scale;
    const R = D.radius_px[band - 1] * (1 + 0.25 * t);
    const g = ctx.createRadialGradient(x, y, 0, x, y, R);
    const L = P.genL(gi), c0 = hollow ? 0.05 : 1;
    g.addColorStop(0, P.rgba(ni, Math.min(0.95, L + 0.08), Math.min(1, a * c0)));
    g.addColorStop(0.35, P.rgba(ni, L, Math.min(1, a * 0.7)));
    g.addColorStop(1, P.rgba(ni, L, 0));
    ctx.fillStyle = g;
    ctx.fillRect(x - R, y - R, 2 * R, 2 * R);
  }
  function weight(band, age, life) { if (age < 0 || age >= life) return 0; const t = age / life, r = D.radius_px[band - 1] / 15; return (1 - t) * (1 - t) * r * r; }
  // quadratic arc point and its path
  function arcPt(x0, y0, x1, y1, u, sg) {
    const mx = (x0 + x1) / 2 - (y1 - y0) * 0.25 * sg, my = (y0 + y1) / 2 + (x1 - x0) * 0.25 * sg, w = 1 - u;
    return [w * w * x0 + 2 * w * u * mx + u * u * x1, w * w * y0 + 2 * w * u * my + u * u * y1];
  }
  function arcLine(ctx, x0, y0, x1, y1, u0, u1, sg) {
    ctx.beginPath(); const n = 8;
    for (let k = 0; k <= n; k++) { const p = arcPt(x0, y0, x1, y1, u0 + (u1 - u0) * k / n, sg); if (k === 0) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]); }
    ctx.stroke();
  }
  function render(ctx, f) {
    const S = KW.getState(f), v = KW.view(f), collapsed = KW.cmask[f] === 1;
    ctx.globalCompositeOperation = 'lighter';
    const B = D.beam_f, merged = new Map();
    let W = 0;
    for (let q = 0; q < S.nlive; q++) {
      const i = S.live[q], sh = KW.lshape[i];
      if (sh === 1 && KW.wstart[i + 1] > KW.wstart[i]) { for (let k = KW.wstart[i]; k < KW.wstart[i + 1]; k++) W += weight(KW.wband[k], f - KW.wf[k], KW.llife[i]); }
      else W += weight(KW.lband[i], f - KW.lf[i], KW.llife[i]);
    }
    const sc = W > CAP ? CAP / W : 1;
    function put(reg, x, y, ni, gi, band, age, life, hollow) {
      if (age < 0 || age >= life) return;
      if (!collapsed) { bloom(ctx, x, y, ni, gi, band, age, life, sc, hollow); return; }
      const m = merged.get(reg);
      if (!m) merged.set(reg, { x, y, ni, gi, band, age, life, n: 1, hollow });
      else { m.n++; if (band > m.band) { m.band = band; m.ni = ni; m.gi = gi; } if (age < m.age) { m.age = age; m.life = life; } }
    }
    for (let q = 0; q < S.nlive; q++) {
      const i = S.live[q], ni = KW.lnat[i], gi = KW.lgen[i], fl = KW.lflags[i], sh = KW.lshape[i];
      const life = KW.llife[i], age = f - KW.lf[i], reg = KW.lreg[i];
      const x = KW.sx(KW.lx[i], v), y = KW.sy(KW.ly[i], v), hollow = (fl & 8) !== 0;
      const w0 = KW.wstart[i], w1 = KW.wstart[i + 1];
      if (sh === 1 && w1 > w0) {
        // one beam HQ -> split point, then warheads
        const hx = KW.sx(hqx[KW.lf[i]], v), hy = KW.sy(hqy[KW.lf[i]], v);
        let cxm = 0, cym = 0; for (let k = w0; k < w1; k++) { cxm += KW.sx(KW.wx[k], v); cym += KW.sy(KW.wy[k], v); }
        cxm /= (w1 - w0); cym /= (w1 - w0);
        const px = hx + (cxm - hx) * D.split_at, py = hy + (cym - hy) * D.split_at, fsplit = D.split_at * B;
        if (!collapsed) {
          const tail = Math.max(0, age - fsplit);
          if (age >= 0 && age < fsplit + 14) {
            const a = age < fsplit ? 1 : 1 - (age - fsplit) / 14, u1 = Math.min(1, age / fsplit), u0 = Math.max(0, u1 - 0.55);
            ctx.strokeStyle = P.rgba(ni, 0.8, 0.75 * a * sc); ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(hx + (px - hx) * u0, hy + (py - hy) * u0); ctx.lineTo(hx + (px - hx) * u1, hy + (py - hy) * u1); ctx.stroke();
          }
          for (let k = w0; k < w1; k++) {
            const tx = KW.sx(KW.wx[k], v), ty = KW.sy(KW.wy[k], v), land = KW.wf[k], sg = (k % 2 ? 1 : -1);
            if (f > fsplit + KW.lf[i] - 1 && f < land + 10) {
              const u1 = Math.max(0, Math.min(1, (f - KW.lf[i] - fsplit) / Math.max(1, land - KW.lf[i] - fsplit))), u0 = Math.max(0, u1 - 0.4);
              const a = f < land ? 0.8 : 0.8 * (1 - (f - land) / 10);
              ctx.strokeStyle = P.rgba(ni, 0.78, a * sc); ctx.lineWidth = 1.2;
              arcLine(ctx, px, py, tx, ty, u0, u1, sg);
            }
          }
        }
        for (let k = w0; k < w1; k++) put(KW.wreg[k], KW.sx(KW.wx[k], v), KW.sy(KW.wy[k], v), ni, gi, KW.wband[k], f - KW.wf[k], life, hollow);
      } else {
        if (sh === 2 && !collapsed && KW.ustart[i + 1] > KW.ustart[i] && age < 0) {
          const p = (age + KW.lpre[i]) / Math.max(1, KW.lpre[i]);
          ctx.strokeStyle = P.rgba(ni, 0.8, 0.55 * sc); ctx.lineWidth = 1.2;
          for (let k = KW.ustart[i]; k < KW.ustart[i + 1]; k++) {
            const sx = KW.sx(KW.ux[k], v), sy = KW.sy(KW.uy[k], v);
            ctx.beginPath(); ctx.moveTo(sx + (x - sx) * Math.max(0, p - 0.45), sy + (y - sy) * Math.max(0, p - 0.45)); ctx.lineTo(sx + (x - sx) * p, sy + (y - sy) * p); ctx.stroke();
          }
        }
        put(reg, x, y, ni, gi, KW.lband[i], age, life, hollow);
        if ((fl & 1) && age >= 0 && age < 36) {   // lineage-first: the ring that goes with the bell
          const t = age / 36;
          ctx.strokeStyle = P.rgba(ni, 0.85, 0.6 * (1 - t) * sc); ctx.lineWidth = 1.5;
          ctx.beginPath(); ctx.arc(x, y, 8 + 20 * t, 0, TAU); ctx.stroke();
        }
        if (hollow && age >= 0 && age < life) {  // inferred (ChatGPT): an open ring, gap at the top right
          ctx.strokeStyle = P.rgba(ni, 0.7, 0.55 * (1 - age / life) * sc); ctx.lineWidth = 1.2;
          const r = D.radius_px[KW.lband[i] - 1] * 0.45 + 3 * age / life;
          ctx.beginPath(); ctx.arc(x, y, r, 0.35, TAU - 0.35); ctx.stroke();
        }
      }
    }
    if (collapsed) {
      const keys = Array.from(merged.keys()).sort((a, b) => a - b);
      for (const k of keys) { const m = merged.get(k); bloom(ctx, m.x, m.y, m.ni, m.gi, Math.min(6, m.band + (m.n >= 4 ? 1 : 0)), m.age, m.life, sc, m.hollow); }
    }
  }
  KW.registerLayer({ id: 'launches', z: 60, map: true, render });
})();
