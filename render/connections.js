// Recorded connection memory. Latest past event per edge; age in story days.
(function () {
  const KW = window.KW, D = KW.D, U = KW.util;
  if (!D.connection_expire_days) return;
  const hold = D.connection_hold_days, end = D.connection_expire_days;
  KW.connectionFade = (f, last) => {
    if (last < 0 || last > f) return 0;
    const age = KW.tau[f] - KW.tau[last];
    return age <= hold ? 1 : age >= end ? 0 : 1 - (age - hold) / (end - hold);
  };
  const hx = U.f32(D.hqx), hy = U.f32(D.hqy), host = U.u8(D.hqh);
  const histories = new Map(), clocks = new Map();
  function record(key, event) { if (!histories.has(key)) histories.set(key, []); histories.get(key).push(event); }
  function stamp(key, f) { if (!clocks.has(key)) clocks.set(key, []); clocks.get(key).push(f); }
  function lastBefore(rows, f, frame) {
    let lo = 0, hi = rows.length;
    while (lo < hi) { const m = (lo + hi) >> 1; if (frame(rows[m]) <= f) lo = m + 1; else hi = m; }
    return lo ? rows[lo - 1] : null;
  }
  KW.connectionLast = (key, f) => { const rows = clocks.get(key); return rows ? lastBefore(rows, f, x => x) ?? -1 : -1; };
  const bf = U.i32(D.bfirst), ba = U.u16(D.bra), bb = U.u16(D.brb);
  const sf = U.i32(D.spf), sx = U.f32(D.spx1), sy = U.f32(D.spy1);
  for (let b = 0; b < D.nb; b++) stamp('bridge:' + b, bf[b]);
  for (let s = 0; s < D.nsp; s++) stamp('spur:' + s, sf[s]);
  for (let i = 0; i < KW.nl; i++) {
    const f = KW.lf[i], regions = new Set([KW.lreg[i]]);
    for (let k = KW.wstart[i]; k < KW.wstart[i + 1]; k++) {
      regions.add(KW.wreg[k]);
      if (KW.wkind[k] === 1) for (let s = 0; s < D.nsp; s++) {
        if (Math.abs(sx[s] - KW.wx[k]) < 0.01 && Math.abs(sy[s] - KW.wy[k]) < 0.01) stamp('spur:' + s, KW.wf[k]);
      }
    }
    for (let b = 0; b < D.nb; b++) if (f >= bf[b] && regions.has(ba[b]) && regions.has(bb[b])) stamp('bridge:' + b, f);
    if (KW.lshape[i] === 1) {
      for (let k = KW.wstart[i]; k < KW.wstart[i + 1]; k++) record('burst:' + host[f] + ':' + KW.wreg[k],
        {f: KW.wf[k], x0: hx[f], y0: hy[f], x1: KW.wx[k], y1: KW.wy[k]});
    } else if (KW.lshape[i] === 2) {
      for (let k = KW.ustart[i]; k < KW.ustart[i + 1]; k++) record('converge:' + KW.ux[k] + ':' + KW.uy[k] + ':' + KW.lreg[i],
        {f, x0: KW.ux[k], y0: KW.uy[k], x1: KW.lx[i], y1: KW.ly[i]});
    }
  }
  const bs = U.i32(D.bs), br = U.u16(D.br);
  for (let f = 0; f < D.F; f++) {
    for (let k = bs[f]; k < bs[f + 1]; k++) {
      const r = br[k]; if (KW.rfirst[r] > f) continue;
      record('project:' + host[f] + ':' + r, {f, x0: hx[f], y0: hy[f], x1: KW.rx[r], y1: KW.ry[r]});
    }
  }
  for (const name of ['omen-linux', 'am4', 'fx99']) {
    const seat = U.u8(D.seat[name]), b = D.bcn[name]; if (!b) continue;
    for (let f = 0; f < D.F; f++) if (seat[f]) record('seat:' + host[f] + ':' + name, {f, x0: hx[f], y0: hy[f], x1: b[0], y1: b[1]});
  }
  for (const rows of histories.values()) rows.sort((a,b) => a.f - b.f);
  for (const rows of clocks.values()) rows.sort((a,b) => a - b);
  KW.registerLayer({id: 'connection-memory', z: 43, map: true, render(ctx, f) {
    const v = KW.view(f); ctx.lineWidth = 1; ctx.strokeStyle = KW_SYS.color.fg2;
    for (const rows of histories.values()) {
      const e = lastBefore(rows, f, x => x.f); if (!e) continue;
      const fade = KW.connectionFade(f, e.f); if (!fade) continue;
      ctx.globalAlpha = 0.32 * fade * KW.codaK(f);
      const x0 = KW.sx(e.x0,v), y0 = KW.sy(e.y0,v), x1 = KW.sx(e.x1,v), y1 = KW.sy(e.y1,v);
      ctx.beginPath(); ctx.moveTo(x0,y0); ctx.quadraticCurveTo((x0+x1)/2-(y1-y0)*0.15,(y0+y1)/2+(x1-x0)*0.15,x1,y1); ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }});
})();
