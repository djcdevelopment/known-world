// export/chrome.mjs: player chrome checks (ia): visible at load, hidden after 3 s without input (0.3 s fade), back on pointer movement, the s toggle, and absent under ?export=1.
//   node export/chrome.mjs --data <rel> --out <dir> [--f 19300]
import {createRequire} from 'module';
import fs from 'fs';
import path from 'path';
const require = createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium} = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const root = path.resolve(new URL('..', import.meta.url).pathname);
const browser = await chromium.launch({headless: true, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text']});
const out = {};
fs.mkdirSync(A.out, {recursive: true});
for (const [vw, vh] of [[1920, 1080], [390, 844]]) {
  const ctx = await browser.newContext({viewport: {width: vw, height: vh}, deviceScaleFactor: 1});
  const page = await ctx.newPage();
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await page.goto('file://' + root + '/render/index.html?audio=none&f=' + (A.f || '19300') + '&data=' + encodeURIComponent(A.data));
  await page.waitForFunction(() => window.__ready === true && window.kwPlayer);
  const tag = vw + 'x' + vh, r = {};
  const op = () => page.evaluate(() => { const t = document.querySelector('.tp'); return { opacity: parseFloat(getComputedStyle(t).opacity), hidden: t.classList.contains('hide'), rect: (b => [b.x, b.y, b.width, b.height])(t.getBoundingClientRect()) }; });
  await page.mouse.move(vw / 2, vh / 2);
  await page.waitForTimeout(500);
  r.at_load = await op();
  await page.screenshot({path: `${A.out}/chrome-visible-${tag}.png`});
  await page.waitForTimeout(3600);
  r.after_3_6s_idle = await op();
  await page.screenshot({path: `${A.out}/chrome-hidden-${tag}.png`});
  await page.mouse.move(vw / 2 + 5, vh / 2 + 5);
  await page.waitForTimeout(450);
  r.after_pointer_move = await op();
  await page.keyboard.press('s');
  await page.waitForTimeout(200);
  r.surfaces_toggle = await page.evaluate(() => KW.ui.surfaces);
  await page.screenshot({path: `${A.out}/chrome-surfaces-${tag}.png`});
  r.page_errors = errs;
  out[tag] = r;
  await ctx.close();
}
const ctx = await browser.newContext({viewport: {width: 1920, height: 1080}, deviceScaleFactor: 1});
const page = await ctx.newPage();
await page.goto('file://' + root + '/render/index.html?export=1&data=' + encodeURIComponent(A.data));
await page.waitForFunction(() => window.__ready === true);
out.export = {tp_elements: await page.evaluate(() => document.querySelectorAll('.tp, #ui, #stage').length), player_loaded: await page.evaluate(() => typeof window.kwPlayer !== 'undefined')};
console.log(JSON.stringify(out));
await browser.close();
