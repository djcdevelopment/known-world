import {createRequire} from 'module';
import fs from 'fs';
const require=createRequire('/home/derek/work/founderOS/node_modules/');
const {chromium}=require('playwright');
const here=new URL('.',import.meta.url).pathname;
const med=a=>{const s=[...a].sort((x,y)=>x-y);return s[Math.floor(s.length/2)]};
const mx=a=>Math.max(...a);
const browser=await chromium.launch({headless:true});
const ctx=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1});
const page=await ctx.newPage();
const webgl2=await page.evaluate(()=>!!document.createElement('canvas').getContext('webgl2'));
const out={webgl2_available:webgl2,results:[]};
async function loadN(n){await page.goto(`file://${here}hex.html?n=${n}`);await page.waitForFunction(()=>typeof window.__kwFrame==='function');}
for(const n of [5000,20000,80000]){
  await loadN(n);
  for(let i=0;i<2;i++){await page.evaluate(i=>window.__kwFrame(i),i);await page.screenshot({type:'png'});}
  const R=[],S=[],T=[];
  for(let i=0;i<10;i++){
    const t0=performance.now();
    const r=await page.evaluate(i=>window.__kwFrame(i+2),i);
    const t1=performance.now();
    await page.screenshot({type:'png'});
    const t2=performance.now();
    R.push(r);S.push(t2-t1);T.push(t2-t0);
  }
  const row={n,render_ms:{median:med(R),max:mx(R)},screenshot_ms:{median:med(S),max:mx(S)},total_ms:{median:med(T),max:mx(T)},
    proj_min_20000_frames:med(T)*20000/60000};
  out.results.push(row);
}
if(process.argv[2]==='frames'){
  await loadN(20000);
  fs.mkdirSync(here+'frames',{recursive:true});
  for(let i=0;i<60;i++){
    await page.evaluate(i=>window.__kwFrame(i),i);
    await page.screenshot({type:'png',path:here+`frames/f${String(i).padStart(5,'0')}.png`});
  }
  out.frames_written=60;
}
await browser.close();
fs.writeFileSync(here+'result.json',JSON.stringify(out,null,1));
console.log(JSON.stringify(out,null,1));
