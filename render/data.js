// data.js: decode window.KW_DATA (base64 typed arrays). Refuses a wrong version. No names ever arrive here.
(function () {
  function u8(b64) { const s = atob(b64), a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i); return a; }
  function f64(b64) { const a = u8(b64); return new Float64Array(a.buffer, 0, a.length / 8); }
  function f32(b64) { const a = u8(b64); return new Float32Array(a.buffer, 0, a.length / 4); }
  function i32(b64) { const a = u8(b64); return new Int32Array(a.buffer, 0, a.length / 4); }
  function u16(b64) { const a = u8(b64); return new Uint16Array(a.buffer, 0, a.length / 2); }
  const D = window.KW_DATA;
  if (!D || (D.version !== 1 && D.version !== 2)) throw new Error('KW_DATA version mismatch');
  const KW = window.KW = { D, layers: [], fonts: {}, util: { u8, f64, f32, i32, u16 } };
  KW.tau = f64(D.tau);
  KW.era = u8(D.era);
  KW.F = D.F; KW.fps = D.fps;
  // layout from the viewport. The compile writes the landscape frame (1920 x 1080 and the HUD insets) and the portrait recipe; the page
  // derives its logical frame from the viewport: landscape keeps the height 1080 and takes the width from the aspect (16:9 gives the
  // export frame exactly), portrait is 450 logical px wide. The export path (?export=1 without vw/vh) always uses the compiled frame.
  // The map owns the whole frame; the plates hug the edges at about 60 percent opacity and the camera fits the known world into the
  // safe area, the frame minus the plates' insets (KW.VIEW). Nothing in a layer hard-codes a size: everything reads KW.LAY.
  const Q = new URLSearchParams(location.search);
  const L0 = D.layout || { W: 1920, H: 1080, hud: 'columns', alpha: 1, left: 240, top: 64, right: 320, bottom: 120, safe: [240, 64, 1360, 896] };
  const exporting = Q.get('export') === '1';
  const vw = parseFloat(Q.get('vw')) || (exporting ? 0 : window.innerWidth), vh = parseFloat(Q.get('vh')) || (exporting ? 0 : window.innerHeight);
  const dpr = parseFloat(Q.get('dpr')) || (exporting ? 1 : (window.devicePixelRatio || 1));
  function layoutFor() {
    const LY = Object.assign({ mode: 'landscape', stream: !!D.stream, bandY: L0.H - L0.bottom, bandH: L0.bottom, tickerH: L0.top, stripH: 0, tpH: 0, B: 1, css: 1 }, L0);
    if (!vw || !vh) return LY;
    if (vw >= vh) {
      const H = L0.H, W = Math.max(1440, Math.min(2560, Math.round(H * vw / vh)));
      LY.W = W; LY.H = H;
      LY.css = Math.min(vw / W, vh / H); LY.B = LY.css * dpr;
      const streamW = LY.stream && D.stream ? D.stream.col_w : 0;
      LY.safe = [L0.left, L0.top, W - L0.left - L0.right - streamW, H - L0.top - L0.bottom];
      if (W === L0.W && H === L0.H) LY.safe = L0.safe.slice();
      if (LY.B === 1) LY.B = 1;
      return LY;
    }
    const P = D.layout_portrait || { w: 450, ticker: 56, strip: 30, band: 84, tp: 64 };
    const W = P.w, H = Math.round(W * vh / vw);
    Object.assign(LY, { mode: 'portrait', W, H, left: 0, right: 0, top: P.ticker + P.strip, tickerH: P.ticker, stripH: P.strip, bandH: P.band, tpH: P.tp,
                        bottom: P.band + P.tp, bandY: H - P.band - P.tp, stream: false });
    LY.css = vw / W; LY.B = LY.css * dpr;
    LY.safe = [0, LY.top, W, H - LY.top - LY.bottom];
    return LY;
  }
  const LY = layoutFor();
  KW.LAY = LY; KW.B = LY.B; KW.dpr = dpr; KW.viewport = { w: vw, h: vh };
  KW.FRAME = { x: 0, y: 0, w: LY.W, h: LY.H };
  KW.VIEW = { x: LY.safe[0], y: LY.safe[1], w: LY.safe[2], h: LY.safe[3], cx: LY.safe[0] + LY.safe[2] / 2, cy: LY.safe[1] + LY.safe[3] / 2 };
  // the camera is compiled for the landscape safe area; any other safe area contains it (what was in view stays in view)
  KW.camK = (L0.safe[2] === LY.safe[2] && L0.safe[3] === LY.safe[3]) ? 1 : Math.min(LY.safe[2] / L0.safe[2], LY.safe[3] / L0.safe[3]);
  KW.ui = { nations: false, surfaces: false };
  KW.compat = Q.get('compat') === 'slice9';   // verification arm: no hashmark hairline, the slice-9 stream header; at 1920 x 1080 it must hash equal to the slice-9 renderer
  // a HUD plate: translucent dark panel with a 1 px border (opaque under hud: columns)
  KW.plate = function (ctx, x, y, w, h) {
    ctx.fillStyle = 'rgba(11,14,20,' + LY.alpha.toFixed(3) + ')'; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = LY.alpha < 1 ? 'rgba(74,86,112,0.55)' : '#1b2230';
    ctx.fillRect(x, y, w, 1); ctx.fillRect(x, y + h - 1, w, 1); ctx.fillRect(x, y, 1, h); ctx.fillRect(x + w - 1, y, 1, h);
  };
  // running totals helpers: thousands separators, compact figures, and the shared log scale of the micro-bars
  // (0 below 10; full at 10^7.5; faint ticks at 1k, 10k, 100k, 1M)
  const commas = v => { let s = String(Math.round(v)), o = ''; while (s.length > 3) { o = ',' + s.slice(-3) + o; s = s.slice(0, -3); } return s + o; };
  const compact = v => v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e3 ? (v / 1e3).toFixed(v >= 1e4 ? 0 : 1) + 'k' : String(Math.round(v));
  const barLen = (v, w) => v < 10 ? 0 : Math.min(w, Math.round(w * (Math.log10(v) - 1) / 6.5));
  const TICKS = [3, 4, 5, 6];
  function microBar(ctx, x, y, w, h, vals, color) {
    // vals: one value (a bar of height h) or two (ins over del, each h/2 rounded)
    ctx.fillStyle = 'rgba(139,147,166,0.10)'; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = color;
    if (vals.length === 1) ctx.fillRect(x, y, barLen(vals[0], w), h);
    else { const h1 = Math.floor(h / 2); ctx.fillRect(x, y, barLen(vals[0], w), h1); ctx.fillRect(x, y + h - h1, barLen(vals[1], w), h1); }
    ctx.fillStyle = 'rgba(232,224,192,0.22)';
    for (const t of TICKS) ctx.fillRect(x + Math.round(w * (t - 1) / 6.5), y - 1, 1, h + 2);
  }
  KW.fmt = { commas, compact, barLen, microBar };
  KW.registerLayer = function (l) { KW.layers.push(l); KW.layers.sort((a, b) => a.z - b.z); };
})();
