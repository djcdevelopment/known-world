// export/rehash.mjs: re-render chosen frames in a fresh Chromium (opposite order) and print per-frame PNG sha256 (same capture as the export).
//   node export/rehash.mjs --data <rel> --frames 1,2,3
import {createRequire} from 'module';
import path from 'path';
import crypto from 'crypto';
const require = createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium} = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const QP = new URLSearchParams(A.query || '');
const VPW = parseInt(QP.get('vw') || '1920', 10), VPH = parseInt(QP.get('vh') || '1080', 10), DSF = parseFloat(QP.get('dpr') || '1');
const root = path.resolve(new URL('..', import.meta.url).pathname);
const browser = await chromium.launch({headless: true, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text']});
const ctx = await browser.newContext({viewport: {width: VPW, height: VPH}, deviceScaleFactor: DSF});
const page = await ctx.newPage();
await page.goto('file://' + root + '/render/index.html?export=1&data=' + encodeURIComponent(A.data) + (A.query ? '&' + A.query : ''));
await page.waitForFunction(() => window.__ready === true);
const cdp = await ctx.newCDPSession(page);
const out = {};
for (const f of A.frames.split(',').map(Number).reverse()) {
  await page.evaluate(f => window.renderFrame(f), f);
  const s = await cdp.send('Page.captureScreenshot', (DSF === 1 ? {format: 'png', optimizeForSpeed: true} : {format: 'png', optimizeForSpeed: true, clip: {x: 0, y: 0, width: VPW, height: VPH, scale: DSF}}));
  out[f] = crypto.createHash('sha256').update(Buffer.from(s.data, 'base64')).digest('hex');
}
console.log(JSON.stringify(out));
await browser.close();
