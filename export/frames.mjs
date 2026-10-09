// export/frames.mjs: CDP Page.captureScreenshot (optimizeForSpeed) -> per-segment ffmpeg image2pipe -> libx264.
// One Chromium per worker; segments resume by their done marker; per-frame sha256 of the PNG bytes.
//   NODE_PATH=/home/derek/work/founderOS/node_modules nice node export/frames.mjs --data <path> --out <dir> --from 0 --to F
import {createRequire} from 'module';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import {spawn} from 'child_process';
const require = createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium} = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const root = path.resolve(new URL('..', import.meta.url).pathname);
const out = path.resolve(A.out);
const workers = parseInt(A.workers || '10', 10);
const from = parseInt(A.from || '0', 10);
const FFMPEG = process.env.FFMPEG;
const page_url = 'file://' + root + '/render/index.html?export=1&data=' + encodeURIComponent(A.data) + (A.query ? '&' + A.query : '');
fs.mkdirSync(out + '/seg', {recursive: true});
fs.mkdirSync(out + '/hashes', {recursive: true});
const launchOpts = {headless: true, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text']};

async function openPage() {
  const browser = await chromium.launch(launchOpts);
  const ctx = await browser.newContext({viewport: {width: 1920, height: 1080}, deviceScaleFactor: 1});
  const page = await ctx.newPage();
  await page.goto(page_url);
  await page.waitForFunction(() => window.__ready === true);
  const cdp = await ctx.newCDPSession(page);
  return {browser, page, cdp};
}

const first = await openPage();
const info = await first.page.evaluate(() => window.kwInfo());
const to = parseInt(A.to || String(info.F), 10);
const total = to - from;
const segFrames = parseInt(A['segment-frames'] || String(Math.min(1800, Math.ceil(total / workers))), 10);
const segs = [];
for (let s = from; s < to; s += segFrames) segs.push([s, Math.min(to, s + segFrames)]);
const segName = i => 'seg_' + String(i).padStart(4, '0');
let next = 0, doneFrames = 0, skipped = 0;
const timing = {errors: [], workers, segFrames, segments: segs.length, per_segment: []};
const t0 = process.hrtime.bigint();

async function worker(w) {
  const h = w === 0 ? first : await openPage();
  while (true) {
    const i = next++;
    if (i >= segs.length) break;
    const [a, b] = segs[i];
    const mp4 = `${out}/seg/${segName(i)}.mp4`, hf = `${out}/hashes/${segName(i)}.txt`;
    if (fs.existsSync(mp4) && fs.existsSync(hf)) { skipped++; continue; }
    const tmp = mp4 + '.part.mp4';
    const ff = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(info.fps), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-g', '60', '-threads', '3', '-r', String(info.fps), tmp], {stdio: ['pipe', 'inherit', 'inherit']});
    const exited = new Promise(res => ff.on('close', res));
    ff.stdin.on('error', () => {});
    const lines = [];
    const ts = process.hrtime.bigint();
    let renderNs = 0n;
    for (let f = a; f < b; f++) {
      const r0 = process.hrtime.bigint();
      await h.page.evaluate(f => window.renderFrame(f), f);
      const shot = await h.cdp.send('Page.captureScreenshot', {format: 'png', optimizeForSpeed: true});
      renderNs += process.hrtime.bigint() - r0;
      const buf = Buffer.from(shot.data, 'base64');
      lines.push(f + ' ' + crypto.createHash('sha256').update(buf).digest('hex'));
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      doneFrames++;
    }
    ff.stdin.end();
    const code = await exited;
    if (code !== 0) throw new Error('ffmpeg exit ' + code + ' on ' + segName(i));
    fs.renameSync(tmp, mp4);
    fs.writeFileSync(hf, lines.join('\n') + '\n');
    const wall = Number(process.hrtime.bigint() - ts) / 1e6;
    timing.per_segment.push({seg: i, frames: b - a, wall_ms: wall, capture_ms_per_frame: Number(renderNs) / 1e6 / (b - a), worker: w});
  }
  const errs = await h.page.evaluate(() => window.kwErrors ? window.kwErrors() : []);
  for (const e of errs) timing.errors.push(e);
  await h.browser.close();
}
await Promise.all(Array.from({length: workers}, (_, w) => worker(w)));
const wall = Number(process.hrtime.bigint() - t0) / 1e6;
timing.wall_ms = wall; timing.frames = total; timing.skipped_segments = skipped;
timing.ms_per_frame_effective = wall / Math.max(1, total - skipped * segFrames);
timing.info = info;
fs.writeFileSync(out + '/timing.json', JSON.stringify(timing, null, 1));
const n = segs.length;
fs.writeFileSync(out + '/segments.txt', segs.map((s, i) => `file 'seg/${segName(i)}.mp4'`).join('\n') + '\n');
console.log(JSON.stringify({frames: total, segments: n, skipped, wall_ms: Math.round(wall), ms_per_frame_effective: timing.ms_per_frame_effective.toFixed(2)}));
