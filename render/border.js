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
    // world running totals, cumulative, muted
    if (D.w_cum) {
      const F = D.F, W3 = KW.wcum || (KW.wcum = KW.util.f32(D.w_cum)), c = KW.fmt.compact;
      ctx.font = '14px ' + FONT; ctx.fillStyle = '#8b93a6';
      ctx.fillText('commits ' + c(W3[f]) + ' \u00b7 files ' + c(W3[F + f]) + ' \u00b7 lines ' + c(W3[2 * F + f]), 700, 38);
    }
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
  const commits = U.f32(D.commits_cum), capfiles = U.f32(D.capfiles_cum), parts = U.f32(D.parts_cum);
  const insC = U.f32(D.ins_cum), delC = U.f32(D.del_cum), rateN = U.f32(D.rate_nat), crN = D.created_nat ? U.f32(D.created_nat) : null;
  const fm = KW.fmt, UNIT = D.rate_unit_names;
  const compact = v => v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e3 ? (v / 1e3).toFixed(v >= 1e4 ? 0 : 1) + 'k' : String(Math.round(v));
  function drawLegend(ctx, f) {
    const x0 = 1600, rowH = 136;
    ctx.fillStyle = '#0b0e14'; ctx.fillRect(x0, 64, 320, 1016);
    ctx.fillStyle = '#1b2230'; ctx.fillRect(x0, 64, 1, 1016);
    ctx.textBaseline = 'alphabetic';
    ctx.save(); ctx.beginPath(); ctx.rect(x0 + 1, 64, 319, 1016); ctx.clip();  // nothing of a row or chip leaves the panel
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
      // chips: the last chip_max entered, a new chip named in words for 3 s (scaled by the cut), then abbreviated; "+n" overflow
      let cx = x + 14; const hold = D.chip_named_f, vis = [];
      for (const c of D.chips) if (c.n === i && c.f <= f) vis.push(c);
      const shown = vis.slice(Math.max(0, vis.length - D.chip_max)), over = vis.length - shown.length;
      ctx.font = '12px ' + FONT;
      if (over > 0) { ctx.fillStyle = 'rgba(139,147,166,0.9)'; ctx.fillText('+' + over, cx, y + 38); cx += ('+' + over).length * 7.4 + 8; }
      const right = x + 306;  // chips stay inside the panel: a caption that does not fit falls back to its short form, then is cut with an ellipsis, then dropped
      for (const c of shown) {
        const fresh = f - c.f < hold;
        let label = fresh ? c.label : c.short;
        const room = right - cx;
        if (label.length * 7.4 > room) label = c.short;
        if (label.length * 7.4 > room) { const n = Math.floor(room / 7.4) - 1; label = n >= 2 ? label.slice(0, n) + '\u2026' : ''; }
        if (!label) continue;
        ctx.fillStyle = KW.palette.rgba(i, fresh ? 0.9 : 0.62, 1);
        ctx.fillText(label, cx, y + 38);
        cx += label.length * 7.4 + 10;
      }
      ctx.font = '14px ' + FONT; ctx.fillStyle = '#8b93a6';
      const ln = lines[i * F + f], fl2 = files[i * F + f], pc = parts[i * F + f], tc = tests[i * F + f];
      let yv = ln > 0 ? compact(ln) + ' lines' : (fl2 > 0 ? compact(fl2) + ' files' : '0');
      if (tc === 0) yv = compact(pc) + (D.nat_classes[i] === 'local_model' ? ' offload calls' : ' sessions');
      ctx.fillText(yv + '  \u00b7  ' + compact(commits[i * F + f]) + 'c ' + compact(capfiles[i * F + f]) + 'f', x + 14, y + 58);
      // running totals: log micro-bars on a shared scale (ticks 1k 10k 100k 1M) in the nation's hue, then the rate
      const k = i * F + f, hue = KW.palette.rgba(i, 0.62, 0.9), bx = x + 150, bw = 156;
      const rows = [['commits', fm.commas(commits[k]), [commits[k]]], ['files', fm.commas(capfiles[k]), [capfiles[k]]],
                    ['lines', '+' + fm.compact(insC[k]) + ' \u2212' + fm.compact(delC[k]), [insC[k], delC[k]]]];
      ctx.font = '12px ' + FONT;
      for (let r = 0; r < 3; r++) {
        const by = y + 76 + r * 15;
        ctx.textAlign = 'left'; ctx.fillStyle = '#8b93a6'; ctx.fillText(rows[r][0], x + 14, by);
        ctx.textAlign = 'right'; ctx.fillStyle = '#c9c3a8'; ctx.fillText(rows[r][1], x + 142, by);
        fm.microBar(ctx, bx, by - 8, bw, 8, rows[r][2], hue);
      }
      ctx.textAlign = 'left'; ctx.fillStyle = '#8b93a6';
      ctx.fillText('commits/' + UNIT[KW.era[f]], x + 14, y + 121);
      ctx.textAlign = 'right'; ctx.fillStyle = '#c9c3a8'; ctx.fillText(fm.commas(rateN[k]), x + 142, y + 121);
      if (crN) { ctx.textAlign = 'left'; ctx.fillStyle = '#8b93a6'; ctx.fillText('created~ ' + fm.compact(crN[k]), x + 160, y + 121); }
      ctx.textAlign = 'left';
    }
    ctx.restore();
    ctx.textAlign = 'left';
  }
  KW.registerLayer({ id: 'legend', z: 70, render: drawLegend });
})();
