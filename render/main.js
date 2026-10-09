// main.js: the canvas, renderFrame(f), export purity. No Date, no Math.random; rAF only outside ?export=1.
(function () {
  const KW = window.KW, D = KW.D;
  const Q = new URLSearchParams(location.search);
  const cv = document.getElementById('c'), ctx = cv.getContext('2d');
  KW.errors = [];
  function renderFrame(f) {
    f = Math.max(0, Math.min(KW.F - 1, f | 0));
    if (f === D.probe_f) { ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, cv.width, cv.height); return; }
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = '#07090e'; ctx.fillRect(0, 0, cv.width, cv.height);
    for (const l of KW.layers) {
      if (KW.off && KW.off.has(l.id)) continue;
      ctx.save();
      try { l.render(ctx, f); } catch (e) { KW.errors.push(l.id + '@' + f + ':' + e.message); }
      ctx.restore();
    }
  }
  window.renderFrame = renderFrame;
  window.kwErrors = () => KW.errors;
  window.kwOff = list => { KW.off = new Set(list); };
  window.kwInfo = () => ({ F: KW.F, fps: KW.fps, font: ctx.font, layers: KW.layers.map(l => l.id) });
  const ready = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
  ready.then(() => {
    if (Q.get('export') === '1') { window.__ready = true; return; }
    // preview: wall-clock driven playback, never used by the export
    let t0 = null;
    function tick(ts) { if (t0 === null) t0 = ts; renderFrame(Math.floor((ts - t0) * KW.fps / 1000) % KW.F); requestAnimationFrame(tick); }
    renderFrame(0); window.__ready = true; requestAnimationFrame(tick);
  });
})();
