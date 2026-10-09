// panels.js: surface tallies (left 240 px) and the mirrored radio band (bottom 120 px). Plain figures; no captions on the map.
(function () {
  const KW = window.KW, D = KW.D, P = KW.palette, U = KW.util;
  if (!D.T || D.version < 2) return;
  const FONT = '"JetBrains Mono", monospace', F = D.F;
  const S = D.surfaces, nS = S.names.length;
  const tests = U.u16(D.sc_tests), commits = U.f32(D.sc_commits), files = U.f32(D.sc_files), islc = U.u16(D.isl_cum);
  const compact = v => v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e3 ? (v / 1e3).toFixed(v >= 1e4 ? 0 : 1) + 'k' : String(Math.round(v));
  const created = U.f32(D.sc_created), updated = U.f32(D.sc_updated), fm = KW.fmt;
  const HOSTIDX = { 'omen-e': 0, 'omen-c': 1, 'omen-linux': 2, 'am4': 3, 'fx99': 4 };
  const KEYS = ['omen-c', 'omen-e', 'omen-linux', 'am4', 'fx99', 'github'];
  function tallies(ctx, f) {
    const x0 = 0, LY = KW.LAY, por = LY.mode === 'portrait';
    if ((por || LY.ia) && !KW.ui.surfaces) return;   // portrait and the ia layout: the tallies sit behind a toggle (a tap, the key s)
    const PW = por ? 240 : (LY.ia ? 240 : LY.left), PH = por ? LY.bandY - LY.top : (LY.ia ? LY.ia.tl[1] - LY.top : LY.H - LY.top - LY.bottom);
    KW.plate(ctx, x0, LY.top, PW, PH);
    ctx.textBaseline = 'alphabetic';
    ctx.save(); ctx.beginPath(); ctx.rect(0, LY.top, PW - 8, PH); ctx.clip();
    // rows in entry order
    const idx = []; for (let i = 0; i < nS; i++) if (S.entry[i] < F) idx.push(i);
    idx.sort((a, b) => S.entry[a] - S.entry[b] || a - b);
    const rowH = por ? Math.min(96, Math.floor((PH - 12) / Math.max(1, idx.length))) : 96;
    KW.tallyRows = idx.map((i, r) => ({ i, y: LY.top + 12 + r * rowH, h: rowH, name: S.names[i] }));
    for (let r = 0; r < idx.length; r++) {
      const i = idx[r], age = f - S.entry[i];
      if (age < 0) continue;
      const u = Math.min(1, age / 12), s = LY.ia ? 1 : u * u * (3 - 2 * u), dx = LY.ia ? 0 : -Math.round(200 * (1 - s));
      const y = LY.top + 12 + r * rowH, x = x0 + dx, k = KEYS[i];
      ctx.globalAlpha = s;
      const gh = k === 'github';
      ctx.fillStyle = P.rgbaRaw(0.45, 0.05, 190, 0.9);
      if (!gh) ctx.fillStyle = P.rgbaRaw(0.45, 0.05, [275, 255, 165, 310, 60][['omen-c', 'omen-e', 'omen-linux', 'am4', 'fx99'].indexOf(k)], 0.95);
      if (KW.C.surf) ctx.fillStyle = KW.C.surf[i];   // design system: surface-* hex
      ctx.fillRect(x + 14, y + 4, 16, 16);
      ctx.font = '20px ' + FONT; ctx.fillStyle = KW.C.fg; ctx.textAlign = 'left'; ctx.fillText(S.names[i], x + 40, y + 20);
      ctx.font = '28px ' + FONT; ctx.textAlign = 'right';
      ctx.fillText(String(gh ? islc[f] : tests[i * F + f]), x + 226, y + 22);
      ctx.textAlign = 'left'; ctx.font = '14px ' + FONT; ctx.fillStyle = KW.C.muted;
      ctx.fillText(gh ? 'repos risen' : compact(commits[i * F + f]) + 'c  ' + compact(files[i * F + f]) + 'f', x + 14, y + 44);
      if (!gh) {
        // files created and files updated per surface: the same shared-log micro-bars as the right panel
        const k = i * F + f, hue = P.rgbaRaw(0.62, 0.05, [275, 255, 165, 310, 60][['omen-c', 'omen-e', 'omen-linux', 'am4', 'fx99'].indexOf(KEYS[i])], 0.9);
        ctx.font = '12px ' + FONT;
        [['created', created[k]], ['updated', updated[k]]].forEach((rw, r) => {
          const by = y + 62 + r * 15;
          ctx.textAlign = 'left'; ctx.fillStyle = KW.C.muted; ctx.fillText(rw[0], x + 14, by);
          ctx.textAlign = 'right'; ctx.fillStyle = KW.C.fg2; ctx.fillText(fm.compact(rw[1]), x + 128, by);
          fm.microBar(ctx, x + 134, by - 8, 92, 8, [rw[1]], hue);
        });
        ctx.textAlign = 'left';
      }
    }
    ctx.restore();
    ctx.textAlign = 'left';
  }
  const band = U.u8(D.band), names = D.band_names, BW = D.band_window_f;
  const col = names.map(n => D.nat_classes.indexOf(n));
  function drawBand(ctx, f) {
    const LY = KW.LAY, x0 = LY.left, w = LY.W - LY.left - LY.right, y0 = LY.bandY, h = LY.bandH, mid = y0 + h / 2, K = h === 120 ? 1 : h / 120;
    KW.plate(ctx, x0, y0, w, h);
    ctx.fillStyle = '#222b3b'; ctx.fillRect(x0 + 1, mid, w - 2, 1);
    const ncol = Math.floor(w / 2), ck = KW.codaK(f);
    for (let k = 0; k < ncol; k++) {
      const g = f - (BW - 1) + Math.round(k * (BW - 1) / (ncol - 1));
      if (g < 0) continue;
      const x = x0 + k * 2;
      let y = mid - 2;
      // chatter above by class, log-scaled, stacked
      for (let c = 0; c < 4; c++) {
        const a = band[c * F + g] / 255 * 22 * ck * K;
        if (a < 0.5) continue;
        ctx.fillStyle = P.rgba(col[c], 0.62, 0.85); ctx.fillRect(x, y - a, 2, a); y -= a;
      }
      // commits below, warm grey
      const cm = band[4 * F + g] / 255 * 50 * ck * K;
      if (cm >= 0.5) { ctx.fillStyle = 'rgba(150,135,112,0.8)'; ctx.fillRect(x, mid + 2, 2, cm); }
      // offloads: an ember hairline on the centre line
      const o = band[5 * F + g] / 255;
      if (o > 0.02) { ctx.fillStyle = P.rgba(D.nat_classes.indexOf('local_model'), 0.6, Math.min(1, 0.25 + o)); ctx.fillRect(x, mid - 1, 2, 2); }
    }
    // era ticks
    ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.55)';
    for (const sf of D.era_switch_f) { const k = Math.round((sf - (f - (BW - 1))) * (ncol - 1) / (BW - 1)); if (k >= 0 && k < ncol) ctx.fillRect(x0 + k * 2, y0 + 4, 1, h - 8); }
    
  }
  KW.registerLayer({ id: 'tallies', z: 71, render: tallies });
  if (!KW.LAY.ia) KW.registerLayer({ id: 'band', z: 72, render: drawBand });
})();
