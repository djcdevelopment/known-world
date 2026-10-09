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
  // information architecture (layout ia): four zones in the order the eye asks: ticker top-left, the map in the safe area, nations at the right,
  // the timeline at the bottom (marks ruler, chatter and commit band, lineage lanes on one scrolling axis). Rects come from the compile (D.ia).
  const IA0 = D.ia;
  function iaRects(W, H, por) {
    const I = IA0, P = I.portrait;
    if (!por) {
      const th = I.ticker[3], nw = I.nations[2], tlh = I.timeline[3], ty = H - tlh, rh = I.ruler[3], bh = I.band[3];
      const ax1 = W - (I.timeline[2] - I.ax1), ax0 = Math.max(I.name_w, ax1 - 3 * I.window_f);
      return { tick: [0, 0, I.ticker[2], th], nat: [W - nw, 0, nw, ty], tl: [0, ty, W, tlh], ruler: [0, ty, W, rh], band: [0, ty + rh, W, bh],
               lanes: [0, ty + rh + bh + 3, W, I.nl * I.pitch], ax0, ax1, pxf: (ax1 - ax0) / I.window_f, nameX: ax0 - I.name_w, nameW: I.name_w, pitch: I.pitch, nl: I.nl, window_f: I.window_f,
               safe: [0, th, W - nw, ty - th], fade_f: I.nation_fade_f, namePx: 10 };
    }
    // portrait (the primary frame, 360 x 640 css): ticker, nation strip, map, timeline. Closed = ruler + band at the bottom; open (the lanes behind a tap) = the zone grows up
    const rh = P.ruler, bh = P.band, tlc = rh + bh, tlo = P.lanes_open, ax1 = W - 8, ax0 = P.name_w;
    const mk = tl => { const ty = H - tl; return { tl: [0, ty, W, tl], ruler: [0, ty, W, rh], band: [0, ty + rh, W, bh], lanes: [0, ty + rh + bh + 3, W, I.nl * P.pitch] }; };
    return Object.assign({ tick: [0, 0, W, P.ticker], nat: [0, P.ticker, W, P.strip], ax0, ax1, pxf: (ax1 - ax0) / I.window_f, nameX: 3, nameW: P.name_w - 4, pitch: P.pitch, nl: I.nl, window_f: I.window_f,
             safe: [0, P.ticker + P.strip, W, H - P.ticker - P.strip - tlc], fade_f: I.nation_fade_f, namePx: 10, open: mk(tlo), closed: mk(tlc) }, mk(tlc));
  }
  function layoutFor() {
    if (IA0) return layoutIA();
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
  function layoutIA() {
    const LY = { mode: 'landscape', ia: null, stream: true, B: 1, css: 1, alpha: 1, hud: 'columns', W: L0.W, H: L0.H, bandY: 0, bandH: 0, tickerH: IA0.ticker[3], stripH: 0, tpH: 0, left: 0, top: IA0.ticker[3], right: IA0.nations[2], bottom: IA0.timeline[3] };
    if (vw && vh && vw < vh) {
      const P = IA0.portrait, W = P.w, H = Math.round(W * vh / vw);
      Object.assign(LY, { mode: 'portrait', W, H, stream: true, css: vw / W, tickerH: P.ticker, stripH: P.strip });
      LY.B = LY.css * dpr; LY.ia = iaRects(W, H, true);
      LY.top = P.ticker + P.strip; LY.bandY = LY.ia.tl[1]; LY.bottom = P.ruler + P.band; LY.left = 0; LY.right = 0;
    } else {
      if (vw && vh) {
        const H = L0.H, W = Math.max(1440, Math.min(2560, Math.round(H * vw / vh)));
        LY.W = W; LY.H = H; LY.css = Math.min(vw / W, vh / H); LY.B = LY.css * dpr;
      }
      LY.ia = iaRects(LY.W, LY.H, false);
      LY.bandY = LY.ia.band[1];
    }
    LY.safe = LY.ia.safe.slice();
    return LY;
  }
  const LY = layoutFor();
  KW.LAY = LY; KW.B = LY.B; KW.dpr = dpr; KW.viewport = { w: vw, h: vh };
  KW.FRAME = { x: 0, y: 0, w: LY.W, h: LY.H };
  KW.VIEW = { x: LY.safe[0], y: LY.safe[1], w: LY.safe[2], h: LY.safe[3], cx: LY.safe[0] + LY.safe[2] / 2, cy: LY.safe[1] + LY.safe[3] / 2 };
  // the camera is compiled for the landscape safe area; any other safe area contains it (what was in view stays in view)
  KW.camK = (L0.safe[2] === LY.safe[2] && L0.safe[3] === LY.safe[3]) ? 1 : Math.min(LY.safe[2] / L0.safe[2], LY.safe[3] / L0.safe[3]);
  KW.ui = { nations: false, surfaces: false, lanes: false };
  KW.compat = Q.get('compat') === 'slice9';   // verification arm: no hashmark hairline, the slice-9 stream header; at 1920 x 1080 it must hash equal to the slice-9 renderer
  // colours: the film's own (slice 10) unless the design system is on (layout ia, design_system on): design/known-world-design-system/tokens.json fg, fg-2, frame-muted, muted, frame-line, canvas, dim, sea
  const DS = !!(D.ia && D.ia.design);
  const SY = window.KW_SYS, hexRgb = h => parseInt(h.slice(1, 3), 16) + ',' + parseInt(h.slice(3, 5), 16) + ',' + parseInt(h.slice(5, 7), 16);
  KW.C = DS ? { fg: SY.color.fg, fgRgb: hexRgb(SY.color.fg), fg2: SY.color.fg2, muted: SY.color.frameMuted, mutedRgb: hexRgb(SY.color.frameMuted), muted2: SY.color.muted, rule: SY.color.frameLine,
                canvas: SY.color.canvas, sea: SY.color.sea, surf: ['omen-c', 'omen-e', 'omen-linux', 'am4', 'fx99', 'github'].map(k => SY.surface[k]), plateRgb: hexRgb(SY.color.canvas), dim: SY.color.dim }
            : { fg: '#e8e0c0', fgRgb: '232,224,192', fg2: '#c9c3a8', muted: '#8b93a6', mutedRgb: '139,147,166', muted2: '#5f6779', rule: '#1b2230', canvas: '#07090e', sea: null, surf: null, plateRgb: '11,14,20', dim: '#2a3346' };
  // a HUD plate: translucent dark panel with a 1 px border (opaque under hud: columns)
  KW.plate = function (ctx, x, y, w, h) {
    ctx.fillStyle = 'rgba(' + KW.C.plateRgb + ',' + LY.alpha.toFixed(3) + ')'; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = LY.alpha < 1 ? 'rgba(74,86,112,0.55)' : KW.C.rule;
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
    ctx.fillStyle = 'rgba(' + KW.C.mutedRgb + ',0.10)'; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = color;
    if (vals.length === 1) ctx.fillRect(x, y, barLen(vals[0], w), h);
    else { const h1 = Math.floor(h / 2); ctx.fillRect(x, y, barLen(vals[0], w), h1); ctx.fillRect(x, y + h - h1, barLen(vals[1], w), h1); }
    ctx.fillStyle = 'rgba(' + KW.C.fgRgb + ',0.22)';
    for (const t of TICKS) ctx.fillRect(x + Math.round(w * (t - 1) / 6.5), y - 1, 1, h + 2);
  }
  KW.fmt = { commas, compact, barLen, microBar };
  KW.registerLayer = function (l) { KW.layers.push(l); KW.layers.sort((a, b) => a.z - b.z); };
})();
