// export/still.mjs: write PNG stills of chosen frames (look at the page, never part of an export).
import {createRequire} from 'module';
import fs from 'fs';
import path from 'path';
const require = createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium} = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const root = path.resolve(new URL('..', import.meta.url).pathname);
const browser = await chromium.launch({headless: true, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text']});
const VW = parseInt(A.vw || '1920', 10), VH = parseInt(A.vh || '1080', 10);
const ctx = await browser.newContext({viewport: {width: VW, height: VH}, deviceScaleFactor: parseFloat(A.dsf || '1')});
const page = await ctx.newPage();
page.on('pageerror', e => console.log('pageerror', e.message));
await page.goto('file://' + root + '/render/index.html?export=1&data=' + encodeURIComponent(A.data) + (A.vw ? '&vw=' + VW + '&vh=' + VH : '') + (A.query ? '&' + A.query : ''));
await page.waitForFunction(() => window.__ready === true);
fs.mkdirSync(A.out, {recursive: true});
for (const f of A.frames.split(',').map(Number)) {
  if (A.ui) await page.evaluate(u => window.kwUi(JSON.parse(u)), A.ui);
  await page.evaluate(f => window.renderFrame(f), f);
  await page.screenshot({path: `${A.out}/${A.prefix || 'f'}${String(f).padStart(5, '0')}.png`});
}
console.log(JSON.stringify(await page.evaluate(() => window.kwErrors())));
await browser.close();
