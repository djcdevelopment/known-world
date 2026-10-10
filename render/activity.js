// Activity metadata has its own units: no inferred yields, models or GPU time.
(function () {
  const KW = window.KW, D = KW.D, A = D.activity;
  if (!A) return;
  const U = KW.util, FONT = '"JetBrains Mono", monospace';
  const counts = Object.fromEntries(Object.entries(A.counts).map(([k, v]) => [k, U.i32(v)]));
  const lanes = A.lanes.map(l => ({ ...l, hist: U.i32(l.hist) }));
  const first = lanes.map(l => { const i = l.hist.findIndex(v => v > 0); return i < 0 ? D.F : i; });
  KW.activity = { counts, lanes, notes: A.notes };
  const number = v => KW.fmt.commas(v);

  function counters(ctx, f) {
    const LY = KW.LAY;
    if (!LY.ia) return;
    const portrait = LY.mode === 'portrait';
    const left = portrait ? 14 : 748, available = portrait ? LY.W - 28 : LY.ia.nat[0] - left - 12;
    const wide = !portrait && available >= 670, cols = wide ? 5 : 2, cw = available / cols;
    const valueAt = key => counts[key] ? counts[key][f] : 0;
    const items = [
      ['LOCAL CALLS', counts.local_calls[f], 'HEARTH dispatch records', '#e2ef6a', ''],
      ['HEARTH RUNS', counts.executions[f], 'peak ' + counts.overlap_peak[f] + ' · ' + counts.failed[f] + ' failed', '#e2ef6a', valueAt('fleet_results') + ' fleet results'],
      ['ANTIGRAVITY', counts.conversations[f], 'conversations seen*', '#b5a2ef', '*last recorded update'],
      ['MEASURED TRIALS', valueAt('bench_trials'), valueAt('bench_measurements') + ' bench configurations', '#f0d883', valueAt('bench_runs') + ' recorded runners'],
      ['DIRECT RESEARCH', valueAt('direct_attempts'), 'attempts outside HEARTH', '#efb065', valueAt('experiment_trials') + ' experiment records']
    ];
    items.forEach(([label, value, note, color, foot], i) => {
      if (!value) return;
      const x = left + (i % cols) * cw;
      const y = portrait ? LY.top + 18 + Math.floor(i / cols) * 66 : wide ? 17 : 12 + Math.floor(i / cols) * 24;
      ctx.save(); ctx.beginPath(); ctx.rect(x, y - 12, cw - 8, wide || portrait ? 72 : 25); ctx.clip();
      ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      ctx.fillStyle = KW.C.fg2; ctx.font = (wide || portrait ? '10px ' : '8px ') + FONT; ctx.fillText(label, x, y);
      ctx.fillStyle = color; ctx.font = (wide || portrait ? '25px ' : '13px ') + FONT; ctx.fillText(number(value), x, y + (wide || portrait ? 25 : 12));
      if (wide || portrait) { ctx.font = '9px ' + FONT; ctx.fillStyle = KW.C.muted; ctx.fillText(note, x, y + 42); ctx.fillText(foot, x, y + 55); }
      ctx.restore();
    });
  }

  function pulses(ctx, f) {
    const v = KW.view(f), life = 22;
    for (const [at, region, lane, count] of A.pulses) {
      if (at > f) break;
      const age = f - at;
      if (age >= life || KW.rfirst[region] > f) continue;
      const x = KW.sx(KW.rx[region], v), y = KW.sy(KW.ry[region], v), t = age / life;
      ctx.globalAlpha = (1 - t) * 0.75 * KW.codaK(f);
      ctx.strokeStyle = lanes[lane].color; ctx.lineWidth = 1.5;
      const radius = 9 + 30 * t + Math.min(10, Math.log2(1 + count) * 2);
      ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.stroke();
      if (age < 12 && KW.LAY.mode !== 'portrait') {
        ctx.fillStyle = lanes[lane].color; ctx.font = '10px ' + FONT; ctx.textAlign = 'left';
        ctx.fillText(['conversation', 'execution', 'research record', 'bench run', 'fleet result', 'direct research', 'bench measure', 'experiment trial'][lane], x + radius + 4, y - 4);
      }
    }
  }

  KW.drawActivityScore = function (ctx, f, y0, s, condensed) {
    const axis = KW.iaAxis;
    lanes.forEach((lane, i) => {
      if (f < first[i]) return;
      const y = y0 + i * s;
      ctx.fillStyle = 'rgba(' + KW.C.mutedRgb + ',0.18)';
      ctx.fillRect(axis.AX0, y + s - 1, axis.AX1 - axis.AX0, 1);
      ctx.fillStyle = lane.color;
      for (let g = Math.max(0, f - axis.WF + 1); g <= f; g++) {
        const n = lane.hist[g]; if (!n) continue;
        const h = Math.min(s - 3, 2 + Math.log2(1 + n) * 2);
        ctx.fillRect(Math.round(axis.xOf(f, g)), y + s - 2 - h, 2, h);
      }
      ctx.fillRect(axis.I.nameX + 4, y + Math.floor(s / 2) - 2, 5, 5);
      if (!condensed) {
        ctx.font = '10px ' + FONT; ctx.fillStyle = KW.C.fg2; ctx.textAlign = 'left';
        ctx.fillText(lane.name, axis.I.nameX + 14, y + Math.floor(s / 2) + 4);
      }
    });
  };
  KW.registerLayer({ id: 'activity-pulses', z: 54, map: true, render: pulses });
  KW.registerLayer({ id: 'activity-counters', z: 81, render: counters });
})();
