// export/perf.mjs: frame-time budget. Renders a deterministic grid of frames (and any named ones) twice, with and without
// the stream layer, timing each renderFrame with performance.now (a measurement only; never part of a render).
import {createRequire} from 'module';
import path from 'path';
const require = createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium} = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const root = path.resolve(new URL('..', import.meta.url).pathname);
const browser = await chromium.launch({headless: true, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text']});
const ctx = await browser.newContext({viewport: {width: 1920, height: 1080}, deviceScaleFactor: 1});
const page = await ctx.newPage();
await page.goto('file://' + root + '/render/index.html?export=1&data=' + encodeURIComponent(A.data));
await page.waitForFunction(() => window.__ready === true);
const extra = (A.frames || '').split(',').filter(Boolean).map(Number);
const r = await page.evaluate(({n, run, extra}) => {
  // blocks of `run` consecutive frames (the real access pattern), an untimed warm-up frame before each block
  const F = window.KW.F, starts = [];
  for (let i = 0; i < n; i++) starts.push(Math.max(1, Math.floor((i + 0.5) * (F - run) / n)));
  for (const e of extra) starts.push(e);
  starts.sort((x, y) => x - y);
  const pass = off => { window.kwOff(off); const out = []; for (const s0 of starts) { window.renderFrame(s0 - 1); for (let f = s0; f < s0 + run; f++) { const t = performance.now(); window.renderFrame(f); document.getElementById('c').getContext('2d').getImageData(0, 0, 1, 1); out.push(performance.now() - t); } } return out; };
  pass([]);
  const all = pass([]), no = pass(['stream']);
  window.kwOff([]);
  const q = (a, p) => { const s = a.slice().sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
  const d = all.map((v, i) => v - no[i]);
  const r3 = o => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, Math.round(v * 100) / 100]));
  return {frames: all.length, total: r3({median: q(all, 0.5), p95: q(all, 0.95), max: Math.max(...all)}), without_stream: r3({median: q(no, 0.5), p95: q(no, 0.95), max: Math.max(...no)}),
          stream_delta: r3({median: q(d, 0.5), p95: q(d, 0.95), max: Math.max(...d)}), errors: window.kwErrors()};
}, {n: parseInt(A.n || '40', 10), run: parseInt(A.run || '30', 10), extra});
console.log(JSON.stringify(r));
await browser.close();
