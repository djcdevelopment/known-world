// fields.js: the atlas. Sea lattice, land in three fog states (unknown = void, explored = dim terrain tint, active = lit by the
// last conductor's hue, normal compositing, L <= 0.55), ruins hatch, risen islands, harbours, bridges, spurs, notches.
// The page draws what the compile laid out; nothing here decides anything (no names, no judgement).
(function () {
  const KW = window.KW, D = KW.D, P = KW.palette, U = KW.util;
  if (!D.T || D.version < 2) return;
  const F = D.F, T = D.T, G = D.G, V = KW.VIEW;
  KW.fieldMaxL = 0.55;
  KW.ccx = U.f32(D.ccx); KW.ccy = U.f32(D.ccy); KW.cstart = U.i32(D.cstart); KW.tfirst = U.i32(D.tfirst); KW.thost = U.u8(D.thost); KW.tkind = U.u8(D.tkind);
  KW.tregion = U.u16(D.tregion); KW.tx = U.f32(D.tx); KW.ty = U.f32(D.ty);
  KW.rx = U.f32(D.rx); KW.ry = U.f32(D.ry); KW.rfirst = U.i32(D.rfirst);
  KW.cam = U.f32(D.camera);
  KW.view = f => { const i = f * 3; return { cx: KW.cam[i], cy: KW.cam[i + 1], s: KW.cam[i + 2] }; };
  KW.codaK = f => f < D.coda_f ? 1 : Math.max(0, 1 - (f - D.coda_f) / (4 * D.fps));
  KW.sx = (x, v) => V.cx + (x - v.cx) * v.s;
  KW.sy = (y, v) => V.cy + (y - v.cy) * v.s;
  const TAU = 6.283185307179586, RHO = 0.96;
  const HX = [0.8660254037844386, 0, -0.8660254037844386, -0.8660254037844386, 0, 0.8660254037844386];
  const HY = [0.5, 1, 0.5, -0.5, -1, -0.5];
  function hexAdd(p, x, y, r) { p.moveTo(x + HX[0] * r, y + HY[0] * r); for (let k = 1; k < 6; k++) p.lineTo(x + HX[k] * r, y + HY[k] * r); p.closePath(); }
  KW.hexAdd = hexAdd;
  // tiles by first frame (stable): explored set = prefix
  const order = []; for (let t = 0; t < T; t++) if (KW.tfirst[t] < F) order.push(t);
  order.sort((a, b) => KW.tfirst[a] - KW.tfirst[b] || a - b);
  const ofirst = new Int32Array(order.length); for (let i = 0; i < order.length; i++) ofirst[i] = KW.tfirst[order[i]];
  const ub = (v) => { let lo = 0, hi = ofirst.length; while (lo < hi) { const m = (lo + hi) >> 1; if (ofirst[m] <= v) lo = m + 1; else hi = m; } return lo; };   // count with first <= v
  KW.exploredOrder = order; KW.exploredCount = f => ub(f);
  // terrain tints by surface (omen-e, omen-c, omen-linux, am4, fx99) and three shades per tile id for texture
  const HOSTHUE = [255, 275, 165, 310, 60];
  const TL = D.terrain_L, TC = D.terrain_C;
  const TINT = HOSTHUE.map(h => TL.map(L => P.rgb(L, TC, h)));
  const TINTA = HOSTHUE.map(h => TL.map(L => (a) => P.rgbaRaw(L, TC, h, a)));
  KW.tint = TINT; KW.tintA = TINTA;
  const land = { n: -1, paths: null };
  function addTiles(paths, a, b) {
    for (let i = a; i < b; i++) {
      const t = order[i], k = KW.tkind[t];
      const p = k === 2 ? paths[15] : paths[KW.thost[t] * 3 + (t % 3)];
      for (let c = KW.cstart[t]; c < KW.cstart[t + 1]; c++) hexAdd(p, KW.ccx[c], KW.ccy[c], RHO);
    }
  }
  let hatch = null;
  function getHatch(ctx) {
    if (hatch) return hatch;
    const oc = document.createElement('canvas'); oc.width = 8; oc.height = 8; const o = oc.getContext('2d');
    o.fillStyle = P.rgb(0.27, 0.004, 250); o.fillRect(0, 0, 8, 8);
    o.strokeStyle = P.rgb(0.40, 0.004, 250); o.lineWidth = 1; o.beginPath(); o.moveTo(0, 8); o.lineTo(8, 0); o.moveTo(-2, 2); o.lineTo(2, -2); o.moveTo(6, 10); o.lineTo(10, 6); o.stroke();
    hatch = ctx.createPattern(oc, 'repeat'); return hatch;
  }
  function setWorld(ctx, v) { ctx.setTransform(v.s, 0, 0, v.s, V.cx - v.cx * v.s, V.cy - v.cy * v.s); }
  KW.setWorld = setWorld;
  function lattice(ctx, f) {
    const v = KW.view(f); if (v.s < 6) return;
    const dx = 1.7320508075688772 * v.s, dy = 1.5 * v.s;
    ctx.fillStyle = 'rgba(180,200,230,0.04)';
    ctx.beginPath();
    const r0 = Math.floor((V.y - V.cy) / dy + v.cy / 1.5) - 1, r1 = Math.ceil((V.y + V.h - V.cy) / dy + v.cy / 1.5) + 1;
    for (let r = r0; r <= r1; r++) {
      const y = V.cy + (r * 1.5 - v.cy) * v.s;
      const q0 = Math.floor((V.x - V.cx) / dx + v.cx / 1.7320508075688772 - r / 2) - 1, q1 = Math.ceil((V.x + V.w - V.cx) / dx + v.cx / 1.7320508075688772 - r / 2) + 1;
      for (let q = q0; q <= q1; q++) { const x = V.cx + (1.7320508075688772 * (q + r / 2) - v.cx) * v.s; ctx.rect(x - 0.5, y - 0.5, 1, 1); }
    }
    ctx.fill();
  }
  function drawLand(ctx, f) {
    const v = KW.view(f), n = ub(f), n9 = ub(f - 9);
    if (!land.paths || land.n > n9) { land.paths = []; for (let i = 0; i < 16; i++) land.paths.push(new Path2D()); land.n = 0; }
    if (n9 > land.n) { addTiles(land.paths, land.n, n9); land.n = n9; }
    setWorld(ctx, v);
    for (let h = 0; h < 5; h++) for (let sh = 0; sh < 3; sh++) { ctx.fillStyle = TINT[h][sh]; ctx.fill(land.paths[h * 3 + sh]); }
    // tiles revealed within the last 9 frames fade in
    for (let i = n9; i < n; i++) {
      const t = order[i], a = Math.min(1, (f - KW.tfirst[t] + 1) / 9);
      const p = new Path2D();
      for (let c = KW.cstart[t]; c < KW.cstart[t + 1]; c++) hexAdd(p, KW.ccx[c], KW.ccy[c], RHO);
      if (KW.tkind[t] === 2) { ctx.globalAlpha = a; ctx.fillStyle = 'rgb(66,67,70)'; } else ctx.fillStyle = TINTA[KW.thost[t]][t % 3](a);
      ctx.fill(p); ctx.globalAlpha = 1;
    }
    // ruins: grey hatch in screen scale
    const pat = getHatch(ctx);
    if (pat.setTransform) pat.setTransform(new DOMMatrix([1 / v.s, 0, 0, 1 / v.s, 0, 0]));
    ctx.fillStyle = pat; ctx.fill(land.paths[15]);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }
  // --- activity: lit tiles, last conductor's hue, <= L 0.55 ------------------------------------------------------------------
  KW.tileTot = new Float64Array(T); KW.regTot = new Float64Array(D.R);
  function drawActivity(ctx, f) {
    const v = KW.view(f), S = KW.getState(f), n = ub(f), ck = KW.codaK(f);
    const buckets = new Map();
    KW.regTot.fill(0);
    for (let i = 0; i < n; i++) {
      const t = order[i];
      let tot = 0, best = 0, bg = 0;
      for (let g = 0; g < G; g++) { const x = S.shown[t * G + g]; tot += x; if (x > best) { best = x; bg = g; } }
      tot *= ck;
      KW.tileTot[t] = tot; KW.regTot[KW.tregion[t]] += tot;
      const norm = 1 - Math.exp(-tot / 6), q = Math.round(norm * 31);   // 32 levels
      if (q < 1 || KW.tkind[t] === 2) continue;
      const key = bg * 32 + q;
      let p = buckets.get(key); if (!p) { p = new Path2D(); buckets.set(key, p); }
      for (let c = KW.cstart[t]; c < KW.cstart[t + 1]; c++) hexAdd(p, KW.ccx[c], KW.ccy[c], RHO);
    }
    setWorld(ctx, v);
    const keys = Array.from(buckets.keys()).sort((a, b) => a - b);
    for (const key of keys) {
      const g = Math.floor(key / 32), q = (key % 32) / 31, L = 0.20 + 0.35 * q;
      ctx.fillStyle = P.rgba(g, L, 0.30 + 0.62 * q); ctx.fill(buckets.get(key));
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }
  // --- islands, harbours, bridges, spurs, notches ----------------------------------------------------------------------------
  const ifirst = U.i32(D.ifirst), icx = U.f32(D.icx), icy = U.f32(D.icy), istart = U.i32(D.istart), ifork = U.u8(D.ifork), ix = U.f32(D.ix), iy = U.f32(D.iy);
  function drawIslands(ctx, f) {
    const v = KW.view(f); setWorld(ctx, v);
    for (let j = 0; j < D.ni; j++) {
      if (ifirst[j] > f) continue;
      const u = Math.min(1, (f - ifirst[j]) / 30), e = u * u * (3 - 2 * u), p = new Path2D();
      for (let c = istart[j]; c < istart[j + 1]; c++) hexAdd(p, icx[c], icy[c], RHO * (0.3 + 0.7 * e));
      ctx.fillStyle = ifork[j] ? P.rgbaRaw(0.30, 0.008, 250, e) : P.rgbaRaw(0.34, 0.035, 190, e);
      ctx.fill(p);
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }
  const hx = U.f32(D.hx), hy = U.f32(D.hy), hisl = U.u16(D.hisl), hreg = U.u16(D.hreg);
  const b0x = U.f32(D.b0x), b0y = U.f32(D.b0y), b1x = U.f32(D.b1x), b1y = U.f32(D.b1y), bra = U.u16(D.bra), brb = U.u16(D.brb), bkind = U.u8(D.bkind);
  KW.bridgeFrame = new Int32Array(D.nb); for (let b = 0; b < D.nb; b++) KW.bridgeFrame[b] = Math.max(KW.rfirst[bra[b]], KW.rfirst[brb[b]]);
  function drawLinks(ctx, f) {
    const v = KW.view(f), ck = KW.codaK(f);
    ctx.lineWidth = 1;
    // harbours: a landing on the coast of the home region, the day both the region and its island exist
    for (let h = 0; h < D.nh; h++) {
      const af = Math.max(KW.rfirst[hreg[h]], ifirst[hisl[h]]);
      if (af > f) continue;
      const x = KW.sx(hx[h], v), y = KW.sy(hy[h], v), x2 = KW.sx(ix[hisl[h]], v), y2 = KW.sy(iy[hisl[h]], v);
      const a = Math.min(1, (f - af + 1) / 18), dl = Math.hypot(x2 - x, y2 - y) || 1, dk = Math.max(3, Math.min(9, 1.6 * v.s));
      ctx.strokeStyle = P.rgbaRaw(0.55, 0.05, 185, 0.8 * a); ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + (x2 - x) / dl * dk, y + (y2 - y) / dl * dk); ctx.stroke();
      ctx.fillStyle = P.rgbaRaw(0.55, 0.05, 185, 0.9 * a); const r = Math.max(1, Math.min(2.5, 0.5 * v.s)); ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
    }
    // bridges: dark until both ends exist, then a hairline at the lower activity of the two
    for (let b = 0; b < D.nb; b++) {
      const bf = KW.bridgeFrame[b];
      if (bf > f || bf >= F) continue;
      const act = Math.min(KW.regTot[bra[b]], KW.regTot[brb[b]]);
      const age = f - bf, lit = age < 24 ? 1 - age / 24 : 0;
      const al = Math.min(0.9, 0.16 + 0.55 * (1 - Math.exp(-act / 6)) + 0.5 * lit);
      const x0 = KW.sx(b0x[b], v), y0 = KW.sy(b0y[b], v), x1 = KW.sx(b1x[b], v), y1 = KW.sy(b1y[b], v);
      const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, dx = x1 - x0, dy = y1 - y0, sg = (b % 2 ? 1 : -1) * 0.2;
      ctx.strokeStyle = bkind[b] ? P.rgbaRaw(0.55, 0.06, 85, al) : P.rgbaRaw(0.55, 0.06, 235, al);
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.quadraticCurveTo(mx - dy * sg, my + dx * sg, x1, y1); ctx.stroke();
    }
  }
  const spf = U.i32(D.spf), spx0 = U.f32(D.spx0), spy0 = U.f32(D.spy0), spx1 = U.f32(D.spx1), spy1 = U.f32(D.spy1), spreg = U.u16(D.spreg);
  const nof = U.i32(D.nof), nx = U.f32(D.nx), ny = U.f32(D.ny), nux = U.f32(D.nux), nuy = U.f32(D.nuy);
  function drawSpurs(ctx, f) {
    const v = KW.view(f);
    for (let k = 0; k < D.nsp; k++) {
      if (spf[k] > f) continue;
      const age = KW.tau[f] - KW.tau[spf[k]], fac = 0.3 + 0.7 * Math.pow(2, -age / D.hl);
      const ramp = Math.min(1, (f - spf[k] + 1) / 12);
      const x0 = KW.sx(spx0[k], v), y0 = KW.sy(spy0[k], v), x1 = x0 + (KW.sx(spx1[k], v) - x0) * fac * ramp, y1 = y0 + (KW.sy(spy1[k], v) - y0) * fac * ramp;
      ctx.strokeStyle = P.rgbaRaw(0.55, 0.02, 250, 0.4 + 0.5 * fac); ctx.lineWidth = Math.max(1, Math.min(2, 0.35 * v.s));
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    }
    ctx.lineWidth = Math.max(1, Math.min(2.2, 0.4 * v.s)); ctx.strokeStyle = 'rgba(7,9,14,0.9)';
    for (let k = 0; k < D.nn; k++) {
      if (nof[k] > f) continue;
      const x = KW.sx(nx[k], v), y = KW.sy(ny[k], v), L = Math.max(1.5, 0.9 * v.s);
      ctx.beginPath(); ctx.moveTo(x - nux[k] * L, y - nuy[k] * L); ctx.lineTo(x + nux[k] * L * 0.6, y + nuy[k] * L * 0.6); ctx.stroke();
    }
  }
  KW.registerLayer({ id: 'lattice', z: 5, map: true, render: lattice });
  KW.registerLayer({ id: 'land', z: 10, map: true, render: drawLand });
  KW.registerLayer({ id: 'islands', z: 20, map: true, render: drawIslands });
  KW.registerLayer({ id: 'activity', z: 30, map: true, render: drawActivity });
  KW.registerLayer({ id: 'links', z: 40, map: true, render: drawLinks });
  KW.registerLayer({ id: 'spurs', z: 41, map: true, render: drawSpurs });
})();
