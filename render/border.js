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

  // --- the growing legend: right 320 px, one row per nation sliding in at its entry frame ------------------------
  if (!D.nat_names) return;
  const U = KW.util, F = D.F, N = D.nat_names.length;
  const entry = U.i32(D.nat_entry_f), tests = U.u16(D.tests_cum), lines = U.f32(D.lines_cum), files = U.f32(D.files_cum);
  const commits = U.f32(D.commits_cum), capfiles = U.f32(D.capfiles_cum);
  const compact = v => v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e3 ? (v / 1e3).toFixed(v >= 1e4 ? 0 : 1) + 'k' : String(Math.round(v));
  function drawLegend(ctx, f) {
    const x0 = 1600, rowH = 76;
    ctx.fillStyle = '#0b0e14'; ctx.fillRect(x0, 64, 320, 1016);
    ctx.fillStyle = '#1b2230'; ctx.fillRect(x0, 64, 1, 1016);
    ctx.textBaseline = 'alphabetic';
    for (let i = 0; i < N; i++) {
      const age = f - entry[i];
      if (age < 0) continue;
      const u = Math.min(1, age / 12), s = u * u * (3 - 2 * u), dx = Math.round(320 * (1 - s));
      const y = 64 + 12 + i * rowH, x = x0 + dx;
      const fl = age < 18 ? 1 - age / 18 : 0;
      ctx.fillStyle = KW.palette.rgba(i, 0.62 + 0.3 * fl, 1);
      ctx.fillRect(x + 14, y + 4, 16, 16);
      ctx.font = '20px ' + FONT; ctx.fillStyle = '#e8e0c0'; ctx.textAlign = 'left';
      ctx.fillText(D.nat_names[i], x + 40, y + 20);
      ctx.font = '28px ' + FONT; ctx.textAlign = 'right';
      ctx.fillText(String(tests[i * F + f]), x + 306, y + 22);
      ctx.textAlign = 'left';
      // chips: a new chip is named for 3 s (90 frames in the full piece, scaled by the cut), then reads short
      let cx = x + 14; const hold = Math.max(18, Math.round(90 * D.env_scale));
      for (const c of D.chips) {
        if (c.n !== i || c.f > f) continue;
        const fresh = f - c.f < hold, label = fresh ? c.label : c.short;
        ctx.font = '12px ' + FONT; ctx.fillStyle = KW.palette.rgba(i, fresh ? 0.9 : 0.62, 1);
        ctx.fillText(label, cx, y + 38);
        cx += label.length * 7.4 + 10;
      }
      ctx.font = '14px ' + FONT; ctx.fillStyle = '#8b93a6';
      const ln = lines[i * F + f], fl2 = files[i * F + f];
      const yv = ln > 0 ? compact(ln) + ' lines' : (fl2 > 0 ? compact(fl2) + ' files' : '0');
      ctx.fillText(yv + '  \u00b7  ' + compact(commits[i * F + f]) + 'c ' + compact(capfiles[i * F + f]) + 'f', x + 14, y + 58);
    }
    ctx.textAlign = 'left';
  }
  KW.registerLayer({ id: 'legend', z: 70, render: drawLegend });
})();
