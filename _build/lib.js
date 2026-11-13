const ALLOW=['siteassets.parastorage.com','pages.parastorage.com','staticorigin.wixstatic.com','www.wcarc.com','static.wixstatic.com','static.parastorage.com'];
async function setup(ctx){ await ctx.route('**/*',r=>{const h=new URL(r.request().url()).host; if(ALLOW.includes(h)||r.request().url().startsWith('data:')) r.continue(); else r.abort();}); }
async function load(page,u){ await page.goto(u,{waitUntil:'load',timeout:60000}); await page.waitForTimeout(2500);
  const H=await page.evaluate(()=>document.documentElement.scrollHeight);
  for(let y=0;y<H;y+=600){await page.evaluate(y=>scrollTo(0,y),y); await page.waitForTimeout(200);} await page.evaluate(()=>scrollTo(0,0)); await page.waitForTimeout(1500);}
module.exports={setup,load};
