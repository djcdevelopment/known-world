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
  // hashmarks (marks.json via the data block): one 1 px tick per mark on a hairline over the whole timeline, kind-coloured and muted;
  // the playhead rides it. The exported ticker carries them faintly; the player's scrubber draws the same marks in the DOM.
  const MARKC = { era: [232, 224, 192, 0.55], surface: [112, 170, 226, 0.50], nation: [128, 210, 140, 0.50], migration: [240, 160, 96, 0.65], storm: [228, 98, 72, 0.65], regime: [190, 150, 232, 0.50] };
  KW.markColor = (kind, a) => { const c = MARKC[kind] || [200, 200, 200, 0.5]; return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + (a === undefined ? c[3] : a) + ')'; };
  function markLine(ctx, f, x0, x1, y) {
    const M = D.marks;
    ctx.fillStyle = '#2a3346'; ctx.fillRect(x0, y, x1 - x0, 1);
    if (M) for (const m of M) { ctx.fillStyle = KW.markColor(m.kind); ctx.fillRect(x0 + Math.round((x1 - x0 - 1) * m.frame / (KW.F - 1)), y - 4, 1, 5); }
    ctx.fillStyle = KW.C.fg; ctx.fillRect(x0 + Math.round((x1 - x0 - 2) * f / (KW.F - 1)), y - 3, 2, 7);
  }
  function drawTicker(ctx, f) {
    const LY = KW.LAY, W = LY.W, T = KW.tickerText(f), por = LY.mode === 'portrait';
    ctx.save();
    if (!LY.ia || por) KW.plate(ctx, 0, 0, W, LY.tickerH);
    ctx.textBaseline = 'alphabetic';
    // rate glyph: dim, brightening for 0.6 s (18 frames) after an era switch
    let a = 0.45;
    for (const sf of D.era_switch_f) { const k = f - sf; if (k >= 0 && k < 18) a = 0.45 + 0.55 * (1 - k / 18); }
    const tot = D.w_cum ? (() => { const F = D.F, W3 = KW.wcum || (KW.wcum = (D.totals_precision === 'f64' ? KW.util.f64 : KW.util.f32)(D.w_cum)), c = KW.fmt.compact; return (por ? 'c ' : 'commits ') + c(W3[f]) + (por ? ' \u00b7 touches ' : ' \u00b7 file touches ') + c(W3[F + f]) + (por ? ' \u00b7 Δlines ' : ' \u00b7 line changes ') + c(W3[2 * F + f]); })() : '';
    if (LY.ia && !por) {
      // ia: date (kw-ticker 44 px) and rate glyph on line one, the world totals beneath once commits exist; no hairline (the timeline's ruler carries the marks)
      ctx.font = '44px ' + FONT; ctx.fillStyle = KW.C.fg;
      ctx.fillText(T.text, 24, 48);
      ctx.font = '20px ' + FONT; ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.600)';   // constant: no era-switch brightening (motion budget)
      ctx.fillText(D.rate_labels[T.era], 430, 44);
      if (tot && KW.wcum[f] > 0) { ctx.font = '14px ' + FONT; ctx.fillStyle = KW.C.muted; ctx.fillText(tot, 24, 74); }
    } else if (!por) {
      ctx.font = '30px ' + FONT; ctx.fillStyle = KW.C.fg;
      ctx.fillText(T.text, 24, 42);
      ctx.font = '20px ' + FONT; ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',' + a.toFixed(3) + ')';
      ctx.fillText(D.rate_labels[T.era], 330, 40);
      // world running totals, cumulative, muted
      if (tot) { ctx.font = '14px ' + FONT; ctx.fillStyle = KW.C.muted; ctx.fillText(tot, 700, 38); }
      // 24-hour hairline, era C only: a story hour is 0.1 s at the C rate
      if (T.era === 2) {
        const x0 = 24, w = 270;
        ctx.fillStyle = '#2a3346'; ctx.fillRect(x0, 54, w, 1);
        for (let h = 0; h <= 24; h += 6) ctx.fillRect(x0 + Math.round(w * h / 24), 51, 1, 7);
        ctx.fillStyle = KW.C.fg; ctx.fillRect(x0 + Math.round(w * T.frac), 49, 2, 11);
      }
      if (D.marks && !KW.compat) markLine(ctx, f, 24, W - 24, 62);
    } else if (LY.ia) {
      ctx.font = '32px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.fillText(T.text, 12, 33);
      ctx.font = '11px ' + FONT; ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.600)'; ctx.fillText(D.rate_labels[T.era].split(' \u00b7 ')[0], 12, 56);   // the cut's long label ("... \u00b7 x8") would run into the totals
      if (tot && KW.wcum[f] > 0) { ctx.font = '10px ' + FONT; ctx.fillStyle = KW.C.muted; ctx.textAlign = 'right'; ctx.fillText(tot, W - 12, 56); ctx.textAlign = 'left'; }
    } else {
      ctx.font = '24px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.fillText(T.text, 12, 25);
      ctx.font = '12px ' + FONT; ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',' + a.toFixed(3) + ')'; ctx.fillText(D.rate_labels[T.era], 12, 42);
      if (tot && (!LY.ia || KW.wcum[f] > 0)) { ctx.font = '11px ' + FONT; ctx.fillStyle = KW.C.muted; ctx.textAlign = 'right'; ctx.fillText(tot, W - 12, 42); ctx.textAlign = 'left'; }
      if (D.marks && !KW.compat && !LY.ia) markLine(ctx, f, 12, W - 12, 51);
    }
    ctx.restore();
  }
  KW.registerLayer({ id: 'ticker', z: 80, render: drawTicker });

  // --- the growing legend: right 320 px, one row per nation sliding in at its entry frame ------------------------
  if (!D.nat_names) return;
  const U = KW.util, F = D.F, N = D.nat_names.length;
  const entry = U.i32(D.nat_entry_f), tests = U.u16(D.tests_cum), lines = U.f32(D.lines_cum), files = U.f32(D.files_cum);
  const commits = U.f32(D.commits_cum), capfiles = U.f32(D.capfiles_cum), parts = U.f32(D.parts_cum);
  const totals = D.totals_precision === 'f64' ? U.f64 : U.f32;
  const insC = totals(D.ins_cum), delC = totals(D.del_cum), rateN = U.f32(D.rate_nat), crN = D.created_nat ? U.f32(D.created_nat) : null;
  const fm = KW.fmt, UNIT = D.rate_unit_names;
  const compact = v => v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e3 ? (v / 1e3).toFixed(v >= 1e4 ? 0 : 1) + 'k' : String(Math.round(v));
  // one nation row at (x, y); cmp = compact (portrait overlay): no chips, bars tighter; mini = one line of figures, no bars
  function row(ctx, f, i, x, y, cmp, mini, ia, noCounters) {
    const age = f - entry[i];
    ctx.font = '20px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.textAlign = 'left';
    const fl = age < 18 && !ia ? 1 - age / 18 : 0;
    ctx.fillStyle = KW.palette.flat(i, 0.62 + 0.3 * fl, 1);
    ctx.fillRect(x + 14, y + 4, 16, 16);
    ctx.font = '20px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.textAlign = 'left';
    ctx.fillText(D.nat_names[i], x + 40, y + 20);
    ctx.font = (ia ? '30px ' : '28px ') + FONT; ctx.textAlign = 'right';   // kw-count: 30 px in the ia layout
    const k0 = i * F + f, burst = tests[k0], native = parts[k0];
    if (D.count_semantics) {
      ctx.font = '25px ' + FONT;
      if (burst > 0 || native > 0) ctx.fillText(fm.commas(burst > 0 ? burst : native), x + 306, y + 22);
      ctx.font = '10px ' + FONT; ctx.fillStyle = KW.C.muted;
      if (burst > 0 || native > 0) ctx.fillText(burst > 0 ? 'bursts' : (D.part_labels[i] === 'sessions' ? 'sessions' : 'calls'), x + 306, y + 38);
    } else if (!ia || burst > 0) ctx.fillText(String(burst), x + 306, y + 22);
    ctx.textAlign = 'left';
    if (!cmp) {
      // chips: the last chip_max entered, a new chip named in words for 3 s (scaled by the cut), then abbreviated; "+n" overflow
      let cx = x + 14; const hold = D.chip_named_f, vis = [];
      for (const c of D.chips) if (c.n === i && c.f <= f) vis.push(c);
      const shown = vis.slice(Math.max(0, vis.length - D.chip_max)), over = vis.length - shown.length;
      ctx.font = '12px ' + FONT;
      if (over > 0) { ctx.fillStyle = 'rgba(' + KW.C.mutedRgb + ',0.9)'; ctx.fillText('+' + over, cx, y + 38); cx += ('+' + over).length * 7.4 + 8; }
      const right = x + (D.count_semantics ? 240 : 306);
      for (const c of shown) {
        const fresh = f - c.f < hold;
        let label = fresh ? c.label : c.short;
        const room = right - cx;
        if (label.length * 7.4 > room) label = c.short;
        if (label.length * 7.4 > room) { const n = Math.floor(room / 7.4) - 1; label = n >= 2 ? label.slice(0, n) + '\u2026' : ''; }
        if (!label) continue;
        ctx.fillStyle = KW.palette.flat(i, fresh ? 0.9 : 0.62, 1);
        ctx.fillText(label, cx, y + 38);
        cx += label.length * 7.4 + 10;
      }
    }
    const yy = cmp ? 40 : (ia ? 56 : 58);
    ctx.font = '14px ' + FONT; ctx.fillStyle = KW.C.muted;
    const ln = lines[i * F + f], fl2 = files[i * F + f], pc = parts[i * F + f], tc = tests[i * F + f];
    let yv = ln > 0 ? compact(insC[i * F + f] + delC[i * F + f]) + ' changes' : (fl2 > 0 ? compact(fl2) + ' file links' : '0');
    if (tc === 0) yv = compact(pc) + ' ' + (D.part_labels ? D.part_labels[i] : D.nat_classes[i] === 'local_model' ? 'offload calls' : 'sessions');
    if (!ia) ctx.fillText(yv + '  \u00b7  ' + compact(commits[i * F + f]) + 'c ' + compact(capfiles[i * F + f]) + 'f', x + 14, y + yy);
    else {   // ia: only the nonzero parts of the summary line
      const parts_ = []; if (yv !== '0') parts_.push(yv);
      const cf_ = D.count_semantics
        ? (pc > 0 && tc > 0 ? fm.commas(pc) + ' ' + D.part_labels[i] : '')
        : [commits[i * F + f] > 0 ? compact(commits[i * F + f]) + 'c' : '', capfiles[i * F + f] > 0 ? compact(capfiles[i * F + f]) + 'f' : ''].filter(Boolean).join(' ');
      if (cf_) parts_.push(cf_);
      if (parts_.length) ctx.fillText(parts_.join('  \u00b7  '), x + 14, y + yy);
    }
    // running totals: log micro-bars on a shared scale (ticks 1k 10k 100k 1M) in the nation's hue, then the rate
    const k = i * F + f, hue = KW.palette.flat(i, 0.62, 0.9), bx = x + 150, bw = 156;
    if (noCounters) { ctx.textAlign = 'left'; return; }   // a compact row (below counters_min_row): tests, yield and chips only
    if (mini) {
      ctx.font = '12px ' + FONT; ctx.fillStyle = KW.C.fg2;
      ctx.fillText('+' + fm.compact(insC[k]) + ' \u2212' + fm.compact(delC[k]) + '   ' + fm.commas(rateN[k]) + ' c/' + UNIT[KW.era[f]], x + 14, y + 58);
      ctx.textAlign = 'left';
      return;
    }
    const rows = [['commits', fm.commas(commits[k]), [commits[k]]], [D.count_semantics ? 'git touches' : 'files', fm.commas(capfiles[k]), [capfiles[k]]],
                  ['lines', '+' + fm.compact(insC[k]) + ' \u2212' + fm.compact(delC[k]), [insC[k], delC[k]]]];
    ctx.font = '12px ' + FONT;
    const b0 = cmp ? 56 : (ia ? 72 : 76), bp = cmp ? 14 : (ia ? 14 : 15);
    // ia: bars ease over one film second (a boxcar over the last 30 frames of the cumulative series); a zero value draws no row at all
    // kw-label (design system): 11 px, uppercase, 1 px tracking, in muted; the film's own labels otherwise
    const lbl = (t, lx, ly) => { if (!ia || !KW.C.surf) { ctx.fillText(t, lx, ly); return; } ctx.save(); ctx.font = '11px ' + FONT; ctx.letterSpacing = '1px'; ctx.fillText(t.toUpperCase(), lx, ly); ctx.restore(); };
    const ez = a => { if (!ia) return a[k]; let t = 0; for (let g = 0; g < 30; g++) t += a[i * F + Math.max(0, f - g)]; return t / 30; };
    for (let r = 0; r < 3; r++) {
      if (ia && rows[r][2].every(v => v <= 0)) continue;
      const by = y + b0 + r * bp;
      ctx.textAlign = 'left'; ctx.fillStyle = KW.C.muted; lbl(rows[r][0], x + 14, by);
      ctx.textAlign = 'right'; ctx.fillStyle = KW.C.fg2; ctx.fillText(rows[r][1], x + 142, by);
      fm.microBar(ctx, bx, by - 8, bw, 8, ia ? (r === 2 ? [ez(insC), ez(delC)] : [ez(r === 0 ? commits : capfiles)]) : rows[r][2], hue);
    }
    const ry = y + (cmp ? 100 : (ia ? 115 : 121));
    if (!ia || rateN[k] > 0) {
      ctx.textAlign = 'left'; ctx.fillStyle = KW.C.muted;
      lbl('commits/' + UNIT[KW.era[f]], x + 14, ry);
      ctx.textAlign = 'right'; ctx.fillStyle = KW.C.fg2; ctx.fillText(fm.commas(rateN[k]), x + 142, ry);
    }
    if (crN && (!ia || crN[k] > 0)) { ctx.textAlign = 'left'; ctx.fillStyle = KW.C.muted; ctx.fillText('created~ ' + fm.compact(crN[k]), x + 160, ry); }
    ctx.textAlign = 'left';
  }
  // ia: a nation row exists from the first frame it has any signal (its entry, or a later frame if everything is still zero), one second fade-in,
  // no slide; rows keep entry order and never move. The panel plate hugs the rows. Zero figures are not drawn (see row).
  const sigF = new Int32Array(N).fill(F);
  for (let i = 0; i < N; i++) for (let g = Math.max(0, entry[i]); g < F; g++) {
    const k = i * F + g;
    if (tests[k] > 0 || commits[k] > 0 || capfiles[k] > 0 || lines[k] > 0 || files[k] > 0 || parts[k] > 0 || insC[k] > 0) { sigF[i] = g; break; }
  }
  KW.natShownF = sigF;
  const iaOrder = [...Array(N).keys()].sort((a, b) => sigF[a] - sigF[b] || a - b);
  // Fixed row heights keep entry order steady. Call/session-only rows do not need
  // space for empty capacity bars; preserve full counters as new providers enter.
  const capacityRow = i => commits[i * F + F - 1] > 0 || insC[i * F + F - 1] > 0 || delC[i * F + F - 1] > 0;
  const rowHeights = iaOrder.map(i => D.part_labels ? (capacityRow(i) ? 136 : 72) : D.ia?.nation_row || 136);
  const rowOffset = [0]; for (const h of rowHeights) rowOffset.push(rowOffset[rowOffset.length - 1] + h);
  function drawLegendIA(ctx, f) {
    const LY = KW.LAY, I = LY.ia;
    KW.nationRows = [];
    const vis = iaOrder.filter(i => f >= sigF[i]);
    if (!vis.length) return;
    const x0 = I.nat[0], y0 = I.nat[1], w = I.nat[2];
    KW.plate(ctx, x0, y0, w, Math.min(I.nat[3], 16 + rowOffset[N]));
    ctx.textBaseline = 'alphabetic';
    ctx.save(); ctx.beginPath(); ctx.rect(x0 + 1, y0, w - 9, I.nat[3]); ctx.clip();
    vis.forEach((i, r) => {
      const rowH = rowHeights[r], compact = rowH < D.ia.counters_min_row;
      const y = y0 + 12 + rowOffset[r], a = Math.min(1, (f - sigF[i] + 1) / I.fade_f);
      KW.nationRows.push({ i, x: x0, y, h: rowH, w });
      ctx.globalAlpha = a; row(ctx, f, i, x0, y, false, false, true, compact); ctx.globalAlpha = 1;
    });
    ctx.restore(); ctx.textAlign = 'left';
  }
  function drawLegend(ctx, f) {
    const LY = KW.LAY;
    if (LY.ia && LY.mode === 'landscape') return drawLegendIA(ctx, f);
    if (LY.mode === 'portrait') return portraitNations(ctx, f);
    const x0 = LY.W - LY.right, rowH = 136, PH = LY.H - LY.top;
    KW.plate(ctx, x0, LY.top, LY.right, PH);
    ctx.textBaseline = 'alphabetic';
    ctx.save(); ctx.beginPath(); ctx.rect(x0 + 1, LY.top, LY.right - 9, PH); ctx.clip();  // nothing of a row or chip leaves the panel
    KW.nationRows = [];
    for (let i = 0; i < N; i++) {
      const age = f - entry[i];
      if (age < 0) continue;
      const u = Math.min(1, age / 12), s = u * u * (3 - 2 * u), dx = Math.round(240 * (1 - s));
      const y = LY.top + 12 + i * rowH, x = x0 + dx;
      KW.nationRows.push({ i, x: x0, y, h: rowH, w: LY.right });
      ctx.globalAlpha = s;
      row(ctx, f, i, x, y, false, false);
      ctx.globalAlpha = 1;
    }
    ctx.restore();
    ctx.textAlign = 'left';
  }
  // portrait: a one-line strip of swatches with test counts under the ticker; a tap expands the compact panel over the map
  function portraitNations(ctx, f) {
    const LY = KW.LAY, y0 = LY.tickerH, h = LY.stripH, cw = LY.ia ? Math.floor((LY.W - 8) / Math.max(1, D.ia.nN)) : 54, oy = LY.ia ? 8 : 0, ef = i => LY.ia ? sigF[i] : entry[i];
    KW.nationRows = []; KW.surfBtn = null;
    if (LY.ia && !iaOrder.some(i => f >= sigF[i])) return;   // signal-gated: no strip until a nation exists
    KW.plate(ctx, 0, y0, LY.W, h);
    ctx.textBaseline = 'alphabetic';
    let x = 8;
    ctx.font = '13px ' + FONT;
    for (let i = 0; i < N; i++) {
      if (f < ef(i)) continue;
      ctx.fillStyle = KW.palette.flat(i, 0.62, 1); ctx.fillRect(x, y0 + 10 + oy, 10, 10);
      ctx.fillStyle = KW.C.fg; ctx.textAlign = 'left'; if (!LY.ia || tests[i * F + f] > 0) ctx.fillText(String(tests[i * F + f]), x + 14, y0 + 20 + oy);   // ia: a zero is not drawn
      KW.nationRows.push({ i, x, y: y0, h, w: cw });
      x += cw;
    }
    if (LY.ia) KW.surfBtn = { x: 0, y: 0, w: LY.W, h: LY.tickerH };   // a tap on the ticker opens the surface tallies (the strip is chips only)
    else {
    ctx.font = '12px ' + FONT; ctx.textAlign = 'right'; ctx.fillStyle = KW.ui.surfaces ? KW.C.fg : KW.C.muted;
    ctx.fillText('surfaces \u25be', LY.W - 8, y0 + 20); ctx.textAlign = 'left';
    KW.surfBtn = { x: LY.W - 100, y: y0, w: 100, h };
    }
    if (!KW.ui.nations) return;
    const nIn = []; for (let i = 0; i < N; i++) if (f >= ef(i)) nIn.push(i);
    const PWd = 320, PH = LY.bandY - LY.top, px = LY.W - PWd, rowH = Math.min(108, Math.floor((PH - 8) / Math.max(1, nIn.length))), mini = rowH < 92;
    KW.plate(ctx, px, LY.top, PWd, PH);
    ctx.save(); ctx.beginPath(); ctx.rect(px + 1, LY.top, PWd - 9, PH); ctx.clip();
    nIn.forEach((i, r) => row(ctx, f, i, px, LY.top + 8 + r * rowH, true, mini));
    ctx.restore(); ctx.textAlign = 'left';
  }
  KW.registerLayer({ id: 'legend', z: 70, render: drawLegend });
})();
