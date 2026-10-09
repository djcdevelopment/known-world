// export/landbox.mjs: the bounding box of the drawn land (the 'land' layer alone) inside the safe area, per frame, and its centre offset from the safe-area centre.
//   node export/landbox.mjs --data <rel> --frames f,f,f
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
const res = await page.evaluate(frames => {
  const cv = document.getElementById('c'), c2 = cv.getContext('2d'), W = cv.width, H = cv.height, V = KW.VIEW;
  window.kwOff(KW.layers.filter(l => l.id !== 'land').map(l => l.id));
  const out = {};
  for (const f of frames) {
    window.renderFrame(f);
    const d = c2.getImageData(0, 0, W, H).data;
    let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1;
    for (let y = Math.floor(V.y); y < V.y + V.h; y++) for (let x = Math.floor(V.x); x < V.x + V.w; x++) {
      const i = (y * W + x) * 4;
      if (d[i] > 14 || d[i + 1] > 16 || d[i + 2] > 22) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    }
    out[f] = x1 < 0 ? null : {bbox: [x0, y0, x1 + 1, y1 + 1], dx: (x0 + x1 + 1) / 2 - V.cx, dy: (y0 + y1 + 1) / 2 - V.cy};
  }
  return {view: [V.x, V.y, V.w, V.h], cx: V.cx, cy: V.cy, boxes: out};
}, A.frames.split(',').map(Number));
console.log(JSON.stringify(res));
await browser.close();
