// radio.js: the signal layer on the map. Comms beams HQ -> region (the countdown before a launch), ChatGPT rings into the void,
// offload sparks HQ -> seat beacons, the HQ ring and the beacons. Normal compositing for rings and beams (radio, not detonation);
// nothing here flashes per commit. The HQ crossing to omen-linux has no caption.
(function () {
  const KW = window.KW, D = KW.D, P = KW.palette, U = KW.util;
  if (!D.T || D.version < 2) return;
  const TAU = 6.283185307179586;
  const hqx = U.f32(D.hqx), hqy = U.f32(D.hqy), bs = U.i32(D.bs), br = U.u16(D.br), bw = U.u8(D.bw), bcn = U.u8(D.bcn_n), ringF = U.i32(D.ring_f);
  const seatNames = ['omen-linux', 'am4', 'fx99'], seat = seatNames.map(h => U.u8(D.seat[h]));
  const LOOK = 12;
  const seatFirst = seat.map(a => { for (let g = 0; g < a.length; g++) if (a[g] > 0) return g; return 1e9; });   // a beacon exists from its seat's first offload
  function beams(ctx, f) {
    const v = KW.view(f), hx = KW.sx(hqx[f], v), hy = KW.sy(hqy[f], v), ck = KW.codaK(f);
    ctx.lineWidth = 1;
    for (let g = Math.max(0, f - LOOK + 1); g <= f; g++) {
      const fade = 1 - (f - g) / LOOK;
      for (let k = bs[g]; k < bs[g + 1]; k++) {
        const r = br[k];
        if (KW.rfirst[r] > f) continue;
        const a = (bw[k] / 255) * 0.5 * fade * fade * ck;
        if (a < 0.02) continue;
        ctx.strokeStyle = P.rgba(bcn[k], 0.5, a);
        ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(KW.sx(KW.rx[r], v), KW.sy(KW.ry[r], v)); ctx.stroke();
      }
    }
  }
  function rings(ctx, f) {
    const v = KW.view(f), x = KW.sx(D.ring_xy[0], v), y = KW.sy(D.ring_xy[1], v), life = Math.max(12, Math.round(45 * D.env_scale + 8));
    let lo = 0, hi = ringF.length; while (lo < hi) { const m = (lo + hi) >> 1; if (ringF[m] < f - life) lo = m + 1; else hi = m; }
    const ni = D.nat_classes.indexOf('chatgpt');
    ctx.lineWidth = 1.2;
    for (let i = lo; i < ringF.length && ringF[i] <= f; i++) {
      const t = (f - ringF[i]) / life, r = 8 + 150 * t;
      ctx.strokeStyle = P.rgba(ni, 0.5, 0.35 * (1 - t) * (1 - t) * KW.codaK(f));
      ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.stroke();
    }
  }
  function sparks(ctx, f) {
    const v = KW.view(f), hx = KW.sx(hqx[f], v), hy = KW.sy(hqy[f], v), ni = D.nat_classes.indexOf('local_model');
    ctx.globalCompositeOperation = 'lighter';
    for (let s = 0; s < 3; s++) {
      const b = D.bcn[seatNames[s]]; if (!b || f < seatFirst[s]) continue;
      const bx = KW.sx(b[0], v), by = KW.sy(b[1], v);
      let act = 0;
      for (let g = Math.max(0, f - 14); g <= f; g++) act += seat[s][g] * (1 - (f - g) / 15);
      const lit = 1 - Math.exp(-act / 4);
      // beacon: a small diamond, brightness follows recent offloads
      ctx.fillStyle = P.rgba(ni, 0.5 + 0.35 * lit, 0.45 + 0.5 * lit);
      ctx.beginPath(); ctx.moveTo(bx, by - 5); ctx.lineTo(bx + 4, by); ctx.lineTo(bx, by + 5); ctx.lineTo(bx - 4, by); ctx.closePath(); ctx.fill();
      // one arc per seat per frame: the spark runs HQ -> beacon
      if (seat[s][f] > 0 && KW.sfirstSeat !== false) {
        const mx = (hx + bx) / 2 - (by - hy) * 0.2, my = (hy + by) / 2 + (bx - hx) * 0.2;
        ctx.strokeStyle = P.rgba(ni, 0.7, 0.55); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(hx, hy); ctx.quadraticCurveTo(mx, my, bx, by); ctx.stroke();
        const u = ((f * 5) % 10) / 10, w = 1 - u, px = w * w * hx + 2 * w * u * mx + u * u * bx, py = w * w * hy + 2 * w * u * my + u * u * by;
        ctx.fillStyle = P.rgba(ni, 0.9, 0.9); ctx.fillRect(px - 1.5, py - 1.5, 3, 3);
      }
    }
  }
  function hq(ctx, f) {
    const v = KW.view(f), x = KW.sx(hqx[f], v), y = KW.sy(hqy[f], v);
    ctx.strokeStyle = 'rgba(240,232,205,0.85)'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(x, y, 9, 0, TAU); ctx.stroke();
    ctx.fillStyle = 'rgba(240,232,205,0.9)'; ctx.beginPath(); ctx.arc(x, y, 2, 0, TAU); ctx.fill();
  }
  KW.registerLayer({ id: 'beams', z: 50, map: true, render: beams });
  KW.registerLayer({ id: 'rings', z: 51, map: true, render: rings });
  KW.registerLayer({ id: 'sparks', z: 52, map: true, render: sparks });
  KW.registerLayer({ id: 'hq', z: 65, map: true, render: (ctx, f) => { if (f >= D.hq_first) hq(ctx, f); } });
})();
