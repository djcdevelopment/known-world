// export/motion.mjs: the motion budget (DIRECTION rev 5). For each start frame, render the next 30 frames in one page and diff consecutive frames
// on the canvas itself (getImageData), counting changed pixels outside the map rect and the timeline rect.
//   node export/motion.mjs --data <kw-data.js rel to render/> --starts f,f,f --map x,y,w,h --timeline x,y,w,h [--n 30]
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
const res = await page.evaluate(({starts, map, tl, n}) => {
  const cv = document.getElementById('c'), c2 = cv.getContext('2d'), W = cv.width, H = cv.height;
  const inRect = (x, y, r) => x >= r[0] && x < r[0] + r[2] && y >= r[1] && y < r[1] + r[3];
  const out = [];
  for (const s of starts) {
    let prev = null; const shares = [], where = [];
    for (let g = s; g < s + n; g++) {
      window.renderFrame(g);
      const d = c2.getImageData(0, 0, W, H).data;
      if (prev) {
        let ch = 0, tot = 0, minx = 1e9, miny = 1e9, maxx = -1, maxy = -1;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          if (inRect(x, y, map) || inRect(x, y, tl)) continue;
          tot++;
          const i = (y * W + x) * 4;
          if (d[i] !== prev[i] || d[i + 1] !== prev[i + 1] || d[i + 2] !== prev[i + 2]) { ch++; if (x < minx) minx = x; if (x > maxx) maxx = x; if (y < miny) miny = y; if (y > maxy) maxy = y; }
        }
        shares.push(ch / tot); if (ch) where.push([minx, miny, maxx, maxy]);
      }
      prev = d;
    }
    out.push({start: s, max_share: Math.max(...shares), mean_share: shares.reduce((a, b) => a + b, 0) / shares.length, frames_changed: shares.filter(v => v > 0).length, over_0_5pct: shares.filter(v => v > 0.005).length});
  }
  return out;
}, {starts: A.starts.split(',').map(Number), map: A.map.split(',').map(Number), tl: A.timeline.split(',').map(Number), n: parseInt(A.n || '30', 10)});
console.log(JSON.stringify(res));
await browser.close();
