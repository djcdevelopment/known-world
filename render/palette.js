// palette.js: OKLCH by nation (hue table from DIRECTION), generation shades at 0.06 L steps. Pure math, no names.
(function () {
  const KW = window.KW, D = KW.D;
  const HUE = { human: [85, 0.045], chatgpt: [155, 0.16], claude: [35, 0.17], codex: [205, 0.13], opencode: [300, 0.18], local_model: [27, 0.2], automation: [80, 0.16] };
  function gamma(v) { v = v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055; return v < 0 ? 0 : v > 1 ? 1 : v; }
  function oklch(L, C, H) {
    const h = H * Math.PI / 180, a = C * Math.cos(h), b = C * Math.sin(h);
    const l_ = L + 0.3963377774 * a + 0.2158037573 * b, m_ = L - 0.1055613458 * a - 0.0638541728 * b, s_ = L - 0.0894841775 * a - 1.2914855480 * b;
    const l = l_ * l_ * l_, m = m_ * m_ * m_, s = s_ * s_ * s_;
    return [255 * gamma(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
            255 * gamma(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
            255 * gamma(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)];
  }
  const cache = new Map();
  // rgba string of a nation class index at lightness L (quantised to 1/64) and alpha. Only the rgb prefix is cached:
  // alpha is formatted on every call, so no result depends on what was drawn before (render(f) stays pure).
  function rgba(ni, L, a) {
    const Lq = Math.round(L * 64), key = ni * 1000 + Lq;
    let s = cache.get(key);
    if (!s) {
      const cls = D.nat_classes[ni], hc = HUE[cls] || [250, 0.02];
      const c = oklch(Lq / 64, hc[1], hc[0]);
      s = 'rgba(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ',';
      cache.set(key, s);
    }
    return s + (a < 0 ? 0 : a > 1 ? 1 : a).toFixed(3) + ')';
  }
  function rgb(L, C, H) { const c = oklch(L, C, H); return 'rgb(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ')'; }
  function rgbaRaw(L, C, H, a) { const c = oklch(L, C, H); return 'rgba(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ',' + a.toFixed(3) + ')'; }
  KW.palette = { oklch, rgba, rgb, rgbaRaw, HUE, genL: gi => Math.max(0.6, 0.92 - 0.06 * gi) };
})();
