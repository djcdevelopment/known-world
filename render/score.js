// score.js: the short score (plan section 4), the cinematic timeline default. One stave per nation in entry order (name and swatch at the left like an
// instrument); a note per launch at its frame (head at the yield band's height, radius by band; a MIRV is a chord of up to four heads on one stem with +n
// for more; a unified launch is a slur over its converging run; an inferred nation has hollow heads); dynamics = the commit rate as a wedge under the
// stave; texture = the chatter rate as a stipple above it; bar lines are story days; a double bar and a letter mark a nation (N), constellation (C),
// migration (M) or storm (S). Window = the timeline axis (20 film s), now at the right edge. Everything is a lookup in tables the compile laid out.
(function () {
  const KW = window.KW, D = KW.D, U = KW.util;
  if (!D.T || D.version < 2 || !D.score || !KW.iaAxis) return;
  const A = KW.iaAxis, F = D.F, FONT = '"JetBrains Mono", monospace', N = D.nat_names.length, P = KW.palette;
  const hs = U.i32(D.score.hs), hb = U.u8(D.score.hb), more = U.u8(D.score.more), chat = U.u8(D.score.chat), rate = U.f32(D.rate_nat);
  const lf = KW.lf, lnat = KW.lnat, lband = KW.lband, lflags = KW.lflags, lpre = KW.lpre, tau = KW.tau;
  const marks = (D.marks || []).filter(m => A.letters[m.kind]);
  let rank = null;
  const rankOf = () => { if (rank) return rank; const o = [...Array(N).keys()].sort((a, b) => (KW.natShownF[a] - KW.natShownF[b]) || a - b); rank = new Int32Array(N); o.forEach((i, r) => { rank[i] = r; }); return rank; };
  const hash = (a, b) => { let h = (a * 374761393 + b * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177 | 0; return ((h ^ (h >>> 16)) >>> 0); };
  KW.drawScore = function (ctx, f, y0, h, condensed) {
    const R = rankOf(), s = Math.max(4, Math.min(condensed ? 8 : 24, Math.floor(h / N))), WF = A.WF, W = KW.LAY.W;
    let nVis = 0; for (let i = 0; i < N; i++) if (f >= KW.natShownF[i]) nVis++;
    if (!nVis) return;
    ctx.save(); ctx.beginPath(); ctx.rect(1, y0, W - 2, N * s); ctx.clip();
    // bar lines: story days
    ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.07)';
    for (let g = Math.max(1, f - WF + 1); g <= f; g++) if (Math.floor(tau[g] + 1e-9) !== Math.floor(tau[g - 1] + 1e-9)) ctx.fillRect(Math.round(A.xOf(f, g)), y0, 1, N * s);
    for (let i = 0; i < N; i++) {
      if (f < KW.natShownF[i]) continue;
      const top = y0 + R[i] * s, col = P.flat(i, 0.62, 0.9);
      ctx.fillStyle = 'rgba(' + KW.C.mutedRgb + ',0.18)'; ctx.fillRect(A.AX0, top + s - 1, A.AX1 - A.AX0, 1);
      // wedge: commit rate (log), under the stave, a few px
      ctx.fillStyle = P.flat(i, 0.62, 0.30);
      for (let g = Math.max(0, f - WF + 1); g <= f; g += 3) { const hgt = Math.min(Math.max(2, s * 0.25), Math.log10(1 + rate[i * F + g]) * 1.6); if (hgt >= 0.6) ctx.fillRect(Math.round(A.xOf(f, g)), top + s - 1 - hgt, 3, hgt); }
      // stipple: chatter rate, above the stave
      ctx.fillStyle = P.flat(i, 0.62, 0.55);
      for (let g = Math.max(0, f - WF + 1); g <= f; g += 2) { const v = chat[i * F + g]; if (v > 8 && (hash(g, i) & 255) < v) ctx.fillRect(Math.round(A.xOf(f, g)), top + 1 + (hash(i, g) % Math.max(1, Math.floor(s * 0.25))), 1, 1); }
      // name and swatch at the left
      const I = A.I;
      ctx.fillStyle = P.flat(i, 0.62, 1); ctx.fillRect(I.nameX + 4, top + Math.floor(s / 2) - 3, 6, 6);
      if (!condensed) { ctx.font = '11px ' + FONT; ctx.fillStyle = KW.C.fg2; ctx.textAlign = 'left'; ctx.fillText(D.nat_names[i], I.nameX + 14, top + Math.floor(s / 2) + 4); }
    }
    // notes
    const i0 = A.lb(lf, KW.nl, f - WF - 40), i1 = A.ub(lf, KW.nl, f), step = (s - 6) / 5;
    for (let q = i0; q < i1; q++) {
      const ni = lnat[q]; if (f < KW.natShownF[ni]) continue;
      const x = A.xOf(f, lf[q]); if (x < A.AX0 - 6) continue;
      const top = y0 + R[ni] * s, band = lband[q], hollow = (lflags[q] & 8) !== 0, col = P.flat(ni, 0.75, 0.95);
      const yb = b => top + s - 3 - (b - 1) * step, rad = b => Math.min(s / 2 - 1, condensed ? 2 : 1.4 + 0.65 * b);
      const heads = []; for (let k = hs[q]; k < hs[q + 1]; k++) heads.push(hb[k]);
      if (!heads.length) heads.push(band);
      if (lpre[q] > 0 && !condensed) {   // a unified launch: a slur over the converging run into the consolidated note
        const xa = A.xOf(f, lf[q] - lpre[q]);
        ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(xa, top + 4); ctx.quadraticCurveTo((xa + x) / 2, top - 1, x, top + 4); ctx.stroke();
      }
      if (heads.length > 1) { const ys = heads.map(yb); ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(Math.round(x) + 0.5, Math.min(...ys)); ctx.lineTo(Math.round(x) + 0.5, Math.max(...ys)); ctx.stroke(); }
      for (const b of heads) {
        ctx.beginPath(); ctx.arc(x, yb(b), rad(b), 0, 6.283185307179586);
        if (hollow) { ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.stroke(); } else { ctx.fillStyle = col; ctx.fill(); }
      }
      if (more[q] > 0 && !condensed) { ctx.font = '11px ' + FONT; ctx.fillStyle = col; ctx.textAlign = 'left'; ctx.fillText('+' + more[q], x + 5, top + 10); }
    }
    // double bar and a letter for nation, constellation, migration, storm marks
    ctx.font = '11px ' + FONT; ctx.textAlign = 'center';
    for (const m of marks) {
      if (m.frame > f || m.frame < f - WF) continue;
      const x = Math.round(A.xOf(f, m.frame));
      ctx.fillStyle = KW.markColor(m.kind, 0.55); ctx.fillRect(x, y0, 1, N * s); ctx.fillRect(x + 2, y0, 1, N * s);
      if (!condensed) { ctx.fillStyle = KW.markColor(m.kind, 0.95); ctx.fillText(A.letters[m.kind], x + 1, y0 + 10); }
    }
    ctx.restore(); ctx.textAlign = 'left'; ctx.lineWidth = 1;
  };
})();
