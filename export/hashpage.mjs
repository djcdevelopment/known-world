// export/hashpage.mjs: per-frame PNG sha256 of any page URL that exposes renderFrame (the same capture as the export), 1920 x 1080.
//   node export/hashpage.mjs --url <page url with ?export=1&data=...> --frames 1,2,3
import {createRequire} from 'module';
import crypto from 'crypto';
const require = createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium} = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const browser = await chromium.launch({headless: true, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text']});
const ctx = await browser.newContext({viewport: {width: 1920, height: 1080}, deviceScaleFactor: 1});
const page = await ctx.newPage();
await page.goto(A.url);
await page.waitForFunction(() => window.__ready === true);
const cdp = await ctx.newCDPSession(page);
const out = {};
for (const f of A.frames.split(',').map(Number)) {
  await page.evaluate(f => window.renderFrame(f), f);
  const s = await cdp.send('Page.captureScreenshot', {format: 'png', optimizeForSpeed: true});
  out[f] = crypto.createHash('sha256').update(Buffer.from(s.data, 'base64')).digest('hex');
}
console.log(JSON.stringify(out));
await browser.close();
