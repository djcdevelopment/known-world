import {createRequire} from 'module';import fs from 'fs';
const {chromium}=createRequire('/home/derek/work/founderOS/node_modules/')('playwright');
const b=await chromium.launch({headless:true}),p=await b.newPage();
await p.goto('file:///home/derek/work/known-world/render/index.html?export=1&data=../laps/LAP-27-connection-memory/build/kw-data.js');await p.waitForFunction(()=>window.__ready);
const r=await p.evaluate(()=>{
 const K=window.KW,original=K.tau;K.tau=new Float64Array([0,5,6,7,8]);
 const fade=[0,1,2,3,4].map(f=>K.connectionFade(f,0)),future=K.connectionFade(0,1);K.tau=original;
 if(JSON.stringify(fade)!=='[1,1,0.5,0,0]'||future!==0)throw Error('Bad story-day fade');
 for(const f of [2250,1550,2580,0,2250])window.renderFrame(f);
 if(window.kwErrors().length)throw Error(window.kwErrors().join('\n'));
 return {fade_at_days:[0,5,6,7,8],opacity:fade,future_opacity:future,seek_errors:window.kwErrors()};
});fs.writeFileSync('laps/LAP-27-connection-memory/validation/fade.json',JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));await b.close();
