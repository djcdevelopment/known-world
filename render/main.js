// main.js: the canvas, renderFrame(f), export purity. No Date, no Math.random in anything renderFrame reaches; the interactive clock lives in
// player.js and never loads under ?export=1. The canvas backs the logical frame (KW.LAY.W x H) at KW.B device pixels per logical pixel
// (1 in the export, so the 1920 x 1080 frames are the same pixels as before the layout came from the viewport).
(function () {
  const KW = window.KW, D = KW.D;
  const Q = new URLSearchParams(location.search);
  const cv = document.getElementById('c');
  const LY = KW.LAY, B = KW.B;
  cv.width = Math.round(LY.W * B); cv.height = Math.round(LY.H * B);
  if (B !== 1 || Q.get('vw')) { cv.style.width = Math.round(LY.W * LY.css) + 'px'; cv.style.height = Math.round(LY.H * LY.css) + 'px'; }
  const ctx = cv.getContext('2d');
  KW.errors = [];
  KW.resetT = c => c.setTransform(B, 0, 0, B, 0, 0);
  function renderFrame(f) {
    f = Math.max(0, Math.min(KW.F - 1, f | 0));
    KW.resetT(ctx);
    if (f === D.probe_f) { ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, LY.W, LY.H); return; }
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = '#07090e'; ctx.fillRect(0, 0, LY.W, LY.H);
    const V = KW.VIEW;
    for (const l of KW.layers) {
      if (KW.off && KW.off.has(l.id)) continue;
      ctx.save();
      if (l.map) { const C = LY.hud === 'plates' ? KW.FRAME : V; ctx.beginPath(); ctx.rect(C.x, C.y, C.w, C.h); ctx.clip(); }
      try { l.render(ctx, f); } catch (e) { KW.errors.push(l.id + '@' + f + ':' + e.message); }
      ctx.restore();
    }
  }
  window.renderFrame = renderFrame;
  window.kwErrors = () => KW.errors;
  window.kwOff = list => { KW.off = new Set(list); };
  window.kwOnlyBelow = z => { KW.off = new Set(KW.layers.filter(l => l.z >= z).map(l => l.id)); };
  window.kwInfo = () => ({ F: KW.F, fps: KW.fps, font: ctx.font, layers: KW.layers.map(l => l.id), layout: { mode: LY.mode, W: LY.W, H: LY.H, B: LY.B, safe: LY.safe } });
  window.kwUi = ui => { Object.assign(KW.ui, ui); };   // portrait overlays for stills; the export never sets it
  const ready = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
  ready.then(() => {
    if (Q.get('export') === '1') { window.__ready = true; return; }
    renderFrame(0); window.__ready = true;
    if (KW.startPlayer) KW.startPlayer(ctx, renderFrame);
  });
})();
