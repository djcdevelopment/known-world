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
  // map area on the 1920 x 1080 canvas: left 240 tallies, top 64 ticker, right 320 legend, bottom 120 band
  KW.VIEW = { x: 240, y: 64, w: 1360, h: 896, cx: 920, cy: 512 };
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
