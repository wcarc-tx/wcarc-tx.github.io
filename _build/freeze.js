// Usage: node freeze.js <variant: d|m>
const { chromium, devices } = require('playwright'); const fs=require('fs'); const path=require('path'); const crypto=require('crypto');
const {setup,load}=require('./lib.js');
const PAGES={'/':'index','/about-6':'about','/contact-8':'contact','/general-5':'club-information','/blog':'blog','/general-9':'field-day','/general-clean-2':'faqs','/event-list':'events','/repeaters-map':'repeaters-map','/post/wcarc-saturday-breakfast':'post-wcarc-saturday-breakfast','/post/2025-wcarc-picnic':'post-2025-wcarc-picnic'};
const variant=process.argv[2]||'d';
const OUT='/tmp/cap/raw-'+variant; fs.mkdirSync(OUT,{recursive:true}); fs.mkdirSync('/tmp/cap/shots-'+variant,{recursive:true});
(async()=>{
 const b=await chromium.launch();
 const ctx= variant==='d' ? await b.newContext({viewport:{width:1440,height:900}}) : await b.newContext({...devices['iPhone 13']});
 await setup(ctx); const page=await ctx.newPage();
 for(const [p,name] of Object.entries(PAGES)){
  const u='https://www.wcarc.com'+p;
  try{ await load(page,u);}catch(e){console.log('ERR',p,e.message.slice(0,100));continue;}
  await page.screenshot({path:`/tmp/cap/shots-${variant}/${name}.png`,fullPage:true});
  const html=await page.evaluate(()=>{
    // materialize CSSOM rules into <style> text
    for(const s of [...document.styleSheets]){ try{ const n=s.ownerNode; if(n&&n.tagName==='STYLE'){ const txt=[...s.cssRules].map(r=>r.cssText).join('\n'); if(!n.textContent.trim()) n.textContent=txt; } }catch(e){} }
    try{ for(const sh of (document.adoptedStyleSheets||[])){ const st=document.createElement('style'); st.setAttribute('data-adopted','1'); st.textContent=[...sh.cssRules].map(r=>r.cssText).join('\n'); document.head.appendChild(st);} }catch(e){}
    document.querySelectorAll('img').forEach(i=>{ if(i.currentSrc){i.setAttribute('src',i.currentSrc);} i.removeAttribute('srcset'); i.removeAttribute('sizes'); i.setAttribute('loading','lazy'); });
    document.querySelectorAll('source').forEach(s=>s.remove());
    document.querySelectorAll('script, link[rel=preload], link[rel=prefetch], link[rel=preconnect], link[rel=dns-prefetch], link[rel=modulepreload], noscript, meta[http-equiv]').forEach(e=>e.remove());
    document.querySelectorAll('[data-hook="wix-ads"], #WIX_ADS').forEach(e=>e.remove());
    return '<!DOCTYPE html>\n'+document.documentElement.outerHTML;
  });
  fs.writeFileSync(path.join(OUT,name+'.html'),html); console.log('ok',name,html.length);
 }
 await b.close();
})();
