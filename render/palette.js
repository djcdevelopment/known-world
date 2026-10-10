// palette.js: OKLCH by nation (hue table from DIRECTION), generation shades at 0.06 L steps. Pure math, no names.
(function () {
  const KW = window.KW, D = KW.D;
  const HUE = { human: [85, 0.045], chatgpt: [155, 0.16], claude: [35, 0.17], codex: [205, 0.13], opencode: [300, 0.18], local_model: [27, 0.2], automation: [80, 0.16], gemini: [195, 0.12] };
  // Known World design system (design/known-world-design-system/tokens.json, nation-*): under layout ia the nation hues and chromas are the system's hex values, read back to OKLCH;
  // the lightness stays the film's own physics (fields capped at L 0.55, launches above it), so a hue changes without changing the luminance budget.
  const SYS_HEX = window.KW_SYS.nation;
  const design = !!(D.ia && D.ia.design);
  function lin(c) { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
  function hexToOklch(h) {
    const r = lin(parseInt(h.slice(1, 3), 16)), g = lin(parseInt(h.slice(3, 5), 16)), b = lin(parseInt(h.slice(5, 7), 16));
    const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b), m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b), s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
    const L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s, a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s, bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s;
    return { L, C: Math.hypot(a, bb), h: (Math.atan2(bb, a) * 180 / Math.PI + 360) % 360 };
  }
  KW.hexToOklch = hexToOklch;
  const OLD_HUE = {}; for (const k of Object.keys(HUE)) OLD_HUE[k] = HUE[k].slice();
  if (design) for (const k of Object.keys(SYS_HEX)) { const o = hexToOklch(SYS_HEX[k]); HUE[k] = [o.h, o.C]; }
  function gamma(v) { v = v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055; return v < 0 ? 0 : v > 1 ? 1 : v; }
  function inGamut(L, C, H) {
    const h = H * Math.PI / 180, a = C * Math.cos(h), b = C * Math.sin(h);
    const l_ = L + 0.3963377774 * a + 0.2158037573 * b, m_ = L - 0.1055613458 * a - 0.0638541728 * b, s_ = L - 0.0894841775 * a - 1.2914855480 * b;
    const l = l_ * l_ * l_, m = m_ * m_ * m_, s = s_ * s_ * s_, e = 1e-4;
    const r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;
    return r >= -e && r <= 1 + e && g >= -e && g <= 1 + e && bl >= -e && bl <= 1 + e;
  }
  function oklch(L, C, H) {
    if (design && !inGamut(L, C, H)) { let lo = 0, hi = C; for (let k = 0; k < 18; k++) { const mid = (lo + hi) / 2; if (inGamut(L, mid, H)) lo = mid; else hi = mid; } C = lo; }   // hold L and h, reduce chroma into sRGB
    const h = H * Math.PI / 180, a = C * Math.cos(h), b = C * Math.sin(h);
    const l_ = L + 0.3963377774 * a + 0.2158037573 * b, m_ = L - 0.1055613458 * a - 0.0638541728 * b, s_ = L - 0.0894841775 * a - 1.2914855480 * b;
    const l = l_ * l_ * l_, m = m_ * m_ * m_, s = s_ * s_ * s_;
    return [255 * gamma(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
            255 * gamma(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
            255 * gamma(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)];
  }
  // luminance budget: at the field cap (L 0.55) a nation's tint must not out-shine the film's own hue there. Where the system's hue has more than 10 percent more
  // relative luminance at the cap (nation-local, yellow), the field tint (L at or below the cap) is dimmed by a lightness factor; launches (L above the cap) are untouched.
  const fieldK = {};
  function relY(L, C, H) {
    if (!inGamut(L, C, H)) { let lo = 0, hi = C; for (let k = 0; k < 18; k++) { const mid = (lo + hi) / 2; if (inGamut(L, mid, H)) lo = mid; else hi = mid; } C = lo; }
    const h = H * Math.PI / 180, a = C * Math.cos(h), b = C * Math.sin(h);
    const l_ = L + 0.3963377774 * a + 0.2158037573 * b, m_ = L - 0.1055613458 * a - 0.0638541728 * b, s_ = L - 0.0894841775 * a - 1.2914855480 * b;
    const l = l_ * l_ * l_, m = m_ * m_ * m_, s = s_ * s_ * s_;
    const cl = v => v < 0 ? 0 : v > 1 ? 1 : v;
    return 0.2126 * cl(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s) + 0.7152 * cl(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s) + 0.0722 * cl(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s);
  }
  if (design) for (const k of Object.keys(HUE)) {
    const yo = relY(0.55, OLD_HUE[k][1], OLD_HUE[k][0]), yn = relY(0.55, HUE[k][1], HUE[k][0]);
    if (yn > 1.10 * yo) { let lo = 0.3, hi = 0.55; for (let i = 0; i < 24; i++) { const mid = (lo + hi) / 2; if (relY(mid, HUE[k][1], HUE[k][0]) > yo) hi = mid; else lo = mid; } fieldK[k] = lo / 0.55; }
  }
  KW.fieldDim = fieldK;
  const cache = new Map();
  // rgba string of a nation class index at lightness L (quantised to 1/64) and alpha. Only the rgb prefix is cached:
  // alpha is formatted on every call, so no result depends on what was drawn before (render(f) stays pure).
  function rgba(ni, L, a) {
    const Lq = Math.round(L * 64), key = ni * 1000 + Lq;
    let s = cache.get(key);
    if (!s) {
      const cls = D.nat_classes[ni], hc = HUE[cls] || [250, 0.02];
      let Le = Lq / 64; if (design && Le <= 0.5501 && fieldK[cls]) Le *= fieldK[cls];
      const c = oklch(Le, hc[1], hc[0]);
      s = 'rgba(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ',';
      cache.set(key, s);
    }
    return s + (a < 0 ? 0 : a > 1 ? 1 : a).toFixed(3) + ')';
  }
  function rgb(L, C, H) { const c = oklch(L, C, H); return 'rgb(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ')'; }
  function rgbaRaw(L, C, H, a) { const c = oklch(L, C, H); return 'rgba(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ',' + a.toFixed(3) + ')'; }
  const hexOf = (ni) => design ? SYS_HEX[D.nat_classes[ni]] : null;
  // flat colour for chrome (swatches, chips, bars, band, ticks, connectors): the system's exact hex with an alpha under the design system, the film's OKLCH shade otherwise
  const flatCache = new Map();
  function flat(ni, L, a) {
    if (!design) return rgba(ni, L, a);
    let s = flatCache.get(ni);
    if (!s) { const h = SYS_HEX[D.nat_classes[ni]]; s = 'rgba(' + parseInt(h.slice(1, 3), 16) + ',' + parseInt(h.slice(3, 5), 16) + ',' + parseInt(h.slice(5, 7), 16) + ','; flatCache.set(ni, s); }
    return s + (a < 0 ? 0 : a > 1 ? 1 : a).toFixed(3) + ')';
  }
  KW.palette = { oklch, rgba, flat, rgb, rgbaRaw, HUE, design, sysHex: SYS_HEX, hex: hexOf, genL: gi => Math.max(0.6, 0.92 - 0.06 * gi) };
})();
