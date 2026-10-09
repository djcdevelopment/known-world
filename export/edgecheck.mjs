// export/edgecheck.mjs: nothing of a sliding-in row may render in the outer 8 px of its plate. Renders a frame with and without the
// nation panel (legend) and tallies layers and counts the pixels that differ inside the edge strips (borders excluded).
import {createRequire} from 'module';
import path from 'path';
const require = createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium} = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const root = path.resolve(new URL('..', import.meta.url).pathname);
const browser = await chromium.launch({headless: true, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text']});
const page = await (await browser.newContext({viewport: {width: 1920, height: 1080}, deviceScaleFactor: 1})).newPage();
await page.goto('file://' + root + '/render/index.html?export=1&data=' + encodeURIComponent(A.data));
await page.waitForFunction(() => window.__ready === true);
const out = {};
for (const f of A.frames.split(',').map(Number)) {
  out[f] = await page.evaluate(f => {
    const ctx = document.getElementById('c').getContext('2d'), L = KW.LAY;
    const grab = off => { window.kwOff(off); window.renderFrame(f); return ctx.getImageData(0, 0, L.W, L.H).data; };
    const full = grab([]), noR = grab(['legend']), noL = grab(['tallies']);
    window.kwOff([]);
    const al = L.alpha, P = [11, 14, 20];
    // the plate over the bare map is a fixed blend; anything else in the strip is content that leaked into it
    const cnt = (a, b, x0, x1, y0, y1) => { let n = 0; for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { const i = (y * L.W + x) * 4; for (let c = 0; c < 3; c++) if (Math.abs(a[i + c] - (b[i + c] * (1 - al) + P[c] * al)) > 2) { n++; break; } } return n; };
    return {nation_panel_outer_8px_differing: cnt(full, noR, L.W - 8, L.W - 1, L.top + 1, L.H - 1) , tallies_outer_8px_differing: cnt(full, noL, L.left - 8, L.left - 1, L.top + 1, L.H - L.bottom - 1)};
  }, f);
}
console.log(JSON.stringify(out));
await browser.close();
