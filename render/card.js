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
    ctx.fillStyle = 'rgba(7,9,14,' + (0.96 * fin).toFixed(3) + ')'; ctx.fillRect(0, 0, 1920, 1080);
    ctx.globalAlpha = fin;
    const x0 = 160, cols = [x0, x0 + 360, x0 + 560, x0 + 700, x0 + 930, x0 + 1250], y0 = 150, rowH = 62;
    ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
    ctx.font = '18px ' + FONT; ctx.fillStyle = '#8b93a6';
    ['', 'first test', 'tests', 'yield', 'single / MIRV / unified', 'tiles explored / laid out'].forEach((h, i) => { if (h) ctx.fillText(h, cols[i], y0 - 16); });
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
    }
    ctx.font = '20px ' + FONT; ctx.fillStyle = '#8b93a6';
    D.card_footer.forEach((t, i) => ctx.fillText(t, x0, 950 + i * 30));
    ctx.globalAlpha = 1;
    if (fout > 0) { ctx.fillStyle = 'rgba(0,0,0,' + fout.toFixed(3) + ')'; ctx.fillRect(0, 0, 1920, 1080); }
  }
  KW.registerLayer({ id: 'card', z: 90, render: card });
})();
