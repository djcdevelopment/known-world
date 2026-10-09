// ia.js: the information architecture layers (DIRECTION rev 5, layout ia): the timeline zone at the bottom and the coast labels on the map.
// The timeline is one horizontal time axis shared by three sections: the marks ruler (date ticks and the marks.json hashmarks), the chatter and
// commit band, and the lineage lanes (the stream turned horizontal). The trailing stream_window_s (20 film s) fills the axis, "now" at the right
// edge, scrolling left at a constant 3 px per film frame (landscape export). A section renders only when it has signal: the ruler always, the band
// from the first chatter or commit, the lanes from the first lane. Lanes keep fixed vertical slots while visible; nothing slides.
// Everything is a lookup in tables the compile laid out; no Date, no Math.random.
(function () {
  const KW = window.KW, D = KW.D, LY = KW.LAY, I = LY.ia;
  if (!I || !D.T || D.version < 2) return;
  const U = KW.util, F = D.F, P = KW.palette, FONT = '"JetBrains Mono", monospace', S = D.stream, por = LY.mode === 'portrait';
  const WF = I.window_f, PXF = I.pxf, AX0 = I.ax0, AX1 = I.ax1, W = LY.W;
  const NP = I.namePx, CW = NP * 0.6, NCH = Math.max(6, Math.floor((I.nameW - 6) / CW));
  let RULER_Y = I.ruler[1], RULER_H = I.ruler[3], BAND_Y = I.band[1], BAND_H = I.band[3], LANE_Y = I.lanes[1], TL_Y = I.tl[1], TL_H = I.tl[3];
  const PITCH = I.pitch;
  // portrait: the zone is closed (ruler + band) unless the lanes are opened (KW.ui.lanes), when it grows up; landscape always shows the lanes
  function setZ() {
    const z = por ? (KW.ui.lanes ? I.open : I.closed) : I;
    RULER_Y = z.ruler[1]; RULER_H = z.ruler[3]; BAND_Y = z.band[1]; BAND_H = z.band[3]; LANE_Y = z.lanes[1]; TL_Y = z.tl[1]; TL_H = z.tl[3];
    KW.timelineRects = { ruler: [0, RULER_Y, W, RULER_H], band: [0, BAND_Y, W, BAND_H], lanes: [0, LANE_Y, W, I.nl * PITCH], open: !por || !!KW.ui.lanes };
  }
  const lanesShown = () => !por || !!KW.ui.lanes;
  const xOf = (f, g) => AX1 - (f - g) * PXF;
  const lb = (arr, n, v) => { let lo = 0, hi = n; while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] < v) lo = m + 1; else hi = m; } return lo; };
  const ub = (arr, n, v) => { let lo = 0, hi = n; while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] <= v) lo = m + 1; else hi = m; } return lo; };
  const clip = (t, n) => t.length > n ? t.slice(0, n - 1) + '…' : t;
  // ---- signal gates: the first frame each section has anything to show (a scan of the compiled tables, once) --------------------------------
  const band = U.u8(D.band);
  let bandFirst = F;
  for (let g = 0; g < F && bandFirst === F; g++) for (let c = 0; c < 5; c++) if (band[c * F + g] > 0) { bandFirst = g; break; }
  const K = S ? S.K : 0;
  const sid = S ? U.u8(S.sid) : null, sx = S ? U.f32(S.sx) : null, ss = S ? U.i32(S.ss) : null, sq = S ? U.u8(S.sq) : null;
  let laneFirst = F;
  if (S) for (let g = 0; g < F; g++) if (sid[g * K] !== 255) { laneFirst = g; break; }
  KW.gates = { band: bandFirst, lanes: laneFirst };
  const bnames = D.band_names, bcol = bnames.map(n => D.nat_classes.indexOf(n));
  const N = D.nat_names.length;
  const nat = []; for (let i = 0; i < N; i++) nat.push(P.flat(i, 0.74, 0.62));
  // ---- stream tables ------------------------------------------------------------------------------------------------------------------------
  let cf, cl, cn, cc, cs, bf, rf0, rf1, rlane, rflag, rside, mf, mnat, mstart, mlane, ef, ea, eb, tf, tl, tlab;
  if (S) {
    cf = U.i32(S.cf); cl = U.u8(S.cl); cn = U.u8(S.cn); cc = U.u8(S.cc); cs = U.u8(S.cs); bf = U.i32(S.bf);
    rf0 = U.i32(S.rf0); rf1 = U.i32(S.rf1); rlane = U.u8(S.rlane); rflag = U.u8(S.rflag); rside = U.u8(S.rside);
    mf = U.i32(S.mf); mnat = U.u8(S.mnat); mstart = U.i32(S.mstart); mlane = U.u8(S.mlane);
    ef = U.i32(S.ef); ea = U.u8(S.ea); eb = U.u8(S.eb); tf = U.i32(S.tf); tl = U.u8(S.tl); tlab = S.tlab;
  }
  const slotOf = new Int16Array(S ? S.L : 1), sinceOf = new Int32Array(S ? S.L : 1);
  const RAIL_OFF = [3.5, -3.5, 5.5, -5.5].map(v => v * PITCH / 12), PAIR = 2.5 * PITCH / 12;
  const MARK_RANK = { nation: 0, surface: 1, era: 2, migration: 3, storm: 4, regime: 5 };
  const marks = (D.marks || []).slice().sort((a, b) => (MARK_RANK[a.kind] - MARK_RANK[b.kind]) || (b.frame - a.frame));

  function ruler(ctx, f) {
    const y0 = RULER_Y, h = RULER_H;
    ctx.save(); ctx.beginPath(); ctx.rect(1, y0, W - 2, h); ctx.clip();
    ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left'; ctx.font = (por ? 9 : 10) + 'px ' + FONT;
    if (S) {
      const t0 = lb(tf, S.nt, f - WF), t1 = ub(tf, S.nt, f);
      let lastRight = -1e9;   // labels are thinned: one is written only when it clears the previous one (dense eras, the cut's day ticks)
      for (let i = t0; i < t1; i++) {
        const x = Math.round(xOf(f, tf[i])), lv = tl[i];
        if (lv === 2) { ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.40)'; ctx.fillRect(x, y0, 1, h); }
        else if (lv === 1) { ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.45)'; ctx.fillRect(x, y0, 1, 7); }
        else { ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.20)'; ctx.fillRect(x, y0, 1, 3); }
        if (tlab[i] && x + 3 > lastRight + 6) { ctx.fillStyle = 'rgba(' + KW.C.mutedRgb + ',0.85)'; ctx.fillText(tlab[i], x + 3, y0 + 9); lastRight = x + 3 + tlab[i].length * (por ? 5.4 : 6); }
      }
    }
    // marks: a kind-coloured tick on the lower row, the label to the left of the tick, skipped when it would overlap one already written
    const occ = [];
    const cw = por ? 5.4 : 6.0;
    for (const m of marks) {
      if (m.frame > f || m.frame < f - WF) continue;
      if (SCORE_ON && !SCORE_KINDS[m.kind]) continue;
      const x = Math.round(xOf(f, m.frame));
      ctx.fillStyle = KW.markColor(m.kind, 0.85); ctx.fillRect(x, y0 + 11, 1, h - 12);
      if (SCORE_ON) continue;   // the score writes the letter itself
      const w = m.label.length * cw, a = x - 4 - w, b = x - 3;
      if (occ.some(o => a < o[1] + 4 && b > o[0] - 4)) continue;
      occ.push([a, b]);
      ctx.fillStyle = KW.markColor(m.kind, m.kind === 'regime' ? 0.75 : 0.95); ctx.fillText(m.label, a, y0 + h - 3);
    }
    ctx.restore();
  }

  function bandSec(ctx, f) {
    const y0 = BAND_Y, h = BAND_H, mid = y0 + Math.round(h * 0.5), K1 = h / 120, ck = KW.codaK(f);
    ctx.save(); ctx.beginPath(); ctx.rect(1, y0, W - 2, h); ctx.clip();
    ctx.fillStyle = '#222b3b'; ctx.fillRect(AX0, mid, AX1 - AX0, 1);
    const cwid = Math.max(1, PXF);
    for (let g = Math.max(0, f - WF + 1); g <= f; g++) {
      const x = AX1 - (f - g + 1) * PXF;
      let y = mid - 1;
      for (let c = 0; c < 4; c++) {   // chatter above the centre line by class, log-scaled, stacked
        const a = band[c * F + g] / 255 * 22 * ck * K1 * 1.6;
        if (a < 0.5) continue;
        ctx.fillStyle = P.flat(bcol[c], 0.62, 0.85); ctx.fillRect(x, y - a, cwid, a); y -= a;
      }
      const cm = band[4 * F + g] / 255 * 50 * ck * K1 * 1.1;   // commits below, warm grey
      if (cm >= 0.5) { ctx.fillStyle = 'rgba(150,135,112,0.8)'; ctx.fillRect(x, mid + 2, cwid, cm); }
      const o = band[5 * F + g] / 255;   // offloads: an ember mark on the centre line
      if (o > 0.02) { ctx.fillStyle = P.flat(D.nat_classes.indexOf('local_model'), 0.6, Math.min(1, 0.25 + o)); ctx.fillRect(x, mid - 1, cwid, 2); }
    }
    ctx.restore();
    if (sq && sq[f] > 0) { ctx.font = (por ? 9 : 11) + 'px ' + FONT; ctx.textAlign = 'left'; ctx.fillStyle = KW.C.muted2; ctx.fillText('+' + sq[f] + ' quiet', I.nameX + 4, y0 + h - 6); }
  }

  function lanesSec(ctx, f) {
    const yc = slot => LANE_Y + slot * PITCH + PITCH / 2;
    const base = f * K, vis = [];
    for (let k = 0; k < K; k++) { const id = sid[base + k]; if (id === 255) break; slotOf[id] = Math.round(sx[base + k]); sinceOf[id] = ss[base + k]; vis.push(id); }
    ctx.save(); ctx.beginPath(); ctx.rect(1, LANE_Y - 2, W - 2, I.lanes[3] + 3); ctx.clip();
    ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left'; ctx.lineWidth = 1;
    const xa0 = id => Math.max(AX0, Math.round(xOf(f, Math.max(sinceOf[id], f - WF))));
    // lane hairlines and paired rails (a lineage on two surfaces runs as two rails joined at the bridge frame)
    for (const id of vis) {
      const y = Math.round(yc(slotOf[id])) + 0.5, b = bf[id], xs = xa0(id);
      ctx.strokeStyle = 'rgba(' + KW.C.mutedRgb + ',0.28)'; ctx.beginPath();
      if (b >= 0 && b <= f) {
        const xb = Math.max(xs, Math.round(xOf(f, Math.max(b, f - WF))));
        if (b >= f - WF) { ctx.moveTo(xs, y); ctx.lineTo(xb, y); ctx.moveTo(xb, y - PAIR); ctx.lineTo(xb, y + PAIR); }
        ctx.moveTo(xb, y - PAIR); ctx.lineTo(AX1, y - PAIR); ctx.moveTo(xb, y + PAIR); ctx.lineTo(AX1, y + PAIR);
      } else { ctx.moveTo(xs, y); ctx.lineTo(AX1, y); }
      ctx.stroke();
    }
    // rails: branches and worktrees fork a thin parallel rail, rejoining at a unified launch or fading
    for (let r = 0; r < S.nr; r++) {
      const a0 = rf0[r]; if (a0 > f) break;
      const a1 = rf1[r], id = rlane[r]; if (a1 < f - WF || sinceOf[id] === undefined || !vis.includes(id)) continue;
      const y0 = Math.round(yc(slotOf[id])) + 0.5, y = Math.round(yc(slotOf[id]) + RAIL_OFF[rside[r]]) + 0.5, wt = rflag[r] & 1, jn = rflag[r] & 2;
      const xa = Math.max(AX0, Math.round(xOf(f, Math.max(a0, f - WF)))), xz = Math.round(xOf(f, Math.min(a1, f)));
      ctx.strokeStyle = (wt ? 'rgba(196,164,112,0.55)' : 'rgba(112,150,196,0.55)');
      ctx.beginPath(); ctx.moveTo(xa, y); ctx.lineTo(xz, y);
      if (a0 >= f - WF) { ctx.moveTo(xa, y0); ctx.lineTo(xa + 3, y); }
      if (jn && a1 <= f) { ctx.moveTo(xz, y); ctx.lineTo(xz + 5, y0); }
      ctx.stroke();
      if (!jn && a1 <= f) { ctx.fillStyle = wt ? 'rgba(196,164,112,0.4)' : 'rgba(112,150,196,0.4)'; ctx.fillRect(xz, y - 1, 2, 2); }
    }
    // association: a faint vertical connector per cross-constellation edge where both lanes first stood together
    for (let e = 0; e < S.ne; e++) {
      if (ef[e] > f || ef[e] < f - WF) continue;
      const A = ea[e], B = eb[e]; if (!vis.includes(A) || !vis.includes(B)) continue;
      const x = Math.round(xOf(f, ef[e])) + 0.5, ya = Math.round(yc(slotOf[A])), yb = Math.round(yc(slotOf[B]));
      ctx.strokeStyle = 'rgba(201,195,168,0.30)'; ctx.beginPath(); ctx.moveTo(x, ya); ctx.lineTo(x, yb); ctx.stroke();
      ctx.fillStyle = 'rgba(201,195,168,0.45)'; ctx.fillRect(x - 1.5, ya - 1, 3, 3); ctx.fillRect(x - 1.5, yb - 1, 3, 3);
    }
    // ticks: commits. Dot area by log(lines, capped), hue by nation, density by overlap ('lighter')
    const c0 = lb(cf, S.n, Math.max(0, f - WF + 1)), c1 = ub(cf, S.n, f), sc = PITCH / 12;
    const paths = []; for (let i = 0; i < N; i++) paths.push(null);
    const inVis = new Set(vis);
    for (let i = c0; i < c1; i++) {
      const id = cl[i]; if (!inVis.has(id) || cf[i] < sinceOf[id]) continue;
      const u = cc[i] / 255, r = Math.sqrt((3 + 26 * u) / Math.PI) * sc, b = bf[id];
      const x = xOf(f, cf[i]), y = yc(slotOf[id]) + (b >= 0 && cf[i] >= b ? (cs[i] ? PAIR : -PAIR) : 0);
      const n = cn[i]; let p = paths[n]; if (!p) p = paths[n] = new Path2D();
      p.moveTo(x + r, y); p.arc(x, y, r, 0, 6.283185307179586);
    }
    ctx.globalCompositeOperation = 'lighter';
    for (let n = 0; n < N; n++) if (paths[n]) { ctx.fillStyle = nat[n]; ctx.fill(paths[n]); }
    ctx.globalCompositeOperation = 'source-over';
    // MIRV connectors: a vertical line across the lanes the warheads touched, at the launch frame, in the nation's hue; the newest 0.6 s bright
    const m0 = lb(mf, S.nm, f - WF), m1 = ub(mf, S.nm, f);
    ctx.lineWidth = 1.5;
    for (let m = m0; m < m1; m++) {
      let ya = 1e9, yb = -1e9, n = 0;
      for (let j = mstart[m]; j < mstart[m + 1]; j++) { const id = mlane[j]; if (!inVis.has(id)) continue; n++; const y = yc(slotOf[id]); if (y < ya) ya = y; if (y > yb) yb = y; }
      if (n < 2) continue;
      const k = f - mf[m] < S.conn_f ? 1 : 0.55, x = Math.round(xOf(f, mf[m])) + 0.5;
      ctx.strokeStyle = P.flat(mnat[m], 0.8, 0.85 * k); ctx.beginPath(); ctx.moveTo(x, Math.round(ya)); ctx.lineTo(x, Math.round(yb)); ctx.stroke();
      ctx.fillStyle = P.flat(mnat[m], 0.85, k);
      for (let j = mstart[m]; j < mstart[m + 1]; j++) { const id = mlane[j]; if (inVis.has(id)) ctx.fillRect(x - 2, Math.round(yc(slotOf[id])) - 2, 4, 4); }
    }
    ctx.lineWidth = 1;
    ctx.restore();
    // names at the left end of each lane (11 px, ellipsis); full name on hover in the player
    ctx.font = NP + 'px ' + FONT; ctx.fillStyle = KW.C.fg2; ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
    for (const id of vis) ctx.fillText(clip(S.names[id], NCH), I.nameX + 4, Math.round(yc(slotOf[id])) + Math.round(NP * 0.36));
  }

  const SCORE_KINDS = { nation: 'N', constellation: 'C', migration: 'M', storm: 'S' };
  KW.iaAxis = { xOf, ub, lb, WF, AX0, AX1, por, I, z: () => ({ RULER_Y, RULER_H, BAND_Y, BAND_H, LANE_Y, TL_Y, TL_H }), letters: SCORE_KINDS };
  const useScore = () => D.timeline_form === 'score' && !KW.ui.lanesForm && !!KW.drawScore;
  let SCORE_ON = false;
  function timeline(ctx, f) {
    setZ();
    SCORE_ON = useScore();
    if (SCORE_ON) {   // the short score: ruler, then one stave per nation (portrait closed: a condensed score in the band's 60 px)
      KW.plate(ctx, 0, RULER_Y, W, TL_Y + TL_H - RULER_Y);
      ruler(ctx, f);
      ctx.fillStyle = KW.C.rule; ctx.fillRect(1, BAND_Y - 1, W - 2, 1);
      KW.drawScore(ctx, f, BAND_Y, TL_Y + TL_H - BAND_Y - 1, por && !KW.ui.lanes);
      ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.30)'; ctx.fillRect(AX1, BAND_Y, 1, TL_Y + TL_H - BAND_Y - 1);
      ctx.textAlign = 'left';
      return;
    }
    const bandOn = f >= bandFirst, lanesOn = S && f >= laneFirst && lanesShown();
    let hOcc = RULER_H;
    if (bandOn) hOcc = BAND_Y + BAND_H - RULER_Y;
    if (lanesOn) hOcc = TL_Y + TL_H - RULER_Y;
    KW.plate(ctx, 0, RULER_Y, W, hOcc);
    ruler(ctx, f);
    if (bandOn) {
      ctx.fillStyle = KW.C.rule; ctx.fillRect(1, BAND_Y - 1, W - 2, 1);
      bandSec(ctx, f);
    }
    if (lanesOn) {
      ctx.fillStyle = KW.C.rule; ctx.fillRect(1, LANE_Y - 3, W - 2, 1);
      lanesSec(ctx, f);
    }
    if (bandOn) { ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.30)'; ctx.fillRect(AX1, BAND_Y, 1, hOcc - (BAND_Y - RULER_Y) - 1); }   // now
    ctx.textAlign = 'left';
  }
  KW.registerLayer({ id: 'timeline', z: 73, render: timeline });
  // hover: the lane under a logical point at frame f
  KW.streamLaneAt = function (f, px, py) {
    setZ();
    if (!S || f < laneFirst || !lanesShown() || py < LANE_Y || py >= LANE_Y + I.lanes[3]) return null;
    const slot = Math.floor((py - LANE_Y) / PITCH), base = f * K;
    for (let k = 0; k < K; k++) { const id = sid[base + k]; if (id === 255) break; if (Math.round(sx[base + k]) === slot) return { id, name: S.names[id] }; }
    return null;
  };
  setZ();


  // ---- coast edge: a 1 px edge on every side of a revealed cell whose neighbour is not revealed yet at f (the neighbour's own first frame decides, not the
  // final occupancy: early land has its sides until a neighbour rises). One neutral hue. Segments are intervals [start, end); the path is rebuilt when the active set changes.
  if (D.coast) {
    const SQ3 = 1.7320508075688772, R = 0.96, HXr = [0.8660254037844386, 0, -0.8660254037844386, -0.8660254037844386, 0, 0.8660254037844386], HYr = [0.5, 1, 0.5, -0.5, -1, -0.5];
    const NB = [[1, 1], [-1, 1], [-2, 0], [-1, -1], [1, -1], [2, 0]];
    const key = (a, r) => (a + 4000) * 20000 + (r + 8000), ak = x => Math.round(x / (SQ3 / 2)), rk = y => Math.round(y / 1.5);
    const cellFirst = new Map();
    for (const t of KW.exploredOrder) { if (KW.tkind[t] === 2) continue; for (let c = KW.cstart[t]; c < KW.cstart[t + 1]; c++) cellFirst.set(key(ak(KW.ccx[c]), rk(KW.ccy[c])), KW.tfirst[t]); }
    const segs = [];   // [start, end, x0, y0, x1, y1]
    for (const t of KW.exploredOrder) {
      if (KW.tkind[t] === 2) continue;
      for (let c = KW.cstart[t]; c < KW.cstart[t + 1]; c++) {
        const x = KW.ccx[c], y = KW.ccy[c], a = ak(x), r = rk(y);
        for (let k = 0; k < 6; k++) {
          const nf = cellFirst.get(key(a + NB[k][0], r + NB[k][1]));
          const end = nf === undefined ? 1e9 : nf;
          if (end <= KW.tfirst[t]) continue;
          const k2 = (k + 1) % 6;
          segs.push([KW.tfirst[t], end, x + HXr[k] * R, y + HYr[k] * R, x + HXr[k2] * R, y + HYr[k2] * R]);
        }
      }
    }
    segs.sort((p, q) => p[0] - q[0]);
    const st = segs.map(q => q[0]), ens = segs.map(q => q[1]).sort((p, q) => p - q);
    KW.coastSegs = segs;
    let cache = { key: -1, p: null };
    KW.registerLayer({ id: 'coast-edge', z: 12, map: true, render: function (ctx, f) {
      const v = KW.view(f), ck = KW.codaK(f); if (ck <= 0) return;
      const n = ub(st, st.length, f - 9), e = ub(ens, ens.length, f), kk = n * 1e6 + e;
      if (cache.key !== kk) { const p = new Path2D(); for (let i = 0; i < n; i++) if (segs[i][1] > f) { p.moveTo(segs[i][2], segs[i][3]); p.lineTo(segs[i][4], segs[i][5]); } cache = { key: kk, p }; }
      KW.setWorld(ctx, v); ctx.lineWidth = 1 / v.s; ctx.globalAlpha = 0.6 * ck; ctx.strokeStyle = KW.C.muted; ctx.stroke(cache.p); ctx.globalAlpha = 1;
    } });
  }

  // ---- coast labels: a constellation's name sits just below the southern coast of the land revealed so far (the lowest revealed cell of its regions), from its
  // second visible member on (one region is a place, not yet a land). The anchor is a step function of the frame. The archipelago is not named.
  if (D.coast && D.ncon) {
    const rcon = U.u8(D.rcon), clf = U.i32(D.con_label_f), frames = [], bxs = [], bys = [];
    for (let c = 0; c < D.ncon; c++) {
      const ev = [];
      for (let t = 0; t < D.T; t++) {
        if (rcon[KW.tregion[t]] !== c || KW.tkind[t] === 2 || KW.tfirst[t] >= F) continue;
        let by = -1e9, bx = 0;
        for (let q = KW.cstart[t]; q < KW.cstart[t + 1]; q++) if (KW.ccy[q] > by || (KW.ccy[q] === by && KW.ccx[q] < bx)) { by = KW.ccy[q]; bx = KW.ccx[q]; }
        ev.push([KW.tfirst[t], by, bx]);
      }
      ev.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);
      const fr = [], xs = [], ys = []; let cy = -1e9, cx = 0;
      for (const e of ev) { if (e[1] > cy || (e[1] === cy && e[2] < cx)) { cy = e[1]; cx = e[2]; } fr.push(e[0]); xs.push(cx); ys.push(cy); }
      frames.push(fr); bxs.push(xs); bys.push(ys);
    }
    KW.registerLayer({ id: 'coast', z: 66, map: true, render: function (ctx, f) {
      KW.resetT(ctx);
      const v = KW.view(f), ck = KW.codaK(f);
      if (ck <= 0) return;
      ctx.font = '12px ' + FONT; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = KW.C.muted; ctx.globalAlpha = 0.9 * ck;
      for (let c = 0; c < D.ncon; c++) {
        if (clf[c] > f) continue;
        const n = ub(frames[c], frames[c].length, f) - 1; if (n < 0) continue;
        ctx.fillText(D.con_names[c], Math.round(KW.sx(bxs[c][n], v)), Math.round(KW.sy(bys[c][n], v) + v.s * 1.0 + 15));
      }
      ctx.globalAlpha = 1; ctx.textAlign = 'left';
    } });
  }
})();
