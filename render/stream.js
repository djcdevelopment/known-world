// stream.js: the stream column (DIRECTION 'The stream'): lanes = lineages, ticks = commits, rails = branches and worktrees,
// connectors = MIRV launches and cross-constellation edges. Everything is a lookup in tables the compile laid out; nothing
// flashes and nothing sounds. Repo names are printed here only (the map's labels stay off); the hashed arm swaps them at compile.
(function () {
  const KW = window.KW, D = KW.D, S = D.stream;
  if (!S || !KW.LAY.stream || KW.LAY.ia) return;   // portrait hides the stream (hud_portrait: hidden)
  const U = KW.util, F = D.F, K = S.K, L = S.L, FONT = '"JetBrains Mono", monospace';
  const LY = KW.LAY, X0 = LY.W - LY.right - S.col_w, W = S.col_w, TOP = LY.top, PHT = LY.H - LY.top - LY.bottom, YQ = TOP + 20, YH = YQ + 104, YB = LY.H - LY.bottom, H = YB - YH, Wf = S.window_f, PPF = H / Wf;
  const sid = U.u8(S.sid), sx = U.f32(S.sx), sa = U.u8(S.sa), ss = U.i32(S.ss), sq = U.u8(S.sq);
  const cf = U.i32(S.cf), cl = U.u8(S.cl), cn = U.u8(S.cn), cc = U.u8(S.cc), cs = U.u8(S.cs), bf = U.i32(S.bf), con = U.u8(S.con);
  const rf0 = U.i32(S.rf0), rf1 = U.i32(S.rf1), rlane = U.u8(S.rlane), rflag = U.u8(S.rflag), rside = U.u8(S.rside);
  const mf = U.i32(S.mf), mnat = U.u8(S.mnat), mstart = U.i32(S.mstart), mlane = U.u8(S.mlane);
  const ef = U.i32(S.ef), ea = U.u8(S.ea), eb = U.u8(S.eb);
  const tf = U.i32(S.tf), tl = U.u8(S.tl), tlab = S.tlab;
  const N = D.nat_names.length, P = KW.palette;
  const RAIL_OFF = [3.5, -3.5, 5.5, -5.5], PAIR = 2.5, MAXCH = 14;
  const lx = new Float32Array(L), la = new Float32Array(L), ls = new Int32Array(L);
  const lb = (arr, n, v) => { let lo = 0, hi = n; while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] < v) lo = m + 1; else hi = m; } return lo; };   // first index with arr[i] >= v
  const ub = (arr, n, v) => { let lo = 0, hi = n; while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] <= v) lo = m + 1; else hi = m; } return lo; };   // first index with arr[i] > v
  const clip = (t, n) => { n = n || MAXCH; return t.length > n ? t.slice(0, n - 1) + '…' : t; };
  const NAME_MIN_PX = 18, NAME_WIDE_PX = 30;
  const nat = []; for (let i = 0; i < N; i++) nat.push(P.rgba(i, 0.74, 0.62));
  let fadeG = null;
  function draw(ctx, f) {
    const Y = fr => YB - (f - fr) * PPF;
    KW.plate(ctx, X0, TOP, W, PHT);
    ctx.save(); ctx.beginPath(); ctx.rect(X0 + 1, TOP, W - 2, PHT); ctx.clip();
    ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
    // ruler: era ticks and a faint time axis on the left edge, newest at the bottom
    ctx.save(); ctx.beginPath(); ctx.rect(X0 + 1, YH, W - 1, H + 1); ctx.clip();
    ctx.font = '10px ' + FONT;
    const t0 = lb(tf, S.nt, f - Wf), t1 = ub(tf, S.nt, f);
    for (let i = t0; i < t1; i++) {
      const y = Math.round(Y(tf[i])), lv = tl[i];
      if (lv === 2) { ctx.fillStyle = 'rgba(232,224,192,0.30)'; ctx.fillRect(X0 + 4, y, W - 8, 1); ctx.fillRect(X0 + 4, y - 1, 14, 3); }
      else if (lv === 1) { ctx.fillStyle = 'rgba(232,224,192,0.45)'; ctx.fillRect(X0 + S.ruler_w - 12, y, 10, 1); }
      else { ctx.fillStyle = 'rgba(232,224,192,0.18)'; ctx.fillRect(X0 + S.ruler_w - 6, y, 4, 1); }
      if (tlab[i]) { ctx.fillStyle = 'rgba(139,147,166,0.85)'; ctx.fillText(tlab[i], X0 + 6, y - 3); }
    }
    ctx.fillStyle = 'rgba(232,224,192,0.5)'; ctx.fillRect(X0 + 4, YB - 1, S.ruler_w - 6, 1);
    // slots for this frame
    const base = f * K, vis = [];
    for (let k = 0; k < K; k++) {
      const id = sid[base + k]; if (id === 255) break;
      lx[id] = sx[base + k] + X0; la[id] = sa[base + k] / 255; ls[id] = ss[base + k]; vis.push(id);
    }
    // lane hairlines and paired rails (a lineage on two surfaces runs as two rails joined at the bridge frame)
    ctx.lineWidth = 1;
    for (const id of vis) {
      const a = la[id], x = Math.round(lx[id]) + 0.5, ytop = Math.max(YH, Y(Math.max(ls[id], f - Wf))), b = bf[id];
      ctx.strokeStyle = 'rgba(139,147,166,' + (0.28 * a).toFixed(3) + ')';
      ctx.beginPath();
      if (b >= 0 && b <= f) {
        const yb = Math.max(ytop, Y(Math.max(b, f - Wf)));
        if (b >= f - Wf) { ctx.moveTo(x, ytop); ctx.lineTo(x, yb); ctx.moveTo(x - PAIR, yb); ctx.lineTo(x + PAIR, yb); }
        ctx.moveTo(x - PAIR, yb); ctx.lineTo(x - PAIR, YB); ctx.moveTo(x + PAIR, yb); ctx.lineTo(x + PAIR, YB);
      } else { ctx.moveTo(x, ytop); ctx.lineTo(x, YB); }
      ctx.stroke();
    }
    // rails: branches and worktrees fork a short parallel rail, rejoining at a unified launch or fading
    for (let r = 0; r < S.nr; r++) {
      const a0 = rf0[r]; if (a0 > f) break;
      const a1 = rf1[r], id = rlane[r]; if (a1 < f - Wf || la[id] <= 0) continue;
      const a = la[id], x = Math.round(lx[id] + RAIL_OFF[rside[r]]) + 0.5, wt = rflag[r] & 1, jn = rflag[r] & 2;
      const ya = Math.max(YH, Y(Math.max(a0, f - Wf))), yz = Y(Math.min(a1, f));
      ctx.strokeStyle = (wt ? 'rgba(196,164,112,' : 'rgba(112,150,196,') + (0.55 * a).toFixed(3) + ')';
      ctx.beginPath(); ctx.moveTo(x, ya); ctx.lineTo(x, yz);
      if (a0 >= f - Wf) { ctx.moveTo(Math.round(lx[id]) + 0.5, Y(a0)); ctx.lineTo(x, Y(a0) + 3); }
      if (jn && a1 <= f) { ctx.moveTo(x, yz); ctx.lineTo(Math.round(lx[id]) + 0.5, yz + 5); }
      ctx.stroke();
      if (!jn && a1 <= f) { ctx.fillStyle = (wt ? 'rgba(196,164,112,' : 'rgba(112,150,196,') + (0.4 * a).toFixed(3) + ')'; ctx.fillRect(x - 1, yz, 2, 2); }
    }
    // association: one faint connector per cross-constellation edge, drawn where both lanes first stood together
    ctx.lineWidth = 1;
    for (let e = 0; e < S.ne; e++) {
      if (ef[e] > f || ef[e] < f - Wf) continue;
      const A = ea[e], B = eb[e]; if (la[A] <= 0 || la[B] <= 0) continue;
      const y = Math.round(Y(ef[e])) + 0.5, a = Math.min(la[A], la[B]);
      ctx.strokeStyle = 'rgba(201,195,168,' + (0.30 * a).toFixed(3) + ')';
      ctx.beginPath(); ctx.moveTo(Math.round(lx[A]), y); ctx.lineTo(Math.round(lx[B]), y); ctx.stroke();
      ctx.fillStyle = 'rgba(201,195,168,' + (0.45 * a).toFixed(3) + ')'; ctx.fillRect(Math.round(lx[A]) - 1, y - 1, 3, 3); ctx.fillRect(Math.round(lx[B]) - 1, y - 1, 3, 3);
    }
    // ticks: commits. Dot area by log(lines, capped), hue by nation, density by overlap ('lighter')
    const c0 = lb(cf, S.n, Math.max(0, f - Wf)), c1 = ub(cf, S.n, f);
    const paths = []; for (let i = 0; i < N; i++) paths.push(null);
    const slow = [];
    for (let i = c0; i < c1; i++) {
      const id = cl[i], a = la[id]; if (a <= 0 || cf[i] < ls[id]) continue;
      const u = cc[i] / 255, r = Math.sqrt((3 + 26 * u) / Math.PI), b = bf[id];
      const x = lx[id] + (b >= 0 && cf[i] >= b ? (cs[i] ? PAIR : -PAIR) : 0), y = Y(cf[i]);
      if (y < YH - 4) continue;
      if (a < 1) { slow.push(x, y, r, cn[i], a); continue; }
      const n = cn[i]; let p = paths[n]; if (!p) p = paths[n] = new Path2D();
      p.moveTo(x + r, y); p.arc(x, y, r, 0, 6.283185307179586);
    }
    ctx.globalCompositeOperation = 'lighter';
    for (let n = 0; n < N; n++) if (paths[n]) { ctx.fillStyle = nat[n]; ctx.fill(paths[n]); }
    for (let i = 0; i < slow.length; i += 5) { ctx.globalAlpha = slow[i + 4]; ctx.fillStyle = nat[slow[i + 3]]; ctx.beginPath(); ctx.arc(slow[i], slow[i + 1], slow[i + 2], 0, 6.283185307179586); ctx.fill(); }
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
    // MIRV connectors: a horizontal line across the lanes the warheads touched, at the launch frame, 0.6 s, nation hue
    const m0 = lb(mf, S.nm, f - S.conn_f), m1 = ub(mf, S.nm, f);
    ctx.lineWidth = 1.5;
    for (let m = m0; m < m1; m++) {
      let xa = 1e9, xb = -1e9, n = 0;
      for (let j = mstart[m]; j < mstart[m + 1]; j++) { const id = mlane[j]; if (la[id] <= 0) continue; n++; if (lx[id] < xa) xa = lx[id]; if (lx[id] > xb) xb = lx[id]; }
      if (n < 2) continue;
      const k = 1 - (f - mf[m]) / S.conn_f, y = Math.round(Y(mf[m])) + 0.5;
      ctx.strokeStyle = P.rgba(mnat[m], 0.8, 0.85 * k); ctx.beginPath(); ctx.moveTo(Math.round(xa), y); ctx.lineTo(Math.round(xb), y); ctx.stroke();
      ctx.fillStyle = P.rgba(mnat[m], 0.85, k);
      for (let j = mstart[m]; j < mstart[m + 1]; j++) { const id = mlane[j]; if (la[id] > 0) ctx.fillRect(Math.round(lx[id]) - 2, y - 2, 4, 4); }
    }
    ctx.lineWidth = 1;
    // entry labels: a lane enters at its first commit with its name, written up the lane
    ctx.font = '12px ' + FONT; ctx.fillStyle = '#c9c3a8';
    for (const id of vis) {
      const y = Y(ls[id]); if (ls[id] < f - Wf || y < YH + 24) continue;
      ctx.globalAlpha = 0.7 * la[id]; ctx.save(); ctx.translate(Math.round(lx[id]) + 4, y - 6); ctx.rotate(-Math.PI / 2); ctx.fillText(clip(S.names[id]), 0, 0); ctx.restore();
    }
    ctx.globalAlpha = 1;
    // the plot leaves at the top through a soft edge
    
    ctx.restore();
    // header: pinned names and the quiet count
    ctx.fillStyle = '#1b2230'; ctx.fillRect(X0 + 1, YH - 1, W - 2, 1);
    ctx.font = '12px ' + FONT;
    if (sq[f] > 0) { ctx.textAlign = 'right'; ctx.fillStyle = '#8b93a6'; ctx.fillText('+' + sq[f] + ' quiet', X0 + W - 8, TOP + 15); ctx.textAlign = 'left'; }
    // header names follow the legibility rule (DIRECTION 'Stream header legibility'): a lane is named only when its pitch (the gap to its
    // nearer neighbour) is at least 18 px; named lanes alternate between two staggered rows of 7 characters, or stand alone in one row
    // of 14 once the pitch is 30 px or more. The rest keep their entry label and show their name on hover in the player.
    let prev = -2, nn = 0;
    for (let q = 0; q < vis.length; q++) {
      const id = vis[q], a = la[id];
      if (prev >= 0 && con[prev] !== con[id] && Math.min(la[prev], a) > 0.5) { const xm = Math.round((lx[prev] + lx[id]) / 2) + 0.5; ctx.fillStyle = 'rgba(139,147,166,0.30)'; ctx.fillRect(xm, YQ + 18, 1, YH - YQ - 24); }
      const dl = q > 0 ? lx[id] - lx[vis[q - 1]] : 1e9, dr = q + 1 < vis.length ? lx[vis[q + 1]] - lx[id] : 1e9, pitch = Math.min(dl, dr);
      if (KW.compat) {
        ctx.globalAlpha = 0.9 * a; ctx.fillStyle = '#e8e0c0';
        ctx.save(); ctx.translate(Math.round(lx[id]) + 4, YH - 6); ctx.rotate(-Math.PI / 2); ctx.fillText(clip(S.names[id]), 0, 0); ctx.restore();
      } else if (pitch >= NAME_MIN_PX) {
        const wide = pitch >= NAME_WIDE_PX, row = wide ? 0 : (nn++ & 1);
        ctx.globalAlpha = 0.9 * a; ctx.fillStyle = '#e8e0c0';
        ctx.save(); ctx.translate(Math.round(lx[id]) + 4, YH - 6 - row * 50); ctx.rotate(-Math.PI / 2); ctx.fillText(wide ? clip(S.names[id]) : clip(S.names[id], 7), 0, 0); ctx.restore();
      }
      prev = id;
    }
    ctx.globalAlpha = 1;
    for (const id of vis) la[id] = 0;
    ctx.restore();
    ctx.textAlign = 'left';
  }
  // hover: the lane under a logical point at frame f (the player shows its name)
  KW.streamLaneAt = function (f, px, py) {
    if (px < X0 || px > X0 + W || py < YQ || py > YB) return null;
    const base = f * K; let best = null, bd = 1e9;
    for (let k = 0; k < K; k++) {
      const id = sid[base + k]; if (id === 255) break;
      const d = Math.abs(sx[base + k] + X0 - px);
      if (d < bd && sa[base + k] > 0) { bd = d; best = id; }
    }
    return best !== null && bd <= 9 ? { id: best, name: S.names[best] } : null;
  };
  KW.registerLayer({ id: 'stream', z: 73, render: draw });
})();
