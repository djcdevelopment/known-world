// card.js: the coda card. Over the map's last 18 s: decay 3 s, camera to the whole world 4 s, silence 2 s, the tally card 8 s,
// black 1 s (fractions of the coda, so the cut's 6 s keeps the shape). One row per nation in entry order; two plain footer lines.
(function () {
  const KW = window.KW, D = KW.D, P = KW.palette;
  if (!D.T || D.version < 2) return;
  const FONT = '"JetBrains Mono", monospace';
  KW.codaLen = D.F - D.coda_f;
  KW.codaFrac = f => (f - D.coda_f) / KW.codaLen;
  function card(ctx, f) {
    const u = KW.codaFrac(f);
    if (u < 9 / 18) return;
    const fin = Math.min(1, (u - 9 / 18) / (1 / 18)), fout = u > 17 / 18 ? Math.min(1, (u - 17 / 18) / (1 / 18)) : 0;
    ctx.fillStyle = 'rgba(7,9,14,' + (0.96 * fin).toFixed(3) + ')'; ctx.fillRect(0, 0, KW.LAY.W, KW.LAY.H);
    ctx.globalAlpha = fin;
    if (KW.LAY.mode === 'portrait') { portrait(ctx, fin, fout); return; }
    const x0 = 160, cols = [x0, x0 + 250, x0 + 410, x0 + 500, x0 + 690, x0 + 920, x0 + 1110, x0 + 1220, x0 + 1370], y0 = 150, rowH = 62;
    ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
    ctx.font = '16px ' + FONT; ctx.fillStyle = '#8b93a6';
    ['', 'first test', 'tests', 'yield', 'single/MIRV/unified', 'tiles / laid out', 'commits', 'files changed', '+lines / \u2212lines'].forEach((h, i) => { if (h) ctx.fillText(h, cols[i], y0 - 16); });
    ctx.fillStyle = '#1b2230'; ctx.fillRect(x0, y0 - 6, 1600, 1);
    for (let i = 0; i < D.card.length; i++) {
      const r = D.card[i], y = y0 + 40 + i * rowH;
      ctx.fillStyle = P.rgba(i, 0.62, 1); ctx.fillRect(cols[0], y - 20, 20, 20);
      ctx.font = '28px ' + FONT; ctx.fillStyle = '#e8e0c0'; ctx.fillText(r.name, cols[0] + 34, y);
      ctx.font = '24px ' + FONT; ctx.fillStyle = '#c9c3a8';
      ctx.fillText(r.first || (r.parts ? '—' : '—'), cols[1], y);
      ctx.font = '30px ' + FONT; ctx.fillStyle = '#e8e0c0'; ctx.fillText(String(r.tests), cols[2], y);
      ctx.font = '24px ' + FONT; ctx.fillStyle = '#c9c3a8'; ctx.fillText(r.yield, cols[3], y);
      ctx.fillText(r.shapes, cols[4], y); ctx.fillText(r.tiles, cols[5], y);
      ctx.fillText(r.commits, cols[6], y); ctx.fillText(r.files, cols[7], y); ctx.fillText(r.lines, cols[8], y);
    }
    { // the world row: totals over every nation
      const r = D.card_world, y = y0 + 40 + D.card.length * rowH;
      ctx.fillStyle = '#1b2230'; ctx.fillRect(x0, y - 44, 1600, 1);
      ctx.font = '28px ' + FONT; ctx.fillStyle = '#e8e0c0'; ctx.fillText(r.name, cols[0] + 34, y);
      ctx.font = '30px ' + FONT; ctx.fillText(String(r.tests), cols[2], y);
      ctx.font = '24px ' + FONT; ctx.fillStyle = '#c9c3a8';
      ctx.fillText(r.commits, cols[6], y); ctx.fillText(r.files, cols[7], y); ctx.fillText(r.lines + ' lines', cols[8], y);
    }
    if (D.card_third) { ctx.font = '22px ' + FONT; ctx.fillStyle = '#5f6779'; ctx.fillText(D.card_third, cols[0] + 34, y0 + 40 + (D.card.length + 1) * rowH + 6); }
    ctx.font = '20px ' + FONT; ctx.fillStyle = '#8b93a6';
    D.card_footer.forEach((t, i) => ctx.fillText(t, x0, 950 + i * 30));
    ctx.globalAlpha = 1;
    if (fout > 0) { ctx.fillStyle = 'rgba(0,0,0,' + fout.toFixed(3) + ')'; ctx.fillRect(0, 0, KW.LAY.W, KW.LAY.H); }
  }
  // portrait: one block of three lines per nation, the world row, then the footer wrapped to the frame
  function wrap(ctx, text, w) {
    const words = text.split(' '), out = []; let cur = '';
    for (const t of words) { const nx = cur ? cur + ' ' + t : t; if (ctx.measureText(nx).width > w && cur) { out.push(cur); cur = t; } else cur = nx; }
    if (cur) out.push(cur); return out;
  }
  function portrait(ctx, fin, fout) {
    const LY = KW.LAY, x0 = 14, rowH = Math.min(62, Math.floor((LY.H - 330) / (D.card.length + 1)));
    let y = 44;
    ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
    const lines = r => r.commits + ' commits \u00b7 ' + r.files + ' files \u00b7 ' + r.lines;
    for (let i = 0; i < D.card.length; i++) {
      const r = D.card[i];
      ctx.fillStyle = P.rgba(i, 0.62, 1); ctx.fillRect(x0, y - 14, 14, 14);
      ctx.font = '20px ' + FONT; ctx.fillStyle = '#e8e0c0'; ctx.fillText(r.name, x0 + 24, y);
      ctx.textAlign = 'right'; ctx.font = '22px ' + FONT; ctx.fillText(String(r.tests), LY.W - x0, y); ctx.textAlign = 'left';
      ctx.font = '12px ' + FONT; ctx.fillStyle = '#c9c3a8';
      ctx.fillText((r.first || '\u2014') + '  \u00b7  ' + r.yield + '  \u00b7  ' + r.shapes, x0 + 24, y + 18);
      ctx.fillStyle = '#8b93a6'; ctx.fillText(lines(r), x0 + 24, y + 34);
      y += rowH;
    }
    const w = D.card_world;
    ctx.fillStyle = '#1b2230'; ctx.fillRect(x0, y - 22, LY.W - 2 * x0, 1);
    ctx.font = '20px ' + FONT; ctx.fillStyle = '#e8e0c0'; ctx.fillText(w.name, x0 + 24, y);
    ctx.textAlign = 'right'; ctx.font = '22px ' + FONT; ctx.fillText(String(w.tests), LY.W - x0, y); ctx.textAlign = 'left';
    ctx.font = '12px ' + FONT; ctx.fillStyle = '#8b93a6'; ctx.fillText(lines(w).replace(/ \u00b7 ([^ ]+)$/, ' \u00b7 $1 lines'), x0 + 24, y + 18);
    y += 44;
    ctx.font = '11px ' + FONT; ctx.fillStyle = '#5f6779';
    const foot = (D.card_third ? [D.card_third] : []).concat(D.card_footer);
    for (const t of foot) { for (const ln of wrap(ctx, t, LY.W - 2 * x0)) { ctx.fillText(ln, x0, y); y += 15; } y += 4; }
    ctx.globalAlpha = 1;
    if (fout > 0) { ctx.fillStyle = 'rgba(0,0,0,' + fout.toFixed(3) + ')'; ctx.fillRect(0, 0, LY.W, LY.H); }
  }
  KW.registerLayer({ id: 'card', z: 90, render: card });
})();
