import {createRequire} from 'module';
import fs from 'fs';
const require=createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium}=require('playwright');
const out='laps/LAP-27-connection-memory/validation';
const browser=await chromium.launch({headless:true});
const checks=[];
for (const [width,height] of [[1920,1080],[390,844]]) {
 const page=await browser.newPage({viewport:{width,height}}), errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('https://fx99.tail8e749c.ts.net/chronicles/known-world/');
 if(width===1920) await page.locator('video').evaluate(v=>{v.src='known-world-90s.mp4?delivery=20261010-connection-memory';v.load();});
 await page.locator('video').evaluate(v=>{v.load();});
 await page.waitForFunction(()=>document.querySelector('video').readyState>=1);
 const duration=await page.locator('video').evaluate(v=>v.duration);if(Math.abs(duration-95)>0.1)throw Error('Unexpected duration '+duration);
 const rows=await page.locator('tr').allTextContents();
 for (const [label,value] of [['Direct research attempts','11,388'],['Benchmark runs','298'],['Native benchmark measurements','436'],['Measured experiment trials','1,487']]) {
  if (!rows.some(r=>r.includes(label)&&r.includes(value))) throw Error('Missing public count '+label);
 }
 await page.locator('video').evaluate(async v=>{v.muted=true;await v.play();});
 await page.waitForTimeout(750);
 const played=await page.locator('video').evaluate(v=>v.currentTime>0.3);
 await page.locator('video').evaluate(v=>{v.pause();v.currentTime=2;});
 await page.waitForFunction(()=>{const v=document.querySelector('video');return !v.seeking&&v.readyState>=2;});
 await page.screenshot({path:`${out}/intro-${width}.png`});
 await page.locator('video').evaluate(v=>{v.currentTime=5.1;});
 await page.waitForFunction(()=>{const v=document.querySelector('video');return !v.seeking&&v.readyState>=2;});
 await page.screenshot({path:`${out}/transition-${width}.png`});
 await page.locator('video').evaluate(v=>{v.currentTime=80;});
 await page.waitForFunction(()=>{const v=document.querySelector('video');return !v.seeking&&v.readyState>=2;});
 await page.screenshot({path:`${out}/story-${width}.png`});
 await page.locator('video').evaluate(v=>{v.currentTime=93;});
 await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=2 && Math.abs(v.currentTime-93)<0.1;});
 await page.screenshot({path:`${out}/live-${width}.png`});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 if (!played||overflow||errors.length)throw Error(JSON.stringify({played,overflow,errors}));
 checks.push({viewport:[width,height],played,overflow,errors,duration,counts_verified:true,decoded_end_card:true});
 await page.close();
}
await browser.close();
fs.writeFileSync(out+'/live-browser.json',JSON.stringify(checks,null,2)+'\n');
console.log(JSON.stringify(checks));
