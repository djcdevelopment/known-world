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
  KW.registerLayer = function (l) { KW.layers.push(l); KW.layers.sort((a, b) => a.z - b.z); };
})();
