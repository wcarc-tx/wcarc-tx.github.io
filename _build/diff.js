const { chromium } = require('playwright'); const fs=require('fs'); const {PNG}=require('pngjs'); const pm=require('pixelmatch');
const names=process.argv.slice(2);
(async()=>{
 const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1440,height:900}});
 await ctx.route('**/*',r=>{const u=r.request().url(); if(u.startsWith('http://localhost:8765')||u.startsWith('data:')) r.continue(); else r.abort();});
 const page=await ctx.newPage(); fs.mkdirSync('local',{recursive:true}); fs.mkdirSync('dif',{recursive:true});
 for(const n of names){
  await page.goto(`http://localhost:8765/${n}.html`,{waitUntil:'load'}); 
  const H=await page.evaluate(()=>document.documentElement.scrollHeight);
  for(let y=0;y<H;y+=600){await page.evaluate(y=>scrollTo(0,y),y); await page.waitForTimeout(100);} await page.evaluate(()=>scrollTo(0,0)); await page.waitForTimeout(800);
  await page.screenshot({path:`local/${n}.png`,fullPage:true});
  const a=PNG.sync.read(fs.readFileSync(`shots-d/${n}.png`)), c=PNG.sync.read(fs.readFileSync(`local/${n}.png`));
  const w=Math.min(a.width,c.width), h=Math.min(a.height,c.height);
  const crop=(p)=>{const o=new PNG({width:w,height:h}); PNG.bitblt(p,o,0,0,w,h,0,0); return o;};
  const A=crop(a),C=crop(c),D=new PNG({width:w,height:h});
  const bad=pm(A.data,C.data,D.data,w,h,{threshold:0.15});
  fs.writeFileSync(`dif/${n}.png`,PNG.sync.write(D));
  console.log(n.padEnd(32), `prod ${a.width}x${a.height} local ${c.width}x${c.height}`, 'diff%', (100*bad/(w*h)).toFixed(2));
 }
 await b.close();
})();
