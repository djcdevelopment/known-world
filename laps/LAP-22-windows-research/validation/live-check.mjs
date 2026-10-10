import {createRequire} from 'module';
import fs from 'fs';
const require=createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium}=require('playwright');
const out='laps/LAP-22-windows-research/validation';
const browser=await chromium.launch({headless:true});
const checks=[];
for (const [width,height] of [[1920,1080],[390,844]]) {
 const page=await browser.newPage({viewport:{width,height}}), errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('https://fx99.tail8e749c.ts.net/chronicles/known-world/');
 const rows=await page.locator('tr').allTextContents();
 for (const [label,value] of [['Direct research attempts','11,388'],['Benchmark runs','298'],['Native benchmark measurements','210']]) {
  if (!rows.some(r=>r.includes(label)&&r.includes(value))) throw Error('Missing public count '+label);
 }
 await page.locator('video').evaluate(async v=>{v.muted=true;await v.play();});
 await page.waitForTimeout(750);
 const played=await page.locator('video').evaluate(v=>v.currentTime>0.3);
 await page.locator('video').evaluate(v=>{v.pause();v.currentTime=88;});
 await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=2 && Math.abs(v.currentTime-88)<0.1;});
 await page.screenshot({path:`${out}/live-${width}.png`});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 if (!played||overflow||errors.length)throw Error(JSON.stringify({played,overflow,errors}));
 checks.push({viewport:[width,height],played,overflow,errors,counts_verified:true,decoded_end_card:true});
 await page.close();
}
await browser.close();
fs.writeFileSync(out+'/live-browser.json',JSON.stringify(checks,null,2)+'\n');
console.log(JSON.stringify(checks));
