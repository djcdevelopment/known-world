// border.js: the top strip. The ticker (date, rate glyph, 24-hour hairline). Monospace fallback is recorded in the receipt.
(function () {
  const KW = window.KW, D = KW.D;
  const FONT = '"JetBrains Mono", monospace';
  const P2 = n => (n < 10 ? '0' : '') + n;
  // civil date from days since 1970-01-01 (Hinnant); integer arithmetic only
  function civil(z) {
    z += 719468;
    const era = Math.floor(z / 146097), doe = z - era * 146097;
    const yoe = Math.floor((doe - Math.floor(doe / 1460) + Math.floor(doe / 36524) - Math.floor(doe / 146096)) / 365);
    const y = yoe + era * 400, doy = doe - (365 * yoe + Math.floor(yoe / 4) - Math.floor(yoe / 100));
    const mp = Math.floor((5 * doy + 2) / 153), d = doy - Math.floor((153 * mp + 2) / 5) + 1;
    const m = mp < 10 ? mp + 3 : mp - 9;
    return [y + (m <= 2 ? 1 : 0), m, d];
  }
  KW.civil = civil;
  KW.tickerText = function (f) {
    const tau = KW.tau[f], day = Math.floor(tau + 1e-9);
    const [y, m, d] = civil(D.epoch0_days + day);
    const e = KW.era[f];
    return { text: e === 2 ? y + ' · ' + P2(m) + ' · ' + P2(d) : y + ' · ' + P2(m), frac: tau - day, era: e };
  };
  function drawTicker(ctx, f) {
    const W = ctx.canvas.width, T = KW.tickerText(f);
    ctx.save();
    ctx.fillStyle = '#0b0e14'; ctx.fillRect(0, 0, W, 64);
    ctx.fillStyle = '#1b2230'; ctx.fillRect(0, 63, W, 1);
    ctx.textBaseline = 'alphabetic';
    ctx.font = '30px ' + FONT; ctx.fillStyle = '#e8e0c0';
    ctx.fillText(T.text, 24, 42);
    // rate glyph: dim, brightening for 0.6 s (18 frames) after an era switch
    let a = 0.45;
    for (const sf of D.era_switch_f) { const k = f - sf; if (k >= 0 && k < 18) a = 0.45 + 0.55 * (1 - k / 18); }
    ctx.font = '20px ' + FONT; ctx.fillStyle = 'rgba(232,224,192,' + a.toFixed(3) + ')';
    ctx.fillText(D.rate_labels[T.era], 330, 40);
    // 24-hour hairline, era C only: a story hour is 0.1 s at the C rate
    if (T.era === 2) {
      const x0 = 24, w = 270;
      ctx.fillStyle = '#2a3346'; ctx.fillRect(x0, 54, w, 1);
      for (let h = 0; h <= 24; h += 6) ctx.fillRect(x0 + Math.round(w * h / 24), 51, 1, 7);
      ctx.fillStyle = '#e8e0c0'; ctx.fillRect(x0 + Math.round(w * T.frac), 49, 2, 11);
    }
    ctx.restore();
  }
  KW.registerLayer({ id: 'ticker', z: 80, render: drawTicker });
})();
