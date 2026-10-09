// export/verify.mjs: page-side receipts for slice 3. Prints one JSON object.
//   1. order independence: 30 frames rendered in browser A (ascending) and browser B (seeded shuffle): PNG sha256 equal
//   2. buildState dump at three frames (exact activity), for the Python brute-force comparison
//   3. luminance budget: max OKLab L of the map area, fields only vs everything, at the busiest frames
import {createRequire} from 'module';
import path from 'path';
import crypto from 'crypto';
const require = createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium} = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const root = path.resolve(new URL('..', import.meta.url).pathname);
const url = 'file://' + root + '/render/index.html?export=1&data=' + encodeURIComponent(A.data);
const opts = {headless: true, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text']};
function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
async function open() {
  const browser = await chromium.launch(opts);
  const ctx = await browser.newContext({viewport: {width: 1920, height: 1080}, deviceScaleFactor: 1});
  const page = await ctx.newPage();
  await page.goto(url);
  await page.waitForFunction(() => window.__ready === true);
  return {browser, page, cdp: await ctx.newCDPSession(page)};
}
async function shot(h, f) {
  await h.page.evaluate(f => window.renderFrame(f), f);
  const s = await h.cdp.send('Page.captureScreenshot', {format: 'png', optimizeForSpeed: true});
  return crypto.createHash('sha256').update(Buffer.from(s.data, 'base64')).digest('hex');
}
const a = await open();
const F = (await a.page.evaluate(() => window.kwInfo())).F;
const frames = Array.from({length: 30}, (_, i) => Math.floor((i + 0.5) * F / 30));
const hashA = {};
for (const f of frames) hashA[f] = await shot(a, f);
const b = await open();
const rnd = mulberry32(20261009), order = frames.slice();
for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
let equal = 0; const mism = [];
for (const f of order) { const h = await shot(b, f); if (h === hashA[f]) equal++; else mism.push(f); }
const out = {order_check: {frames: frames.length, equal, mismatched: mism, order: order.slice(0, 6)}};
// buildState dump
const sf = (A.state || '').split(',').filter(Boolean).map(Number);
out.state = {};
for (const f of sf) out.state[f] = await a.page.evaluate(f => { const S = KW.newState(); KW.buildState(f, S); return Array.from(S.exact); }, f);
// luminance
out.luminance = await a.page.evaluate(() => {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d');
  const lum = () => {
    const d = ctx.getImageData(240, 64, 1360, 896).data; let m = 0;
    for (let i = 0; i < d.length; i += 4) {
      const lin = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      const r = lin(d[i]), g = lin(d[i + 1]), b = lin(d[i + 2]);
      const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b), mm = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b), s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
      const L = 0.2104542553 * l + 0.7936177850 * mm - 0.0040720468 * s; if (L > m) m = L;
    }
    return m;
  };
  // busiest frames by live launches
  const F = KW.F, cands = [];
  for (let f = 0; f < F; f += 7) cands.push([KW.getState(f).nlive, f]);
  cands.sort((x, y) => y[0] - x[0] || x[1] - y[1]);
  const busy = cands.slice(0, 3).map(x => x[1]);
  const rows = [];
  let fieldMax = 0, allMax = 0;
  for (const f of busy.concat([Math.floor(F * 0.3), Math.floor(F * 0.6), Math.floor(F * 0.8)])) {
    kwOff(['launches', 'legend', 'ticker']); renderFrame(f); const lf = lum();
    kwOff([]); renderFrame(f); const la = lum();
    rows.push({f, nlive: KW.getState(f).nlive, field_max_L: +lf.toFixed(4), all_max_L: +la.toFixed(4)});
    fieldMax = Math.max(fieldMax, lf); allMax = Math.max(allMax, la);
  }
  return {rows, field_max_L: +fieldMax.toFixed(4), all_max_L: +allMax.toFixed(4)};
});
console.log(JSON.stringify(out));
await a.browser.close(); await b.browser.close();
