// card.js: the coda card. Over the map's last 18 s: decay 3 s, camera to the whole world 4 s, silence 2 s, the tally card 8 s,
// black 1 s (fractions of the coda, so the cut's 6 s keeps the shape). One row per nation in entry order; two plain footer lines.
(function () {
  const KW = window.KW, D = KW.D, P = KW.palette;
  if (!D.T || D.version < 2) return;
  const FONT = '"JetBrains Mono", monospace';
  KW.codaLen = D.F - D.coda_f;
  KW.codaFrac = f => (f - D.coda_f) / KW.codaLen;
  // the prologue card (eras: single): the first intro seconds, one line that says what came before the story's first day. It fades in over 0.3 s and out
  // over 0.5 s onto the (empty) world; nothing else says it (the honesty rule). The text comes from the compile (counts only).
  function wrapLine(ctx, text, w) {
    const words = text.split(' '), out = []; let cur = '';
    for (const t of words) { const nx = cur ? cur + ' ' + t : t; if (ctx.measureText(nx).width > w && cur) { out.push(cur); cur = t; } else cur = nx; }
    if (cur) out.push(cur); return out;
  }
  function prologue(ctx, f) {
    const LY = KW.LAY, n = D.intro_f, fin = Math.min(1, (f + 1) / 9), fout = Math.min(1, Math.max(0, (n - f) / 15));
    const a = Math.min(fin, fout);
    ctx.fillStyle = 'rgba(7,9,14,' + (a).toFixed(3) + ')'; ctx.fillRect(0, 0, LY.W, LY.H);
    const por = LY.mode === 'portrait', px = por ? 17 : 30, lh = Math.round(px * 1.5), w = LY.W - (por ? 40 : 360);
    ctx.font = px + 'px ' + FONT; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    const lines = wrapLine(ctx, D.prologue.text, w), y0 = Math.round(LY.H / 2 - (lines.length - 1) * lh / 2);
    ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',' + a.toFixed(3) + ')';
    lines.forEach((t, i) => ctx.fillText(t, LY.W / 2, y0 + i * lh));
    ctx.textAlign = 'left';
  }
  function card(ctx, f) {
    if (D.prologue && f < D.intro_f) { prologue(ctx, f); return; }
    const u = KW.codaFrac(f);
    if (u < 9 / 18) return;
    const fin = Math.min(1, (u - 9 / 18) / (1 / 18)), fout = u > 17 / 18 ? Math.min(1, (u - 17 / 18) / (1 / 18)) : 0;
    ctx.fillStyle = 'rgba(7,9,14,' + ((KW.LAY.ia ? 1 : 0.96) * fin).toFixed(3) + ')'; ctx.fillRect(0, 0, KW.LAY.W, KW.LAY.H);
    ctx.globalAlpha = fin;
    if (KW.LAY.mode === 'portrait') { portrait(ctx, fin, fout); return; }
    const x0 = 160, cols = [x0, x0 + 250, x0 + 410, x0 + 500, x0 + 690, x0 + 920, x0 + 1110, x0 + 1220, x0 + 1370], y0 = 150, rowH = 62;
    ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
    ctx.font = '16px ' + FONT; ctx.fillStyle = KW.C.muted;
    ['', 'first test', 'tests', 'yield', 'single/MIRV/unified', 'tiles / laid out', 'commits', 'files changed', '+lines / \u2212lines'].forEach((h, i) => { if (h) ctx.fillText(h, cols[i], y0 - 16); });
    ctx.fillStyle = KW.C.rule; ctx.fillRect(x0, y0 - 6, 1600, 1);
    for (let i = 0; i < D.card.length; i++) {
      const r = D.card[i], y = y0 + 40 + i * rowH;
      ctx.fillStyle = P.flat(i, 0.62, 1); ctx.fillRect(cols[0], y - 20, 20, 20);
      ctx.font = '28px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.fillText(r.name, cols[0] + 34, y);
      ctx.font = '24px ' + FONT; ctx.fillStyle = KW.C.fg2;
      ctx.fillText(r.first || (r.parts ? '—' : '—'), cols[1], y);
      ctx.font = '30px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.fillText(String(r.tests), cols[2], y);
      ctx.font = '24px ' + FONT; ctx.fillStyle = KW.C.fg2; ctx.fillText(r.yield, cols[3], y);
      ctx.fillText(r.shapes, cols[4], y); ctx.fillText(r.tiles, cols[5], y);
      ctx.fillText(r.commits, cols[6], y); ctx.fillText(r.files, cols[7], y); ctx.fillText(r.lines, cols[8], y);
    }
    { // the world row: totals over every nation
      const r = D.card_world, y = y0 + 40 + D.card.length * rowH;
      ctx.fillStyle = KW.C.rule; ctx.fillRect(x0, y - 44, 1600, 1);
      ctx.font = '28px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.fillText(r.name, cols[0] + 34, y);
      ctx.font = '30px ' + FONT; ctx.fillText(String(r.tests), cols[2], y);
      ctx.font = '24px ' + FONT; ctx.fillStyle = KW.C.fg2;
      ctx.fillText(r.commits, cols[6], y); ctx.fillText(r.files, cols[7], y); ctx.fillText(r.lines + ' lines', cols[8], y);
    }
    if (D.card_third) { ctx.font = '22px ' + FONT; ctx.fillStyle = KW.C.muted2; ctx.fillText(D.card_third, cols[0] + 34, y0 + 40 + (D.card.length + 1) * rowH + 6); }
    if (KW.LAY.ia) {   // the surface tallies live here now (and behind the player's `s` toggle): one line per surface, final figures
      const sb = surfBlock(), y1 = 728;
      ctx.font = '16px ' + FONT; ctx.fillStyle = KW.C.muted;
      ['surfaces', 'tests', 'commits', 'files changed', 'files created / updated'].forEach((h, i) => ctx.fillText(h, [cols[0], cols[2], cols[6], cols[7], cols[8]][i], y1));
      ctx.fillStyle = KW.C.rule; ctx.fillRect(x0, y1 + 8, 1600, 1);
      sb.forEach((r, i) => {
        const y = y1 + 36 + i * 26;
        ctx.font = '22px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.fillText(r.name, cols[0] + 34, y);
        ctx.fillStyle = KW.C.surf ? KW.C.surf[r.si] : P.rgbaRaw(0.45, 0.05, r.hue, 0.95); ctx.fillRect(cols[0], y - 16, 16, 16);
        ctx.font = '20px ' + FONT; ctx.fillStyle = KW.C.fg2;
        if (r.repos !== null) { ctx.fillText(r.repos + ' repos risen', cols[2], y); return; }
        ctx.fillText(r.tests, cols[2], y); ctx.fillText(r.commits, cols[6], y); ctx.fillText(r.files, cols[7], y); ctx.fillText(r.created + ' / ' + r.updated, cols[8], y);
      });
    }
    ctx.font = '18px ' + FONT; ctx.fillStyle = KW.C.muted;
    { let yf = 936; for (const t of D.card_footer) for (const ln of wrapLine(ctx, t, 1600)) { ctx.fillText(ln, x0, yf); yf += 24; } }
    ctx.globalAlpha = 1;
    if (fout > 0) { ctx.fillStyle = 'rgba(0,0,0,' + fout.toFixed(3) + ')'; ctx.fillRect(0, 0, KW.LAY.W, KW.LAY.H); }
  }
  // the final figures per surface (the last frame's cumulative tables), in entry order
  function surfBlock() {
    const U = KW.util, F = D.F, S = D.surfaces, g = F - 1, fm = KW.fmt, KEYS = ['omen-c', 'omen-e', 'omen-linux', 'am4', 'fx99', 'github'], HUE = [275, 255, 165, 310, 60];
    const tests = U.u16(D.sc_tests), cm = U.f32(D.sc_commits), fl = U.f32(D.sc_files), cr = U.f32(D.sc_created), up = U.f32(D.sc_updated), isl = U.u16(D.isl_cum);
    const idx = []; for (let i = 0; i < S.names.length; i++) if (S.entry[i] < F) idx.push(i);
    idx.sort((a, b) => S.entry[a] - S.entry[b] || a - b);
    return idx.map(i => KEYS[i] === 'github'
      ? { si: i, name: S.names[i], hue: 190, repos: fm.commas(isl[g]) }
      : { si: i, name: S.names[i], hue: HUE[i], repos: null, tests: String(tests[i * F + g]), commits: fm.commas(cm[i * F + g]), files: fm.commas(fl[i * F + g]), created: fm.compact(cr[i * F + g]), updated: fm.compact(up[i * F + g]) });
  }
  // portrait: one block of three lines per nation, the world row, then the footer wrapped to the frame
  function wrap(ctx, text, w) {
    const words = text.split(' '), out = []; let cur = '';
    for (const t of words) { const nx = cur ? cur + ' ' + t : t; if (ctx.measureText(nx).width > w && cur) { out.push(cur); cur = t; } else cur = nx; }
    if (cur) out.push(cur); return out;
  }
  function portrait(ctx, fin, fout) {
    const LY = KW.LAY, x0 = 14, rowH = Math.min(62, Math.floor((LY.H - 330 - (LY.ia ? 112 : 0)) / (D.card.length + 1)));
    let y = 44;
    ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
    const lines = r => r.commits + ' commits \u00b7 ' + r.files + ' files \u00b7 ' + r.lines;
    for (let i = 0; i < D.card.length; i++) {
      const r = D.card[i];
      ctx.fillStyle = P.flat(i, 0.62, 1); ctx.fillRect(x0, y - 14, 14, 14);
      ctx.font = '20px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.fillText(r.name, x0 + 24, y);
      ctx.textAlign = 'right'; ctx.font = '22px ' + FONT; ctx.fillText(String(r.tests), LY.W - x0, y); ctx.textAlign = 'left';
      ctx.font = '12px ' + FONT; ctx.fillStyle = KW.C.fg2;
      ctx.fillText((r.first || '\u2014') + '  \u00b7  ' + r.yield + '  \u00b7  ' + r.shapes, x0 + 24, y + 18);
      ctx.fillStyle = KW.C.muted; ctx.fillText(lines(r), x0 + 24, y + 34);
      y += rowH;
    }
    const w = D.card_world;
    ctx.fillStyle = KW.C.rule; ctx.fillRect(x0, y - 22, LY.W - 2 * x0, 1);
    ctx.font = '20px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.fillText(w.name, x0 + 24, y);
    ctx.textAlign = 'right'; ctx.font = '22px ' + FONT; ctx.fillText(String(w.tests), LY.W - x0, y); ctx.textAlign = 'left';
    ctx.font = '12px ' + FONT; ctx.fillStyle = KW.C.muted; ctx.fillText(lines(w).replace(/ \u00b7 ([^ ]+)$/, ' \u00b7 $1 lines'), x0 + 24, y + 18);
    y += 44;
    if (LY.ia) {
      ctx.font = '12px ' + FONT;
      for (const r of surfBlock()) {
        ctx.fillStyle = KW.C.fg; ctx.fillText(r.name, x0 + 24, y);
        ctx.fillStyle = KW.C.muted; ctx.textAlign = 'right';
        ctx.fillText(r.repos !== null ? r.repos + ' repos risen' : r.tests + ' tests \u00b7 ' + r.commits + ' c \u00b7 ' + r.files + ' f', LY.W - x0, y); ctx.textAlign = 'left';
        y += 16;
      }
      y += 10;
    }
    ctx.font = '11px ' + FONT; ctx.fillStyle = KW.C.muted2;
    const foot = (D.card_third ? [D.card_third] : []).concat(D.card_footer);
    for (const t of foot) { for (const ln of wrap(ctx, t, LY.W - 2 * x0)) { ctx.fillText(ln, x0, y); y += 15; } y += 4; }
    ctx.globalAlpha = 1;
    if (fout > 0) { ctx.fillStyle = 'rgba(0,0,0,' + fout.toFixed(3) + ')'; ctx.fillRect(0, 0, LY.W, LY.H); }
  }
  KW.registerLayer({ id: 'card', z: 90, render: card });
})();
